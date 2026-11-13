# Open datasets and execution notes

| Dataset | Format | Source | Main uses |
|---|---|---|---|
| Meuse | CSV/vector | [spData](https://github.com/Nowosad/spData) | Spatial statistics and exploratory GIS |
| North Carolina SIDS | GeoPackage | [spdep SIDS article](https://r-spatial.github.io/spdep/articles/sids.html) | County attributes and zonal summaries |
| DEM | GeoTIFF | [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) or [EarthExplorer](https://earthexplorer.usgs.gov/) | Terrain and hydrology |
| LiDAR | LAS/LAZ | [OpenTopography](https://opentopography.org/) | Point-cloud and surface analysis |
| Hydrography | Vector | [USGS NHD](https://www.usgs.gov/national-hydrography) or [OpenStreetMap](https://www.openstreetmap.org/) | Stream comparison and network analysis |

JupyterLite supports API discovery, metadata, and small NumPy demonstrations in the browser. Operations requiring native raster drivers, GeoPackage support, LAS/LAZ files, or the Whitebox executable are guarded in the notebooks. Download small subsets, record CRS and license, and run native cells with a local Python kernel after installing `whitebox`.

