# JupyterLite-terrio

![Original conceptual landscape showing terrain contours, raster layers, point samples, and a globe](assets/terrio-cover.png)

**A geospatial field guide you can read, run, and question.** Explore [TerrIO](https://github.com/opengeos/terrio) through a Jupyter Book, a browser-based JupyterLite Lab, and 13 original notebook chapters—from your first GeoTIFF to an interactive globe and a reproducible terrain investigation.

## Explore

| Destination | Project link | Available in this repository |
|---|---|---|
| Home | [Learning portal](https://jltobias.github.io/JupyterLite-terrio/) | [Site source](site/index.html) |
| Jupyter Book | [Read the book](https://jltobias.github.io/JupyterLite-terrio/book/intro.html) | [Book introduction](book/intro.md) |
| JupyterLite Lab | [Run Python in your browser](https://jltobias.github.io/JupyterLite-terrio/lite/lab/index.html?path=01-first-contact.ipynb) | [All notebooks](notebooks/) |
| 2D maps | [Explore country outlines](https://jltobias.github.io/JupyterLite-terrio/maps/2d.html) | [Vectors and 2D maps](notebooks/03-vectors-2d-maps.ipynb) |
| 3D maps | [Explore terrain](https://jltobias.github.io/JupyterLite-terrio/maps/3d.html) | [Terrain notebook](notebooks/06-terrain.ipynb) |
| 3D scenes and globe | [Orbit a scene or globe](https://jltobias.github.io/JupyterLite-terrio/maps/scenes.html) | [Scenes and globes notebook](notebooks/09-scenes-and-globes.ipynb) |
| Learning resources and training | [Learning hub](https://jltobias.github.io/JupyterLite-terrio/book/resources.html) | [Resources, videos, and instructor guide](book/resources.md) |

**Live on GitHub Pages:** the destinations above are published and were verified on **2026-11-15**. The [deployment workflow](https://github.com/jltobias/JupyterLite-terrio/actions/workflows/pages.yml) builds and tests every chapter before publishing site updates. Current upstream resources are available at [TerrIO documentation](https://terrio.dev/), [TerrIO playground](https://terrio.dev/playground/), [TerrIO web app](https://terrio.dev/web/), and [TerrIO notebooks](https://terrio.dev/notebooks/).

## The course

Each chapter opens with its own original splash image and includes learning goals, executable Python, visual evidence, interpretation limits, an investigation, a discussion guide, and source credits. Every notebook can run independently. The book shows executed results; Lab lets you change the same code.

| Chapter | What you investigate |
|---|---|
| [01 · First contact](notebooks/01-first-contact.ipynb) | TerrIO I/O, raster metadata, distributions, and verified exports |
| [02 · Coordinates](notebooks/02-coordinates.ipynb) | CRS transforms, pixel centres, units, and map distortion |
| [03 · Vectors and 2D maps](notebooks/03-vectors-2d-maps.ipynb) | Natural Earth, attribute filters, interactive maps, and feature counts |
| [04 · Vector analysis](notebooks/04-vector-analysis.ipynb) | Metric buffers, geometry checks, dissolve, and scale sensitivity |
| [05 · Rasters and COGs](notebooks/05-rasters-and-cogs.ipynb) | Nodata, cloud-ready files, windows, resampling, and memory budgets |
| [06 · Terrain](notebooks/06-terrain.ipynb) | Slope, hillshade, contours, numerical comparisons, and 3D terrain |
| [07 · Imagery](notebooks/07-imagery.ipynb) | Synthetic reflectance, NDVI, quality masks, and thresholds |
| [08 · Point clouds](notebooks/08-point-clouds.ipynb) | LAS round trips, class filtering, gridding, and 3D point scenes |
| [09 · Scenes and globes](notebooks/09-scenes-and-globes.ipynb) | A rotating globe, layered terrain, transects, and accessible profiles |
| [10 · Data cubes](notebooks/10-data-cubes.ipynb) | TerrIO/xarray, dimensions, seasonal signals, and anomalies |
| [11 · Cloud and catalogs](notebooks/11-cloud-and-catalogs.ipynb) | STAC metadata, local COG windows, and honest transfer estimates |
| [12 · Interoperability](notebooks/12-interoperability.ipynb) | GeoJSON/FlatGeobuf/GeoPackage, round-trip checks, and provenance |
| [13 · Capstone](notebooks/13-capstone.ipynb) | A terrain query, sensitivity analysis, exported COG, and cited report |

The [learning hub](book/resources.md) also connects advanced TerrIO topics—HEC-RAS, CAD, multidimensional formats, tiles, Rust, JavaScript, MCP, and rasterio migration—to the authors' primary documentation. This is an independent educational companion, not an official TerrIO product or an exhaustive driver reference.

## Run in your browser

Open Lab, choose a chapter and the **Python (Pyodide)** kernel, then **Run → Run All Cells**. The first run downloads Python and packages. No account or API key is required for the core lessons. Work stays in browser storage: download edited notebooks and `outputs/` files to preserve them.

TerrIO **0.9.0** is pinned with its compatible **Pyodide 0.29** runtime. Browser Python reads local files after download; native remote HTTP range reads are covered as an extension rather than presented as a browser feature. Interactive notebook plots load Plotly's versioned CDN script; 3D views require WebGL. Static figures and numerical summaries provide alternatives. Full offline operation is not promised.

## Data, rights, and attribution

The only bundled real-world dataset is **Natural Earth 1:110m Admin 0 Countries v5.1.2**, public domain, by **Tom Patterson, Nathaniel Vaughn Kelso, and contributors**. **Made with Natural Earth.** See [terms](https://www.naturalearthdata.com/about/terms-of-use/), the [source and checksum manifest](notebooks/data/sources.json), and the [complete attribution ledger](book/attribution.md). Generalized map boundaries are not authoritative legal boundaries.

Terrain, reflectance, point clouds, station positions, and seasonal values are **original synthetic teaching data**, clearly labelled throughout. The [cover illustration](assets/ARTWORK.md) is AI-generated conceptual artwork; chapter cards are original SVG diagrams. Third-party prose, artwork, videos, and restricted datasets are not copied. Training videos are linked at their authors' hosts.

Open-source dependencies remain copyrighted under their licenses. TerrIO credits **John Lindsay / whitebox_next_gen; Frank Warmerdam, Even Rouault and GDAL contributors; Gerald Evenden and PROJ contributors; Hobu, Inc. and PDAL contributors; GeoRust, JTS, GEOS, CSF, rasterio, xarray, and rioxarray authors**, among others. Coordinate definitions include **IOGP's EPSG Geodetic Parameter Dataset** under its [terms](https://epsg.org/terms-of-use.html). Preserve TerrIO's [LICENSE](https://github.com/opengeos/terrio/blob/v0.9.0/LICENSE), [NOTICE](https://github.com/opengeos/terrio/blob/v0.9.0/NOTICE), and [dependency licenses](https://github.com/opengeos/terrio/blob/v0.9.0/LICENSE-THIRD-PARTY.md); the build includes copies alongside the browser wheel.

Credit also belongs to **Project Jupyter, JupyterLite, Pyodide, Executable Books / Jupyter Book, Sphinx, NumPy, Matplotlib, Plotly, pandas, and xarray contributors**. See [third-party notices](THIRD_PARTY_NOTICES.md). Original repository code is MIT; original text, synthetic data, and chapter diagrams are CC0 1.0 to the extent rights exist. These terms do not relicense dependencies or third-party data.

## Citation

For TerrIO, cite **Qiusheng Wu, Mavrick Fitzgerald, and Guillermo Morales Sanchez (2026), _terrio: Pure-Rust geospatial raster, vector and point cloud data I/O_, Zenodo, [doi:10.5281/zenodo.23642204](https://doi.org/10.5281/zenodo.23642204)**. This is the authors' concept DOI; record the actual software version separately. See [TerrIO's citation guide](https://terrio.dev/citation/).

For this course, use [CITATION.cff](CITATION.cff) and record the repository commit and access date. The course has no DOI. Natural Earth and any additional datasets should be cited separately.

## Learning resources and training

- [TerrIO official documentation and tutorials](https://terrio.dev/) — Qiusheng Wu and TerrIO contributors.
- [Introduction to GIS Programming](https://geog-312.gishub.org/) and [Spatial Data Management](https://geog-414.gishub.org/) — Qiusheng Wu.
- [Qiusheng Wu's video channel](https://www.youtube.com/@giswqs) — author-hosted geospatial lessons.
- [NASA ARSET](https://appliedsciences.nasa.gov/what-we-do/capacity-building/arset), [xarray tutorials](https://tutorial.xarray.dev/), and [QGIS Training Manual](https://docs.qgis.org/latest/en/docs/training_manual/) — further practice at the original providers.

## Build and publish

With Python 3.12 in an activated virtual environment:

```sh
python -m pip install -r requirements.txt
python scripts/fetch_assets.py
python scripts/fetch_notices.py
python scripts/validate.py
python scripts/execute_notebooks.py
python scripts/build.py
python -m http.server 8000 --directory _site
```

Open `http://localhost:8000`. The pinned Jupyter Book v1 build is intentional; v2 needs a configuration migration. For browser tests, install Chromium with `python -m playwright install chromium`, then run `python scripts/test_browser.py`.

The [GitHub Actions workflow](.github/workflows/pages.yml) tests and deploys a combined book, Lab, and map site. This repository's **Settings → Pages → Source** is configured as **GitHub Actions**; reviewed changes pushed to `main` trigger the workflow. For a fork, enable that Pages setting in your own repository. See the [contributor guide](book/contributing.md) for runtime details, tests, and maintenance. Source and attribution review date: **2026-11-15**.
