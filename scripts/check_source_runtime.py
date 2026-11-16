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
from expansion_runtime_contracts import reviewed_widget_indices
from climate_plot_oracles import assert_climate_plot
from browser_runtime_diagnostics import attach_diagnostics, sanitized_text, EXECUTION_STATE_JS, guarded_execution

ROOT = Path(__file__).resolve().parents[1]

CHOLERA_ASSERTIONS = r'''
assert len(deaths_df) == 250 and int(deaths_df['DEATHS'].sum()) == 489
assert len(pumps_df) == 8
assert abs(sum(float(row.LAT)*int(row.DEATHS) for row in deaths_df.itertuples())/489 - 51.51339831083845) < 1e-12
assert abs(sum(float(row.LON)*int(row.DEATHS) for row in deaths_df.itertuples())/489 - (-0.1364029734151329)) < 1e-12
_base_layers = [layer for layer in map1._children.values() if isinstance(layer, folium.TileLayer)]
assert len(_base_layers) == 1 and _base_layers[0].tiles == 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
assert 'OpenStreetMap' in _base_layers[0].options['attribution']
_mortality = [layer for layer in map1._children.values() if isinstance(layer, folium.CircleMarker) and layer.options['fillColor'] == 'red']
_pumps = [layer for layer in map1._children.values() if isinstance(layer, folium.RegularPolygonMarker) and layer.options['fillColor'] == 'blue']
assert len(_mortality) == 250 and len(_pumps) == 8
assert [layer.options['radius'] for layer in _mortality] == deaths_df['DEATHS'].tolist()
assert all(layer.options['fill'] and layer.options['fillOpacity'] == 1 for layer in _mortality+_pumps)
assert all(any(isinstance(child, folium.Popup) for child in layer._children.values()) for layer in _mortality+_pumps)
import re as _re
from html import unescape as _unescape
def _bound_popup_text(layer):
    popup = next(child for child in layer._children.values() if isinstance(child, folium.Popup))
    return ' '.join(_re.sub('<[^>]*>', ' ', _unescape(popup.html.render())).split())
for _layer, _row in zip(_mortality, deaths_df.itertuples()):
    assert list(_layer.location) == [float(_row.LAT), float(_row.LON)]
    _text = _bound_popup_text(_layer)
    _coordinate = _re.search(r'Location: *\(([-+0-9.eE]+), *([-+0-9.eE]+)\)', _text)
    assert _coordinate and all(abs(float(value)-expected)<1e-12 for value,expected in zip(_coordinate.groups(),[_row.LAT,_row.LON]))
    assert int(_re.search(r'Deaths: *(\d+)', _text).group(1)) == int(_row.DEATHS)
for _layer, _row in zip(_pumps, pumps_df.itertuples()):
    assert list(_layer.location) == [float(_row.LAT), float(_row.LON)]
    _text = _bound_popup_text(_layer)
    _coordinate = _re.search(r'Location: *\(([-+0-9.eE]+), *([-+0-9.eE]+)\)', _text)
    assert _coordinate and all(abs(float(value)-expected)<1e-12 for value,expected in zip(_coordinate.groups(),[_row.LAT,_row.LON]))
    assert _re.search(r'Street Name: *(.*)$', _text).group(1) == _row.Street
assert list(map1.location) == [51.513578, -0.136722] and map1.options['zoom'] == 17
assert folium.__version__ == '0.20.0'
'''
CHOLERA_MEAN_ASSERTIONS = '''
assert abs(mean_LAT - 51.51339831083845) < 1e-12
assert abs(mean_LON - (-0.1364029734151329)) < 1e-12
assert tuple(mean_center_POINT) == (mean_LAT, mean_LON)
_mean = [layer for layer in map1._children.values() if isinstance(layer, folium.CircleMarker) and layer.options['fillColor'] == 'yellowgreen']
assert len(_mean) == 1 and list(_mean[0].location) == list(mean_center_POINT)
'''

# Original schematic test image, not a provider tile or geographic dataset.
CHOLERA_TILE_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256">
<rect width="256" height="256" fill="#e1e5df"/>
<path d="M0 40H256M0 150H256M50 0V256M180 0V256" stroke="#fff" stroke-width="14"/>
<path d="M0 40H256M0 150H256M50 0V256M180 0V256" stroke="#b6bdb2" stroke-width="1"/>
<text x="65" y="105" fill="#58614f" font-size="13">TEST TILE</text></svg>'''
CHOLERA_TILES_READY = '''() => {
    const map=window[document.querySelector('.folium-map').id];
    const layers=Object.values(map._layers).filter(layer=>layer instanceof L.TileLayer);
    const images=[...map.getPane('tilePane').querySelectorAll('img.leaflet-tile')];
    return layers.length===1 && !layers[0].isLoading() && images.length>0 &&
        images.every(image=>image.complete && image.naturalWidth===256 && image.naturalHeight===256);
}'''

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
    {'label':'cholera-basic-1', 'notebook':'courses/cholera-1854-basic/NB01-Cholera-Case-Study-Folium-Map-Part-1.ipynb',
     'files':['resources/library.py','resources/style.css','resources/cholera_deaths.csv','resources/pumps.csv'],
     'assertions':CHOLERA_ASSERTIONS, 'interactive_cells':True,
     'absent':['outputs/deaths_df.pickle','outputs/pumps_df.pickle'],
     'maps':[{'red':0,'blue':0},{'red':0,'blue':0},{'red':0,'blue':0},
             {'red':250,'blue':0},{'red':250,'blue':8},{'red':250,'blue':8}]},
    {'label':'cholera-basic-2', 'notebook':'courses/cholera-1854-basic/NB02-Cholera-Case-Study-Folium-Map-Part-2.ipynb',
     'files':['resources/library.py','resources/style.css','resources/cholera_deaths.csv','resources/pumps.csv'],
     'assertions':CHOLERA_ASSERTIONS+CHOLERA_MEAN_ASSERTIONS, 'interactive_cells':True,
     'absent':['outputs/deaths_df.pickle','outputs/pumps_df.pickle','outputs/mean_center_df.pickle'],
     'maps':[{'red':250,'blue':8},{'red':250,'blue':8,'yellowgreen':1}]},
    {'label':'gis-workbench', 'notebook':'gis-workbench.ipynb',
     'files':['atlas_gis_handoff.py','assets/browser-gis-pathways.json','courses/onehealth/data/tracts.geojson','courses/onehealth/data/manifest.json'],
     'absent':['exports/fresno-2020-first12.geojson','exports/pyodide-changed.geojson'],
     'download_links':['exports/'+stem+suffix for stem in ['fresno-2020-first12','pyodide-changed']
                       for suffix in ['.geojson','.metadata.json','.review.md']],
     'rerun_edits':{'minimum_value = 0':'minimum_value = 5000', 'selection_limit = 12':'selection_limit = 2', "output_stem = 'fresno-2020-first12'":"output_stem = 'pyodide-changed'"},
     'assertions': '''
assert input_summary['feature_count'] == 166
assert input_summary['measurements']['POP100']['numeric_sum'] == 764468
_default = json.loads(Path('exports/fresno-2020-first12.metadata.json').read_text())
assert _default['selection']['output_count'] == 12
assert package['method']['selection']['output_count'] == 2
assert package['method']['selection']['input_count'] == 166
assert package['method']['selection']['selected_ids'] == ['06019000400', '06019000902']
_written = json.loads(Path('exports/pyodide-changed.geojson').read_text())
assert len(_written['features']) == 2
assert [(f['properties']['_atlas_source_id'], f['properties']['POP100']) for f in _written['features']] == [('06019000400', 5384), ('06019000902', 5263)]
assert package['method']['selection_parameters']['minimum_value'] == 5000
assert all(f['properties']['_atlas_source_id'] == str(f['id']) == f['properties']['GEOID'] for f in _written['features'])
assert package['method']['source_id_property']['name'] == '_atlas_source_id'
assert hashlib.sha256(Path('exports/pyodide-changed.geojson').read_bytes()).hexdigest() == package['method']['geojson_sha256']
assert package['method']['sources'][0]['attribution'].startswith('U.S. Census Bureau')
assert package['method']['sources'][0]['license_evidence'] == manifest['rights']['census']
assert 'POP100' in package['review'] and 'Generated review instructions' in package['review']
assert package['method']['geojson_sha256'] != _default['geojson_sha256']
'''},
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


def assert_cholera_row_correspondence(actual,deaths,pumps):
    """Compare transient rendered rows with CSV rows; retain only a summary."""
    for kind,rows in [('mortality',deaths),('pumps',pumps)]:
        observed=actual[kind]
        assert len(observed)==len(rows), f'{kind}: row count differs'
        for index,(marker,row) in enumerate(zip(observed,rows)):
            location=[float(row['LAT']),float(row['LON'])]
            assert len(marker['location'])==len(marker['popup_location'])==2, (kind,index)
            assert all(isinstance(a,(int,float)) and abs(a-b)<1e-12 for a,b in zip(marker['location'],location)), (kind,index,'marker coordinates')
            assert all(isinstance(a,(int,float)) and abs(a-b)<1e-12 for a,b in zip(marker['popup_location'],location)), (kind,index,'popup coordinates')
            if kind=='mortality':
                assert marker['deaths']==int(row['DEATHS']) and marker['radius']==int(row['DEATHS']), (kind,index,'deaths/radius')
                assert isinstance(marker['radius'],(int,float)), (kind,index,'nonnumeric radius')
            else:assert marker['street']==row['Street'], (kind,index,'street')
    return {'status':'passed','mortality_rows':len(deaths),'pump_rows':len(pumps),
            'csv_rows_sha256':hashlib.sha256(json.dumps({'deaths':deaths,'pumps':pumps},sort_keys=True).encode()).hexdigest()}


def inspect_cholera_maps(page,cell,expected,output,label,timeout,deaths,pumps):
    """Inspect actual loaded Leaflet instances, rather than saved iframe HTML."""
    frames=cell.locator('.jp-OutputArea-output iframe')
    assert frames.count()==len(expected), f'{label}: missing per-cell map displays: {frames.count()}'
    results=[]
    for index,counts in enumerate(expected):
        element=frames.nth(index);element.scroll_into_view_if_needed()
        frame=element.element_handle().content_frame()
        assert frame, 'Folium iframe is missing'
        frame.wait_for_function("typeof L !== 'undefined' && [...document.querySelectorAll('.folium-map')].some(e=>window[e.id] instanceof L.Map)",timeout=timeout*1000)
        # Browser tile requests are fulfilled with an original schematic image;
        # this proves loading/rendering without bulk requests to OSM servers.
        frame.wait_for_function(CHOLERA_TILES_READY,timeout=30000)
        evidence=frame.evaluate(r'''() => {
            const map=window[document.querySelector('.folium-map').id];
            const layers=Object.values(map._layers), tiles=layers.filter(v=>v instanceof L.TileLayer);
            const counts=Object.fromEntries(['red','blue','yellowgreen'].map(color=>[color,layers.filter(v=>v.options?.fillColor===color && v instanceof L.Path).length]));
            const paintColors=Object.fromEntries(['red','blue','yellowgreen'].map(color=>[color,[...new Set(layers.filter(v=>v.options?.fillColor===color && v instanceof L.Path).flatMap(v=>{
                const fill=v._path.getAttribute('fill'), gradient=fill.match(/^url\(#([^)]*)\)$/);
                return gradient ? [...document.getElementById(gradient[1]).querySelectorAll('stop')].map(stop=>getComputedStyle(stop).stopColor) : [getComputedStyle(v._path).fill];
            }))]]));
            const panes=['tile','overlay','marker'].map(name=>[name,getComputedStyle(map.getPane(name+'Pane')).filter]);
            const rows=color=>layers.filter(v=>v.options?.fillColor===color && v instanceof L.Path).map(layer=>{
                const text=layer.getPopup().getContent().textContent.replace(/\s+/g,' ').trim();
                const coordinate=text.match(/Location: *\(([-+0-9.eE]+), *([-+0-9.eE]+)\)/);
                const location=L.latLng(layer.getLatLng());
                return {location:[location.lat,location.lng],
                    popup_location:coordinate ? coordinate.slice(1).map(Number) : [],
                    ...(color==='red' ? {radius:layer.getRadius(),deaths:Number(text.match(/Deaths: *(\d+)/)?.[1])} : {street:text.match(/Street Name: *(.*)$/)?.[1]})};
            });
            return {layers:tiles.map(v=>v._url),counts,paint_colors:paintColors,panes:Object.fromEntries(panes),
                tile_count:map.getPane('tilePane').querySelectorAll('img.leaflet-tile').length,
                all_attached_tiles_verified:true,
                attribution:document.querySelector('.leaflet-control-attribution').innerText,
                center:[map.getCenter().lat,map.getCenter().lng],zoom:map.getZoom(),
                row_data:{mortality:rows('red'),pumps:rows('blue')},
                mean:layers.filter(v=>v.options?.fillColor==='yellowgreen').map(v=>[v.getLatLng().lat,v.getLatLng().lng])};
        }''')
        assert evidence['layers']==['https://tile.openstreetmap.org/{z}/{x}/{y}.png'], evidence
        assert evidence['counts']=={color:counts.get(color,0) for color in ('red','blue','yellowgreen')}, evidence
        for color,rgb in [('red','rgb(255, 0, 0)'),('blue','rgb(0, 0, 255)'),('yellowgreen','rgb(154, 205, 50)')]:
            if counts.get(color):assert rgb in evidence['paint_colors'][color], evidence
        evidence['row_correspondence']=assert_cholera_row_correspondence(evidence.pop('row_data'),deaths if counts.get('red') else [],pumps if counts.get('blue') else [])
        assert 'OpenStreetMap' in evidence['attribution'] and frame.locator('.leaflet-control-attribution').is_visible()
        assert frame.locator('.leaflet-control-attribution a[href="https://www.openstreetmap.org/copyright"]').count()==1
        assert 'grayscale(1)' in evidence['panes']['tile'] and 'brightness(1.12)' in evidence['panes']['tile'] and 'contrast(0.82)' in evidence['panes']['tile']
        assert evidence['panes']['overlay']==evidence['panes']['marker']=='none', evidence
        assert abs(evidence['center'][0]-51.513578)<1e-10 and abs(evidence['center'][1]-(-0.136722))<1e-10 and evidence['zoom']==17, evidence
        for color in ('red','blue'):
            if not counts.get(color):continue
            # RegularPolygonMarker paints through an SVG gradient, so select
            # the path attached to the Leaflet layer rather than fill="blue".
            marker=frame.evaluate_handle('''color=>Object.values(window[document.querySelector('.folium-map').id]._layers).find(v=>v.options?.fillColor===color && v instanceof L.Path)?._path''',color).as_element()
            assert marker and marker.is_visible(), f'{label}: {color} markers are not rendered'
            marker.dispatch_event('click')
            popup=frame.locator('.leaflet-popup-content').last
            popup.wait_for(state='visible')
            assert ('Deaths:' if color=='red' else 'Street Name:') in popup.inner_text()
            frame.locator('.leaflet-popup-close-button').last.click()
            popup.wait_for(state='detached')
        if counts.get('yellowgreen'):
            lat,lon=evidence['mean'][0]
            assert abs(lat-51.51339831083845)<1e-12 and abs(lon-(-0.1364029734151329))<1e-12
            frame.locator('.leaflet-overlay-pane path[fill="yellowgreen"]').dispatch_event('click')
            popup=frame.locator('.leaflet-popup-content').last
            assert 'Mean Center Point:' in popup.inner_text()
            frame.locator('.leaflet-popup-close-button').last.click()
            popup.wait_for(state='detached')
        frame.locator('.leaflet-control-zoom-in').click()
        frame.wait_for_function("(()=>{const m=window[document.querySelector('.folium-map').id];return m.getZoom()===18&&!m._animatingZoom;})()")
        frame.locator('.leaflet-control-zoom-out').click()
        frame.wait_for_function("(()=>{const m=window[document.querySelector('.folium-map').id];return m.getZoom()===17&&!m._animatingZoom;})()")
        frame.wait_for_function(CHOLERA_TILES_READY,timeout=30000)
        if index==len(expected)-1:
            frame.locator('.folium-map').screenshot(path=str(output/f'map-{label}.png'))
        results.append(evidence)
    return results


def execute_case(browser, base, output, timeout, case):
    from check_runtime import select_python
    notebook_path=case['notebook'];canonical=ROOT/'content'/notebook_path
    nb=nbformat.read(canonical,as_version=4)
    skipped=[nb.cells[i].id for i in reviewed_widget_indices(notebook_path,nb,browser=True)] if case.get('skip_widgets') else []
    code='\n\n'.join(c.source for c in nb.cells if c.cell_type=='code' and c.id not in skipped)
    if case.get('skip_widgets'):assert len(skipped)==1, 'Expected one explicit optional widget-only cell'
    asset_hashes={name:hashlib.sha256((canonical.parent/name).read_bytes()).hexdigest() for name in case['files']}
    context=browser.new_context(viewport={'width':1440,'height':1000})
    diagnostics=attach_diagnostics(context)
    tile_requests=[]
    if case.get('maps'):
        def fulfill_tile(route):
            tile_requests.append(route.request.url)
            route.fulfill(status=200,content_type='image/svg+xml',body=CHOLERA_TILE_SVG,headers={'Access-Control-Allow-Origin':'*'})
        context.route('https://tile.openstreetmap.org/**',fulfill_tile)
        # Block accidental reintroduction of the retired/credential-dependent providers.
        context.route('**/*',lambda route:route.abort() if any(name in route.request.url for name in ('cartocdn','cartodb','stamen')) else route.fallback())
    page=context.new_page();errors=[];page.on('pageerror',lambda error:errors.append(sanitized_text(error)))
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
    rerun=''
    if case.get('rerun_edits'):
        changed=code
        for original,replacement in case['rerun_edits'].items():
            assert changed.count(original)==1, 'Expected exactly one canonical parameter to edit'
            changed=changed.replace(original,replacement)
        rerun='\n\n'+changed
    export_proof=(f"\n_atlas_export_paths = {case.get('download_links',[])!r}\n"
                  "_atlas_export_bytes = {name:{'sha256':hashlib.sha256(Path(name).read_bytes()).hexdigest(),'bytes':len(Path(name).read_bytes())} for name in _atlas_export_paths}\n")
    proof=rerun+"\n"+case['assertions']+export_proof+f"\nprint({marker!r}, json.dumps({{'platform':sys.platform,'asset_sha256':_atlas_actual_assets,'exports':_atlas_export_bytes,'assertions':'passed','package_preparation':globals().get('_atlas_browser_package_status')}}))\n"
    execution=code
    if case.get('expected_error'):
        import textwrap
        execution=('try:\n'+textwrap.indent(code,'    ')+
            '\nexcept ValueError as _atlas_error:\n    _atlas_expected_error = str(_atlas_error)\n'+
            f'    assert {case["expected_error"]!r} in _atlas_expected_error\n'+
            'else:\n    raise AssertionError("Invalid uploaded pair was accepted")\n')
    if case.get('interactive_cells'):
        cells=[c.source for c in nb.cells if c.cell_type=='code']
        execution=(f'_atlas_canonical_cells = {cells!r}\n'
                   'for _atlas_cell_number, _atlas_cell in enumerate(_atlas_canonical_cells):\n'
                   '    _atlas_result = await get_ipython().run_cell_async(_atlas_cell, store_history=False)\n'
                   '    if not _atlas_result.success:\n'
                   '        _atlas_cell_error = _atlas_result.error_before_exec or _atlas_result.error_in_exec\n'
                   '        raise RuntimeError("Canonical cell failed: "+str(_atlas_cell_number)+": "+str(_atlas_cell_error)) from _atlas_cell_error\n')
    source=prelude+case.get('setup','')+'\n\n'+execution+proof
    error_marker='ATLAS_SOURCE_PYODIDE_ERROR_'+uuid.uuid4().hex
    source=guarded_execution(source,error_marker)
    try:
        notebook_response=page.request.get(base+'lite/files/'+quote(notebook_path,safe='/'))
        assert notebook_response.ok and hashlib.sha256(notebook_response.body()).hexdigest()==hashlib.sha256(canonical.read_bytes()).hexdigest(), 'Packaged canonical notebook bytes differ: '+notebook_path
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
        executed_cell=editor.locator("xpath=ancestor::div[contains(@class, 'jp-CodeCell')][1]")
        page.keyboard.press('ControlOrMeta+Enter')
        state=page.wait_for_function(EXECUTION_STATE_JS,arg={'cell':executed_cell.element_handle(),'marker':marker,'errorMarker':error_marker},timeout=timeout*1000).json_value()
        if state['status']=='error':
            diagnostics['python_error']={'text':sanitized_text(state['text']),'mime':state.get('mime')}
            raise RuntimeError('Fresh source execution failed: '+sanitized_text(state['text']))
        proof_output=page.locator('.jp-Notebook .jp-OutputArea-output').filter(has_text=marker)
        proof_output.wait_for(state='attached',timeout=timeout*1000);proof_output.scroll_into_view_if_needed()
        text=proof_output.inner_text();line=next(line for line in text.splitlines() if line.startswith(marker+' '))
        evidence=json.loads(line[len(marker)+1:])
        assert evidence['platform']=='emscripten' and evidence['assertions']=='passed'
        assert set(evidence['asset_sha256'])==set(filesystem_hashes)
        assert all(value in filesystem_hashes[name] for name,value in evidence['asset_sha256'].items())
        cell=proof_output.locator("xpath=ancestor::div[contains(@class, 'jp-CodeCell')][1]")
        assert not cell.locator('.jp-OutputArea .jp-mod-error').count(), f'Source {case["label"]} returned an error'
        for href in case.get('download_links',[]):
            download=cell.get_by_role('link',name=href,exact=True)
            assert download.count()>=1 and download.first.get_attribute('href') not in (None,'','#'), 'Missing freshly rendered Lab FileLink: '+href
        downloads=[]
        if case.get('download_links'):
            # Exercise actual browser download from Lab's live file browser;
            # rendered FileLinks alone cannot prove generated bytes are retrievable.
            files=page.get_by_role('tab',name='File Browser')
            if files.get_attribute('aria-selected')!='true':files.click()
            page.get_by_title('Refresh the file browser.',exact=True).click()
            page.locator('.jp-DirListing-itemText').filter(has_text='exports').dblclick()
            for relative,expected in evidence['exports'].items():
                filename=Path(relative).name
                item=page.locator('.jp-DirListing-item').filter(has=page.get_by_text(filename,exact=True))
                item.click(button='right')
                with page.expect_download(timeout=30000) as received:
                    page.get_by_role('menuitem',name='Download',exact=True).click()
                download=received.value
                destination=output/('download-'+filename);download.save_as(destination)
                data=destination.read_bytes();actual={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
                assert actual==expected, f'Lab download bytes differ from fresh kernel: {relative}'
                downloads.append({'path':relative,'suggested_filename':download.suggested_filename,**actual})
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
        deaths=[];pumps=[]
        if case.get('maps'):
            import csv
            with (canonical.parent/'resources/cholera_deaths.csv').open(encoding='utf-8') as data:
                deaths=list(csv.DictReader(data))
            with (canonical.parent/'resources/pumps.csv').open(encoding='utf-8') as data:
                pumps=list(csv.DictReader(data))
        maps=inspect_cholera_maps(page,cell,case['maps'],output,case['label'],timeout,deaths,pumps) if case.get('maps') else []
        plotly=[];plotly_downloads=[]
        if case.get('plotly'):
            # A MIME bundle or emitted HTML is not rendered Plotly evidence.
            # Inspect actual loaded graphs, including sandboxed HTML frames.
            def fresh_graphs():
                found=cell.locator('.js-plotly-plot')
                result=[(found.nth(i),[]) for i in range(found.count())]
                frames=[]
                for iframe in cell.locator('iframe').all():
                    owner=iframe.element_handle();frame=owner.content_frame()
                    if frame:frames.append((frame,[owner]))
                while frames:
                    frame,owners=frames.pop()
                    frames.extend((child,owners+[child.frame_element()]) for child in frame.child_frames)
                    found=frame.locator('.js-plotly-plot')
                    result.extend((found.nth(i),owners) for i in range(found.count()))
                return result
            deadline=time.monotonic()+60;graphs=[]
            while time.monotonic()<deadline:
                graphs=fresh_graphs()
                if len(graphs)>=case['plotly']:break
                page.wait_for_timeout(200)
            assert len(graphs)>=case['plotly'], 'Missing actual Plotly rendering; emitted MIME/HTML alone cannot pass'
            for i,(graph,owners) in enumerate(graphs):
                # The notebook output has its own scroll pane. Reveal each
                # owning frame from the outside in before acting inside it.
                for owner in owners:owner.scroll_into_view_if_needed()
                graph.scroll_into_view_if_needed()
                graph.evaluate('graph=>Promise.resolve(graph._promises?.length ? Promise.all(graph._promises) : null)')
                observed=graph.evaluate('''graph=>({types:(graph._fullData||[]).map(t=>t.type),
                    title:graph._fullLayout?.title?.text,
                    canvases:[...graph.querySelectorAll('canvas')].map(c=>({width:c.width,height:c.height})),
                    svg_paths:graph.querySelectorAll('svg path').length,
                    trace_lengths:(graph._fullData||[]).map(t=>({x:t.x?.length,y:t.y?.length,z:t.z?.length})),
                    camera:graph._fullLayout?.scene?.camera})''')
                assert observed['types'] and observed['title'], 'Plotly layout/data failed to load'
                if case.get('climate'):
                    traces=graph.evaluate('''graph=>{
                        const plain=v=>Array.isArray(v)||ArrayBuffer.isView(v) ? Array.from(v,plain) :
                            (typeof v==='number'&&!Number.isFinite(v) ? null : v);
                        return (graph._fullData||[]).map(t=>({
                            type:t.type,visible:t.visible,x:plain(t.x),y:plain(t.y),z:plain(t.z),surfacecolor:plain(t.surfacecolor)}));
                    }''')
                    kind='globe' if 'surface' in observed['types'] else case['climate']
                    observed['climate_oracle']=assert_climate_plot(traces,kind)
                    if kind!='globe':
                        heatmap=graph.locator('.heatmaplayer .hm image')
                        assert heatmap.count()==1 and heatmap.is_visible(),'Expected the actual rendered climate heatmap image'
                        observed['climate_image']=heatmap.evaluate('image=>({width:image.getBoundingClientRect().width,height:image.getBoundingClientRect().height,opacity:getComputedStyle(image).opacity})')
                        assert observed['climate_image']['width']>0 and observed['climate_image']['height']>0 and float(observed['climate_image']['opacity'])>0
                if 'surface' in observed['types']:
                    assert any(c['width']>=200 and c['height']>=100 for c in observed['canvases']), 'Globe needs a rendered WebGL canvas'
                    before=observed['camera']
                    # Explicit screen coordinates keep the real drag tied to
                    # this graph's visible canvas rather than its modebar.
                    box=graph.bounding_box()
                    page.mouse.move(box['x']+box['width']*.5,box['y']+box['height']*.5)
                    page.mouse.down();page.mouse.move(box['x']+box['width']*.6,box['y']+box['height']*.55,steps=8);page.mouse.up()
                    page.wait_for_timeout(300)
                    after=graph.evaluate('graph=>graph._fullLayout.scene.camera')
                    assert after!=before, 'Globe camera must respond to an actual drag'
                    observed['camera_changed']=True
                else:assert observed['svg_paths']>5,'2D Plotly graph needs rendered paths'
                if case.get('plotly_download'):
                    graph.hover()
                    button=graph.locator('.modebar-btn[data-title*="Download plot"]')
                    assert button.count()==1,'Expected Plotly user image-export control'
                    with page.expect_download(timeout=30000) as received:button.click()
                    download=received.value;destination=output/f'plotly-download-{case["label"]}-{i}.png'
                    download.save_as(destination);data=destination.read_bytes()
                    assert data[:8]==b'\x89PNG\r\n\x1a\n','Plotly export must be an actual PNG download'
                    import struct
                    width,height=struct.unpack('>II',data[16:24]);assert width>=200 and height>=100
                    plotly_downloads.append({'filename':download.suggested_filename,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'width':width,'height':height})
                graph.screenshot(path=str(output/f'plotly-{case["label"]}-{i}.png'))
                plotly.append(observed)
        if maps:assert tile_requests, 'No controlled tile responses were exercised'
        assert not errors,errors
        page.screenshot(path=str(output/f'executed-{case["label"]}.png'))
        result={'status':'passed','notebook':notebook_path,'marker':marker,'proof':evidence,'pngs':images,'downloads':downloads,'maps':maps,'plotly':plotly,'plotly_downloads':plotly_downloads,'skipped_optional_widget_cell_ids':skipped,
                'raw_http_asset_sha256':asset_hashes,'allowed_filesystem_sha256':filesystem_hashes,
                'filesystem_text_transport':'Jupyter Contents universal newlines; JSON text or precisely computed JavaScript JSON.stringify model; UTF-8',
                'canonical_sha256':hashlib.sha256(canonical.read_bytes()).hexdigest(),
                'canonical_code_sha256':hashlib.sha256(code.encode()).hexdigest(),'numerical_assertions':case['assertions'],
                'cell_execution':'IPython sequential run_cell_async; canonical bare expressions display' if case.get('interactive_cells') else 'Concatenated canonical code',
                'tile_verification':{'requests':len(tile_requests),'method':'Intercepted OSM URLs; original schematic test tiles; no requests reach the provider. Verifies iframe rendering, layers, colored markers, popups and zoom, not live OSM availability.'} if maps else None}
        print(f'PASS fresh source Pyodide {case["label"]}: notebook-relative assets, numerical/export assertions, unique marker, {len(images)} PNGs, {len(maps)} loaded map iframes',flush=True)
        return result
    except Exception:
        (output/f'failure-{case["label"]}-body.txt').write_text(page.locator('body').inner_text(),encoding='utf-8')
        page.screenshot(path=str(output/f'failure-{case["label"]}.png'))
        raise
    finally:
        (output/f'diagnostics-{case["label"]}.json').write_text(json.dumps(diagnostics,indent=2)+'\n',encoding='utf-8')
        context.close()


def main():
    from playwright.sync_api import sync_playwright
    parser=argparse.ArgumentParser()
    parser.add_argument('--browser-executable')
    parser.add_argument('--timeout',type=int,default=360,help='Per-case runtime/package startup and execution timeout in seconds')
    parser.add_argument('--case',choices=[c['label'] for c in CASES],action='append',help='Debug a subset; CI runs all declared cases')
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
            'method':'Separate fresh browser context and actual Pyodide kernel per case; canonical code runs against hash-checked packaged notebook-relative files, plus oracle/numerical/export assertions and unique executed markers. Basic map cases use sequential IPython cell semantics, inspect loaded Leaflet iframes, layers, numeric radii, colors, center, popups and zoom, and intercept OSM requests with original schematic test tiles. Other cases also check loaded PNGs where relevant.',
            'limits':'These explicitly selected source notebooks and the authored GIS workbench only. Initial runtime/package retrieval and Folium JavaScript/CSS require network access. Controlled map tiles establish iframe rendering, not live OSM availability or an offline map. No native, credential or live acquisition branch is certified by this browser gate. The existing seven-case SVG runtime gate remains separate.'},indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
