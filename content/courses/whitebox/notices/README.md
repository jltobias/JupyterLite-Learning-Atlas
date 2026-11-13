# JupyterLite-Whitebox

Interactive, browser-based notebooks for learning the **WhiteboxTools Python API** with JupyterLite.

> **Important compatibility note:** the `whitebox` PyPI package is a Python front end around the native WhiteboxTools executable. JupyterLite runs Python in WebAssembly in the browser and cannot launch native subprocess executables. These notebooks therefore use JupyterLite for API discovery, signatures/docstrings, workflow design, and browser-safe visual demonstrations. Cells that actually execute WhiteboxTools are clearly marked for a normal Python kernel (local Jupyter, Binder, Colab, etc.).

## Live links

- [Open the JupyterLite notebook collection](https://jltobias.github.io/JupyterLite-Whitebox/)
- [Open the JupyterBook](https://jltobias.github.io/JupyterLite-Whitebox/book/)

Direct notebook links:

- [Welcome](https://jltobias.github.io/JupyterLite-Whitebox/lab/index.html?path=00_Welcome.ipynb)
- [Architecture and compatibility](https://jltobias.github.io/JupyterLite-Whitebox/lab/index.html?path=01_Architecture_and_Compatibility.ipynb)
- [Data Tools](https://jltobias.github.io/JupyterLite-Whitebox/lab/index.html?path=02_Data_Tools.ipynb)
- [GIS Analysis](https://jltobias.github.io/JupyterLite-Whitebox/lab/index.html?path=03_GIS_Analysis.ipynb)
- [Hydrological Analysis](https://jltobias.github.io/JupyterLite-Whitebox/lab/index.html?path=04_Hydrological_Analysis.ipynb)
- [Image Analysis](https://jltobias.github.io/JupyterLite-Whitebox/lab/index.html?path=05_Image_Analysis.ipynb)
- [LiDAR Analysis](https://jltobias.github.io/JupyterLite-Whitebox/lab/index.html?path=06_LiDAR_Analysis.ipynb)
- [Mathematical and Statistical Analysis](https://jltobias.github.io/JupyterLite-Whitebox/lab/index.html?path=07_Math_and_Stats.ipynb)
- [Stream Network Analysis](https://jltobias.github.io/JupyterLite-Whitebox/lab/index.html?path=08_Stream_Network_Analysis.ipynb)
- [Terrain Analysis](https://jltobias.github.io/JupyterLite-Whitebox/lab/index.html?path=09_Terrain_Analysis.ipynb)
- [API Catalog](https://jltobias.github.io/JupyterLite-Whitebox/lab/index.html?path=10_API_Catalog.ipynb)

## Try the JupyterLite site

After GitHub Pages is enabled with **GitHub Actions** as its source and the deployment workflow has run:

**https://jltobias.github.io/JupyterLite-Whitebox/**

The repository is organized as a chapter-style JupyterLite collection around the high-level Whitebox tool categories:

1. Welcome and runtime check
2. Whitebox + JupyterLite architecture
3. Data Tools
4. GIS Analysis
5. Hydrological Analysis
6. Image Analysis
7. LiDAR Analysis
8. Mathematical & Statistical Analysis
9. Stream Network Analysis
10. Terrain Analysis
11. Searchable Whitebox API catalog

## What runs in the browser?

The current `whitebox` package is distributed as a pure Python wheel, so JupyterLite/Pyodide can install the Python front end and inspect the `WhiteboxTools` class. The notebooks use Python's `inspect` module to show available methods, signatures, and documentation without instantiating `WhiteboxTools` (instantiation downloads/uses the native executable).

Browser-safe notebooks also use NumPy and Matplotlib for small conceptual demonstrations. They do **not** claim to reproduce the WhiteboxTools algorithms.

To execute WhiteboxTools itself, use a standard Python environment:

```bash
python -m pip install whitebox
```

```python
import whitebox
wbt = whitebox.WhiteboxTools()
print(wbt.version())
```

The upstream interactive tutorial is also available through the Whitebox Python project: https://github.com/opengeos/whitebox-python/blob/master/examples/whitebox.ipynb

## Attribution and upstream projects

WhiteboxTools is an advanced geospatial analysis platform developed by **Prof. John Lindsay** at the University of Guelph's Geomorphometry and Hydrogeomatics Research Group. The `whitebox` Python frontend is maintained by **Dr. Qiusheng Wu** / Open Geospatial Solutions and provides a Python interface to WhiteboxTools.

Please cite and credit the upstream projects when using them in teaching, research, or publications:

- WhiteboxTools: https://github.com/jblindsay/whitebox-tools
- WhiteboxTools manual: https://www.whiteboxgeo.com/manual/wbt_book/intro.html
- `whitebox` Python frontend: https://github.com/opengeos/whitebox-python
- `whitebox` on PyPI: https://pypi.org/project/whitebox/
- `whitebox` documentation: https://whitebox.readthedocs.io/
- Original tutorial notebook: https://github.com/opengeos/whitebox-python/blob/master/examples/whitebox.ipynb

WhiteboxTools and the `whitebox` Python frontend are distributed under the MIT license. This repository is an independent educational project and is not an official Whitebox project.

## Local build

```bash
python -m pip install -r requirements.txt
jupyter lite build --contents content --output-dir dist
python -m http.server -d dist 8000
```

Then open `http://localhost:8000`.

## GitHub Pages

The workflow in `.github/workflows/deploy.yml` builds the site on pull requests and deploys it from `main`. In **Settings → Pages**, set **Source** to **GitHub Actions** once for this repository.

## Contributing

New chapters should be small, reproducible, and explicit about execution context:

- **JupyterLite-safe:** API inspection, text, tables, NumPy/Matplotlib demonstrations.
- **Native WhiteboxTools required:** any call that instantiates `whitebox.WhiteboxTools()` or launches a Whitebox tool.

Where an example is adapted from upstream Whitebox material, keep the attribution and source link with the example.
