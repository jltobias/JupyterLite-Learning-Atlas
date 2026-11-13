"""Protect complete, visible credits for actual bundled observations and tables."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from data_credits import validate_data_credits


class DatasetCreditsTests(unittest.TestCase):
    def test_every_declared_data_file_has_visible_current_credits(self):
        result=validate_data_credits(ROOT)
        self.assertGreaterEqual(result['dataset_families'],40)
        self.assertGreater(result['required_data_placements'],300)
        text=(ROOT/'README.md').read_text(encoding='utf-8')
        for credit in ['INV-045237','INV-044979','European Union, 1995-2026',
                       'USGS EROS','NASA Landsat','OpenStreetMap contributors',
                       'Contains National Statistics data','Contains Ordnance Survey data',
                       '10.5281/zenodo.5914709','10.5194/gmd-16-7461-2023',
                       'Porimol Chandro','SYNTHETIC_DEMO_NOT_IHME']:
            self.assertIn(credit,text)

    def prepared_root(self,folder):
        root=Path(folder)
        for name in ['catalog/data-attributions.json','catalog/source-library.json',
                     'README.md','REFERENCES.md','content/references.ipynb']:
            target=root/name
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/name,target)
        ledger=ROOT/'catalog/map-data.json'
        if ledger.exists():shutil.copyfile(ledger,root/'catalog/map-data.json')
        register=json.loads((ROOT/'catalog/data-attributions.json').read_text(encoding='utf-8'))
        for row in register['datasets']:
            for name in row.get('site_files',[]):
                target=root/'site'/name;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/'site'/name,target)
        return root

    def test_site_data_cannot_be_published_without_readme_citation(self):
        with tempfile.TemporaryDirectory() as folder:
            root=self.prepared_root(folder)
            path=root/'catalog/map-data.json';path.parent.mkdir(exist_ok=True)
            ledger=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'assets':[]}
            ledger['assets'].append({'path':'site/data/new-observations.json'})
            path.write_text(json.dumps(ledger),encoding='utf-8')
            with self.assertRaisesRegex(AssertionError,'Site dataset files missing README attribution'):
                validate_data_credits(root)

    def test_entirely_undeclared_site_dataset_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=self.prepared_root(folder)
            (root/'site/data/forgotten-observations.json').write_text('{"observed":42}',encoding='utf-8')
            with self.assertRaisesRegex(AssertionError,'Undeclared published site dataset.*forgotten-observations'):
                validate_data_credits(root)

    def test_explicit_generated_site_metadata_still_allowed(self):
        with tempfile.TemporaryDirectory() as folder:
            root=self.prepared_root(folder)
            for name in ['catalog.json','source-library.json']:
                (root/'site/data'/name).write_text('{}',encoding='utf-8')
            self.assertEqual(validate_data_credits(root),validate_data_credits(ROOT))

    def test_site_citation_cannot_escape_public_site_tree(self):
        with tempfile.TemporaryDirectory() as folder:
            root=self.prepared_root(folder)
            path=root/'catalog/data-attributions.json'
            register=json.loads(path.read_text(encoding='utf-8'))
            register['datasets'][0]['site_files']=['../README.md']
            path.write_text(json.dumps(register),encoding='utf-8')
            with self.assertRaisesRegex(AssertionError,'Unsafe site dataset path'):
                validate_data_credits(root)

    def test_population_input_cannot_be_published_without_its_data_credits(self):
        with tempfile.TemporaryDirectory() as folder:
            root=self.prepared_root(folder)
            path=root/'catalog/data-attributions.json'
            register=json.loads(path.read_text(encoding='utf-8'))
            actual_input='courses/population-data-comparison/population.json'
            for entry in register['datasets']:
                entry['files']=[name for name in entry['files'] if name!=actual_input]
            path.write_text(json.dumps(register),encoding='utf-8')
            with self.assertRaisesRegex(AssertionError,'missing README attribution'):
                validate_data_credits(root)

    def test_stale_readme_copyright_notice_is_detected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=self.prepared_root(folder)
            path=root/'README.md'
            text=path.read_text(encoding='utf-8')
            self.assertIn('European Union, 1995-2026',text)
            path.write_text(text.replace('European Union, 1995-2026','removed notice'),encoding='utf-8')
            with self.assertRaisesRegex(AssertionError,'Stale dataset credits: README'):
                validate_data_credits(root)


if __name__=='__main__':
    unittest.main()
