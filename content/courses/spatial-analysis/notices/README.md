# JupyterLite Geospatial Analysis Learning Lab

This repository contains browser-ready Jupyter notebooks inspired by the GISGeography **Periodic Table for Spatial Analysis**. 

URL: https://gisgeography.com/spatial-analysis-periodic-table/




It includes one notebook for each of the 90 elements, plus an index notebook.

The examples are designed for GitHub Pages + JupyterLite:

- no local Python installation for learners
- synthetic data included in each notebook
- lightweight dependencies: `numpy`, `pandas`, and `matplotlib`
- comments and markdown prompts for self-guided learning

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

1. Create a new GitHub repository and push these files.
2. In GitHub, open **Settings -> Pages**.
3. Set **Source** to **GitHub Actions**.
4. Push to the `main` branch. The workflow in `.github/workflows/deploy.yml` will build and publish the JupyterLite site.

## Suggested teaching pattern

Each notebook follows the same pattern:

1. a concept summary
2. a small synthetic dataset
3. an executable map/chart demonstration
4. reflection prompts
5. extension ideas

This consistent format makes it easy to assign one element per learner, add agency-specific examples, or expand selected notebooks into deeper modules.

## Notes on browser compatibility

The notebooks intentionally avoid heavier native geospatial libraries such as GDAL, Rasterio, Fiona, and GeoPandas. Those are excellent tools in a full Python environment, but they can make JupyterLite/Pyodide deployments more fragile. The examples emphasize core concepts using array, table, graph, and plotting operations that work well in the browser.

## Source inspiration

The element list and grouping are based on GISGeography's article **The Periodic Table for Spatial Analysis**. Review the source for the original definitions and visual periodic-table design.
