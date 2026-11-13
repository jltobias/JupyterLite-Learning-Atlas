// Real source values stay dense; rows and display samples are created on demand.
const ROOT = new URL('./', import.meta.url);
export const localURL = path => new URL(path, ROOT).href;
const cache = new Map();
export async function read(path, kind = 'json') {
  if (!cache.has(path)) cache.set(path, fetch(localURL(path)).then(r => {
    if (!r.ok) throw new Error(`Could not load ${path} (HTTP ${r.status}).`);
    return kind === 'text' ? r.text() : r.json();
  }).catch(error => { cache.delete(path); throw error; }));
  return cache.get(path);
}
export const CITIES = ['Abidjan', 'Bangkok', 'Ho Chi Minh City', 'Lagos', 'Mombasa'];
export const MODELS = [
  ['GLL-DTM v2 (global coastal lowlands)', 'GLL-DTM v2 · corrected MSL'],
  ['FABDEM v1.0 (five poster-city regions)', 'FABDEM v1.0 · corrected MSL'],
  ['DeltaDTM v1.1 (five poster-city regions)', 'DeltaDTM v1.1 · corrected MSL'],
];
export const PRODUCTS = [
  ['worldpop-2025', 'WorldPop Global2 · 2025'], ['grid3-2025', 'GRID3 · 2025'],
  ['landscan-2020', 'LandScan · 2020'], ['ghspop-2025', 'GHS-POP · 2025'],
];
export const METRICS = [
  ['temperature_c', 'Surface temperature · °C'], ['ndvi', 'NDVI · unitless'],
  ['ndwi', 'NDWI · unitless'], ['POP100', 'Whole-tract population · people'],
];
const course = name => `book/courses/${name}`;
const terrainPath = course('sea-level-rise/data/nature-city-surfaces.json');
const populationPath = course('population-data-comparison/population.json');
const onehealth = course('onehealth/data/');
const posterPath = course('sea-level-rise/data/poster-aggregates.json');
export const gaugePath = 'data/uhslc-observed-candidate.json';
const finite = v => typeof v === 'number' && Number.isFinite(v);
export {finite};

function regular(grid) {
  return {
    count: grid.width * grid.height, grid,
    bounds: [[grid.north - grid.height * grid.dy, grid.west],
             [grid.north, grid.west + grid.width * grid.dx]],
    record(i) {
      const row = Math.floor(i / grid.width), col = i % grid.width;
      const west = grid.west + col * grid.dx, north = grid.north - row * grid.dy;
      return {id: `r${row + 1}c${col + 1}`, row, col,
        lon: west + grid.dx / 2, lat: north - grid.dy / 2,
        value: grid.values[i], bounds: [west, north - grid.dy, west + grid.dx, north]};
    },
    value: i => grid.values[i],
  };
}

function parseCSV(text) {
  // This pinned numeric CSV contains no quoted commas; reject schema drift.
  const rows = text.trim().split(/\r?\n/), headers = rows.shift().split(',');
  return rows.map(line => {
    const fields = line.split(',');
    if (fields.length !== headers.length) throw new Error('Unexpected Landsat CSV schema.');
    return Object.fromEntries(headers.map((h, i) => [h, h === 'id' ? fields[i] : fields[i] === '' ? null : Number(fields[i])]));
  });
}

export async function dataset(state) {
  if (state.family === 'terrain') {
    const [data, sources] = await Promise.all([read(terrainPath), read(course('sea-level-rise/data/nature-sources.json'))]);
    const surface = data.cities.find(c => c.city === state.city && c.model === state.model);
    if (!surface) throw new Error('This city/product combination is unavailable.');
    const dx = surface.longitude[1] - surface.longitude[0], dy = surface.latitude[0] - surface.latitude[1];
    const grid = {width: surface.longitude.length, height: surface.latitude.length,
      west: surface.longitude[0] - dx / 2, north: surface.latitude[0] + dy / 2, dx, dy, values: surface.z_msl.flat()};
    return {...regular(grid), family: 'terrain', title: `${surface.city} · ${MODELS.find(m => m[0] === surface.model)?.[1] || surface.model}`,
      unit: 'm above MSL', epoch: 'HYBRID-CNES-CLS2022 MSL · mean period 1993–2021',
      source: 'Seeger & Minderhoud (2026); WUR corrected products; Vernimmen & Hooijer, Hawker & Neal, Pronk et al.',
      credit: data.attribution, license: data.license, licenseURL: data.license_url,
      sourceURL: surface.source_doi, sourcePath: terrainPath,
      note: `${surface.grid_note} ${data.transformation} NoData and the source ≤ −7 m artefact mask remain null, not ocean. A finite height does not establish dry land or hydraulic connectivity. Height screens are not flooding or 2030 risk. No offset has been reapplied.`,
      sampling: `${grid.width} × ${grid.height} nearest-cell display samples; spacing ${dx.toFixed(3)}°; rounding is storage precision, not accuracy.`,
      metadata: {attribution: data.attribution, license: data.license, license_url: data.license_url,
        transformation: data.transformation, city: surface.city, model: surface.model, source_doi: surface.source_doi,
        grid_note: surface.grid_note, provenance: data.provenance, product_sources: sources,
        datum: 'MSL HYBRID-CNES-CLS2022, 1993–2021; already geoid-aligned and MDT-corrected'},
    };
  }
  if (state.family === 'population') {
    const data = await read(populationPath), layer = data.layers.find(l => l.metadata.id === state.product);
    if (!layer) throw new Error('Population product unavailable.');
    const m = layer.metadata;
    return {...regular(layer.grid), family: 'population', title: `Greater Lagos · ${m.title}`,
      unit: 'people / native cell', epoch: `${m.reference_date} · ${m.population_concept}`,
      source: m.source, credit: `${m.citation} ${m.notices || ''}`, license: m.license, licenseURL: m.license_url,
      sourceURL: m.source_asset, sourcePath: populationPath,
      note: `${m.nodata_semantics} ${m.modification} ${m.resolution}. Estimates with independent concepts, dates, masks and grid offsets. Alternative products are never summed. LandScan uses a pinned mirror with regional validation; full-file producer identity has not been established.`,
      sampling: 'Full native-cell counts and masks; no resampling. Statistical columns are a disclosed deterministic cell sample, not a population total.',
      metadata: m,
    };
  }
  if (state.family === 'onehealth') {
    const manifest = await read(onehealth + 'manifest.json');
    if (state.metric === 'POP100') {
      const geojson = await read(onehealth + 'tracts.geojson');
      const rows = geojson.features.map(f => ({id: f.properties.GEOID, lon: Number(f.properties.CENTLON),
        lat: Number(f.properties.CENTLAT), value: f.properties.POP100, geometry: f.geometry, properties: f.properties}));
      const coords = geojson.features.flatMap(f => f.geometry.type === 'Polygon' ? f.geometry.coordinates.flat() : f.geometry.coordinates.flat(2));
      return {family: 'onehealth', count: rows.length, value: i => rows[i].value, record: i => rows[i], geojson,
        bounds: [[Math.min(...coords.map(c => c[1])), Math.min(...coords.map(c => c[0]))],
                 [Math.max(...coords.map(c => c[1])), Math.max(...coords.map(c => c[0]))]],
        title: 'Fresno · 2020 whole-tract population', unit: 'people / whole tract', epoch: '2020-04-01 Census',
        source: manifest.credits.join('; '), credit: manifest.credits.join('; '), license: 'US public-domain source data',
        licenseURL: manifest.rights.census, sourceURL: manifest.census_query.url, sourcePath: onehealth + 'tracts.geojson',
        note: '166 actual tract geometries. POP100 belongs to each entire tract, including portions outside the Fresno sampling box. The 764,468 total is whole-tract population, not bbox population. Column anchors are Census-provided tract centroids (CENTLON/CENTLAT), not buildings.',
        sampling: 'All 166 whole tracts; no area allocation or aggregation in this view.', metadata: manifest};
    }
    const rows = parseCSV(await read(onehealth + 'pixels.csv', 'text'));
    const metric = state.metric;
    const value = r => (metric === 'temperature_c' ? r.thermal_valid === 1 : r.valid === 1) && finite(r[metric]) ? r[metric] : null;
    return {family: 'onehealth', count: rows.length, value: i => value(rows[i]),
      record: i => {const r = rows[i]; return {id: r.id, lon: r.lon, lat: r.lat, value: value(r),
        bounds: [r.west, r.south, r.east, r.north], valid: r.valid, thermal_valid: r.thermal_valid,
        source_row: r.source_row, source_col: r.source_col};},
      bounds: [[manifest.bbox[1], manifest.bbox[0]], [manifest.bbox[3], manifest.bbox[2]]],
      title: `Fresno · ${METRICS.find(m => m[0] === metric)[1]}`, unit: manifest.units[metric],
      epoch: 'Landsat 9 · 2024-08-30 · 18:33 UTC', source: manifest.credits.join('; '), credit: manifest.credits.join('; '),
      license: 'US public-domain source data', licenseURL: manifest.rights.landsat,
      sourceURL: 'https://doi.org/10.5066/P9OGBGM6', sourcePath: onehealth + 'pixels.csv',
      note: `${manifest.sampling} ${manifest.qa} Surface temperature is not air temperature or personal exposure. Optical metrics use valid; temperature uses thermal_valid. Zero remains valid.`,
      sampling: `${manifest.sample_count.toLocaleString()} systematic native-pixel samples at ~${manifest.sample_spacing_m} m spacing; not a full-resolution area mean. Rectangles retain the provided sample bounds.`, metadata: {...manifest, selected_metric: metric}};
  }
  const [all, provenance] = await Promise.all([read(posterPath), read(course('sea-level-rise/data/provenance.json'))]);
  const chosen = all.filter(r => r.scenario === state.scenario && r.year === Number(state.year));
  const rows = chosen.filter(r => r.scope === state.scope);
  return {family: 'poster', count: rows.length, record: i => ({id: rows[i].city, lon: rows[i].longitude,
    lat: rows[i].latitude, value: rows[i].potentially_flooded, ...rows[i]}), value: i => rows[i].potentially_flooded,
    bounds: [[-7, -8], [23, 109]], title: `${state.scenario} · ${state.year} · ${state.scope} reporting scope`,
    unit: 'potentially flooded facilities / reporting row', epoch: `Published AIDS2024 poster · ${state.year} ${state.scenario} · denominator supported in 2023`,
    source: 'James L. Tobias et al., AIDS2024 poster THPEF698, Tables 1–3',
    credit: 'Published aggregate transcription from AIDS2024 poster THPEF698; source counts preserved; percentages recalculated. Reuse authorized by the owner; original source terms retained.',
    license: 'Owner-authorized published aggregate transcription', licenseURL: 'https://plus.iasociety.org/sites/default/files/2024-09/e-poster_755.pdf',
    sourceURL: 'https://plus.iasociety.org/sites/default/files/2024-09/e-poster_755.pdf', sourcePath: posterPath,
    portfolio: chosen.find(r => r.scope !== 'city' && r.scope !== 'district'),
    note: 'Symbols use approximate public city anchors, never facility positions or district centroids. City and district scopes overlap and must not be summed or subtracted. The five examples do not reproduce the portfolio. Historical Climate Central/Kopp/Muis workflow; these are not new Nature-model predictions.',
    sampling: 'Five published reporting rows at contextual city anchors. Zero-count symbols remain visible. Portfolio shown separately; scopes never summed.',
    metadata: {scenario: state.scenario, year: Number(state.year), scope: state.scope, source: 'AIDS2024 poster THPEF698, Tables 1–3',
      transformations: 'Exact published counts, recalculated percent; public approximate city anchors. No facility coordinates.', provenance},
  };
}

export function statistics(d, threshold = 0) {
  let valid = 0, missing = 0, zero = 0, min = Infinity, max = -Infinity, sum = 0, below = 0;
  for (let i = 0; i < d.count; i++) {
    const value = d.value(i);
    if (!finite(value)) {missing++; continue;}
    valid++; if (value === 0) zero++; if (value <= threshold) below++;
    min = Math.min(min, value); max = Math.max(max, value); sum += value;
  }
  return {valid, missing, zero, min: valid ? min : null, max: valid ? max : null,
    sum, mean: valid ? sum / valid : null, below, count: d.count};
}

export function sampleIndices(d, cap = 1600) {
  const result = [];
  if (d.grid) {
    let stride = 1;
    while (Math.ceil(d.grid.width / stride) * Math.ceil(d.grid.height / stride) > cap) stride++;
    for (let row = 0; row < d.grid.height; row += stride)
      for (let col = 0; col < d.grid.width; col += stride) result.push(row * d.grid.width + col);
    return {indices: result, description: `Source rows/columns from index 0 at stride ${stride}; original cell values, no averaging.`, stride};
  }
  const stride = Math.ceil(d.count / cap);
  for (let i = 0; i < d.count; i += stride) result.push(i);
  return {indices: result, description: `Source record order from index 0 at stride ${stride}; original values, no averaging.`, stride};
}

export function exportSelection(d, state) {
  const sample = sampleIndices(d);
  return {type: 'FeatureCollection', title: d.title,
    atlas_metadata: {selection: {...state}, units: d.unit, epoch: d.epoch,
      source: d.source, attribution: d.credit, license: d.license, license_url: d.licenseURL,
      source_url: d.sourceURL, source_file: d.sourcePath,
      sampling: sample.description, sample_count: sample.indices.length, full_record_count: d.count,
      sample_scope: 'Bounded source sample (cap 1,600). Full 2D maps and terrain scenes render all prepared source values with missing holes; statistical columns use this capped source selection. The export is not a complete copy of the 2D/terrain rendering.',
      source_sampling: d.sampling, bounds_south_west_north_east: d.bounds,
      scientific_limits: d.note, statistics: statistics(d, Number(state.threshold)), source_metadata: d.metadata,
      export_note: 'Coordinates are WGS84 longitude/latitude only. Statistical values are properties, never geographic altitude. Null is missing; zero is valid. Display camera/exaggeration does not modify values.'},
    features: sample.indices.map(i => {const r = d.record(i); return {type: 'Feature',
      geometry: r.geometry || {type: 'Point', coordinates: [r.lon, r.lat]},
      properties: {...r, geometry: undefined, source_index: i, unit: d.unit}};}),
  };
}
