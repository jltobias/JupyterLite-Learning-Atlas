# JupyterLite Geospatial Analysis Learning Lab

This repository contains browser-ready Jupyter notebooks inspired by the GISGeography **Periodic Table for Spatial Analysis**. 

URL:  https://gisgeography.com/spatial-analysis-periodic-table/

It includes one notebook for each of the 90 elements, plus an index notebook.  

The JupyterLite notebooks run in your web-browser:  https://jltobias.github.io/JupyterLite-Maps-and-Spatial-Analyses/




## Version 2: map-centric notebooks

The notebooks are designed around interactive geospatial learning rather than generic Cartesian plots. Each element notebook uses:

- real-world latitude/longitude coordinates centered on recognizable places;
- OpenStreetMap basemaps rendered with browser-side Leaflet;
- synthetic privacy-safe point observations, zones, grids, routes, and buffers;
- multiple maps per notebook to compare input data, derived layers, and interpretation layers;
- lightweight dependencies that work well in JupyterLite/Pyodide.

The synthetic values are intentionally small and inspectable so learners can change parameters and immediately see how spatial conclusions respond.

## Repository layout

```text
.
├── notebooks/                  # 00_Index plus one notebook per spatial-analysis element
├── content/elements.csv         # machine-readable element catalog
├── requirements.txt             # packages used to build JupyterLite on GitHub Actions
├── jupyter_lite_config.json      # JupyterLite site configuration
└── .github/workflows/deploy.yml  # publishes the Lite site to GitHub Pages
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter lite build --contents notebooks --contents content --output-dir dist
python -m http.server 8000 -d dist
```

Then open `http://localhost:8000`.

## Publish with GitHub Pages

1. In GitHub, open **Settings -> Pages**.
2. Set **Source** to **GitHub Actions**.
3. Push to the `main` branch. The workflow in `.github/workflows/deploy.yml` will build and publish the JupyterLite site.

## Teaching pattern

Each notebook follows the same pattern:

1. a concept summary;
2. a small synthetic dataset using real latitude/longitude coordinates;
3. an observation map;
4. an analysis map tailored to the element family;
5. a combined interpretation map;
6. reflection prompts and extension ideas.

## Notes on browser compatibility

The notebooks intentionally avoid heavier native geospatial libraries such as GDAL, Rasterio, Fiona, and GeoPandas. Those are excellent tools in a full Python environment, but they can make JupyterLite/Pyodide deployments more fragile. The interactive maps use browser-side Leaflet and OpenStreetMap tiles inside notebook output iframes.

## Source inspiration

The element list and grouping are based on GISGeography's article **The Periodic Table for Spatial Analysis**. Review the source for the original definitions and visual periodic-table design.
