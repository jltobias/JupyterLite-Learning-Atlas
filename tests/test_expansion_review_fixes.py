"""Focused integrity, failure, runtime-contract and edited-input regressions."""
import ast
from contextlib import redirect_stdout, chdir
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import nbformat
import numpy as np
import pandas as pd
import plotly.graph_objects as go

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import import_sources as importer
import append_expansion_catalogs as catalogs
from browser_gis_material import refresh_current_scope
from check_expansion_browser import upload_setup
from climate_plot_oracles import assert_climate_plot
from expansion_material import LESSONS
from expansion_runtime_contracts import WIDGET_CELLS, reviewed_widget_indices

WORK=ROOT/'_build/test-expansion-review';WORK.mkdir(parents=True,exist_ok=True)


def atlas_helper():
    spec=importlib.util.spec_from_file_location('review_atlas_helper',ROOT/'content/courses/c3s-atlas/atlas_helpers.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


class ExpansionReviewFixes(unittest.TestCase):
    def test_browser_gate_helpers_import_with_playwright_blocked_in_fresh_process(self):
        source='''import importlib.abc, sys
from pathlib import Path
class NoPlaywright(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "playwright" or fullname.startswith("playwright."):
            raise ModuleNotFoundError("Playwright deliberately blocked for build-only unit imports")
sys.meta_path.insert(0, NoPlaywright())
sys.path.insert(0, str(Path("scripts").resolve()))
from check_expansion_browser import COMPANIONS, CASES, upload_setup
assert len(COMPANIONS) == 4 and len(CASES) == 9
assert "my_series.csv" in upload_setup() and "synthetic" in upload_setup()
assert not any(name == "playwright" or name.startswith("playwright.") for name in sys.modules)
print("BUILD_ONLY_IMPORT_PASSED")
'''
        result=subprocess.run([sys.executable,'-c',source],cwd=ROOT,check=True,capture_output=True,text=True)
        self.assertIn('BUILD_ONLY_IMPORT_PASSED',result.stdout)

    def test_reference_integrity_requires_pinned_raw_and_exact_mounted_representation(self):
        nb=nbformat.read(ROOT/'content/courses/c3s-atlas/02-data-and-provenance.ipynb',4)
        self.assertTrue(any(c.cell_type=='code' and c.source==importer.C3S_REFERENCE_AUDIT for c in nb.cells))
        parsed=ast.parse(importer.C3S_REFERENCE_AUDIT)
        selected=[node for node in parsed.body if isinstance(node,ast.FunctionDef) or
            isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='_reference_pins' for t in node.targets)]
        state={'hashlib':hashlib,'sys':sys,'Path':Path}
        exec(compile(ast.Module(body=selected,type_ignores=[]),'<reviewed audit>','exec'),state)
        item=next(x for x in json.loads((ROOT/'content/courses/c3s-atlas/data/manifest.json').read_text()) if x['file'].endswith('.geojson'))
        raw=(ROOT/'content/courses/c3s-atlas/data'/item['file']).read_bytes()
        verify=state['_verify_reference_bytes'];self.assertTrue(verify(item,raw,raw))
        stringify=lambda value:json.dumps(value,separators=(',',':'),ensure_ascii=False)
        js=SimpleNamespace(JSON=SimpleNamespace(parse=json.loads,stringify=stringify))
        transport=stringify(json.loads(raw)).encode()
        with patch.dict(sys.modules,{'js':js}),patch.object(sys,'platform','emscripten'):
            self.assertTrue(verify(item,raw,transport))
            changed=json.loads(raw);changed['features'][0]['properties']['unreviewed']='changed object'
            for mounted in [stringify(changed).encode(),json.dumps(json.loads(raw),indent=2).encode()]:
                with self.assertRaisesRegex(ValueError,'Mounted reference'):verify(item,raw,mounted)
        with self.assertRaisesRegex(ValueError,'Authentic raw'):verify(item,raw+b' ',raw+b' ')
        with self.assertRaisesRegex(ValueError,'Authentic raw'):verify({**item,'sha256':'0'*64},raw,raw)

    def test_uploaded_pair_branch_accepts_explicit_blank_and_rejects_null_types_and_gap(self):
        helper=atlas_helper();nb=nbformat.read(ROOT/'content/courses/c3s-atlas/19-bring-real-data.ipynb',4)
        code=next(c.source for c in nb.cells if c.cell_type=='code' and 'csv_path, meta_path' in c.source)
        previous=Path.cwd()
        try:
            with tempfile.TemporaryDirectory(dir=WORK) as folder,chdir(folder):
                shown=[]
                def state():return {'Path':Path,'json':json,'load_monthly_csv':helper.load_monthly_csv,'pd':pd,'go':go,'show':shown.append,'display':lambda *a:None}
                valid=state();exec(upload_setup(),valid);exec(code,valid)
                self.assertEqual(valid['actual'].value.isna().tolist(),[False,True,False]);self.assertEqual(len(shown),1)
                for value in [None,3,False,'','   ']:
                    invalid=state();exec(upload_setup(),invalid)
                    path=Path('my_series.json');meta=json.loads(path.read_text());meta['source']=value;path.write_text(json.dumps(meta))
                    with self.subTest(value=value),self.assertRaisesRegex(ValueError,'Provenance fields'):exec(code,invalid)
                invalid=state();exec(upload_setup(missing_month=True),invalid)
                with self.assertRaisesRegex(ValueError,'Missing month:'):exec(code,invalid)
                invalid=state();exec(upload_setup(),invalid);meta=json.loads(Path('my_series.json').read_text());del meta['source'];Path('my_series.json').write_text(json.dumps(meta))
                with self.assertRaisesRegex(ValueError,'Missing provenance'):exec(code,invalid)
        finally:os.chdir(previous)
        guide=(ROOT/'content/courses/c3s-atlas/data-guide.md').read_text()
        self.assertIn('courses/c3s-atlas/',guide);self.assertIn('beside `19-bring-real-data.ipynb`',guide)
        self.assertLess(guide.index('Download or check out the complete source'),guide.index('python scripts/prepare_netcdf.py'))
        self.assertIn('b41c3e1098a4fb94cef48b3044fe19c6ce7c1a1a',guide)

    def test_widget_skips_require_exact_notebook_cell_id_and_source(self):
        for relative in WIDGET_CELLS:
            nb=nbformat.read(ROOT/'content'/relative,4);self.assertEqual(reviewed_widget_indices(relative,nb),[9])
            mutated=copy.deepcopy(nb);mutated.cells[9].source+='\nprint("substantive new calculation")'
            with self.assertRaisesRegex(ValueError,'cell changed'):reviewed_widget_indices(relative,mutated)
        globe='courses/destination-earth-digital-twin/17-globe.ipynb'
        self.assertEqual(reviewed_widget_indices(globe,nbformat.read(ROOT/'content'/globe,4),browser=True),[9])
        with self.assertRaisesRegex(ValueError,'only for'):reviewed_widget_indices(relative,nb,browser=True)

    def test_climate_trace_oracles_reject_coastline_only_values_and_missing_mask_changes(self):
        helper=atlas_helper();lon,lat,field=helper.regular_grid();xx,yy=np.meshgrid(lon,lat)
        region=np.where((xx>=-10)&(xx<=40)&(yy>=30)&(yy<=70),field,np.nan)
        traces=helper.map_figure(lon,lat,region,'Synthetic oracle fixture')._data
        assert_climate_plot(traces,'regional')
        with self.assertRaises(AssertionError):assert_climate_plot(traces[1:],'regional')
        changed=copy.deepcopy(traces);changed[0]['visible']=False
        with self.assertRaisesRegex(AssertionError,'visibly rendered'):assert_climate_plot(changed,'regional')
        changed=copy.deepcopy(traces);changed[0]['z'][0,0]=0
        with self.assertRaisesRegex(AssertionError,'missing mask'):assert_climate_plot(changed,'regional')
        changed=copy.deepcopy(traces);changed[0]['z'][25,35]+=1
        with self.assertRaises(AssertionError):assert_climate_plot(changed,'regional')
        assert_climate_plot(helper.map_figure(lon,lat,field,'Synthetic global')._data,'global-2d')
        assert_climate_plot(helper.globe_figure()._data,'globe')

    def test_urbanity_disconnected_edit_rejects_exhausted_search(self):
        source=LESSONS['urbanity']['exercise'];start=source.index('edges = ');end=source.index('\n',start)
        source=source[:start]+"edges = [('A','B'),('B','C'),('D','E'),('E','F')]"+source[end:]
        with self.assertRaisesRegex(ValueError,'search is exhausted'),redirect_stdout(io.StringIO()):exec(source,{'bars':lambda *a:None})

    def test_identical_splash_alias_is_explicit_and_conflicting_bytes_are_rejected(self):
        with tempfile.TemporaryDirectory(dir=WORK) as folder:
            checkout=Path(folder);(checkout/'assets').mkdir();(checkout/'content/assets').mkdir(parents=True)
            data=(ROOT/'content/courses/destination-earth-digital-twin/assets/splash.png').read_bytes()
            (checkout/'assets/splash.png').write_bytes(data);(checkout/'content/assets/splash.png').write_bytes(data)
            support={};put=lambda path:importer.collect_support(support,'assets/splash.png','destination-earth-digital-twin',path,checkout)
            put('assets/splash.png');put('content/assets/splash.png')
            self.assertEqual(support['assets/splash.png'],('destination-earth-digital-twin','assets/splash.png'))
            (checkout/'content/assets/splash.png').write_bytes(b'conflicting');before=copy.deepcopy(support)
            with self.assertRaisesRegex(ValueError,'Conflicting support'):put('content/assets/splash.png')
            self.assertEqual(support,before)

    def test_catalog_later_partial_write_restores_every_original_and_retry_works(self):
        with tempfile.TemporaryDirectory(dir=WORK) as folder:
            root=Path(folder);(root/'catalog').mkdir()
            paths=[root/'catalog/repositories.json',root/'catalog/discovery.json',root/'mirror.json']
            for path in paths:path.write_text(json.dumps({'repositories':[]}))
            before={p:p.read_bytes() for p in paths};updates={p:{'repositories':[{'slug':'c3s-atlas'}]} for p in paths}
            real=Path.write_bytes;failed=[False]
            def partial(path,data):
                if path==paths[1] and not failed[0]:
                    failed[0]=True;real(path,data[:5]);raise OSError('later catalog write')
                return real(path,data)
            with patch.object(Path,'write_bytes',partial):
                with self.assertRaisesRegex(OSError,'later catalog'):catalogs.write_catalogs(updates)
            self.assertEqual({p:p.read_bytes() for p in paths},before)
            catalogs.write_catalogs(updates)
            for name in ['launch-checks','map-resources','browser-gis-pathways','data-attributions','source-library']:
                (root/'catalog'/f'{name}.json').write_text('{}')
            with patch.object(catalogs,'ROOT',root),self.assertRaisesRegex(ValueError,'already exist'):catalogs.main()

    def test_current_scope_refresh_preserves_historical_prose_and_reference_code(self):
        with tempfile.TemporaryDirectory(dir=WORK) as folder:
            root=Path(folder);(root/'catalog').mkdir();(root/'content').mkdir()
            (root/'catalog/repositories.json').write_text(json.dumps({'repositories':[{}]*46}))
            (root/'catalog/source-library.json').write_text(json.dumps({'courses':[{}]*46,'sections':[{}]*796}))
            text='Historical milestone:42 chapters/724 imports.\n<!-- BROWSER_GIS_PATHWAYS:START -->\n**42 project chapters and 42 source-course guides**. The 724 imported source lessons.\n<!-- BROWSER_GIS_PATHWAYS:END -->\n'
            for name in ['README.md','REFERENCES.md']:(root/name).write_text(text)
            nb=nbformat.v4.new_notebook(cells=[nbformat.v4.new_markdown_cell(text),nbformat.v4.new_code_cell('answer=42')]);nbformat.write(nb,root/'content/references.ipynb')
            refresh_current_scope(root)
            self.assertIn('Historical milestone:42 chapters/724 imports.',(root/'README.md').read_text())
            self.assertIn('**46 project chapters and 46 source-course guides**',(root/'README.md').read_text())
            updated=nbformat.read(root/'content/references.ipynb',4)
            self.assertEqual(updated.cells[0].source,(root/'REFERENCES.md').read_text());self.assertEqual(updated.cells[1],nb.cells[1])

    def test_four_new_project_git_filter_bytes_match_raw_receipt_inputs(self):
        for slug in LESSONS:
            relative=f'content/projects/{slug}/index.ipynb'
            self.assertEqual(subprocess.check_output(['git','hash-object','--no-filters',relative],cwd=ROOT),
                subprocess.check_output(['git','hash-object','--path='+relative,relative],cwd=ROOT))

    def test_urbanity_order_is_shared_for_append_strings_and_full_refresh_records(self):
        paths=[f'book/notebooks/{name}.ipynb' for name in reversed(importer.URBANITY_ORDER)]
        expected=[f'book/notebooks/{name}.ipynb' for name in importer.URBANITY_ORDER]
        self.assertEqual(importer.ordered_notebooks('urbanity',paths),expected)
        self.assertEqual([n['path'] for n in importer.ordered_notebooks('urbanity',[{'path':p} for p in paths])],expected)

    def test_append_and_full_refresh_fixture_publish_identical_support_links_and_citations(self):
        outputs=[]
        with tempfile.TemporaryDirectory(dir=WORK) as folder:
            for mode in ['append','refresh']:
                root=Path(folder)/mode;sources=root/'sources';checkout=sources/'destination-earth-digital-twin'
                (checkout/'content').mkdir(parents=True);(checkout/'book').mkdir();(root/'catalog').mkdir();(root/'_research').mkdir()
                nbformat.write(nbformat.v4.new_notebook(cells=[nbformat.v4.new_markdown_cell('# Fixture'),nbformat.v4.new_code_cell('print(1)')]),checkout/'content/01-system.ipynb')
                (checkout/'book/index.md').write_text('[Lesson](../content/01-system.ipynb)\n\nDataset not used {cite:p}`climategen2`.\n```{bibliography}\n:filter: docname in docnames\n```')
                (checkout/'book/references.bib').write_text('@misc{climategen2,title={Context only}}')
                (checkout/'LICENSE').write_text('Fixture license')
                previous={'courses':[],'sections':[],'support_files':[],'dispositions':[],'asset_exclusions':[],'inventory':{}}
                (root/'catalog/source-library.json').write_text(json.dumps(previous))
                record={'slug':'destination-earth-digital-twin','name':'Fixture','url':'https://github.com/jltobias/Fixture','commit':'a'*40,'notebooks':[{'path':'content/01-system.ipynb','first_heading':'# Fixture'}],'licenses':['LICENSE'],'readmes':[]}
                (root/'_research/textbook-source-audit.json').write_text(json.dumps({'checked_on':'2026-11-16','repositories':[record]}))
                def git(args,**kwargs):
                    if args[1]=='rev-parse':return 'a'*40+'\n'
                    if args[1]=='status':return ''
                    return b'content/01-system.ipynb\0book/index.md\0book/references.bib\0LICENSE\0'
                with patch.multiple(importer,ROOT=root,DEST=root/'content',SOURCES=sources,EXTRA={}),patch.object(importer.subprocess,'check_output',side_effect=git),patch.dict(importer.course_source,{},clear=True),redirect_stdout(io.StringIO()):
                    if mode=='append':
                        with patch.dict(importer.APPEND_COURSES,{'destination-earth-digital-twin':('Fixture','a'*40,1)}):importer.append_courses(['destination-earth-digital-twin'])
                    else:
                        with patch.object(sys,'argv',['import_sources.py']):importer.main()
                outputs.append((root/'content/courses/destination-earth-digital-twin/book/index.md').read_bytes())
        self.assertEqual(*outputs);self.assertIn(b'../01-system.ipynb',outputs[0]);self.assertIn(b'10.21957/79c6af3105',outputs[0]);self.assertNotIn(b'{cite:p}',outputs[0])


if __name__=='__main__':unittest.main()
