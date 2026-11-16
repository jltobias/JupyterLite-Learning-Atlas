# Learning resources and training

## Official TerrIO learning path

Start with the authors' [documentation](https://terrio.dev/), [getting started](https://terrio.dev/getting-started/), [browser playground](https://terrio.dev/playground/), [web app](https://terrio.dev/web/), and [official notebooks](https://terrio.dev/notebooks/). These are external resources maintained by the TerrIO authors; this course is independent and does not imply their endorsement.

| Topic | Course chapter | Primary reference / further training |
|---|---|---|
| Python, raster I/O, COGs | 1, 5 | [Python API](https://terrio.dev/python/), [OGC COG standard](https://www.ogc.org/standards/ogc-cloud-optimized-geotiff/) |
| Coordinate systems | 2 | [TerrIO CRS guide](https://terrio.dev/crs/), [PROJ documentation](https://proj.org/) |
| Vector formats, SQL, topology | 3, 4, 12 | [Formats](https://terrio.dev/formats/), [Vector SQL](https://terrio.dev/sql/) |
| Terrain and raster operations | 6, 7, 13 | [TerrIO command line](https://terrio.dev/cli/), [GDAL tutorials](https://gdal.org/en/stable/tutorials/index.html) |
| Lidar, LAS, COPC, EPT | 8 | [Point-cloud guide](https://terrio.dev/point-clouds/), [PDAL tutorials](https://pdal.io/en/stable/tutorial/index.html) |
| Browser and 3D visualizations | 3, 9 | [TerrIO JavaScript](https://terrio.dev/javascript/), [Plotly 3D plots](https://plotly.com/python/3d-charts/) |
| xarray, multidimensional data, Zarr | 10 | [TerrIO xarray](https://terrio.dev/xarray/), [Multidimensional arrays](https://terrio.dev/multidim/), [xarray tutorials](https://tutorial.xarray.dev/) |
| Cloud discovery and remote data | 11 | [STAC](https://stacspec.org/en), [Remote data](https://terrio.dev/remote/) |
| HEC-RAS model outputs | Extension | [HEC-RAS guide](https://terrio.dev/hecras/); inspect simulation outputs without treating them as observations |
| Rasterio migration | Extension | [Coming from rasterio](https://terrio.dev/rasterio/) |
| Rust library, CLI, MCP | Extension | [Rust](https://terrio.dev/rust/), [CLI](https://terrio.dev/cli/), [MCP](https://terrio.dev/mcp/) |
| Reliability and conformance | 12, 13 | [Conformance](https://terrio.dev/conformance/), [Testing](https://terrio.dev/testing/), [Roadmap](https://terrio.dev/roadmap/) |

These extension references cover specialized formats such as CAD, GRIB, netCDF/HDF5, GeoParquet, tiles, and archives. Check the selected build's feature support before designing a lesson. Performance numbers from other systems are not measurements of this course.

## Further courses and videos

- [Introduction to GIS Programming](https://geog-312.gishub.org/) — Qiusheng Wu's course materials.
- [Spatial Data Management](https://geog-414.gishub.org/) — Qiusheng Wu's course materials.
- [Qiusheng Wu's video channel](https://www.youtube.com/@giswqs) — author-hosted geospatial demonstrations; select the relevant playlist and use captions where available.
- [NASA ARSET training](https://appliedsciences.nasa.gov/what-we-do/capacity-building/arset) — official remote-sensing courses and recorded sessions. Individual course materials may include third-party content; use their stated terms.
- [QGIS Training Manual](https://docs.qgis.org/latest/en/docs/training_manual/) — additional desktop GIS practice.
- [JupyterLite documentation](https://jupyterlite.readthedocs.io/) and [Jupyter Book documentation](https://jupyterbook.org/) — the publishing tools behind this course.

Videos are linked at their authors' original hosts. No video, transcript, screenshot, music, or third-party teaching material is copied into this repository. External pages may change or require cookies; the core lessons do not depend on watching a video.

## Native cloud extension

Use a full Python environment for real remote COG range reads. Install `terrio==0.9.0`, then follow the authors' [official quickstart notebook](https://github.com/opengeos/terrio/blob/main/docs/notebooks/quickstart.ipynb). Choose a small public asset, verify its provider's terms and CORS/range behavior, and record the exact URL and retrieval date. Compare a window to a whole-image request using measured bytes, not merely array dimensions. Remote datasets are not automatically public domain because the software is open source.

## Instructor guide

Ask learners to predict an output before running it. Give pairs different thresholds or grid sizes and have them reconcile their answers. Award the capstone 0–2 points for each of: question, provenance and rights, CRS/units, method and validity mask, reproducibility, sensitivity, accessible visuals, and limitations/citation (16 total). The score is a discussion aid, not a validated assessment instrument.

For a low-bandwidth session, distribute the executed book beforehand. An initial JupyterLite visit still needs runtime downloads, and the site does not claim full offline support. Save completed work locally before clearing browser data.
