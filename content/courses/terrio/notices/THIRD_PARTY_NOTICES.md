# Third-party notices

The [attribution ledger](book/attribution.md) is the human-readable source of data and software credits. `notebooks/data/sources.json` records the Natural Earth snapshot and checksum.

TerrIO 0.9.0, copyright Qiusheng Wu and TerrIO contributors, is redistributed in the built JupyterLite site as an unmodified upstream WebAssembly wheel. Its release-specific LICENSE, NOTICE, and LICENSE-THIRD-PARTY.md are retained in `licenses/terrio/` by `scripts/fetch_notices.py`. These include notices for upstream algorithms, data, and component exceptions; the repository's MIT license does not replace them.

JupyterLite's generated JavaScript bundles retain their license comments and companion license files. Pyodide's runtime is fetched from its upstream CDN with its original distribution. The portal's Plotly bundle is copied unmodified from the installed Plotly distribution, and its license is included in the build's `licenses/plotly/` directory. Other build dependencies are installed from their upstream Python packages and are not source-vendored here.

The site also carries unmodified, checksum-verified Python wheels for Plotly (MIT), xarray (Apache-2.0), Narwhals (MIT), and packaging (Apache-2.0 or BSD-2-Clause). Their upstream license files remain inside the wheels. Versions, URLs, and digests are recorded in `lite/support-wheel-lock.json`. NumPy, pandas, Matplotlib, and other runtime packages are supplied by the pinned Pyodide distribution.

Natural Earth: Tom Patterson, Nathaniel Vaughn Kelso, and contributors. **Made with Natural Earth.** [Public-domain terms](https://www.naturalearthdata.com/about/terms-of-use/). No third-party basemap tiles, terrain services, satellite imagery, or video files are redistributed.
