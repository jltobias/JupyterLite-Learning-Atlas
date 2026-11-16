"""Explicit local metadata append for the four audited 2026-11-16 courses.

Routine generation never invokes this script and never contacts a network.
"""
from __future__ import annotations
import copy
import json
from pathlib import Path
import subprocess

from expansion_material import LESSONS, profiles
from import_sources import APPEND_COURSES

ROOT=Path(__file__).resolve().parents[1]
DATE='2026-11-16'
ROUTES={
 'c3s-atlas':[('book','Read source Book','book/index.html'),('lab','Run source Lab','lite/lab/index.html?path=01-atlas-orientation.ipynb'),('hub','Open source portal',''),('map-2d','Explore C3S teaching maps','maps/'),('map-3d','Explore C3S teaching globe','globe/'),('scene-3d','Explore C3S teaching scenes','scenes/')],
 'destination-earth-digital-twin':[('book','Read source Book','book/'),('lab','Run source Lab','lab/index.html?path=01-system.ipynb'),('hub','Open source portal',''),('map-2d','Explore synthetic map gallery','gallery/map/'),('map-3d','Explore synthetic terrain gallery','gallery/terrain/'),('scene-3d','Explore synthetic globe gallery','gallery/globe/'),('explorer','Explore synthetic dashboard','gallery/dashboard/'),('explorer','Explore synthetic vector flow','gallery/flow/'),('explorer','Explore synthetic comparison','gallery/compare/')],
 'urbanity':[('book','Read source Book',''),('lab','Run source Lab','lab/lab/index.html?path=notebooks/street-networks.ipynb'),('map-2d','Explore synthetic urban map','exhibits/2d-map.html'),('map-3d','Explore synthetic urban heights','exhibits/3d-map.html'),('scene-3d','Explore synthetic urban scene','exhibits/3d-scene.html')],
 'terrio':[('book','Read source Book','book/intro.html'),('lab','Run matched TerrIO source Lab','lite/lab/index.html?path=01-first-contact.ipynb'),('hub','Open source portal',''),('map-2d','Explore TerrIO 2D maps','maps/2d.html'),('map-3d','Explore TerrIO 3D maps','maps/3d.html'),('scene-3d','Explore TerrIO scene and globe','maps/scenes.html')],
}


def write_catalogs(updates):
    """Restore every catalog/mirror on any write or close failure."""
    before={path:path.read_bytes() if path.exists() else None for path in updates}
    prepared={path:(json.dumps(value,indent=2,ensure_ascii=False)+'\n').encode('utf-8') for path,value in updates.items()}
    try:
        for path,data in prepared.items():path.write_bytes(data)
    except BaseException:
        for path,data in before.items():
            if data is None:
                if path.exists():path.unlink()
            else:path.write_bytes(data)
        raise


def main():
    names=['repositories','discovery','launch-checks','map-resources','browser-gis-pathways','data-attributions','source-library']
    data={name:json.loads((ROOT/'catalog'/f'{name}.json').read_text(encoding='utf-8')) for name in names}
    if set(APPEND_COURSES)&{r['slug'] for r in data['repositories']['repositories']}:
        raise ValueError('Expansion catalog entries already exist; explicit append cannot replay them')
    old_support={s['local_path'] for s in data['source-library']['support_files'] if s['course'] not in APPEND_COURSES}
    for slug,(name,pin,count) in APPEND_COURSES.items():
        lesson=LESSONS[slug];url='https://github.com/jltobias/'+name;base='https://jltobias.github.io/'+name+'/'
        readme=url+'/blob/'+pin+'/README.md';resources=[]
        for kind,label,path in ROUTES[slug]:
            destination=base+path
            resources.append({'kind':kind,'label':label,'url':destination,
                'description':'Exact source README/workflow route; synthetic demonstrations and source-specific runtime/terms apply.',
                'availability':'Source-route reviewed; HTTP entry not freshly checked','checked_on':DATE,'http_status':None})
            data['launch-checks']['results'].append({'repository':name,'url':destination,'status':None,'checked_on':DATE,
                'verification':'Exact pinned README and publishing-layout provenance; no fresh HTTP or runtime certification.'})
            if kind not in {'map-2d','map-3d','scene-3d','explorer'}:continue
            identifier='map-'+str(len(data['map-resources']['resources'])+1).zfill(3)
            data['map-resources']['resources'].append({'id':identifier,'repository':name,'title':label.removeprefix('Explore '),
                'url':destination,'mode':{'map-2d':'2d-map','map-3d':'3d-map','scene-3d':'3d-scene','explorer':'explorer'}[kind],
                'data_class':'synthetic-with-reference-context' if slug in {'c3s-atlas','terrio'} else 'synthetic',
                'description':lesson['summary']+' Runtime, geographic/reference and synthetic status remain separate.',
                'source_commit':pin,'evidence_url':readme,'evidence_type':'exact-readme-and-build-layout',
                'runtime_verification':'not run; reviewed source routes only',
                'entry_check':{'id':identifier,'url':destination,'status':None,'checked_on':DATE,'verification':'not freshly checked'}})
        data['repositories']['repositories'].append({'name':name,'title':lesson['title'],'slug':slug,'theme':lesson['theme'],
            'summary':lesson['summary'],'status':'learning companion','category':'jupyterlite','learning_question':lesson['question'],
            'source_url':url,'readme_url':readme,'default_branch':'main','source_commit':pin,'inspected_on':DATE,
            'visibility':'public','notebook':f'projects/{slug}/index.ipynb','book_path':f'book/projects/{slug}/index.html',
            'lab_path':f'lite/lab/index.html?path=projects/{slug}/index.ipynb','resources':resources,
            'launch_status':'Exact pinned source README and publishing-layout routes reviewed 2026-11-16; HTTP entry and runtime checks remain separate.',
            'attribution':'James L. Tobias / jltobias; '+name+'. Original Atlas exercise and adaptation; source/provider/software/media terms remain separate.',
            'limitations':lesson['limits']+' '+lesson['reading']})
        data['discovery']['repositories'].append({'name':name,'default_branch':'main','visibility':'public','url':url})
        data['discovery']['targeted_additions'].append({'repository':name,'owner':'jltobias','inspected_on':DATE,'source_commit':pin,
            'scope':f'Complete {count}-notebook pinned source/rights/dependency/runtime review; prior discovery rows retained.'})
        checkout=ROOT/'_research/textbook-sources'/slug
        blob=subprocess.check_output(['git','rev-parse','HEAD:README.md'],cwd=checkout,text=True).strip()
        data['map-resources']['repository_coverage'].append({'repository':name,'url':url,'visibility':'public','default_branch':'main',
            'readme_path':'README.md','readme_blob_sha':blob,'readme_available':True,'verified_head_commit':pin,
            'map_status':'indexed-experiences; source-route review only; synthetic fields and real reference/geographic data distinguished'})
    data['repositories']['scope']+=' Targeted 2026-11-16 complete pinned C3S Atlas, Destination Earth Digital Twin, Urbanity and TerrIO expansion: 39 core + 7 related = 46 chapters; all prior catalog rows retained.'
    data['discovery']['method']+=' Targeted 2026-11-16 append preserves all68 prior entries and adds four reviewed public owner repositories: 68 public owner repositories,40 JupyterLite names including Atlas, plus4 external PHI records =72 discovery entries.'
    data['launch-checks']['method']+=' Targeted 2026-11-16 append records exact pinned routes separately from fresh HTTP entry/runtime certification; prior174 rows preserved.'
    data['browser-gis-pathways']['pathways'].extend(profiles())
    data['browser-gis-pathways']['scope']='46 distinct project companions and 46 course guides; prior 42 profiles and shared templates unchanged; imported lessons remain unchanged'
    data['browser-gis-pathways']['inspected_on']=DATE
    data['map-resources']['checked_on']=DATE
    register=data['data-attributions'];register['inspected_on']=DATE
    def row(identifier,title,credit,rights,modifications,files):
        register['datasets'].append({'id':identifier,'title':title,'credit':credit,'rights':rights,'modifications':modifications,'files':files})
    prefix='courses/c3s-atlas/'
    row('c3s-warming-levels','C3S Atlas CMIP6 global-warming-level windows',
        'European Union; C3S Atlas User Tools contributors; underlying CMIP6 modelling groups. ecmwf-projects/c3s-atlas commit 8d80d4e98053d96077ba67f29464b4f373ff4037, auxiliar/GWLs/CMIP6_WarmingLevels.csv. Gutiérrez et al. (2024), DOI 10.21957/ah52ufc369; Iturbide et al. (2020), DOI 10.5194/essd-12-2959-2020.',
        'Apache-2.0; retained licenses/C3S-Atlas-Apache-2.0.txt and source credit.',
        'Unmodified 5,095-byte auxiliary CSV; model/scenario/threshold time windows, not observed local temperatures.',[prefix+'data/reference/CMIP6_WarmingLevels.csv'])
    row('c3s-natural-earth-coastline','Natural Earth 1:110m coastline',
        'Made with Natural Earth. Nathaniel Vaughn Kelso, Tom Patterson and contributors; natural-earth-vector commit ca96624a56bd078437bca8184e78163e5039ad19, geojson/ne_110m_coastline.geojson.',
        'Public domain; retain Natural Earth source/credit notice.',
        'Unmodified 139,907-byte generalized geographic context; no boundary authority or precision claim.',[prefix+'data/reference/ne_110m_coastline.geojson'])
    row('c3s-cds-catalogue','C3S Atlas CDS catalogue snapshot (2026-11-15)',
        'Copernicus Climate Change Service / ECMWF / European Union, multi-origin-c3s-atlas catalogue; dataset DOI 10.24381/cds.h35hb680.',
        'CC BY 4.0 as declared by the retained source manifest; source credits and adaptation notice retained.',
        'Unmodified 5,461-byte metadata snapshot; full gridded climate archive not used or redistributed.',[prefix+'data/reference/atlas-catalogue.json'])
    row('c3s-synthetic-monthly','C3S companion synthetic monthly teaching series',
        'James L. Tobias / JupyterLite-C3S-Atlas, atlas_helpers.py monthly_demo(), seed 381; explicitly synthetic temperature examples.',
        'Original teaching fixtures MIT; no Copernicus observation claim.',
        'Unmodified CSV and JSON sidecar retained, including units, rounding and generator labels.',[prefix+'data/examples/monthly_series.csv',prefix+'data/examples/monthly_series.json'])
    row('terrio-natural-earth-countries','Natural Earth countries v5.1.2 (177 features)',
        'Made with Natural Earth. Tom Patterson, Nathaniel Vaughn Kelso and contributors; countries v5.1.2. Source/version/checksum retained in sources.json.',
        'Public domain; preserve source attribution and generalized-boundary limitations.',
        'Unmodified 838,726-byte GeoJSON; SHA-256 6866c877d39cba9c357620878839b336d569f8c662d3cfab4cb1dbe2d39c977f. Generalized geography, not authoritative borders.',
        ['courses/terrio/data/countries.geojson','courses/terrio/data/sources.json'])
    # The remaining JSON files are original course registries/provenance records,
    # not observational inputs. Every placement still gets explicit coverage.
    credited={p for r in register['datasets'] for p in r.get('files',[])}
    suffixes={'.json','.csv','.geojson','.tsv','.npz','.npy'}
    metadata=[s['local_path'] for s in data['source-library']['support_files'] if s['local_path'] not in old_support and Path(s['local_path']).suffix in suffixes and s['local_path'] not in credited]
    row('expansion-course-metadata','C3S/DestinE/TerrIO source course registries and provenance metadata',
        'James L. Tobias and named source-course contributors (2026); original curriculum/chapter/lesson registries and file-provenance manifests. C3S manifests identify separately credited reference data.',
        'Source-specific: C3S original metadata MIT; DestinE original prose/generated data CC BY4.0; TerrIO original teaching metadata CC0. Provider datasets retain separate terms.',
        'Exact pinned local metadata; no observational/DT/model-service output implied. DestinE and Urbanity numerical teaching fixtures are synthetic equations/code, not downloaded datasets.',metadata)
    register['notes'].append('**2026-11-16 expansion:** Urbanity owner authorization does not imply a public license. DestinE arrays are synthetic, not real twin output; original numerical data/prose CC BY4.0 and code MIT. TerrIO original synthetic fixtures and13 SVGs are CC0, original code MIT; TerrIO/software/dependency/EPSG/IOGP rights remain separate. TerrIO reading copies require the matched Pyodide0.29 source Lab; Atlas stays on314. Only file-specifically cleared original C3S/DestinE PNGs and original Urbanity/TerrIO SVGs are imported with provenance.')
    updates={ROOT/'catalog'/f'{name}.json':value for name,value in data.items() if name!='source-library'}
    updates.update({ROOT/'site/data/catalog.json':data['repositories'],ROOT/'site/data/map-resources.json':data['map-resources'],ROOT/'content/assets/browser-gis-pathways.json':data['browser-gis-pathways']})
    # All validation above completes before any publication catalog is changed.
    write_catalogs(updates)
    print('Appended4 catalog/discovery courses,26 reviewed launch routes,15 map/explorer entries,4 GIS profiles and exact dataset placements.')


if __name__=='__main__':main()
