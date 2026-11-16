"""Actual Pyodide and graphics gate for the four appended course pathways."""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
import time
import urllib.request

from check_expansion import COMPANION_ASSERTIONS, C3S_ASSERTIONS, DESTINE_ASSERTIONS, URBAN_ASSERTIONS
from source_library import ROOT

COMPANIONS={
 'c3s-atlas':'Synthetic latitude weighting and coverage',
 'destination-earth-digital-twin':'Synthetic interpolation contributions',
 'urbanity':'Synthetic street-node degrees',
 'terrio':'Idealized Mercator local length scale',
}
C3S_FILES=['atlas_helpers.py','data/reference/CMIP6_WarmingLevels.csv','data/reference/ne_110m_coastline.geojson']
UPLOAD_PROVENANCE={key:value for key,value in zip(
    ['data_kind','source','variable','units','region','statistic','reference_period','licence','transformations'],
    ['synthetic','Original local synthetic verification fixture; no provider observations','fictional temperature','test units','fictional region','monthly value','2000-01 through 2000-03','CC0 original fixture','none'])}


def upload_setup(*,null_source=False,missing_month=False):
    metadata=dict(UPLOAD_PROVENANCE)
    if null_source:metadata['source']=None
    csv='date,value\n2000-01-01,1\n'+('' if missing_month else '2000-02-01,\n')+'2000-03-01,3\n'
    return f"Path('my_series.csv').write_text({csv!r},encoding='utf-8')\nPath('my_series.json').write_text({json.dumps(metadata)!r},encoding='utf-8')\n"


CASES=[
 {'label':'c3s-provenance','notebook':'courses/c3s-atlas/02-data-and-provenance.ipynb',
  'files':C3S_FILES+['data/manifest.json','data/reference/atlas-catalogue.json'],
  'assertions':"assert len(audit)==3 and all(row['verified'] for row in audit)\nassert _reference_http_hashes=={key:value[0] for key,value in _reference_pins.items()}"},
 {'label':'c3s-weights','notebook':'courses/c3s-atlas/14-regions-and-weights.ipynb','files':C3S_FILES,
  'assertions':C3S_ASSERTIONS+"\nassert weighted<unweighted and 0<coverage<1\n",'plotly':1,'climate':'regional','plotly_download':True},
 {'label':'c3s-globe','notebook':'courses/c3s-atlas/16-globes-and-3d-maps.ipynb','files':C3S_FILES,
  'assertions':C3S_ASSERTIONS+"\nassert abs(float(np.linalg.norm(xyz))-1)<1e-12\n",'plotly':2,'climate':'global-2d'},
 {'label':'c3s-upload','notebook':'courses/c3s-atlas/19-bring-real-data.ipynb',
  'files':['atlas_helpers.py','data/examples/monthly_series.csv','data/examples/monthly_series.json'],
  'setup':upload_setup(),'absent':['my_series.csv','my_series.json'],
  'assertions':"assert len(actual)==3 and actual.value.isna().tolist()==[False,True,False]\nassert provenance['data_kind']=='synthetic' and actual.value.iloc[0]==1 and actual.value.iloc[2]==3",'plotly':1},
 {'label':'c3s-upload-null','notebook':'courses/c3s-atlas/19-bring-real-data.ipynb',
  'files':['atlas_helpers.py','data/examples/monthly_series.csv','data/examples/monthly_series.json'],
  'setup':upload_setup(null_source=True),'expected_error':'Provenance fields must be populated.',
  'assertions':"assert 'Provenance fields' in _atlas_expected_error"},
 {'label':'c3s-upload-gap','notebook':'courses/c3s-atlas/19-bring-real-data.ipynb',
  'files':['atlas_helpers.py','data/examples/monthly_series.csv','data/examples/monthly_series.json'],
  'setup':upload_setup(missing_month=True),'expected_error':'Missing month:',
  'assertions':"assert 'Missing month:' in _atlas_expected_error"},
 {'label':'destine-interpolation','notebook':'courses/destination-earth-digital-twin/11-interpolation.ipynb',
  'files':['earthlab.py'],'assertions':DESTINE_ASSERTIONS+"\nassert abs(float(estimated)-285.7)<1e-12\n",'pngs':1},
 {'label':'destine-globe','notebook':'courses/destination-earth-digital-twin/17-globe.ipynb',
  'files':['earthlab.py'],'assertions':DESTINE_ASSERTIONS,'pngs':1,'skip_widgets':True},
 {'label':'urbanity-streets','notebook':'courses/urbanity/notebooks/street-networks.ipynb',
  'files':[],'assertions':URBAN_ASSERTIONS},
]


def main():
    from check_runtime import execute_case as companion_case
    from check_source_runtime import execute_case as source_case
    from playwright.sync_api import sync_playwright
    parser=argparse.ArgumentParser();parser.add_argument('--browser-executable');parser.add_argument('--timeout',type=int,default=360)
    parser.add_argument('--case',action='append',choices=[*COMPANIONS,*[c['label'] for c in CASES]])
    parser.add_argument('--port',type=int,default=8771);args=parser.parse_args()
    output=ROOT/'_build/expansion-browser';output.mkdir(parents=True,exist_ok=True)
    base=f'http://127.0.0.1:{args.port}/JupyterLite-Learning-Atlas/'
    log=(output/'server.log').open('w',encoding='utf-8')
    server=subprocess.Popen([sys.executable,'scripts/serve.py','--port',str(args.port)],cwd=ROOT,stdout=log,stderr=log)
    results=[];status='failed'
    try:
        for _ in range(50):
            try:urllib.request.urlopen(base,timeout=1).close();break
            except OSError:time.sleep(.2)
        else:raise RuntimeError('Local preview did not start')
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(headless=True,executable_path=args.browser_executable)
            try:
                for slug,title in COMPANIONS.items():
                    if args.case and slug not in args.case:continue
                    results.append(companion_case(browser,base,output,args.timeout,f'projects/{slug}/index.ipynb',COMPANION_ASSERTIONS[slug],title,slug))
                for case in CASES:
                    if args.case and case['label'] not in args.case:continue
                    print('START fresh source Pyodide '+case['label'],flush=True)
                    results.append(source_case(browser,base,output,args.timeout,case))
                status='passed'
            finally:browser.close()
    finally:
        server.terminate();server.wait(timeout=10);log.close()
        (output/'results.json').write_text(json.dumps({'status':status,'cases':results,
            'method':'Fresh browser context and actual Pyodide kernel per case; canonical packaged inputs checked by raw HTTP and kernel filesystem hashes, independent numerical oracles and unique executed markers. Fresh SVG/PNG and loaded Plotly DOM/WebGL plus globe drag are separate graphics evidence.',
            'limits':'Four stdlib companions and explicitly declared safe source/upload cases; upload fixtures are original synthetic local files. DestinE optional widget-only globe cell skipped under its exact reviewed contract. These checks do not certify widget frontend support, real DestinE services or native Urbanity. TerrIO source reading copies require the matched0.29 source runtime and are not executed in Atlas314.'},indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
