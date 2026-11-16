"""Original, deterministic teaching utilities. All generated fields are synthetic.

No function contacts a service or silently substitutes generated data for an export.
Arrays are deliberately small enough for a browser Python kernel.
"""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np

PROVENANCE = "Original synthetic teaching data; not observations or DestinE model output"
EARTH_RADIUS_M = 6_371_000.0


def synthetic_cube(seed=42, days=60, nlat=25, nlon=49):
    """Return a regular global grid, with no duplicated longitude seam."""
    if days < 2 or nlat < 3 or nlon < 4:
        raise ValueError("Use at least 2 days, 3 latitudes and 4 longitudes")
    rng = np.random.default_rng(seed)
    lat = np.linspace(-84, 84, nlat)
    lon = np.linspace(-180, 180, nlon, endpoint=False)
    time = np.arange(days)
    phi = np.deg2rad(lat)[None, :, None]
    lam = np.deg2rad(lon)[None, None, :]
    phase = 2 * np.pi * time[:, None, None] / 30
    temperature = (288 - 35 * np.sin(phi)**2 + 4 * np.cos(lam - phase)
                   + 0.025 * time[:, None, None]
                   + rng.normal(0, .35, (days, nlat, nlon)))
    precipitation = np.maximum(0, 5 * np.cos(phi)**4 * (1 + .6 * np.sin(lam + phase)))
    wind_u = np.broadcast_to(10 * np.cos(2 * phi) + 2 * np.sin(lam + phase), temperature.shape).copy()
    wind_v = np.broadcast_to(3 * np.sin(phi) * np.cos(lam - phase), temperature.shape).copy()
    elevation = np.maximum(0, 1800 * np.cos(phi[0]) * np.sin(2 * lam[0])**4)
    return dict(time=time, lat=lat, lon=lon, temperature=temperature,
                precipitation=precipitation, wind_u=wind_u, wind_v=wind_v,
                elevation=elevation, provenance=PROVENANCE,
                units={"temperature": "K", "precipitation": "mm day-1", "wind_u": "m s-1", "wind_v": "m s-1", "elevation": "m"})


def area_weights(lat):
    lat = np.asarray(lat, dtype=float)
    if lat.ndim != 1 or lat.size == 0 or not np.isfinite(lat).all() or np.any(np.abs(lat) > 90):
        raise ValueError("Latitude must be a finite 1D coordinate within [-90, 90]")
    weights = np.cos(np.deg2rad(lat))
    if weights.sum() <= np.finfo(float).eps * lat.size:
        raise ValueError("Latitude weights have zero area")
    return weights / weights.sum()


def global_mean(field, lat):
    """Cosine-weighted approximation for a regular longitude/latitude grid."""
    weights = area_weights(lat)
    field = np.asarray(field, dtype=float)
    if field.ndim < 2 or min(field.shape[-2:]) == 0 or field.shape[-2] != weights.size or not np.isfinite(field).all():
        raise ValueError("Finite field must end in (latitude, longitude)")
    return np.sum(field.mean(axis=-1) * weights, axis=-1)


def _contains_boolean(value):
    """Inspect before coercion so a mixed [False, 2] array cannot hide its Boolean."""
    if isinstance(value, (bool, np.bool_)):
        return True
    if isinstance(value, np.ndarray):
        return any(_contains_boolean(item) for item in value.flat)
    if isinstance(value, (list, tuple)):
        return any(_contains_boolean(item) for item in value)
    return False


def validate_export(payload):
    """Validate a deliberately narrow interchange schema for a small authorized export.

    Schema: schema_version, variable, units, lat, lon, values (lat x lon), provenance.
    This is a local teaching schema, not a claim about any official service response.
    """
    if not isinstance(payload, dict):
        raise ValueError("Export must be a JSON object")
    required = {"schema_version", "variable", "units", "lat", "lon", "values", "provenance"}
    if not required <= payload.keys():
        raise ValueError("Missing required fields: " + ", ".join(sorted(required - payload.keys())))
    if type(payload["schema_version"]) is not int or payload["schema_version"] != 1:
        raise ValueError("Unsupported schema version")
    allowed = {"temperature": "K", "precipitation": "mm day-1", "wind_speed": "m s-1"}
    if not isinstance(payload["variable"], str) or payload["variable"] not in allowed or payload["units"] != allowed[payload["variable"]]:
        raise ValueError("Unknown variable or incompatible units; convert explicitly first")
    if not isinstance(payload["provenance"], dict):
        raise ValueError("Provenance must be an object")
    for key in ("source", "license", "retrieved", "method"):
        if not isinstance(payload["provenance"].get(key), str) or not payload["provenance"][key].strip():
            raise ValueError("Provenance requires nonempty " + key)
    try:
        if any(_contains_boolean(payload[key]) for key in ("lat", "lon", "values")):
            raise ValueError("Boolean entries are not numerical coordinates or values")
        lat = np.asarray(payload["lat"], dtype=float)
        lon = np.asarray(payload["lon"], dtype=float)
        values = np.asarray(payload["values"], dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("Coordinates and values must be numeric arrays") from exc
    if lat.ndim != 1 or lon.ndim != 1 or min(lat.size, lon.size) < 2:
        raise ValueError("Coordinates must be 1D with at least two values")
    if values.shape != (lat.size, lon.size) or values.size > 100_000:
        raise ValueError("Expected lat x lon values with at most 100000 cells")
    if not all(np.isfinite(a).all() for a in (lat, lon, values)):
        raise ValueError("Missing or nonfinite values require an explicit policy")
    if np.any(np.abs(lat) > 90) or np.any(lon < -180) or np.any(lon >= 180):
        raise ValueError("Coordinates outside latitude/longitude bounds")
    if np.any(np.diff(lat) <= 0) or np.any(np.diff(lon) <= 0):
        raise ValueError("Coordinates must be unique and increasing")
    if payload["variable"] == "temperature" and np.any((values < 150) | (values > 350)):
        raise ValueError("Temperature outside the teaching schema's 150–350 K range")
    if payload["variable"] in {"precipitation", "wind_speed"} and np.any(values < 0):
        raise ValueError("This variable cannot be negative")
    return {**payload, "lat": lat, "lon": lon, "values": values}


def load_export(path):
    """Read user-provided local JSON. Parsing/validation errors propagate unchanged."""
    with Path(path).open(encoding="utf-8") as handle:
        return validate_export(json.load(handle))


def ensemble(seed=7, members=30, days=60):
    if any(isinstance(n, (bool, np.bool_)) or not isinstance(n, (int, np.integer)) or n <= 0 for n in (members, days)):
        raise ValueError("Ensemble members and days must be positive integers")
    rng = np.random.default_rng(seed)
    t = np.arange(days)
    return 14 + .03 * t + rng.normal(0, .7, (members, 1)) + rng.normal(0, .3, (members, days))


def flood_bucket(rain, capacity=12, drainage=.3):
    """Toy storage balance: input = drainage + overflow + storage change."""
    try:
        rain = np.asarray(rain, dtype=float)
        if np.ndim(capacity) != 0 or np.ndim(drainage) != 0:
            raise ValueError("Capacity and drainage must be scalars")
        capacity, drainage = float(capacity), float(drainage)
    except (TypeError, ValueError) as exc:
        raise ValueError("Rain, capacity and drainage must be numeric") from exc
    if rain.ndim != 1 or not np.isfinite(rain).all() or np.any(rain < 0) or not np.isfinite(capacity) or capacity <= 0 or not 0 <= drainage <= 1:
        raise ValueError("Rain must be nonnegative; capacity positive; drainage in [0,1]")
    storage, runoff, loss = np.zeros(len(rain)), np.zeros(len(rain)), np.zeros(len(rain))
    previous = 0.
    for i, amount in enumerate(rain):
        available = previous + amount
        loss[i] = drainage * available
        runoff[i] = max(available - loss[i] - capacity, 0)
        storage[i] = available - loss[i] - runoff[i]
        previous = storage[i]
    return storage, runoff, loss


def bilinear(field, lat, lon, target_lat, target_lon):
    """Bilinear interpolation inside the grid; no extrapolation or seam crossing."""
    try:
        field, lat, lon = (np.asarray(value, dtype=float) for value in (field, lat, lon))
        if np.ndim(target_lat) != 0 or np.ndim(target_lon) != 0:
            raise ValueError("Targets must be scalars")
        target_lat, target_lon = float(target_lat), float(target_lon)
    except (TypeError, ValueError) as exc:
        raise ValueError("Grid and targets must be numeric") from exc
    if lat.ndim != 1 or lon.ndim != 1 or min(lat.size, lon.size) < 2:
        raise ValueError("Each axis must be 1D with at least two coordinates")
    if not all(np.isfinite(value).all() for value in (field, lat, lon)) or not np.isfinite([target_lat, target_lon]).all():
        raise ValueError("Grid and targets must be finite")
    if field.shape != (lat.size, lon.size) or np.any(np.diff(lat) <= 0) or np.any(np.diff(lon) <= 0):
        raise ValueError("Invalid source grid")
    if not lat[0] <= target_lat <= lat[-1] or not lon[0] <= target_lon <= lon[-1]:
        raise ValueError("Target lies outside grid")
    i = min(np.searchsorted(lat, target_lat, side="right") - 1, len(lat) - 2)
    j = min(np.searchsorted(lon, target_lon, side="right") - 1, len(lon) - 2)
    a = (target_lat - lat[i]) / (lat[i+1] - lat[i])
    b = (target_lon - lon[j]) / (lon[j+1] - lon[j])
    return (1-a)*(1-b)*field[i,j] + a*(1-b)*field[i+1,j] + (1-a)*b*field[i,j+1] + a*b*field[i+1,j+1]


def globe_xyz(lat, lon, radius=1):
    phi, lam = np.deg2rad(lat), np.deg2rad(lon)
    return radius*np.cos(phi)*np.cos(lam), radius*np.cos(phi)*np.sin(lam), radius*np.sin(phi)
