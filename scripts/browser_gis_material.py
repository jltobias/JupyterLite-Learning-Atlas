"""Original cross-book browser GIS content and conflict-aware Markdown ownership."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
from urllib.parse import quote
from browser_gis_recipes import CSV_RECIPE, RETURN_RECIPE

ROOT = Path(__file__).resolve().parents[1]
OWNER = 'atlas-browser-gis-pathways'
NAVIGATION_NOTEBOOKS = ('index.ipynb','foundations/browser-python.ipynb','foundations/spatial-thinking.ipynb',
    'foundations/evidence-ai.ipynb','foundations/learning-a-model.ipynb','synthesis/global-health.ipynb')


def refresh_current_scope(root=ROOT):
    """Refresh only current managed GIS counts, preserving historical prose."""
    import nbformat
    root=Path(root)
    catalog=json.loads((root/'catalog/repositories.json').read_text(encoding='utf-8'))
    library=json.loads((root/'catalog/source-library.json').read_text(encoding='utf-8'))
    start='<!-- BROWSER_GIS_PATHWAYS:START -->';end='<!-- BROWSER_GIS_PATHWAYS:END -->'
    for name in ['README.md','REFERENCES.md']:
        path=root/name
        if not path.exists():continue
        text=path.read_text(encoding='utf-8')
        if start not in text:continue
        assert text.count(start)==text.count(end)==1,'Ambiguous managed browser GIS block'
        before,rest=text.split(start,1);block,after=rest.split(end,1)
        block=re.sub(r'\*\*\d+ project chapters and \d+ source-course guides\*\*',
            f"**{len(catalog['repositories'])} project chapters and {len(library['courses'])} source-course guides**",block)
        block=re.sub(r'The \d+ imported source lessons',f"The {len(library['sections'])} imported source lessons",block)
        updated=before+start+block+end+after
        if updated!=text:path.write_text(updated,encoding='utf-8',newline='\n')
    path=root/'content/references.ipynb';source=root/'REFERENCES.md'
    if path.exists() and source.exists():
        nb=nbformat.read(path,4);text=source.read_text(encoding='utf-8')
        if nb.cells[0].source!=text:
            nb.cells[0].source=text;nbformat.write(nb,path)


def load_pathways(root=ROOT):
    return json.loads((root/'catalog/browser-gis-pathways.json').read_text(encoding='utf-8'))


def relative_link(notebook, target):
    return posixpath.relpath(target, str(PurePosixPath(notebook).parent))


def pathway_markdown(profile, notebook):
    def link(label, target):
        if PurePosixPath(target).suffix == '.ipynb':
            return f'[{label}]({relative_link(notebook,target)})'
        # Non-TOC Markdown is an input/notice, not a rendered Book document.
        kind='tree' if (ROOT/'content'/target).is_dir() else 'blob'
        url=f'https://github.com/jltobias/JupyterLite-Learning-Atlas/{kind}/main/content/{quote(target,safe="/")}'
        return f'[{label}]({url}) (`{target}`)'
    sources = ' · '.join(link(item['label'], item['path']) for item in profile['source_links'])
    return '\n'.join([
        '## Browser GIS pathway', '',
        f"**Geographic question:** {profile['question']}", '',
        f"**Data readiness ({profile['route']}):** {profile['data_readiness']}", '',
        '**Start from the chapter evidence:** ' + sources, '',
        f"- **[RustGIS Web](https://web.rustgis.app/):** {profile['rustgis_task']}",
        f"- **[GeoLibre Web](https://web.geolibre.app/):** {profile['geolibre_task']}", '',
        '**Handoff:** Use the ' + link('GIS workbench', 'gis-workbench.ipynb') +
        ' to validate/export an attributed WGS84 layer. Download the GeoJSON, method record and review prompt from `exports/`, then import through the chosen app’s file picker. Compare `_atlas_source_id` (or source `GEOID`) with the original IDs; app-generated internal IDs may differ. Return changed results by explicit upload. Apps and the notebook share no files or kernel state. Practice-only Census data remain Fresno 2020, never this subject’s observations.', '',
        f"**Optional AI prompt (approved subject evidence only):** “{profile['ai_prompt']} Cite supplied feature IDs/fields, separate observations from assumptions, abstain when evidence is missing, and propose one falsifiable check.” For the common practice package, use its generated schema/summary prompt instead. A human-written answer completes the same task.", '',
        f"**GeoAI opportunity:** {profile['geoai_extension']} Any later fitted exercise must name target/features and spatial/temporal support, reserve a spatial/temporal holdout, inspect leakage and uncertainty, and state evidence that would disprove the interpretation. Styling, thresholds, schema checks and chat alone are not model fitting.", '',
        f"**Human evidence check:** {profile['evidence_check']} Ask the intended reader which decision the map supports; change one legend, filter or annotation, then recheck interpretation against the same IDs and values.", '',
        '**Continue:** ' + link('cross-tool guide and optional Ollama setup', 'browser-gis.ipynb') + ' · ' +
        link('RustGIS assistance', 'courses/rustgis/07_ollama_assistance.ipynb') + ' · ' +
        link('GeoLibre setup', 'courses/geolibre-geoai/18_ollama_geolibre_setup.ipynb') + ' · ' +
        link('chat-to-map', 'courses/geolibre-geoai/19_ollama_chat_to_map.ipynb') + ' · ' +
        link('evidence review', 'courses/geolibre-geoai/20_ollama_evidence_review.ipynb') +
        '. AI is optional; no service or model is called by this pathway.', '',
    ])


def reconcile_markdown(path, source, key, report=print):
    """Touch only an exact owner/key/hash match; never adopt legacy cell IDs."""
    nb = json.loads(path.read_text(encoding='utf-8'))
    owned = [c for c in nb['cells'] if c.get('metadata',{}).get('atlas_browser_gis',{}).get('owner') == OWNER
             and c['metadata']['atlas_browser_gis'].get('key') == key]
    if len(owned) > 1:
        report(f'CONFLICT browser GIS: duplicate managed blocks preserved: {path}')
        return 'conflict'
    source = source.strip()+'\n'
    digest = lambda value: hashlib.sha256(value.encode('utf-8')).hexdigest()
    if owned:
        cell = owned[0]
        old = cell.get('source','')
        if isinstance(old,list): old=''.join(old)
        if cell.get('cell_type') != 'markdown' or digest(old) != cell['metadata']['atlas_browser_gis'].get('generated_sha256'):
            report(f'CONFLICT browser GIS: edited managed block preserved: {path}')
            return 'conflict'
        if old == source:
            return 'unchanged'
        cell['source'] = source
        cell['metadata']['atlas_browser_gis']['generated_sha256'] = digest(source)
    else:
        cell = {'cell_type':'markdown','id':'gis-'+digest(key)[:16],
                'metadata':{'atlas_browser_gis':{'owner':OWNER,'key':key,'generated_sha256':digest(source)}},'source':source}
        if any(c.get('id') == cell['id'] for c in nb['cells']):
            report(f'CONFLICT browser GIS: unowned stable ID preserved: {path}')
            return 'conflict'
        nb['cells'].append(cell)
    path.write_text(json.dumps(nb,indent=1,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
    return 'updated'


def navigation_markdown(notebook):
    return '## Continue through browser GIS\n\n'+ ' · '.join(
        f'[{label}]({relative_link(notebook,target)})' for label,target in [
            ('Browser GIS and optional AI','browser-gis.ipynb'),('Real-data GIS workbench','gis-workbench.ipynb')]) + \
        '\n\nEvery project companion and source-course guide has a subject-specific pathway for RustGIS and GeoLibre. Keep geometry, units, dates, source terms and missingness visible. AI is optional; use manual file download/import and human evidence review. Common Fresno Census practice is separate from other subject observations.\n'


def expected_pathway_blocks(profiles):
    for profile in profiles:
        for notebook in (f"projects/{profile['slug']}/index.ipynb", f"courses/{profile['slug']}/index.ipynb"):
            yield notebook,'subject:'+profile['slug'],pathway_markdown(profile,notebook)
    for notebook in NAVIGATION_NOTEBOOKS:
        yield notebook,'navigation:'+notebook,navigation_markdown(notebook)


def validate_pathway_blocks(root=ROOT, profiles=None):
    for notebook,key,source in expected_pathway_blocks(load_pathways(root)['pathways'] if profiles is None else profiles):
        nb=json.loads((root/'content'/notebook).read_text(encoding='utf-8'))
        cells=[c for c in nb['cells'] if c.get('metadata',{}).get('atlas_browser_gis',{}).get('owner')==OWNER]
        assert len(cells)==1, f'Browser GIS ownership count differs: {notebook}'
        cell=cells[0];actual=cell['source'] if isinstance(cell['source'],str) else ''.join(cell['source'])
        managed=cell['metadata']['atlas_browser_gis']
        assert cell['cell_type']=='markdown' and managed.get('key')==key and \
            managed.get('generated_sha256')==hashlib.sha256(actual.encode('utf-8')).hexdigest() and \
            actual==source.strip()+'\n', f'Browser GIS block differs/was edited; review and reconcile manually: {notebook}'


def reconcile_pathways(root=ROOT, report=print):
    return {notebook:reconcile_markdown(root/'content'/notebook,source,key,report)
            for notebook,key,source in expected_pathway_blocks(load_pathways(root)['pathways'])}


def seed_browser_gis(notebook, md, code):
    notebook('browser-gis.ipynb', [
        md('''# Browser GIS, evidence and optional AI

Use [RustGIS Web](https://web.rustgis.app/) or [GeoLibre Web](https://web.geolibre.app/) to inspect a result you can explain and reproduce. Both are separate applications. The same original notebooks appear in the Book and Lab; every project companion and course guide offers a subject-specific route. Imported source lessons retain their exact source/runtime handoffs.

![A manual evidence loop from notebook to GIS and human review](assets/browser-gis-workflow.svg)

Original Atlas visual, James L. Tobias and contributors, CC BY 4.0. [Visual provenance](visual-provenance.ipynb).

**Start:** run the [real-data GIS workbench](gis-workbench.ipynb). Its default is the bundled Fresno 2020 Census snapshot: 166 whole intersecting tracts, 764468 people. A bounded chosen subset is practice in data transfer, not evidence about another chapter's location or health outcome. For other real families, use the [Map and Scene Atlas](https://jltobias.github.io/JupyterLite-Learning-Atlas/teach/) and its source-sample exports, then explicitly upload an attributed GeoJSON and metadata into Lab.'''),
        md('''## Carry evidence across two applications

1. Inspect source terms, geographic meaning, CRS/axis order, time, units, missing values and stable IDs. Select an explicit small set and record the full input versus output counts.
2. Run the workbench. Download all three files from its `exports/` directory: GeoJSON, `.metadata.json` and `.review.md`. In Lab, right-click each file and choose **Download**. A downloaded notebook also needs the linked [helper](atlas_gis_handoff.py), [pathway catalog](assets/browser-gis-pathways.json) and declared inputs; preserve their relative paths.
3. Open the chosen GIS in a separate tab. Use **Add Data** and the local file picker, or a documented drop workflow. A launch link transfers no data. Local notebook paths/blob URLs are not public URLs; no app reads the notebook's variables or filesystem.
4. Inspect extent, count, one known `_atlas_source_id`/value/unit/source, zero/null and the legend. The helper adds this primitive string from the retained GeoJSON `Feature.id`; compare it (or the original `GEOID`) across apps. App-generated internal IDs may differ. In RustGIS compare a selected feature and table; in GeoLibre compare the same attributes and classification. Record any omitted field/geometry. Save app projects and exported data separately: GeoJSON, `.geolibre.json` and `.rgis` are different artifacts.
5. Keep originals. Save changed outputs under a new name and upload through Lab's file browser for separate returned-artifact inspection using the [workbench recipe](gis-workbench.ipynb). Returned Atlas exports retain reserved provenance fields and intentionally cannot enter the fresh-input loader. A successful import demonstrates transfer, not scientific validity.

Use the table/printed summary if a hosted app, basemap, CDN, GPU or optional assistant is unavailable. Browser edits live in this browser/profile: download valuable work. Large rasters, native tools, credentials and source-only services follow their existing runtime routes; never install native `rustgis` into Pyodide.'''),
        md('''## Optional assistant in your chosen GIS

The exercise is complete without AI. A manual or pasted answer uses the same evidence checklist. No notebook here probes a server, installs software, pulls a model, configures a service, stores credentials, uploads data or calls inference.

If you independently choose an already running Ollama service with an actually installed **tool-capable** model, configure the selected GIS app using its official instructions:

| Setting | GeoLibre Web | RustGIS Web |
|---|---|---|
| Assistant | Processing → AI Assistant | Analyze → AI Assistant |
| Native provider | Settings → AI Providers → Ollama | Assistant model/gear → Ollama (local) |
| Native base URL/address | `http://localhost:11434`; provider normalizes `/v1` | OpenAI-compatible address, usually `http://localhost:11434/v1` |
| Custom OpenAI-compatible base | Full `http://localhost:11434/v1` | Full `http://localhost:11434/v1` |
| Requesting page origin | `https://web.geolibre.app` | `https://web.rustgis.app` |

An operator who independently enables hosted-app access must allow the exact requesting origin in `OLLAMA_ORIGINS`; supporting both uses `https://web.geolibre.app,https://web.rustgis.app`. The Atlas/docs URL or a `/user-guide/` path is not the GIS origin. Self-hosted apps require their own exact scheme/host/port. Keep the server loopback-only; broad binds and wildcard origins are unnecessary. Browser/OS local-network permission is separate from CORS and can still deny access; use manual analysis if unavailable. Do not disable browser security.

Localhost describes an endpoint, not where inference runs. Ollama cloud models/routing/search can send data elsewhere. A local-only claim requires actual local inference with no cloud/search/router path. Hosted providers may receive field **values and tool results**, not merely schema; maps/basemaps/data services can have independent network traffic. Runtime licenses do not license model weights or datasets.

Official guidance inspected 2026-11-13: [GeoLibre assistant and Ollama](https://github.com/opengeos/GeoLibre/blob/2189afea6cef078577a2200b358a7dfcf40762f6/docs/user-guide/ai-assistant.md), [RustGIS assistant](https://github.com/opengeos/RustGIS/blob/4d6d0d0f2323bdcac0c40bed2e286df92f7287d3/docs/user-guide/assistant.md), [Ollama FAQ](https://github.com/ollama/ollama/blob/5632619189ab493c70bd3f9435214b8788cc1c80/docs/faq.mdx), [Ollama OpenAI compatibility](https://github.com/ollama/ollama/blob/5632619189ab493c70bd3f9435214b8788cc1c80/docs/api/openai-compatibility.mdx), [Chrome local-network permissions](https://developer.chrome.com/blog/local-network-access). These documentary pins do not pin the evolving hosted apps. See [central citations and separate rights](references.ipynb).'''),
        md('''## Inspect what actually happened

Use only a tiny public/synthetic or otherwise approved package. Ask for a bounded review of supplied IDs/fields or proposed parameter values. Inspect the assistant's tool transcript, SQL, selected layers, filters, CRS, units, extent and output count; independently reproduce a known calculation. A fluent answer cannot establish that the right operation ran. Never run generated Python, JavaScript, shell commands or arbitrary URLs from an answer. GIS undo does not reverse file/network side effects; some generated-code paths bypass app undo.

Record app/version, model/tag and whether inference was local, timestamp, exact prompt, evidence summary, reply, corrections and human disposition. Validate proposed IDs against the actual allowlist and parameters against declared bounds before recomputing. Keep sensitive data out of optional prompts. A failed service connection never blocks the core GIS lesson.

Try without a model: audit the deliberately flawed claim, “The highest mapped tract population proves the highest individual disease risk today.” Name the missing exposure/outcome evidence, time mismatch and denominator error. Then ask your map's intended reader what action it supports, revise one legend or annotation, and check whether the same evidence is understood more accurately.'''),
        md('''## GeoAI is a separate analytical step

Thresholds, weighted indices, schema validation, projection, map styling and chat are described by their actual operation. Fitted GeoAI requires a declared target/features/support, appropriate spatial/temporal validation, leakage controls, uncertainty and evidence that could falsify the interpretation.

Continue with the preserved [GeoLibre 22 DBSCAN bridge](courses/geolibre-geoai/22_rustgis_geoai_bridge.ipynb) (20 invented points, explicitly synthetic fitted ML), the [spatial holdout companion](projects/geolibre-geoai/index.ipynb), [RustGIS bridge](courses/rustgis/03_rustgis_bridge.ipynb), [Population real exports and oracle](courses/population-data-comparison/03_real_exports.ipynb), and [OneHealth tract joins](courses/onehealth/07_eo_population_joins.ipynb). These exact source continuations retain their original pins/runtime requirements; links add no new compatibility certification.

Optional source teaching: [RustGIS assistance 07](courses/rustgis/07_ollama_assistance.ipynb), [GeoLibre setup 18](courses/geolibre-geoai/18_ollama_geolibre_setup.ipynb), [chat-to-map 19](courses/geolibre-geoai/19_ollama_chat_to_map.ipynb) and [evidence review 20](courses/geolibre-geoai/20_ollama_evidence_review.ipynb).'''),
    ], data_status='original guidance; no inference or automatic data transfer')
    notebook('gis-workbench.ipynb', [
        md('''# Real-data GIS export and evidence workbench

**Question:** What survives an explicit, attributed transfer into two browser GIS apps?

Run all cells to inspect real **Fresno 2020 Census whole-tract** population and export a deterministic small selection. The complete bundled input contains **166 tracts / 764468 people**; these are whole intersecting tracts, not a clipped AOI headcount. The default exports the first 12 source IDs meeting the declared threshold. It is never relabeled as another chapter's data.

This notebook calls no models/services and needs no native GIS. Its [original standard-library helper](atlas_gis_handoff.py) validates structural 2D WGS84 geometry, declared attribution, units, IDs and finite values; it cannot certify topology or source authenticity. Download it with this notebook for use outside Atlas and keep the declared relative inputs. [Cross-tool and optional Ollama guide](browser-gis.ipynb).'''),
        code('''import json
import sys
from pathlib import Path
from IPython.display import display, FileLink
from atlas_gis_handoff import load_input, census_metadata, summarize, write_handoff

# Canonical files, published/staged with this notebook; no network fetching.
manifest_path = Path('courses/onehealth/data/manifest.json')
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
metadata = census_metadata(manifest)
input_path = Path('courses/onehealth/data/tracts.geojson')
id_field = 'GEOID'
pathways = json.loads(Path('assets/browser-gis-pathways.json').read_text(encoding='utf-8'))
print('Subject pathways available:', len(pathways['pathways']))
'''),
        md('''## Choose an input honestly

For your own **already geographic, approved** file, upload it and an attributed metadata JSON through Lab's file browser, then explicitly replace `input_path`, `metadata` and `id_field` above. The metadata must declare `dataset_id`, `title`, `observation_status`, `observation_time` (or explicitly unknown), `input_crs`, longitude/latitude `coordinate_order`, `field_units`, `method`, `missingness_policy`, `limitations` and separate `sources` records (`source_id`, `source_url`, `attribution`, `license_statement`, `license_evidence`). Copy actual source terms/metadata, including NC-SA, per-source limits, date and method; do not reuse the Census declaration. EPSG:4326 additionally needs documented `axis_order_evidence`. Original collection metadata, source properties and geometry survive in the package.

These fresh-input instructions exclude app-returned Atlas packages: retain their protected provenance and use the separate returned-artifact inspection recipe below; do not strip reserved fields or silently restore IDs.

An existing Map and Scene Atlas source-sample export is eligible after this same metadata review. Choose the intended subject field below; never use the Fresno population field as a substitute for cholera, reef, climate or clinical observations. Unknown/projected CRS, 3D coordinates, null geometry, malformed or antimeridian/polar polygons stop this route with an actionable error. Preserve unmapped records as a table and follow the source workflow; no silent repair, geocoding, reprojection or dimensional reduction occurs.'''),
        code('''collection, input_record = load_input(input_path, metadata, id_field=id_field)
input_summary = summarize(collection, metadata['field_units'])
print('Actual input SHA-256:', input_record['sha256'])
print('Input feature count:', input_summary['feature_count'])
print('Declared measurements:', input_summary['measurements'])
if metadata['dataset_id'] == 'fresno-census-2020-tracts':
    assert input_summary['feature_count'] == 166
    assert input_summary['measurements']['POP100']['numeric_sum'] == 764468
print('Bounded preview:', json.dumps(input_summary['preview'], indent=2))
'''),
        md('''## Change a parameter, predict, then export

Change `minimum_value` or `selection_limit` and predict which **actual IDs** change. Selection retains source order and does not clip geometry. Null, absent, zero, false and empty string are accounted separately. Empty selection is valid. For another dataset, set its actual field/units and appropriate selection rule explicitly.

Exports are under this notebook's `exports/` directory in Lab. Identical reruns retain identical files; changed results need a **new `output_stem`** so valuable previous work is preserved. The package stores exact selected/excluded IDs, input byte SHA, original metadata, source terms, measurement summary and output SHA. The helper binds the normalized loaded collection to its receipt to catch accidental edits; it does not authenticate the source. Its `max_bytes` limit covers the combined UTF-8 GeoJSON, method JSON and review Markdown; complete provenance is retained or the package fails before writing.'''),
        code('''measurement_field = 'POP100'
minimum_value = 0
selection_limit = 12
output_stem = 'fresno-2020-first12'
assert measurement_field in metadata['field_units'], 'Choose a declared measurement and units.'
assert type(selection_limit) is int and 0 <= selection_limit <= 100, 'Use a bounded explicit selection.'
eligible = [f for f in collection['features']
            if type(f['properties'].get(measurement_field)) in (int, float)
            and f['properties'][measurement_field] >= minimum_value]
selected_ids = [f['id'] for f in eligible[:selection_limit]]
run_metadata = dict(metadata)
run_metadata['selection_parameters'] = {'measurement_field': measurement_field,
    'minimum_value': minimum_value, 'selection_limit': selection_limit,
    'rule': 'numeric value >= minimum; first eligible source IDs in source order'}
package = write_handoff(collection, run_metadata, input_record, Path('exports'),
                        output_stem, selected_ids=selected_ids)
print('Export selection:', package['method']['selection'])
print('Selected measurements:', package['method']['summary']['measurements'])
if sys.platform == 'emscripten':
    for artifact in package['paths'].values():
        display(FileLink(str(artifact)))
else:
    print('Artifact names:', ', '.join(artifact.as_posix() for artifact in package['paths'].values()))
    print('Run this notebook in Lab to create and download these artifacts; saved Book output does not publish temporary exports.')
print(package['review'])
'''),
        md('''## Import, inspect and return

Download all three linked artifacts (or right-click in Lab's `exports/` folder → **Download**). Open [RustGIS Web](https://web.rustgis.app/) or [GeoLibre Web](https://web.geolibre.app/) separately, use **Add Data / file picker**, then inspect count, extent and a known `_atlas_source_id`/value/unit/source. The helper adds this primitive string from the retained GeoJSON `Feature.id`; compare it (or the original `GEOID`) across apps. App-generated internal IDs may differ. Compare the same population legend in both; a selected-tract sum remains a whole-tract sum. Record missing fields and keep the original files. Export changes under a new name, then explicitly upload into Lab for further review. The tabs share no kernel state or files.

The generated `.review.md` contains a prompt grounded in this actual package's schema/summary, an intentionally flawed claim and a human checklist. It is visible text, not a model reply. Review manually or use the [optional assistant guidance](browser-gis.ipynb); no inference is required. Ask a prospective map reader which decision it supports, revise one legend/annotation, and retest. Preserve rights for source data, software, model weights, basemaps and your own outputs separately.

Subject continuations: [OneHealth join](courses/onehealth/07_eo_population_joins.ipynb), [Population exports/oracle](courses/population-data-comparison/03_real_exports.ipynb), [RustGIS bridge](courses/rustgis/03_rustgis_bridge.ipynb) and [synthetic fitted DBSCAN](courses/geolibre-geoai/22_rustgis_geoai_bridge.ipynb). Their inputs/runtime/pins remain separate; the shared exporter does not decode rasters, fit these models or certify native branches.'''),
        md(CSV_RECIPE), md(RETURN_RECIPE),
    ], data_status='real bundled Census aggregates; explicit bounded selection')
