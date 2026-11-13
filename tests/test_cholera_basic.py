"""Basic preparation, atomic refresh and fresh execution without research checkouts."""
import asyncio
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import nbformat
from nbclient import NotebookClient

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import import_sources as importer
from check_source_runtime import CHOLERA_ASSERTIONS, CHOLERA_MEAN_ASSERTIONS, assert_cholera_row_correspondence
from source_library import load_library, stage_dependencies

FIXTURE=json.loads((ROOT/'tests/fixtures/cholera-basic-source-cells.json').read_text(encoding='utf-8'))


class CholeraBasicTests(unittest.TestCase):
    def make_tree(self,root):
        """Serialize sanitized pinned cells as independent local source inputs."""
        library=copy.deepcopy(load_library());slug='cholera-1854-basic'
        for section in [s for s in library['sections'] if s['course']==slug]:
            fixture=FIXTURE['notebooks'][section['source_path']]
            self.assertEqual(section['source_sha256'],fixture['original_sha256'])
            self.assertEqual(section['source_cell_sha256'],fixture['original_cell_sha256'])
            self.assertTrue(all(set(c)=={'cell_type','source'} for c in fixture['cells']))
            self.assertFalse(any('data:image' in c['source'] or 'attachment:' in c['source'] for c in fixture['cells']))
            notebook=nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell(c['source']) if c['cell_type']=='code' else nbformat.v4.new_markdown_cell(c['source']) for c in fixture['cells']])
            source=root/'pins'/slug/section['source_path'];source.parent.mkdir(parents=True,exist_ok=True);nbformat.write(notebook,source)
            # Test containers omit upstream outputs/media. Original pinned
            # source hashes above are retained in the fixture's scoped notice.
            section['source_sha256']=importer.digest(source.read_bytes())
            section['source_cell_sha256']=importer.cell_digest(notebook)
            for disposition in library['dispositions']:
                if disposition['course']==slug and disposition['source_path']==section['source_path']:
                    disposition['source_sha256']=section['source_sha256'];disposition['source_cell_sha256']=section['source_cell_sha256']
            target=root/'content'/section['notebook'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b'existing destination')
        importer.write_json(root/'catalog/source-library.json',library)
        importer.write_json(root/'site/data/source-library.json',library)
        (root/'content/courses/unchanged.ipynb').write_bytes(b'Unrelated notebook bytes')
        return library

    def refresh(self,root):
        with patch.object(importer,'ROOT',root),patch.object(importer,'DEST',root/'content'),patch.object(importer,'SOURCES',root/'pins'):
            return importer.refresh_basic_notebooks()

    def workspace(self):
        work=ROOT/'_build/test-cholera-basic';work.mkdir(parents=True,exist_ok=True)
        return tempfile.TemporaryDirectory(dir=work)

    def test_pinned_fixture_refresh_matches_canonical_and_repeats_without_other_changes(self):
        canonical=load_library()
        self.assertEqual(canonical,json.loads((ROOT/'site/data/source-library.json').read_text(encoding='utf-8')))
        with self.workspace() as folder:
            root=Path(folder);before=self.make_tree(root);after=self.refresh(root)
            self.assertEqual(after,{**before,'sections':after['sections']})
            self.assertEqual([s for s in after['sections'] if s['course']!='cholera-1854-basic'],[s for s in before['sections'] if s['course']!='cholera-1854-basic'])
            self.assertEqual((root/'content/courses/unchanged.ipynb').read_bytes(),b'Unrelated notebook bytes')
            for section in [s for s in after['sections'] if s['course']=='cholera-1854-basic']:
                expected=next(s for s in canonical['sections'] if s['notebook']==section['notebook'])
                self.assertEqual(section['adapted_cell_sha256'],expected['adapted_cell_sha256'])
                prepared=nbformat.read(root/'content'/section['notebook'],4)
                self.assertEqual(importer.cell_digest(nbformat.v4.new_notebook(cells=prepared.cells[1:])),expected['adapted_cell_sha256'])
                self.assertEqual(prepared.metadata.atlas.modifications,[m for m in section['modifications'] if 'adapter' in m])
                self.assertEqual(section['runtime'],importer.runtime(section['course'],section['source_path'],prepared))
                if section['source_path'].startswith('NB01'):
                    self.assertEqual(sum('Optional video continuation:' in c.source for c in prepared.cells),1)
                    self.assertIn('print(folium.__version__)',next(c.source for c in prepared.cells if 'def gray_street_map' in c.source))
            snapshot={p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertEqual(self.refresh(root),after)
            self.assertEqual(snapshot,{p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_second_source_hash_failure_leaves_all_destinations_and_catalogs_unchanged(self):
        with self.workspace() as folder:
            root=Path(folder);self.make_tree(root)
            second=root/'pins/cholera-1854-basic/NB02-Cholera-Case-Study-Folium-Map-Part-2.ipynb'
            second.write_bytes(second.read_bytes()+b' ')
            before={p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()}
            with self.assertRaisesRegex(AssertionError,'original source hash changed'):self.refresh(root)
            self.assertEqual(before,{p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_adapter_is_narrow_and_row_checks_reject_late_coordinate_or_popup_corruption(self):
        untouched=nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell('!pip install untouched')]);original=copy.deepcopy(untouched)
        self.assertEqual(importer.adapt_basic_notebook('cholera-1854-advanced-1',next(iter(importer.BASIC_NOTEBOOKS)),untouched),[])
        self.assertEqual(untouched,original)
        deaths=[{'LAT':'51.5','LON':'-0.1','DEATHS':'2'},{'LAT':'51.6','LON':'-0.2','DEATHS':'3'}]
        pumps=[{'LAT':'51.7','LON':'-0.3','Street':'A'},{'LAT':'51.8','LON':'-0.4','Street':'B'}]
        rows={'mortality':[{'location':[float(r['LAT']),float(r['LON'])],'popup_location':[float(r['LAT']),float(r['LON'])],'radius':int(r['DEATHS']),'deaths':int(r['DEATHS'])} for r in deaths],
              'pumps':[{'location':[float(r['LAT']),float(r['LON'])],'popup_location':[float(r['LAT']),float(r['LON'])],'street':r['Street']} for r in pumps]}
        self.assertEqual(assert_cholera_row_correspondence(rows,deaths,pumps)['status'],'passed')
        for kind,field,value in [('mortality','location',[0,0]),('mortality','popup_location',[0,0]),('mortality','deaths',99),('pumps','popup_location',[0,0]),('pumps','street','wrong')]:
            broken=copy.deepcopy(rows);broken[kind][1][field]=value
            with self.subTest(kind=kind,field=field),self.assertRaises(AssertionError):assert_cholera_row_correspondence(broken,deaths,pumps)

    def test_fixture_generated_pair_runs_in_fresh_native_kernels_without_prior_outputs(self):
        if sys.platform=='win32':asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        with self.workspace() as folder:
            root=Path(folder);self.make_tree(root);library=self.refresh(root)
            for index,section in enumerate([s for s in library['sections'] if s['course']=='cholera-1854-basic']):
                with self.subTest(notebook=section['notebook']):
                    cwd=stage_dependencies(section['notebook'],root/f'native-{index}')
                    (cwd/'outputs/README.md').unlink();(cwd/'outputs').rmdir()
                    notebook=nbformat.read(root/'content'/section['notebook'],4)
                    guard='''import socket, urllib.request
def _block_network(*args, **kwargs):
    raise RuntimeError("Native Basic proof does not fetch data or tiles")
socket.create_connection = _block_network
urllib.request.urlopen = _block_network
'''
                    notebook.cells.insert(0,nbformat.v4.new_code_cell(guard))
                    assertions=CHOLERA_ASSERTIONS+(CHOLERA_MEAN_ASSERTIONS if section['source_path'].startswith('NB02') else '')
                    notebook.cells.append(nbformat.v4.new_code_cell(assertions))
                    NotebookClient(notebook,timeout=120,kernel_name='python3',resources={'metadata':{'path':str(cwd)}},allow_errors=False).execute()
                    maps=[o.data['text/html'] for c in notebook.cells if c.cell_type=='code' for o in c.outputs if o.output_type in {'display_data','execute_result'} and '<iframe' in o.data.get('text/html','')]
                    self.assertEqual(len(maps),2 if section['source_path'].startswith('NB02') else 6)
                    self.assertTrue(all('grayscale(1)' in value and 'tile.openstreetmap.org' in value for value in maps))
                    self.assertTrue((cwd/'outputs'/('mean_center_df.pickle' if section['source_path'].startswith('NB02') else 'deaths_df.pickle')).is_file())


if __name__=='__main__':unittest.main()
