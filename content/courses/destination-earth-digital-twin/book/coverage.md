---
title: Coverage and learning paths
---

These canonical notebooks serve both book and Lab. All default exercises are original and synthetic; official connections and production models remain outside the browser implementation.

| Notebook | Runnable learning goal |
|---|---|
| [A digital twin is a connected system](../01-system.ipynb) | Trace the roles of platform, data lake and twin engine; measure a small data pipeline. |
| [Coordinates, grids and units](../02-grids.ipynb) | Inspect coordinate conventions; convert temperature units without losing metadata. |
| [Data access without credentials in the browser](../03-access.ipynb) | Describe discovery, selection and export; distinguish a query plan from a live request. |
| [Validate a small authorized export](../04-validation.ipynb) | Reject malformed values and missing provenance; keep real imports separate from synthetic examples. |
| [Labeled arrays and regional selection](../05-labelled-arrays.ipynb) | Use xarray dimensions and units; avoid positional indexing mistakes. |
| [Area weighting changes the answer](../06-area-means.ipynb) | Calculate cosine-weighted means; test conservation for a constant field. |
| [Anomalies and baseline choices](../07-climate.ipynb) | Compute a baseline anomaly; distinguish a demonstration trend from a climate projection. |
| [Thresholds and event duration](../08-extremes.ipynb) | Detect exceedance runs; compare absolute and percentile thresholds. |
| [A water budget with a conservation check](../09-water.ipynb) | Implement a toy catchment bucket; close the mass balance. |
| [Vector fields and derived wind speed](../10-wind.ipynb) | Calculate vector magnitude; inspect direction without confusing components with speed. |
| [Interpolation and its assumptions](../11-interpolation.ipynb) | Sample between grid points; distinguish interpolation from new information. |
| [Ensembles and uncertainty bands](../12-ensembles.ipynb) | Summarize member spread; distinguish uncertainty types. |
| [Skill scores and reference forecasts](../13-verification.ipynb) | Compute bias and RMSE; compare against a declared baseline. |
| [Honest two-dimensional maps](../14-maps.ipynb) | Use fixed color limits across time; separate rendering choices from physical change. |
| [From longitude and latitude to a projected plane](../15-projections.ipynb) | Calculate a spherical Mercator projection; diagnose polar distortion. |
| [A three-dimensional terrain scene](../16-terrain.ipynb) | Create a surface from a grid; describe vertical exaggeration explicitly. |
| [Put a field on a globe](../17-globe.ipynb) | Transform spherical coordinates to Cartesian coordinates; verify radius. |
| [Time slices, animation and stable scales](../18-time.ipynb) | Build comparable frames; measure field change rather than relying on motion. |
| [Build an analytical dashboard](../19-dashboard.ipynb) | Coordinate a map, time series and distribution; retain units and provenance. |
| [Browser memory and precision](../20-performance.ipynb) | Estimate array costs; quantify float32 approximation error. |
| [Reproducible methods and provenance](../21-reproducibility.ipynb) | Test random seeds; record transformations and hash an artifact. |
| [A transparent adaptation comparison](../22-capstone.ipynb) | Combine ensemble summaries, threshold exposure and a decision table; state limits. |
| [Digital Twin Engine: workflow and HPC roles](../23-dte-workflows.ipynb) | Model a dependency graph and its critical path; separate local orchestration patterns from HPC execution. |
| [Polytope: select a feature, not a whole cube](../24-polytope.ipynb) | Compare rectangular and trajectory-shaped selections; draft a catalog-grounded request plan. |
| [Earthkit and a server-to-browser export boundary](../25-earthkit-export.ipynb) | Design a small, explicit export contract; validate units and provenance after serialization. |
| [Data Lake services: discovery, compute and hooks](../26-data-lake.ipynb) | Connect HDA/STAC discovery concepts with a local manifest; validate an event-driven processing contract. |
| [AI and ML: a time-aware baseline](../27-ai-validation.ipynb) | Fit a simple regression with held-out future samples; detect temporal leakage. |
| [Regional on-demand extremes and nested scales](../28-regional-extremes.ipynb) | Compare coarse and fine sampling of a localized event; measure what a coarse grid misses. |
| [Land processes: snow storage and melt](../29-land.ipynb) | Partition precipitation and close a snow-water budget. |
| [Waves: forcing, response time and memory](../30-waves.ipynb) | Compare a wind-driven target with a delayed response. |
| [Sea ice: bounded fractions and seasonal response](../31-sea-ice.ipynb) | Preserve fraction bounds and distinguish masked land from open water. |
| [Ocean layers: heat exchange and conservation](../32-ocean.ipynb) | Couple two reservoirs and verify an energy budget. |

## Capability boundaries

| Area | Implemented here | Official or server-assisted work |
|---|---|---|
| Architecture / DTE | Dependency graph and critical path | HPC allocation, model execution, workflow services |
| Data / Polytope | Grid/trajectory selection and request planning | Authenticated catalog requests and official extraction |
| Earthkit / GRIB | Validated JSON export boundary | Native decoding and authorized retrieval |
| Data Lake | Manifest filtering and duplicate-event handling | HDA/STAC, Islet/Stack, Hook/DEFAIR/MLOps services |
| Climate / extremes | Anomalies, thresholds, ensembles, nested sampling | Climate simulations and global/regional on-demand forecasts |
| AI / ML | Held-out temporal regression baseline | Operational model development and validation |
| Maps and scenes | Matplotlib, Python widgets, Canvas maps/3D/globe/dashboard | Authoritative geospatial data and production viewers |
| Reproducibility | Assertions, provenance and automated builds | Service-level governance |

Lessons 23–28 connect scientific foundations to named DestinE interfaces through explicit local simulations of a pattern, not substitute service clients.

ECMWF's [ML Earth-system components](https://destine.ecmwf.int/ml-earth-system-components/) include land, waves, hydrology, sea ice and ocean. Lessons 29–32 introduce selected processes for four of these; [lesson 09](../09-water.ipynb) covers a hydrological storage balance. [Lesson 27](../27-ai-validation.ipynb) supplies a shared temporal-validation exercise. These equations are original teaching models, not copies or implementations of the official trained components. Refer to [AI in DestinE](https://destine.ecmwf.int/ai-in-destination-earth/) for ECMWF's ML program and its connection to Anemoi and AIFS.

## The five Digital Twin Engine roles

ECMWF identifies five roles for the [Digital Twin Engine](https://destine.ecmwf.int/digital-twin-engine/). This mapping connects each role to an executable teaching exercise and states what requires the official infrastructure.

| DTE role | Chapters to run | Production boundary |
|---|---|---|
| Performance | [Memory and precision](../20-performance.ipynb), [workflow timing](../23-dte-workflows.ipynb) | Accelerator portability and EuroHPC performance are not benchmarked by a browser exercise. |
| Integration | [System pipeline](../01-system.ipynb), [workflow dependencies](../23-dte-workflows.ipynb), [regional scales](../28-regional-extremes.ipynb) | Coupled models, initialization, scheduling and allocations require the official modeling environment. |
| Data handling | [Selection](../03-access.ipynb), [Polytope concepts](../24-polytope.ipynb), [validated exports](../25-earthkit-export.ipynb), [Data Lake patterns](../26-data-lake.ipynb) | Authentic catalogs, extraction, streaming and native-format decoding use authorized services and suitable runtimes. |
| Interactivity | [Maps](../14-maps.ipynb), [terrain](../16-terrain.ipynb), [globe](../17-globe.ipynb), [time](../18-time.ipynb), [dashboard](../19-dashboard.ipynb) | Local visual controls do not steer a production simulation. |
| Machine learning | [Uncertainty](../12-ensembles.ipynb), [verification](../13-verification.ipynb), [temporal validation](../27-ai-validation.ipynb) | The regression lesson is an original baseline, not an operational Earth-system ML component. |
