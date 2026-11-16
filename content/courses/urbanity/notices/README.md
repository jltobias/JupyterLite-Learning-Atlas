<div align="center">

<img src="book/_static/urbanity-splash.svg" alt="Illustration of city streets becoming a connected urban graph" width="100%">

# JupyterLite × Urbanity

**Explore how city streets, buildings, places, and people form connected urban systems.**

[![Open the Jupyter Book](https://img.shields.io/badge/Explore-Jupyter%20Book-2b6cb0?style=for-the-badge)](https://jltobias.github.io/JupyterLite-Urbanity/)
[![Launch JupyterLite Lab](https://img.shields.io/badge/Launch-JupyterLite%20Lab-f6ad55?style=for-the-badge)](https://jltobias.github.io/JupyterLite-Urbanity/lab/lab/index.html)

</div>

This companion guide introduces [Urbanity](https://github.com/winstonyym/urbanity), a Python package from the [NUS Urban Analytics Lab](https://ual.sg/) for building feature-rich urban networks and graphs. Read the chapters, run the lightweight browser notebooks, and follow the links to the full Urbanity documentation and data.

> **About the browser notebooks:** Urbanity itself depends on geospatial and compiled Python libraries that are not currently a dependable fit for the Pyodide browser kernel. The JupyterLite notebooks therefore use small, explicitly synthetic networks to teach the ideas without pretending to execute Urbanity. Each chapter pairs that runnable exploration with the corresponding native Urbanity workflow. For live OSM, geospatial, imagery, or graph-ML analysis, use the [native installation guide](https://urbanity.readthedocs.io/en/latest/installation/).

## Open the interactive exhibits

| Exhibit | What to explore |
|---|---|
| [**2D Maps**](https://jltobias.github.io/JupyterLite-Urbanity/exhibits/2d-map.html) | A small illustrative street network; toggle the street, building, and people layers. |
| [**3D Maps**](https://jltobias.github.io/JupyterLite-Urbanity/exhibits/3d-map.html) | Compare schematic building-height and network layers in an isometric view. |
| [**3D Scenes**](https://jltobias.github.io/JupyterLite-Urbanity/exhibits/3d-scene.html) | Rotate an illustrative urban graph and inspect its linked spatial layers. |

These are original, local, synthetic teaching exhibits—not measured city maps, outputs of the Urbanity package, or substitutes for a geospatial viewer. They require no API key or third-party map tiles.

## Learning path

1. [Start here: a city as a network](https://jltobias.github.io/JupyterLite-Urbanity/start-here.html)
2. [Street networks and centrality](https://jltobias.github.io/JupyterLite-Urbanity/notebooks/street-networks.html)
3. [Urban graphs and spatial layers](https://jltobias.github.io/JupyterLite-Urbanity/notebooks/urban-graphs.html)
4. [Buildings, people, and urban context](https://jltobias.github.io/JupyterLite-Urbanity/notebooks/urban-context.html)
5. [Street-view and satellite imagery](https://jltobias.github.io/JupyterLite-Urbanity/notebooks/imagery.html)
6. [Visualising urban networks](https://jltobias.github.io/JupyterLite-Urbanity/notebooks/visualisation.html)
7. [Graph machine learning](https://jltobias.github.io/JupyterLite-Urbanity/notebooks/graph-ml.html)
8. [Reproducibility, export, and next steps](https://jltobias.github.io/JupyterLite-Urbanity/notebooks/reproducibility.html)

The chapters render as a [Jupyter Book](https://jltobias.github.io/JupyterLite-Urbanity/); use **Launch JupyterLite Lab** above to open and edit the notebooks in your browser. The browser kernel runs Python locally; no account or server-side notebook is needed.

## What Urbanity can help you explore

- **Street networks:** request drive, walk, bike, or other networks; work with street segments and intersections; calculate network indicators and centrality.
- **Heterogeneous urban graphs:** connect plots, buildings, streets, and intersections through explicit spatial relationships.
- **Urban context:** enrich networks with building morphology, population, land-use, and related attributes.
- **Imagery:** workflows for street-view imagery and satellite / remote-sensing layers, subject to provider access, terms, and credentials.
- **Analysis and communication:** compute network indicators and centrality, compare neighbourhoods or cities, explore network assortativity, create static and interactive visualisations, and export graph data.
- **Graph machine learning:** prepare graph data for supported PyTorch Geometric or DGL workflows in an appropriately provisioned native environment.

See the [official Urbanity documentation](https://urbanity.readthedocs.io/en/latest/) for the authoritative API reference, supported data sources, current examples, and installation requirements. The [upstream repository](https://github.com/winstonyym/urbanity) and [Urbanity examples repository](https://github.com/winstonyym/urbanity_examples) are maintained separately from this educational companion.

For reuse instead of building from scratch, see the upstream [Global Feature-Rich Urban Network Dataset](https://figshare.com/articles/dataset/Global_Urban_Network_Dataset/22124219) and [Global Urban Graph Dataset](https://figshare.com/articles/dataset/Global_Graph_Dataset/28852319). Check each dataset's documentation, version, coverage, and licence before use.

## Run Urbanity in a native environment

The browser notebooks are for learning the concepts. To execute the real package and access geospatial dependencies, follow the [official installation instructions](https://urbanity.readthedocs.io/en/latest/installation/) and the tutorials for [street networks](https://urbanity.readthedocs.io/en/latest/tutorials/street-networks/) and [urban graphs](https://urbanity.readthedocs.io/en/latest/tutorials/urban-graphs/). A representative native workflow is:

```python
from urbanity import Map

city = Map(country="Singapore")
city.add_polygon_boundary("path/to/study-area.geojson")
graph, nodes, edges = city.get_street_network(
    bandwidth=100,
    network_type="driving",
    graph_attr=True,
)

urban_graph = city.get_urban_graph(bandwidth=100)
urban_graph.initialize_edges(building_neighbours="knn", knn=3, distance=100)
```

The exact data sources, optional features, and access requirements vary. Some imagery and external data workflows require credentials or separate provider terms; keep tokens out of notebooks committed to Git.

## Build locally

Use Python with the packages listed in [`requirements.txt`](requirements.txt). From the repository root:

```console
jupyter-book build book
jupyter lite build --config jupyter_lite_config.py --contents book --output-dir _build/lab
```

The GitHub Actions workflow publishes the book, browser lab, and exhibits to GitHub Pages when changes are pushed to `main`. Enable **Settings → Pages → Build and deployment → GitHub Actions** in the repository once, then use the live links above. The JupyterLite build uses relative URLs under `/lab/`; adjust its base URL if you publish under a different layout.

## Attribution and citation

Urbanity is a separate project; this companion is not an official product of or endorsed by its maintainers. If you use Urbanity in research or a publication, cite the relevant primary work. The core package paper is:

> Yap, W., Stouffs, R., & Biljecki, F. (2023). Urbanity: automated modelling and analysis of multidimensional networks in cities. *npj Urban Sustainability, 3*, 45. https://doi.org/10.1038/s42949-023-00125-w

Depending on the features and datasets used, also cite the relevant work listed in the [official Urbanity citation guide](https://urbanity.readthedocs.io/en/latest/changelog/):

- **Street-view semantic understanding:** Yap, W., Chang, J. H., & Biljecki, F. (2023). Incorporating networks in semantic understanding of streetscapes. *Environment and Planning B: Urban Analytics and City Science, 50*(6), 1416–1437. https://doi.org/10.1177/23998083221138832
- **Global feature-rich network dataset:** Yap, W., & Biljecki, F. (2023). A Global Feature-Rich Network Dataset of Cities. *Scientific Data, 10*, 667. https://doi.org/10.1038/s41597-023-02578-1
- **Urban graph analytics:** Yap, W., & Biljecki, F. (2025). Leveraging Urban Graphs for Multi-Scalar Urban Analytics. *CUPUM 2025*. https://doi.org/10.17605/OSF.IO/ABYQH
- **Building operating carbon (when relevant):** Yap, W., Wu, A. N., Miller, C., & Biljecki, F. (2025). Revealing building operating carbon dynamics for multiple cities. *Nature Sustainability, 8*(1), 1199–1210. https://doi.org/10.1038/s41893-025-01615-8

Urbanity's upstream repository is distributed under the [MIT License](https://github.com/winstonyym/urbanity/blob/main/LICENSE); retain its copyright and license notice when redistributing portions of that software. Cite and attribute underlying data and imagery separately under their own licenses and terms—for example [OpenStreetMap's attribution and ODbL requirements](https://www.openstreetmap.org/copyright), as well as the relevant population, building, street-view, and satellite providers. The synthetic diagrams and toy networks in this companion are not Urbanity outputs and do not represent actual places.

## Acknowledgements

With thanks to [Winston Yap](https://github.com/winstonyym), the Urbanity contributors, and the [NUS Urban Analytics Lab](https://ual.sg/) for creating and maintaining Urbanity and its documentation. This repository is an independent learning companion.
