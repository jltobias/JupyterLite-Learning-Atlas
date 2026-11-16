"""Explicit, deterministic import of inspected pins. Never run/fetch upstream code.

Run only to intentionally rebuild source snapshots. Routine generation preserves them.
All inspected notebook paths have an imported/alias/excluded disposition; support
files have hashes and rights exclusions have exact paths and source continuations.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

import nbformat

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / '_research/textbook-sources'
DEST = ROOT / 'content'

# Prefix mappings reproduce the *tracked* preparation layout documented by the
# investigation. No upstream generator, deserializer or acquisition code runs.
MAPS = {
 'c3s-atlas': [('content/', '')],
 'destination-earth-digital-twin': [('content/', ''), ('book/', 'book/'), ('assets/splash.png', 'assets/splash.png')],
 'urbanity': [('book/', '')],
 'terrio': [('notebooks/', ''), ('book/', 'book/')],
 'ai-agents-and-orchestrator-six-thinking-hats': [('notebooks/', '')],
 'astra-demos': [('content/notebooks/', '')],
 'cholera-1854-basic': [('', '')],
 'cholera-1854-advanced-1': [('content/', '')],
 'cholera-1854-advanced-2': [('', '')],
 'climate-and-health': [('content/', '')],
 'coral-reef-one-health': [('content/', '')],
 'cross-border-ebola-risk-mapping-prototype': [('notebooks_lite/', ''), ('notebooks/', 'native/notebooks/'), ('src/', 'native/src/'), ('configs/', 'native/configs/')],
 'custom-gpt-six-thinking-hats': [('book/notebooks/', '')],
 'data-visualization': [('content/', '')],
 'drc-population-mobility-border-mapping': [('contents/', 'contents/'), ('maps/', 'maps/')],
 'eo-satellite-guide': [('notebooks/', '')],
 'geolibre-geoai': [('book/notebooks/', '')],
 'geospatial-analyses-and-maps': [('notebooks/', 'notebooks/'), ('data/', 'data/'), ('shapefiles/', 'shapefiles/'), ('geopackages/', 'geopackages/'), ('images/', 'images/'), ('videos/', 'videos/')],
 'geospatial-analyses-and-maps-old': [('notebooks/', ''), ('data/', 'data/')],
 'geospatial-analyses-and-maps-revised': [('content/', '')],
 'geospatial-research-awareness-radar': [('', '')],
 'global-fishing-watch-and-dark-vessels': [('content/', '')],
 'global-health-gis': [('content/', '')],
 'global-informal-settlements-storymap': [('content/', '')],
 'gods-eye-view-satellite': [('book/notebooks/', '')],
 'gpt-6-astra-geospatial': [('content/', '')],
 'hivdb-drug-resistance-maps': [('content/', '')],
 'jupytergis-storymap-gaborone-tb-abm': [('content/', '')],
 'maps-and-spatial-analyses': [('notebooks/', ''), ('content/', '')],
 'mdr-tb-thailand-2005': [('', '')],
 'nasa-arset-experiments': [],
 'onehealth': [('content/', '')],
 'osiris': [('content/', '')],
 'population-data-comparison': [('notebooks/', '')],
 'pyscript': [('content/', ''), ('site/apps/shared/', 'source/'), ('site/apps/', 'source/apps/')],
 'rewiring-global-health': [('notebooks/', '')],
 'rustgis': [('lite/', ''), ('notebooks/', 'native/'), ('data/', 'native/data/')],
 'sea-level-rise': [('content/', '')],
 'shiny-live-apps': [],
 'south-sudan-dashboard': [('data/', 'data/'), ('SouthSudanDashboard_JupyterLite.ipynb', 'SouthSudanDashboard_JupyterLite.ipynb')],
 'spatial-analysis': [('notebooks/', ''), ('content/', '')],
 'stac-browser': [('notebooks/', '')],
 'whitebox': [('content/', '')],
 'world-monitor-prototype': [('content/', '')],
 'worldview': [('content/', '')],
 'zarr-sql-views': [('notebooks/', '')],
}
EXTRA = {
 'c3s-atlas': [('assets/PROVENANCE.md', 'notices/assets/PROVENANCE.md'), ('CITATION.cff', 'notices/CITATION.cff'), ('curriculum.json', 'curriculum.json'), ('requirements-data.txt', 'notices/requirements-data.txt')],
 'destination-earth-digital-twin': [('assets/GENERATION.md', 'notices/assets/GENERATION.md'), ('CITATION.cff', 'notices/CITATION.cff'), ('assets/splash.png', 'assets/splash.png')],
 'urbanity': [('book/_static/'+name, '_static/'+name) for name in ['urbanity-mark.svg', 'urbanity-pipeline.svg', 'urbanity-splash.svg']],
 'terrio': [('chapters.json', 'chapters.json'), ('assets/ARTWORK.md', 'notices/assets/ARTWORK.md'), ('CITATION.cff', 'notices/CITATION.cff')],
 'eo-satellite-guide': [('src/eo_guide.py','eo_guide.py'), *[(f'data/{p}',f'data/{p}') for p in ['catalog.json','research-topics.json','stac-coverage.json','research-ontology.ttl','orbit-types.json','geometry-presets.json','mission-registry.json','mission-coverage.json']], ('downloads/eo-explorer.html','support/eo-explorer.html'), ('downloads/eo-swaths.html','support/eo-swaths.html')],
 'population-data-comparison': [('notebooks/population_tools.py','population_tools_real.py'), *[(f'data/{p}',p) for p in ['demo.json','population.json','README.md','import-example.geojson']], ('data/real/independent_oracle.json','independent_oracle.json'), ('data/real/ghsl_copyright.txt','notices/ghsl_copyright.txt'), ('data/real/comparison_source_provenance.json','notices/comparison_source_provenance.json')],
 'geospatial-analyses-and-maps': [('spatial_lite.py','spatial_lite.py')],
 'geospatial-analyses-and-maps-old': [('spatial_lite.py','spatial_lite.py'),('spatial_lite.py','notebooks_spatial_lite_copy.py')],
 'global-fishing-watch-and-dark-vessels': [('content/oceanlab.py','oceanlab.py')],
 'geospatial-research-awareness-radar': [],
 'stac-browser': [('web/public-catalogs.json','public-catalogs.json')],
 'rustgis': [('lite/viz.py','native/viz.py'),('lite/stac_browser.py','native/stac_browser.py')],
 'pyscript': [('content/selection.py','source/selection.py'),('content/chart_data.py','source/chart_data.py'),
              ('content/selection.py','source/apps/shared/selection.py'),('content/chart_data.py','source/apps/shared/chart_data.py'),
              *[(f'site/apps/shared/{name}',f'source/apps/shared/{name}') for name in ['lab.py','lab.js','pyscript.json','charts.py','charts.js','charts.json','charts.css']]],
 'global-health-gis': [('content/data/gbd_country_points_2021_global.geojson',f'data/{name}') for name in ['gbd_country_points_2021.geojson','gbd_country_points_generated.geojson']],
 'zarr-sql-views': [('public/vendor/lexcube/lexcube-2.0.1.tar.gz','wheels/lexcube-2.0.1.tar.gz')],
}
PHI = {'cholera-1854-basic','cholera-1854-advanced-1','cholera-1854-advanced-2','mdr-tb-thailand-2005'}
MEDIA = {'.png','.jpg','.jpeg','.gif','.webp','.mp4','.wav','.mp3','.pdf','.ogg','.ico'}
SAFE_EXT = {'.py','.json','.geojson','.csv','.tsv','.txt','.md','.css','.html','.js','.mjs','.svg','.shp','.shx','.dbf','.prj','.cpg','.gpkg','.xlsx','.xls','.graphml','.xml','.yaml','.yml','.jgis','.jGIS','.npz','.npy','.zip','.whl','.ttl','.vtt','.srt','.wasm','.tif','.tiff','.feather','.bib','.cff'} | MEDIA
# Deliberately independent of the older research audit: append never replays a
# previous course and refuses an unexpected checkout, inventory or destination.
APPEND_COURSES = {
 'c3s-atlas': ('JupyterLite-C3S-Atlas', 'b41c3e1098a4fb94cef48b3044fe19c6ce7c1a1a', 20),
 'destination-earth-digital-twin': ('JupyterLite-Destination-Earth-Digital-Twin', '0e32b2477ba5c0030985e25f1071d94cddabf130', 32),
 'urbanity': ('JupyterLite-Urbanity', 'a9d2b1e0d0af91dc2782f7f1d77d9bbb10c67d0f', 7),
 'terrio': ('JupyterLite-terrio', '18574d4e7a8dabb99d3db65b20c6180185578482', 13),
}
URBANITY_ORDER=('street-networks','urban-graphs','urban-context','imagery','visualisation','graph-ml','reproducibility')


def ordered_notebooks(slug,notebooks):
    def path(item):return item['path'] if isinstance(item,dict) else item
    if slug=='urbanity':return sorted(notebooks,key=lambda item:URBANITY_ORDER.index(PurePosixPath(path(item)).stem))
    return sorted(notebooks,key=lambda item:(path(item).startswith('notebooks/') if slug=='rustgis' else path(item).startswith('contents/'),path(item)))


def collect_support(support,local,slug,path,checkout):
    """Reject a destination conflict before a dict assignment can hide it."""
    candidate=(slug,path);previous=support.get(local)
    if previous is not None and previous!=candidate:
        relative=local.removeprefix(f'courses/{slug}/')
        cleared=slug=='destination-earth-digital-twin' and relative=='assets/splash.png' and previous[0]==slug and {previous[1],path}=={'assets/splash.png','content/assets/splash.png'}
        if not cleared:raise ValueError('Conflicting support destination: '+local)
        left=(checkout/previous[1]).read_bytes();right=(checkout/path).read_bytes()
        if left!=right or digest(left)!='8572f03e5207a2be3189eed9e91b2bcf1224186c495b7907fe817b22681d82e3':
            raise ValueError('Conflicting support destination: '+local)
        candidate=(slug,'assets/splash.png')  # The demonstrated identical-byte source alias.
    support[local]=candidate
BASIC_NOTEBOOKS = {
    'NB01-Cholera-Case-Study-Folium-Map-Part-1.ipynb',
    'NB02-Cholera-Case-Study-Folium-Map-Part-2.ipynb',
}
BASIC_SETUP = '''# Prepare browser packages before importing the lesson dependencies.
import sys
if sys.platform == "emscripten":
    import piplite
    await piplite.install(["numpy", "pandas", "folium==0.20.0"])
# Native kernels use the Atlas pinned build requirements.
%run ./resources/library.py'''
C3S_REFERENCE_AUDIT='''import hashlib
_reference_pins = {
    "reference/CMIP6_WarmingLevels.csv": ("799390194c359224ee41d2a69156728b456b2f62b73ce229930fffcd84996220", 5095),
    "reference/ne_110m_coastline.geojson": ("851f581ff5ffb844deed8ae1a9ce22e3c4bb3d74fa342cadb5d8e39b41ae7c3c", 139907),
    "reference/atlas-catalogue.json": ("33e92f5a01a5aa77cfe6a782776bbc5bba027cb4761b5d25f1faa35a1138dd86", 5461),
}
def _verify_reference_bytes(item, raw, mounted):
    expected = _reference_pins.get(item["file"])
    if expected != (item["sha256"], item["bytes"]) or expected != (hashlib.sha256(raw).hexdigest(), len(raw)):
        raise ValueError("Authentic raw reference bytes or pinned manifest identity changed.")
    allowed = {raw}
    if sys.platform == "emscripten" and Path(item["file"]).suffix.lower() in {".json", ".geojson"}:
        from js import JSON
        allowed.add(str(JSON.stringify(JSON.parse(raw.decode("utf-8")))).encode("utf-8"))
    if mounted not in allowed:
        raise ValueError("Mounted reference differs from the exact authenticated transport representation.")
    return True

manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
assert len(manifest) == len(_reference_pins) and {item["file"] for item in manifest} == set(_reference_pins)
audit = []
_reference_http_hashes = {}
for item in manifest:
    mounted = (DATA / item["file"]).read_bytes()
    raw = mounted
    if sys.platform == "emscripten":
        from js import location
        from pyodide.http import pyfetch
        # Fetch only this Atlas deployment's bundled original bytes, never a provider dataset.
        response = await pyfetch(str(location.origin) + "/JupyterLite-Learning-Atlas/lite/files/courses/c3s-atlas/data/" + item["file"])
        if response.status != 200:
            raise ValueError("Bundled raw reference is unavailable.")
        raw = await response.bytes()
    # The verifier derives the sole JSON transport representation from authenticated raw bytes.
    verified = _verify_reference_bytes(item, raw, mounted)
    _reference_http_hashes[item["file"]] = hashlib.sha256(raw).hexdigest()
    audit.append({"file": item["file"], "bytes": item["bytes"], "licence": item["licence"], "verified": verified})
assert all(row["verified"] for row in audit), "A reference file changed. Review provenance."
display(pd.DataFrame(audit))'''
C3S_BROWSER_PACKAGES='''import importlib
import piplite
_atlas_browser_requirements = {"numpy": "numpy", "pandas": "pandas", "matplotlib": "matplotlib", "plotly": "plotly==6.5.0"}
_atlas_browser_package_status = {"retried": [], "verified": []}
await piplite.install(list(_atlas_browser_requirements.values()))

def _atlas_missing_browser_packages():
    importlib.invalidate_caches()
    missing = []
    for module in _atlas_browser_requirements:
        try:
            importlib.import_module(module)
        except ModuleNotFoundError as error:
            if error.name != module:
                raise RuntimeError(f"Browser package {module} has a missing dependency ({error.name}); preparation stopped without retrying an unrelated failure.") from error
            missing.append(module)
    return missing

_atlas_missing = _atlas_missing_browser_packages()
if _atlas_missing:
    _atlas_browser_package_status["retried"] = list(_atlas_missing)
    print("ATLAS_PACKAGE_RETRY", _atlas_missing, flush=True)
    # One bounded retrieval retry, only for directly confirmed missing modules.
    await piplite.install([_atlas_browser_requirements[module] for module in _atlas_missing])
    _atlas_missing = _atlas_missing_browser_packages()
if _atlas_missing:
    raise RuntimeError("Browser package preparation failed after one missing-module retry: " + ", ".join(_atlas_missing) + ". Check package/network diagnostics, then restart the kernel.")
_atlas_browser_package_status["verified"] = list(_atlas_browser_requirements)'''
C3S_SETUP_NOTEBOOKS=(
    '01-atlas-orientation','02-data-and-provenance','03-baselines-and-anomalies','04-seasons-and-stripes',
    '05-heat-and-cold','06-rain-and-water','07-drought','08-wind-and-radiation','09-snow-and-ice',
    '10-ocean-and-circulation','11-scenarios-and-ensembles','12-global-warming-levels','13-uncertainty-and-bias',
    '14-regions-and-weights','15-interactive-2d-maps','16-globes-and-3d-maps','17-3d-scenes',
    '18-monitoring-and-urban','19-bring-real-data','20-capstone')
BASIC_GRAY_MAP = '''# One keyless modern street layer; only its tile pane is desaturated.
def gray_street_map(location, zoom_start=17):
    street_map = folium.Map(location=location, zoom_start=zoom_start, tiles=None)
    folium.TileLayer(
        tiles="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        name="OpenStreetMap streets", max_zoom=19,
    ).add_to(street_map)
    street_map.get_root().header.add_child(folium.Element(
        "<style>.folium-map .leaflet-tile-pane {"
        "filter: grayscale(1) brightness(1.12) contrast(0.82);"
        "}</style>"
    ))
    return street_map'''


def digest(data): return hashlib.sha256(data).hexdigest()
def cell_digest(nb): return digest(json.dumps([(c.cell_type,c.source) for c in nb.cells],ensure_ascii=False).encode())
def write_json(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def adapt_support(slug,path,data):
    """Small recorded portability adapters; upstream checkouts remain immutable."""
    changes=[]
    if slug=='c3s-atlas' and path=='content/atlas_helpers.py':
        old='''    display({'application/vnd.plotly.v1+json': json.loads(fig.to_json()),
             'text/html': fig.to_html(full_html=False, include_plotlyjs='cdn'),
             'text/plain': str(fig)}, raw=True)'''
        new='''    # Atlas has only the Pyodide extension: isolate Plotly's loader and draw
    # scripts in an opaque-origin frame so the CDN is ready before newPlot.
    from html import escape
    document = fig.to_html(full_html=True, include_plotlyjs='cdn', config={'responsive': True})
    title = escape(fig.layout.title.text or 'Interactive teaching figure', quote=True)
    frame = (f'<iframe title="{title}" srcdoc="{escape(document, quote=True)}" '
             'sandbox="allow-scripts allow-downloads" style="width:100%;height:520px;border:0" loading="eager"></iframe>')
    display({'text/html': frame, 'text/plain': str(fig)}, raw=True)'''
        source=data.decode('utf-8')
        assert source.count(old)==1, 'C3S Plotly portability adapter source changed'
        source=source.replace(old,new)
        source=source.replace('The Lab MIME renderer is supplied by the Plotly extension. Static HTML uses',
            'Atlas uses an isolated sandboxed frame, without a Plotly Lab extension. HTML uses')
        data=source.encode('utf-8')
        changes.append({'kind':'portability','adapter':'c3s-plotly-frame-v1','reason':'Actual Atlas Pyodide probe found Plotly undefined in the unisolated HTML fallback. An opaque-origin sandbox=allow-scripts allow-downloads iframe loads the versioned Plotly CDN before drawing and permits user-initiated image export; no allow-same-origin, extra Lab extension or runtime downgrade. Original numerical code, data, notices and text/plain fallback are retained.'})
    if slug=='stac-browser' and path=='notebooks/stac_browser.py':
        old='return str(location.origin) + config["base_path"].rstrip("/") + "/explorer/"'
        new='return ("" if urlsplit(config["base_path"]).scheme else str(location.origin)) + config["base_path"].rstrip("/") + "/explorer/"'
        text=data.decode('utf-8');assert text.count(old)==1, 'STAC explorer adapter source changed'
        data=text.replace(old,new).encode('utf-8')
        changes.append({'kind':'portability','reason':'Absolute source continuation must not be prefixed by the Atlas worker origin','from':old,'to':new})
    return data,changes


def prepare_support(slug,path,local,raw,aliases,available):
    """One publication adapter shared by append and intentional full refresh."""
    data,changes=adapt_support(slug,path,raw)
    relative=local.removeprefix(f'courses/{slug}/')
    if relative!=mapped(slug,path) and relative.startswith('notices/source-documents/'):
        changes.append({'kind':'layout','from':mapped(slug,path),'to':relative,'reason':'Source Markdown relocated to avoid sharing a canonical notebook document stem.'})
    if slug in APPEND_COURSES and local.endswith('.md') and ('/notices/source-documents/' in local or ('/notices/' not in local and '/licenses/' not in local)):
        source=normalize_markdown(data.decode('utf-8'),path,slug,local,aliases,available,changes)
        if slug=='c3s-atlas' and path=='content/data-guide.md':
            old="Upload the prepared pair as `my_series.csv` and `my_series.json` into the Lab's\n   root file browser. Run Chapter 19."
            new="In the Atlas Lab, open `courses/c3s-atlas/` in the file browser and upload\n   `my_series.csv` and `my_series.json` beside `19-bring-real-data.ipynb`. The\n   original source Lab uses its root directory; these are different layouts. Run Chapter 19."
            assert source.count(old)==1,'C3S upload-guide source changed'
            source=source.replace(old,new)
            old='Install `requirements-data.txt` in your project environment, then run:'
            new=('The following commands belong to the pinned source project, not the Atlas tree.\n'
                 '[Download or check out the complete source at commit b41c3e1098a4fb94cef48b3044fe19c6ce7c1a1a]'
                 '(https://github.com/jltobias/JupyterLite-C3S-Atlas/tree/b41c3e1098a4fb94cef48b3044fe19c6ce7c1a1a), '
                 'then open a terminal in that source root. It supplies\n'
                 '`requirements-data.txt` and `scripts/prepare_netcdf.py`; the source script remains external\n'
                 'to the Atlas. In an isolated desktop environment, install those source requirements, then run:')
            assert source.count(old)==1,'C3S desktop-guide source changed'
            source=source.replace(old,new)
            changes.append({'kind':'layout','adapter':'c3s-upload-guide-v1','reason':'Name the Atlas course-local upload directory and the separate immutable source checkout required for external desktop preparation commands.'})
        if slug=='destination-earth-digital-twin' and '{cite:p}`climategen2`' in source:
            source=source.replace('{cite:p}`climategen2`','([ECMWF Generation 2 Climate DT dataset, DOI 10.21957/79c6af3105](https://doi.org/10.21957/79c6af3105); metadata context only, dataset not used)')
            source=re.sub(r'```\{bibliography\}.*?```','The retained [source BibTeX references](references.bib) provide the original citation metadata.',source,flags=re.S)
            changes.append({'kind':'citation','reason':'Rendered Book 2 citation and bibliography syntax as an explicit DOI and retained BibTeX link for the Book 1 host; dataset not used.'})
        data=source.encode('utf-8')
    return data,changes


def adapt_expansion_notebook(slug,path,nb):
    if slug!='c3s-atlas':return []
    changes=adapt_c3s_setup(path,nb)
    contracts={
        'content/02-data-and-provenance.ipynb':('65c79ef897a887aa36b86a243cf0906ea55ba50977025a7c22b989692bc22bc1','c3s-reference-transport-v1'),
        'content/19-bring-real-data.ipynb':('f7937e4e4fe85da5179a8f639b148cb8306db53b07da6f6b2be3913037ecbb89','c3s-upload-provenance-v1'),
    }
    if path not in contracts:return changes
    expected,adapter=contracts[path]
    cells=[c for c in nb.cells if c.cell_type=='code' and digest(c.source.encode())==expected]
    assert len(cells)==1,'Reviewed C3S source cell changed: '+path
    if adapter=='c3s-reference-transport-v1':
        cells[0].source=C3S_REFERENCE_AUDIT
        reason='Authenticate exact bundled raw bytes and pinned identities, then allow only raw bytes or the exact JavaScript JSON.stringify(JSON.parse(authenticated raw)) Jupyter Contents representation. No arbitrary object changes accepted.'
    else:
        cells[0].source=cells[0].source.replace('all(str(provenance[k]).strip() for k in required)','all(isinstance(provenance[k], str) and provenance[k].strip() for k in required)')
        reason='Required uploaded provenance values must be nonblank strings; reject null, nonstring and missing fields before plotting.'
    changes.append({'kind':'integrity','adapter':adapter,'reason':reason})
    return changes


def adapt_c3s_setup(path,nb):
    if path not in {f'content/{name}.ipynb' for name in C3S_SETUP_NOTEBOOKS}:return []
    cells=[c for c in nb.cells if c.cell_type=='code' and digest(c.source.encode())=='3cf02616e2775971774b493eaba1778ab0996660d1bfb9458b285815f2038d0f']
    assert len(cells)==1,'Reviewed C3S package setup cell changed: '+path
    old='    import piplite\n    await piplite.install(["numpy", "pandas", "matplotlib", "plotly==6.5.0"])'
    assert cells[0].source.count(old)==1
    cells[0].source=cells[0].source.replace(old,'\n'.join('    '+line if line else '' for line in C3S_BROWSER_PACKAGES.splitlines()))
    return [{'kind':'portability','adapter':'c3s-package-verification-v1','reason':'After awaited browser package preparation, verify actual module imports. Retry at most once and only directly missing requested modules, retain the retried list, and fail explicitly if still absent. Nested dependency/import/installer/calculation failures are not retried. Native branches and scientific calculations are unchanged.'}]


def adapt_basic_notebook(slug,path,nb):
    """Audited adapters for exactly the two full Basic source notebooks.

    Cell positions refer to immutable upstream cells, before Atlas provenance.
    Assertions make an upstream revision require a new, deliberate audit.
    """
    if slug!='cholera-1854-basic' or path not in BASIC_NOTEBOOKS:return []
    def replace(index,old,new):
        assert old in nb.cells[index].source, f'Basic adapter source changed: {path} cell {index}'
        nb.cells[index].source=nb.cells[index].source.replace(old,new)
    replace(1,'%run ./resources/library.py',BASIC_SETUP)
    nb.cells[0].source='Run all cells in order in a fresh Python (Pyodide) or native Python kernel. The first code cell prepares browser packages before imports; native dependencies come from the Atlas pinned build requirements. Maps require network access for OpenStreetMap tiles and Folium JavaScript/CSS. Tables and calculations use bundled historical CSVs.'
    first=path.startswith('NB01-')
    if first:
        nb.cells[5].source='In this notebook, we will learn about the approach that Dr. John Snow used when he investigated the London cholera outbreak in 1854. The optional video is an external continuation; it is not required to run this notebook.'
        for index in (6,7):
            nb.cells[index]=nbformat.v4.new_markdown_cell('[Optional video continuation: John Snow and the 1854 cholera outbreak](https://www.youtube.com/watch?v=lNjrAXGRda4). The local video is excluded because its individual reuse rights have not been established.')
        replace(25,'!pip install pandas numpy','# numpy and pandas are prepared in the first code cell; no shell install is needed.')
        replace(40,'%pip install -q folium','# Folium 0.20.0 is prepared in the first code cell; no shell install is needed.')
        replace(41,'folium.__version__','print(folium.__version__)')
        nb.cells[41].source+='\n\n'+BASIC_GRAY_MAP
        nb.cells[42].source='If `folium` is undefined, rerun the first code cell and then the Folium import cell above. Learn more in the [Folium documentation](https://python-visualization.github.io/folium/latest/).'
        nb.cells[38].source='In this mapping exercise, we will place historical mortality and pump data on a modern street basemap (Steps 2–5). The light-gray OpenStreetMap background is geographic context, not a reproduction of Snow\'s 1854 cartography.\n\n[Original map continuation](https://github.com/PHI-Case-Studies/Jupyterlite-1854-Cholera-Basic/blob/476f6dd5a8430e6eb823e79614fda1d7e12a78fb/images/20040209cholera.jpg)'
        nb.cells[47].source='The map uses one [OpenStreetMap](https://www.openstreetmap.org/copyright) street tile layer, with visible contributor attribution. OpenStreetMap is a collaboratively maintained modern map. Tiles and Folium JavaScript/CSS require network access; no offline map or historical street reconstruction is bundled.'
        nb.cells[49].source='Use the `gray_street_map()` helper to give every example a subdued light-gray background. Its original CSS affects only the Leaflet tile pane, so mortality and pump markers retain their teaching colors. This replaces the retired Stamen theme and credential-dependent CARTO choices.'
        nb.cells[50].source='# map1 already has one OpenStreetMap street layer with tile-pane-only gray styling.'
        nb.cells[54].source='A subdued background supports [amplified cognition](https://infovis-wiki.net/wiki/Amplified_cognition) by making the colored markers easier to see. We keep the same single OpenStreetMap layer and light-gray styling in the following examples.'
        replace(57,'# Try to change the theme to "cartodbpositron" below\nfolium.TileLayer(\'cartodbpositron\').add_to(map1)','# The helper keeps one light-gray street basemap; adjust zoom_start to explore.')
        replace(88,'# Pickling dataframes','# Optional local persistence exercise: create our output directory first.\nfrom pathlib import Path\nPath("outputs").mkdir(parents=True, exist_ok=True)\n\n# Pickling dataframes')
        nb.cells[89].source='# Inspect the generated local files using browser-compatible Python.\n[(path.name, path.stat().st_size) for path in sorted(Path("outputs").glob("*.pickle"))]'
        nb.cells[87].source+='\n\nThis local persistence exercise is optional for continuing to Notebook 2, which independently reads the bundled CSVs. Only load pickle files you created and trust; download valuable browser files before clearing site storage.'
    else:
        replace(8,'**Step 1.** Unpickle the dataframes from Notebook 1.','**Step 1.** Load the bundled historical CSVs independently of Notebook 1 outputs.')
        nb.cells[9].source='## <font color=\'blue\'>Step 1. Load the Historical Dataframes</font>'
        nb.cells[10].source='Load the same bundled historical CSVs used in Notebook 1. No previous notebook outputs are needed. As an optional persistence exercise, after running Notebook 1 you can use `pd.read_pickle("outputs/deaths_df.pickle")` and `pd.read_pickle("outputs/pumps_df.pickle")` instead. Only unpickle local files you created and trust.'
        replace(11,"# Let's read the pickle files back into their dataframes.\ndeaths_df = pd.read_pickle('outputs/deaths_df.pickle')\npumps_df = pd.read_pickle('outputs/pumps_df.pickle')","# Load bundled inputs; Notebook 1 outputs are not prerequisites.\ndeaths_df = pd.read_csv('resources/cholera_deaths.csv')\npumps_df = pd.read_csv('resources/pumps.csv')")
        replace(18,'mean_center_df.to_pickle(', 'from pathlib import Path\nPath("outputs").mkdir(parents=True, exist_ok=True)\nmean_center_df.to_pickle(')
        nb.cells[13].source+='\n\nThis weighted mean uses mortality coordinates and death counts only. Pumps are displayed for context and do not enter the calculation. It supplies neither an at-risk population denominator nor a causal inference about pump use.'
        replace(34,'Added Mean Center analysis to triangulate observations of pump and mortality locations on the map','Added a death-weighted mean of mortality coordinates. Pumps are displayed for context and do not enter the weighted mean; this supplies neither an at-risk population denominator nor a causal inference about pump use.')
        nb.cells[28].source='Recreate Notebook 1\'s final map with one modern OpenStreetMap street layer. The helper below applies light-gray CSS only to tiles, leaving mortality, pump and mean-center marker colors intact. Tiles and Folium JavaScript/CSS require network access. This is modern geographic context, not Snow\'s historical cartography.'
        replace(29,'%pip install -q folium','import folium\n\n'+BASIC_GRAY_MAP)
    expected_maps=5 if first else 1
    changed=0
    for cell in nb.cells:
        if cell.cell_type!='code':continue
        old='map1 = folium.Map(location=SOHO_COORDINATES, zoom_start=17)'
        changed+=cell.source.count(old)
        cell.source=cell.source.replace(old,'map1 = gray_street_map(location=SOHO_COORDINATES, zoom_start=17)')
        cell.source=cell.source.replace("\nfolium.TileLayer('cartodbpositron').add_to(map1)\n",'\n')
        cell.source=cell.source.replace('radius=radiuslist[i],','radius=radiuslist[i][0],')
    assert changed==expected_maps, f'Basic map constructors changed: {path}: {changed}'
    # Keep one continuation after all source-position-based changes are done.
    if first:del nb.cells[7]
    return [
        {'kind':'portability','adapter':'cholera-basic-browser-v1','reason':'Prepare numpy/pandas and pinned Folium 0.20.0 with piplite only in Pyodide; remove shell installers/listing; create owned output directories; use independent CSV prerequisites and external optional video continuations.'},
        {'kind':'basemap','adapter':'cholera-basic-browser-v1','reason':'Replace stacked/retired Stamen and CARTO tiles with one explicit keyless OpenStreetMap street layer and original tile-pane-only light-gray CSS; preserve visible OSM attribution and marker colors. Modern street context requires network access, not historical cartography or an offline map.'},
        {'kind':'marker','adapter':'cholera-basic-browser-v1','reason':'Pass each DEATHS value as a scalar CircleMarker radius, retaining the instructional radiuslist list-of-lists and the same mortality sizes/data.'},
        {'kind':'teaching','adapter':'cholera-basic-browser-v1','reason':'Retain one optional video continuation and explicit Folium version display; clarify that the death-weighted mortality center excludes pump locations and provides no at-risk denominator or causal inference.'},
    ]


def generated_configs():
    return {
        'courses/stac-browser/site-config.json':json.dumps({'base_path':'https://jltobias.github.io/JupyterLite-STAC-Browser/'},indent=2)+'\n',
        'courses/pyscript/hub-config.json':json.dumps({'base_url':'https://jltobias.github.io/JupyterLite-PyScript','hub_base':'https://jltobias.github.io/JupyterLite-PyScript/','base_path':'https://jltobias.github.io/JupyterLite-PyScript/'},indent=2)+'\n',
    }


def reconcile_source_sections(previous,current_paths,destination=None):
    """Remove only obsolete, unchanged manifest-owned source sections, never guides."""
    destination=Path(destination or DEST).resolve();current=set(current_paths);remove=[]
    for old in previous.get('sections',[]):
        if old['notebook'] in current:continue
        course_root=(destination/'courses'/old['course']).resolve()
        target=(destination/old['notebook']).resolve()
        if not course_root.is_relative_to(destination/'courses') or not target.is_relative_to(course_root) or target.suffix!='.ipynb' or target==course_root/'index.ipynb':
            raise ValueError(f'Unsafe obsolete source section: {old["notebook"]}')
        if not target.exists():continue
        nb=nbformat.read(target,as_version=4);atlas=nb.metadata.get('atlas',{})
        sources=[(c.cell_type,c.source) for c in nb.cells[1:]]
        if atlas.get('kind')!='source-section' or atlas.get('course')!=old['course'] or atlas.get('source_path')!=old['source_path'] or digest(json.dumps(sources,ensure_ascii=False).encode())!=old['adapted_cell_sha256']:
            raise ValueError(f'Refusing to remove an authored/modified obsolete source section: {old["notebook"]}')
        remove.append(target)
    for target in remove:target.unlink()
    return remove


def mapped(slug,path):
    for old,new in MAPS[slug]:
        if path.startswith(old): return new+path[len(old):]
    return None


def support_local_path(slug,path,notebook_paths):
    """Keep source Markdown out of canonical notebook document stems."""
    local=mapped(slug,path)
    if local is not None and PurePosixPath(local).suffix.lower()=='.md' and (
        local=='index.md' or any(mapped(slug,p)==str(PurePosixPath(local).with_suffix('.ipynb')) for p in notebook_paths)):
        return 'notices/source-documents/'+path
    return local


def exclusion(slug,path):
    lower=path.lower(); parts=PurePosixPath(path).parts
    if slug=='urbanity' and path in {f'book/_static/{name}' for name in ['urbanity-mark.svg','urbanity-pipeline.svg','urbanity-splash.svg']}:
        return None  # Audited original local vector illustrations, owner authorized.
    if any(p.startswith('.') or p in {'__pycache__','node_modules','_build','_static','exports','cache'} for p in parts):
        return 'Build/cache/config artifact, not a teaching dependency'
    if slug=='climate-and-health' and path.startswith('content/legacy/'):
        return 'Legacy collection and attachments explicitly excluded from modern license grants; figure/code rights unclear'
    if slug=='geolibre-geoai' and path.startswith('book/notebooks/assets/learning/') and path.endswith('.html'):
        return 'Upstream watch/index page references excluded poster/video media and source-relative Lab routes; keep the exact upstream experience as an external continuation'
    if 'gadm' in lower: return 'Restricted GADM redistribution; obtain permission/provider download externally'
    if 'imf-dm-export' in lower:return 'IMF dataset has provider-specific/non-open reuse terms; use source continuation instead of redistributing'
    if slug=='mdr-tb-thailand-2005' and PurePosixPath(path).name in {'MDR_RR_TB_burden_estimates_2019-07-03.csv','TB_burden_countries_2019-07-03.csv','TB_data_dictionary_2019-07-03.csv'}:
        return 'Legacy WHO compilation terms do not establish item-specific open redistribution/modification rights; current data.who.int terms do not retroactively license this 2019 export'
    if slug=='south-sudan-dashboard' and path.startswith('data/') and PurePosixPath(path).suffix.lower() not in {'.md','.txt'}:
        return 'Facility/H3/DEM input origin and file-specific reuse grant not established; obtain approved source data externally'
    if slug=='world-monitor-prototype' and path.startswith('content/data/worldmonitor/') and path.endswith('.json'):
        return 'Provider/news sandbox response fixture has no verified open dataset reuse grant; software licenses do not clear third-party quoted content'
    if slug=='drc-population-mobility-border-mapping' and path=='contents/data/ebola/drc_ebola_cases_consolidated.csv':
        return 'INRB-UMIE/BDBV2026 preliminary/prepublication epidemiological series requests investigator contact before reuse; no open item-specific grant established'
    if slug=='cholera-1854-advanced-1' and path=='content/data/Museums_in_DC.geojson':
        return 'Unrelated museum example has no file-specific origin/reuse metadata; not needed by cholera workflow'
    if slug=='cholera-1854-advanced-2' and ('settlement_pnts_clip' in path):
        return 'Settlement points/buffer sidecars have no observed item-specific source reuse grant; use approved local inputs'
    if slug in PHI and (PurePosixPath(path).suffix.lower() in MEDIA or 'book_format.py' in lower):
        return 'Optional third-party historical media/paper or unused helper; individual reuse rights not established'
    if PurePosixPath(path).suffix.lower() in MEDIA:
        cleared = slug=='geospatial-analyses-and-maps' and path.startswith(('images/','videos/'))
        cleared |= slug=='sea-level-rise' and PurePosixPath(path).name in {'continuity-comic.png','scenario-walkthrough.mp4','teaching-video-poster.png'}
        cleared |= (slug,path) in {('c3s-atlas','content/assets/atlas-splash.png'),('destination-earth-digital-twin','content/assets/splash.png'),('destination-earth-digital-twin','assets/splash.png')}
        if not cleared:
            return 'Optional media omitted: file-specific third-party/open reuse grant not established; retain pinned external continuation'
    if slug=='cross-border-ebola-risk-mapping-prototype' and path.startswith(('GIS/','data/')):
        return 'Controlled/sensitive or provider-specific source inputs; use approved aggregated inputs in the native workflow'
    if PurePosixPath(path).suffix.lower() in {'.pickle','.pkl'}:
        return 'Legacy serialized intermediate omitted; regenerate sequentially in the documented source environment; never unpickled during import'
    return None


def runtime(slug,path,nb):
    code='\n'.join(c.source for c in nb.cells if c.cell_type=='code')
    requirements=[]; klass='browser-local'
    if re.search(r'https?://|requests\.|urlopen|fetch\(|piplite.install|micropip.install',code):
        klass='browser-network'; requirements.append('Remote services, tiles, CDN assets or package retrieval are subject to network/CORS availability.')
    if re.search(r'\b(osmnx|geopandas|rasterio|whitebox|subprocess|cberm|gdal|osgeo|ollama)\b|^\s*[!%](?:run|system|conda|bash)|\brustgis\b',code,re.M) or slug in PHI or '/native/' in '/'+path:
        klass='local-server';requirements.append('Use the source local/server environment for native GIS, shell, installed project or legacy dependencies; Lab provides a reading/editing copy.')
    if slug=='hivdb-drug-resistance-maps' or (slug=='global-health-gis' and re.search('sample_gbd_like|gbd.*csv',code)):
        klass='reference-only';requirements.append('Required approved source tables are absent or user-supplied; source workflow/conditional template must be completed first.')
    if slug=='south-sudan-dashboard':
        klass='reference-only';requirements.append('Upstream facility/H3/DEM inputs lack a verified file-specific reuse grant and are not redistributed. Supply approved local inputs; upstream data/service paths remain external.')
    if slug=='gods-eye-view-satellite' and PurePosixPath(path).name.startswith(('05_','09_')):
        klass='browser-network'
        requirements.append('gev_lab.show_map/map_page loads viewers/map2d.html with Leaflet1.9.4 CSS/JavaScript from unpkg. Optional Esri World Imagery requests require network/CORS and Esri/provider terms. The local synthetic plots are separate from this interactive branch.' if PurePosixPath(path).name.startswith('05_') else 'gev_lab.show_map/map_page loads viewers/scene3d.html with Cesium1.124 JavaScript/CSS from jsDelivr and requires browser WebGL. This synthetic grid scene uses no terrain, imagery or API token, but CDN availability is still required; use the pinned source runtime for the full 3D experience.')
    if slug=='global-informal-settlements-storymap' and PurePosixPath(path).name.startswith('08_'):
        klass='reference-only';requirements.append('The AI/chat sidebar requires jupyterlite-ai, absent from the Atlas Pyodide-only shell. The source build must generate global/Global_Human_Settlements_Tour.jGIS and global/ghsl_urban_centres.geojson when absent; open the upstream source deployment for that complete tour and AI integration.')
    if slug=='world-monitor-prototype' and PurePosixPath(path).name.startswith(('01_','02_')):
        klass='reference-only';requirements.append('The default sandbox_index()/sandbox_fixture()/response_body() path reads excluded data/worldmonitor/index.json and operation JSON fixtures (GetCountryRisk, ListMarketQuotes, GetChokepointStatus, GetForecasts). Provider/news fixture reuse rights are unverified, so these inputs are not redistributed; use the upstream source continuation or approved inputs. Synthetic district calculations remain local.')
    if slug=='pyscript':
        klass='browser-network';requirements.append('Local Python preparation and inspectable shared sources are bundled; interactive PyScript apps run separately at the explicitly configured upstream base_url and load their own runtime/CDN assets and data. Notebook variables are not shared with those app interpreters.')
    language=nb.metadata.get('language_info',{}).get('name','python').lower()
    if language not in {'python','ipython'}:
        klass='reference-only';requirements.append(f'Original {language} kernel is not bundled in the Atlas Pyodide-only shell; use the source runtime for execution.')
    if re.search('api[_ -]?key|token|credential|localhost|127.0.0.1',code,re.I):
        requirements.append('Optional live/model branches require their own credentials or local service; do not enter secrets in a public notebook.')
    if slug in PHI: requirements.append('Follow notebook order to regenerate omitted outputs; optional unlicensed media are external continuations.')
    if slug=='gpt-6-astra-geospatial' and 'wasm' in code:
        requirements.append('The upstream build compiles twin_kernel.wasm; if absent, compile in the source toolchain before that branch.')
    if slug in {'geolibre-geoai','zarr-sql-views'}:requirements.append('Widget/anywidget/LexCube branches need their source extensions; the Atlas shell supplies only Pyodide.')
    if slug=='c3s-atlas':
        klass='browser-network';requirements=[
            'Browser-only piplite prepares numpy, pandas, matplotlib and Plotly 6.5.0; native kernels use installed scientific packages. Local calculations use bundled helpers and inputs; Plotly rendering can require its versioned CDN and WebGL.',
            'Seeded monthly examples are synthetic. The C3S warming-level table gives model windows, Natural Earth provides real generalized coastlines, and the CDS catalogue is metadata. No authenticated CDS request, archive download or native regridding is run.',
        ]
    if slug=='destination-earth-digital-twin':
        klass='browser-network';requirements=[
            'Browser-only piplite prepares numpy, matplotlib, pandas, xarray and ipywidgets. Calculations use earthlab.py and original synthetic arrays, not observations or real Digital Twin outputs.',
            'Optional widget controls need the source frontend; static figures and numerical results provide alternatives. Real DestinE accounts, Polytope/Data Lake services, GRIB/netCDF decoding and HPC remain explicit source/native continuations. No credentials or service requests are required for these defaults.',
        ]
    if slug=='urbanity':
        klass='browser-local';requirements=[
            'Standard-library synthetic network, context, imagery-label and graph exercises; these executable cells do not import Urbanity or download OSM/provider data.',
            'Native Urbanity, compiled GIS, imagery and graph-ML examples in Markdown are continuations requiring their own environment and data permissions. Owner-authorized original material has no inferred public repository license.',
        ]
    if slug=='terrio':
        klass='reference-only';requirements=[
            'Reading/editing copy only in the shared Atlas kernel. TerrIO 0.9.0 uses a pyemscripten_2025_0 wasm wheel for Pyodide 0.29; the source pins jupyterlite-pyodide-kernel 0.8.0b0 (default Pyodide 0.29.4). This wheel is incompatible with Atlas Pyodide 314; do not install it here or downgrade the shared runtime.',
            '[Run this lesson in its matched source Lab](https://jltobias.github.io/JupyterLite-terrio/lite/lab/index.html?path='+PurePosixPath(path).name+').',
            'The source uses Plotly 6.3.1, xarray 2025.10.1 and optional CDN/WebGL graphics. Natural Earth countries are real generalized geography; all other numerical fixtures are explicitly synthetic. Native HTTP range I/O, specialized drivers and real service/model calls remain optional external continuations.',
        ]
    if not requirements:requirements=['Local calculations and bundled inputs; first browser runtime/package download still needs connectivity. Static inspection is not execution certification.']
    # Small, explicitly audited local set. Other source code is never auto-run.
    selected=slug in {'population-data-comparison','onehealth'} or (slug=='spatial-analysis' and path.endswith('01_VC_vector-conversion.ipynb')) or (slug=='eo-satellite-guide' and path.endswith('02_sensor_comparison.ipynb'))
    if slug in {'population-data-comparison','onehealth'}: klass='browser-local'
    if slug=='cholera-1854-basic' and path in BASIC_NOTEBOOKS:
        klass='browser-network';selected=True
        requirements=[
            'Run either notebook independently in a fresh Pyodide kernel: the first code cell prepares numpy/pandas and Folium 0.20.0 with piplite. Native kernels use the pinned Atlas build requirements.',
            'Bundled historical CSVs supply calculations; OpenStreetMap street tiles and Folium JavaScript/CSS require network access. One tile layer uses original light-gray CSS while markers retain their colors and OSM attribution remains visible. No offline or historical street-map claim.',
            'Optional video is an external continuation. Local pickle persistence is an exercise, not a Notebook 2 prerequisite; output directories are created before writes.',
        ]
    return {'class':klass,'requirements':requirements,'execution_selected':selected}


def normalize_markdown(source,base,slug,course,aliases,available,changes):
    """Resolve local source links, retaining exact external continuations for gaps."""
    def target(value):
        if slug=='pyscript' and value.startswith('{{HUB_BASE}}'):
            result=value.replace('{{HUB_BASE}}','https://jltobias.github.io/JupyterLite-PyScript',1)
            changes.append({'kind':'link','from':value,'to':result,'reason':'Preserved the exact source-declared deployment continuation'})
            return result
        if slug=='geolibre-geoai' and re.search(r'(?:^|/)assets/learning/\d+/watch\.html$',urlsplit(value).path):
            path=urlsplit(value).path.split('assets/learning/',1)[1]
            result='https://jltobias.github.io/JupyterLite-GeoLibre-GeoAI/lite/files/assets/learning/'+path
            changes.append({'kind':'external-continuation','from':value,'to':result,'reason':'Watch HTML is excluded with its unavailable media/relative Lab dependencies'})
            return result
        u=urlsplit(value)
        if u.scheme or value.startswith(('#','//','data:','mailto:')):return value
        if not u.path:return value
        # Normalize POSIX paths without consulting source filesystem symlinks.
        import posixpath
        upstream=posixpath.normpath(posixpath.join(str(PurePosixPath(base).parent),unquote(u.path)))
        reason=None
        if slug in APPEND_COURSES and PurePosixPath(upstream).suffix.lower()=='.md':
            # These copied support documents are deliberately outside the TOC.
            # MyST otherwise rewrites .md links into nonexistent HTML routes.
            local=course_source[slug]['url']+'/blob/'+course_source[slug]['commit']+'/'+upstream
            reason='Non-TOC source Markdown retained locally for inspection; exact immutable source continuation prevents an absent Book HTML cross-reference.'
        elif (slug=='osiris' and upstream=='content/intro.md') or (slug=='data-visualization' and upstream=='content/repository_examples/index.md'):
            local=posixpath.relpath(f'courses/{slug}/index.ipynb',str(PurePosixPath(course).parent))
        elif upstream in aliases:
            local=posixpath.relpath(aliases[upstream],str(PurePosixPath(course).parent))
        else:
            local_source=mapped(slug,upstream)
            local_full=f'courses/{slug}/{local_source}' if local_source is not None else None
            if local_full in available:
                local=posixpath.relpath(local_full,str(PurePosixPath(course).parent))
            else:
                # Keep the intended source path even if the pin lacks its input;
                # a self-link silently loses the requested destination.
                local=course_source[slug]['url']+'/blob/'+course_source[slug]['commit']+'/'+upstream
        result=local+('?' + u.query if u.query else '')+('#'+u.fragment if u.fragment else '')
        if result!=value:
            change={'kind':'link','from':value,'to':result}
            if reason:change['reason']=reason
            changes.append(change)
        return result
    # Keep markup/prose while converting unsupported relative references into
    # exact pinned source links. HTML image/media paths are covered too.
    source=re.sub(r'(!?\[[^\]]*\]\()([^\s)]+)(\))',lambda m:m[1]+target(m[2])+m[3],source)
    source=re.sub(r'((?:src|href|poster)=[\"\'])([^\"\']+)([\"\'])',lambda m:m[1]+target(m[2])+m[3],source)
    if slug in PHI:
        source,n=re.subn(r'!?\[[^\]]*\]\(data:image[^)]*\)|<img\b[^>]*src=[\"\']data:image[^>]*>', '[Embedded historical figure omitted: individual reuse rights not established; consult the pinned source.]',source,flags=re.I)
        if n:changes.append({'kind':'rights','reason':'Removed embedded third-party historical figure with unclear rights','count':n})
    # MyST turns dollar delimiters and ambiguous HTML into warnings; retain text
    # semantics while disabling accidental equation parsing in source prose.
    return neutralize_embeds(source,changes)


def neutralize_embeds(source,changes):
    """Reading copies never auto-load an external interactive/media branch."""
    def continuation(kind,url,label=''):
        changes.append({'kind':'embed','reason':'External/uncleared media render changed to an explicit continuation; code/prose retained','type':kind,'url':url})
        return f'[{label or "Source " + kind + " continuation"}]({url})'
    source=re.sub(r'!\[([^\]]*)\]\((https?://[^\s)]+)\)',lambda m:continuation('image',m[2],'Source image continuation: '+m[1]),source)
    def html_media(match):
        markup=match[0];target=re.search(r'\bsrc=[\"\']([^\"\']+)[\"\']',markup,re.I)
        if not target:return markup
        kind=match[1].lower();url=target[1]
        if kind=='iframe' or url.startswith(('http://','https://','//')):
            return continuation(kind,url)
        return markup
    source=re.sub(r'<(iframe|video|audio)\b[^>]*>.*?</\1\s*>',html_media,source,flags=re.I|re.S)
    source=re.sub(r'<img\b[^>]*\bsrc=[\"\'](https?://[^\"\']+)[\"\'][^>]*>',lambda m:continuation('image',m[1]),source,flags=re.I)
    return source


course_source={}


def normalize_headings(nb,changes):
    """Repair source heading jumps for strict MyST without changing prose."""
    previous=1;levels={1:1};count=0
    for c in nb.cells:
        if c.cell_type!='markdown':continue
        fence=False;lines=[]
        for line in c.source.splitlines(keepends=True):
            if line.lstrip().startswith(('```','~~~')):fence=not fence
            match=re.match(r'^(#{1,6})(\s+.*)',line) if not fence else None
            if match:
                level=len(match[1]);new=min(level,previous+1,levels.get(level,level))
                levels[level]=new;previous=new
                if new!=level:line='#'*new+line[level:];count+=1
            lines.append(line)
        c.source=''.join(lines)
    if count:changes.append({'kind':'format','reason':'Normalized nonconsecutive Markdown heading levels for strict MyST; heading text retained','count':count})


def prepare_source_notebook(r,n,nb,local,disposition,license_text,aliases,available):
    """Prepare a single pinned notebook; also used for narrowly scoped refreshes."""
    slug=r['slug'];changes=[{'kind':'format','reason':'Normalized notebook v4.5 and deterministic unique cell IDs; inserted Atlas provenance/runtime cell; cleared unverified outputs and widget execution state.'}]
    changes.extend(adapt_basic_notebook(slug,n['path'],nb))
    changes.extend(adapt_expansion_notebook(slug,n['path'],nb))
    run=runtime(slug,n['path'],nb)
    for i,c in enumerate(nb.cells):
        c['id']=digest((local+':'+str(i)).encode())[:16]
        if c.cell_type=='code':c.outputs=[];c.execution_count=None
        elif c.cell_type=='markdown':
            c.source=normalize_markdown(c.source,n['path'],slug,local,aliases,available,changes)
            if slug=='pyscript' and '{{HUB_BASE}}' in c.source:
                c.source=c.source.replace('{{HUB_BASE}}','https://jltobias.github.io/JupyterLite-PyScript');changes.append({'kind':'config','reason':'Resolved HUB_BASE placeholder to exact upstream project continuation'})
        if c.get('attachments'):
            c.source=re.sub(r'!\[[^\]]*\]\(attachment:[^)]+\)','[Embedded image omitted: file-specific reuse rights not established; consult pinned source.]',c.source)
            del c['attachments'];changes.append({'kind':'rights','reason':'Unclear historical attachment omitted'})
    nb.metadata.pop('widgets',None)
    if nb.metadata.get('language_info',{}).get('name','python').lower() in {'python','ipython'}:
        nb.metadata['kernelspec']={'display_name':'Python (Pyodide)','language':'python','name':'python3'}
    nb.nbformat_minor=5
    title=re.sub(r'^#+\s*','',n.get('first_heading') or PurePosixPath(local).stem).strip()[:180]
    compatibility='Compatibility appendix: inherited JupyterLite demonstration, not an authored cholera case lesson.' if slug=='cholera-1854-advanced-1' and not PurePosixPath(n['path']).name.startswith('NB') else ''
    intro=f"# {title}\n\n**Atlas source reading copy · {run['class']}**\n\n[Course guide]("+__import__('posixpath').relpath(f'courses/{slug}/index.ipynb',str(PurePosixPath(local).parent))+f") · [Pinned original]({disposition['source_url']})\n\n{compatibility}\n\n"+' '.join(run['requirements'])+f"\n\n**Provenance:** `{n['path']}` at `{r['commit']}`; original SHA-256 `{disposition['source_sha256']}`. {license_text}\n\n**Verification:** imported by static inspection; saved upstream outputs cleared. Runtime compatibility is separate from executed verification. See the course guide for dependencies, excluded assets, aliases and original credits.\n"
    normalize_headings(nb,changes)
    adapted=cell_digest(nb)
    nb.cells.insert(0,nbformat.v4.new_markdown_cell(intro,id=digest((local+':provenance').encode())[:16]))
    nb.metadata['atlas']={'kind':'source-section','course':slug,'source_path':n['path'],'source_commit':r['commit'],'source_sha256':disposition['source_sha256'],'runtime':run['class'],'data_status':'source-specific; see preserved provider metadata','verification':'not-run'}
    if slug=='cholera-1854-basic' and n['path'] in BASIC_NOTEBOOKS:
        nb.metadata.atlas['modifications']=[change for change in changes if change.get('adapter')=='cholera-basic-browser-v1']
    nbformat.validate(nb)
    return nb,{'course':slug,'title':title,'notebook':local,'source_path':n['path'],'source_sha256':disposition['source_sha256'],'source_cell_sha256':disposition['source_cell_sha256'],'adapted_cell_sha256':adapted,'runtime':run,'verification':{'status':'not-run','reason':'Static import; execution receipts are separate under _build/'},'license':license_text,'modifications':changes,'collection':'compatibility' if compatibility else 'authored'}


def refresh_basic_notebooks():
    """Reapply only the audited Basic repair, preserving every other record/file."""
    manifest=json.loads((ROOT/'catalog/source-library.json').read_text(encoding='utf-8'))
    slug='cholera-1854-basic';record=next(c for c in manifest['courses'] if c['slug']==slug)
    course_source[slug]=record
    aliases={d['source_path']:d['notebook'] for d in manifest['dispositions'] if d['course']==slug and d['disposition']!='excluded'}
    available={s['local_path'] for s in manifest['support_files']}|{s['notebook'] for s in manifest['sections']}
    pending=[]
    for index,section in enumerate(manifest['sections']):
        if section['course']!=slug or section['source_path'] not in BASIC_NOTEBOOKS:continue
        raw=(SOURCES/slug/section['source_path']).read_bytes()
        assert digest(raw)==section['source_sha256'], 'Basic original source hash changed'
        original=nbformat.reads(raw.decode('utf-8-sig'),as_version=4)
        assert cell_digest(original)==section['source_cell_sha256'], 'Basic original cell hash changed'
        disposition=next(d for d in manifest['dispositions'] if d['course']==slug and d['source_path']==section['source_path'])
        prepared,current=prepare_source_notebook(record,{'path':section['source_path'],'first_heading':section['title']},original,
            section['notebook'],disposition,section['license'],aliases,available)
        pending.append((index,prepared,current))
    assert len(pending)==len(BASIC_NOTEBOOKS), 'Basic refresh requires both canonical sections'
    # No existing destination is touched until both sources and preparations pass.
    for index,prepared,current in pending:
        target=DEST/current['notebook'];target.parent.mkdir(parents=True,exist_ok=True)
        nbformat.write(prepared,target);manifest['sections'][index]=current
    write_json(ROOT/'catalog/source-library.json',manifest)
    write_json(ROOT/'site/data/source-library.json',manifest)
    return manifest


def update_inventory(manifest):
    manifest['inventory']={
        'repositories':len(manifest['courses']), 'inspected_notebook_paths':len(manifest['dispositions']),
        'imported_sections':len(manifest['sections']),
        'authored_sections':sum(s['collection']=='authored' for s in manifest['sections']),
        'compatibility_sections':sum(s['collection']=='compatibility' for s in manifest['sections']),
        'aliases':sum(d['disposition']=='alias' for d in manifest['dispositions']),
        'excluded_notebooks':sum(d['disposition']=='excluded' for d in manifest['dispositions']),
        'support_files':len(manifest['support_files']),
    }


def append_courses(slugs):
    """Prepare the complete append in memory before touching any destination.

    Only new course namespaces are writable. Previous manifest rows and files
    remain untouched, including locally authored course guides and saved outputs.
    A failed preparation or write rolls back the new files and manifest mirrors.
    Tests use tiny local Git fixtures; no network or research audit is required.
    """
    slugs=list(slugs)
    if not slugs or len(slugs)!=len(set(slugs)):
        raise ValueError('Choose distinct new course slugs')
    unknown=set(slugs)-set(APPEND_COURSES)
    if unknown:raise ValueError('Unreviewed append course: '+', '.join(sorted(unknown)))
    source_manifest=ROOT/'catalog/source-library.json'
    original=source_manifest.read_bytes();previous=json.loads(original)
    existing={c['slug'] for c in previous['courses']}
    if existing.intersection(slugs):raise ValueError('Existing course cannot be appended: '+', '.join(sorted(existing.intersection(slugs))))
    manifest=copy.deepcopy(previous);pending={};candidates=[];aliases_by_course={}
    def add(local,data):
        path=PurePosixPath(local)
        if path.is_absolute() or '..' in path.parts or '\\' in local or not path.parts or path.parts[0]!='courses' or path.parts[1] not in slugs:
            raise ValueError('Unsafe append destination: '+local)
        if local in pending and pending[local]!=data:raise ValueError('Append destination collision: '+local)
        if (DEST/local).exists():raise FileExistsError('Append destination already exists: '+local)
        pending[local]=data
    for slug in slugs:
        name,pin,count=APPEND_COURSES[slug];checkout=SOURCES/slug
        if (DEST/'courses'/slug).exists():raise FileExistsError('New course namespace already exists: '+slug)
        actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=checkout,text=True).strip()
        if actual!=pin:raise ValueError('Pin changed: '+slug)
        if subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=checkout,text=True).strip():
            raise ValueError('Pinned tracked source checkout has local changes: '+slug)
        tracked=[p for p in subprocess.check_output(['git','ls-files','-z'],cwd=checkout).decode().split('\0') if p]
        for path in tracked:
            target=(checkout/path).resolve()
            if not target.is_relative_to(checkout.resolve()) or (checkout/path).is_symlink() or not target.is_file():
                raise ValueError('Unsafe or missing tracked source: '+path)
        notebooks=ordered_notebooks(slug,[p for p in tracked if p.endswith('.ipynb')])
        if len(notebooks)!=count:raise ValueError('Incomplete source notebook inventory: '+slug)
        r={'slug':slug,'name':name,'url':'https://github.com/jltobias/'+name,'commit':pin}
        course_source[slug]=r
        license_text=('Original owner-authored companion incorporated at repository owner request; Urbanity source repository has no public license grant. Package Urbanity and third-party data retain separate terms.' if slug=='urbanity' else
            'Original code MIT; original prose, generated numerical data and cleared artwork CC BY 4.0, with attribution and Atlas adaptation notice. Official DestinE references/datasets are linked context, not copied inputs.' if slug=='destination-earth-digital-twin' else
            'Original code MIT; original teaching prose, synthetic data and chapter SVG diagrams CC0. Natural Earth is public domain; TerrIO/dependency/EPSG terms remain separately scoped in retained notices. No TerrIO wheel redistributed.' if slug=='terrio' else
            'Original course material MIT; C3S auxiliary table Apache-2.0, Natural Earth public domain and CDS catalogue metadata CC BY 4.0. Preserve source credits, licenses and artwork provenance.')
        manifest['courses'].append({**r,'guide':f'courses/{slug}/index.ipynb','license':license_text,'source_notebook_paths':count,'family':None})
        aliases_by_course[slug]={}
        for path in notebooks:
            raw=(checkout/path).read_bytes();nb=nbformat.reads(raw.decode('utf-8-sig'),as_version=4)
            local=mapped(slug,path)
            if local is None or local=='index.ipynb':raise ValueError('Unmapped source notebook: '+path)
            local=f'courses/{slug}/{local}'
            heading=next((line for c in nb.cells if c.cell_type=='markdown' for line in c.source.splitlines() if line.startswith('#')),'')
            d={'course':slug,'source_path':path,'source_sha256':digest(raw),'source_cell_sha256':cell_digest(nb),'source_url':r['url']+'/blob/'+pin+'/'+path,'disposition':'imported','notebook':local}
            manifest['dispositions'].append(d);aliases_by_course[slug][path]=local
            candidates.append((r,{'path':path,'first_heading':heading},nb,local,d,license_text))
        support={}
        for path in tracked:
            if path.endswith('.ipynb'):continue
            local=support_local_path(slug,path,notebooks);reason=exclusion(slug,path)
            if reason and local is not None:
                manifest['asset_exclusions'].append({'course':slug,'source_path':path,'reason':reason,'source_url':r['url']+'/blob/'+pin+'/'+path})
            if local is not None and not reason and PurePosixPath(path).suffix.lower() in {s.lower() for s in SAFE_EXT} and PurePosixPath(path).name not in {'_config.yml','_toc.yml'}:
                collect_support(support,local,slug,path,checkout)
            if (len(PurePosixPath(path).parts)==1 and (any(t in path.lower() for t in ['license','notice','attribution','citation','readme']) or path=='requirements.txt')) or path.startswith('licenses/'):
                if not reason:collect_support(support,'notices/'+path,slug,path,checkout)
        for source,local in EXTRA.get(slug,[]):
            if source not in tracked:raise ValueError('Missing reviewed dependency: '+source)
            if exclusion(slug,source):raise ValueError('Excluded explicit dependency: '+source)
            collect_support(support,local,slug,source,checkout)
        for local,(_,path) in support.items():
            raw=(checkout/path).read_bytes()
            full=f'courses/{slug}/{local}';add(full,raw)
            item={'course':slug,'source_path':path,'local_path':full,'source_sha256':digest(raw),'sha256':digest(raw),'license':license_text,'source_url':r['url']+'/blob/'+pin+'/'+path}
            manifest['support_files'].append(item)
    available=set(pending)|{c[3] for c in candidates}
    for item in manifest['support_files'][len(previous['support_files']):]:
        local=item['local_path'];path=item['source_path'];slug=item['course']
        data,changes=prepare_support(slug,path,local,pending[local],aliases_by_course[slug],available)
        pending[local]=data;item['sha256']=digest(data)
        if changes:item['modifications']=changes
    for r,n,nb,local,d,license_text in candidates:
        prepared,section=prepare_source_notebook(r,n,nb,local,d,license_text,aliases_by_course[r['slug']],available)
        add(local,nbformat.writes(prepared).encode('utf-8'));manifest['sections'].append(section)
    update_inventory(manifest)
    # Validate collisions across *every* manifest namespace, before writes.
    paths=[s['notebook'] for s in manifest['sections']]+[s['local_path'] for s in manifest['support_files']]
    if len(paths)!=len(set(paths)):raise ValueError('Manifest path collision')
    mirrors=[source_manifest,ROOT/'site/data/source-library.json']
    before={p:p.read_bytes() if p.exists() else None for p in mirrors};written=[]
    data=(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n').encode('utf-8')
    try:
        for local,content in pending.items():
            target=DEST/local;target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as stream:
                written.append(target)  # Exclusive creation succeeded; track even a partial write/close.
                stream.write(content)
        for path in mirrors:
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    except BaseException:
        for path,content in before.items():
            if content is not None:path.write_bytes(content)
            elif path.exists():path.unlink()
        for path in reversed(written):path.unlink(missing_ok=True)
        for slug in slugs:
            base=DEST/'courses'/slug
            if base.exists():
                for directory in sorted((p for p in base.rglob('*') if p.is_dir()),key=lambda p:len(p.parts),reverse=True):directory.rmdir()
                base.rmdir()
        raise
    return manifest


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true')
    parser.add_argument('--cholera-basic-only',action='store_true',help='Reapply only the audited Basic pair from the pinned local checkout')
    parser.add_argument('--append',nargs='+',choices=APPEND_COURSES,help='Append only complete reviewed new courses; never replay existing imports')
    args=parser.parse_args()
    if args.check:
        from source_library import validate_library
        library=validate_library(verify_sources=True);print(f"PASS pinned source/support hashes and all {len(library['dispositions'])} dispositions");return
    if args.append:
        if args.cholera_basic_only:parser.error('--append cannot refresh existing Basic notebooks')
        print(json.dumps(append_courses(args.append)['inventory']));return
    if args.cholera_basic_only:
        refresh_basic_notebooks();print('Prepared only the two Cholera Basic notebooks and their manifest records');return
    previous=json.loads((ROOT/'catalog/source-library.json').read_text(encoding='utf-8')) if (ROOT/'catalog/source-library.json').exists() else {}
    # Additional verified external license notices are tracked canonical files,
    # not necessarily present in the pinned course checkout. Preserve their
    # exact manifest-owned bytes rather than dropping them on an import refresh.
    external_notices=[]
    for item in previous.get('support_files',[]):
        if not item.get('source_path') and item.get('source_url','').startswith('https://') and '/notices/' in item['local_path']:
            path=(DEST/item['local_path']).resolve()
            assert path.is_relative_to((DEST/'courses'/item['course']).resolve()) and digest(path.read_bytes())==item['sha256']
            external_notices.append(item)
    audit_path=ROOT/'_research/textbook-source-audit.json'
    if audit_path.exists():
        audit=json.loads(audit_path.read_text(encoding='utf-8'))
        missing={c['slug'] for c in previous.get('courses',[])}-{c['slug'] for c in audit['repositories']}
        if missing:raise ValueError('Stale research audit would drop existing courses: '+', '.join(sorted(missing)))
    else:
        # A fresh clone can reproduce the import from checked-in immutable pins
        # after the operator prepares those checkouts. Historical research files
        # are not a hidden prerequisite and the importer never fetches them.
        assert previous.get('courses'), 'Prepare the42 pinned checkouts listed in catalog/source-library.json'
        audit={'checked_on':previous['inspected_on'],'repositories':[]}
        for course in previous['courses']:
            checkout=SOURCES/course['slug']
            tracked=[p for p in subprocess.check_output(['git','ls-files','-z'],cwd=checkout).decode().split('\0') if p]
            notebooks=[]
            for path in tracked:
                if not path.endswith('.ipynb') or any(p.startswith('.') for p in PurePosixPath(path).parts):continue
                original=json.loads((checkout/path).read_text(encoding='utf-8-sig'))
                heading=next((line for c in original.get('cells',[]) if c.get('cell_type')=='markdown' for line in ''.join(c.get('source','')).splitlines() if line.startswith('#')),'')
                notebooks.append({'path':path,'first_heading':heading})
            licenses=[p for p in tracked if len(PurePosixPath(p).parts)<4 and any(t in PurePosixPath(p).name.lower() for t in ['license','licence','attribution','notice','citation'])]
            readmes=[p for p in tracked if len(PurePosixPath(p).parts)<3 and PurePosixPath(p).name.lower().startswith('readme')]
            audit['repositories'].append({**course,'notebooks':notebooks,'licenses':licenses,'readmes':readmes})
    manifest={'schema_version':1,'inspected_on':audit['checked_on'],'policy':'Original jltobias material incorporated at repository owner request. No general license inferred where absent; all third-party terms remain scoped. No source code executed during import.','inventory':{},'courses':[],'sections':[],'support_files':[],'dispositions':[],'asset_exclusions':[]}
    candidates=[];support={};aliases_by_course={}
    for r in audit['repositories']:
        slug=r['slug'];course_source[slug]=r;checkout=SOURCES/slug
        pin=subprocess.check_output(['git','rev-parse','HEAD'],cwd=checkout,text=True).strip()
        assert pin==r['commit'],f'Pin changed: {slug}'
        tracked=subprocess.check_output(['git','ls-files','-z'],cwd=checkout).decode().split('\0')
        tracked=[p for p in tracked if p]
        license_text='Source-specific license/notices retained under notices; data and media have separate terms.' if any(PurePosixPath(p).name.upper()=='LICENSE' for p in r['licenses']) else 'Original author material incorporated at repository owner request; no general license inferred. Third-party terms remain separate.'
        manifest['courses'].append({'slug':slug,'name':r['name'],'url':r['url'],'commit':pin,'guide':f'courses/{slug}/index.ipynb','license':license_text,'source_notebook_paths':len(r['notebooks']),'family':'periodic-table-spatial' if slug in {'spatial-analysis','maps-and-spatial-analyses','geospatial-analyses-and-maps','geospatial-analyses-and-maps-old'} else None})
        for path in tracked:
            if path.endswith('.ipynb'):continue
            local=mapped(slug,path);reason=exclusion(slug,path)
            if reason and (local is not None or not reason.startswith('Build/cache')):
                manifest['asset_exclusions'].append({'course':slug,'source_path':path,'reason':reason,'source_url':r['url']+'/blob/'+pin+'/'+path});continue
            if local is not None and not reason and (PurePosixPath(path).suffix.lower() in {s.lower() for s in SAFE_EXT} or PurePosixPath(path).name in {'LICENSE','COPYING'}):
                # Broad root maps are only for these legacy/root-staged sources.
                if slug in PHI and len(PurePosixPath(path).parts)>1 and PurePosixPath(path).parts[0] not in {'resources','images','audio','outputs','data','content'}:continue
                if slug=='geospatial-research-awareness-radar' and len(PurePosixPath(path).parts)>1:continue
                if PurePosixPath(local).name in {'_config.yml','_toc.yml','jupyter-lite.json','jupyter_lite_config.json'}:continue
                if PurePosixPath(local).suffix=='.md' and (local=='index.md' or any(mapped(slug,n['path'])==str(PurePosixPath(local).with_suffix('.ipynb')) for n in r['notebooks'])):
                    local='notices/source-documents/'+path
                full=f'courses/{slug}/{local}'
                if slug in APPEND_COURSES:collect_support(support,full,slug,path,checkout)
                else:support[full]=(slug,path)
        for source,local in EXTRA.get(slug,[]):
            assert (checkout/source).is_file(),(slug,source)
            full=f'courses/{slug}/{local}'
            if slug in APPEND_COURSES:collect_support(support,full,slug,source,checkout)
            else:support[full]=(slug,source)
        # Preserve scoped rights and source narratives, even outside runtime root.
        notices=set(r['licenses'])|set(r['readmes'])|{p for p in tracked if len(PurePosixPath(p).parts)<=2 and PurePosixPath(p).name in {'LICENSES.md','DATA_SOURCES.md','SOURCES.md','CREDITS.md','ATTRIBUTIONS.md','THIRD_PARTY_NOTICES.md'}}
        notices |= {p for p in tracked if (p.startswith('licenses/') or p.startswith('notices/')) and PurePosixPath(p).suffix.lower() in {'.txt','.md'} }
        notices |= {p for p in tracked if p.startswith(('book/','docs/')) and any(t in PurePosixPath(p).name.lower() for t in ['credit','reference','attribution','license','governance','data-source']) and PurePosixPath(p).suffix=='.md'}
        for path in sorted(notices):
            if not exclusion(slug,path):
                full=f'courses/{slug}/notices/{path}'
                if slug in APPEND_COURSES:collect_support(support,full,slug,path,checkout)
                else:support[full]=(slug,path)
        seen={};aliases_by_course[slug]={}
        # Prefer deployed RustGIS Lite and Basic root editions for exact matches.
        paths=ordered_notebooks(slug,r['notebooks'])
        for n in paths:
            path=n['path'];raw=(checkout/path).read_bytes();nb=nbformat.reads(raw.decode('utf-8-sig'),as_version=4);cellhash=cell_digest(nb)
            disposition={'course':slug,'source_path':path,'source_sha256':digest(raw),'source_cell_sha256':cellhash,'source_url':r['url']+'/blob/'+pin+'/'+path}
            reason=exclusion(slug,path)
            if reason:
                disposition.update(disposition='excluded',reason=reason)
            elif cellhash in seen:
                disposition.update(disposition='alias',notebook=seen[cellhash],reason='Exact ordered cell-type/source sequence; canonical preferred deployment edition')
                aliases_by_course[slug][path]=seen[cellhash]
            else:
                local=mapped(slug,path);assert local is not None,(slug,path)
                full=f'courses/{slug}/{local}';assert full!=f'courses/{slug}/index.ipynb'
                seen[cellhash]=full;aliases_by_course[slug][path]=full
                disposition.update(disposition='imported',notebook=full)
                candidates.append((r,n,nb,full,disposition,license_text))
            manifest['dispositions'].append(disposition)
    available=set(support)|{x[3] for x in candidates}
    reconcile_source_sections(previous,{x[3] for x in candidates})
    for old in previous.get('support_files',[]):
        if old['local_path'] not in support and old['local_path'] not in {s['local_path'] for s in external_notices}:
            obsolete=(DEST/old['local_path']).resolve()
            assert obsolete.is_relative_to((DEST/'courses').resolve())
            if obsolete.is_file():obsolete.unlink()
    for local,(slug,path) in sorted(support.items()):
        original=(SOURCES/slug/path).read_bytes();data,changes=prepare_support(slug,path,local,original,aliases_by_course[slug],available)
        out=DEST/local;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
        item={'course':slug,'source_path':path,'local_path':local,'source_sha256':digest(original),'sha256':digest(data),'license':'Retains source-specific notices and provider terms; see course guide and notices/','source_url':course_source[slug]['url']+'/blob/'+course_source[slug]['commit']+'/'+path}
        if changes:item['modifications']=changes
        manifest['support_files'].append(item)
    manifest['support_files'].extend(external_notices)
    generated={
      **generated_configs(),
      'courses/cholera-1854-advanced-2/notices/GLA-BOUNDARIES.md':'# Greater London boundaries\n\nSource: Greater London Authority, Statistical GIS boundary files for London (2015).\nhttps://data.london.gov.uk/dataset/statistical-gis-boundary-files-for-london-20od9\n\nOpen Government Licence v2.0: https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/\n\nContains National Statistics data © Crown copyright and database right [2015]\n\nContains Ordnance Survey data © Crown copyright and database right [2015]\n\nCopied source boundary files retain their original bytes. This notice is an Atlas attribution addition; no endorsement is implied.\n',
      **{f'courses/{slug}/notices/OPENSTREETMAP.md':'# OpenStreetMap-derived streets\n\n© OpenStreetMap contributors. Open Database Licence (ODbL) 1.0.\nhttps://www.openstreetmap.org/copyright\nhttps://opendatacommons.org/licenses/odbl/1-0/\n\nStreet graphs and derived layers were prepared by the source OSMnx workflow. Source file bytes are retained; the Atlas does not independently validate completeness or currency. Tile/service and software terms remain separate.\n' for slug in ['cholera-1854-advanced-1','cholera-1854-advanced-2','mdr-tb-thailand-2005']},
    }
    for local,source in generated.items():
        data=source.encode();out=DEST/local;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
        manifest['support_files'].append({'course':PurePosixPath(local).parts[1],'local_path':local,'sha256':digest(data),'license':'Original Atlas configuration/attribution text; cited provider terms apply to source data','modifications':'Intentionally serialized Atlas preparation/configuration; not claimed as an upstream tracked file'})
    for r,n,nb,local,disposition,license_text in candidates:
        prepared,section=prepare_source_notebook(r,n,nb,local,disposition,license_text,aliases_by_course[r['slug']],available)
        out=DEST/local;out.parent.mkdir(parents=True,exist_ok=True);nbformat.write(prepared,out)
        manifest['sections'].append(section)
    manifest['inventory']={'repositories':len(manifest['courses']),'inspected_notebook_paths':len(manifest['dispositions']),'imported_sections':len(manifest['sections']),'authored_sections':sum(s['collection']=='authored' for s in manifest['sections']),'compatibility_sections':sum(s['collection']=='compatibility' for s in manifest['sections']),'aliases':sum(d['disposition']=='alias' for d in manifest['dispositions']),'excluded_notebooks':sum(d['disposition']=='excluded' for d in manifest['dispositions']),'support_files':len(manifest['support_files'])}
    write_json(ROOT/'catalog/source-library.json',manifest)
    print(json.dumps(manifest['inventory']))


if __name__=='__main__':main()
