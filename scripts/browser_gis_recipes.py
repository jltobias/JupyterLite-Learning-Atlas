"""Optional, copyable stdlib recipes; neither is executed by the default notebook."""

CSV_RECIPE = '''## Optional: prepare an existing geographic CSV

This optional recipe does not run with Run All. Copy its code into a new cell only for the selected subject, with reviewed source-specific metadata. Keep the Census default unchanged. It uses USGS `longitude/latitude/id`, historical cholera **deaths and pumps separately** `LON/LAT/FID`, and the old edition's teaching grid `lon/lat/cell_id` (never planar `x/y`). Raw CSV columns/values survive alongside explicit prefixed numeric derivatives. No observations, coordinates or crosswalks are invented.

Read the retained [USGS/snapshot notices](https://github.com/jltobias/JupyterLite-Learning-Atlas/blob/main/content/courses/data-visualization/repository_examples/data/NOTICES.md), [historical bundle license](https://github.com/jltobias/JupyterLite-Learning-Atlas/blob/main/content/courses/cholera-1854-basic/notices/LICENSE) and [old-edition teaching description](https://github.com/jltobias/JupyterLite-Learning-Atlas/blob/main/content/courses/geospatial-analyses-and-maps-old/notices/README.md). Author a metadata JSON from those actual notices/provider records: source URL, attribution, applicable license statement/evidence, observation time, limitations and units. Unknown rights stay unknown; Census terms are unsuitable. The recipe retains notice text, source CSV hash, selected IDs and mapping. Conversion does not establish rights, geographic accuracy, disease risk or causation.

```python
import csv
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
from atlas_gis_handoff import point_feature

csv_profiles = {
    'usgs': {'path': 'courses/data-visualization/repository_examples/data/usgs/events.csv',
        'xyid': ('longitude', 'latitude', 'id'), 'numeric': {'depth_km': 'km', 'magnitude': 'reported magnitude; not a linear count'},
        'status': 'published USGS earthquake snapshot',
        'notice': 'courses/data-visualization/repository_examples/data/NOTICES.md'},
    'cholera-deaths': {'path': 'courses/cholera-1854-basic/resources/cholera_deaths.csv',
        'xyid': ('LON', 'LAT', 'FID'), 'numeric': {'DEATHS': 'recorded deaths at location; no at-risk denominator'},
        'status': 'historical 1854 death-location transcription',
        'notice': 'courses/cholera-1854-basic/notices/LICENSE'},
    'cholera-pumps': {'path': 'courses/cholera-1854-basic/resources/pumps.csv',
        'xyid': ('LON', 'LAT', 'FID'), 'numeric': {},
        'status': 'historical pump-location transcription',
        'notice': 'courses/cholera-1854-basic/notices/LICENSE'},
    'landcover': {'path': 'courses/geospatial-analyses-and-maps-old/data/landcover_grid.csv',
        'xyid': ('lon', 'lat', 'cell_id'), 'numeric': {'elevation_m': 'm; teaching value', 'ndvi': 'unitless teaching value'},
        'status': 'synthetic geographic teaching grid',
        'notice': 'courses/geospatial-analyses-and-maps-old/notices/README.md'},
}

def _prepare_csv_points(kind, supplied_metadata, limit=5):
    profile = csv_profiles[kind]
    assert type(limit) is int and 0 <= limit <= 20, 'Choose an explicit small row limit.'
    assert supplied_metadata['dataset_id'] != 'fresno-census-2020-tracts', 'Supply CSV source metadata, not Census terms.'
    assert supplied_metadata['observation_status'] == profile['status'], 'Retain the historical/teaching/observed status.'
    assert any(profile['notice'] in source['license_evidence'] for source in supplied_metadata['sources']), 'Review and cite the retained notice for this CSV.'
    raw = Path(profile['path']).read_bytes()
    rows = list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    x, y, identity = profile['xyid']
    selected = rows[:limit]
    features = []
    for row in selected:
        typed = {'_csv_longitude': float(row[x]), '_csv_latitude': float(row[y])}
        typed.update({'_csv_' + field: float(row[field]) if row[field].strip() else None for field in profile['numeric']})
        assert not set(typed).intersection(row), 'Preserve existing columns; typed field collision.'
        features.append(point_feature(row[identity], typed['_csv_longitude'], typed['_csv_latitude'], {**row, **typed}))
    result_metadata = deepcopy(supplied_metadata)
    result_metadata['field_units'] = {**result_metadata['field_units'], '_csv_longitude': 'degrees longitude',
        '_csv_latitude': 'degrees latitude', **{'_csv_' + field: unit for field, unit in profile['numeric'].items()}}
    result_metadata['csv_preparation'] = {'source_path': profile['path'], 'source_csv_sha256': hashlib.sha256(raw).hexdigest(),
        'input_rows': len(rows), 'selected_ids': [row[identity] for row in selected],
        'selection': 'first explicitly limited source rows, in source order', 'longitude_latitude_id_columns': [x, y, identity],
        'raw_columns_retained': list(rows[0]) if rows else [], 'typed_fields': result_metadata['field_units'],
        'notice_path': profile['notice'], 'retained_notice': Path(profile['notice']).read_text(encoding='utf-8')}
    result_metadata['method'] += ' CSV preparation retained raw strings and explicit typed derivatives; empty numeric strings become null; no reprojection or inference.'
    return {'type': 'FeatureCollection', 'features': features}, result_metadata

# After authoring my-usgs.metadata.json with actual source terms:
# supplied = json.loads(Path('my-usgs.metadata.json').read_text())
# prepared, csv_metadata = _prepare_csv_points('usgs', supplied, limit=5)
# with Path('usgs-prepared.geojson').open('x', encoding='utf-8') as stream:
#     json.dump(prepared, stream, ensure_ascii=False, allow_nan=False)
# metadata = csv_metadata
# input_path = Path('usgs-prepared.geojson')
# collection, input_record = load_input(input_path, metadata)
# Then explicitly choose its typed measurement, threshold, IDs and a new export stem.
```
'''

RETURN_RECIPE = '''## Review an uploaded GIS return separately

An app-returned Atlas export is a **review artifact**, not a fresh input to `load_input`: it already contains protected `_atlas_source_id`/`_atlas_handoff` fields, which the loader intentionally rejects. Keep those fields and the original package. Do not strip provenance, restore app IDs automatically, or rerun the fresh-input path. Upload the returned GeoJSON under a new name and inspect it against original portable IDs/values using this optional cell. It reports differences without merging or re-ingesting anything.

```python
import json
from pathlib import Path

def _inspect_returned(returned, original_package, fields):
    assert returned.get('type') == 'FeatureCollection' and isinstance(returned.get('features'), list)
    original = {f['properties']['_atlas_source_id']: f for f in original_package['collection']['features']}
    seen, comparisons = set(), []
    for feature in returned['features']:
        properties = feature.get('properties', {})
        source_id = properties.get('_atlas_source_id')
        assert isinstance(source_id, str) and source_id and source_id not in seen, 'Missing/duplicate portable source ID: review manually.'
        seen.add(source_id)
        previous = original.get(source_id)
        comparisons.append({'source_id': source_id, 'returned_app_id': feature.get('id'),
            'status': 'matched' if previous else 'unmatched; review manually',
            'original_feature_id': previous['id'] if previous else None,
            'values': {field: {'original_present': field in previous['properties'] if previous else False,
                'original': previous['properties'].get(field) if previous else None,
                'returned_present': field in properties, 'returned': properties.get(field)} for field in fields}})
    return comparisons

# After uploading returned-gis.geojson, inspect against this run's original package:
# returned = json.loads(Path('returned-gis.geojson').read_text(encoding='utf-8'))
# comparisons = _inspect_returned(returned, package, list(metadata['field_units']))
# print(json.dumps(comparisons, indent=2))
```

Compare counts, unmatched IDs, changed/missing values, geometry, units and notices before making a new decision. App internal `FeatureID` may differ from GeoJSON `Feature.id`; neither replaces the portable source field. If that field is lost, stop automated comparison and inspect source evidence. A deliberately prepared new analytical input needs a separately documented source/provenance workflow; this recipe provides no automatic conversion back into the exporter.
'''
