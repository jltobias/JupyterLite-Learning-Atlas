"""Execute the actual EO notebook, edit its taught inputs and inspect its SVG."""
import contextlib
import ast
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET

import nbformat
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import generate
from atlas_paths import canonical_notebooks
from eo_material import ACTIVITY, BASE, COMMIT, FILES, PIN, bibliography, source_overview
from lesson_material import PATHS
from validate import validate_catalog_sources

NS = '{http://www.w3.org/2000/svg}'
EO = ROOT/'content/projects/eo-satellite-guide/index.ipynb'
# The pre-EO milestone contains 38 project notebooks and these nine other paths.
# Later chapters are outside this historical preservation contract.
BASELINE_NONPROJECT = (
    'contributor-guide.ipynb',
    'foundations/browser-python.ipynb',
    'foundations/evidence-ai.ipynb',
    'foundations/learning-a-model.ipynb',
    'foundations/spatial-thinking.ipynb',
    'index.ipynb',
    'references.ipynb',
    'synthesis/global-health.ipynb',
    'visual-provenance.ipynb',
)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')).hexdigest()


def printed_proposals(text):
    heading = 'PRINTED PROPOSALS ONLY — no endpoint, method, file, network or model call:\n'
    return json.loads(text.split(heading,1)[1])


def run_eo(replacements=None):
    notebook = nbformat.read(EO, as_version=4)
    state, figures, text = {}, [], io.StringIO()
    with patch('IPython.display.display', side_effect=figures.append), contextlib.redirect_stdout(text):
        for cell in notebook.cells:
            if cell.cell_type != 'code':
                continue
            source = cell.source
            for before, after in (replacements or {}).items():
                source = source.replace(before, after)
            exec(compile(source, 'canonical EO activity', 'exec'), state)
    figure = ET.fromstring(figures[-1].data)
    return state, figure, text.getvalue()


class EOActivityTests(unittest.TestCase):
    def assert_routes(self, state, figure, expected):
        self.assertEqual(state['counts'], expected)
        self.assertEqual(sum(expected.values()), 5)
        self.assertEqual(figure.attrib['role'], 'img')
        self.assertTrue(figure.attrib['aria-label'])
        self.assertIn(state['target_property'], figure.find(NS+'title').text)
        for row in state['routed']:
            group = figure.find(f"{NS}g[@id='candidate-{row['id']}']")
            self.assertIsNotNone(group)
            self.assertEqual(group.attrib['data-route'], row['route'])
            mark = group.find(f"{NS}rect[@class='route-mark']")
            self.assertEqual(float(mark.attrib['x']), state['lane_x'][row['route']])
            self.assertIn(row['id'], ' '.join(group.itertext()))
            self.assertIn(row['route'], ' '.join(group.itertext()))
            self.assertIn(row['id']+': collection ', figure.find(NS+'desc').text)
        self.assertEqual(len(state['proposals']), expected['draft'])

    def test_default_routes_query_and_unknowns_are_printed_and_drawn(self):
        state, figure, text = run_eo()
        self.assert_routes(state, figure, dict(draft=1, incompatible=2, unmapped=1, **{'browse-static':1, 'check-api':0}))
        self.assertEqual(len({r['mission'] for r in state['candidates']}), 4)
        self.assertEqual([p['intent']['candidate'] for p in state['proposals']], ['optical-sr'])
        proposal = state['proposals'][0]
        self.assertIs(proposal['simulation'], True)
        self.assertEqual(proposal['status'], 'proposal-only')
        self.assertEqual(proposal['search'], {'collections':['demo-optical-sr'], 'bbox':[-10,-5,10,5],
            'datetime':'2024-06-01T00:00:00Z/2024-06-30T23:59:59Z', 'limit':3})
        self.assertEqual(printed_proposals(text), [{
            'simulation':True, 'status':'proposal-only',
            'intent':{'candidate':'optical-sr', 'mission':'demo-optical', 'property':'surface_reflectance', 'processing':'L2A'},
            'search':{'collections':['demo-optical-sr'], 'bbox':[-10,-5,10,5],
                      'datetime':'2024-06-01T00:00:00Z/2024-06-30T23:59:59Z', 'limit':3},
        }])
        self.assertIn('optical-sr | demo-optical | active | collection: demo-optical-sr | property: surface_reflectance | processing: L2A | route: draft',text)
        self.assertIn('optical-toa | demo-optical | active | collection: demo-optical-toa | property: toa_reflectance | processing: L1C | route: incompatible',text)
        self.assertIn('radar-grd | demo-radar | active | collection: demo-radar-grd | property: backscatter | processing: GRD | route: incompatible',text)
        self.assertFalse({'endpoint','method','url'} & set(proposal))
        self.assertIn('unknown (None)', text)
        self.assertIn('unknown (None)', ' '.join(figure.itertext()))
        archive = next(r for r in state['routed'] if r['id']=='archive-static')
        self.assertEqual((archive['status'], archive['route']), ('retired','browse-static'))

    def test_backscatter_edit_moves_marks_and_only_radar_drafts(self):
        state, figure, text = run_eo({"target_property = 'surface_reflectance'":"target_property = 'backscatter'",
                                    "target_processing = 'L2A'":"target_processing = 'GRD'"})
        self.assert_routes(state, figure, dict(draft=1, incompatible=4, unmapped=0, **{'browse-static':0, 'check-api':0}))
        self.assertEqual([p['intent']['candidate'] for p in state['proposals']], ['radar-grd'])
        self.assertEqual(state['proposals'][0]['search']['collections'], ['demo-radar-grd'])
        self.assertIn('backscatter / GRD', text)

    def test_unconfirmed_api_and_missing_mapping_move_the_first_mark(self):
        first_line = next(line for line in ACTIVITY.splitlines() if "'id': 'optical-sr'" in line)
        changed = first_line.replace("'item_search': True", "'item_search': False")
        state, figure, _ = run_eo({first_line:changed})
        self.assert_routes(state, figure, dict(draft=0, incompatible=2, unmapped=1, **{'browse-static':1, 'check-api':1}))
        self.assertEqual(state['proposals'], [])
        state, figure, text = run_eo({"'collection': 'demo-optical-sr'":"'collection': None"})
        self.assert_routes(state, figure, dict(draft=0, incompatible=2, unmapped=2, **{'browse-static':1, 'check-api':0}))
        self.assertEqual(text.count('collection: unknown (None)'), 2)
        # Mismatch is checked before missing mapping or static/API capability.
        row = dict(state['candidates'][0], property='other', collection=None, kind='static')
        self.assertEqual(state['route_candidate'](row, 'surface_reflectance', 'L2A'), 'incompatible')
        row = dict(state['candidates'][0], collection='demo-optical-sr', kind='api', item_search=1)
        self.assertEqual(state['route_candidate'](row, 'surface_reflectance', 'L2A'), 'check-api')

    def test_invalid_taught_query_edits_raise_before_any_proposal_is_emitted(self):
        changes = [
            {'bbox = [-10, -5, 10, 5]':'bbox = [10, -5, -10, 5]'},
            {'bbox = [-10, -5, 10, 5]':'bbox = [0, 0, 0, 5]'},
            {'bbox = [-10, -5, 10, 5]':'bbox = [-181, -5, 10, 5]'},
            {'bbox = [-10, -5, 10, 5]':'bbox = [-10, -91, 10, 5]'},
            {'bbox = [-10, -5, 10, 5]':"bbox = [-10, -5, float('nan'), 5]"},
            {'bbox = [-10, -5, 10, 5]':"bbox = [-10, -5, float('inf'), 5]"},
            {'bbox = [-10, -5, 10, 5]':'bbox = [True, -5, 10, 5]'},
            {'bbox = [-10, -5, 10, 5]':'bbox = [0, 0, 10**1000, 5]'},
            {"start = '2024-06-01T00:00:00Z'":"start = '2024-07-01T00:00:00Z'"},
            {"start = '2024-06-01T00:00:00Z'":"start = '2024-02-30T00:00:00Z'"},
            {"start = '2024-06-01T00:00:00Z'":"start = '2024-6-1T00:00:00Z'"},
            {"start = '2024-06-01T00:00:00Z'":"start = '2024-06-01T0:0:0Z'"},
            {'limit = 3':'limit = 0'}, {'limit = 3':'limit = 101'},
            {'limit = 3':'limit = 3.0'}, {'limit = 3':'limit = True'},
        ]
        for edit in changes:
            displayed, text = [], io.StringIO()
            with self.subTest(edit=edit), patch('IPython.display.display', side_effect=displayed.append), contextlib.redirect_stdout(text):
                with self.assertRaises(ValueError):
                    state = {}
                    for cell in nbformat.read(EO,as_version=4).cells:
                        if cell.cell_type != 'code':
                            continue
                        source = cell.source
                        for before,after in edit.items():
                            source = source.replace(before,after)
                        exec(compile(source,'invalid EO query edit','exec'),state)
                self.assertNotIn('PRINTED PROPOSALS', text.getvalue())
                self.assertEqual(displayed, [])
                self.assertNotIn('proposals',state)

    def test_valid_query_edits_propagate_without_implicitly_requesting_data(self):
        state, _, text = run_eo({'bbox = [-10, -5, 10, 5]':'bbox = [0, 1, 2, 3]', 'limit = 3':'limit = 100',
            "start = '2024-06-01T00:00:00Z'":"start = '2024-06-30T23:59:59Z'"})
        self.assertEqual(state['proposals'][0]['search']['bbox'], [0,1,2,3])
        self.assertEqual(state['proposals'][0]['search']['limit'], 100)
        self.assertEqual(state['proposals'][0]['search']['datetime'], '2024-06-30T23:59:59Z/2024-06-30T23:59:59Z')
        self.assertEqual(printed_proposals(text), [{
            'simulation':True, 'status':'proposal-only',
            'intent':{'candidate':'optical-sr', 'mission':'demo-optical', 'property':'surface_reflectance', 'processing':'L2A'},
            'search':{'collections':['demo-optical-sr'], 'bbox':[0,1,2,3],
                      'datetime':'2024-06-30T23:59:59Z/2024-06-30T23:59:59Z', 'limit':100},
        }])

    def test_edited_id_stays_well_formed_in_actual_svg_attributes(self):
        edited_id = 'optical & "sensor"'
        state,figure,text = run_eo({"'id': 'optical-sr'": "'id': '"+edited_id+"'"})
        group = next(group for group in figure.findall(NS+'g') if group.attrib['id']=='candidate-'+edited_id)
        self.assertEqual(group.attrib['data-route'],'draft')
        self.assertIn(edited_id,' '.join(group.itertext()))
        self.assertEqual(printed_proposals(text)[0]['intent']['candidate'],edited_id)
        self.assertEqual(state['counts']['draft'],1)

    def test_same_sized_fixture_mission_edit_updates_actual_header(self):
        state,figure,text = run_eo({"'id': 'optical-toa', 'mission': 'demo-optical'":
                                   "'id': 'optical-toa', 'mission': 'demo-other-optical'"})
        self.assertEqual(len(state['candidates']),5)
        self.assertIn('Fictional candidates: 5 | fictional missions: 5',text)
        header = figure.find(f"{NS}text[@y='60']")
        self.assertIn('5 candidates / 5 missions',header.text)

    def test_default_print_assertion_detects_empty_json_print_regression(self):
        _,_,text = run_eo({'print(json.dumps(proposals, indent=2))':'print(json.dumps([], indent=2))'})
        self.assertEqual(printed_proposals(text),[])
        # The default test's complete printout assertion must reject this mutation.
        with patch(__name__+'.run_eo',return_value=run_eo({
                'print(json.dumps(proposals, indent=2))':'print(json.dumps([], indent=2))'})):
            with self.assertRaises(AssertionError):
                self.test_default_routes_query_and_unknowns_are_printed_and_drawn()

    def test_fresh_browser_runtime_assertions_match_the_canonical_activity(self):
        state,_,_ = run_eo()
        tree = ast.parse((ROOT/'scripts/check_runtime.py').read_text(encoding='utf-8'))
        assignment = next(node for node in tree.body if isinstance(node,ast.Assign)
            and any(isinstance(target,ast.Name) and target.id=='EO_ASSERTIONS' for target in node.targets))
        exec(compile(ast.literal_eval(assignment.value),'EO browser runtime assertions','exec'),state)


class EOIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads((ROOT/'catalog/repositories.json').read_text(encoding='utf-8'))
        self.record = next(r for r in self.catalog['repositories'] if r['slug']=='eo-satellite-guide')

    def test_catalog_evidence_totals_and_all_prior_records_are_preserved(self):
        schema = json.loads((ROOT/'catalog/repositories.schema.json').read_text(encoding='utf-8'))
        validate_catalog_sources(self.catalog,schema)
        records = self.catalog['repositories']
        discovery = json.loads((ROOT/'catalog/discovery.json').read_text(encoding='utf-8'))
        audit = json.loads((ROOT/'catalog/launch-checks.json').read_text(encoding='utf-8'))
        # Minimum milestone sizes permit later, independently reviewed additions.
        self.assertGreaterEqual(len(records),39)
        self.assertGreaterEqual(sum(r['category']=='jupyterlite' for r in records),32)
        self.assertGreaterEqual(len(discovery['repositories']),65)
        self.assertGreaterEqual(len(audit['results']),168)
        self.assertGreaterEqual(sum(r['status']==200 for r in audit['results']),166)
        self.assertTrue({r['source_url'].rstrip('/') for r in records} <=
                        {r['url'].rstrip('/') for r in discovery['repositories']})
        notebooks = canonical_notebooks()
        self.assertEqual({ROOT/'content'/r['notebook'] for r in records},
                         {p for p in notebooks if p.parent.parent.name=='projects'})
        for value,expected in [
            (records[:38], '5dba1e654688bc3eb8ea1c393be27442943c9f519545687e0a8d56db1e293778'),
            (discovery['repositories'][:64], '8c539fee7c82ad36d19b15e4bf35bb64b3da5e24fa99de299d72ef46d27f9dbe'),
            (audit['results'][:158], '4bfc64d0f6d200bb1da081a32417af307d19a0fdc34a450f2acd834c5748718e'),
            (audit['manifest_evidence'][:2], '2e315f40a19a69be2f32346f13bf72bdd2ad7a64e2cb4249ce1a08da125e04c0'),
        ]:
            self.assertEqual(digest(value),expected)
        self.assertEqual(len(self.record['resources']),10)
        self.assertEqual([(r['url'],r['resolved_url'],r['status'],r['checked_on']) for r in audit['results'][158:168]],
                         [(r['url'],r['url'],200,'2026-11-02') for r in self.record['resources']])
        eo_evidence = [item for item in audit['manifest_evidence'] if item['repository']==self.record['name']]
        self.assertEqual(len(eo_evidence),1)
        evidence = eo_evidence[0]
        self.assertEqual(evidence['sha256'],'0e3514a09d0f4d432430ad6ae1a1867e30bbd7a20096bdddec9200173781d74e')
        self.assertEqual(evidence['confirmed_notebook_basenames'], [name for name,_ in FILES])
        self.assertEqual((evidence['source_commit'], evidence['checked_on']), (COMMIT,'2026-11-02'))

    def test_all_previous_notebook_code_and_stac_outputs_remain_unchanged(self):
        notebooks = canonical_notebooks()
        self.assertGreaterEqual(len(notebooks),48)
        baseline_paths = {ROOT/'content'/r['notebook'] for r in self.catalog['repositories'][:38]}
        baseline_paths.update(ROOT/'content'/name for name in BASELINE_NONPROJECT)
        self.assertEqual(len(baseline_paths),47)
        self.assertTrue(baseline_paths | {EO} <= set(notebooks))
        codes = []
        for path in sorted(baseline_paths,key=lambda p:p.as_posix()):
            notebook = nbformat.read(path,as_version=4)
            relative = path.relative_to(ROOT).as_posix()
            codes.append((relative,[cell.source for i,cell in enumerate(notebook.cells)
                if cell.cell_type=='code' and not (relative=='content/index.ipynb' and i==4)]))
        self.assertEqual(digest(codes),'4a4ba3b12879338a5fecaa375b57a6f48b450aa03e19cf548a889be3ee0cdd8e')
        stac = json.loads((ROOT/'content/projects/stac-browser/index.ipynb').read_text(encoding='utf-8'))
        self.assertEqual(digest([c['outputs'] for c in stac['cells'] if c['cell_type']=='code']), 'cdfca2459040c5f75768b7da3e55b6be21fe343322f3b20b49f58cf384b31f43')

    def test_seed_matches_canonical_activity_and_never_overwrites(self):
        canonical = nbformat.read(EO,as_version=4)
        with tempfile.TemporaryDirectory() as folder, patch.object(generate,'ROOT',Path(folder)):
            generate.seed_project(self.record)
            seeded_path = Path(folder)/'content'/self.record['notebook']
            seeded = nbformat.read(seeded_path,as_version=4)
            self.assertEqual([(c.cell_type,c.source) for c in seeded.cells],[(c.cell_type,c.source) for c in canonical.cells])
            seeded_path.write_text('authored sentinel',encoding='utf-8')
            generate.seed_project(self.record)
            self.assertEqual(seeded_path.read_text(encoding='utf-8'),'authored sentinel')
            stac = next(r for r in self.catalog['repositories'] if r['slug']=='stac-browser')
            generate.seed_project(stac)
            self.assertIn('../eo-satellite-guide/index.ipynb',(Path(folder)/'content'/stac['notebook']).read_text(encoding='utf-8'))
        with patch.object(generate,'notebook') as capture:
            generate.seed_foundations(self.catalog['repositories'])
        intro_cells = next(call.args[1] for call in capture.call_args_list if call.args[0]=='index.ipynb')
        self.assertIn('assets/splash-v2.png',intro_cells[0]['source'])
        self.assertIn('AI-generated',intro_cells[0]['source'])
        self.assertIn('SPLASH-PROVENANCE.md',intro_cells[0]['source'])
        self.assertEqual(intro_cells[1]['source'].count('projects/eo-satellite-guide/index.ipynb'),1)

    def test_source_credits_primary_works_and_reciprocal_navigation(self):
        for filename in ['README.md','REFERENCES.md','content/references.ipynb','content/projects/eo-satellite-guide/index.ipynb']:
            text = (ROOT/filename).read_text(encoding='utf-8')
            for name,_ in FILES:
                self.assertIn(PIN+'notebooks/'+name,text)
            for required in [COMMIT,'James L. Tobias','Natural Earth','MIT','CC BY 4.0',
                             'https://www.w3.org/TR/vocab-ssn/','https://www.w3.org/TR/vocab-dcat-3/',
                             'https://www.w3.org/TR/prov-o/','https://earthcode.esa.int/',
                             'https://github.com/radiantearth/stac-api-spec/blob/v1.0.0/item-search/README.md',
                             BASE+'api/contents/all.json']:
                self.assertIn(required,text)
        chapter = '\n'.join(c.source for c in nbformat.read(EO,as_version=4).cells)
        for required in ['OGC API Records','not a deployed connector','many-to-many','human-centered','CDSE','not all free','sameAs']:
            self.assertIn(required,chapter)
        self.assertIn('normal-sized printed evidence',chapter)
        self.assertIn('Open Image in New Tab',chapter)
        self.assertIn('web/app.js',bibliography())
        intro = nbformat.read(ROOT/'content/index.ipynb',as_version=4)
        self.assertEqual(''.join(c.source for c in intro.cells).count('projects/eo-satellite-guide/index.ipynb'),1)
        route = next(keys for title,_,keys in PATHS if title=='Observe a changing Earth')
        self.assertLess(route.index('EO-Satellite-Guide'),route.index('STAC-Browser'))
        toc = yaml.safe_load((ROOT/'content/_toc.yml').read_text(encoding='utf-8'))
        paths = [c['file'] for p in toc['parts'] for c in p['chapters']]
        self.assertEqual(paths.count('projects/eo-satellite-guide/index'),1)
        self.assertEqual(paths[:2],['foundations/browser-python','projects/cholera-1854-basic/index'])

    def test_cover_identity_credit_and_noncount_artwork_bytes(self):
        cover_hash = '09b30e50095b2286df7ea0a1556fd447d1124c83b3ab5dfc68fab4c29877b0f9'
        for name in ['assets/splash-v2.png','content/assets/splash-v2.png']:
            image = (ROOT/name).read_bytes()
            self.assertEqual(hashlib.sha256(image).hexdigest(),cover_hash)
            self.assertEqual(len(image),2450981)
            self.assertEqual((int.from_bytes(image[16:20],'big'),int.from_bytes(image[20:24],'big')),(1774,887))
        intro = nbformat.read(ROOT/'content/index.ipynb',as_version=4)
        self.assertIn('assets/splash-v2.png',intro.cells[0].source)
        self.assertIn('AI-generated conceptual illustration',intro.cells[0].source)
        self.assertIn('SPLASH-PROVENANCE.md',intro.cells[0].source)
        protected = {'atlas-mark.svg':'d5c633a5d7740b6b4857ccdb72ab40cb420aaf14b694f2a39bce86b17f9abda9',
            'capabilities.svg':'0295b11c98518d98e8774c4ba49f45383f18678328b2e1b9738bc1978ee968c3',
            'empathy-iteration.svg':'a8251d0b2d0a1de5e662716c5a6df11debd2a8af6cffddd29fab4d812c58c212',
            'evidence-to-action.svg':'90ff3b2c55b480a9ec8e6b04902e5f94e29f37d5fc22ed20a2d2f1237931c770',
            'splash.svg':'e806a2310592b64324f3e2b28747c2f62f73432517afe04b2dcef458ef0fc959'}
        for name,expected in protected.items():
            normalized = (ROOT/'assets'/name).read_bytes().replace(b'\r\n',b'\n')
            self.assertEqual(hashlib.sha256(normalized).hexdigest(),expected)


if __name__=='__main__':
    unittest.main()
