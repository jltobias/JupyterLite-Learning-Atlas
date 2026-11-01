# JupyterLite Learning Atlas

**James L. Tobias / browser geospatial science, global health and shared decisions**

![An original illustrated globe connects browser notebooks, geographic evidence and people learning together.](assets/splash.svg)

A growing index of public JupyterLite projects, a Jupyter Book and a matching browser-executable JupyterLite Lab. Follow six paths through GIS, remote sensing, Earth observation, AI/ML, GeoAI/GeoML, global health and human-centered experiments. Every project has a distinct explained exercise, visual output, interpretation, extension and source citation.

**29 public JupyterLite-named repositories + 3 related browser projects / 32 project chapters / 41 canonical notebooks / no credentials for default exercises.** The public inventory was inspected on 2026-11-01. The four requested source repositories are now public and included; the refreshed discovery contains 58 public records. Original, revised and old editions remain distinct. The title-only Shiny repository is labeled a source stub. No sensitive health data are published.

## Read, run and explore

The source visibility changes are complete. GitHub Actions builds and publishes this index from `main`; see the [publication workflow](https://github.com/jltobias/JupyterLite-Index-Repo/actions/workflows/pages.yml) for the latest build and deployment status. Source companion availability is recorded independently.

Use the published entry points below. Availability follows the latest successful Pages deployment:

| Experience | Published link | What you do |
|---|---|---|
| Learning hub | [Open the atlas](https://jltobias.github.io/JupyterLite-Index-Repo/) | Choose a question and a learning path |
| Jupyter Book | [Read the Book](https://jltobias.github.io/JupyterLite-Index-Repo/book/index.html) | Read explanations and executed outputs |
| JupyterLite Lab | [Run the same notebooks](https://jltobias.github.io/JupyterLite-Index-Repo/lite/lab/index.html?path=index.ipynb) | Edit assumptions and run Python in a browser |
| Resource explorer | [Search the collection](https://jltobias.github.io/JupyterLite-Index-Repo/explore/) | Filter exact Book, Lab, 2D map, 3D map, scene and explorer links |
| Local teaching views | [2D map](https://jltobias.github.io/JupyterLite-Index-Repo/teach/?view=2d) / [3D map](https://jltobias.github.io/JupyterLite-Index-Repo/teach/?view=3d-map) / [3D scene](https://jltobias.github.io/JupyterLite-Index-Repo/teach/?view=3d-scene) | Change a water threshold on a fictional grid; compare interpretations |

For a local preview, build the site, run `python scripts/serve.py`, and open [localhost](http://localhost:8000/JupyterLite-Index-Repo/).

## Published companion experiences

These **existing source projects** returned HTTP 200 on 2026-11-01. Entry reachability does not verify every notebook path or interaction; their own dependencies and terms apply.

| Source experience | Verified source link |
|---|---|
| Rewiring Global Health Book | [Read the original course](https://jltobias.github.io/JupyterLite-Rewiring-Global-Health/) |
| Rewiring Global Health Lab | [Run the original lessons](https://jltobias.github.io/JupyterLite-Rewiring-Global-Health/lite/lab/index.html) |
| RustGIS companion 2D map | [Open the 2D map](https://jltobias.github.io/JupyterLite-RustGIS/maps/2d.html) |
| RustGIS companion 3D map | [Open the extruded 3D map](https://jltobias.github.io/JupyterLite-RustGIS/maps/3d.html) |
| RustGIS companion 3D scene | [Open the orbitable scene](https://jltobias.github.io/JupyterLite-RustGIS/maps/scene.html) |
| STAC resource explorer | [Discover source catalog metadata](https://jltobias.github.io/JupyterLite-STAC-Browser/explorer/) |

This index's entry points: [hub](https://jltobias.github.io/JupyterLite-Index-Repo/), [Book](https://jltobias.github.io/JupyterLite-Index-Repo/book/index.html), [Lab](https://jltobias.github.io/JupyterLite-Index-Repo/lite/lab/index.html?path=index.ipynb), [explorer](https://jltobias.github.io/JupyterLite-Index-Repo/explore/), and [local teaching views](https://jltobias.github.io/JupyterLite-Index-Repo/teach/). The workflow status records whether the latest revision has deployed successfully.

## Six connected paths

1. **Start with a browser:** Python foundations / original Shiny-stub prototype / [fit and evaluate a small model](content/foundations/learning-a-model.ipynb) / Data Visualization / PyScript / RustGIS.
2. **Read a map critically:** neighborhoods / inclusive distance buffers / layer contracts / aggregation / extract provenance; compare distinct original, revised and old public spatial-analysis editions.
3. **Observe a changing Earth:** procedural terrain / viewing geometry / Whitebox runtime boundary / STAC / Zarr/SQL.
4. **Rewire global health:** stakeholder priorities / burden denominators / HIVDB / climate/coastal services / mobility and community review.
5. **Inspect AI and decisions:** fitted models / Six Hats / structured JSON / spatial holdouts / evidence contracts / research discovery. Explore [design thinking, human-centered design and fail-fast iteration](content/foundations/evidence-ai.ipynb).
6. **Build a common picture:** World Monitor / WorldView / OSIRIS; verify uncertain signals before briefing.

## Rewiring Global Health in the Age of AI

The featured [source course](https://github.com/jltobias/JupyterLite-Rewiring-Global-Health) connects evidence, climate/STAC, 2D/3D GIS, GeoLibre, time, Zarr/SQL, GeoAI/world models, AI orchestration, digital twins and geoprivacy. Its [atlas chapter](content/projects/rewiring-global-health/index.ipynb) preserves **all ten original lesson run links** and adds a stakeholder-weighting exercise. The [synthesis notebook](content/synthesis/global-health.ipynb) connects the wider collection to privacy, empathy, human authority and reversible experimentation.

![An original evidence-to-action loop connects questions, provenance, analysis, community review and learning.](assets/evidence-to-action.svg)

Synthetic teaching results are not real health evidence, causal effects, treatment guidance or live AI outputs. Models, masked locations and encryption do not replace consent, validation or community review.

## Public project catalog

The links below open canonical notebooks on GitHub. The assembled Book and Lab use those exact notebooks. Source links lead to the actual repositories; immutable reviewed READMEs, resource types, status dates and limitations are in the [catalog](catalog/repositories.json). No hosted URL is guessed when a README lacks one. Shiny-Live-Apps contains only a title-only README; its atlas notebook is an original prototype, with no source app or source Lab claimed. The Maps-and-Spatial-Analyses README launcher is retained exactly and labeled HTTP 404 (2026-11-01). The other three new sources document no hosted launcher.

| Public JupyterLite source | Atlas exercise | Status |
|---|---|---|
| [JupyterLite-Data-Visualization](https://github.com/jltobias/JupyterLite-Data-Visualization) | [See the same evidence two ways](content/projects/data-visualization/index.ipynb) | learning companion |
| [JupyterLite-Shiny-Live-Apps](https://github.com/jltobias/JupyterLite-Shiny-Live-Apps) | [Prototype a reactive rule before an app](content/projects/shiny-live-apps/index.ipynb) | source stub |
| [JupyterLite-South-Sudan-Dashboard](https://github.com/jltobias/JupyterLite-South-Sudan-Dashboard) | [Service continuity as a dependency](content/projects/south-sudan-dashboard/index.ipynb) | learning companion |
| [JupyterLite-Spatial-Analysis](https://github.com/jltobias/JupyterLite-Spatial-Analysis) | [Neighborhoods change a summary](content/projects/spatial-analysis/index.ipynb) | synthetic methods edition |
| [JupyterLite-Maps-and-Spatial-Analyses](https://github.com/jltobias/JupyterLite-Maps-and-Spatial-Analyses) | [A buffer is a declared rule](content/projects/maps-and-spatial-analyses/index.ipynb) | map-centric edition |
| [JupyterLite-Geospatial-Analyses-and-Maps-old](https://github.com/jltobias/JupyterLite-Geospatial-Analyses-and-Maps-old) | [A teaching extract is not a census](content/projects/geospatial-analyses-and-maps-old/index.ipynb) | old edition |
| [JupyterLite-Geospatial-Analyses-and-Maps](https://github.com/jltobias/JupyterLite-Geospatial-Analyses-and-Maps) | [Overlay with an explicit layer contract](content/projects/geospatial-analyses-and-maps/index.ipynb) | original variant |
| [JupyterLite-Geospatial-Analyses-and-Maps-revised](https://github.com/jltobias/JupyterLite-Geospatial-Analyses-and-Maps-revised) | [Show what aggregation hides](content/projects/geospatial-analyses-and-maps-revised/index.ipynb) | revised variant |
| [JupyterLite-Global-Health-GIS](https://github.com/jltobias/JupyterLite-Global-Health-GIS) | [Weight burden without hiding assumptions](content/projects/global-health-gis/index.ipynb) | learning companion |
| [JupyterLite-HIVDB-Drug-Resistance-Maps](https://github.com/jltobias/JupyterLite-HIVDB-Drug-Resistance-Maps) | [Audit the surveillance denominator](content/projects/hivdb-drug-resistance-maps/index.ipynb) | learning companion |
| [JupyterLite-Whitebox](https://github.com/jltobias/JupyterLite-Whitebox) | [Trace downhill, then change runtimes](content/projects/whitebox/index.ipynb) | learning companion |
| [JupyterLite-AI-Agents-and-Orchestrator-Six-Thinking-Hats](https://github.com/jltobias/JupyterLite-AI-Agents-and-Orchestrator-Six-Thinking-Hats) | [Route perspectives before synthesis](content/projects/ai-agents-and-orchestrator-six-thinking-hats/index.ipynb) | learning companion |
| [JupyterLite-DRC-Population-Mobility-Border-Mapping](https://github.com/jltobias/JupyterLite-DRC-Population-Mobility-Border-Mapping) | [Flows are connections, not infections](content/projects/drc-population-mobility-border-mapping/index.ipynb) | learning companion |
| [JupyterLite-Geospatial-Research-Awareness-Radar](https://github.com/jltobias/JupyterLite-Geospatial-Research-Awareness-Radar) | [Rank leads without endorsing claims](content/projects/geospatial-research-awareness-radar/index.ipynb) | learning companion |
| [JupyterLite-World-Monitor-Prototype](https://github.com/jltobias/JupyterLite-World-Monitor-Prototype) | [Put freshness in the situation report](content/projects/world-monitor-prototype/index.ipynb) | learning companion |
| [JupyterLite-Astra-demos](https://github.com/jltobias/JupyterLite-Astra-demos) | [Procedural terrain, transparent assumptions](content/projects/astra-demos/index.ipynb) | learning companion |
| [JupyterLite-Gods-Eye-View-Satellite](https://github.com/jltobias/JupyterLite-Gods-Eye-View-Satellite) | [Inspect the viewing geometry](content/projects/gods-eye-view-satellite/index.ipynb) | learning companion |
| [JupyterLite-WorldView](https://github.com/jltobias/JupyterLite-WorldView) | [Allocate supplies with visible constraints](content/projects/worldview/index.ipynb) | learning companion |
| [JupyterLite-Custom-GPT-Six-Thinking-Hats](https://github.com/jltobias/JupyterLite-Custom-GPT-Six-Thinking-Hats) | [Validate a structured conversation](content/projects/custom-gpt-six-thinking-hats/index.ipynb) | learning companion |
| [JupyterLite-GeoLibre-GeoAI](https://github.com/jltobias/JupyterLite-GeoLibre-GeoAI) | [Check a spatial holdout](content/projects/geolibre-geoai/index.ipynb) | learning companion |
| [JupyterLite-GPT-6-Astra-Geospatial](https://github.com/jltobias/JupyterLite-GPT-6-Astra-Geospatial) | [Evaluate claims against a contract](content/projects/gpt-6-astra-geospatial/index.ipynb) | learning companion |
| [JupyterLite-zarr-sql-views](https://github.com/jltobias/JupyterLite-zarr-sql-views) | [Query a cube, account for the work](content/projects/zarr-sql-views/index.ipynb) | learning companion |
| [JupyterLite-Rewiring-Global-Health](https://github.com/jltobias/JupyterLite-Rewiring-Global-Health) | [Rewiring Global Health in the Age of AI](content/projects/rewiring-global-health/index.ipynb) | learning companion |
| [JupyterLite-Sea-Level-Rise](https://github.com/jltobias/JupyterLite-Sea-Level-Rise) | [Separate hazard from service impact](content/projects/sea-level-rise/index.ipynb) | learning companion |
| [JupyterLite-STAC-Browser](https://github.com/jltobias/JupyterLite-STAC-Browser) | [Discover assets without reading pixels](content/projects/stac-browser/index.ipynb) | learning companion |
| [JupyterLite-Climate-and-Health](https://github.com/jltobias/JupyterLite-Climate-and-Health) | [Count heat exposure, preserve uncertainty](content/projects/climate-and-health/index.ipynb) | learning companion |
| [JupyterLite-RustGIS](https://github.com/jltobias/JupyterLite-RustGIS) | [Export a small layer with a contract](content/projects/rustgis/index.ipynb) | learning companion |
| [JupyterLite-Osiris](https://github.com/jltobias/JupyterLite-Osiris) | [Turn signals into a reviewed brief](content/projects/osiris/index.ipynb) | learning companion |
| [JupyterLite-PyScript](https://github.com/jltobias/JupyterLite-PyScript) | [One data contract, two browser runtimes](content/projects/pyscript/index.ipynb) | learning companion |

## Related browser projects

These source READMEs explicitly describe JupyterLite/JupyterGIS material without a JupyterLite-prefixed name.

| Source | Atlas exercise | Source boundary |
|---|---|---|
| [JupyterGIS-StoryMap-Gaborone-TB-ABM](https://github.com/jltobias/JupyterGIS-StoryMap-Gaborone-TB-ABM) | [Storytelling needs a residual check](content/projects/jupytergis-storymap-gaborone-tb-abm/index.ipynb) | No published launch URL in README; source only |
| [Cross-Border-Ebola-Risk-Mapping-Prototype](https://github.com/jltobias/Cross-Border-Ebola-Risk-Mapping-Prototype) | [Sensitivity before a risk label](content/projects/cross-border-ebola-risk-mapping-prototype/index.ipynb) | No published launch URL in README; source only |
| [global-informal-settlements-storymap](https://github.com/jltobias/global-informal-settlements-storymap) | [A settlement label needs evidence](content/projects/global-informal-settlements-storymap/index.ipynb) | README links checked as indicated |

## Build and expand

```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements-build.txt
python scripts/generate.py
python scripts/validate.py
python scripts/execute.py --write
python scripts/build.py
python scripts/serve.py
```

Use Python 3.13. This pins the stable Jupyter Book v1/Sphinx renderer (maintenance mode) and JupyterLite stack; Node is unnecessary. First-time browser runtime downloads need network. Computations use bundled synthetic values or metadata; no learner package installs or remote data services. Native/GPU tools and live model providers have explicit separate continuation paths and trial limits in each relevant chapter. Download notebook edits to keep them; browser storage is not GitHub or a shared database.

To publish, set repository **Settings / Pages / Source: GitHub Actions**, then run the supplied workflow on `main`. Pull requests validate/build without deploying. Exactly four source visibility changes were authorized and completed; their public audit is in [catalog/public-visibility-changes.json](catalog/public-visibility-changes.json). Commits pushed to `main` run the [validation and deployment workflow](https://github.com/jltobias/JupyterLite-Index-Repo/actions/workflows/pages.yml). See [CONTRIBUTING.md](CONTRIBUTING.md) for catalog schema, preservation of manual notebook edits, build/preview commands, runtime limits and publication setup. See [VALIDATION.md](VALIDATION.md) for actual verification and remaining limits.

![The catalog's actual repository theme counts.](assets/repository-overview.svg)

## Citations, rights and provenance

[Full references](REFERENCES.md) / [Data provenance](DATA_SOURCES.md) / [Visual provenance](assets/PROVENANCE.md) / [Third-party notices](THIRD_PARTY_NOTICES.md) / [Citation metadata](CITATION.cff).

Original code is [MIT](LICENSE); original narrative, visuals, figures and synthetic fixtures are [CC BY 4.0](LICENSE-CONTENT.md). Source repositories, concepts, data, software distributions and linked works retain their own terms. Cite James L. Tobias and contributors (2026), *JupyterLite Learning Atlas*, plus the original projects/data used. Original SVGs are locally bundled, accessible and reproducible from `scripts/make_assets.py`; no third-party imagery is copied.
