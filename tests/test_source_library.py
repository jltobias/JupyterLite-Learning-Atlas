"""Cross-course publication boundaries and real local Population calculations."""
import csv
import copy
import hashlib
import importlib.util
import io
import json
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path

import nbformat
import yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from source_library import load_library, source_sections, toc_files, validate_library, stage_dependencies, publishable_files


class SourceLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.library=load_library()

    def test_every_inspected_path_has_a_hashed_disposition_and_scoped_rights(self):
        validate_library(self.library)
        self.assertEqual(self.library['inventory']['imported_sections'],796)
        self.assertEqual(self.library['inventory']['authored_sections'],777)
        self.assertEqual(self.library['inventory']['aliases'],12)
        self.assertEqual(self.library['inventory']['excluded_notebooks'],17)
        excluded=[d for d in self.library['dispositions'] if d['disposition']=='excluded']
        self.assertTrue(all(d['course']=='climate-and-health' and d['source_path'].startswith('content/legacy/') for d in excluded))
        support={s.get('source_path','') for s in self.library['support_files']}
        self.assertFalse(any('gadm' in p.lower() for p in support))
        self.assertFalse(any(p.endswith(('.pickle','.pkl')) for p in support))
        reasons=' '.join(s['reason'] for s in self.library['asset_exclusions'])
        for term in ['GADM','IMF','WHO','prepublication','sandbox','Facility/H3/DEM']:self.assertIn(term,reasons)

    def test_recursive_routes_are_exactly_once_and_keep_editorial_start(self):
        from atlas_paths import canonical_notebooks
        toc=yaml.safe_load((ROOT/'content/_toc.yml').read_text(encoding='utf-8'));routes=list(toc_files(toc))
        self.assertEqual(len(routes),len(set(routes)))
        self.assertEqual(set(routes),{p.relative_to(ROOT/'content').with_suffix('').as_posix() for p in canonical_notebooks()})
        self.assertEqual([c['file'] for c in toc['parts'][0]['chapters']][:2],['foundations/browser-python','projects/cholera-1854-basic/index'])
        for slug in ['spatial-analysis','maps-and-spatial-analyses','geospatial-analyses-and-maps-old','geospatial-analyses-and-maps']:
            self.assertGreaterEqual(sum(s['course']==slug for s in self.library['sections']),90)

    def test_future_course_and_inspected_path_counts_can_grow_without_losing_accounting(self):
        library=copy.deepcopy(self.library)
        catalog=json.loads((ROOT/'catalog/repositories.json').read_text(encoding='utf-8'))
        catalog['repositories'].append({'slug':'future-course'})
        library['courses'].append({'slug':'future-course','commit':'a'*40,'source_notebook_paths':1})
        library['dispositions'].append({'course':'future-course','source_path':'future.ipynb',
            'disposition':'excluded','source_sha256':'b'*64,'source_cell_sha256':'c'*64,
            'reason':'Future source-specific rights exclusion retained as a continuation',
            'source_url':'https://example.org/pinned/future.ipynb'})
        library['inventory']['repositories']+=1
        library['inventory']['inspected_notebook_paths']+=1
        library['inventory']['excluded_notebooks']+=1
        validate_library(library,catalog=catalog)
        duplicate=copy.deepcopy(library)
        duplicate['dispositions'].append(copy.deepcopy(duplicate['dispositions'][-1]))
        duplicate['inventory']['inspected_notebook_paths']+=1
        with self.assertRaisesRegex(AssertionError,'Duplicate source disposition'):
            validate_library(duplicate,catalog=catalog)
        with self.assertRaisesRegex(AssertionError,'coverage differs'):
            validate_library(library,catalog={'repositories':catalog['repositories'][:-1]})

    def test_source_selection_never_autoruns_native_external_or_unknown_lessons(self):
        selected=[s for s in self.library['sections'] if s['runtime']['execution_selected']]
        self.assertEqual(len(selected),18)
        self.assertTrue(all(s['runtime']['class']=='browser-local' or
            (s['course']=='cholera-1854-basic' and s['runtime']['class']=='browser-network') for s in selected))
        self.assertEqual(sum(s['course']=='cholera-1854-basic' for s in selected),2)
        self.assertEqual(sum(s['course']=='population-data-comparison' for s in selected),3)
        self.assertEqual(sum(s['course']=='onehealth' for s in selected),11)
        self.assertTrue(all(s['verification']['status']=='not-run' for s in self.library['sections']))

    def test_population_support_stages_in_fresh_relative_layout_and_preserves_alias(self):
        work=ROOT/'_build/test-source-stage';work.mkdir(parents=True,exist_ok=True)
        path='courses/population-data-comparison/01_real_population.ipynb'
        with tempfile.TemporaryDirectory(dir=work) as folder:
            cwd=stage_dependencies(path,folder,self.library)
            for name in ['population.json','independent_oracle.json','population_tools.py','population_tools_real.py']:
                self.assertTrue((cwd/name).is_file())
            self.assertEqual((cwd/'population_tools.py').read_bytes(),(cwd/'population_tools_real.py').read_bytes())
            self.assertGreater((cwd/'population.json').stat().st_size,5_000_000)
        packaged={p.relative_to(ROOT/'content').as_posix() for p in publishable_files()}
        self.assertIn('courses/onehealth/data/pixels.csv',packaged)
        self.assertIn('courses/eo-satellite-guide/eo_guide.py',packaged)

    def test_population_totals_coverage_and_export_metadata_agree_with_independent_oracle(self):
        folder=ROOT/'content/courses/population-data-comparison'
        spec=importlib.util.spec_from_file_location('atlas_population_test',folder/'population_tools_real.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        data=module.load_population(folder/'population.json');oracle=json.loads((folder/'independent_oracle.json').read_text(encoding='utf-8'))
        results=module.compare(data['layers'],oracle['default_aoi'])
        for result in results:
            expected=oracle['sources'][result['metadata']['id']]
            self.assertAlmostEqual(result['population'],expected['aoi_population'],places=4)
            self.assertAlmostEqual(result['coverage'],expected['aoi_coverage'],places=10)
            self.assertEqual(result['intersected_cells'],expected['aoi_intersected_cells'])
            self.assertIn('CC BY',result['metadata']['license'])
        rows=list(csv.DictReader(io.StringIO(module.export_csv(results))))
        self.assertEqual(len(rows),4)
        for row,result in zip(rows,results):self.assertEqual(json.loads(row['metadata_json']),result['metadata'])

    def test_git_transport_preserves_manifested_source_bytes(self):
        # An untracked CRLF helper passes local hashes but would fail clean CI
        # if Git normalized it during add/checkout. Verify the actual filter.
        relative='content/courses/eo-satellite-guide/eo_guide.py'
        raw=subprocess.check_output(['git','hash-object','--no-filters',relative],cwd=ROOT)
        transported=subprocess.check_output(['git','hash-object','--path='+relative,relative],cwd=ROOT)
        self.assertEqual(raw,transported)


if __name__=='__main__':unittest.main()
