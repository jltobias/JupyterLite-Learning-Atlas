"""Actual canonical case calculations, edit matrices, SVGs and source integration."""
import ast
import contextlib
import copy
import hashlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET

import nbformat
import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from atlas_paths import canonical_notebooks
from generate import make_toc, seed_project
from phi_case_material import CASES, OWNER, bibliography, source_overview
from validate import validate_catalog_sources

NS = '{http://www.w3.org/2000/svg}'


def run_case(slug, replacements=None):
    notebook = nbformat.read(ROOT / f'content/projects/{slug}/index.ipynb', as_version=4)
    state, displayed, text = {}, [], io.StringIO()
    sources = [cell.source for cell in notebook.cells if cell.cell_type == 'code']
    for before in replacements or {}:
        assert any(before in source for source in sources), before
    with patch('IPython.display.display', side_effect=displayed.append), contextlib.redirect_stdout(text):
        for source in sources:
            for before, after in (replacements or {}).items():
                source = source.replace(before, after)
            exec(compile(source, slug, 'exec'), state)
    figure = ET.fromstring(displayed[-1].data)
    assert figure.find(NS+'title').text and figure.find(NS+'desc').text
    assert figure.attrib['role'] == 'img' and figure.attrib['aria-label']
    return state, figure, text.getvalue()


def svg_text(figure):
    return ' '.join(figure.itertext())


class PHICaseMatrixTests(unittest.TestCase):
    def assert_weighted_diamond(self, figure, weighted):
        diamonds = [path for path in figure.findall(NS+'path') if path.attrib.get('fill') == '#f3bd5c']
        self.assertEqual(len(diamonds), 1)
        coordinates = [float(value) for value in re.findall(r'-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?', diamonds[0].attrib['d'])]
        self.assertEqual(len(coordinates), 8)
        xs, ys = coordinates[::2], coordinates[1::2]
        self.assertAlmostEqual((min(xs)+max(xs))/2, 55+weighted[0]*60)
        self.assertAlmostEqual((min(ys)+max(ys))/2, 270-weighted[1]*52)
        self.assertAlmostEqual(max(xs)-min(xs), 20)
        self.assertAlmostEqual(max(ys)-min(ys), 20)

    def test_basic_default_counts_centres_zero_and_area_encoding(self):
        state, figure, text = run_case('cholera-1854-basic')
        self.assertEqual((len(state['rows']), state['positive'], state['total']), (6, 5, 14))
        self.assertEqual(state['unweighted'], (28/6, 2))
        self.assertEqual(state['weighted'], (30/14, 26/14))
        for phrase in ['positive-death locations: 5/6', 'fictional deaths: 14', '(4.666667, 2.000000)', '(2.142857, 1.857143)', 'not attack rates']:
            self.assertIn(phrase, text)
        circles = figure.findall(NS+'circle')
        self.assertEqual(len(circles), 6)
        self.assertEqual(circles[-1].attrib['fill'], '#ffffff')
        self.assertGreater(float(circles[-1].attrib['r']), 0)
        self.assertAlmostEqual(float(circles[0].attrib['r'])**2 / float(circles[3].attrib['r'])**2, 6, places=3)
        self.assertIn('B3: 0', svg_text(figure))
        self.assertIn('weighted centre (2.142857, 1.857143)', figure.find(NS+'desc').text)
        self.assert_weighted_diamond(figure, (30/14, 26/14))

    def test_basic_instructed_edit_and_all_zero_update_text_and_svg(self):
        state, figure, text = run_case('cholera-1854-basic', {"('B3', 9, 2, 0)": "('B3', 9, 2, 14)"})
        self.assertEqual(state['total'], 28)
        self.assertEqual(state['weighted'], (156/28, 54/28))
        self.assertEqual(state['unweighted'], (28/6, 2))
        self.assertIn('positive-death locations: 6/6', text)
        self.assertIn('(5.571429, 1.928571)', svg_text(figure))
        self.assert_weighted_diamond(figure, (156/28, 54/28))
        state, figure, text = run_case('cholera-1854-basic', {'pumps =': 'rows = [(name, x, y, 0) for name, x, y, count in rows]\npumps ='})
        self.assertIsNone(state['weighted'])
        self.assertEqual(state['total'], 0)
        self.assertIn('Death-weighted centre, planar units: unknown', text)
        self.assertIn('weighted unknown', svg_text(figure))
        self.assertEqual(len(figure.findall(NS+'circle')), 6)
        self.assertTrue(all(c.attrib['fill'] == '#ffffff' for c in figure.findall(NS+'circle')))
        self.assertFalse([path for path in figure.findall(NS+'path') if path.attrib.get('fill') == '#f3bd5c'])

    def test_access_inclusive_budget_and_unreachable_unknown(self):
        state, figure, text = run_case('cholera-1854-advanced-1')
        self.assertEqual(state['costs'], {'S': 0, 'A': 2, 'B': 1, 'C': 4, 'D': 2, 'E': 3, 'U': None})
        self.assertEqual(state['reached'], ['S', 'A', 'B', 'D', 'E'])
        self.assertEqual(state['boundary'], ['E'])
        self.assertIn('5/7 graph nodes', text)
        self.assertIn('U: unknown', figure.find(NS+'desc').text)
        self.assertIn('3 min', svg_text(figure))
        self.assertIn('5/7 nodes reached', svg_text(figure))
        state, figure, text = run_case('cholera-1854-advanced-1', {'budget = 3': 'budget = 2'})
        self.assertEqual(state['reached'], ['S', 'A', 'B', 'D'])
        self.assertEqual(state['boundary'], ['A', 'D'])
        self.assertIsNone(state['costs']['U'])
        self.assertIn('4/7 graph nodes', text)
        self.assertIn('4/7 nodes reached', svg_text(figure))

    def test_access_removed_connection_recomputes_costs_and_figure(self):
        state, figure, text = run_case('cholera-1854-advanced-1', {"('B', 'D', 1),": ''})
        self.assertEqual(state['costs']['E'], 8)
        self.assertEqual(state['costs']['D'], 9)
        self.assertEqual(state['reached'], ['S', 'A', 'B'])
        self.assertIsNone(state['costs']['U'])
        self.assertIn('3/7 graph nodes', text)
        self.assertIn('8 min', svg_text(figure))
        self.assertIn('9 min', svg_text(figure))
        self.assertIn('3/7 nodes reached', svg_text(figure))
        self.assertEqual(len(figure.findall(NS+'circle')), 7)

    def test_access_rejects_nonpositive_and_nonfinite_edge_minutes(self):
        for invalid in ['-1', '0', "float('nan')", "float('inf')"]:
            with self.subTest(minutes=invalid), self.assertRaisesRegex(ValueError, 'positive finite minutes'):
                run_case('cholera-1854-advanced-1', {"('S', 'A', 2)": f"('S', 'A', {invalid})"})

    def test_nearest_samples_buildings_ties_outside_and_edit(self):
        cases = [({}, {'A': 15, 'B': 15, 'tie': 5, 'outside': 0}, {'A': 2, 'B': 2, 'tie': 1, 'outside': 1}),
                 ({"'B': (5, 1)": "'B': (4, 1)"}, {'A': 15, 'B': 20, 'tie': 0, 'outside': 0}, {'A': 2, 'B': 3, 'tie': 0, 'outside': 1})]
        for edits, grid, buildings in cases:
            with self.subTest(edits=edits):
                state, figure, text = run_case('cholera-1854-advanced-2', edits)
                self.assertEqual(state['grid_counts'], grid)
                self.assertEqual(state['building_counts'], buildings)
                self.assertEqual(sum(grid.values()), len(state['samples']))
                self.assertEqual(sum(buildings.values()), len(state['buildings']))
                self.assertEqual(state['building_membership']['o'], 'outside')
                self.assertEqual(state['nearest_site']((0, 0), state['pumps'], state['domain']), 'A')
                self.assertEqual(state['nearest_site']((6, 4), state['pumps'], state['domain']), 'B')
                self.assertEqual(state['nearest_site']((-1, 0), state['pumps'], state['domain']), 'outside')
                self.assertIn('Grid samples / 35: '+str(grid), text)
                self.assertIn('Building centroids / 6: '+str(buildings), text)
                self.assertIn(f'Grid / 35: A {grid["A"]}, B {grid["B"]}, tie {grid["tie"]}, outside {grid["outside"]}', svg_text(figure))
                self.assertIn('outside 1', svg_text(figure))
                self.assertIn('o: outside', figure.find(NS+'desc').text)
        state, _, _ = run_case('cholera-1854-advanced-2')
        self.assertEqual(state['nearest_site']((3, 0), state['pumps'], state['domain']), 'tie')

    def test_narrowed_domain_accounts_for_all_samples_and_moves_frame_caption(self):
        state, figure, text = run_case('cholera-1854-advanced-2', {'domain = (0, 6, 0, 4)': 'domain = (1, 5, 0, 4)'})
        counts = {'A': 10, 'B': 10, 'tie': 5, 'outside': 10}
        self.assertEqual(state['grid_counts'], counts)
        self.assertEqual(len(state['samples']), 35)
        self.assertEqual(sum(state['grid_counts'].values()), 35)
        self.assertEqual(state['building_counts'], {'A': 2, 'B': 2, 'tie': 1, 'outside': 1})
        self.assertIn('Grid samples / 35: '+str(counts), text)
        self.assertIn('inclusive domain: (1, 5, 0, 4)', text)
        self.assertIn('Grid / 35: A 10, B 10, tie 5, outside 10', svg_text(figure))
        self.assertIn('Samples x 0..6, y 0..4; domain x 1..5, y 0..4 (inclusive planar units).', svg_text(figure))
        self.assertIn('Inclusive domain: (1, 5, 0, 4)', figure.find(NS+'desc').text)
        frame = figure.find(NS+"rect[@id='domain-frame']")
        self.assertEqual({key: float(frame.attrib[key]) for key in ['x', 'y', 'width', 'height']},
                         {'x': 129, 'y': 109, 'width': 256, 'height': 216})
        samples = [rect for rect in figure.findall(NS+'rect') if rect.attrib.get('width') == '40']
        self.assertEqual(len(samples), 35)
        self.assertEqual(sum(rect.attrib['fill'] == '#ffffff' for rect in samples), 10)

    def test_contact_policy_merges_components_preserves_isolate_and_dst(self):
        state, figure, text = run_case('mdr-tb-thailand-2005')
        self.assertEqual(state['components'], [['A', 'B', 'C'], ['D', 'E'], ['F']])
        self.assertEqual(state['summary'], {'mdr': 3, 'known': 4, 'unknown': 2, 'fraction': 3/4})
        self.assertIn('3/4 (75.0%)', text)
        self.assertIn('unknown DST / all IDs: 2/6', text)
        self.assertIn('weak excluded', svg_text(figure))
        changed, figure, text = run_case('mdr-tb-thailand-2005', {'include_weak = False': 'include_weak = True'})
        self.assertEqual(changed['components'], [['A', 'B', 'C', 'D', 'E'], ['F']])
        self.assertEqual(changed['dst'], state['dst'])
        self.assertEqual(changed['summary'], state['summary'])
        self.assertIn('Component sizes: [5, 1]', svg_text(figure))
        self.assertIn('weak selected', svg_text(figure))
        self.assertEqual(len(figure.findall(NS+'circle')), 6)
        self.assertFalse(any('marker-end' in p.attrib for p in figure.findall(NS+'path')))

    def test_dst_observation_edit_and_all_unknown_do_not_infer_resistance(self):
        state, figure, text = run_case('mdr-tb-thailand-2005', {"'C': None": "'C': 'MDR'"})
        self.assertEqual(state['summary'], {'mdr': 4, 'known': 5, 'unknown': 1, 'fraction': 4/5})
        self.assertIn('4/5 (80.0%)', text)
        self.assertIn('4/5 (80.0%)', svg_text(figure))
        state, figure, text = run_case('mdr-tb-thailand-2005', {'contacts =': 'dst = dict.fromkeys(dst)\ncontacts ='})
        self.assertEqual(state['summary'], {'mdr': 0, 'known': 0, 'unknown': 6, 'fraction': None})
        self.assertEqual(state['sizes'], [3, 2, 1])
        self.assertIn('0/0 (unknown)', text)
        self.assertIn('unknown DST / all IDs: 6/6', text)
        self.assertIn('0/0 (unknown)', svg_text(figure))
        self.assertEqual(sum(t.text == 'unknown' for t in figure.findall(NS+'text')), 6)

    def test_mdr_rejects_unsupported_dst_and_contact_evidence(self):
        for label in ["'susceptible'", "'mdr'", '0']:
            with self.subTest(dst=label), self.assertRaisesRegex(ValueError, 'DST labels must be MDR, non-MDR or None'):
                run_case('mdr-tb-thailand-2005', {"'C': None": "'C': "+label})
        for policy in ['False', 'True']:
            with self.subTest(include_weak=policy), self.assertRaisesRegex(ValueError, 'Contact evidence must be strong or weak'):
                run_case('mdr-tb-thailand-2005', {
                    "('C', 'D', 'weak')": "('C', 'D', 'unreviewed')",
                    'include_weak = False': 'include_weak = '+policy})

    def test_updated_advanced2_runtime_assertions_match_canonical_activity(self):
        tree = ast.parse((ROOT/'scripts/check_runtime.py').read_text(encoding='utf-8'))
        assignment = next(node for node in tree.body if isinstance(node, ast.Assign)
                          and any(isinstance(target, ast.Name) and target.id == 'PHI_RUNTIME' for target in node.targets))
        _, assertions, _ = next(case for case in ast.literal_eval(assignment.value) if case[0] == 'cholera-1854-advanced-2')
        state, _, _ = run_case('cholera-1854-advanced-2')
        exec(compile(assertions, 'Advanced2 runtime assertions', 'exec'), state)


class PHIIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads((ROOT/'catalog/repositories.json').read_text(encoding='utf-8'))
        self.records = self.catalog['repositories']

    def test_external_review_is_required_and_owner_must_match_source_url(self):
        schema = json.loads((ROOT/'catalog/repositories.schema.json').read_text(encoding='utf-8'))
        self.assertEqual(validate_catalog_sources(self.catalog, schema), self.records)
        index = next(i for i, record in enumerate(self.records) if record['slug'] == 'cholera-1854-basic')
        for missing in [('source_owner',), ('source_review',), ('source_owner', 'source_review')]:
            changed = copy.deepcopy(self.catalog)
            for field in missing:
                del changed['repositories'][index][field]
            with self.subTest(missing=missing), self.assertRaises(jsonschema.ValidationError):
                validate_catalog_sources(changed, schema)
        changed = copy.deepcopy(self.catalog)
        changed['repositories'][index]['source_owner'] = 'another-owner'
        with self.assertRaisesRegex(AssertionError, 'source_owner disagrees with source URL'):
            validate_catalog_sources(changed, schema)

    def test_manifest_metadata_retains_exact_checksums_without_adding_launch_rows(self):
        audit = json.loads((ROOT/'catalog/launch-checks.json').read_text(encoding='utf-8'))
        preserved = json.dumps(audit['results'][:158], sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
        self.assertEqual(hashlib.sha256(preserved).hexdigest(), '4bfc64d0f6d200bb1da081a32417af307d19a0fdc34a450f2acd834c5748718e')
        manifests = {item['repository']: item for item in audit['manifest_evidence']}
        checksums = {'cholera-1854-basic': '9719e69cd9c0a58a92e9f72010cbd61ccf605b798672f1af25f7446464f34369',
                     'cholera-1854-advanced-1': 'afade817393c60e3a89d66077a726a9ea3e76d0b061273440774528696b7b602'}
        self.assertEqual(set(manifests), {CASES[slug]['name'] for slug in checksums})
        for slug, checksum in checksums.items():
            case = CASES[slug]
            evidence = manifests[case['name']]
            self.assertEqual(evidence['url'], f'https://phi-case-studies.github.io/{case["name"]}/api/contents/all.json')
            self.assertEqual(evidence['checked_on'], '2026-11-02')
            self.assertEqual(evidence['source_commit'], case['commit'])
            self.assertEqual(evidence['sha256'], checksum)
            self.assertEqual(evidence['normalization'], 'UTF-8 JSON object, sort_keys=True, ensure_ascii=False, separators=(comma,colon), no whitespace')
            self.assertEqual(evidence['confirmed_notebook_basenames'], [Path(path).name for path, _ in case['files']])
            for filename in ['README.md', 'REFERENCES.md', 'content/references.ipynb']:
                text = (ROOT/filename).read_text(encoding='utf-8')
                self.assertIn(evidence['url'], text)
                self.assertIn('https://jltobias.github.io/JupyterLite-Learning-Atlas/catalog/launch-checks.json', text)
        basic = next(record for record in self.records if record['slug'] == 'cholera-1854-basic')
        self.assertEqual(basic['source_review']['launch_provenance'], 'reviewed README and published manifest')

    def test_shared_bibliography_and_standalone_source_heading_hierarchy(self):
        group = '## PHI outbreak cases: creators, sources and rights (2026-11-02)'
        expected = ['### '+case['title']+': inspected source notebooks' for case in CASES.values()]
        expected.append('### Historical and methodological works used')
        shared = [bibliography(), (ROOT/'README.md').read_text(encoding='utf-8'),
                  (ROOT/'REFERENCES.md').read_text(encoding='utf-8'),
                  nbformat.read(ROOT/'content/references.ipynb', as_version=4).cells[0].source]
        for text in shared:
            section = group+text.split(group, 1)[1]
            self.assertEqual([line for line in section.splitlines() if line.startswith('## ')], [group])
            self.assertEqual([line for line in section.splitlines() if line.startswith('### ')], expected)
        for slug, case in CASES.items():
            heading = '## '+case['title']+': inspected source notebooks'
            self.assertTrue(source_overview(slug).startswith(heading))
            notebook = nbformat.read(ROOT/f'content/projects/{slug}/index.ipynb', as_version=4)
            self.assertEqual(sum(cell.cell_type == 'markdown' and cell.source.startswith(heading) for cell in notebook.cells), 1)

    def test_editorial_order_each_notebook_once_and_matching_seeds(self):
        toc = yaml.safe_load((ROOT/'content/_toc.yml').read_text(encoding='utf-8'))
        self.assertEqual(toc, make_toc(self.records))
        self.assertEqual([c['file'] for c in toc['parts'][0]['chapters']][:2],
                         ['foundations/browser-python', 'projects/cholera-1854-basic/index'])
        investigations = next(p for p in toc['parts'] if p['caption'] == 'Outbreak investigations')
        self.assertEqual([c['file'] for c in investigations['chapters']],
                         [f'projects/{slug}/index' for slug in list(CASES)[1:]])
        navigation = [toc['root']] + [c['file'] for p in toc['parts'] for c in p['chapters']]
        notebooks = canonical_notebooks()
        self.assertEqual(len(navigation), len(set(navigation)))
        self.assertEqual(set(navigation), {p.relative_to(ROOT/'content').as_posix().removesuffix('.ipynb') for p in notebooks})
        for record in self.records:
            if record['slug'] not in CASES:
                continue
            canonical = nbformat.read(ROOT/'content'/record['notebook'], as_version=4)
            with patch('generate.notebook') as seeded:
                seed_project(record)
            self.assertEqual([c['source'].strip() for c in seeded.call_args.args[1]], [c.source.strip() for c in canonical.cells])
            work = ROOT/'_build/test-phi-seed'; work.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(dir=work) as folder, patch('generate.ROOT', Path(folder)):
                seed_project(record)
                target = Path(folder)/'content'/record['notebook']
                self.assertTrue(target.exists())
                target.write_text('authored sentinel', encoding='utf-8')
                seed_project(record)
                self.assertEqual(target.read_text(encoding='utf-8'), 'authored sentinel')

    def test_external_owner_scope_dated_evidence_and_preserved_baseline(self):
        discovery = json.loads((ROOT/'catalog/discovery.json').read_text(encoding='utf-8'))
        expected_core = {r['name'] for r in discovery['repositories'] if r['url'].split('/')[3].lower() == 'jltobias'
                         and r['name'].startswith('JupyterLite') and r['name'] != 'JupyterLite-Learning-Atlas'}
        self.assertEqual({r['name'] for r in self.records if r['category'] == 'jupyterlite'}, expected_core)
        audit = json.loads((ROOT/'catalog/launch-checks.json').read_text(encoding='utf-8'))
        self.assertEqual(len(audit['results']), sum(len(r['resources']) for r in self.records))
        # These are the approved pre-PHI milestone's evidence, not overall-size constraints.
        for values, count, digest in [
            (audit['results'], 145, '7dd298d7a1ea50941c176b5047717f5062726b22b62b5e210fa3dc0e2606b7f1'),
            (self.records, 34, '02802e2627002fac2e6ec9d590d338a88ca2e3268965dac815bf6bfac6590415'),
            (discovery['repositories'], 60, '8960fadde672a6bded51cac22c1a44a74ea9092f3e6bbfd3f61e11dff18d63b2')]:
            canonical = json.dumps(values[:count], sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()
            self.assertEqual(hashlib.sha256(canonical).hexdigest(), digest)
        for record in self.records:
            if record['slug'] not in CASES:
                continue
            self.assertEqual(record['category'], 'related')
            self.assertEqual(record['source_owner'], OWNER)
            self.assertEqual(record['source_review']['kind'], 'targeted-external')
            if record['slug'] in ['cholera-1854-advanced-2', 'mdr-tb-thailand-2005']:
                self.assertIn('exact README-documented Binder entry GET', record['launch_status'])
                self.assertIn('no browser manifest, source execution or Binder session is certified', record['launch_status'])
                self.assertNotIn('manifests confirm', record['launch_status'])
            evidence = [r for r in audit['results'] if r['repository'] == record['name']]
            self.assertEqual({r['url'] for r in evidence}, {r['url'] for r in record['resources']})
            self.assertTrue(all(r['status'] == 200 and r['checked_on'] == '2026-11-02' for r in evidence))
        self.assertEqual(json.loads((ROOT/'site/data/catalog.json').read_text(encoding='utf-8')), self.catalog)

    def test_complete_used_source_register_primary_credits_and_reciprocal_routes(self):
        documents = {p: (ROOT/p).read_text(encoding='utf-8') for p in ['README.md', 'REFERENCES.md', 'content/references.ipynb']}
        for slug, case in CASES.items():
            nb = nbformat.read(ROOT/f'content/projects/{slug}/index.ipynb', as_version=4)
            text = '\n'.join(c.source for c in nb.cells if c.cell_type == 'markdown')
            for path, _ in case['files']:
                link = f'https://github.com/{OWNER}/{case["name"]}/blob/{case["commit"]}/{path}'
                self.assertIn(link, text)
                for document, raw in documents.items():
                    self.assertIn(link, raw, document)
            for other in CASES:
                if other != slug:
                    self.assertIn('../'+other+'/index.ipynb', text)
            for phrase in ['synthetic', 'Learning question', 'Interpret', 'Change one thing', 'Save', 'Source rights', '60 seconds']:
                self.assertIn(phrase, text)
            self.assertIn('https://www.who.int/', text)
        for raw in documents.values():
            for required in ['97a1d13dfb23032387ed23804e3d6f4dbc99aec7', 'GNU GPLv3', 'content/LICENSE', 'Apache 2.0',
                             'Charles Frederick Cheffins', 'Ralph R. Frerichs', 'Henry Whitehead',
                             'https://doi.org/10.1016/S0140-6736(00)02442-9', 'https://doi.org/10.3201/eid1411.071629',
                             'https://www.openstreetmap.org/copyright', 'World Bank', 'John Oeltmann']:
                self.assertIn(required, raw)
        intro = nbformat.read(ROOT/'content/index.ipynb', as_version=4)
        self.assertIn('projects/cholera-1854-basic/index.ipynb', intro.cells[0].source)
        browser = nbformat.read(ROOT/'content/foundations/browser-python.ipynb', as_version=4)
        self.assertIn('../projects/cholera-1854-basic/index.ipynb', browser.cells[-1].source)


if __name__ == '__main__':
    unittest.main()
