---
title: Official access and a safe export boundary
---

The browser demonstrations are independent synthetic exercises. They do not authenticate to Destination Earth, retrieve restricted fields, create cloud resources or submit simulations.

## Identify the service before writing a request

Start with the [Destination Earth service catalog](https://platform.destine.eu/services/) and [registration/access FAQ](https://platform.destine.eu/support-faq/). Registration is not a promise that every service, dataset or computing capability is available to every user. Some services require additional approval or resources.

The [Digital Twin Engine](https://destine.ecmwf.int/digital-twin-engine/) supports workflows around the twins. [Polytope](https://polytope.readthedocs.io/en/stable/) provides feature-oriented extraction. The [Data Lake documentation](https://destine-data-lake-docs.data.destination-earth.eu/en/latest/) describes HDA and discovery/access interfaces, plus Islet, Stack, Hook, DEFAIR and MLOps Studio. Read each interface's documentation and entitlement requirements.

## A real-data workflow

1. Register and obtain required service authorization in the official interface.
2. Discover the dataset and inspect variables, experiment, time, grid, units and provenance. Obtain the request from the current catalog/client example; do not guess collection IDs.
3. Read the dataset license and [Data Lake terms](https://data.destination-earth.eu/terms-and-conditions). Restrictions can differ by service and collection. Older generic data-policy descriptions do not override current applicable terms.
4. Retrieve and decode the permitted selection in an appropriate local or server environment. Keep credentials there using the service's documented mechanism. Native GRIB, netCDF, projection or authentication dependencies may require server-side processing.
5. Record source, license, retrieval date and every transformation. Export a small authorized subset in a documented format.
6. Upload that permitted export into Lab and validate it. Keep it separate from generated examples; do not commit restricted data or credentials.

[Earthkit data](https://earthkit-data.readthedocs.io/en/latest/) is a relevant server-side tool family. Its native/source-specific capabilities are not all available in Pyodide. A CORS failure, unsupported library or rejected permission is a failed request. Move work to a suitable server when needed; do not bypass access controls or expose secrets to fix browser restrictions.

## The teaching export schema

The helper accepts this small **local schema**, not an official service response:

```json
{
  "schema_version": 1,
  "variable": "temperature",
  "units": "K",
  "lat": [40, 50],
  "lon": [-10, 10],
  "values": [[285, 286], [280, 281]],
  "provenance": {
    "source": "original synthetic example",
    "license": "CC BY 4.0",
    "retrieved": "2026-11-15",
    "method": "hand-constructed teaching grid"
  }
}
```

Coordinates must be unique, increasing and finite: longitudes `[-180,180)`, latitudes `[-90,90]`. Values must be a finite latitude-by-longitude array of at most 100,000 cells. Supported variable/unit pairs are `temperature` / `K`, `precipitation` / `mm day-1`, and `wind_speed` / `m s-1`. Temperature is limited to 150–350 K for this teaching contract; precipitation/wind speed must be nonnegative. Missing values require explicit preprocessing. Invalid imports fail without synthetic fallback.

Lesson 04 tests rejection; lesson 25 serializes a synthetic export. Neither establishes permission to export or redistribute real data.

## Linked metadata, not downloaded data

The [Generation 2 Climate DT metadata](https://www.ecmwf.int/en/forecasts/dataset/destination-earth-digital-twin-climate-change-adaptation-gen2), DOI [10.21957/79c6af3105](https://doi.org/10.21957/79c6af3105), is a conceptual reference. No part of that dataset is included. Authentic model runs, restricted redistribution, allocations and live submission remain outside the demonstrations.
