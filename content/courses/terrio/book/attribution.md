# Attribution, citations, and reuse

This course uses original explanations and synthetic measurements, one public-domain map dataset, and openly licensed software. Open-source software is usually copyrighted; its license permits use under conditions. Third-party prose, artwork, videos, and restricted datasets are not copied into the course. Links to authors' original materials do not transfer their rights.

## Data and visual assets

| Asset | Creator / source | Rights and credit | Modifications / limits |
|---|---|---|---|
| `notebooks/data/countries.geojson` | Natural Earth: Tom Patterson, Nathaniel Vaughn Kelso, and contributors; 1:110m Admin 0 Countries v5.1.2 | [Public-domain terms](https://www.naturalearthdata.com/about/terms-of-use/). **Made with Natural Earth.** | Original upstream GeoJSON bytes; plots show derived outlines and counts. Generalized boundaries; not authoritative legal boundaries. |
| Terrain, reflectance, points, stations, seasonal cube, capstone mask | JupyterLite-terrio contributors | Original synthetic teaching data, dedicated under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) to the extent rights exist | Deterministic generation in notebook code; no observational or survey meaning. |
| Cover image | Generated with OpenAI's built-in image-generation tool for this repository, 2026-11-15 | Original AI-generated conceptual illustration; no third-party image was supplied | Not a real map or scientific observation; see `assets/ARTWORK.md` for prompt and provenance. |
| Chapter title cards | JupyterLite-terrio contributors | Original programmatic SVG illustrations; CC0 1.0 to the extent rights exist | Mathematical contours are decorative. |
| Charts, maps, 3D surfaces and globe | Original course code; Natural Earth where geographic outlines appear | Cite this course, the relevant data source, and plotting software | Units, synthetic status, and display exaggeration are labelled. |
| External videos and training | Respective authors / hosts | Linked only; retain original host terms | No copies or transcripts redistributed. |

The data manifest `notebooks/data/sources.json` records the upstream URL, version, retrieval date, and SHA-256. Build and test scripts check the checksum. Browser lessons use this local snapshot rather than silently changing with an online dataset.

## Cite TerrIO

Qiusheng Wu, Mavrick Fitzgerald, and Guillermo Morales Sanchez (2026). *terrio: Pure-Rust geospatial raster, vector and point cloud data I/O*. Zenodo. [https://doi.org/10.5281/zenodo.23642204](https://doi.org/10.5281/zenodo.23642204).

This is the concept DOI reported in the authors' [CITATION.cff](https://github.com/opengeos/terrio/blob/main/CITATION.cff); it resolves to the project archive and may point to a later release. This course executes **TerrIO 0.9.0**. Use a release-specific DOI when the archive provides one for the exact release you used. See the authors' [citation guide](https://terrio.dev/citation/).

## TerrIO and its foundations

TerrIO is copyright Qiusheng Wu and TerrIO contributors, under MIT with component exceptions. The browser wheel is redistributed with its packaged notices; the site also includes the upstream release's [LICENSE](https://github.com/opengeos/terrio/blob/v0.9.0/LICENSE), [NOTICE](https://github.com/opengeos/terrio/blob/v0.9.0/NOTICE), and [third-party license inventory](https://github.com/opengeos/terrio/blob/v0.9.0/LICENSE-THIRD-PARTY.md). The build copies those documents into the deployed `licenses/` directory.

Credit the upstream foundations identified by TerrIO: John Lindsay and **whitebox_next_gen**; Frank Warmerdam, Even Rouault, and **GDAL** contributors; Gerald Evenden and **PROJ** contributors; Hobu, Inc. and **PDAL** contributors; **GeoRust**, **JTS**, **GEOS**, **CSF**, **rasterio**, **xarray**, and **rioxarray** authors. The full notices specify the applicable terms, including MIT, Apache-2.0, and MPL-2.0 components. Do not describe the entire dependency graph as public domain or uniformly MIT.

Coordinate definitions in TerrIO derive in part from the **EPSG Geodetic Parameter Dataset**, copyright **International Association of Oil & Gas Producers (IOGP)**, under its [terms of use](https://epsg.org/terms-of-use.html), and Esri projection-engine data under Apache-2.0. The course uses the definitions through TerrIO rather than copying a separate coordinate database. TerrIO's notices retain their attribution.

## Publishing and visualization software

Credit **Project Jupyter**, **JupyterLite** and **Pyodide** contributors for browser execution; **Executable Books / Jupyter Book** and **Sphinx** contributors for publishing; **NumPy**, **Matplotlib**, **Plotly**, **pandas**, and **xarray** contributors for numerical and visual tools; and **Narwhals** and **packaging** contributors for supporting libraries. Jupyter components commonly use BSD licenses; Pyodide uses MPL-2.0; Plotly and Narwhals use MIT; xarray uses Apache-2.0; packaging is Apache-2.0 or BSD-2-Clause; Matplotlib has its own BSD-compatible license. Unmodified Plotly, xarray, Narwhals, and packaging wheels are served with the site and retain their upstream license files. Their versions and checksums are recorded in `lite/support-wheel-lock.json`. Other installed distributions and generated bundles also retain their respective licenses. No institutional or product endorsement is implied.

This repository's original code is MIT-licensed. Original teaching text, SVG title cards, and synthetic data are offered under CC0 1.0. Third-party data and dependencies keep their own terms. AI-generated imagery is identified separately, with no assertion of exclusive copyright. See the root `LICENSE` and `THIRD_PARTY_NOTICES.md`.

## Cite this course

Use the repository's `CITATION.cff`, and include the commit identifier or release tag and access date. No DOI has been minted for this course; do not substitute TerrIO's DOI for the course itself. Attribution and links were checked on **2026-11-15**.
