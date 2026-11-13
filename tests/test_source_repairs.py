"""Focused source preparation, managed refresh and actual capstone export checks."""
import asyncio
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import nbformat
from nbclient import NotebookClient

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import generate
import import_sources as importer
import textbook_material as material
from source_library import load_library, stage_dependencies


class SourcePreparationRepairs(unittest.TestCase):
    def test_pyscript_shared_layout_and_unchanged_chart_lessons_use_actual_config(self):
        library=load_library();support={s['local_path']:s for s in library['support_files']}
        self.assertEqual(importer.mapped('pyscript','site/apps/shared/lab.py'),'source/lab.py')
        self.assertEqual(importer.mapped('pyscript','site/apps/d3/index.html'),'source/apps/d3/index.html')
        for name in ['lab.py','lab.js','pyscript.json','charts.py','charts.js','charts.json','charts.css']:
            item=support['courses/pyscript/source/'+name]
            self.assertEqual(item['source_sha256'],item['sha256'])
            self.assertEqual(item['source_path'],'site/apps/shared/'+name)
        config=json.loads((ROOT/'content/courses/pyscript/hub-config.json').read_text())
        self.assertEqual(config['base_url'],'https://jltobias.github.io/JupyterLite-PyScript')
        work=ROOT/'_build/test-source-repairs';work.mkdir(parents=True,exist_ok=True)
        for path in sorted((ROOT/'content/courses/pyscript').glob('0[4-7]*.ipynb')):
            with self.subTest(path=path.name),tempfile.TemporaryDirectory(dir=work) as folder:
                cwd=stage_dependencies(path.relative_to(ROOT/'content').as_posix(),folder,library)
                nb=nbformat.read(path,4)
                source='\n\n'.join(c.source for c in nb.cells if c.cell_type=='code')
                # Displaying an IFrame emits HTML only; the Python test does not
                # start its independent remote interpreter or contact its API.
                source+="\nassert app_url.startswith('https://jltobias.github.io/JupyterLite-PyScript/apps/')\n"
                result=subprocess.run([sys.executable,'-c',source],cwd=cwd,capture_output=True,text=True,encoding='utf-8')
                self.assertEqual(result.returncode,0,result.stderr)

    def test_stac_absolute_continuation_has_one_origin_and_recorded_adapter(self):
        path=ROOT/'content/courses/stac-browser/stac_browser.py'
        spec=importlib.util.spec_from_file_location('atlas_stac_repair',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with patch.dict(sys.modules,{'js':SimpleNamespace(location=SimpleNamespace(origin='http://127.0.0.1:8768'))}):
            self.assertEqual(module.explorer_url(),'https://jltobias.github.io/JupyterLite-STAC-Browser/explorer/')
        item=next(s for s in load_library()['support_files'] if s['local_path']=='courses/stac-browser/stac_browser.py')
        # Reverse the recorded one-line adapter using only public canonical
        # bytes, then verify its original hash and the forward transformation.
        canonical=path.read_bytes();change=item['modifications'][0]
        self.assertEqual(canonical.count(change['to'].encode()),1)
        original=canonical.replace(change['to'].encode(),change['from'].encode(),1)
        prepared,changes=importer.adapt_support(item['course'],item['source_path'],original)
        self.assertEqual(prepared,canonical)
        self.assertEqual(item['source_sha256'],importer.digest(original))
        self.assertEqual(item['sha256'],importer.digest(prepared))
        self.assertEqual(item['modifications'],changes)

    def test_ghgis_aliases_are_exact_credited_source_bytes(self):
        library=load_library();support={s['local_path']:s for s in library['support_files']}
        original=(ROOT/'content/courses/global-health-gis/data/gbd_country_points_2021_global.geojson').read_bytes()
        original_item=support['courses/global-health-gis/data/gbd_country_points_2021_global.geojson']
        self.assertEqual(hashlib.sha256(original).hexdigest(),original_item['source_sha256'])
        for name in ['gbd_country_points_2021.geojson','gbd_country_points_generated.geojson']:
            relative='courses/global-health-gis/data/'+name;item=support[relative]
            self.assertEqual((ROOT/'content'/relative).read_bytes(),original)
            self.assertEqual(item['source_path'],'content/data/gbd_country_points_2021_global.geojson')
            self.assertEqual(item['sha256'],item['source_sha256'])
        self.assertEqual(len(json.loads(original)['features']),232)

    def test_exact_deployment_and_missing_pinned_paths_do_not_become_self_links(self):
        record=next(c for c in load_library()['courses'] if c['slug']=='pyscript')
        with patch.dict(importer.course_source,{'pyscript':record}):
            changes=[]
            value=importer.normalize_markdown('[2D]({{HUB_BASE}}/apps/leaflet/) [authoring]({{HUB_BASE}}/book/authoring/) [input](missing.csv)',
                'content/03-author-an-app.ipynb','pyscript','courses/pyscript/03-author-an-app.ipynb',{},set(),changes)
        self.assertIn('https://jltobias.github.io/JupyterLite-PyScript/apps/leaflet/',value)
        self.assertIn('https://jltobias.github.io/JupyterLite-PyScript/book/authoring/',value)
        self.assertIn('/blob/'+record['commit']+'/content/missing.csv',value)
        self.assertNotIn('/content/03-author-an-app.ipynb',value)

    def test_watch_html_is_excluded_and_source_runtime_gaps_are_precise(self):
        library=load_library()
        self.assertTrue(importer.exclusion('geolibre-geoai','book/notebooks/assets/learning/00/watch.html'))
        self.assertFalse(any(s['course']=='geolibre-geoai' and '/assets/learning/' in s['local_path'] and s['local_path'].endswith('.html') for s in library['support_files']))
        self.assertTrue((ROOT/'content/courses/geolibre-geoai/assets/learning/00/infographic.svg').is_file())
        for section in library['sections']:
            slug=section['course'];name=Path(section['source_path']).name
            if (slug=='gods-eye-view-satellite' and name.startswith(('05_','09_'))) or (slug=='global-informal-settlements-storymap' and name.startswith('08_')) or (slug=='world-monitor-prototype' and name.startswith(('01_','02_'))):
                prepared=nbformat.read(ROOT/'content'/section['notebook'],4)
                # Runtime policy consumes the published code. Original-versus-
                # prepared preservation is covered by the separate source audit,
                # whose optional checkouts are not a clean-CI prerequisite.
                self.assertEqual(section['runtime'],importer.runtime(slug,section['source_path'],prepared))
                text=' '.join(section['runtime']['requirements'])
                self.assertIn('jupyterlite-ai' if slug=='global-informal-settlements-storymap' else 'data/worldmonitor/index.json' if slug=='world-monitor-prototype' else 'Leaflet' if name.startswith('05_') else 'Cesium',text)
                self.assertEqual(section['runtime']['class'],'browser-network' if slug=='gods-eye-view-satellite' else 'reference-only')

    def test_refresh_removes_only_obsolete_unchanged_owned_source_notebooks(self):
        work=ROOT/'_build/test-source-repairs';work.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=work) as folder:
            root=Path(folder);path=root/'courses/example/obsolete.ipynb';path.parent.mkdir(parents=True)
            nb=nbformat.v4.new_notebook(cells=[nbformat.v4.new_markdown_cell('Provenance'),nbformat.v4.new_code_cell('x=1')],metadata={'atlas':{'kind':'source-section','course':'example','source_path':'old.ipynb'}})
            nbformat.write(nb,path)
            entry={'course':'example','notebook':'courses/example/obsolete.ipynb','source_path':'old.ipynb','adapted_cell_sha256':importer.digest(json.dumps([(c.cell_type,c.source) for c in nb.cells[1:]],ensure_ascii=False).encode())}
            guide=path.with_name('index.ipynb');guide.write_text('authored guide');companion=root/'projects/example/index.ipynb';companion.parent.mkdir(parents=True);companion.write_text('original companion')
            self.assertEqual(importer.reconcile_source_sections({'sections':[entry]},set(),root),[path.resolve()])
            self.assertEqual(guide.read_text(),'authored guide');self.assertEqual(companion.read_text(),'original companion')
            nb.cells[1].source='x=2';nbformat.write(nb,path)
            with self.assertRaisesRegex(ValueError,'authored/modified'):
                importer.reconcile_source_sections({'sections':[entry]},set(),root)
            self.assertTrue(path.exists())
            unsafe={**entry,'notebook':'../outside.ipynb'}
            with self.assertRaisesRegex(ValueError,'Unsafe'):
                importer.reconcile_source_sections({'sections':[unsafe]},set(),root)

    def test_managed_guides_refresh_manifest_content_and_preserve_authored_additions(self):
        work=ROOT/'_build/test-source-repairs';work.mkdir(parents=True,exist_ok=True)
        library={'inventory':{'repositories':1,'inspected_notebook_paths':1,'authored_sections':1,'compatibility_sections':0,'aliases':0,'excluded_notebooks':0},
            'courses':[{'slug':'example','name':'Example source','url':'https://example.org/source','commit':'a'*40,'guide':'courses/example/index.ipynb','license':'Scoped author grant'}],
            'sections':[{'course':'example','title':'Old lesson','notebook':'courses/example/old.ipynb','collection':'authored','runtime':{'class':'browser-local','requirements':['Old requirement']},'verification':{'status':'not-run'}}],
            'support_files':[],'dispositions':[],'asset_exclusions':[]}
        records=[{'slug':'example','title':'Example chapter','notebook':'projects/example/index.ipynb'}]
        with tempfile.TemporaryDirectory(dir=work) as folder,patch.object(generate,'ROOT',Path(folder)),patch.object(material,'ROOT',Path(folder)),patch.object(material,'load_library',return_value=library):
            material.seed_library(generate.notebook,generate.md,records)
            path=Path(folder)/'content/courses/example/index.ipynb';nb=nbformat.read(path,4)
            for i,c in enumerate(nb.cells):
                c.metadata.pop('atlas_managed',None);c['id']=hashlib.sha256(('courses/example/index.ipynb'+str(i)).encode()).hexdigest()[:12]
            authored=nbformat.v4.new_code_cell('workshop_answer=42',outputs=[nbformat.v4.new_output('stream',name='stdout',text='keep this output')],execution_count=1)
            nb.cells.append(authored);nbformat.write(nb,path)
            library['sections'][0]['title']='Updated lesson';library['sections'][0]['runtime']={'class':'reference-only','requirements':['Precise missing.csv input']}
            library['asset_exclusions']=[{'course':'example','source_path':'missing.csv','source_url':'https://example.org/source/missing.csv','reason':'Explicit missing input'}]
            library['sections'].append({**copy.deepcopy(library['sections'][0]),'title':'Second lesson','notebook':'courses/example/second.ipynb'})
            library['inventory']['inspected_notebook_paths']=2;library['inventory']['authored_sections']=2
            material.seed_library(generate.notebook,generate.md,records)
            updated=nbformat.read(path,4);text='\n'.join(c.source for c in updated.cells)
            self.assertIn('2 full local source notebooks',text);self.assertIn('Updated lesson',text);self.assertIn('Second lesson',text)
            self.assertIn('reference-only',text);self.assertIn('missing.csv',text);self.assertNotIn('Old requirement',text)
            self.assertEqual(next(c for c in updated.cells if c.id==authored.id),authored)
            index=nbformat.read(Path(folder)/'content/notebook-library.ipynb',4)
            self.assertIn('2 inspected notebook paths','\n'.join(c.source for c in index.cells))

    def test_canonical_capstone_writes_selected_sample_means_and_provenance(self):
        if sys.platform=='win32':asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        work=ROOT/'_build/test-source-repairs';work.mkdir(parents=True,exist_ok=True)
        relative='courses/onehealth/10_capstone.ipynb'
        with tempfile.TemporaryDirectory(dir=work) as folder:
            cwd=stage_dependencies(relative,folder)
            notebook=nbformat.read(ROOT/'content'/relative,4)
            NotebookClient(notebook,timeout=120,kernel_name='python3',resources={'metadata':{'path':str(cwd)}},allow_errors=False).execute()
            report=json.loads((cwd/'my-evidence-brief.json').read_text())
            self.assertEqual(report['selected_samples'],3178)
            self.assertAlmostEqual(report['mean_sample_surface_c'],44.711140075707995,places=10)
            self.assertAlmostEqual(report['mean_sample_ndvi'],0.27940307781623663,places=12)
            for actual,expected in zip(report['bbox'],[-119.86,36.69,-119.69,36.86]):self.assertAlmostEqual(actual,expected,places=10)
            self.assertEqual(report['scene_id'],'LC09_L2SP_042035_20240830_02_T1')
            self.assertEqual(report['satellite_datetime'],'2024-08-30T18:33:53.353894Z')
            self.assertEqual(report['population_reference'],'2020-04-01')
            self.assertIn('Systematic samples, not full-resolution area means',report['limits'])
            self.assertIn('No health outcomes or animal observations',report['limits'])


if __name__=='__main__':unittest.main()
