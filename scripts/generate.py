"""Generate navigation and seed missing notebooks; never overwrite authored notebooks."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path
import yaml

from lesson_material import HEALTH_LESSONS, LESSONS, PATHS
from ocean_earth_material import CUBE_CODE, CUBE_INTRO, CUBE_INTERPRET, EARTH_LESSONS, earth_overview, ocean_overview
from coral_material import coral_overview
from phi_case_material import CASES as PHI_CASES, chapter_cells as phi_chapter_cells

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog/repositories.json"

HELPERS = '''from IPython.display import SVG, display
from html import escape

def svg(body, title, description, width=760, height=330):
    label = escape(title, quote=True)
    display(SVG(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{label}"><title>{escape(title)}</title><desc>{escape(description)}</desc><rect width="100%" height="100%" fill="#f5f5ef" rx="12"/>{body}</svg>'))

def bars(values, title, unit):
    print(title + ' | ' + unit + ':', {k:round(v,3) for k,v in values.items()})
    n = len(values)
    height = max(250, 82 + n*36)
    maximum = max(max(values.values()), 1)
    body = f'<text x="22" y="30" font-family="sans-serif" font-size="18" fill="#123c45">{escape(title)}</text>'
    for i,(key,value) in enumerate(values.items()):
        y=58+i*36
        body += f'<text x="22" y="{y+17}" font-family="sans-serif" font-size="13">{escape(str(key))}</text><rect x="205" y="{y}" width="{max(0,value)/maximum*440:.2f}" height="23" rx="3" fill="#16756b"/><text x="{213+max(0,value)/maximum*440:.2f}" y="{y+17}" font-family="sans-serif" font-size="13">{value:.2f}</text>'
    body += f'<text x="205" y="{height-15}" font-family="sans-serif" font-size="12">zero baseline · {escape(unit)}</text>'
    svg(body, title, 'Values are printed as a text alternative; consult the chart title for data status.', height=height)

def grid(values, columns, title):
    print(title + ':', [round(v,3) for v in values])
    maximum = max(max(values),1)
    size = 54
    body = f'<text x="22" y="30" font-family="sans-serif" font-size="18">{escape(title)}</text>'
    for i,v in enumerate(values):
        x=25+(i%columns)*size; y=52+(i//columns)*size
        light=92-50*v/maximum
        body += f'<rect x="{x}" y="{y}" width="50" height="50" fill="hsl(169,45%,{light:.1f}%)" stroke="#123c45"/><text x="{x+25}" y="{y+29}" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#061c21">{v:.1f}</text>'
    svg(body,title,'Synthetic grid with values printed in each cell; no actual boundaries.',height=max(220,70+((len(values)+columns-1)//columns)*size))

def lines(series, title, xunit, yunit):
    print(title + ':', {k:[round(v,3) for v in vs] for k,vs in series.items()})
    maximum=max(max(vs) for vs in series.values()) or 1
    body=f'<text x="22" y="30" font-family="sans-serif" font-size="18">{escape(title)}</text><path d="M55 55V265H710" fill="none" stroke="#123c45"/>'
    for j,(name,vs) in enumerate(series.items()):
        color=['#16756b','#a34712','#41449c'][j%3]
        pts=' '.join(f'{55+i*650/max(1,len(vs)-1):.1f},{265-v*200/maximum:.1f}' for i,v in enumerate(vs))
        body+=f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="3"/><text x="{60+j*220}" y="310" font-family="sans-serif" font-size="13" fill="{color}">{escape(name)}</text>'
    body+=f'<text x="55" y="288" font-family="sans-serif" font-size="12">{escape(xunit)} → · {escape(yunit)} ↑ · y starts at zero</text>'
    svg(body,title,'Synthetic series; printed values are the text alternative.')
'''


def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source.strip() + "\n"}


def code(source):
    metadata = {"tags": ["hide-input"], "jupyter": {"source_hidden": True}} if source == HELPERS else {}
    return {"cell_type": "code", "execution_count": None, "metadata": metadata, "outputs": [], "source": source.strip() + "\n"}


def notebook(path, cells, kind="foundation", **metadata):
    """Only create missing files. Canonical notebooks are always the authoring source."""
    target = ROOT / "content" / path
    if target.exists():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    for i, cell in enumerate(cells):
        cell["id"] = hashlib.sha256((str(path) + str(i)).encode()).hexdigest()[:12]
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python (Pyodide)", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.13"},
            "atlas": {"kind": kind, "data_status": "synthetic", **metadata},
        },
        "nbformat": 4, "nbformat_minor": 5,
    }
    target.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def health_table():
    base = "https://jltobias.github.io/JupyterLite-Rewiring-Global-Health/lite/lab/index.html?path="
    return "\n".join([
        "## The ten original lessons",
        "These links are transcribed from the actual source README, not reconstructed notebook names. They open the **source course**, whose runtime and terms are separate. The source course's title is *Rewiring Global Health for the Age of AI*.",
        "\n| Lesson | Investigation | Run original |\n|---|---|---|",
        *[f"| {n} · {title} | {desc} | [Run lesson {n}]({base}{filename}) |" for n,title,desc,filename in HEALTH_LESSONS],
        "\nThe source traces its concept to Tobias's 2013 Spatial Plexus presentation on wicked public-health problems and Ethan Zuckerman's *Rewire*. The atlas only cites that presentation through the source repository; it has not independently inspected the presentation. [Zuckerman's author page](https://ethanzuckerman.com/books/rewire/).",
    ])


def seed_project(r):
    if r['slug'] in PHI_CASES:
        notebook(r['notebook'], phi_chapter_cells(r, md, code, HELPERS), kind='project', repository=r['name'])
        return
    key = r["name"].removeprefix("JupyterLite-")
    item = LESSONS.get(key)
    if item is None:
        notebook(r["notebook"], [md(f'# {r["title"]}\n\nContributor scaffold: write and explain a distinct browser-safe exercise, visual, interpretation, extension and source citations. See the contributor guide.')], kind="project", repository=r["name"], scaffold=True)
        return
    title, theme, summary, question, method, exercise, interpretation, extension, limitation = item
    relative = "../../assets/"
    diagram = "evidence-to-action.svg" if theme == "Global health" else "empathy-iteration.svg" if theme == "AI & human decisions" else "capabilities.svg"
    source_links = "\n".join(f"- [{x['label']}]({x['url']}) — {x['description']} **{x['availability']}**"
                             for x in r["resources"] if key != "zarr-sql-views" or "?path=" not in x['url'])
    extra = (health_table() if key == "Rewiring-Global-Health" else
             ocean_overview() if key == "Global-Fishing-Watch-and-Dark-Vessels" else
             coral_overview() if key == "Coral-Reef-One-Health" else "")
    activity_context = ("It is an original prototype motivated only by a title-only source stub; no source Shiny app, source Lab or deployed service is supplied or verified."
                        if r["status"] == "source stub" else "It is a small companion to the source project, not a reproduction of that project's full course.")
    continuation = ("This source stub supplies no runtime or deployment instructions. Before any future app continuation, review actual application code, accessibility, dependencies and deployment evidence."
                    if r["status"] == "source stub" else "For native/GPU tools, use the source's local/server guide in an isolated environment, start with one small public/synthetic fixture, limit a trial to 5 minutes, and inspect memory, provider costs and outputs before scaling. For live models, use an approved authenticated backend with server-side secrets and a bounded single request; do not put credentials or sensitive records into a browser. Nothing in this chapter calls those services.")
    spatial_continuations = {
        "Spatial-Analysis": "Continue with the reviewed README's local JupyterLite build or GitHub Actions/Pages instructions. Its synthetic numpy/pandas/matplotlib notebooks avoid compiled GIS libraries; verify their behavior in the resulting browser build. No hosted launch URL is documented.",
        "Maps-and-Spatial-Analyses": "Continue with the reviewed README's local JupyterLite build or GitHub Actions/Pages instructions. Its Leaflet/OpenStreetMap iframe maps require external tiles and browser networking; retain their attribution and verify source map behavior separately. The documented root launcher returned HTTP 404 on 2026-11-01.",
        "Geospatial-Analyses-and-Maps-old": "Continue with the reviewed README's local JupyterLite build, including notebooks, data and spatial_lite.py. It documents the Python (Pyodide) kernel and numpy/pandas/matplotlib workflows that avoid compiled GIS stacks. Review each teaching extract's provenance and terms before reuse; no hosted launch URL is documented.",
    }
    if key in spatial_continuations:
        continuation = f"{spatial_continuations[key]} [Reviewed source README]({r['readme_url']})."
    if key == "Coral-Reef-One-Health":
        continuation = "For a continuation, inspect each provider's product metadata, version, observation dates, requested citation and permissions; source entry checks do not validate service functions. The original local exercise uses only standard-library Python and IPython display."
    cells = [
        md(f"# {title}\n\n**{theme} · 15–25 minutes · {r['status']}**\n\n{summary}\n\n**Learning question:** {question}\n\nThis original index activity is **synthetic teaching analysis**. It uses invented values or authored metadata, no real people or sensitive locations, no remote APIs, and no AI model calls. {activity_context}\n\n![Learning workflow]({relative}{diagram})\n\nOriginal atlas diagram, James L. Tobias and contributors, CC BY 4.0; see [asset provenance](../../visual-provenance.ipynb)."),
        md(f"## Predict before running\n\n{method}\n\nWrite a prediction and one assumption you would need to check. Run cells in order with **Shift+Enter**, or **Run → Run All Cells**. The next cell defines only local SVG display helpers; the following cell performs the analysis. Every graphic also prints its values as a text alternative."),
        code(HELPERS), code(exercise),
        md(f"## Interpret the result\n\n{interpretation}\n\nName the result, the assumption producing it, and one conclusion it cannot support. These are not clinical findings, causal effects or live model outputs.\n\n## Change one thing\n\n{extension}\n\nSave a copy with **File → Save and Export Notebook As → Notebook** (or the file browser's Download command). Browser storage is local to this browser/profile; it is not a GitHub commit or shared database."),
        md(extra) if extra else md(f"## Connect the idea\n\nCompare this activity with another chapter on the same [learning path](../../index.ipynb). Keep the question, data status and interpretation visible when transferring a method."),
        md(f"## Sources, continuation and limits\n\n**Source repository:** [{r['name']}]({r['source_url']}).\n\n**Source README:** [reviewed immutable version]({r['readme_url']}); inspected {r['inspected_on']}, commit `{r['source_commit'][:12]}`. Repository content and linked works keep their original terms. Summaries and exercises here are newly authored.\n\n{limitation}\n\n{source_links or 'No exact published launch URL is documented in this README. Use the repository source; hosted availability is unverified.'}\n\n**Runtime budget:** this default is fewer than 100 values and normally completes within seconds; allow 60 seconds per cell while first loading Python. {continuation}\n\n[Central references](../../references.ipynb) · [Contribute](../../contributor-guide.ipynb)"),
    ]
    if key == "zarr-sql-views":
        cells[0] = md(cells[0]["source"].replace(summary, r["summary"]))
        cells[6] = md(cells[6]["source"].replace(limitation, r["limitations"]))
        cells[5:5] = [md(CUBE_INTRO), code(CUBE_CODE), md(CUBE_INTERPRET), md(earth_overview(EARTH_LESSONS))]
    notebook(r["notebook"], cells, kind="project", repository=r["name"])


def seed_foundations(records):
    path_links = []
    prefixed_count = sum(r["category"] == "jupyterlite" for r in records)
    related_count = sum(r["category"] == "related" for r in records)
    known = {r["name"].removeprefix("JupyterLite-"): r for r in records}
    for title, subtitle, keys in PATHS:
        links = " → ".join(f"[{known[k]['title']}]({known[k]['notebook']})" for k in keys if k in known)
        path_links.append(f"### {title}\n\n{subtitle}.\n\n{links}")
    notebook("index.ipynb", [
        md(f"# The JupyterLite Learning Atlas\n\n**James L. Tobias · a browser, a question, a world to explore**\n\n![The learning atlas: geography, notebooks and shared decisions](assets/splash.svg)\n\nDiscover **{len(records)} public projects**: {prefixed_count} core JupyterLite-named repositories by jltobias plus {related_count} related browser/teaching projects (three prior related and four external PHI cases). Each has an original, small companion exercise. Read this Book, then run the same chapter notebooks in the bundled Lab. No account, API key, desktop GIS or data-service connection is required for these defaults. The four source visibility changes are complete; GitHub Actions builds and publishes this index from `main`; see the [workflow status](https://github.com/jltobias/JupyterLite-Learning-Atlas/actions/workflows/pages.yml) for deployment results.\n\nStart with [browser Python](foundations/browser-python.ipynb), [1854 Cholera Basic](projects/cholera-1854-basic/index.ipynb), [spatial thinking](foundations/spatial-thinking.ipynb), and [evidence, AI and empathy](foundations/evidence-ai.ipynb). The Book displays executed outputs; the Lab lets you change assumptions.\n\nAll local exercises use synthetic values or authored teaching metadata. They do not estimate real health outcomes or reproduce a source model. External companion projects can have different data, dependencies, credentials and licenses."),
        md("## Choose a route\n\n" + "\n\n".join(path_links)),
        md("## Rewiring Global Health in the Age of AI\n\nThe [featured course chapter](projects/rewiring-global-health/index.ipynb) preserves links to all ten source lessons. The [cross-project synthesis](synthesis/global-health.ipynb) connects observation, assumptions, privacy, empathy and accountable review.\n\n![Evidence to action](assets/evidence-to-action.svg)\n\nOriginal atlas diagrams: James L. Tobias and contributors, CC BY 4.0. [Visual provenance](visual-provenance.ipynb).\n\n## A useful workshop rhythm\n\nPredict → run → interpret → change one assumption → discuss who benefits or could be harmed → save a decision record. Treat a vivid map as a question worth examining, not proof.\n\n[Contributor guide](contributor-guide.ipynb) · [References](references.ipynb)"),
        code(HELPERS), code("counts = {}\nfor theme in "+repr([r['theme'] for r in records])+":\n    counts[theme] = counts.get(theme,0)+1\nbars(counts, 'Public catalog themes — repository metadata', 'repositories')"),
        md("The chart counts catalog records. It measures neither source quality nor the relative importance of these disciplines. All public JupyterLite records in the checked discovery snapshot, except this index, have one matching project chapter."),
    ], data_status="repository metadata")
    notebook("foundations/browser-python.ipynb", [
        md("# Your first browser experiment\n\n**Foundations · 15 minutes**\n\nJupyterLite runs Python through Pyodide/WebAssembly in your browser. First load needs a network connection to fetch the runtime. Once loaded, these exercises read no external data; a fresh fully offline browser is not guaranteed to start.\n\nOpen a notebook, wait for **Python (Pyodide)**, and run with **Shift+Enter**. Restart the kernel and Run All to check reproducibility. Files and edits live in browser storage; download valuable work before clearing browser data or changing browser profiles. This index uses its own storage namespace.\n\n**Question:** How does a threshold change the summary of an invented dataset?"),
        code(HELPERS), code("observations = [2,4,4,6,9]\nthreshold = 5\nprint('Synthetic observations:', observations)\nprint('Mean:', sum(observations)/len(observations))\nbars({'below':sum(x<threshold for x in observations), 'at or above':sum(x>=threshold for x in observations)}, 'Your first synthetic comparison', 'observations')"),
        md("## Interpret and try\n\nThree invented observations are below 5 and two are at or above it. Change the threshold to 4 and predict the result before running. A programming error, a bad assumption and an unsupported interpretation are different problems.\n\nIf no kernel appears, allow runtime downloads, wait for startup, and reload once; use the static Book while troubleshooting. No package installation is needed inside these lessons. Do not upload sensitive records.\n\n![Browser and continuation capabilities](../assets/capabilities.svg)\n\nOriginal diagram, CC BY 4.0. [Provenance](../visual-provenance.ipynb).\n\n**References:** [JupyterLite](https://jupyterlite.readthedocs.io/en/stable/) and [Pyodide](https://pyodide.org/en/stable/). Their runtime downloads and libraries retain their terms. [Next: 1854 Cholera Basic](../projects/cholera-1854-basic/index.ipynb) · [Spatial thinking](spatial-thinking.ipynb)."),
    ])
    notebook("foundations/spatial-thinking.ipynb", [
        md("# Ask a spatial question\n\n**Foundations · 20 minutes**\n\nA map combines values, geometry, scale, projection and design choices. Before mapping, ask what was measured, where, when, with which units and for whom. Longitude/latitude degrees are not a uniform distance unit. Counts need denominators before comparing rates.\n\n**Question:** Can the nearest location change when distance follows a network? Compare straight-line and grid-route distance for fictional points in arbitrary planar units."),
        code(HELPERS), code("from math import hypot\npoints = {'A':(3,4),'B':(0,6),'C':(4,4)}\neuclidean = {k:hypot(x,y) for k,(x,y) in points.items()}\ngrid_route = {k:abs(x)+abs(y) for k,(x,y) in points.items()}\nprint('Straight-line:', euclidean, '\\nGrid route:',grid_route)\nbars(grid_route, 'Synthetic route length on an orthogonal grid', 'planar units')"),
        md("## Interpret and extend\n\nA is nearest by straight-line distance; B is nearest by an orthogonal route. Actual travel also depends on roads, crossings, transport, time, cost and exclusion. Change one coordinate and compare both rankings.\n\nDo not label this arbitrary grid as a country or administrative boundary. Spatial uncertainty and aggregation can change a decision. [Explore overlay](../projects/geospatial-analyses-and-maps/index.ipynb) and [metadata discovery](../projects/stac-browser/index.ipynb).\n\n**Source context:** [GISGeography's Periodic Table for Spatial Analysis](https://gisgeography.com/spatial-analysis-periodic-table/) inspires several linked source collections; the diagram and exercise here are original. [STAC specification overview](https://stacspec.org/en/about/stac-spec/)."),
    ])
    notebook("foundations/evidence-ai.ipynb", [
        md("# Evidence, AI and human agency\n\n**Foundations · 20 minutes**\n\nAn observation, a prediction, an assumed scenario and a causal claim need different support. A model output or generated explanation is not automatically verified evidence. Ask who supplied the data, who is missing, who decides, and who can challenge a conclusion.\n\n![Empathy and iteration](../assets/empathy-iteration.svg)\n\nOriginal diagram, CC BY 4.0; [provenance](../visual-provenance.ipynb).\n\n**Question:** Does an apparently complete checklist conceal a missing stakeholder? Count authored review roles. This is metadata analysis, not a measure of participation quality."),
        code(HELPERS), code("review = {'analyst':2, 'service worker':1, 'community representative':0, 'privacy steward':1}\nprint('Missing voices:', [k for k,n in review.items() if n==0])\nbars(review, 'Fictional review participation', 'review entries')"),
        md("## Interpret and extend\n\nThe community role has no entry. Adding a name or counting attendance is insufficient: participation requires meaningful influence, context and the possibility of disagreement. Write one open question you would ask before choosing a tool.\n\nUse small reversible prototypes, invite critique, record changes and revisit assumptions. Protect privacy by minimizing data and precision rather than relying only on masking or encryption.\n\n**Sources:** [IDEO.org Design Kit methods](https://www.designkit.org/methods.html), [WHO (2021), Ethics and governance of AI for health](https://www.who.int/publications/i/item/9789240029200), [Edward de Bono, Six Thinking Hats](https://www.debono.com/Books/six-thinking-hats). These concepts inform the original exercise and are not reproduced frameworks or endorsed deployments. [Continue to the synthesis](../synthesis/global-health.ipynb)."),
    ])
    notebook("synthesis/global-health.ipynb", [
        md("# From geographic evidence to a shared health decision\n\n**Global Health synthesis · 30 minutes**\n\nA useful chain connects observation → data contract → inspectable analysis → uncertainty → community review → action → learning. A failure anywhere can undermine a persuasive map. The [Rewiring Global Health chapter](../projects/rewiring-global-health/index.ipynb) links all ten actual lessons; this synthesis connects the wider collection.\n\n![Evidence to action with a feedback loop](../assets/evidence-to-action.svg)\n\nOriginal diagram, CC BY 4.0; [provenance](../visual-provenance.ipynb).\n\nUse [STAC metadata](../projects/stac-browser/index.ipynb) to ask what a dataset represents; [GIS weighting](../projects/global-health-gis/index.ipynb) to expose denominators; [HIVDB](../projects/hivdb-drug-resistance-maps/index.ipynb) to avoid invalid aggregation; [climate](../projects/climate-and-health/index.ipynb) and [coastal services](../projects/sea-level-rise/index.ipynb) to separate hazards from outcomes; [GeoAI](../projects/geolibre-geoai/index.ipynb) to question transfer; and [Six Hats](../projects/ai-agents-and-orchestrator-six-thinking-hats/index.ipynb) to expose missing perspectives.\n\n**Question:** What happens when a project passes technical checks but has not completed community or privacy review?"),
        code(HELPERS), code("checks = {'data contract':True,'reproducible analysis':True,'uncertainty stated':True,'privacy review':False,'community review':False}\nprint('Ready for accountable decision review:', all(checks.values()))\nprint('Outstanding:', [k for k,ok in checks.items() if not ok])\nbars({k:int(v) for k,v in checks.items()}, 'Fictional project review state — not a health finding', 'check completed')"),
        md("## Interpret, then design the next experiment\n\nTechnical checks alone leave two review steps unresolved. This small checklist cannot certify safety or substitute for an institution's governance. Its purpose is to make unfinished work visible.\n\nDraft a decision record with a question, data/provenance, competing explanations, who may be affected, data minimization, a reversible prototype, a stopping rule, reviewer names/roles, review date and a way to contest the result. Use fictional or consented non-sensitive workshop material.\n\nAn AI explanation should preserve source context and uncertainty. A world model is a representation with assumptions, not a validated twin of a community. Encryption protects a payload under specific assumptions; it cannot repair consent or an inappropriate release. Empathy means listening and giving affected people authority, including the authority to reject a proposed intervention.\n\n**Sources:** [source course README](https://github.com/jltobias/JupyterLite-Rewiring-Global-Health/blob/main/README.md), [WHO AI governance](https://www.who.int/publications/i/item/9789240029200), [IDEO.org Design Kit](https://www.designkit.org/methods.html), [Zuckerman's Rewire](https://ethanzuckerman.com/books/rewire/). [Central references](../references.ipynb)."),
    ])
    notebook("contributor-guide.ipynb", [md((ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8"))])
    notebook("visual-provenance.ipynb", [md((ROOT / "assets/PROVENANCE.md").read_text(encoding="utf-8"))])
    refs = (ROOT / "REFERENCES.md").read_text(encoding="utf-8")
    notebook("references.ipynb", [md(refs)])


def make_toc(records):
    """Build structured navigation so arbitrary valid titles cannot break YAML."""
    by_slug = {r['slug']: r for r in records}
    early = ['projects/cholera-1854-basic/index'] if 'cholera-1854-basic' in by_slug else []
    parts=[{'caption':'Start here','chapters':[{'file':path} for path in [
        'foundations/browser-python', *early, 'foundations/spatial-thinking','foundations/learning-a-model',
        'foundations/evidence-ai','synthesis/global-health']]}]
    investigations = [by_slug[slug] for slug in PHI_CASES if slug != 'cholera-1854-basic' and slug in by_slug]
    if investigations:
        parts.append({'caption':'Outbreak investigations','chapters':[
            {'file':r['notebook'].removesuffix('.ipynb'), 'title':r['title']} for r in investigations]})
    for theme in dict.fromkeys(r['theme'] for r in records if r['category']=='jupyterlite'):
        parts.append({'caption':theme,'chapters':[
            {'file':r['notebook'].removesuffix('.ipynb'),
             'title':f"{r['name'].removeprefix('JupyterLite-')} - {r['title']}"}
            for r in records if r['theme']==theme and r['category']=='jupyterlite']})
    parts.append({'caption':'Related browser projects','chapters':[
        {'file':r['notebook'].removesuffix('.ipynb'),'title':f"{r['name']} - {r['title']}"}
        for r in records if r['category']=='related' and r['slug'] not in PHI_CASES]})
    parts.append({'caption':'Keep exploring','chapters':[{'file':path} for path in [
        'contributor-guide','references','visual-provenance']]})
    return {'format':'jb-book','root':'index','parts':parts}


def main():
    records = json.loads(CATALOG.read_text(encoding="utf-8"))["repositories"]
    seed_foundations(records)
    for r in records:
        seed_project(r)
    assets = ROOT / "content/assets"
    assets.mkdir(parents=True, exist_ok=True)
    for p in (ROOT / "assets").glob("*"):
        if p.is_file():
            shutil.copyfile(p, assets / p.name)
    (ROOT / "content/_toc.yml").write_text(yaml.safe_dump(make_toc(records),sort_keys=False,allow_unicode=True),encoding='utf-8')
    data_dir = ROOT / "site/data"
    data_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(CATALOG, data_dir / "catalog.json")
    print(f"Generated navigation for {len(records)} projects. Existing notebooks preserved.")


if __name__ == "__main__":
    main()
