"""Ownership, portable evidence, failure boundaries and actual canonical execution."""
import asyncio
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

import nbformat
from nbclient import NotebookClient

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'_build/test-browser-gis'
WORK.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'scripts'))
from browser_gis_material import OWNER, NAVIGATION_NOTEBOOKS, load_pathways, pathway_markdown, reconcile_markdown, validate_pathway_blocks
from browser_gis_recipes import CSV_RECIPE, RETURN_RECIPE
from source_library import publishable_files, stage_dependencies, validate_authored_support

spec=importlib.util.spec_from_file_location('handoff',ROOT/'content/atlas_gis_handoff.py')
handoff=importlib.util.module_from_spec(spec);spec.loader.exec_module(handoff)


class BrowserGis(unittest.TestCase):
    def metadata(self):
        return {'dataset_id':'test','title':'Test-only fixture','observation_status':'test fixture',
            'observation_time':'not an observation','input_crs':'OGC:CRS84','coordinate_order':['longitude','latitude'],
            'field_units':{'value':'test units'},'method':'explicit test fixture',
            'missingness_policy':'preserve null/zero/false/absent','limitations':['Test fixture only.'],
            'sources':[{'source_id':'fixture','source_url':'https://example.org/test',
                'attribution':'Test author','license_statement':'CC BY-NC-SA 4.0 test declaration',
                'license_evidence':'https://example.org/terms'}]}

    def input(self,folder,features,metadata=None,**foreign):
        path=Path(folder)/'input.geojson'
        path.write_text(json.dumps({'type':'FeatureCollection','features':features,**foreign}),encoding='utf-8')
        return handoff.load_input(path,metadata or self.metadata())

    def test_complete_distinct_profiles_and_matching_course_placements(self):
        profiles=load_pathways()['pathways']
        slugs={r['slug'] for r in json.loads((ROOT/'catalog/repositories.json').read_text())['repositories']}
        self.assertEqual({p['slug'] for p in profiles},slugs)
        for key in ['question','ai_prompt','geoai_extension','evidence_check','rustgis_task','geolibre_task']:
            self.assertEqual(len({p[key] for p in profiles}),len(slugs),key)
        for profile in profiles:
            for relative in [f"projects/{profile['slug']}/index.ipynb",f"courses/{profile['slug']}/index.ipynb"]:
                path=ROOT/'content'/relative;nb=nbformat.read(path,4)
                owned=[c for c in nb.cells if c.metadata.get('atlas_browser_gis',{}).get('owner')==OWNER]
                self.assertEqual(len(owned),1)
                self.assertEqual(owned[0].source,pathway_markdown(profile,relative).strip()+'\n')
                for link in re.findall(r'\[[^]]*\]\(([^)]+)\)',owned[0].source):
                    if not link.startswith('https:'):
                        self.assertTrue((path.parent/link).is_file(),(relative,link))

    def test_owner_preserves_cells_outputs_metadata_and_edited_blocks(self):
        with tempfile.TemporaryDirectory(dir=WORK) as folder:
            path=Path(folder)/'index.ipynb'
            nb=nbformat.v4.new_notebook(metadata={'custom':{'keep':[1,2]}},cells=[
                nbformat.v4.new_markdown_cell('Author note',id='legacy'),
                nbformat.v4.new_code_cell('x=42',id='answer',execution_count=8,
                    outputs=[nbformat.v4.new_output('stream',name='stdout',text='kept')])])
            nbformat.write(nb,path);old=json.loads(path.read_text())
            self.assertEqual(reconcile_markdown(path,'Generated','subject:test'),'updated')
            added=json.loads(path.read_text());self.assertEqual(added['cells'][:-1],old['cells'])
            self.assertEqual(added['metadata'],old['metadata'])
            raw=path.read_bytes();self.assertEqual(reconcile_markdown(path,'Generated','subject:test'),'unchanged');self.assertEqual(path.read_bytes(),raw)
            self.assertEqual(reconcile_markdown(path,'Updated','subject:test'),'updated')
            edited=json.loads(path.read_text());edited['cells'][-1]['source']='User revised the pathway\n';path.write_text(json.dumps(edited))
            raw=path.read_bytes();messages=[]
            self.assertEqual(reconcile_markdown(path,'Replacement','subject:test',messages.append),'conflict')
            self.assertEqual(path.read_bytes(),raw);self.assertIn('preserved',messages[0])

    def test_source_notebooks_stay_local_and_non_notebook_inputs_use_canonical_urls(self):
        profiles=load_pathways()['pathways']
        for profile in profiles:
            for notebook in [f"projects/{profile['slug']}/index.ipynb",f"courses/{profile['slug']}/index.ipynb"]:
                rendered=pathway_markdown(profile,notebook)
                for item in profile['source_links']:
                    target=item['path']
                    if target.endswith('.ipynb'):
                        self.assertNotIn('/main/content/'+target,rendered)
                    else:
                        kind='tree' if (ROOT/'content'/target).is_dir() else 'blob'
                        self.assertIn(f'https://github.com/jltobias/JupyterLite-Learning-Atlas/{kind}/main/content/{target}',rendered)
                        self.assertIn('`'+target+'`',rendered)

    def test_duplicate_managed_blocks_preserve_every_byte(self):
        with tempfile.TemporaryDirectory(dir=WORK) as folder:
            path=Path(folder)/'duplicate.ipynb'
            path.write_text(json.dumps({'cells':[],'metadata':{'user':'keep'}}))
            reconcile_markdown(path,'original','subject:duplicate')
            nb=json.loads(path.read_text());nb['cells'].append(deepcopy(nb['cells'][0]));path.write_text(json.dumps(nb))
            before=path.read_bytes();messages=[]
            self.assertEqual(reconcile_markdown(path,'replacement','subject:duplicate',messages.append),'conflict')
            self.assertIn('duplicate',messages[0]);self.assertEqual(path.read_bytes(),before)

    def test_all_six_navigation_blocks_require_exact_ownership_hash_and_content(self):
        with tempfile.TemporaryDirectory(dir=WORK) as folder:
            root=Path(folder)
            for relative in NAVIGATION_NOTEBOOKS:
                path=root/'content'/relative;path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes((ROOT/'content'/relative).read_bytes())
            validate_pathway_blocks(root,[])
            for relative in NAVIGATION_NOTEBOOKS:
                path=root/'content'/relative;original=path.read_bytes()
                for change in ['key','hash','content','type']:
                    nb=json.loads(original);cell=next(c for c in nb['cells'] if c.get('metadata',{}).get('atlas_browser_gis',{}).get('owner')==OWNER)
                    if change=='key':cell['metadata']['atlas_browser_gis']['key']='other'
                    elif change=='hash':cell['metadata']['atlas_browser_gis']['generated_sha256']='0'*64
                    elif change=='type':cell['cell_type']='code'
                    else:
                        cell['source']='Edited block\n';cell['metadata']['atlas_browser_gis']['generated_sha256']=hashlib.sha256(cell['source'].encode()).hexdigest()
                    path.write_text(json.dumps(nb))
                    with self.subTest(relative=relative,change=change),self.assertRaises(AssertionError):validate_pathway_blocks(root,[])
                    path.write_bytes(original)

    def test_real_default_native_fresh_kernel_and_changed_export(self):
        if sys.platform=='win32':asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        runtime=ROOT/'_build/jupyter-runtime';runtime.mkdir(parents=True,exist_ok=True)
        os.environ['JUPYTER_RUNTIME_DIR']=str(runtime)
        with tempfile.TemporaryDirectory(dir=WORK) as folder:
            cwd=stage_dependencies('gis-workbench.ipynb',folder)
            for name in ['atlas_gis_handoff.py','assets/browser-gis-pathways.json','courses/onehealth/data/tracts.geojson','courses/onehealth/data/manifest.json']:
                self.assertEqual((cwd/name).read_bytes(),(ROOT/'content'/name).read_bytes())
            nb=nbformat.read(ROOT/'content/gis-workbench.ipynb',4)
            selection_source=next(c.source for c in nb.cells if c.cell_type=='code' and "minimum_value = 0" in c.source)
            nb.cells.append(nbformat.v4.new_code_cell('''
assert input_summary['feature_count'] == 166
assert input_summary['measurements']['POP100']['numeric_sum'] == 764468
assert package['method']['selection']['output_count'] == 12
assert package['method']['selection']['input_count'] == 166
assert package['method']['source_id_property']['name'] == '_atlas_source_id'
assert all(f['properties']['_atlas_source_id'] == str(f['id']) == f['properties']['GEOID'] for f in package['collection']['features'])
changed = write_handoff(collection, metadata, input_record, Path('exports'), 'native-changed', selected_ids=selected_ids[:2])
assert changed['method']['selection']['output_count'] == 2
written = json.loads(changed['paths']['geojson'].read_text())
assert len(written['features']) == 2
assert all(f['properties']['_atlas_source_id'] == str(f['id']) == f['properties']['GEOID'] for f in written['features'])
assert changed['method']['geojson_sha256'] != package['method']['geojson_sha256']
'''))
            nb.cells.append(nbformat.v4.new_code_cell(selection_source.replace('minimum_value = 0','minimum_value = 5000')
                .replace('selection_limit = 12','selection_limit = 2')
                .replace("output_stem = 'fresno-2020-first12'","output_stem = 'native-threshold'")))
            nb.cells.append(nbformat.v4.new_code_cell('''
assert package['method']['selection']['selected_ids'] == ['06019000400', '06019000902']
threshold_written = json.loads(Path('exports/native-threshold.geojson').read_text())
assert [(f['properties']['_atlas_source_id'], f['properties']['POP100']) for f in threshold_written['features']] == [('06019000400', 5384), ('06019000902', 5263)]
assert package['method']['selection_parameters']['minimum_value'] == 5000
print('ATLAS_NATIVE_GIS_FRESH_PROOF')
'''))
            executed=NotebookClient(nb,timeout=90,kernel_name='python3',resources={'metadata':{'path':str(cwd)}},allow_errors=False).execute()
            self.assertIn('ATLAS_NATIVE_GIS_FRESH_PROOF',executed.cells[-1].outputs[0].text)
            outputs=[output for cell in executed.cells if cell.cell_type=='code' for output in cell.outputs]
            saved_text=''.join(output.get('text','') for output in outputs)
            self.assertIn('Artifact names: exports/fresno-2020-first12.geojson',saved_text)
            self.assertIn('Run this notebook in Lab to create and download these artifacts',saved_text)
            self.assertIn('Input feature count: 166',saved_text)
            self.assertIn('764468',saved_text)
            self.assertFalse(any(re.search(r'href=[\"\']exports/',output.get('data',{}).get('text/html','')) for output in outputs),
                             'Native saved Book outputs must not link to temporary exports')

    def test_roundtrip_source_rights_zero_null_missing_and_no_overwrite(self):
        metadata=self.metadata()
        metadata['modifications']=['Original source processing receipt retained']
        features=[handoff.point_feature('zero',-70,20,{'value':0,'keep':{'source':'original'}}),
            handoff.rectangle_feature('null',[-71,19,-70,20],{'value':None}),
            handoff.point_feature('missing',-69,20,{}),handoff.point_feature(17,-68,20,{'value':False})]
        with tempfile.TemporaryDirectory(dir=WORK) as folder:
            collection,record=self.input(folder,features,license='original NC-SA collection terms',method={'retain':'yes'})
            original=deepcopy(collection)
            result=handoff.write_handoff(collection,metadata,record,Path(folder)/'exports','reviewed',selected_ids=['zero','null','missing',17])
            self.assertEqual(collection,original)
            self.assertEqual(result['collection']['license'],'original NC-SA collection terms')
            self.assertEqual(result['method']['input']['original_collection_metadata']['method'],{'retain':'yes'})
            self.assertEqual(result['method']['sources'],metadata['sources'])
            self.assertEqual(result['method']['supplied_metadata'],metadata)
            measure=result['method']['summary']['measurements']['value']
            self.assertEqual([measure[k] for k in ['zero','null','absent','false']],[1,1,1,1])
            for before,after in zip(features,result['collection']['features']):
                self.assertEqual(after['id'],before['id'])
                self.assertEqual(after['properties']['_atlas_source_id'],str(before['id']))
                self.assertEqual(before['geometry'],after['geometry'])
                self.assertEqual(before['properties'],{k:v for k,v in after['properties'].items() if k not in {'_atlas_handoff','_atlas_source_id'}})
            self.assertEqual(result['method']['source_id_property']['name'],'_atlas_source_id')
            self.assertIn('_atlas_source_id',result['review'])
            self.assertEqual(hashlib.sha256(result['paths']['geojson'].read_bytes()).hexdigest(),result['method']['geojson_sha256'])
            self.assertIn('"value"',result['review']);self.assertIn('zero',result['review'])
            for text in ['not an observation','CC BY-NC-SA 4.0','Test author','Test fixture only.','explicit test fixture','test units']:
                self.assertIn(text,result['review'])
            old={p:p.read_bytes() for p in result['paths'].values()}
            handoff.write_handoff(collection,metadata,record,Path(folder)/'exports','reviewed')
            with self.assertRaises(FileExistsError):handoff.write_handoff(collection,metadata,record,Path(folder)/'exports','reviewed',selected_ids=['zero'])
            self.assertEqual({p:p.read_bytes() for p in old},old)
            empty=handoff.write_handoff(collection,metadata,record,Path(folder)/'exports','empty',selected_ids=[])
            self.assertEqual(empty['collection']['features'],[]);self.assertTrue(empty['method']['selection']['empty'])
            self.assertNotIn('bbox',empty['collection'])
            for stem in ['../input','nested/path','C:\\escape','bad.name']:
                with self.assertRaises(ValueError):handoff.write_handoff(collection,metadata,record,Path(folder)/'exports',stem)

    def test_invalid_geometry_crs_attribution_and_selection_stop_export(self):
        feature=handoff.point_feature('a',-120,35,{'value':1})
        collection={'type':'FeatureCollection','features':[feature]};metadata=self.metadata()
        for coordinates in [[True,35],[-120,False],[float('nan'),30],[0,float('inf')],[20,95],[181,20],[1,2,3],['0',2]]:
            with self.subTest(coordinates=coordinates),self.assertRaises(ValueError):
                bad=deepcopy(collection);bad['features'][0]['geometry']['coordinates']=coordinates;handoff.validate_collection(bad,metadata)
        for crs in ['EPSG:3857','unknown','EPSG:4326']:
            with self.subTest(crs=crs),self.assertRaises(ValueError):handoff.validate_collection(collection,{**metadata,'input_crs':crs})
        for key in ['sources','field_units','coordinate_order']:
            bad=deepcopy(metadata);bad.pop(key)
            with self.subTest(key=key),self.assertRaises(ValueError):handoff.validate_collection(collection,bad)
        bad=deepcopy(collection);bad['features'].append(deepcopy(feature))
        with self.assertRaisesRegex(ValueError,'Duplicate'):handoff.validate_collection(bad,metadata)
        for bounds in [[170,0,-170,1],[0,0,0,1],[-180,0,180,1]]:
            with self.assertRaises(ValueError):handoff.rectangle_feature('bad',bounds,{})
        bad=deepcopy(collection);bad['features'][0]['geometry']={'type':'Polygon','coordinates':[[[0,0],[1,0],[1,1],[0,1]]]}
        with self.assertRaisesRegex(ValueError,'closed'):handoff.validate_collection(bad,metadata)
        bad=deepcopy(collection);bad['features'][0]['properties']['value']=float('inf')
        with self.assertRaises(ValueError):handoff.validate_collection(bad,metadata)
        for reserved in ['_atlas_handoff','_atlas_source_id']:
            bad=deepcopy(collection);bad['features'][0]['properties'][reserved]='conflicting original property'
            with self.subTest(reserved=reserved),self.assertRaisesRegex(ValueError,'Reserved'):
                handoff.validate_collection(bad,metadata)
        with tempfile.TemporaryDirectory(dir=WORK) as folder:
            data,record=self.input(folder,[feature])
            for ids in [['unknown'],['a','a']]:
                with self.assertRaises(ValueError):handoff.write_handoff(data,metadata,record,Path(folder)/'exports','bad',selected_ids=ids)
            self.assertFalse((Path(folder)/'exports').exists())

    def test_mutated_loaded_collection_cannot_use_original_receipt(self):
        with tempfile.TemporaryDirectory(dir=WORK) as folder:
            collection,receipt=self.input(folder,[handoff.point_feature('a',1,2,{'value':4})])
            for change in ['value','geometry','id']:
                changed=deepcopy(collection)
                if change=='value':changed['features'][0]['properties']['value']=5
                elif change=='geometry':changed['features'][0]['geometry']['coordinates']=[2,3]
                else:changed['features'][0]['id']='b'
                with self.subTest(change=change),self.assertRaisesRegex(ValueError,'changed after load_input'):
                    handoff.write_handoff(changed,self.metadata(),receipt,Path(folder)/'exports','mutated')
                self.assertFalse((Path(folder)/'exports').exists())

    def test_source_references_are_checked_for_single_and_multiple_sources(self):
        collection={'type':'FeatureCollection','features':[handoff.point_feature('a',1,2,{'value':1})]}
        for refs in [[],None,'fixture',['unknown'],['fixture','fixture'],[{}],[False],['']]:
            changed=deepcopy(collection);changed['features'][0]['properties']['source_ids']=refs
            with self.subTest(refs=refs),self.assertRaisesRegex(ValueError,'source_ids'):
                handoff.validate_collection(changed,self.metadata())
        collection['features'][0]['properties']['source_ids']=['fixture']
        handoff.validate_collection(collection,self.metadata())
        metadata=self.metadata();metadata['sources'].append({**metadata['sources'][0],'source_id':'second'})
        del collection['features'][0]['properties']['source_ids']
        with self.assertRaisesRegex(ValueError,'source_ids'):handoff.validate_collection(collection,metadata)

    def test_nonnumeric_and_all_unknown_measurements_are_explicit(self):
        features=[handoff.point_feature(str(i),1,2,p) for i,p in enumerate([{'value':0},{'value':None},{},{'value':''},{'value':False},{'value':'unknown'},{'value':3}])]
        summary=handoff.summarize({'features':features},{'value':'rate'})
        m=summary['measurements']['value']
        self.assertEqual([m[k] for k in ['numeric_count','nonnumeric_count','absent','null','empty_string','zero','false','numeric_sum']],[2,3,1,1,1,1,1,3])
        self.assertIn('not an approved aggregation',summary['numeric_sum_scope'])
        unknown=handoff.summarize({'features':features[1:3]},{'value':'temperature'})['measurements']['value']
        self.assertEqual(unknown['numeric_count'],0);self.assertIsNone(unknown['numeric_sum'])

    def test_complete_package_limit_and_string_selection_fail_before_writes(self):
        with tempfile.TemporaryDirectory(dir=WORK) as folder:
            output=Path(folder)/'exports'
            collection,receipt=self.input(folder,[handoff.point_feature(i,1,2,{'value':1}) for i in ['1','2']])
            with self.assertRaisesRegex(ValueError,'explicit list or tuple'):
                handoff.write_handoff(collection,self.metadata(),receipt,output,'string-selection',selected_ids='12')
            self.assertFalse(output.exists())
            metadata=self.metadata();metadata['extra_provenance']='é'*30000
            with self.assertRaisesRegex(ValueError,'Complete UTF-8 evidence package'):
                handoff.write_handoff(collection,metadata,receipt,output,'large-method',max_bytes=10000)
            self.assertFalse(output.exists())
            collection,receipt=self.input(folder,[handoff.point_feature('x'*12000+str(i),1,2,{'value':1}) for i in range(2)])
            with self.assertRaisesRegex(ValueError,'Complete UTF-8 evidence package'):
                handoff.write_handoff(collection,self.metadata(),receipt,output,'large-exclusions',selected_ids=[],max_bytes=10000)
            self.assertFalse(output.exists())

    def test_optional_csv_recipe_uses_actual_rows_and_retains_raw_values(self):
        state={};recipe=CSV_RECIPE.split('```python\n',1)[1].split('```',1)[0]
        with patch.dict(sys.modules,{'atlas_gis_handoff':handoff}):exec(recipe,state)
        previous=Path.cwd()
        try:
            os.chdir(ROOT/'content')
            expected={'usgs':('us6000m0xj',[137.2491,37.4933]),'cholera-deaths':('0',[-0.13793,51.513418]),
                'cholera-pumps':('250',[-0.136668,51.513341]),'landcover':('C_00_00',[-105.25,39.55])}
            for kind,(identity,xy) in expected.items():
                profile=state['csv_profiles'][kind];metadata=self.metadata();metadata['observation_status']=profile['status'];metadata['sources'][0]['license_evidence']=profile['notice']
                prepared,record=state['_prepare_csv_points'](kind,metadata,2)
                self.assertEqual(prepared['features'][0]['id'],identity)
                self.assertEqual(prepared['features'][0]['geometry']['coordinates'],xy)
                import csv
                with Path(profile['path']).open(encoding='utf-8-sig',newline='') as stream:raw=next(csv.DictReader(stream))
                self.assertEqual({k:prepared['features'][0]['properties'][k] for k in raw},raw)
                self.assertEqual(record['csv_preparation']['source_csv_sha256'],hashlib.sha256(Path(profile['path']).read_bytes()).hexdigest())
                self.assertEqual(record['csv_preparation']['retained_notice'],Path(profile['notice']).read_text(encoding='utf-8'))
                typed_expected={'usgs':{'_csv_depth_km':10.0,'_csv_magnitude':5.8},'cholera-deaths':{'_csv_DEATHS':3.0},
                    'cholera-pumps':{},'landcover':{'_csv_elevation_m':1923.3,'_csv_ndvi':0.442}}[kind]
                for field,value in typed_expected.items():self.assertEqual(prepared['features'][0]['properties'][field],value)
                if kind=='landcover':self.assertEqual(prepared['features'][0]['properties']['x'],'0');self.assertNotEqual(xy,[0,0])
                if kind=='cholera-pumps':self.assertNotIn('_csv_DEATHS',prepared['features'][0]['properties'])
        finally:os.chdir(previous)

    def test_returned_artifact_recipe_matches_portable_ids_without_reingestion(self):
        state={};exec(RETURN_RECIPE.split('```python\n',1)[1].split('```',1)[0],state)
        original={'collection':{'features':[{'id':'source-0001','properties':{'_atlas_source_id':'source-0001','value':5}}]}}
        returned={'type':'FeatureCollection','features':[{'id':1,'properties':{'_atlas_source_id':'source-0001','value':7}}]}
        before=deepcopy(returned)
        result=state['_inspect_returned'](returned,original,['value'])
        self.assertEqual(result[0]['original_feature_id'],'source-0001');self.assertEqual(result[0]['returned_app_id'],1)
        self.assertEqual(result[0]['values']['value'],{'original_present':True,'original':5,'returned_present':True,'returned':7})
        self.assertEqual(returned,before)

    def test_narrow_audited_helper_publication(self):
        manifest=validate_authored_support()
        self.assertEqual([f['local_path'] for f in manifest['files']],['atlas_gis_handoff.py'])
        self.assertIn(ROOT/'content/atlas_gis_handoff.py',publishable_files())
        self.assertEqual(set(manifest['dependencies']),{'gis-workbench.ipynb'})


if __name__=='__main__':unittest.main()
