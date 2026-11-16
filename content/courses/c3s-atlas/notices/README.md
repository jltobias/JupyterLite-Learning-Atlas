# JupyterLite-C3S-Atlas

![Original climate globe splash illustration for JupyterLite-C3S-Atlas; decorative artwork, not a measured climate map](assets/atlas-splash.png)

**Explore climate. Inspect the evidence. Learn in your browser.**

An independent educational Jupyter Book and JupyterLite Lab for exploring the
[Copernicus Interactive Climate Atlas](https://atlas.climate.copernicus.eu/).
Twenty Python notebooks connect climate questions with reproducible calculations,
charts, interactive maps, rotating globes, and three-dimensional scenes.
Each chapter opens with an original splash illustration and includes a guiding
question, worked code, an interpretation check, an official-Atlas exercise, and credits.

## Open the learning environment

| Destination | Launch link | What you can do |
| --- | --- | --- |
| Project home | [Explore the site](https://jltobias.github.io/JupyterLite-C3S-Atlas/) | Choose a learning route. |
| Jupyter Book | [Read the chapters](https://jltobias.github.io/JupyterLite-C3S-Atlas/book/index.html) | Read explanations and executed notebook outputs. |
| JupyterLite Lab | [Launch Python Lab](https://jltobias.github.io/JupyterLite-C3S-Atlas/lite/lab/index.html?path=01-atlas-orientation.ipynb) | Run and edit the same notebooks on your device. |
| 2D maps | [Explore interactive maps](https://jltobias.github.io/JupyterLite-C3S-Atlas/maps/) | Pan, zoom, inspect values, and compare colour scales. |
| 3D maps and globes | [Rotate the globe](https://jltobias.github.io/JupyterLite-C3S-Atlas/globe/) | Inspect geographic patterns on a sphere. |
| 3D scenes | [Explore climate scenes](https://jltobias.github.io/JupyterLite-C3S-Atlas/scenes/) | Explore year, season, and anomaly in three dimensions. |
| Learning resources | [Resources and training](https://jltobias.github.io/JupyterLite-C3S-Atlas/book/learning-resources.html) | Continue with official C3S courses, notebooks, and media. |

The [Pages workflow](https://github.com/jltobias/JupyterLite-C3S-Atlas/actions/workflows/pages.yml)
builds and publishes these destinations together. You can also browse the
[notebook sources](content/) or build a local preview using the commands below.
The [official C3S Atlas](https://atlas.climate.copernicus.eu/) and
[official C3S user-tools book](https://ecmwf-projects.github.io/c3s-atlas/) are separate,
existing resources.

## The course

| Chapter | Notebook | Main idea |
| --- | --- | --- |
| 01 | [A question-led tour](content/01-atlas-orientation.ipynb) | Define variable, dataset, place, period, and statistic. |
| 02 | [Data and provenance](content/02-data-and-provenance.ipynb) | Distinguish observations, reanalyses, and projections; verify source hashes. |
| 03 | [Baselines and anomalies](content/03-baselines-and-anomalies.ipynb) | Compare reference periods and descriptive trends. |
| 04 | [Seasons and stripes](content/04-seasons-and-stripes.ipynb) | Read annual cycles, seasonal stripes, and cross-year seasons. |
| 05 | [Heat and cold](content/05-heat-and-cold.ipynb) | Calculate daily thresholds, extremes, and degree-days. |
| 06 | [Rain and water](content/06-rain-and-water.ipynb) | Separate amounts, intensity, counts, and multi-day extremes. |
| 07 | [Drought](content/07-drought.ipynb) | Understand accumulation, water balance, and SPI/SPEI limitations. |
| 08 | [Wind and radiation](content/08-wind-and-radiation.ipynb) | Understand units and nonlinear energy relationships. |
| 09 | [Snow and ice](content/09-snow-and-ice.ipynb) | Distinguish concentration, area, extent, and water equivalent. |
| 10 | [Ocean and circulation](content/10-ocean-and-circulation.ipynb) | Interpret SST and pressure patterns without causal overclaims. |
| 11 | [Scenarios and ensembles](content/11-scenarios-and-ensembles.ipynb) | Compare conditional futures and ensemble spread. |
| 12 | [Global warming levels](content/12-global-warming-levels.ipynb) | Explore **real upstream CMIP6 warming-level windows**. |
| 13 | [Uncertainty and bias](content/13-uncertainty-and-bias.ipynb) | See why correcting a mean need not correct an extreme. |
| 14 | [Regions and weights](content/14-regions-and-weights.ipynb) | Calculate area-weighted regional means and coverage. |
| 15 | [Interactive 2D maps](content/15-interactive-2d-maps.ipynb) | Use honest legends, coordinates, and numerical alternatives. |
| 16 | [Globes and 3D maps](content/16-globes-and-3d-maps.ipynb) | Rotate a scalar field on a sphere and inspect occlusion. |
| 17 | [3D scenes](content/17-3d-scenes.ipynb) | Compare a year–month surface with its flat heatmap. |
| 18 | [Monitoring and urban context](content/18-monitoring-and-urban.ipynb) | Separate anomalies, paired contrasts, and local exposure. |
| 19 | [Bring real C3S data](content/19-bring-real-data.ipynb) | Validate a small authentic export and its provenance. |
| 20 | [Reproducible capstone](content/20-capstone.ipynb) | Build a cited evidence card with a bounded conclusion. |

The [coverage index](content/variables.md) maps the 35 base CDS Atlas variables to
the chapters and identifies the official workflows linked for advanced methods.
The course covers all major climate themes and application views; it does not
claim to reproduce every production algorithm or to bundle every dataset.

## Understand the data before interpreting a plot

- **Authentic bundled references:** a pinned CMIP6 warming-level table from the
  C3S Atlas User Tools, a CDS catalogue snapshot, and Natural Earth coastlines.
  [File-level provenance and hashes](content/data/manifest.json) identify exact inputs.
- **Synthetic teaching examples:** small seeded datasets and analytic fields
  demonstrate methods. They are explicitly labelled in the lessons and figures.
  They are not C3S observations, projections, forecasts, or official map products.
- **Your authentic C3S subset:** Chapter 19 and the [data guide](docs/data-guide.md)
  explain how to bring in an Atlas regional export or prepare a small NetCDF subset.
  The full gridded C3S archive requires its own access/download workflow.

The 3D scenes are climate-data visualisations, not terrain models or urban digital
twins. Companion 2D views and numerical tables support comparison and accessibility.
No API key is needed for the bundled lessons. **Keep CDS credentials out of browser
notebooks and version control.**

JupyterLite runs Python on your device. Its first visit requires internet for the
runtime and packages. Some book charts load Plotly from its versioned CDN; map
galleries bundle Plotly locally. Lab edits are stored in the current browser;
download notebooks and results you want to keep. Saving in Lab does not save to GitHub.

## Learning resources, training, and videos

- [C3S introduction to the Atlas](https://climate.copernicus.eu/copernicus-interactive-climate-atlas-guide-powerful-new-c3s-tool)
- [Full Atlas user guide, including the official introductory video link](https://confluence.ecmwf.int/spaces/CKB/pages/394237545/Copernicus+Interactive+Climate+Atlas+User+Guide)
- [Official C3S Atlas User Tools and notebooks](https://github.com/ecmwf-projects/c3s-atlas)
- [C3S User Learning Services: modules, courses, and training events](https://climate.copernicus.eu/user-learning-services)
- [C3S training notebook collection](https://ecmwf-training.github.io/c3s-training/)
- [CDS Atlas data catalogue](https://doi.org/10.24381/cds.h35hb680) and [CDS API guide](https://cds.climate.copernicus.eu/how-to-api)
- [IPCC AR6 WGI Atlas chapter](https://www.ipcc.ch/report/ar6/wg1/chapter/atlas/)

Videos and publisher media are linked at their sources so their captions, authorship,
and usage terms remain attached. No copied screenshots, logos, or video files are
included. All exercises have written instructions.

## Citations, attribution, and licences

Credit **Copernicus Climate Change Service (C3S), implemented by ECMWF on behalf of
the European Union**, and the **CSIC/Predictia** Atlas teams. Credit the underlying
observation, reanalysis, and modelling teams identified in each actual data product.

Core references:

1. **C3S/ECMWF.** *Gridded dataset underpinning the Copernicus Interactive Climate
   Atlas.* [doi:10.24381/cds.h35hb680](https://doi.org/10.24381/cds.h35hb680).
   The current catalogue identifies [CC BY 4.0](https://cds.climate.copernicus.eu/licences/cc-by).
   Cite the release, access date, selected source/model, and modifications for real-data results.
2. **Gutiérrez, J. M.; San Martín, D.; Horányi, A.; Brookshaw, A.; Buontempo, C.;
   Díez-Sierra, J.; Goddard, C.; and Tuni, M. (2024).** *The Copernicus Interactive
   Climate Atlas: a tool to explore regional climate change.* ECMWF Newsletter 181.
   [doi:10.21957/ah52ufc369](https://doi.org/10.21957/ah52ufc369).
3. **European Union and C3S Atlas User Tools contributors.**
   [c3s-atlas](https://github.com/ecmwf-projects/c3s-atlas), upstream repository:
   Copyright 2023, European Union; Apache License 2.0. The bundled auxiliary table is
   preserved unmodified with a pinned revision and [upstream licence](licenses/C3S-Atlas-Apache-2.0.txt).
4. **Iturbide, M., et al. (2020).** *An update of IPCC climate reference regions for
   subcontinental analysis of climate model data: definition and aggregated datasets.*
   ESSD 12, 2959–2970. [doi:10.5194/essd-12-2959-2020](https://doi.org/10.5194/essd-12-2959-2020).
   The course's rectangular teaching masks are not these reference-region boundaries.
5. **Natural Earth; Nathaniel Vaughn Kelso, Tom Patterson, and contributors.**
   Coastlines: **Made with Natural Earth**, [public domain](https://www.naturalearthdata.com/about/terms-of-use/).

See [full credits and the real-data attribution template](docs/credits.md),
[data provenance](content/data/README.md), [third-party licences](licenses/), and
[CITATION.cff](CITATION.cff). Jupyter, JupyterLite, Pyodide, Jupyter Book, NumPy,
pandas, Matplotlib, and Plotly remain projects of their respective contributors.

Original code, prose, and teaching data use the [MIT licence](LICENSE). The original
AI-generated splash illustration has a recorded [creation prompt](assets/PROVENANCE.md)
and is not a scientific data product. Third-party open data retain their own terms;
attribution does not turn copyrighted material into public domain. Source articles
and media are linked, not reproduced. This project is not an official or endorsed
Copernicus, ECMWF, CSIC, Predictia, IPCC, or Jupyter publication.

## Build and preview locally

Use Python 3.13 in a project virtual environment:

```shell
python -m venv .venv
# Activate .venv using the command appropriate to your shell.
python -m pip install -r requirements.txt -r requirements-data.txt
python scripts/prepare_content.py
python -m pytest -q
python scripts/execute_notebooks.py
python scripts/build_site.py
python scripts/check_site.py
python -m http.server 8000 --directory _site --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/`. Stop the preview server with Ctrl+C.
On PowerShell, activation is `.\.venv\Scripts\Activate.ps1`; alternatively invoke
`.venv/Scripts/python.exe` directly for every command. A local environment avoids
changing system Python. The Sphinx-based Jupyter Book 1 build is intentionally
pinned for its static HTML notebook rendering; it remains in maintenance mode.

Notebook sources are authored in `scripts/generate_notebooks.py`. After changing
lesson definitions, run it before execution. It replaces generated notebook files,
so preserve intentional notebook edits in the definitions first. Documentation in
`docs/` is copied into the book/Lab by `prepare_content.py`.

## Publish with GitHub Pages

The included [workflow](.github/workflows/pages.yml) tests the calculations,
executes the notebooks, builds the complete site, and checks local links. Pull
requests build without deploying. A push to `main` or manual workflow run on
`main` deploys the generated `_site` artifact when Pages is configured.

In the repository's **Settings → Pages**, set the source to **GitHub Actions**.
Commit and push the reviewed files, then check the workflow's deployment result.
The site destinations above share one deployment: `/book/`, `/lite/`, `/maps/`,
`/globe/`, and `/scenes/`. Deployment status is not inferred from a local build.

For validation evidence and known limitations, see [validation](validation/README.md).
