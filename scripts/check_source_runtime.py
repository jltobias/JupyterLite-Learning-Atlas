"""Fresh Pyodide proof for selected imported source lessons, separate from SVG fixtures.

Runs the actual canonical code in a new browser context/kernel per case. Local
inputs must load through the packaged Lab filesystem and match canonical hashes;
no saved output, rewritten lesson, staged replacement dataset or loaded shell
can satisfy the unique executed proof marker.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
import urllib.request
import uuid
from pathlib import Path
from urllib.parse import quote

import nbformat
from playwright.sync_api import sync_playwright

from check_runtime import select_python

ROOT = Path(__file__).resolve().parents[1]

POPULATION_ASSERTIONS = '''
assert len(data['layers']) == 4
assert [layer['metadata']['id'] for layer in data['layers']] == ['worldpop-2025', 'grid3-2025', 'landscan-2020', 'ghspop-2025']
assert data['default_aoi'] == oracle['default_aoi'] == [3.3, 6.45, 3.45, 6.6]
_aoi_results = compare(data['layers'], oracle['default_aoi'])
for _result in _aoi_results:
    _expected = oracle['sources'][_result['metadata']['id']]
    assert abs(_result['population'] - _expected['aoi_population']) < .0001
    assert abs(_result['coverage'] - _expected['aoi_coverage']) < 1e-10
    assert _result['intersected_cells'] == _expected['aoi_intersected_cells']
    assert _result['metadata']['synthetic'] is False
    for _field in ('source', 'citation', 'license', 'license_url', 'version', 'reference_date', 'population_concept', 'modification'):
        assert _result['metadata'][_field]
    assert _result['metadata']['license'] == 'CC BY 4.0'
assert abs(_aoi_results[0]['population'] - 3058259.422010836) < .0001
assert abs(_aoi_results[2]['population'] - 7422966.9999449905) < .0001
'''

POPULATION_EXPORT_ASSERTIONS = '''
import csv, io
_csv_rows = list(csv.DictReader(Path('outputs/real-comparison.csv').open(encoding='utf-8')))
_export = json.loads(Path('outputs/real-comparison.json').read_text(encoding='utf-8'))
_cell_export = json.loads(Path('outputs/real-count-cell.geojson').read_text(encoding='utf-8'))
assert len(_csv_rows) == len(_export['results']) == 4
assert _export['results'] == results
assert _export['bounds'] == data['default_aoi'] and _export['method'] == METHOD
assert 'CC BY 4.0' in _export['notice'] and 'no endorsement' in _export['notice']
for _csv_row, _result in zip(_csv_rows, results):
    assert json.loads(_csv_row['metadata_json']) == _result['metadata']
    assert abs(float(_csv_row['population']) - _result['population']) < 1e-8
    assert _csv_row['citation'] == _result['metadata']['citation']
    assert _csv_row['version'] == _result['metadata']['version']
    assert _csv_row['license_url'] == 'https://creativecommons.org/licenses/by/4.0/'
assert _cell_export == document
assert _cell_export['metadata']['synthetic'] is False
assert _cell_export['metadata']['citation'] == data['layers'][3]['metadata']['citation']
assert compare([import_geojson(_cell_export)], cell['bounds'])[0]['population'] == cell['population']
'''

ONEHEALTH_ASSERTIONS = '''
assert manifest['scene_id'] == 'LC09_L2SP_042035_20240830_02_T1'
assert manifest['population_date'] == '2020-04-01'
assert manifest['sample_count'] == len(data) == 6890 and len(tracts) == 166
assert sum(bool(r['valid']) for r in data) == 6890
assert abs(avg('red') - 0.1426091211901306) < 1e-12
assert abs(avg('temperature_c') - 43.56588259297533) < 1e-10
assert abs(data[0]['red'] - .1933875) < 1e-12
assert abs(data[0]['temperature_c'] - 43.9413876) < 1e-8
assert manifest['source_grid_m'] == 30 and manifest['thermal_native_resolution_m'] == 100
assert 'USGS' in ' '.join(manifest['credits']) and 'Census' in ' '.join(manifest['credits'])
'''

EO_ASSERTIONS = '''
assert len(catalog['satellites']) == 958
assert {s['id'] for s in selected} == {'landsat-8', 'landsat-9', 'sentinel-2b', 'sentinel-2c', 'enmap'}
assert mission['id'] == 'landsat-8' and mission['evidence']
_comparison = comparison(catalog, ['landsat-8', 'sentinel-1c', 'enmap', 'goes-19'])
assert 'Contextual comparison; no universal ranking' in _comparison.data
for _name in ('Landsat 8', 'Sentinel-1C', 'EnMAP', 'GOES-19'):
    assert _name in _comparison.data
_rows = list(csv.DictReader(export_path.open(encoding='utf-8')))
assert len(_rows) == sum(len(s['sensors']) for s in selected) == 6
assert all(r['source_urls'].startswith('https://') for r in _rows)
assert all(r['spatial_context'] and r['temporal_context'] for r in _rows)
from IPython.display import display
display(_comparison)
'''

SPATIAL_ASSERTIONS = '''
assert len(points) == len(assigned) == 80
assert assigned.groupby('nearest').size().to_dict() == {'clinic':39, 'school':40, 'warehouse':1}
assert abs(assigned['distance'].mean() - 1.0052428391442043) < 1e-12
assert abs(points.iloc[0]['x'] - 3.4369468482303027) < 1e-12
for _row in assigned.itertuples():
    _nearest = min(facilities, key=lambda name: math.hypot(_row.x-facilities[name][0], _row.y-facilities[name][1]))
    assert _row.nearest == _nearest
    assert abs(_row.distance - math.hypot(_row.x-facilities[_nearest][0], _row.y-facilities[_nearest][1])) < 1e-12
'''

POPULATION_FILES = ['population_tools_real.py', 'population_tools.py', 'population.json', 'independent_oracle.json']
CASES = [
    {'label':'population-comparison', 'notebook':'courses/population-data-comparison/01_real_population.ipynb',
     'files':POPULATION_FILES, 'assertions':POPULATION_ASSERTIONS},
    {'label':'population-coverage', 'notebook':'courses/population-data-comparison/02_real_coverage.ipynb',
     'files':POPULATION_FILES, 'assertions':POPULATION_ASSERTIONS + '''
assert zero['population'] == 0 and abs(zero['coverage']-1) < 1e-10
assert missing['population'] is None and missing['coverage'] == 0
assert abs(half['population'] - cell['population']/2) < 1e-6
'''},
    {'label':'population-exports', 'notebook':'courses/population-data-comparison/03_real_exports.ipynb',
     'files':POPULATION_FILES, 'assertions':POPULATION_ASSERTIONS + POPULATION_EXPORT_ASSERTIONS,
     'absent':['outputs/real-comparison.csv','outputs/real-comparison.json','outputs/real-count-cell.geojson']},
    {'label':'onehealth-qa', 'notebook':'courses/onehealth/03_qa_scaling.ipynb',
     'files':['data/manifest.json','data/pixels.csv','data/tracts.geojson'], 'assertions':ONEHEALTH_ASSERTIONS, 'pngs':1},
    {'label':'eo-sensor-comparison', 'notebook':'courses/eo-satellite-guide/02_sensor_comparison.ipynb',
     'files':['eo_guide.py','data/catalog.json'], 'assertions':EO_ASSERTIONS, 'absent':['my-sensor-comparison.csv'],
     'html':'Contextual comparison; no universal ranking'},
    {'label':'spatial-vc', 'notebook':'courses/spatial-analysis/01_VC_vector-conversion.ipynb', 'files':[],
     'setup':"import piplite\nawait piplite.install(['numpy','pandas','matplotlib'])\nget_ipython().run_line_magic('matplotlib','inline')",
     'assertions':SPATIAL_ASSERTIONS, 'pngs':2},
]


def execute_case(browser, base, output, timeout, case):
    notebook_path=case['notebook'];canonical=ROOT/'content'/notebook_path
    nb=nbformat.read(canonical,as_version=4)
    code='\n\n'.join(c.source for c in nb.cells if c.cell_type=='code')
    asset_hashes={name:hashlib.sha256((canonical.parent/name).read_bytes()).hexdigest() for name in case['files']}
    context=browser.new_context(viewport={'width':1440,'height':1000})
    page=context.new_page();errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
    # Jupyter Contents transports text with universal newlines and JSON models
    # via JSON.stringify (e.g. 0.0 becomes 0). Require exact raw HTTP bytes and
    # only these precisely computed transport forms inside the mounted kernel.
    filesystem_hashes={}
    for name in case['files']:
        text=(canonical.parent/name).read_text(encoding='utf-8')
        forms=[text]
        if Path(name).suffix in {'.json','.geojson'}:
            forms.append(page.evaluate('text=>JSON.stringify(JSON.parse(text))',text))
        filesystem_hashes[name]=sorted({asset_hashes[name],*[hashlib.sha256(form.encode()).hexdigest() for form in forms]})
    marker='ATLAS_SOURCE_PYODIDE_PROOF_'+uuid.uuid4().hex
    prelude=("import sys, json, hashlib\nfrom pathlib import Path\n"
             "assert sys.platform == 'emscripten', 'A fresh real Pyodide kernel is required'\n"
             f"_atlas_expected_assets = {filesystem_hashes!r}\n"
             "_atlas_actual_assets = {name:hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in _atlas_expected_assets}\n"
             "assert all(_atlas_actual_assets[name] in expected for name,expected in _atlas_expected_assets.items()), 'Packaged notebook-relative input content differs: '+repr(_atlas_actual_assets)\n"
             f"assert not any(Path(name).exists() for name in {case.get('absent',[])!r}), 'A fresh context must not contain prior exports'\n")
    proof="\n"+case['assertions']+f"\nprint({marker!r}, json.dumps({{'platform':sys.platform,'asset_sha256':_atlas_actual_assets,'assertions':'passed'}}))\n"
    source=prelude+case.get('setup','')+'\n\n'+code+proof
    try:
        for name,expected in asset_hashes.items():
            relative=(Path(notebook_path).parent/name).as_posix()
            response=page.request.get(base+'lite/files/'+quote(relative,safe='/'))
            assert response.ok and hashlib.sha256(response.body()).hexdigest()==expected, f'Missing/different packaged asset: {relative}'
        page.goto(base+'lite/lab/index.html?path='+quote(notebook_path,safe='/'),wait_until='domcontentloaded')
        page.locator('.jp-Notebook').wait_for(timeout=timeout*1000)
        select_python(page,timeout*1000)
        editor=page.locator('.jp-Notebook .jp-CodeCell .cm-content').first
        editor.wait_for(timeout=30000);editor.click();page.keyboard.press('ControlOrMeta+a');page.keyboard.insert_text(source)
        assert marker in editor.inner_text()
        page.keyboard.press('ControlOrMeta+Enter')
        page.wait_for_function("""marker=>[...document.querySelectorAll('.jp-Notebook .jp-OutputArea-output')].some(e=>e.textContent.includes(marker) || e.textContent.includes('Traceback (most recent call last)'))""",arg=marker,timeout=timeout*1000)
        failure=page.locator('.jp-Notebook .jp-OutputArea-output').filter(has_text='Traceback (most recent call last)')
        if failure.count():raise RuntimeError('Fresh source execution failed: '+failure.first.inner_text())
        proof_output=page.locator('.jp-Notebook .jp-OutputArea-output').filter(has_text=marker)
        proof_output.wait_for(state='attached',timeout=timeout*1000);proof_output.scroll_into_view_if_needed()
        text=proof_output.inner_text();line=next(line for line in text.splitlines() if line.startswith(marker+' '))
        evidence=json.loads(line[len(marker)+1:])
        assert evidence['platform']=='emscripten' and evidence['assertions']=='passed'
        assert set(evidence['asset_sha256'])==set(filesystem_hashes)
        assert all(value in filesystem_hashes[name] for name,value in evidence['asset_sha256'].items())
        cell=proof_output.locator("xpath=ancestor::div[contains(@class, 'jp-CodeCell')][1]")
        assert not cell.locator('.jp-OutputArea .jp-mod-error').count(), f'Source {case["label"]} returned an error'
        images=[]
        for graphic in cell.locator('.jp-OutputArea-output img').all():
            rendered=graphic.evaluate('''async image=>{
                await image.decode();const response=await fetch(image.currentSrc||image.src);
                const bytes=new Uint8Array(await response.arrayBuffer());
                const hash=await crypto.subtle.digest('SHA-256',bytes);
                return {width:image.naturalWidth,height:image.naturalHeight,header:Array.from(bytes.slice(0,8)),
                    sha256:Array.from(new Uint8Array(hash)).map(n=>n.toString(16).padStart(2,'0')).join('')};
            }''')
            assert rendered['header']==[137,80,78,71,13,10,26,10], 'Expected a newly generated PNG, not the original SVG gate'
            assert rendered['width']>=200 and rendered['height']>=100
            images.append(rendered)
        assert len(images)>=case.get('pngs',0), f'Missing fresh {case["label"]} PNG figures'
        if case.get('html'):
            assert case['html'] in cell.locator('.jp-OutputArea').inner_text(), 'Missing freshly displayed source comparison table'
        assert not errors,errors
        page.screenshot(path=str(output/f'executed-{case["label"]}.png'))
        result={'status':'passed','notebook':notebook_path,'marker':marker,'proof':evidence,'pngs':images,
                'raw_http_asset_sha256':asset_hashes,'allowed_filesystem_sha256':filesystem_hashes,
                'filesystem_text_transport':'Jupyter Contents universal newlines; JSON text or precisely computed JavaScript JSON.stringify model; UTF-8',
                'canonical_sha256':hashlib.sha256(canonical.read_bytes()).hexdigest(),
                'canonical_code_sha256':hashlib.sha256(code.encode()).hexdigest(),'numerical_assertions':case['assertions']}
        print(f'PASS fresh source Pyodide {case["label"]}: notebook-relative assets, numerical/export assertions, unique marker, {len(images)} PNGs',flush=True)
        return result
    except Exception:
        (output/f'failure-{case["label"]}-body.txt').write_text(page.locator('body').inner_text(),encoding='utf-8')
        page.screenshot(path=str(output/f'failure-{case["label"]}.png'))
        raise
    finally:context.close()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--browser-executable')
    parser.add_argument('--timeout',type=int,default=360,help='Per-case runtime/package startup and execution timeout in seconds')
    parser.add_argument('--case',choices=[c['label'] for c in CASES],action='append',help='Debug a subset; CI runs all six cases')
    parser.add_argument('--port',type=int,default=8768)
    args=parser.parse_args();cases=[c for c in CASES if not args.case or c['label'] in args.case]
    output=ROOT/'_build/runtime-source-browser';output.mkdir(parents=True,exist_ok=True)
    base=f'http://127.0.0.1:{args.port}/JupyterLite-Learning-Atlas/'
    log=(output/'server.log').open('w',encoding='utf-8')
    server=subprocess.Popen([sys.executable,'scripts/serve.py','--port',str(args.port)],cwd=ROOT,stdout=log,stderr=log)
    results=[];status='failed'
    try:
        for _ in range(50):
            try:urllib.request.urlopen(base,timeout=1).close();break
            except OSError:time.sleep(.2)
        else:raise RuntimeError('Local atlas preview did not start')
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(headless=True,executable_path=args.browser_executable)
            try:
                for case in cases:
                    print('START fresh source Pyodide '+case['label'],flush=True)
                    results.append(execute_case(browser,base,output,args.timeout,case))
                status='passed'
            finally:browser.close()
    finally:
        server.terminate();server.wait(timeout=10);log.close()
        (output/'results.json').write_text(json.dumps({'status':status,'cases':results,
            'selected_cases':[c['label'] for c in cases],
            'method':'Separate fresh browser context and actual Pyodide kernel per case; canonical code runs against hash-checked packaged notebook-relative files, plus oracle/numerical/export assertions, unique executed markers and loaded PNG checks where relevant.',
            'limits':'These six explicitly selected source notebooks only. Initial runtime/package retrieval requires network access. No native, credential, external provider or live acquisition branch is certified. The existing seven-case SVG runtime gate remains separate.'},indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
