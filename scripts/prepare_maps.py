"""Prepare reviewed map evidence offline; normal builds never download sources.

Run --write with the retained public research captures to refresh the gallery and
gauge subset. --check needs only the committed site/content/catalog files.
"""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / '_research/real-maps'
GAUGES = ['uhslc-observed-candidate.json', 'uhslc-hourly-metadata.csv',
          'uhslc-lagos-1994-july-28days.csv', 'uhslc-mombasa-1994-july-28days.csv']
GAUGE_SOURCE_HASHES = {
 'uhslc-hourly-metadata.csv': '600fd81e0fe388aaeb49cb5526ed46d4b8d5326bb0e6a21e0e919bdfdf93dcab',
 'uhslc-lagos-1994-july-28days.csv': 'bdccadf2072d657838529ef2743034640fed598f858a5e00e17c45cdc9a71186',
 'uhslc-mombasa-1994-july-28days.csv': 'e791097129a424d2ae39ce642728f4cea56aa47ca9e3d6cc239b98170102c715',
}
COURSE_INPUTS = {
 'c3s-atlas/data/reference/CMIP6_WarmingLevels.csv': ('model-window-reference', 'Apache-2.0; C3S/EU/CMIP6 credits retained'),
 'c3s-atlas/data/reference/ne_110m_coastline.geojson': ('geographic-context', 'Natural Earth public domain'),
 'c3s-atlas/data/reference/atlas-catalogue.json': ('catalogue-metadata', 'CC-BY-4.0; C3S/ECMWF/EU credit'),
 'terrio/data/countries.geojson': ('geographic-context', 'Natural Earth public domain; generalized boundaries'),
 'terrio/data/sources.json': ('geographic-provenance', 'Source-specific metadata; Natural Earth public-domain geography'),
 'sea-level-rise/data/nature-city-surfaces.json': ('terrain', 'CC-BY-NC-SA-4.0'),
 'sea-level-rise/data/nature-sources.json': ('terrain-metadata', 'source-specific'),
 'sea-level-rise/data/nature-raster-catalog.json': ('terrain-metadata', 'source-specific'),
 'sea-level-rise/data/poster-aggregates.json': ('published-aggregates', 'owner-authorized published transcription; retain source citation'),
 'sea-level-rise/data/provenance.json': ('poster-metadata', 'source-specific'),
 'sea-level-rise/data/natural-earth-land.geojson': ('geographic-context', 'public-domain'),
 'sea-level-rise/assets/plotly.min.js': ('renderer', 'MIT'),
 'sea-level-rise/notices/licenses/plotly-js-MIT.txt': ('renderer-license', 'MIT'),
 'population-data-comparison/population.json': ('population', 'CC-BY-4.0; individual producer notices retained'),
 'onehealth/data/pixels.csv': ('landsat', 'US public-domain; USGS/NASA credit'),
 'onehealth/data/tracts.geojson': ('census', 'US public-domain; Census credit'),
 'onehealth/data/manifest.json': ('onehealth-metadata', 'US public-domain source data; source-specific metadata'),
}


def stamp(path):
    data = path.read_bytes()
    return {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def verify_gauges(folder):
    """Reconcile the complete small derivative against pinned original responses."""
    folder = Path(folder)
    candidate = json.loads((folder / GAUGES[0]).read_text(encoding='utf-8'))
    for name, expected in GAUGE_SOURCE_HASHES.items():
        assert stamp(folder / name)['sha256'] == expected, 'Gauge source response hash: ' + name
    with (folder / 'uhslc-hourly-metadata.csv').open(encoding='utf-8', newline='') as stream:
        attributes = {(r['Variable Name'], r['Attribute Name']): r['Value']
                      for r in csv.DictReader(stream) if r['Row Type'] == 'attribute'}
    assert candidate['source_metadata_file'] == 'uhslc-hourly-metadata.csv', 'Gauge metadata filename'
    assert candidate['source_metadata_sha256'] == GAUGE_SOURCE_HASHES[candidate['source_metadata_file']], 'Gauge embedded metadata hash'
    license_text = ' '.join(attributes['NC_GLOBAL', 'license'].replace('\\n', ' ').split())
    assert candidate['source_license_statement'] in license_text, 'Gauge producer license statement'
    assert candidate['source_info_url'] == attributes['NC_GLOBAL', 'infoUrl'], 'Gauge producer metadata URL'
    assert candidate['source_fill_value'] == int(attributes['sea_level', '_FillValue']), 'Gauge fill metadata'
    assert attributes['sea_level', 'units'] == 'millimeters', 'Gauge raw units metadata'
    start = datetime(1994, 7, 1, tzinfo=timezone.utc)
    axis = [(start + timedelta(hours=i)).strftime('%Y-%m-%dT%H:%M:%SZ') for i in range(672)]
    assert candidate['time_utc'] == axis, 'Gauge hourly timestamps'
    assert candidate['window_start_utc'] == axis[0] and candidate['window_end_exclusive_utc'] == '1994-07-29T00:00:00Z', 'Gauge window bounds'
    assert candidate['sample_interval_seconds'] == 3600, 'Gauge sample interval'
    identities = [('Lagos', 233, 2333, 'C', 6.4233, 3.4117), ('Mombasa', 101, 1011, 'A', -4.06999, 39.65732)]
    assert len(candidate['stations']) == len(identities), 'Gauge station count'
    for station, identity in zip(candidate['stations'], identities):
        city, uhslc_id, record_id, version, latitude, longitude = identity
        assert tuple(station[k] for k in ['city', 'uhslc_id', 'record_id', 'version', 'latitude', 'longitude']) == identity, 'Gauge station identity'
        name = f'uhslc-{city.lower()}-1994-july-28days.csv'
        assert station['source_file'] == name and station['source_sha256'] == GAUGE_SOURCE_HASHES[name], 'Gauge embedded source hash'
        expected_url = ('https://uhslc.soest.hawaii.edu/erddap/tabledap/global_hourly_rqds.csv?'
                        'time,sea_level,quality,latitude,longitude,station_name,record_id,uhslc_id,version,reference_datum'
                        f'&record_id={record_id}&time>=1994-07-01T00:00:00Z&time<1994-07-29T00:00:00Z')
        assert station['source_url'] == expected_url, 'Gauge source query'
        with (folder / name).open(encoding='utf-8', newline='') as stream:
            reader = csv.DictReader(stream)
            units = next(reader)
            rows = list(reader)
        assert units['time'] == 'UTC' and units['sea_level'] == station['source_units'] == attributes['sea_level', 'units'], 'Gauge CSV units'
        assert [r['time'] for r in rows] == axis, 'Gauge response timestamp order/coverage'
        assert len({r['time'] for r in rows}) == len(rows), 'Gauge duplicate timestamps'
        for row in rows:
            assert (row['station_name'], int(row['uhslc_id']), int(row['record_id']), row['version'], float(row['latitude']), float(row['longitude'])) == identity, 'Gauge response station metadata'
            assert row['reference_datum'] == station['reference_datum'] == 'station zero', 'Gauge station datum'
        raw = [float(r['sea_level']) if r['sea_level'] not in ['', 'NaN', '-32767'] else None for r in rows]
        quality = [int(r['quality']) for r in rows]
        assert all(q == 4 for q in quality) and station['source_quality_values'] == sorted(set(quality)), 'Gauge quality array'
        if 'quality' in station: assert station['quality'] == quality, 'Gauge derived quality array'
        assert station['sea_level_mm'] == raw, 'Gauge raw readings'
        valid = [v for v in raw if v is not None]
        assert (station['row_count'], station['valid_count'], station['missing_count'], station['missing_timestamp_count']) == (672, len(valid), 672-len(valid), 0), 'Gauge counts/missingness'
        assert station['source_range_mm'] == [min(valid), max(valid)], 'Gauge raw range'
        mean = math.fsum(valid) / len(valid)
        assert station['window_mean_sea_level_mm'] == mean, 'Gauge window mean'
        anomalies = [round((v-mean)/1000, 6) if v is not None else None for v in raw]
        assert station['observed_anomaly_m'] == anomalies, 'Gauge derived anomalies'
    return candidate


def prepare():
    verify_gauges(RESEARCH)
    data_dir = ROOT / 'site/data'
    data_dir.mkdir(parents=True, exist_ok=True)
    for name in GAUGES:
        shutil.copyfile(RESEARCH / name, data_dir / name)
    candidates = json.loads((RESEARCH / 'repo-map-candidates.json').read_text(encoding='utf-8'))
    entries = []
    seen = set()
    for item in candidates['candidates']:
        if 'JupyterLite-Learning-Atlas' in item['url'] or item['url'] in seen:
            continue
        assert item['url'].startswith('https://') and item['evidence_url'].startswith('https://')
        seen.add(item['url'])
        entries.append(item)
    represented = {e['repository'] for e in entries}
    gallery = {
        'schema_version': 1, 'checked_on': candidates['checked_on'],
        'verification_note': candidates['verification_note'],
        'source_capture_sha256': stamp(RESEARCH / 'repo-map-candidates.json')['sha256'],
        'resources': entries,
        'repository_coverage': [dict(r, map_status=('local Map and Scene Atlas studio: ../teach/' if r['repository'] == 'JupyterLite-Learning-Atlas'
                                                   else 'indexed-experiences' if r['repository'] in represented
                                                   else 'source-only; no reviewed standalone map entry'))
                                for r in candidates['public_repository_scan']],
    }
    write_json(ROOT / 'catalog/map-resources.json', gallery)
    write_json(data_dir / 'map-resources.json', gallery)
    refresh_ledger()


def refresh_ledger():
    records = []
    library = json.loads((ROOT / 'catalog/source-library.json').read_text(encoding='utf-8'))
    support = {entry['local_path']: entry for entry in library['support_files']}
    for relative, (role, license_name) in COURSE_INPUTS.items():
        path = ROOT / 'content/courses' / relative
        source = support['courses/' + relative]
        assert stamp(path)['sha256'] == source['sha256'], 'Pinned course input changed: ' + relative
        records.append(dict(path=path.relative_to(ROOT).as_posix(), site_path='book/courses/' + relative,
                            role=role, license=license_name, source_url=source['source_url'],
                            source_sha256=source['source_sha256'], **stamp(path)))
    for name in GAUGES:
        path = ROOT / 'site/data' / name
        records.append(dict(path=path.relative_to(ROOT).as_posix(), site_path='data/' + name,
                            role='gauge-data' if name.endswith('.json') else 'gauge-source-evidence',
                            license='UHSLC producer free-use/redistribution statement and complete warranty/liability terms in uhslc-hourly-metadata.csv',
                            source_url='https://uhslc.soest.hawaii.edu/erddap/info/global_hourly_rqds/index.html',
                            **stamp(path)))
    for path in sorted((ROOT / 'site/vendor/leaflet').rglob('*')):
        if path.is_file():
            records.append(dict(path=path.relative_to(ROOT).as_posix(), site_path=path.relative_to(ROOT / 'site').as_posix(),
                                role='renderer-license' if path.name == 'LICENSE' else 'renderer',
                                license='BSD-2-Clause', source_url='https://github.com/Leaflet/Leaflet/releases/tag/v1.9.4', **stamp(path)))
    for name in ['teach/index.html', 'teaching.js', 'map-data.js', 'map-renderers.js', 'map-studio.css', 'data/map-resources.json']:
        path = ROOT / 'site' / name
        if path.exists():
            records.append(dict(path=path.relative_to(ROOT).as_posix(), site_path=name,
                                role='atlas-output', license='MIT code; original narrative CC-BY-4.0; data rights remain separate', **stamp(path)))
    ledger = {
      'schema_version': 1, 'prepared_on': '2026-11-13',
      'preparation': 'python scripts/prepare_maps.py --write; offline from reviewed public captures. No normal-build downloads.',
      'scope': 'Map studio inputs, public gauge subset/evidence, renderer distribution and original outputs. Imported source bytes remain unchanged.',
      'source_metadata': {'terrain': 'book/courses/sea-level-rise/data/nature-sources.json',
                          'terrain_rasters': 'book/courses/sea-level-rise/data/nature-raster-catalog.json',
                          'population': 'book/courses/population-data-comparison/population.json',
                          'onehealth': 'book/courses/onehealth/data/manifest.json',
                          'gauges': 'data/uhslc-observed-candidate.json'},
      'scientific_limits': 'Independent families, units, masks and epochs. No facility coordinates; no flood predictions. Gauge station zero/window anomalies are not MSL. Alternative population products are never summed.',
      'assets': records,
    }
    write_json(ROOT / 'catalog/map-data.json', ledger)
    write_json(ROOT / 'site/data/map-data.json', ledger)


def check():
    verify_gauges(ROOT / 'site/data')
    ledger = json.loads((ROOT / 'catalog/map-data.json').read_text(encoding='utf-8'))
    paths = {record['path'] for record in ledger['assets']}
    assert len(paths) == len(ledger['assets']), 'Duplicate ledger paths'
    assert {'content/courses/' + relative for relative in COURSE_INPUTS}.issubset(paths), 'Missing required map inputs'
    for record in ledger['assets']:
        path = (ROOT / record['path']).resolve()
        assert path.is_relative_to(ROOT), record['path']
        assert (ROOT / '_site' / record['site_path']).resolve().is_relative_to(ROOT / '_site'), record['site_path']
        assert stamp(path) == {k: record[k] for k in ['sha256', 'bytes']}, record['path']
    for name in ['map-data.json', 'map-resources.json']:
        assert (ROOT / 'catalog' / name).read_bytes() == (ROOT / 'site/data' / name).read_bytes(), name
    gallery = json.loads((ROOT / 'catalog/map-resources.json').read_text(encoding='utf-8'))
    assert len({r['url'] for r in gallery['resources']}) == len(gallery['resources'])
    assert all(r['url'].startswith('https://') and r['evidence_url'].startswith('https://') for r in gallery['resources'])
    print(f"Map ledger: {len(ledger['assets'])} byte/hash checks; {len(gallery['resources'])} evidence-backed external entries")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--refresh-ledger', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.write: prepare()
    elif args.refresh_ledger: refresh_ledger()
    check()
