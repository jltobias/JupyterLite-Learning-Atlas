# Data access and browser limits

The default lessons use original synthetic examples, authentic upstream CMIP6
warming-level windows, an authentic CDS catalogue snapshot, and Natural Earth
coastlines. **The repository does not bundle the full C3S gridded climate archive.**
Synthetic fields are deliberately labelled on every figure. Read `data/manifest.json`
for exact sources, revisions, licences, byte counts, hashes, and retrieval dates.

## Get an authentic regional series

1. Open the [official Atlas](https://atlas.climate.copernicus.eu/). Choose the
   dataset, variable, region, period, scenario where relevant, and statistic.
2. Read and save its information/provenance panel. Export the regional time-series
   data using the application's download controls. Preserve that original file.
3. Inspect the export header and columns. Product layouts differ. Select one
   series explicitly, retaining its model/member identity. Create a separate CSV
   with `date,value` columns, ISO month-start dates, and one row per month.
4. Represent missing values with blanks. Include missing months as rows instead
   of silently shortening the time axis. Do not interpolate without a stated method.
5. Create a JSON sidecar with `data_kind`, `source`, `variable`, `units`, `region`,
   `statistic`, `reference_period`, `licence`, and `transformations`. Add dataset
   version, access date, source citations, model/member, scenario, calendar, and
   source-file checksum. Describe whether values are absolute or anomalies.
6. In the Atlas Lab, open `courses/c3s-atlas/` in the file browser and upload
   `my_series.csv` and `my_series.json` beside `19-bring-real-data.ipynb`. The
   original source Lab uses its root directory; these are different layouts. Run Chapter 19. It validates the series and reports whether
   the optional real-data analysis actually ran.

This intentionally uses an explicit input contract rather than claiming to guess
every Atlas export layout. Compare your prepared values with the original export.

## Prepare a small gridded subset on your computer

Use the [CDS catalogue](https://doi.org/10.24381/cds.h35hb680) and
[API setup guide](https://cds.climate.copernicus.eu/how-to-api) to obtain a licensed
NetCDF file. Generate the request from the current CDS download form; available
periods and request keys can change. Keep credentials in your local CDS configuration,
outside notebooks and version control.

The following commands belong to the pinned source project, not the Atlas tree.
[Download or check out the complete source at commit b41c3e1098a4fb94cef48b3044fe19c6ce7c1a1a](https://github.com/jltobias/JupyterLite-C3S-Atlas/tree/b41c3e1098a4fb94cef48b3044fe19c6ce7c1a1a), then open a terminal in that source root. It supplies
`requirements-data.txt` and `scripts/prepare_netcdf.py`; the source script remains external
to the Atlas. In an isolated desktop environment, install those source requirements, then run:

```shell
python scripts/prepare_netcdf.py data/raw/my_atlas_file.nc my_series.csv --variable t --start 1991-01-01 --end 2020-12-31 --box 50 -10 40 10
```

Add `--member-dim member_id --member EXACT_LABEL` only when those are the real
dimension and coordinate labels in your file. The tool rejects unresolved extra
dimensions, irregular grids, incomplete monthly coverage, masked cells, and
nonstandard calendars. It exports a cosine-latitude-weighted mean over selected
cell centres, preserves units, and records original attributes and changes in JSON.
It does not regrid, bias-adjust, infer land masks, or average model members.

The bounding box is not a polygon clip. For coastlines, land-only fields, partial
cells, or irregular grids, adapt the coverage/mask method explicitly using the
official tools. Use a new output filename to preserve earlier exports.

## JupyterLite behaviour

Python runs on your device using Pyodide. The initial visit needs internet for the
runtime and packages. Plotly's book views use a versioned JavaScript CDN; standalone
map galleries bundle their JavaScript locally. No lesson sends your data to a server.
External resource requests still reach their providers.

Browser storage belongs to this browser/profile. Download edited notebooks and
results before clearing site data, switching browsers, or closing a private session.
Saving in Lab does not commit to GitHub. The published book contains precomputed
outputs; editing Python requires Lab or desktop Jupyter.

Use small subsets. The full CDS archive, authenticated API clients, Dask clusters,
ESMF-based regridding, and upstream native-library workflows belong in a desktop
or hosted scientific environment. WebGL must be enabled for 3D; use the companion
2D views and numerical tables if it is unavailable.
