# Start here: a city as a network

Urbanity turns spatial features into connected objects that can be measured and compared. The core mental model is simple:

```{image} _static/urbanity-pipeline.svg
:alt: Study area and urban data flow through network construction, analysis, and visualisation.
:width: 100%
```

| From | To | Example question |
|---|---|---|
| A study boundary | Street segments and intersections | How connected are the routes through this neighbourhood? |
| Plots and buildings | A multi-layer urban graph | Which buildings are near a street, plot, or neighbour? |
| Contextual datasets | Attributes on urban objects | How do building form or population relate to network structure? |
| Graph structure and labels | An analysis or graph-learning task | Can a model predict an attribute while respecting spatial relationships? |

## Use the book and lab

1. Read each chapter and open its notebook with **Launch in JupyterLite**.
2. Run the cells marked **Try it** and change the small example values.
3. Use the **Native Urbanity workflow** sections to continue with the actual package in a supported Python environment.
4. Explore the independent [2D map](https://jltobias.github.io/JupyterLite-Urbanity/exhibits/2d-map.html), [3D map](https://jltobias.github.io/JupyterLite-Urbanity/exhibits/3d-map.html), and [3D scene](https://jltobias.github.io/JupyterLite-Urbanity/exhibits/3d-scene.html) exhibits.

These pages deliberately label the illustrative geometries as synthetic. They are explanatory pictures, not evidence about a real city.

## When to leave the browser

The real package includes geospatial workflows and libraries such as GeoPandas, rasterio, PyDeck, and optional OSM tooling. Those dependencies and external data services are not provided by the browser kernel. Follow Urbanity's [official installation guide](https://urbanity.readthedocs.io/en/latest/installation/) for the full environment; visit the official [quickstart](https://urbanity.readthedocs.io/en/latest/quickstart/) and [API reference](https://urbanity.readthedocs.io/en/latest/api/) for the latest interfaces.

```{admonition} A note on live data, credentials, and licensing
Network downloads and imagery services may need API credentials, network access, and provider-specific attribution. Do not put secret tokens in shared notebooks. Read the source terms before downloading, redistributing, or publishing derived datasets.
```

## Chapters

- [Street networks and centrality](https://jltobias.github.io/JupyterLite-Urbanity/notebooks/street-networks.html)
- [Urban graphs and spatial layers](https://jltobias.github.io/JupyterLite-Urbanity/notebooks/urban-graphs.html)
- [Buildings, people, and urban context](https://jltobias.github.io/JupyterLite-Urbanity/notebooks/urban-context.html)
- [Street-view and satellite imagery](https://jltobias.github.io/JupyterLite-Urbanity/notebooks/imagery.html)
- [Visualising urban networks](https://jltobias.github.io/JupyterLite-Urbanity/notebooks/visualisation.html)
- [Graph machine learning](https://jltobias.github.io/JupyterLite-Urbanity/notebooks/graph-ml.html)
- [Reproducibility, export, and next steps](https://jltobias.github.io/JupyterLite-Urbanity/notebooks/reproducibility.html)
