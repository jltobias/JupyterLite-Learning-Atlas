"""Original chapter introductions and discovery for the pinned source library."""
from __future__ import annotations
from collections import Counter
import json
import hashlib
import posixpath
from pathlib import Path
import nbformat

from source_library import ROOT, load_library
from expansion_material import LESSONS as EXPANSION_LESSONS, COURSE_VISUALS


NEW = {
 'nasa-arset-experiments': {
  'title':'Choose an Earth observation before choosing an index',
  'theme':'Terrain & Earth observation',
  'summary':'Original Atlas resolution and observation-design exercises complement official ARSET learning resources. The source repository is README-only.',
  'question':'Which combination of pixel support, revisit time and spectral information could answer a bounded environmental question?',
  'method':'Compare spatial, temporal, spectral and radiometric resolution separately. A finer pixel cannot recover an observation missed between acquisitions; a dense time series cannot identify a spectral property its sensor never measured. Cloud and QA masks change coverage. Match the measurement dates and footprint to the decision before computing an index.',
  'exercise':"candidates = {'fine spatial':{'pixel_m':10,'revisit_days':10}, 'frequent view':{'pixel_m':250,'revisit_days':1}, 'regional detail':{'pixel_m':30,'revisit_days':16}}\nwindow_days = 7\nexpected = {k:window_days/v['revisit_days'] for k,v in candidates.items()}\nprint('Fictional design candidates, not sensor product specifications:', candidates)\nbars(expected, 'Synthetic expected opportunities in a seven-day window', 'opportunities before clouds')",
  'interpret':'This illustrative calculation compares potential opportunities, not usable acquisitions or scientific accuracy. A seven-day event may be missed by a sixteen-day cycle; 250 m support may mix a small water body with surrounding land. Band ratios do not establish health effects. Inspect the QA, cloud cover, projection, units and calibration before comparing scenes.',
  'change':'Set window_days to 30, then add an explicit assumed cloud-free fraction. Explain why multiplying by that fraction is a scenario rather than a forecast. Design a water, fire, crop or air-quality question with a footprint, date window, target observable, validation observation and a stopping rule.',
  'limits':'README-only source: no original source notebooks, dataset, Book, Lab or hosted project deployment are supplied. This is independently authored Atlas teaching material, not a NASA/ARSET course or endorsed product. Official slides, videos, handouts, NASA logos and third-party course repositories are not copied. Official ARSET resources remain external and retain their own terms.',
  'reading':'Begin with [NASA Earth Action](https://science.nasa.gov/earth-science/earth-action/), the [NASAARSET code organization](https://github.com/NASAARSET), and the [Fundamentals course](https://arset.unhosting.site/course/view.php?id=26), which may require an account. Those are external learning references, not launches of this README-only project. Resolution trade-offs, band calibration, compositing and projections are prerequisites for a defensible application. Write the expected observable and an alternative explanation before choosing an NDVI/NDWI-like ratio. No NASA artwork or course handouts are imported; [NASA media policy](https://www.nasa.gov/nasa-brand-center/images-and-media/) remains separately scoped.'},
 'population-data-comparison': {
  'title':'Compare population products on their native support', 'theme':'Global health',
  'summary':'Three complete local source notebooks compare real Greater Lagos WorldPop, GRID3, LandScan and GHS-POP native count cells with an independent oracle.',
  'question':'How do coverage, population concept and partial-cell overlap change an estimate for the same rectangle?',
  'method':'Count cells contain modelled people on native grids; density is a display quantity. The Population source course retains native offsets instead of resampling products onto a common grid. Residential and ambient population concepts and their reference dates differ. NoData is missing evidence; numeric zero is a valid value. Agreement among products sharing inputs is not independent validation.',
  'exercise':"cells = [{'people':120,'fraction':1.0}, {'people':80,'fraction':0.25}, {'people':0,'fraction':0.5}]\nweighted = sum(c['people']*c['fraction'] for c in cells)\nprint('Synthetic partial-cell total:', weighted)\nbars({'whole cells':sum(c['people'] for c in cells),'area-fraction estimate':weighted}, 'Synthetic count support comparison', 'modelled people')",
  'interpret':'The synthetic example gives 140 people under a uniform-within-cell assumption, compared with 200 if every intersected cell is counted in full. Neither is ground truth. The actual source lessons below use credited real model products and spherical overlap areas, then reproduce a shared rectangle against a separately prepared oracle.',
  'change':'Change the partial overlap from 0.25 to 0.75 and explain the implicit within-cell assumption. Then open all three source notebooks: compare the independent oracle, inspect native cells and coverage, and export results while retaining every product citation and modification field.',
  'limits':'Source JSON contains real modelled Greater Lagos excerpts, not observed individual people. WorldPop 2025/GRID3 2025, LandScan ambient 2020 and GHS-POP projected residential 2025 differ in concept and date. All selected excerpts retain CC BY 4.0 creator/version/source/modification metadata. The broader TIFF viewer remains an external continuation; browser Range/CORS and provider restrictions are separate from local JSON notebook execution.',
  'reading':'The complete population.json and independent_oracle.json are local siblings of the three source notebooks, along with population_tools.py and its exact population_tools_real.py alias. The source uses standard-library Python. First browser runtime retrieval needs networking; the population calculations then read local inputs. Exports retain provenance. No full TIFF viewer or arbitrary-raster GIS capability is claimed.'},
 'onehealth': {
  'title':'Connect environmental observations to bounded One Health questions', 'theme':'Global health',
  'summary':'Eleven complete source lessons join real Fresno Landsat samples and Census tracts while keeping environmental proxies, population denominators and health evidence distinct.',
  'question':'What can real surface observations and tract denominators support, and which One Health evidence is still missing?',
  'method':'One Health connects people, animals, plants and their environment. Global Health adds equity and missing voices; spatial epidemiology adds support, time and ecological inference. Fresno Landsat 9 data were acquired on 2024-08-30, while tract populations reference 2020-04-01. Surface temperature is neither air temperature nor personal exposure, and a vegetation/water proxy is not illness evidence.',
  'exercise':"tracts = [{'population':400,'overlap':0.5}, {'population':600,'overlap':0.2}]\nwhole = sum(t['population'] for t in tracts)\narea_fraction = sum(t['population']*t['overlap'] for t in tracts)\nprint('Synthetic whole-tract count:', whole, 'Synthetic overlap estimate:', area_fraction)\nbars({'whole tracts':whole,'uniform area-fraction estimate':area_fraction}, 'Synthetic denominator support', 'people')",
  'interpret':'A whole-tract population sum is not the population inside a bounding box. An area-fraction estimate assumes uniform population within each tract. The real source profile includes 6,890 systematic Landsat samples and 166 Census tracts (764,468 whole-tract people); those totals retain their distinct measurement support and dates.',
  'change':'Change one overlap fraction, then list the additional observations needed for a health or equity question. Follow source lessons 00–10 for provenance, QA/scaling, vegetation/water, heat, scale, point-in-polygon joins, evidence gaps and an exportable evidence brief.',
  'limits':'Real public-domain USGS/NASA Landsat and U.S. Census inputs retain their exact source metadata. Original OneHealth source material is included at the owner request without a general license inferred. Agency articles, photographs, presentation figures and videos remain external. Environmental proxies are not validated disease or vulnerability scores. The live explorer has separate service/CORS/acquisition requirements.',
  'reading':'All lesson calculation inputs are bundled at data/manifest.json, data/pixels.csv and data/tracts.geojson, with source-metadata.json and README. Matplotlib is required; first browser package/runtime retrieval may use the network. Landsat DN reflectance scaling is DN×0.0000275−0.2; temperature in °C is DN×0.00341802+149−273.15, with the source QA/mask rules retained. Thermal product grid spacing is not independent thermal support.'},
}
NEW.update(EXPANSION_LESSONS)


def chapter_cells(record,md,code,helpers):
    m=NEW[record['slug']]
    return [md(f"# {m['title']}\n\n**Learning question:** {m['question']}\n\n{m['summary']}\n\nThis introductory calculation is an original **synthetic** teaching exercise. Full source lessons and their actual data status are separately described below."),
            md('## Predict before running\n\n'+m['method']),code(helpers),code(m['exercise']),
            md('## Interpret the result\n\n'+m['interpret']+'\n\n## Change one thing\n\n'+m['change']),
            md('## Source course and scientific boundaries\n\n'+m['reading']+f"\n\n[Complete local course guide](../../courses/{record['slug']}/index.ipynb) · [Notebook library](../../notebook-library.ipynb)"),
            md(f"## Sources, attribution and limits\n\n[Reviewed source README]({record['readme_url']}) · [Source repository]({record['source_url']})\n\n{m['limits']}\n\n"+'\n'.join(f"- [{x['label']}]({x['url']}) — {x['availability']}" for x in record['resources'])+'\n\n[Central references](../../references.ipynb)')]


def refresh_managed_notebook(notebook,path,cells,**metadata):
    """Refresh owned guide/library blocks, retaining every unowned authored cell."""
    managed='atlas-source-library'
    def key(cell):return hashlib.sha256(cell['source'].splitlines()[0].encode()).hexdigest()[:16]
    fresh=[]
    for cell in cells:
        cell=nbformat.from_dict(cell)
        cell.metadata['atlas_managed']={'owner':managed,'key':key(cell)}
        cell['id']=hashlib.sha256((path+':'+key(cell)).encode()).hexdigest()[:12]
        fresh.append(cell)
    notebook(path,fresh,**metadata)
    target=ROOT/'content'/path
    if not target.exists():return  # Supports callers capturing seed content.
    nb=nbformat.read(target,as_version=4)
    if nb.metadata.get('atlas',{}).get('kind')!=metadata['kind']:
        return  # A separately authored notebook has not opted into management.
    original=json.dumps(nb,sort_keys=True,ensure_ascii=False)
    # Migrate only cells carrying the old generator's deterministic IDs. New
    # user-created cells have independent IDs and remain in place with outputs.
    legacy_ids={hashlib.sha256((path+str(i)).encode()).hexdigest()[:12] for i in range(len(nb.cells)+len(fresh)+1)}
    wanted={key(c):c for c in fresh};emitted=set();updated=[];insertion=0
    for cell in nb.cells:
        marker=cell.metadata.get('atlas_managed',{})
        owned=marker.get('owner')==managed or cell.get('id') in legacy_ids or (cell.get('id')=='lexcube-source' and cell.source.startswith('## LexCube source availability'))
        if owned:
            block=marker.get('key',key(cell))
            if block in wanted and block not in emitted:
                updated.append(wanted[block]);emitted.add(block)
            insertion=len(updated)
        else:updated.append(cell)
    updated[insertion:insertion]=[c for c in fresh if key(c) not in emitted]
    nb.cells=updated
    nb.metadata.atlas['managed_blocks']=managed
    if json.dumps(nb,sort_keys=True,ensure_ascii=False)!=original:nbformat.write(nb,target)


def seed_library(notebook,md,records):
    library=load_library();by_slug={r['slug']:r for r in records}
    intro=[md('# The source notebook library\n\nRead full pinned source lessons alongside the original short Atlas companions. Each notebook is the same canonical file in Book and Lab. Runtime labels describe intended requirements; execution receipts identify the smaller set actually tested. First runtime/package downloads require connectivity. Download important edits and exports from browser storage.\n\n**Browser local:** bundled calculation inputs. **Browser network:** remote APIs, tiles, packages or services. **Local/server:** native GIS, shell, legacy or installed services. **Reference only:** missing/conditional inputs. A local Lab link is an editing/reading handoff, not a promise every branch executes there.')]
    inv=library['inventory'];intro.append(md(f"## Scope and provenance\n\n{inv['repositories']} pinned source repositories; {inv['inspected_notebook_paths']} inspected notebook paths; {inv['authored_sections']} distinct authored lessons, {inv['compatibility_sections']} inherited compatibility examples, {inv['aliases']} exact aliases and {inv['excluded_notebooks']} rights-excluded legacy notebooks. Source code and prose are preserved except documented format, provenance, link, rights and browser compatibility adaptations. Unverified upstream outputs were cleared. Scoped notices and file hashes are recorded in the [published source manifest](https://github.com/jltobias/JupyterLite-Learning-Atlas/blob/main/catalog/source-library.json).\n\nFour spatial periodic-table variants are retained as separate course editions: synthetic methods, map-centric, older helper and current map/helper editions. The current map/helper guide gives the richest local map/data context; matching titles do not establish duplicates."))
    for course in library['courses']:
        slug=course['slug'];sections=[s for s in library['sections'] if s['course']==slug]
        counts=Counter(s['runtime']['class'] for s in sections)
        row=f"## {by_slug[slug]['title']}\n\n[Course guide]({course['guide']}) · [Original Atlas companion]({by_slug[slug]['notebook']})\n\n{len(sections)} complete local source notebooks"+(' · '+', '.join(f'{k}: {v}' for k,v in counts.items()) if counts else ' · No upstream source notebooks: see the clearly original Atlas material and source-status explanation.')+f"\n\n{course['license']}"
        intro.append(md(row))
        cells=[md(f"# {by_slug[slug]['title']} — source course\n\n[Atlas companion](../../projects/{slug}/index.ipynb) · [All courses](../../notebook-library.ipynb)\n\n**Pinned source:** [{course['name']}]({course['url']}/tree/{course['commit']}) at `{course['commit']}`. {course['license']}\n\n{len(sections)} full local source notebooks. Original ordering and within-course file layout are retained. Run sequential prerequisites in a fresh course kernel; helper names overlap across courses. Python-level network guarding is applied only to selected verification runs. No native/service branches are automatically executed. Saved source outputs were cleared, so reading publication alone is not execution proof.")]
        if slug in NEW:cells.append(md(NEW[slug]['reading']+'\n\n'+NEW[slug]['limits']))
        if slug in EXPANSION_LESSONS:
            image,alternative,credit=COURSE_VISUALS[slug]
            cells.append(md(f'## Course visual\n\n![{alternative}]({image})\n\n{credit}'))
            cells.append(md('## Calculation and frontend verification\n\nThe separate [2026-11-16 expansion execution receipt](https://jltobias.github.io/JupyterLite-Learning-Atlas/catalog/expansion-execution.json) records fresh guarded native calculations for the four original companions and all 59 safe C3S, Destination Earth and Urbanity source notebooks. Five optional Destination Earth widget-only cells are explicitly skipped; these controls need their source frontend. The 13 TerrIO source copies remain unexecuted reading/editing copies requiring their matched Pyodide 0.29 source Lab. Native numerical success and saved figures do not certify browser package/CDN/WebGL rendering, optional widgets, real services or native geospatial extensions. Import-time table labels below remain separate from these later execution receipts.'))
        if slug=='cholera-1854-basic':cells.append(md('## Browser map preparation\n\nBoth full Basic notebooks run independently from the bundled historical CSVs. Their first code cell uses browser-aware piplite preparation for numpy/pandas and Folium 0.20.0; native kernels use the pinned Atlas build requirements. Each map uses one keyless OpenStreetMap street layer with visible contributor attribution and original CSS limited to the tile pane, so red mortality, blue pump and yellow-green mean-center markers retain their colors. This modern light-gray context does not reproduce Snow\'s 1854 streets. Tiles and Folium JavaScript/CSS need network access; no provider tiles are bundled or promised offline. Tables and numerical results remain inspectable when tiles are blocked.\n\nShell installs/listing, retired Stamen/CARTO choices and the excluded local-video execution were replaced by browser-compatible preparation, Python file inspection and an external video continuation. Notebook 2 reads CSVs without Notebook 1 pickle outputs. The local pickle exercises remain, with output directories created before writes. Original source hashes/pins, historical data, markers, weighted-center calculations and credits are retained. The narrow deterministic adapter is recorded in each notebook\'s provenance metadata and catalog/source-library.json.'))
        if slug=='zarr-sql-views':cells.append(md('## LexCube source availability\n\nThe redistributed LexCube2.0.1 wheel retains its GPL notices. Its complete corresponding [upstream source archive](wheels/lexcube-2.0.1.tar.gz) is bundled locally beside the wheel; the manifest records the original archive path and exact hash. The source archive is a distribution/inspection resource and is never executed during import or build. Widget/extension requirements remain separate from the Atlas single-extension shell.'))
        if not sections:cells.append(md('## Source status\n\nNo source notebooks exist at this pin. NASA ARSET is README-only; Shiny is title-only; Gaborone supplies JupyterGIS project/data files rather than notebooks. The Atlas companion is original teaching material. No nonexistent source notebook, data payload or deployment is inferred.'))
        groups={'authored':'Complete authored lessons','compatibility':'Optional compatibility appendix'}
        for group,title in groups.items():
            selected=[s for s in sections if s['collection']==group]
            if not selected:continue
            rows=['## '+title,'','| Lesson | Runtime and requirements |','|---|---|']
            for s in selected:
                link=posixpath.relpath(s['notebook'],f'courses/{slug}')
                rows.append(f"| [{s['title'].replace('|','—')}]({link}) | **{s['runtime']['class']}**. {' '.join(s['runtime']['requirements'])} Verification: {s['verification']['status']}. |")
            cells.append(md('\n'.join(rows)))
        excluded=[d for d in library['dispositions'] if d['course']==slug and d['disposition']=='excluded']+[d for d in library['asset_exclusions'] if d['course']==slug]
        aliases=[d for d in library['dispositions'] if d['course']==slug and d['disposition']=='alias']
        cells.append(md('## Dependencies, rights and adaptations\n\nSource-local helpers and data retain original bytes and source hashes. Provider and software terms remain in `notices/` and beside data. Source code is not globally relicensed by the Atlas MIT/CC BY notices. Unclear optional media, restricted GADM, controlled inputs and rights-excluded climate legacy remain external. Legacy pickle outputs are not imported or unpickled: follow the source prerequisites to regenerate them. Full source hashes, link modifications, support inventory and exclusions are in catalog/source-library.json.\n\nImport-time status in the lesson table describes static ingestion. [Selected native execution receipts](https://github.com/jltobias/JupyterLite-Learning-Atlas/blob/main/catalog/source-execution.json) identify later fresh runs and explicit skips; native passing does not establish browser compatibility.\n\n'+f"{sum(s['course']==slug for s in library['support_files'])} local support-file placements. Open-license copyright and attribution notices are retained."))
        if aliases:cells.append(md('## Exact source aliases\n\n'+'\n'.join(f"- `{d['source_path']}` → [{Path(d['notebook']).name}]({posixpath.relpath(d['notebook'],f'courses/{slug}')}) — exact ordered cell-source duplicate." for d in aliases)))
        if excluded:cells.append(md('## Excluded files and external continuations\n\n'+'\n'.join(f"- [`{d['source_path']}`]({d['source_url']}) — {d['reason']}." for d in excluded)))
        refresh_managed_notebook(notebook,course['guide'],cells,kind='source-guide',data_status='source-specific',runtime='reading')
    refresh_managed_notebook(notebook,'notebook-library.ipynb',intro,kind='library',data_status='inventory metadata')
