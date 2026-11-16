# Destination Earth · Learning book & browser lab

![Original abstract globe with synthetic weather streamlines](assets/splash.png)

**Understand Earth-system digital twins by reading, running and changing small experiments.** This independent project connects 32 original notebooks, a Jupyter Book 2 and a JupyterLite Python lab with six interactive visual experiences. Every default exercise uses explicitly synthetic data and needs no DestinE account.

Destination Earth (DestinE) is a European Union initiative implemented by ECMWF, ESA and EUMETSAT. This project introduces its architecture and workflows without claiming to reproduce its production models, computing infrastructure or services. It is not an official DestinE product or an institutional endorsement.

## Open an experience

**Public deployment status: live.** The Book, Lab, galleries and all 32 notebooks are published on GitHub Pages. The deployment passed native and browser verification, and the public links below have been checked over HTTPS.

| Experience | Live destination | Source |
|---|---|---|
| Landing page | [Earth / Lab](https://jltobias.github.io/JupyterLite-Destination-Earth-Digital-Twin/) | [HTML](web/index.html) |
| Learning book | [Read the book](https://jltobias.github.io/JupyterLite-Destination-Earth-Digital-Twin/book/) | [Introduction](book/index.md) |
| Python browser lab | [Open JupyterLite](https://jltobias.github.io/JupyterLite-Destination-Earth-Digital-Twin/lab/index.html) | [Canonical notebooks](content/) |
| First notebook | [Start lesson 01](https://jltobias.github.io/JupyterLite-Destination-Earth-Digital-Twin/lab/index.html?path=01-system.ipynb) | [System architecture](content/01-system.ipynb) |
| 2D maps / interactive maps | [Explore a field](https://jltobias.github.io/JupyterLite-Destination-Earth-Digital-Twin/gallery/map/) | [Page](web/gallery/map/index.html) |
| 3D maps / 3D scenes | [Rotate a landscape](https://jltobias.github.io/JupyterLite-Destination-Earth-Digital-Twin/gallery/terrain/) | [Shared terrain page](web/gallery/terrain/index.html) |
| Globe | [Turn the Earth](https://jltobias.github.io/JupyterLite-Destination-Earth-Digital-Twin/gallery/globe/) | [Page](web/gallery/globe/index.html) |
| Dashboard | [Connect the views](https://jltobias.github.io/JupyterLite-Destination-Earth-Digital-Twin/gallery/dashboard/) | [Page](web/gallery/dashboard/index.html) |
| Vector field | [Follow the flow](https://jltobias.github.io/JupyterLite-Destination-Earth-Digital-Twin/gallery/flow/) | [Page](web/gallery/flow/index.html) |
| Time comparison | [Compare two days](https://jltobias.github.io/JupyterLite-Destination-Earth-Digital-Twin/gallery/compare/) | [Page](web/gallery/compare/index.html) |

## Follow the learning path

| Lessons | Focus |
|---|---|
| 01–05 | Architecture, grids, data selection, export validation and labeled arrays |
| 06–13 | Area means, anomalies, extremes, water balance, wind, interpolation, ensembles and verification |
| 14–19 | 2D maps, projections, 3D terrain, globes, time and dashboards, including live notebook controls |
| 20–22 | Browser memory, reproducibility and an adaptation comparison |
| 23–28 | DTE/HPC workflows, Polytope, Earthkit/GRIB export boundaries, Data Lake services, time-aware ML and regional extremes |
| 29–32 | Land/snow, waves, sea ice and ocean process exercises; hydrology is covered in lesson 09 |

Every notebook begins with original artwork, states objectives, runs a worked experiment with assertions, offers an exercise, explains limitations and cites sources. The book consumes these same notebooks directly; the Lite build copies them alongside [`earthlab.py`](content/earthlab.py). See the [coverage matrix](book/coverage.md) for exact chapter links.

## Run locally

Use Python 3.13 and Node.js 22 or later in a fresh environment.

```sh
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell instead:
# .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.lock
python -m pytest -q
python scripts/build.py --execute
python -m http.server 8000 --directory _site
```

Open `http://localhost:8000/`. One `_site/` contains the book, Lab and gallery. Use HTTP on localhost or HTTPS; `file://` and some private-browser modes cannot support JupyterLite's service worker and file synchronization. The first Python kernel start downloads Pyodide and packages. Internet access and a modern browser are required; offline operation is not guaranteed. `requirements.lock` pins the cross-platform Python build environment; `requirements.txt` records the direct constraints. Browser packages come from the Pyodide distribution and may have different versions from native Python.

For repository-subpath hosting:

```sh
python scripts/build.py --base-url /JupyterLite-Destination-Earth-Digital-Twin
```

Serve that artifact at the matching path; MyST asset URLs include `/JupyterLite-Destination-Earth-Digital-Twin/book`. Gallery and Lab routes are relative. The native execution report is `_executed/execution-report.json`. Rerun selected notebooks with `python scripts/execute_notebooks.py --only 09-water 17-globe`.

Browser verification is a separate check after building:

```sh
python -m pip install -r requirements-browser.txt
python -m playwright install --with-deps chromium
python scripts/browser_smoke.py
```

The smoke test serves the built artifact at its configured repository prefix and checks gallery controls, book navigation and fresh Pyodide kernels. Use `--browser-executable PATH` for an existing Chromium installation, `--gallery-only` for gallery diagnostics, or `--notebooks-only --notebooks 14-maps` for a targeted widget check. Reports go to `_executed/browser-smoke-report.json`; native execution results remain separate.

The GitHub Actions workflow validates/builds pull requests and deploys successful `main` pushes through GitHub Pages. This repository uses **GitHub Actions** as its Pages source. For a fork, select that source in **Settings → Pages**. Check the workflow result and public URLs after each deployment.

## Authentic data is a separate path

Default examples use no observational datasets, model outputs, agency imagery or copied notebook code. Official access may require registration, permissions and server-side tools. Never put tokens or passwords in this static site. Use a catalog-generated request, inspect applicable dataset/service terms, and export only a small permitted subset. [`load_export`](content/earthlab.py) rejects invalid schemas, units, coordinates and missing provenance without silently falling back to generated data. Read the [official-access guide](book/official-access.md).

## Credit and reuse

Original code is MIT; original prose, generated data and project artwork are offered under CC BY 4.0. Dependency licenses remain with their authors. Official references are conceptual links, not a claim of data use or unrestricted reuse. See [ATTRIBUTIONS.md](ATTRIBUTIONS.md), [LICENSE](LICENSE), [CITATION.cff](CITATION.cff) and [artwork provenance](assets/GENERATION.md).

Repository maintainer: [jltobias](https://github.com/jltobias). Original instructional implementation and artwork were produced with OpenAI Codex/image-generation assistance. No agency authorship or endorsement is implied.

| Credit or source | Relationship to this project |
|---|---|
| European Union | Destination Earth initiative ownership; no authorship or endorsement of this repository |
| ECMWF · [DestinE](https://destine.ecmwf.int/) · [DTE](https://destine.ecmwf.int/digital-twin-engine/) | Entrusted entity for the Digital Twin Engine and initial twins; conceptual citation only |
| ESA · [DestinE Platform](https://platform.destine.eu/) | Entrusted entity for the platform; linked service, not used by the default exercises |
| EUMETSAT · [Data Lake documentation](https://destine-data-lake-docs.data.destination-earth.eu/en/latest/) | Entrusted entity for the Data Lake; HDA/STAC, Islet, Stack, Hook, DEFAIR and MLOps context only |
| [Official DestinE source index](https://github.com/destination-earth/DestinE) | Component/source orientation; no external notebook code copied |
| [Climate DT](https://destine.ecmwf.int/climate-digital-twin/) and [Weather-Induced Extremes DT](https://destine.ecmwf.int/weather-induced-extremes-digital-twin/) | Scientific context only; no model outputs used |
| [AI in DestinE](https://destine.ecmwf.int/ai-in-destination-earth/) and [ML Earth-system components](https://destine.ecmwf.int/ml-earth-system-components/) | Component orientation only; no official model code, weights or training data used |
| [Polytope](https://polytope.readthedocs.io/en/stable/) and [Earthkit data](https://earthkit-data.readthedocs.io/en/latest/) | Feature-extraction and server/export concepts; no authentic data retrieved |
| [Climate DT Generation 2](https://www.ecmwf.int/en/forecasts/dataset/destination-earth-digital-twin-climate-change-adaptation-gen2), DOI [10.21957/79c6af3105](https://doi.org/10.21957/79c6af3105) | Linked metadata example, **dataset not used** |
| [Data Lake terms](https://data.destination-earth.eu/terms-and-conditions), [services](https://platform.destine.eu/services/), [access FAQ](https://platform.destine.eu/support-faq/) | Official account, permission and redistribution guidance; check the exact service/dataset terms |
| Original synthetic arrays and splash artwork | The only numerical data and imagery used here; project-generated, CC BY 4.0 |
| Jupyter Book/MyST, JupyterLite/Pyodide, NumPy, Matplotlib, pandas, xarray, SciPy, ipywidgets and notebook/test tooling | Software dependencies; their authors retain their licenses; [full notices and source links](ATTRIBUTIONS.md#software-dependencies--licenses-remain-with-their-authors) |

Official sources were checked on 2026-11-15. No observational data, authentic DT outputs or agency images are redistributed. The project does not imply that all DestinE datasets are freely redistributable or share one license.
