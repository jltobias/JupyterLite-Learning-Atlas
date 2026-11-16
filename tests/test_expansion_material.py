"""Independent numerical, media and complete-course checks for the new material."""
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
import re
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import nbformat
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from expansion_material import LESSONS
from source_library import load_library, validate_library


def module(slug,name):
    spec=importlib.util.spec_from_file_location('expansion_test_'+name,ROOT/'content/courses'/slug/(name+'.py'))
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result


class ExpansionMaterial(unittest.TestCase):
    def test_packaged_monthly_loader_distinguishes_missing_month_and_explicit_blank(self):
        helper=module('c3s-atlas','atlas_helpers')
        work=ROOT/'_build/test-expansion-months';work.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=work) as folder:
            path=Path(folder)/'series.csv';path.write_text('date,value\n2000-01-01,1\n2000-03-01,3\n')
            with self.assertRaisesRegex(ValueError,'Missing month:'):helper.load_monthly_csv(path)
            path.write_text('date,value\n2000-01-01,1\n2000-02-01,\n2000-03-01,3\n')
            self.assertEqual(helper.load_monthly_csv(path).value.isna().tolist(),[False,True,False])

    def test_new_support_documents_avoid_book_stems_and_unbuilt_markdown_targets(self):
        library=load_library();new=set(LESSONS)
        stems={Path(s['notebook']).with_suffix('').as_posix() for s in library['sections'] if s['course'] in new}
        stems|={Path(c['guide']).with_suffix('').as_posix() for c in library['courses'] if c['slug'] in new}
        for support in library['support_files']:
            if support['course'] in new and support['local_path'].endswith('.md'):
                self.assertNotIn(Path(support['local_path']).with_suffix('').as_posix(),stems)
                self.assertEqual(hashlib.sha256((ROOT/'content'/support['local_path']).read_bytes()).hexdigest(),support['sha256'])
        for slug,source in [('c3s-atlas','content/index.md'),('urbanity','book/index.md')]:
            self.assertFalse((ROOT/'content/courses'/slug/'index.md').exists())
            self.assertTrue((ROOT/'content/courses'/slug/'notices/source-documents'/source).is_file())
        receipts={r['notebook']:r for r in json.loads((ROOT/'catalog/expansion-execution.json').read_text(encoding='utf-8'))['results']}
        for section in library['sections']:
            if section['course'] not in new:continue
            path=ROOT/'content'/section['notebook'];nb=nbformat.read(path,4)
            for cell in nb.cells:
                if cell.cell_type!='markdown':continue
                for target in re.findall(r'!?\[[^]]*\]\(([^)]+)\)',cell.source):
                    self.assertFalse(not target.startswith(('https:','http:','#')) and Path(target.split('#')[0]).suffix.lower()=='.md',(path,target))
            if section['course']=='c3s-atlas':
                receipt=receipts[section['notebook']]
                self.assertEqual(receipt['canonical_sha256'],hashlib.sha256(path.read_bytes()).hexdigest())
                if receipt.get('prose_only_amendments'):
                    amendment=receipt['prose_only_amendments'][-1]
                    code=[c for c in nb.cells if c.cell_type=='code']
                    self.assertEqual(amendment['unchanged_executed_code_sha256'],hashlib.sha256('\n\n'.join(c.source for c in code).encode()).hexdigest())
                    self.assertEqual(amendment['unchanged_code_cells_metadata_and_outputs_sha256'],hashlib.sha256(json.dumps(code,sort_keys=True,ensure_ascii=False).encode()).hexdigest())
        for slug,filename in [('c3s-atlas','PROVENANCE.md'),('destination-earth-digital-twin','GENERATION.md')]:
            nb=nbformat.read(ROOT/'content/courses'/slug/'index.ipynb',4)
            visual=next(c.source for c in nb.cells if c.source.startswith('## Course visual'))
            course=next(c for c in library['courses'] if c['slug']==slug)
            self.assertIn(course['url']+'/blob/'+course['commit']+'/assets/'+filename,visual)
            self.assertNotIn('(notices/assets/',visual)

    def test_c3s_plotly_portability_adapter_retains_text_and_isolates_script_loading(self):
        atlas=module('c3s-atlas','atlas_helpers');emitted=[]
        with patch.object(atlas,'display',side_effect=lambda data,**kw:emitted.append(data)):
            atlas.show(atlas.go.Figure(atlas.go.Scatter(x=[0,1],y=[2,3])).update_layout(title='Synthetic adapter fixture'))
        self.assertEqual(len(emitted),1);self.assertEqual(set(emitted[0]),{'text/html','text/plain'})
        class Frame(HTMLParser):
            def handle_starttag(self,tag,attrs):
                if tag=='iframe':self.frame=dict(attrs)
        parsed=Frame();parsed.feed(emitted[0]['text/html'])
        self.assertEqual(set(parsed.frame['sandbox'].split()),{'allow-scripts','allow-downloads'})
        self.assertEqual(parsed.frame['title'],'Synthetic adapter fixture')
        document=parsed.frame['srcdoc']
        self.assertIn('https://cdn.plot.ly/plotly-',document)
        self.assertLess(document.index('https://cdn.plot.ly/plotly-'),document.index('Plotly.newPlot'))
        self.assertIn('Figure(',emitted[0]['text/plain'])
        helper=next(s for s in load_library()['support_files'] if s['local_path']=='courses/c3s-atlas/atlas_helpers.py')
        self.assertNotEqual(helper['sha256'],helper['source_sha256'])
        self.assertEqual(helper['modifications'][0]['adapter'],'c3s-plotly-frame-v1')

    def test_four_canonical_companions_execute_without_services_and_emit_accessible_svg(self):
        states={}
        for slug in LESSONS:
            nb=nbformat.read(ROOT/'content/projects'/slug/'index.ipynb',4);state={};graphics=[]
            with self.subTest(slug=slug),redirect_stdout(io.StringIO()),patch('IPython.display.display',side_effect=lambda value:graphics.append(value)):
                for cell in nb.cells:
                    if cell.cell_type=='code':exec(cell.source,state)
                self.assertEqual(len(graphics),1)
                svg=ET.fromstring(graphics[0].data);ns='{http://www.w3.org/2000/svg}'
                self.assertIsNotNone(svg.find(ns+'title'));self.assertIsNotNone(svg.find(ns+'desc'))
                self.assertGreaterEqual(len(svg.findall(ns+'rect')),4)
                states[slug]=state
        self.assertAlmostEqual(states['c3s-atlas']['full_mean'],3)
        self.assertAlmostEqual(states['c3s-atlas']['missing_mean'],4.5)
        self.assertAlmostEqual(states['destination-earth-digital-twin']['interpolated'],25)
        self.assertEqual(states['urbanity']['route'],['A','B','C','F'])
        self.assertEqual(states['urbanity']['degrees'],{'A':2,'B':4,'C':2,'D':3,'E':3,'F':2})
        self.assertEqual((states['terrio']['centre_x'],states['terrio']['centre_y']),(500315,4399385))
        self.assertAlmostEqual(states['terrio']['scale']['60 degrees'],2)

    def test_packaged_climate_helpers_agree_with_small_independent_oracles(self):
        atlas=module('c3s-atlas','atlas_helpers');earth=module('destination-earth-digital-twin','earthlab')
        self.assertAlmostEqual(atlas.area_mean(np.array([[0,0],[9,9]]),np.array([0,60])),3)
        self.assertAlmostEqual(atlas.area_mean(np.array([[0,np.nan],[9,9]]),np.array([0,60])),4.5)
        windows=atlas.warming_levels();self.assertEqual(len(windows),600)
        known=windows[(windows.member=='CCCma_CanESM5_r1i1p1f1')&(windows.scenario=='ssp585')&(windows.level==2)].iloc[0]
        self.assertEqual((known.start,known.end,known.midpoint),(2013,2032,2022.5))
        lat=np.array([-10.,0,10]);lon=np.array([0.,10,20]);x,y=np.meshgrid(lon,lat)
        self.assertAlmostEqual(earth.bilinear(3*x+2*y,lat,lon,2,7),25)
        xx,yy,zz=earth.globe_xyz(lat,lon,radius=2)
        np.testing.assert_allclose(xx*xx+yy*yy+zz*zz,4)
        self.assertEqual(earth.synthetic_cube()['temperature'].shape,(60,25,49))

    def test_real_geography_and_cleared_artwork_have_audited_bytes_and_scoped_terms(self):
        files={
            'courses/terrio/data/countries.geojson':'6866c877d39cba9c357620878839b336d569f8c662d3cfab4cb1dbe2d39c977f',
            'courses/c3s-atlas/assets/atlas-splash.png':'56c372f295e7716a8b76c316249a17272cc2d441987c8c2df7e50b1a80be2dd1',
            'courses/destination-earth-digital-twin/assets/splash.png':'8572f03e5207a2be3189eed9e91b2bcf1224186c495b7907fe817b22681d82e3',
        }
        for relative,expected in files.items():self.assertEqual(hashlib.sha256((ROOT/'content'/relative).read_bytes()).hexdigest(),expected)
        countries=json.loads((ROOT/'content/courses/terrio/data/countries.geojson').read_text(encoding='utf-8'))
        self.assertEqual(len(countries['features']),177)
        data=load_library();urbanity=next(c for c in data['courses'] if c['slug']=='urbanity')
        self.assertIn('no public license grant',urbanity['license'])
        bib=ROOT/'content/courses/destination-earth-digital-twin/book/references.bib'
        self.assertTrue(bib.is_file())
        intro=(bib.parent/'index.md').read_text(encoding='utf-8')
        self.assertIn('10.21957/79c6af3105',intro);self.assertIn('dataset not used',intro)
        self.assertNotIn('{cite:p}',intro);self.assertNotIn('```{bibliography}',intro)


if __name__=='__main__':unittest.main()
