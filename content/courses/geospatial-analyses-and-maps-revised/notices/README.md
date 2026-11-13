# JupyterLite Geospatial Analyses and Maps - revised browser-first edition

This revision replaces repetitive synthetic-boundary examples with a smaller set of distinct, map-first notebooks designed for JupyterLite and Pyodide. The notebooks emphasize real administrative/electoral boundaries, open-data workflows, browser-safe Python, and compelling visualization patterns including H3-style hexagons, animated GeoJSON, NASA tile overlays, and deck.gl 3D scenes.

## What changed

- Added 12 distinct lesson notebooks plus a JupyterLite index notebook.
- Bundled a real GeoJSON boundary layer: Montreal electoral districts from Plotly's example datasets.
- Added local CSV layers for election attributes, car-share points, health-facility training points, NYC taxi pickup teaching points, and Meuse environmental sampling teaching points.
- Removed the design posture that synthetic boundaries are acceptable for administrative mapping.
- Added browser-native H3 and deck.gl examples that do not require native Python geospatial wheels.
- Added notebook-specific reflection questions, source notes, code comments, and video embeds.
- Added graceful fallback patterns for live APIs such as USGS/Data.gov earthquake feeds and OpenStreetMap/Overpass workflows.

## JupyterLite compatibility posture

These notebooks avoid compiled geospatial packages such as GeoPandas, Fiona, Shapely, Rasterio, and PyProj. They use Pyodide-friendly packages and browser JavaScript where appropriate:

- `pandas`
- `folium`
- `branca`
- `plotly`
- Leaflet, h3-js, and deck.gl through browser CDNs in selected notebooks

## Suggested deployment

Set GitHub Pages to GitHub Actions and use the included workflow. The workflow installs JupyterLite, copies the `content/` directory, and builds a static browser site.

## Source and licensing notes

See `SOURCES.md`. External web tiles, APIs, and YouTube embeds remain subject to their respective terms. The bundled Montreal boundary and attribute examples are copied from Plotly package example datasets for educational use. For production public-health or administrative analysis, replace training point layers with authoritative exports such as healthsites.io, GADM, geoBoundaries, national statistical agencies, or agency-managed GIS services.
