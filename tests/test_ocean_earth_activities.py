"""Numerical and evidence contracts for the original Ocean/Earth refresh."""
import contextlib
import copy
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET

import nbformat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from generate import seed_project
from ocean_earth_material import CUBE_CODE, EARTH_LESSONS, OCEAN_CODE, OCEAN_LESSONS


def run_cells(slug, replacements=None):
    nb = nbformat.read(ROOT/'content/projects'/slug/'index.ipynb', as_version=4)
    namespace, displayed = {}, []
    text = io.StringIO()
    for before in (replacements or {}):
        assert any(before in c.source for c in nb.cells if c.cell_type == 'code'), before
    with patch('IPython.display.display', side_effect=displayed.append), contextlib.redirect_stdout(text):
        for cell in nb.cells:
            if cell.cell_type != 'code':
                continue
            source = cell.source
            for before, after in (replacements or {}).items():
                source = source.replace(before, after)
            exec(compile(source, slug, 'exec'), namespace)
    return namespace, displayed, text.getvalue()


def plotted_bars(figure):
    """Read category/value pairs from the SVG rows drawn by the shared helper."""
    root = ET.fromstring(figure.data)
    rows = {}
    for node in root.findall('{http://www.w3.org/2000/svg}text'):
        rows.setdefault(node.attrib.get('y'), []).append(node.text)
    return {texts[0]: float(texts[1]) for texts in rows.values() if len(texts) == 2}


class OceanEarthActivities(unittest.TestCase):
    def test_ocean_defaults_keep_ambiguity_and_inclusive_boundary(self):
        state, figures, text = run_cells('global-fishing-watch-and-dark-vessels')
        self.assertEqual(state['candidates'], {'S1':['A'], 'S2':['B','C'], 'S3':['D'], 'S4':[]})
        self.assertEqual(state['counts'], {'unique candidate':2, 'ambiguous':1, 'unmatched':1})
        self.assertEqual(state['denominator'], 4)
        self.assertIn('Unmatched fraction: 0.25', text)
        self.assertIn('2 unique-candidate, 1 ambiguous, 1 unmatched of 4', text)
        svg = ET.fromstring(figures[-1].data)
        self.assertIn('1 km / 5 min', svg.find('{http://www.w3.org/2000/svg}title').text)
        self.assertEqual(plotted_bars(figures[-1]), {'unique candidate':2, 'ambiguous':1, 'unmatched':1})

    def test_ocean_instructed_gate_edits_reach_current_text_and_svg(self):
        for replacement, expected, title in [
            ({'time_gate_min = 5':'time_gate_min = 15'}, (3,1,0), '1 km / 15 min'),
            ({'distance_gate_km = 1.0':'distance_gate_km = 0.99'}, (1,1,2), '0.99 km / 5 min')]:
            state, figures, text = run_cells('global-fishing-watch-and-dark-vessels', replacement)
            self.assertEqual(tuple(state['counts'].values()), expected)
            self.assertIn(f'{expected[0]} unique-candidate, {expected[1]} ambiguous, {expected[2]} unmatched of 4', text)
            self.assertIn(title, ET.fromstring(figures[-1].data).find('{http://www.w3.org/2000/svg}title').text)
            self.assertEqual(plotted_bars(figures[-1]), dict(zip(['unique candidate','ambiguous','unmatched'],expected)))
            self.assertIn('No category determines legality', text)

    def test_cube_zero_missing_variable_masks_and_final_interval(self):
        state, figures, text = run_cells('zarr-sql-views')
        self.assertEqual(state['interval_days'], [8,5])
        self.assertEqual(state['support']['burned_ha'], dict(covered_cell_days=18,possible_cell_days=26,observed_rows=3,observed_total=10,weighted_mean=None))
        self.assertEqual(state['support']['temperature_c']['covered_cell_days'], 21)
        self.assertAlmostEqual(state['support']['temperature_c']['weighted_mean'], 450/21)
        self.assertIn('10.000 ha observed total', text)
        self.assertIn('21.429 C weighted mean', text)
        self.assertIn('coverage 18/26', text)
        self.assertIn('coverage 21/26', text)
        self.assertEqual(plotted_bars(figures[-1]), {'burned_ha':18, 'temperature_c':21, 'possible support':26})
        # The eight-day observed zero must contribute coverage, not disappear.
        self.assertEqual(state['summarize_support']([{'period':0,'burned_ha':0,'temperature_c':None}], [8])['burned_ha']['covered_cell_days'], 8)

    def test_cube_all_missing_is_unknown_and_does_not_borrow_mask(self):
        state, _, _ = run_cells('zarr-sql-views')
        for variable, other in [('burned_ha','temperature_c'),('temperature_c','burned_ha')]:
            rows = copy.deepcopy(state['cube_rows'])
            for row in rows:
                row[variable] = None
            result = state['summarize_support'](rows, state['interval_days'])
            self.assertEqual(result[variable]['covered_cell_days'], 0)
            self.assertIsNone(result[variable]['observed_total'])
            self.assertIsNone(result[variable]['weighted_mean'])
            self.assertEqual(result[other], state['support'][other])
        # Execute the actual edited lesson so the printed unknown and SVG zero agree.
        state, figures, text = run_cells('zarr-sql-views', {'support = summarize_support(cube_rows, interval_days)':
            "for row in cube_rows:\n    row['burned_ha'] = None\nsupport = summarize_support(cube_rows, interval_days)"})
        self.assertIn('unknown ha observed total; 0/4 rows; coverage 0/26', text)
        self.assertIn('0.00', figures[-1].data)

    def test_cube_instructed_equal_duration_edit_changes_weather_weighting(self):
        state, _, _ = run_cells('zarr-sql-views', {"('2021-12-27', '2022-01-01')":"('2021-12-27', '2022-01-04')"})
        self.assertEqual(state['interval_days'], [8,8])
        self.assertEqual(state['support']['burned_ha']['observed_total'], 10)
        self.assertEqual(state['support']['temperature_c']['weighted_mean'], 20)
        self.assertEqual(state['support']['temperature_c']['covered_cell_days'], 24)

    def test_seeds_and_exact_course_link_and_audit_contracts(self):
        records=json.loads((ROOT/'catalog/repositories.json').read_text(encoding='utf-8'))['repositories']
        audit=json.loads((ROOT/'catalog/launch-checks.json').read_text(encoding='utf-8'))['results']
        observed={(r['repository'],r['url']):r['status'] for r in audit}
        for slug in ['zarr-sql-views','global-fishing-watch-and-dark-vessels']:
            record=next(r for r in records if r['slug']==slug)
            canonical=nbformat.read(ROOT/'content'/record['notebook'],as_version=4)
            with patch('generate.notebook') as seeded:
                seed_project(record)
            cells=seeded.call_args.args[1]
            self.assertEqual([c['source'].strip() for c in cells if c['cell_type']=='code'],
                             [c.source.strip() for c in canonical.cells if c.cell_type=='code'])
            text='\n'.join(c.source for c in canonical.cells if c.cell_type=='markdown')
            if slug=='zarr-sql-views':
                self.assertEqual(len(EARTH_LESSONS),30)
                for _,_,url in EARTH_LESSONS:
                    self.assertIn(url,text)
                    self.assertTrue(any(r['url']==url for r in record['resources']))
            else:
                for _,_,_,filename in OCEAN_LESSONS:
                    self.assertIn('/blob/'+record['source_commit']+'/content/'+filename,text)
            for res in record['resources']:
                self.assertEqual(observed[(record['name'],res['url'])],res['http_status'])


if __name__ == '__main__':
    unittest.main()
