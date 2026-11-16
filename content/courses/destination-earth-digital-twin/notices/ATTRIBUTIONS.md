# Attribution, provenance and reuse

This is an independent educational repository. Destination Earth is an initiative of the **European Union**, implemented by **ECMWF, ESA and EUMETSAT**. ECMWF develops the Digital Twin Engine and initial twins; ESA implements the DestinE Platform; EUMETSAT implements the Data Lake. These credits describe official roles, not authorship of or endorsement for this repository.

## Original work actually included

| Material | Origin | Reuse terms |
|---|---|---|
| Python helpers, notebook code, scripts, tests, HTML/CSS/JavaScript | Original project implementation with OpenAI Codex assistance | MIT |
| Notebook explanations, book and README | Original project prose with OpenAI Codex assistance | CC BY 4.0 |
| Numerical demonstration arrays | Original deterministic equations and seeded pseudorandom values | CC BY 4.0 |
| `assets/splash.png` and identical notebook copy | Original built-in image-generation output, 2026-11-15 | CC BY 4.0, to the extent rights can be licensed |

Artwork depicts an abstract globe and invented weather streamlines. It is not real observations or model results. No agency logo, satellite image, external notebook code or authentic DT output is included. See [generation provenance](assets/GENERATION.md). Repository maintainer: [jltobias](https://github.com/jltobias); contributions may be credited through version history. No institutional affiliation is inferred from the maintainer's handle.

## Primary conceptual references — linked, not copied or downloaded

| Source | Purpose | Actual data use |
|---|---|---|
| [Destination Earth source index](https://github.com/destination-earth/DestinE) | Initiative/component orientation | None |
| [Digital Twin Engine](https://destine.ecmwf.int/digital-twin-engine/) | Architecture and workflow concepts | None |
| [Climate DT](https://destine.ecmwf.int/climate-digital-twin/) | Climate adaptation context | None |
| [Weather-Induced Extremes DT](https://destine.ecmwf.int/weather-induced-extremes-digital-twin/) | Global/regional extremes context | None |
| [AI in DestinE](https://destine.ecmwf.int/ai-in-destination-earth/) and [ML Earth-system components](https://destine.ecmwf.int/ml-earth-system-components/) | ML program and land, waves, hydrology, sea-ice and ocean context | None; no official weights, model code or training data used |
| [Polytope](https://polytope.readthedocs.io/en/stable/) | Feature extraction concepts | None; no API call |
| [Data Lake documentation](https://destine-data-lake-docs.data.destination-earth.eu/en/latest/) | HDA, STAC and service roles | None; no cloud service invoked |
| [DestinE Data Lake Lab](https://github.com/destination-earth/DestinE-DataLake-Lab) | Official learning destination | None; no notebook code copied |
| [Platform services](https://platform.destine.eu/services/) and [access FAQ](https://platform.destine.eu/support-faq/) | Registration and selection | None |
| [Data Lake terms](https://data.destination-earth.eu/terms-and-conditions) | Service-specific access/reuse rules | None |
| [Climate DT Generation 2 metadata](https://www.ecmwf.int/en/forecasts/dataset/destination-earth-digital-twin-climate-change-adaptation-gen2), DOI [10.21957/79c6af3105](https://doi.org/10.21957/79c6af3105) | Dataset citation example | **Not used** |
| [Earthkit data](https://earthkit-data.readthedocs.io/en/latest/) | Server-side decoding/export concepts | No authentic decoding or retrieval |
| [PROJ Mercator docs](https://proj.org/en/stable/operations/projections/merc.html) | Projection explanation | No PROJ dependency or map data |

Primary DestinE sources were verified on 2026-11-15. Explanations are original paraphrases. Service terms and dataset licenses can change and differ: this project does **not** describe all DestinE data as open, freely redistributable or universally CC BY. Check applicable terms for the exact dataset and service before authentic use.

## Software dependencies — licenses remain with their authors

| Dependency | Role | Upstream license |
|---|---|---|
| [Jupyter Book / MyST](https://github.com/jupyter-book/jupyter-book) | Book publishing | MIT |
| [JupyterLite](https://github.com/jupyterlite/jupyterlite) and [Pyodide kernel](https://github.com/jupyterlite/pyodide-kernel) | Browser Lab | BSD-3-Clause |
| [Pyodide](https://github.com/pyodide/pyodide) | Browser Python | MPL-2.0 plus component licenses |
| [NumPy](https://github.com/numpy/numpy), [SciPy](https://github.com/scipy/scipy), [pandas](https://github.com/pandas-dev/pandas) | Scientific computation | BSD-3-Clause |
| [Matplotlib](https://github.com/matplotlib/matplotlib) | Scientific plotting | Matplotlib license (PSF-based) |
| [xarray](https://github.com/pydata/xarray) | Labeled arrays | Apache-2.0 |
| [ipywidgets](https://github.com/jupyter-widgets/ipywidgets) | Notebook controls | BSD-3-Clause |
| [nbformat](https://github.com/jupyter/nbformat), [nbclient](https://github.com/jupyter/nbclient), [ipykernel](https://github.com/ipython/ipykernel) | Validation/execution | BSD-3-Clause |
| [pytest](https://github.com/pytest-dev/pytest) | Tests | MIT |
| [Playwright](https://github.com/microsoft/playwright-python) | Browser verification tooling | Apache-2.0 |
| [Node.js](https://github.com/nodejs/node) | Build runtime | MIT plus bundled-component notices |

This table is an orientation, not a replacement for notices distributed with installed versions. Build tools preserve bundled dependency license files. The project license does not override third-party licenses. Browser package downloads retain their own terms.
