# A geospatial field guide

[Source image continuation: Original conceptual terrain, raster layers, points, and globe](https://github.com/jltobias/JupyterLite-terrio/blob/18574d4e7a8dabb99d3db65b20c6180185578482/assets/terrio-cover.png)

Learn how a geospatial file becomes an explanation. This independent educational companion to [TerrIO](https://terrio.dev/) combines a readable Jupyter Book, a browser-based JupyterLite Lab, and small experiments you can inspect and change.

<p><a href="https://github.com/jltobias/JupyterLite-terrio/blob/18574d4e7a8dabb99d3db65b20c6180185578482/lite/lab/index.html?path=01-first-contact.ipynb"><strong>Launch JupyterLite Lab</strong></a> · <a href="https://github.com/jltobias/JupyterLite-terrio/blob/18574d4e7a8dabb99d3db65b20c6180185578482/maps/2d.html">2D maps</a> · <a href="https://github.com/jltobias/JupyterLite-terrio/blob/18574d4e7a8dabb99d3db65b20c6180185578482/maps/3d.html">3D maps</a> · <a href="https://github.com/jltobias/JupyterLite-terrio/blob/18574d4e7a8dabb99d3db65b20c6180185578482/maps/scenes.html">3D scenes and globe</a></p>

## Read, run, question

Read the chapter's scientific question, predict the result, run the code, and explain what changes when you alter an assumption. The book contains executed outputs. JupyterLite contains editable copies of the same source notebooks. Each chapter runs independently and takes roughly 30–45 minutes.

The course covers TerrIO's core raster, vector, coordinate, point-cloud, and xarray workflows. Advanced formats and interfaces are mapped to official references in [Resources](resources.md); this is a curated introduction, not a promise to demonstrate every TerrIO driver or operation.

## What is real and what is invented?

The country outlines are Natural Earth public-domain data. The terrain, reflectance, station locations, point clouds, seasonal temperature cube, and scene transect are **synthetic teaching data**. They must not be interpreted as observations. The cover is an AI-generated conceptual illustration; chapter title cards are original vector diagrams.

## Browser essentials

Use a recent Chrome, Edge, Firefox, or Safari browser. The first launch downloads Python and packages and can take several minutes. Select **Python (Pyodide)** and **Run → Run All Cells**. Browser storage is separate from this repository: download your edited notebooks and results to keep or share them. Clearing site data can remove your work.

The runtime is pinned to Pyodide 0.29 because TerrIO 0.9.0's wheel uses its ABI. The browser Python package reads files after they have been downloaded; native HTTP range access is a separate extension activity. Plotly interactive views load a versioned script from its CDN; 3D requires WebGL. Every chapter includes numerical output or a static plot as a reading alternative.

## Learning paths

- **First map, 90 minutes:** chapters 1–3, then the 2D gallery.
- **Terrain workshop, half day:** chapters 5–6, 8–9, then the capstone.
- **Data stewardship, half day:** chapters 3, 7, 10–12, with the attribution ledger.
- **Full course:** all 13 chapters, plus the capstone report and peer discussion.

Read [Resources and training](resources.md), [Attribution and reuse](attribution.md), and [Contributor guide](contributing.md) for next steps.
