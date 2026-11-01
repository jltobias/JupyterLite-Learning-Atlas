"""Regression checks live outside editable teaching notebooks."""
import ast
import base64
import contextlib
import colorsys
import copy
import io
import json
import math
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from xml.etree import ElementTree as ET

import nbformat

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from lesson_material import LESSONS
from generate import HELPERS, seed_project


def run_activity(relative, replacements=None):
    notebook=nbformat.read(ROOT/'content'/relative,as_version=4)
    namespace={};displayed=[];stdout=io.StringIO()
    with tempfile.TemporaryDirectory(prefix='atlas-activity-') as directory:
        previous=Path.cwd()
        try:
            os.chdir(directory)
            with patch('IPython.display.display',side_effect=displayed.append),contextlib.redirect_stdout(stdout):
                for cell in notebook.cells:
                    if cell.cell_type!='code':continue
                    source=cell.source
                    for before,after in (replacements or {}).items():source=source.replace(before,after)
                    exec(compile(source,relative,'exec'),namespace)
            exports={p.name:p.read_bytes() for p in Path(directory).glob('*.geojson')}
        finally:os.chdir(previous)
    return namespace,displayed,stdout.getvalue(),exports


class ActivityRepairs(unittest.TestCase):
    def test_ml_default_and_editable_offset_reach_svg(self):
        default,rendered,_,_=run_activity('foundations/learning-a-model.ipynb')
        self.assertAlmostEqual(default['metrics']['West training MAE'],0.7238095238095239)
        self.assertAlmostEqual(default['metrics']['East held-out MAE'],7.685714285714286)
        self.assertAlmostEqual(default['metrics']['East constant-baseline MAE'],19)
        self.assertTrue(any('Train here, test elsewhere' in str(getattr(item,'data','')) for item in rendered))
        changed,rendered,_,_=run_activity('foundations/learning-a-model.ipynb',{'east_offset = 8':'east_offset = 1'})
        self.assertEqual(changed['east_offset'],1)
        self.assertLess(changed['metrics']['East held-out MAE'],default['metrics']['East held-out MAE'])
        self.assertTrue(any('Train here, test elsewhere' in str(getattr(item,'data','')) for item in rendered))

    def test_whitebox_default_and_sink(self):
        normal,_,_,_=run_activity('projects/whitebox/index.ipynb')
        self.assertEqual(normal['direction'],'east')
        sink,rendered,text,_=run_activity('projects/whitebox/index.ipynb',{'center = terrain[1][1]':'center = 0'})
        self.assertIsNone(sink['direction']);self.assertEqual(set(sink['drops'].values()),{0})
        self.assertIn('none (sink or flat)',text);self.assertTrue(rendered)

    def test_hats_required_fields_types_and_extra_metadata(self):
        namespace,_,_,_=run_activity('projects/custom-gpt-six-thinking-hats/index.ipynb')
        validate=namespace['validate_perspectives'];record=namespace['record']
        self.assertEqual(namespace['issues'],{'missing':[],'empty':['green'],'invalid':{}})
        altered=copy.deepcopy(record);del altered['white'];altered['red']='not a list'
        altered['black']=['valid',None,'   '];altered['evidence_url']='https://example.org/context'
        counts,issues=validate(altered)
        self.assertEqual(issues['missing'],['white']);self.assertEqual(issues['empty'],['green'])
        self.assertEqual(set(issues['invalid']),{'red','black'})
        self.assertEqual(counts['red'],0);self.assertEqual(counts['black'],1)
        self.assertNotIn('evidence_url',issues['invalid'])
        self.assertEqual(altered['evidence_url'],'https://example.org/context')
        original_line=next(line for line in LESSONS['Custom-GPT-Six-Thinking-Hats'][5].splitlines() if line.startswith('record = '))
        for value in ['2','[{"white": []}]']:
            invalid,rendered,_,_=run_activity('projects/custom-gpt-six-thinking-hats/index.ipynb',{original_line:'record = '+value})
            self.assertIn('record',invalid['issues']['invalid']);self.assertTrue(rendered)

    def test_rustgis_bbox_coverage_and_portable_download(self):
        namespace,rendered,text,exports=run_activity('projects/rustgis/index.ipynb')
        self.assertEqual(namespace['bbox'],[20,-10,20.3,-9.85])
        self.assertTrue(all(v=={'present':4,'missing_ids':[]} for v in namespace['coverage'].values()))
        layer=json.loads(exports['atlas-synthetic-rustgis.geojson'])
        self.assertEqual(layer,namespace['layer'])
        self.assertTrue(all(f['properties']['origin']=='synthetic' and f['properties']['units']=='arbitrary index' for f in layer['features']))
        html=next(item.data for item in rendered if 'download="atlas-synthetic-rustgis.geojson"' in str(getattr(item,'data','')))
        encoded=re.search(r'base64,([^"\s]+)',html).group(1)
        self.assertEqual(json.loads(base64.b64decode(encoded)),layer)
        self.assertNotIn('href="atlas-synthetic',html)
        self.assertIn('Lab file browser',text)

    def test_hivdb_default_eligible_country_and_denominator(self):
        namespace,_,_,_=run_activity('projects/hivdb-drug-resistance-maps/index.ipynb')
        self.assertEqual([r[0] for r in namespace['single']],['A','A'])
        self.assertEqual(sum(n for _,n,_ in namespace['single']),120)
        self.assertAlmostEqual(namespace['weighted'],0.13333333333333333)

    def test_seed_code_matches_repaired_canonical_activities(self):
        for key,slug in [('Whitebox','whitebox'),('RustGIS','rustgis'),('Custom-GPT-Six-Thinking-Hats','custom-gpt-six-thinking-hats')]:
            notebook=nbformat.read(ROOT/'content/projects'/slug/'index.ipynb',as_version=4)
            self.assertEqual(LESSONS[key][5].strip(),notebook.cells[3].source.strip(),key)

    def test_shared_grid_uses_dark_labels_and_text_alternative(self):
        displayed=[];namespace={};text=io.StringIO()
        with patch('IPython.display.display',side_effect=displayed.append),contextlib.redirect_stdout(text):
            exec(HELPERS,namespace);namespace['grid']([0,1],2,'Contrast fixture')
        root=ET.fromstring(displayed[0].data)
        labels=root.findall('{http://www.w3.org/2000/svg}text')[1:]
        self.assertEqual({t.attrib['fill'] for t in labels},{'#061c21'})
        self.assertIn('[0, 1]',text.getvalue())
        rgb=[int('061c21'[i:i+2],16)/255 for i in [0,2,4]]
        def luminance(values):
            return sum((v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4)*w for v,w in zip(values,[.2126,.7152,.0722]))
        foreground=luminance(rgb)
        for rectangle in root.findall('{http://www.w3.org/2000/svg}rect')[1:]:
            hue,saturation,lightness=map(float,re.findall(r'[\d.]+',rectangle.attrib['fill']))
            background=luminance(colorsys.hls_to_rgb(hue/360,lightness/100,saturation/100))
            self.assertGreaterEqual((background+.05)/(foreground+.05),4.5)


class PublicFourActivities(unittest.TestCase):
    def test_shiny_threshold_ties(self):
        namespace,rendered,_,_=run_activity('projects/shiny-live-apps/index.ipynb')
        self.assertEqual(namespace['counts'],{'3':4,'5':2,'8':1})
        self.assertEqual(namespace['count_at_or_above']([4,4],4),2)
        changed,_,_,_=run_activity('projects/shiny-live-apps/index.ipynb',{
            'thresholds = [3, 5, 8]':'thresholds = [3, 4, 5, 8]'})
        self.assertEqual(changed['counts'],{'3':4,'4':4,'5':2,'8':1})
        self.assertTrue(rendered)

    def test_buffer_membership_edits_descriptions_and_escaped_labels(self):
        relative='projects/maps-and-spatial-analyses/index.ipynb'
        cases=[({},3,{'A':True,'B':True,'C':False,'D':True},'A, B, D','C'),
               ({'radius = 3':'radius = 2.5'},2.5,{'A':True,'B':False,'C':False,'D':False},'A','B, C, D'),
               ({'distance <= radius':'distance < radius'},3,{'A':True,'B':False,'C':False,'D':True},'A, D','B, C')]
        for edits,radius,membership,included,excluded in cases:
            with self.subTest(edits=edits):
                namespace,rendered,_,_=run_activity(relative,edits)
                self.assertEqual(namespace['inside'],membership)
                self.assertAlmostEqual(namespace['distances']['A'],math.sqrt(2))
                self.assertEqual(namespace['distances']['B'],3)
                self.assertAlmostEqual(namespace['distances']['C'],math.sqrt(13))
                self.assertAlmostEqual(namespace['distances']['D'],math.sqrt(8))
                root=ET.fromstring(rendered[-1].data)
                title=root.find('{http://www.w3.org/2000/svg}title').text
                description=root.find('{http://www.w3.org/2000/svg}desc').text
                self.assertEqual(title,f'Synthetic distance buffer: radius {radius:g}')
                self.assertIn(f'Current radius: {radius:g} arbitrary planar units.',description)
                self.assertIn(f'Inside: {included}. Outside: {excluded}.',description)
                self.assertNotIn('inclusive',title)
        _,rendered,_,_=run_activity(relative,{"'A':(1,1)":"'A<&':(1,1)"})
        root=ET.fromstring(rendered[-1].data)
        self.assertIn('A<&: inside',[item.text for item in root.findall('{http://www.w3.org/2000/svg}text')])
        self.assertIn('Inside: A<&, B, D.',root.find('{http://www.w3.org/2000/svg}desc').text)
        self.assertIn('A&lt;&amp;',rendered[-1].data)

    def test_focal_means_denominators_end_peak_and_full_window_extension(self):
        relative='projects/spatial-analysis/index.ipynb'
        default,_,_,_=run_activity(relative)
        self.assertEqual(default['near'],[1,4,4,4,1])
        self.assertEqual(default['near_n'],[2,3,3,3,2])
        self.assertEqual(default['wide'],[4,3.25,2.8,3.25,4])
        self.assertEqual(default['wide_n'],[3,4,5,4,3])
        self.assertAlmostEqual(sum(default['wide'])/5,3.46)
        self.assertEqual(sum(default['values'])/5,2.8)
        changed,rendered,_,_=run_activity(relative,{'values = [1, 1, 10, 1, 1]':'values = [10, 1, 1, 1, 1]'})
        self.assertEqual(changed['near'],[5.5,4,1,1,1])
        self.assertEqual(changed['near_n'],[2,3,3,3,2])
        self.assertEqual(changed['wide'],[4,3.25,2.8,1,1])
        self.assertEqual(changed['wide_n'],[3,4,5,4,3])
        self.assertTrue(rendered)
        notebook=nbformat.read(ROOT/'content'/relative,as_version=4)
        scaffold=re.search(r'```python\n(.*?)\n```',notebook.cells[4].source,re.S).group(1)
        with contextlib.redirect_stdout(io.StringIO()):exec(scaffold,changed)
        self.assertEqual(changed['valid_indices'],[2])
        self.assertEqual(changed['full_means'],[2.8])
        self.assertEqual(changed['unavailable_indices'],[0,1,3,4])

    def test_extract_means_coverage_and_two_per_group_selection(self):
        relative='projects/geospatial-analyses-and-maps-old/index.ipynb'
        default,_,_,_=run_activity(relative)
        self.assertEqual(default['means'],{'complete invented fixture':4.5,'uneven teaching extract':5.5})
        self.assertEqual(default['coverage'],{'low':{'full':4,'extract':1},'high':{'full':4,'extract':3}})
        self.assertEqual(sum(row[2] for row in default['cells'] if row[1]=='low')/4,2)
        self.assertEqual(sum(row[2] for row in default['cells'] if row[1]=='high')/4,7)
        self.assertEqual(next(row[2] for row in default['extract'] if row[1]=='low'),1)
        changed,rendered,_,_=run_activity(relative,{
            "selected_ids = {'L1', 'H1', 'H2', 'H3'}":"selected_ids = {'L1', 'L4', 'H1', 'H4'}"})
        self.assertEqual(changed['means'],{'complete invented fixture':4.5,'uneven teaching extract':4.5})
        self.assertEqual(changed['coverage'],{'low':{'full':4,'extract':2},'high':{'full':4,'extract':2}})
        self.assertTrue(rendered)

    def test_new_lesson_seed_code_fixture_contracts_and_source_continuations(self):
        records=json.loads((ROOT/'catalog/repositories.json').read_text(encoding='utf-8'))['repositories']
        keys=['Shiny-Live-Apps','Spatial-Analysis','Maps-and-Spatial-Analyses','Geospatial-Analyses-and-Maps-old']
        for key in keys:
            record=next(r for r in records if r['name']=='JupyterLite-'+key)
            notebook=nbformat.read(ROOT/'content'/record['notebook'],as_version=4)
            self.assertEqual(LESSONS[key][5].strip(),notebook.cells[3].source.strip(),key)
            with patch('generate.notebook') as seeded:seed_project(record)
            cells=seeded.call_args.args[1]
            for source in [notebook.cells[1].source,cells[1]['source']]:
                self.assertIn('fixtures have no missing values',source)
                self.assertIn('complete finite numeric',source)
                self.assertIn('define a missing-data rule before introducing missing data',source)
            if key=='Spatial-Analysis':self.assertIn('nonnegative integer focal radius',notebook.cells[1].source)
            if key=='Maps-and-Spatial-Analyses':self.assertIn('nonnegative finite buffer radius',notebook.cells[1].source)
            if key!='Shiny-Live-Apps':
                self.assertEqual(cells[6]['source'],notebook.cells[6].source)
                self.assertIn('[Reviewed source README]('+record['readme_url']+')',notebook.cells[6].source)
                self.assertIn('JupyterLite build',notebook.cells[6].source)
                self.assertNotIn('For native/GPU tools',notebook.cells[6].source)
                self.assertNotIn('For live models',notebook.cells[6].source)


if __name__=='__main__':unittest.main()
