"""Original, network-free GeoJSON handoff and evidence-package helper.

Structural WGS84 validation only: this is not a topology engine, reprojection
library, scientific quality assessment, or proof of the supplied attribution.
"""
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import re


def _json(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def _collection_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
        separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def _require(value, message):
    if not value:
        raise ValueError(message)


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def _position(value):
    _require(isinstance(value, list) and len(value) == 2,
             "Geometry requires exactly 2D [longitude, latitude]; retain any Z in a unit-labelled property first.")
    x, y = value
    _require(_number(x) and _number(y), "Coordinates must be finite numbers, never booleans or strings.")
    _require(-180 <= x <= 180 and -90 <= y <= 90,
             "Longitude/latitude outside WGS84 ranges; verify axis order and CRS. No reprojection is performed.")


def _line(value, ring=False):
    _require(isinstance(value, list) and len(value) >= (4 if ring else 2), "Malformed ring/line: too few positions.")
    for position in value:
        _position(position)
    _require(all(abs(a[0] - b[0]) <= 180 for a, b in zip(value, value[1:])),
             "Antimeridian-crossing geometry needs a reviewed source workflow.")
    if ring:
        _require(value[0] == value[-1], "Polygon rings must be explicitly closed; no silent repair.")
        _require(all(abs(p[1]) < 90 for p in value), "Polar polygon needs a reviewed source workflow.")
        area = sum(a[0]*b[1] - b[0]*a[1] for a, b in zip(value, value[1:]))
        _require(area != 0, "Polygon ring has zero signed area.")


def _geometry(geometry):
    _require(isinstance(geometry, dict), "Missing geometry: retain unmapped records in a separate table.")
    kind, coords = geometry.get("type"), geometry.get("coordinates")
    if kind == "Point":
        _position(coords)
    elif kind == "MultiPoint":
        _require(isinstance(coords, list) and coords, "Empty MultiPoint.")
        for position in coords:
            _position(position)
    elif kind in ("LineString", "MultiLineString"):
        lines = [coords] if kind == "LineString" else coords
        _require(isinstance(lines, list) and lines, "Empty line geometry.")
        for line in lines:
            _line(line)
    elif kind in ("Polygon", "MultiPolygon"):
        polygons = [coords] if kind == "Polygon" else coords
        _require(isinstance(polygons, list) and polygons, "Empty polygon geometry.")
        for polygon in polygons:
            _require(isinstance(polygon, list) and polygon, "Polygon requires an exterior ring.")
            for ring in polygon:
                _line(ring, ring=True)
    else:
        raise ValueError("Unsupported geometry type; use Point/line/polygon source continuation, not silent conversion: " + str(kind))


def point_feature(feature_id, longitude, latitude, properties):
    feature = {"type": "Feature", "id": feature_id,
               "geometry": {"type": "Point", "coordinates": [longitude, latitude]},
               "properties": deepcopy(properties)}
    _geometry(feature["geometry"])
    return feature


def rectangle_feature(feature_id, bounds, properties):
    _require(isinstance(bounds, (list, tuple)) and len(bounds) == 4, "Rectangle needs west/south/east/north.")
    west, south, east, north = bounds
    _position([west, south]); _position([east, north])
    _require(west < east and south < north and east-west <= 180,
             "Rectangle needs west < east, south < north, and no antimeridian crossing.")
    feature = {"type": "Feature", "id": feature_id, "properties": deepcopy(properties),
               "geometry": {"type": "Polygon", "coordinates": [[[west, south], [east, south],
                   [east, north], [west, north], [west, south]]]}}
    _geometry(feature["geometry"])
    return feature


def validate_collection(collection, metadata, id_field=None):
    """Return a copy; preserve all properties/foreign members and explicit IDs.

    An explicit id_field may supply missing GeoJSON IDs, never row order. Numeric
    source IDs remain numeric; string and numeric IDs cannot collide by text.
    """
    _require(isinstance(metadata, dict), "Provide an attributed metadata object.")
    for key in ("dataset_id", "title", "observation_status", "observation_time", "method", "missingness_policy"):
        _require(isinstance(metadata.get(key), str) and metadata[key].strip(), "Required attribution/method metadata: " + key)
    _require(metadata.get("input_crs") in ("OGC:CRS84", "EPSG:4326"),
             "Declare known WGS84 input_crs (OGC:CRS84 or explicitly longitude/latitude EPSG:4326); unknown/projected CRS needs a source workflow.")
    _require(metadata.get("coordinate_order") == ["longitude", "latitude"],
             "Explicit coordinate_order must be longitude, latitude; ranges alone do not prove axis order.")
    if metadata["input_crs"] == "EPSG:4326":
        _require(isinstance(metadata.get("axis_order_evidence"), str) and metadata["axis_order_evidence"].strip(),
                 "EPSG:4326 needs documented axis_order_evidence before longitude/latitude export.")
    _require(isinstance(metadata.get("field_units"), dict) and metadata["field_units"], "Declare selected measurement fields and their units.")
    _require(all(isinstance(k, str) and isinstance(v, str) and v.strip() for k, v in metadata["field_units"].items()), "Each declared measurement needs units (unknown must be explicit).")
    _require(isinstance(metadata.get("limitations"), list) and metadata["limitations"], "Record dataset-specific limitations.")
    sources = metadata.get("sources")
    _require(isinstance(sources, list) and sources, "Required source attribution and license statements are missing.")
    source_ids = []
    for source in sources:
        _require(isinstance(source, dict), "Each source needs its own attribution record.")
        for key in ("source_id", "source_url", "attribution", "license_statement", "license_evidence"):
            _require(isinstance(source.get(key), str) and source[key].strip(), "Required source attribution: " + key)
        source_ids.append(source["source_id"])
    _require(len(source_ids) == len(set(source_ids)), "Duplicate source_id in attribution.")
    _require(isinstance(collection, dict) and collection.get("type") == "FeatureCollection" and isinstance(collection.get("features"), list), "Input must be a GeoJSON FeatureCollection.")
    if "crs" in collection:
        name = collection.get("crs", {}).get("properties", {}).get("name")
        _require(name in ("OGC:CRS84", "urn:ogc:def:crs:OGC:1.3:CRS84", "EPSG:4326", "urn:ogc:def:crs:EPSG::4326"),
                 "Input declares unsupported CRS; do not relabel/reproject it here.")
        _require(("4326" in name) == (metadata["input_crs"] == "EPSG:4326"), "Input CRS and declared metadata disagree.")
    result = deepcopy(collection)
    # GeoJSON output uses RFC 7946 longitude/latitude; provenance remains below.
    result.pop("crs", None)
    ids = set()
    for feature in result["features"]:
        _require(isinstance(feature, dict) and feature.get("type") == "Feature" and isinstance(feature.get("properties"), dict), "Each Feature requires a properties object.")
        if "id" not in feature and id_field:
            feature["id"] = feature["properties"].get(id_field)
        identity = feature.get("id")
        _require((isinstance(identity, str) and bool(identity.strip())) or (type(identity) in (int, float) and math.isfinite(identity)), "Stable feature ID missing; choose an explicit source ID field.")
        _require(str(identity) not in ids, "Duplicate/ambiguous feature ID: " + str(identity))
        ids.add(str(identity))
        _require("_atlas_handoff" not in feature["properties"], "Reserved _atlas_handoff property collision; retain the input and choose another source workflow.")
        _require("_atlas_source_id" not in feature["properties"], "Reserved _atlas_source_id property collision; retain the input and choose another source workflow.")
        _geometry(feature.get("geometry"))
        for field in metadata["field_units"]:
            value = feature["properties"].get(field)
            _require(not isinstance(value, float) or math.isfinite(value), "Non-finite measurement: " + field)
        if "source_ids" in feature["properties"] or len(sources) > 1:
            refs = feature["properties"].get("source_ids")
            _require(isinstance(refs, list) and refs and
                     all(isinstance(ref, str) and ref.strip() for ref in refs),
                     "source_ids must be a nonempty list of declared source-ID strings; mixed-source features require it explicitly.")
            _require(len(refs) == len(set(refs)) and set(refs) <= set(source_ids),
                     "source_ids contains duplicate or unknown source references.")
    _json(result); _json(metadata)  # rejects non-finite nested values too
    return result


def load_input(input_path, metadata, id_field=None, max_input_bytes=20_000_000):
    path = Path(input_path)
    _require(path.is_file(), "Input file not found: " + str(path))
    _require(path.stat().st_size <= max_input_bytes, "Input exceeds the reviewed byte limit; select a bounded source extract first.")
    raw = path.read_bytes()
    collection = json.loads(raw)
    result = validate_collection(collection, metadata, id_field)
    return result, {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(),
                    "normalized_collection_sha256": _collection_digest(result),
                    "binding_scope": "Detects accidental changes to the normalized collection; not a signature or independent source authentication.",
                    "bytes": len(raw), "feature_count": len(result["features"]),
                    "id_field_for_missing_ids": id_field, "original_collection_metadata":
                        {k: v for k, v in collection.items() if k != "features"}}


def summarize(collection, field_units):
    features = collection["features"]
    fields = sorted({key for f in features for key in f["properties"] if key != "_atlas_handoff"})
    missingness = {}
    for field in field_units:
        values = [f["properties"].get(field) for f in features]
        present = [f["properties"][field] for f in features if field in f["properties"]]
        numeric = [v for v in values if _number(v)]
        missingness[field] = {"absent": sum(field not in f["properties"] for f in features),
            "null": sum(field in f["properties"] and f["properties"][field] is None for f in features),
            "empty_string": sum(v == "" for v in values), "zero": sum(type(v) in (int, float) and v == 0 for v in values),
            "false": sum(v is False for v in values), "numeric_count": len(numeric),
            "nonnumeric_count": sum(v is not None and not _number(v) for v in present),
            "numeric_sum": sum(numeric) if numeric else None, "units": field_units[field]}
    return {"feature_count": len(features), "fields": fields, "measurements": missingness,
            "numeric_sum_scope": "Arithmetic diagnostic over numeric values only, not an approved aggregation for rates, temperatures or other nonadditive measurements. Nonnumeric counts cover present non-null values, including empty strings and booleans.",
            "preview": [{"id": f["id"], "properties": f["properties"]} for f in features[:3]]}


def write_handoff(collection, metadata, input_record, export_dir, stem, selected_ids=None,
                  max_features=100, max_bytes=5_000_000):
    """Write a deterministic, bounded package; never replace differing files.

    Selection is explicit, by source ID, and output retains source order. Any
    changed run needs a new stem (or a new directory chosen by the learner).
    max_bytes bounds the combined UTF-8 GeoJSON, method and review files.
    """
    _require(isinstance(stem, str) and re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", stem), "Use a safe lowercase filename stem, with no path components.")
    _require(type(max_features) is int and max_features > 0 and type(max_bytes) is int and max_bytes > 0, "Feature/byte limits must be positive integers.")
    validated = validate_collection(collection, metadata)
    _require(isinstance(input_record, dict) and re.fullmatch(r"[0-9a-f]{64}", input_record.get("sha256", "")), "Record the actual input byte SHA-256 through load_input.")
    _require(input_record.get("normalized_collection_sha256") == _collection_digest(validated),
             "Collection changed after load_input; preserve the original receipt and prepare/load a separately named input for intentional changes.")
    _require(selected_ids is None or isinstance(selected_ids, (list, tuple)),
             "selected_ids must be an explicit list or tuple of feature IDs, not a string or other iterable.")
    all_ids = [str(f["id"]) for f in validated["features"]]
    chosen = all_ids if selected_ids is None else [str(i) for i in selected_ids]
    _require(len(chosen) == len(set(chosen)) and set(chosen) <= set(all_ids), "Selection contains duplicate or unknown feature IDs.")
    selected = set(chosen)
    output = deepcopy(validated)
    output["features"] = [f for f in output["features"] if str(f["id"]) in selected]
    # A source-wide bbox would be misleading after subsetting; preserve it in
    # original metadata and explicitly record its removal, never clip geometry.
    output.pop("bbox", None)
    _require(len(output["features"]) <= max_features, "Export exceeds max_features; choose an explicit subset or reviewed limit.")
    _require("atlas_handoff" not in output, "Reserved atlas_handoff collection metadata collision.")
    for feature in output["features"]:
        feature["properties"]["_atlas_source_id"] = str(feature["id"])
        feature["properties"]["_atlas_handoff"] = {"dataset_id": metadata["dataset_id"],
            "source_ids": feature["properties"].get("source_ids", [s["source_id"] for s in metadata["sources"]]),
            "observation_status": metadata["observation_status"], "field_units": metadata["field_units"]}
    output["atlas_handoff"] = {"dataset_id": metadata["dataset_id"], "sources": metadata["sources"],
        "output_crs": "OGC:CRS84", "observation_time": metadata["observation_time"]}
    output_text = _json(output)
    _require(len(output_text.encode("utf-8")) <= max_bytes, "GeoJSON exceeds max_bytes; choose a smaller explicit subset.")
    report = deepcopy(metadata)
    report.update({"schema_version": 1, "input": deepcopy(input_record), "output_crs": "OGC:CRS84",
        "supplied_metadata": deepcopy(metadata),
        "coordinate_units": "degrees", "dimensions": 2,
        "byte_limit": {"max_bytes": max_bytes, "scope": "Complete combined UTF-8 GeoJSON, method JSON and review Markdown; no provenance truncation."},
        "source_id_property": {"name": "_atlas_source_id", "type": "string",
            "derivation": "String representation of the retained Feature.id; missing input IDs are supplied only by the declared source id_field.",
            "inspection": "Compare this source field (or original GEOID) across apps; app-generated internal IDs may differ."},
        "selection": {"input_count": len(all_ids), "output_count": len(selected),
            "selected_ids": [i for i in all_ids if i in selected], "excluded_ids": [i for i in all_ids if i not in selected],
            "complete_input": len(selected) == len(all_ids), "empty": not selected},
        "modifications": ["Explicit ID selection; source geometry/properties retained; missing IDs supplied only from the declared id_field.",
            "Removed legacy collection CRS/bbox from output; preserved original collection metadata in input record; added reserved _atlas_handoff and primitive string _atlas_source_id properties; original Feature.id retained."],
        "summary": summarize(output, metadata["field_units"]),
        "geojson_sha256": hashlib.sha256(output_text.encode("utf-8")).hexdigest(),
        "validation_scope": "Finite 2D WGS84 coordinates, supported structural geometry, IDs and attribution declarations; no topology, source authenticity or scientific accuracy certification."})
    prompt = ("# Inspect this exact GIS evidence package\n\n"
        "Generated review instructions, not an AI response. No model was called.\n\n"
        + "Dataset: " + metadata["title"] + "\n\n"
        + "Input byte SHA-256: `" + input_record["sha256"] + "`\n\n"
        + "Actual evidence context (data rights remain separate from software, model and basemap rights):\n```json\n"
        + _json({key: metadata[key] for key in ("observation_time", "observation_status", "sources", "method", "field_units", "limitations", "input_crs", "coordinate_order")}) + "```\n\n"
        + "Selection and actual schema/summary:\n```json\n" + _json({"selection": report["selection"], "summary": report["summary"]}) + "```\n\n"
        + "Optional prompt: Using only this package, cite actual feature IDs/fields and audit missing values, units, epoch, selection and source terms. Distinguish absent, null, zero and false. Do not infer causes, health outcomes or unprovided subject observations. Identify one claim this evidence cannot support and one independent check. Return suggested IDs/parameters as reviewable text; never execute generated code or URLs.\n\n"
        + "Deliberately flawed candidate to audit: 'The mapped population proves which residents experienced the highest disease risk today.' Explain the unsupported exposure, outcome, time and denominator claims without using a model.\n\n"
        + "Manual handoff: download the GeoJSON, method JSON and this review file from the notebook exports directory. Open https://web.rustgis.app/ or https://web.geolibre.app/ in a separate tab; use Add Data/file picker. Inspect count, extent, one _atlas_source_id/value/unit/source, nulls and the same legend. Compare the portable _atlas_source_id string (or original GEOID) with the retained GeoJSON Feature.id; app-generated internal IDs may differ. A launch link shares no notebook files or kernel state. Record any lost properties. Save changed GIS results under a new name and explicitly upload them back into Lab if needed.\n\n"
        + "Human review: check tool operations/SQL, source layer, filter, coordinate order and distance units; reproduce one known result without AI. Ask the map's intended reader what decision it supports, then change one legend/annotation and retest interpretation. Mapping/style/threshold rules are not fitted GeoAI. A fitted extension needs a declared target/features, spatial/temporal holdout, uncertainty, leakage controls and falsification evidence.\n")
    target = Path(export_dir)
    _require(target.name == "exports" and not target.is_symlink(), "Choose a notebook-owned directory named exports, not a source directory.")
    paths = {"geojson": target/(stem+".geojson"), "method": target/(stem+".metadata.json"), "review": target/(stem+".review.md")}
    payloads = {"geojson": output_text, "method": _json(report), "review": prompt}
    _require(sum(len(value.encode("utf-8")) for value in payloads.values()) <= max_bytes,
             "Complete UTF-8 evidence package (GeoJSON + method + review) exceeds max_bytes; choose a smaller input/selection or an explicitly reviewed larger limit. Provenance is never truncated.")
    # Preflight every target before creating or writing anything.
    for key, path in paths.items():
        if path.exists() and (path.is_symlink() or not path.is_file() or path.read_bytes() != payloads[key].encode("utf-8")):
            raise FileExistsError("Preserving existing output: " + str(path) + "; choose a new stem.")
    target.mkdir(parents=True, exist_ok=True)
    for key, path in paths.items():
        if not path.exists():
            with path.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(payloads[key])
    written = json.loads(paths["geojson"].read_bytes())
    written_method = json.loads(paths["method"].read_bytes())
    _require(written == output and written_method == report, "Written package does not match the selected input.")
    _require(hashlib.sha256(paths["geojson"].read_bytes()).hexdigest() == report["geojson_sha256"], "Written output hash mismatch.")
    return {"paths": paths, "collection": written, "method": written_method, "review": prompt}


def census_metadata(manifest):
    """Use the existing Census query/rights evidence; no Landsat values inferred."""
    return {"dataset_id": "fresno-census-2020-tracts", "chapter_slug": "onehealth",
        "title": "Fresno 2020 Census whole-tract population practice", "observation_status": "published aggregate Census counts",
        "observation_time": manifest["population_date"], "input_crs": "EPSG:4326",
        "coordinate_order": ["longitude", "latitude"],
        "axis_order_evidence": "Bundled TIGERweb GeoJSON query requests outSR=4326; GeoJSON positions are longitude/latitude. Source query and metadata retained.",
        "field_units": {"POP100": manifest["units"]["POP100"]},
        "sources": [{"source_id": "us-census-2020", "source_url": manifest["census_query"]["resolved_url"],
            "attribution": "U.S. Census Bureau, 2020 Census TIGERweb tracts and POP100",
            "license_statement": "U.S. Census Bureau public data; retain attribution and the linked source-specific rights evidence.",
            "license_evidence": manifest["rights"]["census"], "retrieved_at": manifest["census_query"]["retrieved_at"],
            "source_query": manifest["census_query"]}],
        "method": "Read bundled Fresno tracts unchanged; use GEOID for missing GeoJSON IDs; deterministic explicit ID selection, no clipping, spatial join or resampling.",
        "missingness_policy": "Missing field, null, zero, false and empty string counted separately; no imputation.",
        "limitations": ["166 complete intersecting tracts total 764468 people; neither complete-source nor subset sums are an AOI headcount.",
            "2020 whole-tract population is not 2024 Landsat exposure, current population, disease risk or evidence for other chapter locations."],
        "source_manifest": deepcopy(manifest)}
