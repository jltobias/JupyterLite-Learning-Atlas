# South Sudan Dashboard - JupyterLite Conversion

This folder contains a JupyterLite-compatible conversion of the Shiny app.

## Contents

- `SouthSudanDashboard_JupyterLite.ipynb` - interactive dashboard notebook
- `data/SouthSudanHealthFacilities1282026.csv` - facility data
- `data/SouthSudanH3res5.geojson` and `data/SouthSudanH3res6.geojson` - optional H3 layers
- `data/dem_overlay.png` and `data/dem_bounds.json` - pre-rendered DEM overlay for Folium
- `data/hstp_discontinued.json` - HSTP discontinued facility names extracted from the Shiny app
- `requirements-jupyterlite.txt` - browser-friendly package list

## How to use in JupyterLite

1. Open JupyterLite.
2. Upload the notebook and the `data/` folder together, keeping the same relative paths.
3. Open `SouthSudanDashboard_JupyterLite.ipynb`.
4. Run all cells from top to bottom.

## Important changes from Shiny

- `shiny`, `shinywidgets`, `rasterio`, and `acled` were removed from the runtime path because they are not appropriate for normal JupyterLite/Pyodide execution.
- The DEM GeoTIFF was converted to a PNG overlay ahead of time.
- ACLED is represented by deterministic sample data. For production, export ACLED events to CSV and load that file in the notebook.
- HDX/IDMC is attempted with `pd.read_csv(url)`, but browser CORS/network rules may block it; in that case the notebook uses deterministic sample data.
