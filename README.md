# JupyterLite Learning Atlas

**James L. Tobias / browser geospatial science, global health and shared decisions**

![The JupyterLite Learning Atlas: an open notebook becomes a coastal landscape and coral reef, with an Earth globe, satellite and people learning together.](assets/splash-v2.png)

*AI-generated conceptual illustration. [Generation prompt, provenance and credits](assets/SPLASH-PROVENANCE.md).*

This repository is now **[JupyterLite-Learning-Atlas](https://github.com/jltobias/JupyterLite-Learning-Atlas)**, renamed on 2 November 2026. [Repository identity record](catalog/repository-rename.json). Its live Book and Lab use the updated links below.

A growing index of public JupyterLite projects, a Jupyter Book and a matching browser-executable JupyterLite Lab. Follow six paths through GIS, remote sensing, Earth observation, AI/ML, GeoAI/GeoML, global health and human-centered experiments. Every project has a distinct explained exercise, visual output, interpretation, extension and source citation.

**31 core public JupyterLite-named repositories by jltobias + 3 prior related browser projects + 4 external PHI teaching cases / 38 project chapters / 47 canonical notebooks (44 with code, 3 narrative) / no credentials for default exercises.** The public inventory was inspected on 2026-11-01; Coral Reef One Health was added through a targeted source review on 2026-11-02. Four external PHI-Case-Studies courses were added through targeted review on 2026-11-02. Discovery now contains 64 public records; existing records were retained without full reinspection. The four requested source repositories remain public and included. Original, revised and old editions remain distinct. The title-only Shiny repository is labeled a source stub. No sensitive health data are published.

## Read, run and explore

The source visibility changes are complete. GitHub Actions builds and publishes this index from `main`; see the [publication workflow](https://github.com/jltobias/JupyterLite-Learning-Atlas/actions/workflows/pages.yml) for the latest build and deployment status. Source companion availability is recorded independently.

Use the published entry points below. Availability follows the latest successful Pages deployment:

| Experience | Published link | What you do |
|---|---|---|
| Learning hub | [Open the atlas](https://jltobias.github.io/JupyterLite-Learning-Atlas/) | Choose a question and a learning path |
| Jupyter Book | [Read the Book](https://jltobias.github.io/JupyterLite-Learning-Atlas/book/index.html) | Read explanations and executed outputs |
| JupyterLite Lab | [Run the same notebooks](https://jltobias.github.io/JupyterLite-Learning-Atlas/lite/lab/index.html?path=index.ipynb) | Edit assumptions and run Python in a browser |
| Resource explorer | [Search the collection](https://jltobias.github.io/JupyterLite-Learning-Atlas/explore/) | Filter exact Book, Lab, 2D map, 3D map, scene and explorer links |
| Local teaching views | [2D map](https://jltobias.github.io/JupyterLite-Learning-Atlas/teach/?view=2d) / [3D map](https://jltobias.github.io/JupyterLite-Learning-Atlas/teach/?view=3d-map) / [3D scene](https://jltobias.github.io/JupyterLite-Learning-Atlas/teach/?view=3d-scene) | Change a water threshold on a fictional grid; compare interpretations |

For a local preview, build the site, run `python scripts/serve.py`, and open [localhost](http://localhost:8000/JupyterLite-Learning-Atlas/).


## PHI outbreak learning sequence

Start with browser Python, then take Basic as the Book's second learning chapter. Continue through Advanced1 and Advanced2, followed by MDR-TB. The four sources belong to **PHI-Case-Studies**, not the 31 core jltobias repositories.

| Case | Read in the live Book | Run matching atlas Lab | Canonical notebook | Original source |
|---|---|---|---|---|
| 1854 Cholera Basic: dots, counts and centres | [Read](https://jltobias.github.io/JupyterLite-Learning-Atlas/book/projects/cholera-1854-basic/index.html) | [Run](https://jltobias.github.io/JupyterLite-Learning-Atlas/lite/lab/index.html?path=projects/cholera-1854-basic/index.ipynb) | [Source](content/projects/cholera-1854-basic/index.ipynb) | [PHI course](https://github.com/PHI-Case-Studies/Jupyterlite-1854-Cholera-Basic) |
| 1854 Cholera Advanced1: routes and reachable nodes | [Read](https://jltobias.github.io/JupyterLite-Learning-Atlas/book/projects/cholera-1854-advanced-1/index.html) | [Run](https://jltobias.github.io/JupyterLite-Learning-Atlas/lite/lab/index.html?path=projects/cholera-1854-advanced-1/index.ipynb) | [Source](content/projects/cholera-1854-advanced-1/index.ipynb) | [PHI course](https://github.com/PHI-Case-Studies/Jupyterlite-1854-Cholera-Outbreak-London-Advanced-1) |
| 1854 Cholera Advanced2: nearest sites, ties and buildings | [Read](https://jltobias.github.io/JupyterLite-Learning-Atlas/book/projects/cholera-1854-advanced-2/index.html) | [Run](https://jltobias.github.io/JupyterLite-Learning-Atlas/lite/lab/index.html?path=projects/cholera-1854-advanced-2/index.ipynb) | [Source](content/projects/cholera-1854-advanced-2/index.ipynb) | [PHI course](https://github.com/PHI-Case-Studies/1854-Cholera-Outbreak-London-Advanced-2) |
| 2005 MDR-TB Thailand: contact evidence and unknown results | [Read](https://jltobias.github.io/JupyterLite-Learning-Atlas/book/projects/mdr-tb-thailand-2005/index.html) | [Run](https://jltobias.github.io/JupyterLite-Learning-Atlas/lite/lab/index.html?path=projects/mdr-tb-thailand-2005/index.ipynb) | [Source](content/projects/mdr-tb-thailand-2005/index.ipynb) | [PHI course](https://github.com/PHI-Case-Studies/2005-MDR-TB-Outbreak-Thailand) |

The atlas companions run original small synthetic calculations with no package installs, external data, tiles, APIs or Binder builds. Basic and Advanced1 link separately checked source JupyterLite courses; Advanced2 and MDR-TB link native/server source continuations. Dated source GET checks establish reachability, not source execution. Exact source notebook paths, creators, commits, primary works and rights follow below.

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

This index's entry points: [hub](https://jltobias.github.io/JupyterLite-Learning-Atlas/), [Book](https://jltobias.github.io/JupyterLite-Learning-Atlas/book/index.html), [Lab](https://jltobias.github.io/JupyterLite-Learning-Atlas/lite/lab/index.html?path=index.ipynb), [explorer](https://jltobias.github.io/JupyterLite-Learning-Atlas/explore/), and [local teaching views](https://jltobias.github.io/JupyterLite-Learning-Atlas/teach/). The workflow status records whether the latest revision has deployed successfully.

## Six connected paths

1. **Start with a browser:** Python foundations / original Shiny-stub prototype / [fit and evaluate a small model](content/foundations/learning-a-model.ipynb) / Data Visualization / PyScript / RustGIS.
2. **Read a map critically:** neighborhoods / inclusive distance buffers / layer contracts / aggregation / extract provenance; compare distinct original, revised and old public spatial-analysis editions.
3. **Observe a changing Earth:** procedural terrain / viewing geometry / Whitebox runtime boundary / STAC / Ocean Watch / [Coral Reef One Health](content/projects/coral-reef-one-health/index.ipynb) / Zarr/SQL and Earth studios.
4. **Rewire global health:** stakeholder priorities / reef ecosystems and community questions / burden denominators / HIVDB / climate/coastal services / mobility and community review.
5. **Inspect AI and decisions:** fitted models / Six Hats / structured JSON / spatial holdouts / evidence contracts / research discovery. Explore [design thinking, human-centered design and fail-fast iteration](content/foundations/evidence-ai.ipynb).
6. **Build a common picture:** World Monitor / WorldView / OSIRIS; verify uncertain signals before briefing.

## Rewiring Global Health in the Age of AI

The featured [source course](https://github.com/jltobias/JupyterLite-Rewiring-Global-Health) connects evidence, climate/STAC, 2D/3D GIS, GeoLibre, time, Zarr/SQL, GeoAI/world models, AI orchestration, digital twins and geoprivacy. Its [atlas chapter](content/projects/rewiring-global-health/index.ipynb) preserves **all ten original lesson run links** and adds a stakeholder-weighting exercise. The [synthesis notebook](content/synthesis/global-health.ipynb) connects the wider collection to privacy, empathy, human authority and reversible experimentation.

![An original evidence-to-action loop connects questions, provenance, analysis, community review and learning.](assets/evidence-to-action.svg)

Synthetic teaching results are not real health evidence, causal effects, treatment guidance or live AI outputs. Models, masked locations and encryption do not replace consent, validation or community review.

## Public project catalog

The links below open canonical notebooks on GitHub. The assembled Book and Lab use those exact notebooks. Source links lead to the actual repositories; immutable reviewed READMEs, resource types, status dates and limitations are in the [catalog](catalog/repositories.json). No hosted URL is guessed: a reviewed README or an explicitly observed pinned deployment workflow/published manifest must support it. Shiny-Live-Apps contains only a title-only README; its atlas notebook is an original prototype, with no source app or source Lab claimed. The Maps-and-Spatial-Analyses README launcher is retained exactly and labeled HTTP 404 (2026-11-01). The other three sources from the earlier visibility-change milestone document no hosted launcher.

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
| [JupyterLite-Global-Fishing-Watch-and-Dark-Vessels](https://github.com/jltobias/JupyterLite-Global-Fishing-Watch-and-Dark-Vessels) | [Observe vessels, preserve uncertainty](content/projects/global-fishing-watch-and-dark-vessels/index.ipynb) | learning companion |
| [JupyterLite-Rewiring-Global-Health](https://github.com/jltobias/JupyterLite-Rewiring-Global-Health) | [Rewiring Global Health in the Age of AI](content/projects/rewiring-global-health/index.ipynb) | learning companion |
| [JupyterLite-Sea-Level-Rise](https://github.com/jltobias/JupyterLite-Sea-Level-Rise) | [Separate hazard from service impact](content/projects/sea-level-rise/index.ipynb) | learning companion |
| [JupyterLite-STAC-Browser](https://github.com/jltobias/JupyterLite-STAC-Browser) | [Discover assets without reading pixels](content/projects/stac-browser/index.ipynb) | learning companion |
| [JupyterLite-Climate-and-Health](https://github.com/jltobias/JupyterLite-Climate-and-Health) | [Count heat exposure, preserve uncertainty](content/projects/climate-and-health/index.ipynb) | learning companion |
| [JupyterLite-RustGIS](https://github.com/jltobias/JupyterLite-RustGIS) | [Export a small layer with a contract](content/projects/rustgis/index.ipynb) | learning companion |
| [JupyterLite-Osiris](https://github.com/jltobias/JupyterLite-Osiris) | [Turn signals into a reviewed brief](content/projects/osiris/index.ipynb) | learning companion |
| [JupyterLite-PyScript](https://github.com/jltobias/JupyterLite-PyScript) | [One data contract, two browser runtimes](content/projects/pyscript/index.ipynb) | learning companion |
| [JupyterLite-Coral-Reef-One-Health](https://github.com/jltobias/JupyterLite-Coral-Reef-One-Health) | [Coral Reef One Health: maps, evidence and priorities](content/projects/coral-reef-one-health/index.ipynb) | learning companion |

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

To publish, set repository **Settings / Pages / Source: GitHub Actions**, then run the supplied workflow on `main`. Pull requests validate/build without deploying. Exactly four source visibility changes were authorized and completed; their public audit is in [catalog/public-visibility-changes.json](catalog/public-visibility-changes.json). Commits pushed to `main` run the [validation and deployment workflow](https://github.com/jltobias/JupyterLite-Learning-Atlas/actions/workflows/pages.yml). See [CONTRIBUTING.md](CONTRIBUTING.md) for catalog schema, preservation of manual notebook edits, build/preview commands, runtime limits and publication setup. See [VALIDATION.md](VALIDATION.md) for actual verification and remaining limits.

![The catalog's actual repository theme counts.](assets/repository-overview.svg)

## Citations, rights and provenance

[Full references](REFERENCES.md) / [Data provenance](DATA_SOURCES.md) / [Visual provenance](assets/PROVENANCE.md) / [Third-party notices](THIRD_PARTY_NOTICES.md) / [Citation metadata](CITATION.cff).

Original code is [MIT](LICENSE); original narrative, visuals, figures and synthetic fixtures are [CC BY 4.0](LICENSE-CONTENT.md). Source repositories, concepts, data, software distributions and linked works retain their own terms. Cite James L. Tobias and contributors (2026), *JupyterLite Learning Atlas*, plus the original projects/data used. Original SVGs are locally bundled, accessible and reproducible from `scripts/make_assets.py`; no third-party imagery is copied.

## Ocean Watch and Earth studios: sources and attribution

The new [Ocean Watch chapter](content/projects/global-fishing-watch-and-dark-vessels/index.ipynb) retains ambiguity in an original synthetic AIS–SAR candidate screen and links all nine source notebooks. [Zarr/SQL](content/projects/zarr-sql-views/index.ipynb) keeps its chunk exercise and adds interval/missing-coverage accounting, with all thirty source lessons and representative studio views. Neither fixture copies source data or runs source SQL or LexCube. Activity is not catch, stock, disease or proof of illegal fishing; embeddings, predicted fields and conditional projections require independent interpretation.

- **Source courses:** James L. Tobias / jltobias (2026), *Ocean Watch: Fishing, Dark Vessels & One Health*, [commit `145a73e500cb`](https://github.com/jltobias/JupyterLite-Global-Fishing-Watch-and-Dark-Vessels/blob/145a73e500cb06070f399a040206802cc279174e/README.md); and *Earth in the Browser*, [commit `9a191f1fd30c`](https://github.com/jltobias/JupyterLite-zarr-sql-views/blob/9a191f1fd30c40e09b48b9f92a9b5fdd9676509e/README.md). The Earth course builds on [dzole0311's *Zarr SQL Views*](https://github.com/dzole0311/zarr-sql-views) (ISC); its original lessons/artwork remain ISC. Full [Ocean sources](https://github.com/jltobias/JupyterLite-Global-Fishing-Watch-and-Dark-Vessels/blob/145a73e500cb06070f399a040206802cc279174e/content/sources.md) and [Earth credits](https://github.com/jltobias/JupyterLite-zarr-sql-views/blob/9a191f1fd30c40e09b48b9f92a9b5fdd9676509e/book/credits.md) retain provider terms.
- **Ocean research:** Paolo, F. S., Kroodsma, D., Raynor, J., et al. (2024), *Satellite mapping reveals extensive industrial activity at sea*, Nature **625**, 85–91, [paper](https://doi.org/10.1038/s41586-023-06825-8). Paolo, Kroodsma, Davis & Hochberg's [analysis-data deposit](https://doi.org/10.6084/m9.figshare.24309475.v4), version 4, covers 2017–2021 and is **CC BY 4.0**. This differs from GFW's inspected [platform terms](https://globalfishingwatch.org/terms-of-use/), **CC BY-NC 4.0**; follow each product's metadata. [NOAA NCEI OISST v2.1](https://www.ncei.noaa.gov/products/optimum-interpolation-sst), [Copernicus Sentinel-1 RTC / Microsoft Planetary Computer](https://planetarycomputer.microsoft.com/dataset/sentinel-1-rtc) and [Natural Earth (public domain)](https://www.naturalearthdata.com/about/terms-of-use/) are credited source-course inputs, not copied index inputs. The source also credits [FAO's 2025 marine fishery assessment](https://www.fao.org/newsroom/detail/fao-releases-the-most-detailed-global-assessment-of-marine-fish-stocks-to-date) and [ICEYE's dark-vessel discussion](https://www.iceye.com/blog/dark-vessels-in-northern-europe-and-how-iceyes-satellites-find-them); no report graphics or vendor imagery are reproduced. [WHO/OHHLEP One Health principles](https://www.who.int/publications/m/item/one-health-definitions-and-principles) frame the ecosystem/health questions.
- **SeasFire:** Alonso, L., Gans, F., Karasante, I., et al. (2024), *SeasFire Cube*, **v0.4**, [dataset](https://doi.org/10.5281/zenodo.13834057), **CC BY 4.0**; Karasante et al. (2025), *SeasFire cube — a multivariate dataset for global wildfire modeling*, Scientific Data **12**, 368, [paper](https://doi.org/10.1038/s41597-025-04546-3). Credit the SeasFire consortium/ESA, [JRC/GWIS](https://gwis.jrc.ec.europa.eu/), [ECMWF/Copernicus ERA5](https://doi.org/10.24381/cds.adbb2d47), [NASA MODIS MOD13C1 v6](https://doi.org/10.5067/MODIS/MOD13C1.006) and ESA EarthCODE/CloudFerro.
- **LexCube:** Söchting, M., Scheuermann, G., Montero, D., & Mahecha, M. D. (2025), *Interactive Earth system data cube visualization in Jupyter notebooks*, Big Earth Data **9(2)**, **321–335**, [paper](https://doi.org/10.1080/20964471.2025.2471646). [LexCube **2.0.1**](https://github.com/msoechting/lexcube), Maximilian Söchting and contributors, **GPL-3.0-or-later**; credit RSC4Earth/Leipzig University and ESA DeepESDL/DFG NFDI4Earth. [Source-course adaptation/source/license](https://jltobias.github.io/JupyterLite-zarr-sql-views/vendor/lexcube/README.md). This index embeds no LexCube binaries; source ISC does not replace GPL.
- **Global FTW:** Robinson, C., Muhawenayo, G., Khanal, S., et al. (2026), *The first global agricultural field boundary map at 10 m resolution*, [arXiv:2605.11055](https://doi.org/10.48550/arXiv.2605.11055). [Global Fields of the World](https://source.coop/ftw/global-data), alpha **2024/2025**, **CC BY 4.0**: Taylor Geospatial and collaborators, Microsoft AI for Good, participating universities, Copernicus Sentinel-2, Source Cooperative/Radiant Earth. Predictions do not establish parcels or ownership.
- **TESSERA:** Feng, Z., et al. (2025; revised 2026), *TESSERA: Temporal Embeddings of Surface Spectra for Earth Representation and Analysis*, [arXiv:2506.20380](https://doi.org/10.48550/arXiv.2506.20380). Credit TESSERA/University of Cambridge, dClimate inference/hosting and GeoTessera contributors. Source data **v1.1 / dClimate** are explicitly **CC0** under the [terms](https://github.com/ucam-eo/tessera/blob/master/aup.md); legacy inconsistent CC-BY wording is retained upstream and ethical guidance is advisory. GeoTessera code is MIT.
- **AR6:** Garner et al. (2021), *IPCC AR6 Sea Level Projections*, **v20210809**, [dataset](https://doi.org/10.5281/zenodo.5914709), **CC BY 4.0**; Fox-Kemper et al. (2021), WG1 Chapter 9, [DOI](https://doi.org/10.1017/9781009157896.011); Kopp et al. (2023), *FACTS v1.0*, GMD **16**, 7461–7489, [DOI](https://doi.org/10.5194/gmd-16-7461-2023). Credit the projection authors, supporting funders and NASA Sea Level Change Team; retain the [pinned Rutgers guide](https://github.com/Rutgers-ESSP/IPCC-AR6-Sea-Level-Projections/tree/8ee75128d8f6d9a8ba9825f47c92d11955d0651e). Scenarios have no assigned probabilities; workflow percentiles are not the assessed p-box.

These datasets, code, pixels, model weights and source graphics are **linked, not bundled**. Index fixtures and SVGs are original (CC BY 4.0); original executable code is MIT. See [REFERENCES.md](REFERENCES.md), [DATA_SOURCES.md](DATA_SOURCES.md) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for the rights/use distinctions and complete provider references. No institutional endorsement is implied.


The [Coral Reef One Health chapter](content/projects/coral-reef-one-health/index.ipynb) adds an original two-descriptor weighting exercise: complete evidence, explicit missingness and weight sensitivity. Its teaching index is not validated health or conservation advice. Three mapping initiatives and four external research tools connect maps to field and community evidence; no external data or artwork is copied.

## Coral Reef One Health: citations and rights (2026-11-02)

- **Tobias, James L. / jltobias (2026).** *Coral Reef One Health*. [Reviewed README](https://github.com/jltobias/JupyterLite-Coral-Reef-One-Health/blob/6b76d79a9b4b683a52bbf0ba019f204e7635aaf9/README.md), commit `6b76d79a9b4b683a52bbf0ba019f204e7635aaf9`, inspected 2026-11-02. [Mapping guide](https://github.com/jltobias/JupyterLite-Coral-Reef-One-Health/blob/6b76d79a9b4b683a52bbf0ba019f204e7635aaf9/book/mapping-initiatives.md), [One Health guide](https://github.com/jltobias/JupyterLite-Coral-Reef-One-Health/blob/6b76d79a9b4b683a52bbf0ba019f204e7635aaf9/book/one-health.md), [research guide](https://github.com/jltobias/JupyterLite-Coral-Reef-One-Health/blob/6b76d79a9b4b683a52bbf0ba019f204e7635aaf9/book/research-resources.md) and [source references](https://github.com/jltobias/JupyterLite-Coral-Reef-One-Health/blob/6b76d79a9b4b683a52bbf0ba019f204e7635aaf9/book/references.md) informed the selection. **No repository-wide license selected**: no source code, dataset, prose, artwork or splash is copied.
- **Allen Coral Atlas / Arizona State University Center for Global Discovery and Conservation Science and partners.** [Atlas](https://allencoralatlas.org/), [methods](https://allencoralatlas.org/methods/) and [Terms of Use](https://allencoralatlas.org/tou/). Credit Paul Allen's Vulcan, Planet, Coral Reef Alliance and University of Queensland. Shallow habitat classes depend on product, depth and water visibility; they are not direct live coral cover or household health. Website terms and product permissions are separate; no blanket CC BY grant is asserted.
- **Khaled bin Sultan Living Oceans Foundation (KSLOF).** [Mapping the World's Coral Reefs](https://www.livingoceansfoundation.org/mapping-the-worlds-coral-reefs/) and [World Reef Map](https://maps.lof.org/). Expedition habitat/bathymetry mapping combines satellite and field evidence, with NASA collaboration; selected sites are not continuous global monitoring. Viewing and the provider's data-request permissions are separate.
- **NASA Landsat / University of South Florida Institute for Marine Remote Sensing (IMaRS).** [*Landsat 7 Worldwide Inventory of Coral Reefs Completed*](https://landsat.gsfc.nasa.gov/wp-content/uploads/2012/07/coral-l7.pdf), historical Millennium mapping context using 1999–2002 imagery. [IMaRS project](https://imars.usf.edu/millennium-corals/) and [UNEP-WCMC global reef compilation record](https://data-gis.unep-wcmc.org/portal/home/item.html?id=0613604367334836863f5c0c10e452bf) are continuation links: obtain the actual product version, contributors, requested citation and terms from current provider metadata. A release date is not every feature's observation date.
- **World Health Organization.** [One Health](https://www.who.int/health-topics/one-health), for integrated people/animal/ecosystem inquiry and shared governance. **Sweet, Michael; Burian, Alfred; Bulling, Mark (2021).** *Corals as canaries in the coalmine: Towards the incorporation of marine ecosystems into the 'One Health' concept*. Journal of Invertebrate Pathology **186**, 107538. [DOI](https://doi.org/10.1016/j.jip.2021.107538) · [PubMed PMID 33545133](https://pubmed.ncbi.nlm.nih.gov/33545133/). Indexed abstract and bibliographic metadata inspected; full text not inspected. The arbitrary atlas index does not implement or validate their proposed framework.
- **NOAA.** [Coral reef ecosystems](https://www.noaa.gov/education/resource-collections/marine-life/coral-reef-ecosystems), ecosystem-services and cultural context; no photographs or clinical findings copied. The evidence plan here is an original interpretation, not a reproduced WHO or NOAA diagram.
- **luismmontilla and contributors.** [Awesome coral research](https://github.com/luismmontilla/awesome-coral-research), discovery directory, [CC BY 4.0 license](https://github.com/luismmontilla/awesome-coral-research/blob/master/LICENCE.md). Credit the directory's selection; this atlas selects four links with newly authored descriptions and copies no full directory or image. Provider terms remain separate.
- **NOAA Coral Reef Watch.** [Satellite monitoring/products](https://coralreefwatch.noaa.gov/satellite/index.php): temperature, heat stress and bleaching alerts are distinct from field bleaching observations. **MERMAID team / Wildlife Conservation Society.** [MERMAID](https://datamermaid.org/): standardized field survey collection, exploration and management. **CoralNet team.** [CoralNet](https://coralnet.ucsd.edu/): image organization/annotation and statistics, with labels requiring validation. **OBIS contributors / IOC-UNESCO.** [Ocean Biodiversity Information System](https://obis.org/): marine occurrence discovery; sampling effort matters and absent records do not establish species absence. Obtain dataset-specific citations, versions, permissions and access conditions from each provider before any continuation.

Only the sources used above are cited as consulted; unused source-course readings and videos are not adopted. No provider data, reef/community observations, imagery, annotations, models or API connections are bundled or requested. All summaries, fixture code and SVGs here are original: **MIT code; CC BY 4.0 narrative, figures and synthetic fixtures**, attributed to James L. Tobias and contributors (2026). External rights remain with their creators; no endorsement is implied. The 2026-11-02 HTTP checks establish entry reachability only, not external notebook targets or service functions.

### README splash illustration

The [new cover](assets/splash-v2.png) was created for this index on **2 November 2026** with **OpenAI's built-in image generation tool**, directed and selected by **James L. Tobias and JupyterLite Learning Atlas contributors**. Its fictional landscape, reef, team, charts and globe are conceptual artwork. No external reference images, provider imagery or source-course art were used. [Full prompt, artifact details and attribution](assets/SPLASH-PROVENANCE.md). Original project artwork uses [CC BY4.0](LICENSE-CONTENT.md); this does not license linked provider materials. The earlier SVG remains available for the website and Book.


## PHI outbreak cases: creators, sources and rights (2026-11-02)

### 1854 Cholera Basic: dots, counts and centres: inspected source notebooks

**Creators:** PHI-Case-Studies and contributors; the Cholera notebooks list contact credits for Herman Tolentino, Jan MacGregor, James Tobias and Zhanar Haimovich. Contacts do not establish sole authorship.

**Repository:** [PHI-Case-Studies/Jupyterlite-1854-Cholera-Basic](https://github.com/PHI-Case-Studies/Jupyterlite-1854-Cholera-Basic). [Reviewed README](https://github.com/PHI-Case-Studies/Jupyterlite-1854-Cholera-Basic/blob/476f6dd5a8430e6eb823e79614fda1d7e12a78fb/README.md), full commit `476f6dd5a8430e6eb823e79614fda1d7e12a78fb`, branch `main`, inspected 2026-11-02.

The source supplies a published JupyterLite course. Its pandas/Folium maps and external tiles have separate runtime and attribution requirements; their execution is not certified by entry checks.

**Source rights:** Root LICENSE: GNU GPLv3.

| Inspected source file | What the source teaches |
|---|---|
| [NB01-Cholera-Case-Study-Folium-Map-Part-1.ipynb](https://github.com/PHI-Case-Studies/Jupyterlite-1854-Cholera-Basic/blob/476f6dd5a8430e6eb823e79614fda1d7e12a78fb/NB01-Cholera-Case-Study-Folium-Map-Part-1.ipynb) | Tables, deaths/pumps, Folium layers and the information value cycle |
| [NB02-Cholera-Case-Study-Folium-Map-Part-2.ipynb](https://github.com/PHI-Case-Studies/Jupyterlite-1854-Cholera-Basic/blob/476f6dd5a8430e6eb823e79614fda1d7e12a78fb/NB02-Cholera-Case-Study-Folium-Map-Part-2.ipynb) | Death-weighted mean centre and careful map interpretation |

[Root license at the inspected commit](https://github.com/PHI-Case-Studies/Jupyterlite-1854-Cholera-Basic/blob/476f6dd5a8430e6eb823e79614fda1d7e12a78fb/LICENSE).

The [published contents manifest](https://phi-case-studies.github.io/Jupyterlite-1854-Cholera-Basic/api/contents/all.json) was inspected 2026-11-02. The [existing source audit](https://jltobias.github.io/JupyterLite-Learning-Atlas/catalog/launch-checks.json) records its dated URL, source commit, confirmed course notebook basenames and canonical-JSON SHA-256 under `manifest_evidence`, separate from launch rows. This confirms filenames, not source execution or provider behavior. The reviewed Basic README supplies the course root; the manifest separately confirms its two root notebook filenames.

### 1854 Cholera Advanced1: routes and reachable nodes: inspected source notebooks

**Creators:** PHI-Case-Studies and contributors; the Cholera notebooks list contact credits for Herman Tolentino, Jan MacGregor, James Tobias and Zhanar Haimovich. Contacts do not establish sole authorship.

**Repository:** [PHI-Case-Studies/Jupyterlite-1854-Cholera-Outbreak-London-Advanced-1](https://github.com/PHI-Case-Studies/Jupyterlite-1854-Cholera-Outbreak-London-Advanced-1). [Reviewed README](https://github.com/PHI-Case-Studies/Jupyterlite-1854-Cholera-Outbreak-London-Advanced-1/blob/8bde848d13d71602b2b32c62e5d4b4957e4a45a1/README.md), full commit `8bde848d13d71602b2b32c62e5d4b4957e4a45a1`, branch `main`, inspected 2026-11-02.

This later Jupyterlite source is primary. Its published deployment and root notebook paths were observed in the pinned deployment workflow and public manifest; its generic template README's demo is not the Cholera course. OSMnx/NetworkX/Folium workflows and external tiles need separate support checks.

**Source rights:** Root LICENSE: GNU GPLv3; content/LICENSE: Apache 2.0, with Apache wording in the content README. Both layers are recorded; no blanket resolution is asserted.

| Inspected source file | What the source teaches |
|---|---|
| [content/NB01-Cholera-Case-Study-OpenStreetMaps-Networkx.ipynb](https://github.com/PHI-Case-Studies/Jupyterlite-1854-Cholera-Outbreak-London-Advanced-1/blob/8bde848d13d71602b2b32c62e5d4b4957e4a45a1/content/NB01-Cholera-Case-Study-OpenStreetMaps-Networkx.ipynb) | OSMnx street graph and Folium overlay |
| [content/NB02-Cholera-Case-Study-OpenStreetMaps-Networkx.ipynb](https://github.com/PHI-Case-Studies/Jupyterlite-1854-Cholera-Outbreak-London-Advanced-1/blob/8bde848d13d71602b2b32c62e5d4b4957e4a45a1/content/NB02-Cholera-Case-Study-OpenStreetMaps-Networkx.ipynb) | Pairwise network distances, nearest-node connectors and a 400 m walkability assumption |
| [content/NB03-Cholera-Case-Study-Isochrone-Map.ipynb](https://github.com/PHI-Case-Studies/Jupyterlite-1854-Cholera-Outbreak-London-Advanced-1/blob/8bde848d13d71602b2b32c62e5d4b4957e4a45a1/content/NB03-Cholera-Case-Study-Isochrone-Map.ipynb) | Projected walking times and convex-hull/buffer approximations |
| [content/NB04-Cholera-Case-Study-Isochrone-Map.ipynb](https://github.com/PHI-Case-Studies/Jupyterlite-1854-Cholera-Outbreak-London-Advanced-1/blob/8bde848d13d71602b2b32c62e5d4b4957e4a45a1/content/NB04-Cholera-Case-Study-Isochrone-Map.ipynb) | Point-location counts within isochrones, distinct from death weights |
| [content/NB05-Cholera-Case-Study-Inspiration-and-To-Do-List.ipynb](https://github.com/PHI-Case-Studies/Jupyterlite-1854-Cholera-Outbreak-London-Advanced-1/blob/8bde848d13d71602b2b32c62e5d4b4957e4a45a1/content/NB05-Cholera-Case-Study-Inspiration-and-To-Do-List.ipynb) | Further work, including synthetic time series |

[Root license at the inspected commit](https://github.com/PHI-Case-Studies/Jupyterlite-1854-Cholera-Outbreak-London-Advanced-1/blob/8bde848d13d71602b2b32c62e5d4b4957e4a45a1/LICENSE).

The [published contents manifest](https://phi-case-studies.github.io/Jupyterlite-1854-Cholera-Outbreak-London-Advanced-1/api/contents/all.json) was inspected 2026-11-02. The [existing source audit](https://jltobias.github.io/JupyterLite-Learning-Atlas/catalog/launch-checks.json) records its dated URL, source commit, confirmed course notebook basenames and canonical-JSON SHA-256 under `manifest_evidence`, separate from launch rows. This confirms filenames, not source execution or provider behavior. The source deployment is also evidenced by its pinned workflow below.
[Content license](https://github.com/PHI-Case-Studies/Jupyterlite-1854-Cholera-Outbreak-London-Advanced-1/blob/8bde848d13d71602b2b32c62e5d4b4957e4a45a1/content/LICENSE) and [content README](https://github.com/PHI-Case-Studies/Jupyterlite-1854-Cholera-Outbreak-London-Advanced-1/blob/8bde848d13d71602b2b32c62e5d4b4957e4a45a1/content/README.md) retain the separate Apache wording.

The [pinned deployment workflow](https://github.com/PHI-Case-Studies/Jupyterlite-1854-Cholera-Outbreak-London-Advanced-1/blob/8bde848d13d71602b2b32c62e5d4b4957e4a45a1/.github/workflows/deploy.yml) and [published manifest](https://phi-case-studies.github.io/Jupyterlite-1854-Cholera-Outbreak-London-Advanced-1/api/contents/all.json) establish the separately observed course route. The earlier [native original README](https://github.com/PHI-Case-Studies/1854-Cholera-Outbreak-London-Advanced-1/blob/97a1d13dfb23032387ed23804e3d6f4dbc99aec7/README.md), master commit `97a1d13dfb23032387ed23804e3d6f4dbc99aec7`, describes Notebook/Docker/Binder. It remains background continuation, not a duplicate atlas chapter.

### 1854 Cholera Advanced2: nearest sites, ties and buildings: inspected source notebooks

**Creators:** PHI-Case-Studies and contributors; the Cholera notebooks list contact credits for Herman Tolentino, Jan MacGregor, James Tobias and Zhanar Haimovich. Contacts do not establish sole authorship.

**Repository:** [PHI-Case-Studies/1854-Cholera-Outbreak-London-Advanced-2](https://github.com/PHI-Case-Studies/1854-Cholera-Outbreak-London-Advanced-2). [Reviewed README](https://github.com/PHI-Case-Studies/1854-Cholera-Outbreak-London-Advanced-2/blob/d1b56c135b0fab2f470b837a51e6777dfc20b286/README.md), full commit `d1b56c135b0fab2f470b837a51e6777dfc20b286`, branch `master`, inspected 2026-11-02.

The source documents native/server Notebook, Docker and Binder. No public JupyterLite counterpart was found. Its SciPy/Shapely/GeoPandas/OSMnx/Folium polygon and overlay workflow is a separate continuation, not executed by this browser-safe companion. A Binder entry response is not a running session; no Binder build was started.

**Source rights:** Root LICENSE: Apache 2.0.

| Inspected source file | What the source teaches |
|---|---|
| [NB01-Intro-Voronoi-Diagrams.ipynb](https://github.com/PHI-Case-Studies/1854-Cholera-Outbreak-London-Advanced-2/blob/d1b56c135b0fab2f470b837a51e6777dfc20b286/NB01-Intro-Voronoi-Diagrams.ipynb) | Introduction to Voronoi diagrams |
| [NB02-Computing-Convex-Hulls.ipynb](https://github.com/PHI-Case-Studies/1854-Cholera-Outbreak-London-Advanced-2/blob/d1b56c135b0fab2f470b837a51e6777dfc20b286/NB02-Computing-Convex-Hulls.ipynb) | Convex hull construction |
| [NB03-Constructing-Voronoi-Polygons.ipynb](https://github.com/PHI-Case-Studies/1854-Cholera-Outbreak-London-Advanced-2/blob/d1b56c135b0fab2f470b837a51e6777dfc20b286/NB03-Constructing-Voronoi-Polygons.ipynb) | Voronoi polygon construction |
| [NB04-Interactive-Voronoi-Map-Folium.ipynb](https://github.com/PHI-Case-Studies/1854-Cholera-Outbreak-London-Advanced-2/blob/d1b56c135b0fab2f470b837a51e6777dfc20b286/NB04-Interactive-Voronoi-Map-Folium.ipynb) | Interactive Folium Voronoi map |
| [NB05-Buildings-in-Voronoi-Cells.ipynb](https://github.com/PHI-Case-Studies/1854-Cholera-Outbreak-London-Advanced-2/blob/d1b56c135b0fab2f470b837a51e6777dfc20b286/NB05-Buildings-in-Voronoi-Cells.ipynb) | Building-footprint centroids and point-in-polygon counts |
| [NB99-Computing-Convex-Hulls-Part-2.ipynb](https://github.com/PHI-Case-Studies/1854-Cholera-Outbreak-London-Advanced-2/blob/d1b56c135b0fab2f470b837a51e6777dfc20b286/NB99-Computing-Convex-Hulls-Part-2.ipynb) | Supplement: alpha shapes and further hull exploration |

[Root license at the inspected commit](https://github.com/PHI-Case-Studies/1854-Cholera-Outbreak-London-Advanced-2/blob/d1b56c135b0fab2f470b837a51e6777dfc20b286/LICENSE).

### 2005 MDR-TB Thailand: contact evidence and unknown results: inspected source notebooks

**Creators:** PHI-Case-Studies and contributors as teaching-course creators, with John Oeltmann credited in the source. Research authors are credited separately below.

**Repository:** [PHI-Case-Studies/2005-MDR-TB-Outbreak-Thailand](https://github.com/PHI-Case-Studies/2005-MDR-TB-Outbreak-Thailand). [Reviewed README](https://github.com/PHI-Case-Studies/2005-MDR-TB-Outbreak-Thailand/blob/6d50f558cd39b40089cd3eea1fbc19425e5191d1/README.md), full commit `6d50f558cd39b40089cd3eea1fbc19425e5191d1`, branch `master`, inspected 2026-11-02.

The source documents Binder/native Notebook, not a deployed JupyterLite course; no public JupyterLite counterpart was found. Its pandas, Plotly, NetworkX and Bokeh pipeline is separate. A Binder entry response is not a running session; no Binder build was started.

**Source rights:** Root LICENSE: Apache 2.0.

| Inspected source file | What the source teaches |
|---|---|
| [NB01-MDR-TB-Case-Study-Case-Intro.ipynb](https://github.com/PHI-Case-Studies/2005-MDR-TB-Outbreak-Thailand/blob/6d50f558cd39b40089cd3eea1fbc19425e5191d1/NB01-MDR-TB-Case-Study-Case-Intro.ipynb) | Investigation, genotyping and the information workflow |
| [NB02-World-TB-Notebook-Part-1.ipynb](https://github.com/PHI-Case-Studies/2005-MDR-TB-Outbreak-Thailand/blob/6d50f558cd39b40089cd3eea1fbc19425e5191d1/NB02-World-TB-Notebook-Part-1.ipynb) | Historical WHO/World Bank TB, GDP, education and health-spending preparation |
| [NB03-World-TB-Notebook-Part-2.ipynb](https://github.com/PHI-Case-Studies/2005-MDR-TB-Outbreak-Thailand/blob/6d50f558cd39b40089cd3eea1fbc19425e5191d1/NB03-World-TB-Notebook-Part-2.ipynb) | Country/year data merging |
| [NB04-World-TB-Notebook-Part-3.ipynb](https://github.com/PHI-Case-Studies/2005-MDR-TB-Outbreak-Thailand/blob/6d50f558cd39b40089cd3eea1fbc19425e5191d1/NB04-World-TB-Notebook-Part-3.ipynb) | Plotly exploration and ecological summaries |
| [NB05-MDR-TB-Case-Study-Part-1.ipynb](https://github.com/PHI-Case-Studies/2005-MDR-TB-Outbreak-Thailand/blob/6d50f558cd39b40089cd3eea1fbc19425e5191d1/NB05-MDR-TB-Case-Study-Part-1.ipynb) | Mapping and genotype/DST joins |
| [NB06-MDR-TB-Case-Study-Part-2.ipynb](https://github.com/PHI-Case-Studies/2005-MDR-TB-Outbreak-Thailand/blob/6d50f558cd39b40089cd3eea1fbc19425e5191d1/NB06-MDR-TB-Case-Study-Part-2.ipynb) | Reported contacts, duplicate edges and secondary interviews; work in progress |
| [NB07-MDR-TB-Case-Study-Part-3.ipynb](https://github.com/PHI-Case-Studies/2005-MDR-TB-Outbreak-Thailand/blob/6d50f558cd39b40089cd3eea1fbc19425e5191d1/NB07-MDR-TB-Case-Study-Part-3.ipynb) | Social networks with NetworkX/Bokeh |

[Root license at the inspected commit](https://github.com/PHI-Case-Studies/2005-MDR-TB-Outbreak-Thailand/blob/6d50f558cd39b40089cd3eea1fbc19425e5191d1/LICENSE).

**Historical provider pipeline:** WHO and the World Bank are credited as providers in the pinned NB02–NB04 preparation/merge/exploration sequence. The inspected source snapshot is dated 2025-07-23; its preserved country/year TB, GDP, education and health-spending inputs are historical course material. No current provider feed is queried, no source table is imported, and country-level associations cannot identify individual risk. Provider attribution here is through those inspected source notebooks, rather than a claim to have refreshed their underlying datasets.

### Historical and methodological works used

- **Snow, John (1855).** *On the Mode of Communication of Cholera*, 2nd ed., London: John Churchill, pp. 38–55. [Primary transcription and map context, UCLA](https://epi-snow.ph.ucla.edu/Stream2_BSPoutbreak_a.html). Credit Charles Frederick Cheffins for historical maps drawn for Snow, and Ralph R. Frerichs and contributors for UCLA archive/curation. Historical maps are linked, never reproduced.
- **Brody, H.; Rip, M. R.; Vinten-Johansen, P.; Paneth, N.; Rachman, S. (2000).** *Map-making and myth-making in Broad Street: the London cholera epidemic, 1854.* Lancet **356**(9223), 64–68. [DOI](https://doi.org/10.1016/S0140-6736(00)02442-9), [author reprint](https://epi-snow.ph.ucla.edu/Stream2_BSPoutbreak_f.html). Snow's water hypothesis preceded the famous map; a map alone did not establish an intervention effect.
- **UCLA Department of Epidemiology, Ralph R. Frerichs and contributors.** [Historical investigation](https://epi-snow.ph.ucla.edu/Stream2_BSPoutbreak_d.html) and [Henry Whitehead context](https://epi-snow.ph.ucla.edu/Stream2_BSPoutbreak_e.html). Household inquiries, Whitehead and local officials contributed; attacks were already declining before the pump handle was removed on 8 September 1854.
- **CDC (2004).** *150th Anniversary of John Snow and the Pump Handle.* MMWR **53**(34), 783. [Historical overview](https://www.cdc.gov/mmwr/preview/mmwrhtml/mm5334a1.htm). A retrospective account is not a randomized counterfactual comparison.
- **World Health Organization (29 September 2026).** [*Cholera* fact sheet](https://www.who.int/news-room/fact-sheets/detail/cholera). Contaminated food/water, safe water, sanitation and community work provide context; this activity supplies no burden or treatment estimate.

- **Oeltmann, J. E.; Varma, J. K.; Ortega, L.; Liu, Y.; O'Rourke, T.; Cano, M.; et al. (2008).** *Multidrug-Resistant Tuberculosis Outbreak among US-bound Hmong Refugees, Thailand, 2005.* Emerging Infectious Diseases **14**(11), 1715–1721. [DOI](https://doi.org/10.3201/eid1411.071629), [primary article](https://wwwnc.cdc.gov/eid/article/14/11/07-1629_article). Credit the research authors, CDC, Thailand Ministry of Public Health and International Organization for Migration. Published tables, patient locations, networks and effect estimates are not reproduced in the atlas.
- **World Health Organization (20 May 2024).** [*Tuberculosis: Multidrug-resistant (MDR-TB) or rifampicin-resistant TB (RR-TB)*](https://www.who.int/news-room/questions-and-answers/item/tuberculosis-multidrug-resistant-tuberculosis-%28mdr-tb%29). MDR includes resistance to rifampicin and isoniazid; this exercise computes no diagnosis or treatment decision. Historical policies/data are not current clinical or immigration guidance.

- **NetworkX contributors.** [Weighted shortest paths](https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html) and [connected components](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.components.connected_components.html), algorithm background only. No NetworkX code/examples are copied and no package installation is needed.
- **SciPy contributors.** [Voronoi method documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.Voronoi.html), source-method context only. The atlas samples a finite nearest-site grid rather than constructing exact Voronoi polygons; SciPy is not installed by these activities.
- **OpenStreetMap contributors.** [Copyright and ODbL attribution](https://www.openstreetmap.org/copyright). Source streets/buildings and Folium/CARTO tiles have separate data/provider terms. All atlas geometry is invented; no OSM graph, footprint, tile or historical basemap is bundled or downloaded. Retain required attribution in source continuations.
- **Upstream software communities:** pandas, NumPy, Folium, OSMnx, NetworkX, GeoPandas, Shapely, SciPy, Bokeh and Plotly support the linked source courses. The original atlas activities execute only Python's standard library and IPython display, under the atlas's existing runtime notices.

All summaries, code, synthetic fixtures and SVGs here are newly authored: MIT executable code; CC BY 4.0 narrative, fixtures and figures, James L. Tobias and JupyterLite Learning Atlas contributors (2026). No source code/prose/data/imagery, patient records, pickles, saved graphs or map tiles are copied. Source rights remain with their creators; public access and shared contributors imply no blanket relicensing or endorsement.
