"""Explicit, deterministic import of inspected pins. Never run/fetch upstream code.

Run only to intentionally rebuild source snapshots. Routine generation preserves them.
All inspected notebook paths have an imported/alias/excluded disposition; support
files have hashes and rights exclusions have exact paths and source continuations.
"""
from __future__ import annotations

import argparse
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
SAFE_EXT = {'.py','.json','.geojson','.csv','.tsv','.txt','.md','.css','.html','.js','.mjs','.svg','.shp','.shx','.dbf','.prj','.cpg','.gpkg','.xlsx','.xls','.graphml','.xml','.yaml','.yml','.jgis','.jGIS','.npz','.npy','.zip','.whl','.ttl','.vtt','.srt','.wasm','.tif','.tiff','.feather'} | MEDIA


def digest(data): return hashlib.sha256(data).hexdigest()
def cell_digest(nb): return digest(json.dumps([(c.cell_type,c.source) for c in nb.cells],ensure_ascii=False).encode())
def write_json(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def adapt_support(slug,path,data):
    """Small recorded portability adapters; upstream checkouts remain immutable."""
    changes=[]
    if slug=='stac-browser' and path=='notebooks/stac_browser.py':
        old='return str(location.origin) + config["base_path"].rstrip("/") + "/explorer/"'
        new='return ("" if urlsplit(config["base_path"]).scheme else str(location.origin)) + config["base_path"].rstrip("/") + "/explorer/"'
        text=data.decode('utf-8');assert text.count(old)==1, 'STAC explorer adapter source changed'
        data=text.replace(old,new).encode('utf-8')
        changes.append({'kind':'portability','reason':'Absolute source continuation must not be prefixed by the Atlas worker origin','from':old,'to':new})
    return data,changes


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


def exclusion(slug,path):
    lower=path.lower(); parts=PurePosixPath(path).parts
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
    if not requirements:requirements=['Local calculations and bundled inputs; first browser runtime/package download still needs connectivity. Static inspection is not execution certification.']
    # Small, explicitly audited local set. Other source code is never auto-run.
    selected=slug in {'population-data-comparison','onehealth'} or (slug=='spatial-analysis' and path.endswith('01_VC_vector-conversion.ipynb')) or (slug=='eo-satellite-guide' and path.endswith('02_sensor_comparison.ipynb'))
    if slug in {'population-data-comparison','onehealth'}: klass='browser-local'
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
        if (slug=='osiris' and upstream=='content/intro.md') or (slug=='data-visualization' and upstream=='content/repository_examples/index.md'):
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
        if result!=value:changes.append({'kind':'link','from':value,'to':result})
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


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    if args.check:
        from source_library import validate_library
        validate_library(verify_sources=True);print('PASS pinned source/support hashes and all 753 dispositions');return
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
                support[f'courses/{slug}/{local}']=(slug,path)
        for source,local in EXTRA.get(slug,[]):
            assert (checkout/source).is_file(),(slug,source)
            support[f'courses/{slug}/{local}']=(slug,source)
        # Preserve scoped rights and source narratives, even outside runtime root.
        notices=set(r['licenses'])|set(r['readmes'])|{p for p in tracked if len(PurePosixPath(p).parts)<=2 and PurePosixPath(p).name in {'LICENSES.md','DATA_SOURCES.md','SOURCES.md','CREDITS.md','ATTRIBUTIONS.md','THIRD_PARTY_NOTICES.md'}}
        notices |= {p for p in tracked if (p.startswith('licenses/') or p.startswith('notices/')) and PurePosixPath(p).suffix.lower() in {'.txt','.md'} }
        notices |= {p for p in tracked if p.startswith(('book/','docs/')) and any(t in PurePosixPath(p).name.lower() for t in ['credit','reference','attribution','license','governance','data-source']) and PurePosixPath(p).suffix=='.md'}
        for path in sorted(notices):
            if not exclusion(slug,path):support[f'courses/{slug}/notices/{path}']=(slug,path)
        seen={};aliases_by_course[slug]={}
        # Prefer deployed RustGIS Lite and Basic root editions for exact matches.
        paths=sorted(r['notebooks'],key=lambda n:(n['path'].startswith('notebooks/') if slug=='rustgis' else n['path'].startswith('contents/'),n['path']))
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
        original=(SOURCES/slug/path).read_bytes();data,changes=adapt_support(slug,path,original)
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
        slug=r['slug'];changes=[{'kind':'format','reason':'Normalized notebook v4.5 and deterministic unique cell IDs; inserted Atlas provenance/runtime cell; cleared unverified outputs and widget execution state.'}]
        run=runtime(slug,n['path'],nb)
        for i,c in enumerate(nb.cells):
            c['id']=digest((local+':'+str(i)).encode())[:16]
            if c.cell_type=='code':c.outputs=[];c.execution_count=None
            elif c.cell_type=='markdown':
                c.source=normalize_markdown(c.source,n['path'],slug,local,aliases_by_course[slug],available,changes)
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
        nbformat.validate(nb);out=DEST/local;out.parent.mkdir(parents=True,exist_ok=True);nbformat.write(nb,out)
        manifest['sections'].append({'course':slug,'title':title,'notebook':local,'source_path':n['path'],'source_sha256':disposition['source_sha256'],'source_cell_sha256':disposition['source_cell_sha256'],'adapted_cell_sha256':adapted,'runtime':run,'verification':{'status':'not-run','reason':'Static import; execution receipts are separate under _build/'},'license':license_text,'modifications':changes,'collection':'compatibility' if compatibility else 'authored'})
    manifest['inventory']={'repositories':len(manifest['courses']),'inspected_notebook_paths':len(manifest['dispositions']),'imported_sections':len(manifest['sections']),'authored_sections':sum(s['collection']=='authored' for s in manifest['sections']),'compatibility_sections':sum(s['collection']=='compatibility' for s in manifest['sections']),'aliases':sum(d['disposition']=='alias' for d in manifest['dispositions']),'excluded_notebooks':sum(d['disposition']=='excluded' for d in manifest['dispositions']),'support_files':len(manifest['support_files'])}
    write_json(ROOT/'catalog/source-library.json',manifest)
    print(json.dumps(manifest['inventory']))


if __name__=='__main__':main()
