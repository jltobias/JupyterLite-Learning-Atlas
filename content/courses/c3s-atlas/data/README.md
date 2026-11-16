# Bundled data

`reference/` contains unmodified public source bytes; `manifest.json` records exact
provenance and SHA-256 checksums. The CMIP6 warming-level table is a real auxiliary
product from C3S Atlas User Tools, not a gridded climate observation. Its `NA` and
`9999` tokens are retained, never converted to dates or zero values.

`examples/monthly_series.csv` is a **synthetic** import fixture with a JSON sidecar.
Its values come from the documented seeded teaching generator in `atlas_helpers.py`.
No fictional numbers are labelled as downloaded Copernicus data.

Coastlines: Made with Natural Earth (public domain), by Nathaniel Vaughn Kelso,
Tom Patterson and contributors. Source licences are in the repository `licenses/`.

See the book's data guide for authentic Atlas exports and NetCDF preparation.
