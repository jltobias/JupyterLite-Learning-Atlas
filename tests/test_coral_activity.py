"""Behavior, citation and integration contracts for the original reef activity."""
import contextlib
import ast
from collections import Counter
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET

import nbformat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from coral_material import CORAL_COMMIT, CORAL_REPO
from generate import seed_project

NOTEBOOK = ROOT / 'content/projects/coral-reef-one-health/index.ipynb'
NS = '{http://www.w3.org/2000/svg}'


def run_activity(replacements=None, notebook=NOTEBOOK):
    nb = nbformat.read(notebook, as_version=4)
    state, displayed, output = {}, [], io.StringIO()
    for before in replacements or {}:
        assert any(before in c.source for c in nb.cells if c.cell_type == 'code'), before
    with patch('IPython.display.display', side_effect=displayed.append), contextlib.redirect_stdout(output):
        for cell in nb.cells:
            if cell.cell_type != 'code':
                continue
            source = cell.source
            for before, after in (replacements or {}).items():
                source = source.replace(before, after)
            exec(compile(source, 'coral activity', 'exec'), state)
    return state, ET.fromstring(displayed[-1].data), output.getvalue()


class CoralActivityTests(unittest.TestCase):
    def test_default_values_missing_coverage_and_accessible_svg(self):
        state, figure, text = run_activity()
        self.assertAlmostEqual(state['results']['A']['index'], .65)
        self.assertAlmostEqual(state['results']['B']['index'], .35)
        self.assertEqual(state['results']['C'], dict(index=None, coverage=.75, observed=1))
        self.assertIn('A: teaching index 0.650; observed weight coverage 100%', text)
        self.assertIn('C: teaching index unknown; observed weight coverage 75%', text)
        self.assertIn("['A', 'B']", text)
        self.assertIn('arbitrary normalized 0–1', text)
        self.assertIn('not a validated health or conservation index', text)
        self.assertIn('weights 3:1', figure.find(NS + 'title').text)
        self.assertIn('C: index None, observed weight coverage 75%', figure.find(NS + 'desc').text)
        self.assertEqual([n.text for n in figure.findall(NS + 'text') if n.text in ['0.650','0.350','unknown']], ['0.650','0.350','unknown'])

    def test_instructed_weight_edit_changes_text_svg_and_ordering(self):
        state, figure, text = run_activity({'weights = (3.0, 1.0)': 'weights = (1.0, 3.0)'})
        self.assertAlmostEqual(state['results']['A']['index'], .35)
        self.assertAlmostEqual(state['results']['B']['index'], .65)
        self.assertIsNone(state['results']['C']['index'])
        self.assertEqual(state['results']['C']['coverage'], .25)
        self.assertIn("['B', 'A']", text)
        self.assertIn('C: teaching index unknown; observed weight coverage 25%', text)
        self.assertIn('weights 1:3', figure.find(NS + 'title').text)
        self.assertIn('coverage 25%', [n.text for n in figure.findall(NS + 'text')])
        plotted = [float(r.attrib['width']) for r in figure.findall(NS + 'rect') if r.attrib.get('fill') == '#16756b']
        self.assertEqual(plotted, [126, 234])

    def test_observed_zero_and_all_missing_follow_actual_edited_notebook(self):
        state, figure, text = run_activity({"'C': (0.9, None)": "'C': (0.9, 0)"})
        self.assertAlmostEqual(state['results']['C']['index'], .675)
        self.assertEqual(state['results']['C']['coverage'], 1)
        self.assertEqual(state['results']['C']['observed'], 2)
        self.assertIn('C: teaching index 0.675; observed weight coverage 100%', text)
        self.assertNotIn('unknown', [n.text for n in figure.findall(NS + 'text')])
        state, figure, text = run_activity({"'C': (0.9, None)": "'C': (None, None)"})
        self.assertEqual(state['results']['C'], dict(index=None, coverage=0, observed=0))
        self.assertIn('C: teaching index unknown; observed weight coverage 0%; 0/2', text)
        self.assertIn('coverage 0%', [n.text for n in figure.findall(NS + 'text')])
        # A true complete observed zero needs a finite index and full coverage.
        self.assertEqual(state['teaching_index']((0, 0), (3, 1)), dict(index=0, coverage=1, observed=2))

    def test_incomplete_coverage_never_rounds_to_an_endpoint_in_text_or_svg(self):
        for weights, label in [('1000.0, 1.0', '<100%'), ('1.0, 1000.0', '>0%')]:
            with self.subTest(weights=weights):
                state, figure, text = run_activity({'weights = (3.0, 1.0)': f'weights = ({weights})'})
                self.assertIsNone(state['results']['C']['index'])
                self.assertTrue(0 < state['results']['C']['coverage'] < 1)
                self.assertIn(f'C: teaching index unknown; observed weight coverage {label}; 1/2', text)
                self.assertIn('coverage '+label, [n.text for n in figure.findall(NS+'text')])
                self.assertIn('C: index None, observed weight coverage '+label, figure.find(NS+'desc').text)

    def test_canonical_introduction_calculation_print_and_svg_match_catalog(self):
        records = json.loads((ROOT/'catalog/repositories.json').read_text(encoding='utf-8'))['repositories']
        expected = dict(Counter(r['theme'] for r in records))
        state, figure, text = run_activity(notebook=ROOT/'content/index.ipynb')
        self.assertEqual(state['counts'], expected)
        self.assertEqual(sum(state['counts'].values()), len(records))
        printed = text.split('Public catalog themes — repository metadata | repositories:',1)[1].strip()
        self.assertEqual(ast.literal_eval(printed), expected)
        chart_rows = {}
        for element in figure.findall(NS+'text'):
            chart_rows.setdefault(element.attrib['y'], []).append(element.text)
        actual = {row[0]:float(row[1]) for row in chart_rows.values() if len(row)==2}
        self.assertEqual(actual, expected)
        bars = [element for element in figure.findall(NS+'rect') if element.attrib.get('fill')=='#16756b']
        self.assertEqual(len(bars), len(expected))
        for bar, count in zip(bars, expected.values(), strict=True):
            self.assertAlmostEqual(float(bar.attrib['width']), count/max(expected.values())*440, places=2)
        intro = nbformat.read(ROOT/'content/index.ipynb', as_version=4)
        guidance = intro.cells[0].source
        for phrase in ['foundations/learning-a-model.ipynb', 'design thinking and human-centered iteration',
                       'title-only source stub', 'HTTP 404 on 2026-11-01', 'targeted review on 2026-11-02']:
            self.assertIn(phrase, guidance)
        for route in ['Observe a changing Earth','Rewire global health']:
            section = intro.cells[1].source.split('### '+route+'\n',1)[1].split('### ',1)[0]
            self.assertIn('projects/coral-reef-one-health/index.ipynb', section)

    def test_invalid_weights_fail_before_normalization_or_plot(self):
        for invalid in ['0', '-1', "float('inf')", "float('nan')"]:
            with self.subTest(invalid=invalid), self.assertRaisesRegex(ValueError, 'positive finite'):
                run_activity({'weights = (3.0, 1.0)': f'weights = ({invalid}, 1.0)'})
        state, _, _ = run_activity()
        for values, weights in [((.8,), (3,1)), ((.8,.2), ()), ((.8,.2), (True,1))]:
            with self.assertRaises(ValueError):
                state['teaching_index'](values, weights)
        for values in [(float('nan'), .2), (.8, float('inf')), (-.1, .2), (1.1, .2)]:
            with self.assertRaisesRegex(ValueError, 'Descriptors'):
                state['teaching_index'](values, (3,1))
        self.assertAlmostEqual(state['teaching_index']((.8,.2), (1e308,1e308))['index'], .5)

    def test_seed_recreates_code_and_preserves_authored_notebook(self):
        catalog = json.loads((ROOT / 'catalog/repositories.json').read_text(encoding='utf-8'))
        record = next(r for r in catalog['repositories'] if r['slug'] == 'coral-reef-one-health')
        canonical = nbformat.read(NOTEBOOK, as_version=4)
        with patch('generate.notebook') as seeded:
            seed_project(record)
        self.assertEqual([c['source'].strip() for c in seeded.call_args.args[1] if c['cell_type']=='code'],
                         [c.source.strip() for c in canonical.cells if c.cell_type=='code'])
        work = ROOT / '_build/test-coral-seed'
        work.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=work) as folder, patch('generate.ROOT', Path(folder)):
            seed_project(record)
            target = Path(folder) / 'content' / record['notebook']
            self.assertTrue(target.exists())
            target.write_text('authored sentinel', encoding='utf-8')
            seed_project(record)
            self.assertEqual(target.read_text(encoding='utf-8'), 'authored sentinel')

    def test_catalog_and_primary_credit_links_are_consistent(self):
        catalog = json.loads((ROOT / 'catalog/repositories.json').read_text(encoding='utf-8'))
        records = catalog['repositories']
        discovery = json.loads((ROOT / 'catalog/discovery.json').read_text(encoding='utf-8'))
        self.assertEqual({r['name'] for r in records if r['category']=='jupyterlite'},
                         {r['name'] for r in discovery['repositories'] if r['url'].split('/')[3].lower()=='jltobias'
                          and r['name'].lower().startswith('jupyterlite-')
                          and r['name']!='JupyterLite-Learning-Atlas'})
        self.assertTrue({r['name'] for r in records} <= {r['name'] for r in discovery['repositories']})
        self.assertEqual(discovery['baseline_inspection']['inspected_on'], '2026-11-01')
        self.assertTrue(any(r['repository']=='JupyterLite-Coral-Reef-One-Health' and r['inspected_on']=='2026-11-02'
                            for r in discovery['targeted_additions']))
        record = next(r for r in records if r['slug']=='coral-reef-one-health')
        self.assertEqual(record['source_commit'], CORAL_COMMIT)
        self.assertEqual(record['inspected_on'], '2026-11-02')
        self.assertIn('targeted', catalog['scope'].lower())
        audit = json.loads((ROOT / 'catalog/launch-checks.json').read_text(encoding='utf-8'))
        self.assertEqual(len(audit['results']), sum(len(r['resources']) for r in records))
        new = [r for r in audit['results'] if r['repository']==record['name']]
        self.assertEqual(len(new), 11)
        self.assertEqual({r['url'] for r in new}, {r['url'] for r in record['resources']})
        self.assertTrue(all(r['status']==200 and r['checked_on']=='2026-11-02' for r in new))
        text = '\n'.join(c.source for c in nbformat.read(NOTEBOOK, as_version=4).cells if c.cell_type=='markdown')
        for name in ['01-reef-mapping.ipynb', '02-one-health.ipynb']:
            self.assertIn(f'{CORAL_REPO}/blob/{CORAL_COMMIT}/content/{name}', text)
            self.assertIn('?path='+name, text)
        for document in ['README.md', 'REFERENCES.md', 'content/references.ipynb']:
            raw = (ROOT / document).read_text(encoding='utf-8')
            for required in [CORAL_COMMIT, 'https://allencoralatlas.org/methods/', 'https://allencoralatlas.org/tou/',
                             'https://www.livingoceansfoundation.org/mapping-the-worlds-coral-reefs/',
                             'https://landsat.gsfc.nasa.gov/wp-content/uploads/2012/07/coral-l7.pdf',
                             'https://doi.org/10.1016/j.jip.2021.107538', 'https://www.who.int/health-topics/one-health',
                             'https://github.com/luismmontilla/awesome-coral-research/blob/master/LICENCE.md',
                             'https://coralreefwatch.noaa.gov/satellite/index.php', 'https://datamermaid.org/',
                             'https://coralnet.ucsd.edu/', 'https://obis.org/', 'No repository-wide license selected']:
                self.assertIn(required, raw, (document, required))


if __name__ == '__main__':
    unittest.main()
