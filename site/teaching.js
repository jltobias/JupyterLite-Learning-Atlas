import {CITIES, MODELS, PRODUCTS, METRICS, dataset, statistics, sampleIndices, exportSelection, read, finite, localURL, gaugePath} from './map-data.js';
import {renderMap, ensureMapRenderer, render3D, clear3D, resetMap, setStreetTiles, showGaugeMarkers} from './map-renderers.js';

const $ = id => document.getElementById(id);
const number = (n, digits = 2) => finite(n) ? n.toLocaleString(undefined, {maximumFractionDigits: digits}) : 'unknown';
const controls = ['family', 'city', 'model', 'product', 'metric', 'scenario', 'year', 'scope', 'threshold', 'rotation', 'tilt', 'exaggeration'];
const defaults = {view: '2d', family: 'terrain', city: 'Lagos', model: MODELS[1][0], product: PRODUCTS[0][0],
  metric: 'temperature_c', scenario: 'RCP 2.6', year: '2030', scope: 'city', threshold: '0', rotation: '35', tilt: '35', exaggeration: '100'};
function options(id, items) {$(id).replaceChildren(...items.map(([value, label]) => new Option(label, value)));}
options('city', CITIES.map(c => [c, c])); options('model', MODELS); options('product', PRODUCTS); options('metric', METRICS);
options('year', Array.from({length: 8}, (_, i) => [String(2030 + 10 * i), String(2030 + 10 * i)]));
let state, selectedData = null, selectedKey = '', requestID = 0, tablePage = 0, renderQueue = Promise.resolve(), timer, gauges, gallery, galleryPage = 0;
function readQuery() {
  const params = new URLSearchParams(location.search), next = {...defaults};
  for (const [key, defaultValue] of Object.entries(defaults)) {
    const el = $(key === 'view' ? 'mode' : key), value = params.get(key);
    if (value !== null && el.tagName === 'SELECT' && [...el.options].some(o => o.value === value)) next[key] = value;
    else if (value !== null && el.type === 'range' && Number.isFinite(Number(value))) {
      el.value = value; next[key] = el.value; // Browser range sanitization applies bounds AND step alignment.
    }
    else next[key] = defaultValue;
  }
  if (next.view === '3d-scene') next.family = 'terrain';
  return next;
}
function syncControls() {
  $('mode').value = state.view;
  for (const key of controls) $(key).value = state[key];
  for (const el of document.querySelectorAll('[data-for]')) el.hidden = el.dataset.for !== state.family;
  for (const id of ['rotation', 'tilt']) $(id).disabled = state.view === '2d';
  $('exaggeration-control').hidden = state.view !== '3d-scene';
  $('threshold-value').textContent = `${state.threshold} m MSL`;
  $('rotation-value').textContent = `${state.rotation}°`; $('tilt-value').textContent = `${state.tilt}°`;
  $('exaggeration-value').textContent = `${state.exaggeration}×`;
  $('view-badge').textContent = state.view === '2d' ? '2D MAP' : state.view === '3d-map' ? '3D COLUMNS' : '3D TERRAIN';
  const url = new URL(location.href); for (const [key, value] of Object.entries(state)) url.searchParams.set(key, value);
  history.replaceState(null, '', url);
}
function dataKey() {return JSON.stringify([state.family, state.city, state.model, state.product, state.metric, state.scenario, state.year, state.scope]);}
function status(message, failure = false) {
  $('view-status').textContent = message; $('view-status').dataset.state = failure ? 'error' : 'ready';
  $('recovery-actions').hidden = !failure;
}
function table() {
  if (!selectedData) return;
  const d = selectedData, start = tablePage * 50, end = Math.min(d.count, start + 50), rows = [];
  for (let i = start; i < end; i++) {
    const r = d.record(i), tr = document.createElement('tr');
    let quality = !finite(r.value) ? 'Missing / unknown' : r.value === 0 ? 'Valid zero' : 'Valid source value';
    if (d.family === 'terrain' && finite(r.value)) quality += ` · ${r.value <= Number(state.threshold) ? 'at/below' : 'above'} ${state.threshold} m screen`;
    if (r.facilities_2023 !== undefined) quality += ` · ${r.value} / ${r.facilities_2023} supported (2023); ${r.scope}; city anchor`;
    if (r.valid !== undefined) quality += ` · optical QA ${r.valid}; thermal QA ${r.thermal_valid}`;
    if (r.geometry) quality += ' · entire Census tract';
    [r.id, number(r.lon, 6), number(r.lat, 6), finite(r.value) ? number(r.value, 6) : 'Missing', quality].forEach((text, col) => {
      const td = document.createElement(col ? 'td' : 'th'); if (!col) td.scope = 'row'; td.textContent = text; tr.append(td);
    }); rows.push(tr);
  }
  $('teaching-table').replaceChildren(...rows);
  $('table-caption').textContent = `${d.title} · ${d.unit} · rows ${number(start + 1, 0)}–${number(end, 0)} of ${number(d.count, 0)} (full source order, including missing)`;
  $('value-heading').textContent = d.unit;
  $('page-label').textContent = `Page ${tablePage + 1} of ${Math.ceil(d.count / 50)}`;
  $('previous-page').disabled = tablePage === 0; $('next-page').disabled = end === d.count;
}
function describe(d, s) {
  const sample = sampleIndices(d), rendered = sample.indices.filter(i => finite(d.value(i))).length;
  $('view-title').textContent = d.title; $('view-epoch').textContent = `${d.epoch} · WGS84 / EPSG:4326`;
  $('evidence-type').textContent = d.family === 'terrain' ? 'CORRECTED TERRAIN ESTIMATE' : d.family === 'population' ? 'POPULATION ESTIMATE · ALTERNATIVE PRODUCTS' : d.family === 'poster' ? 'PUBLISHED REPORTING COUNTS' : 'SATELLITE MEASUREMENTS / CENSUS COUNTS';
  let summary = `${number(s.valid, 0)} valid of ${number(s.count, 0)} source ${d.grid ? 'cells' : 'records'}; ${number(s.missing, 0)} missing; ${number(s.zero, 0)} valid zero. Range ${number(s.min)} to ${number(s.max)} ${d.unit}.`;
  if (d.family === 'terrain') summary += ` Mean ${number(s.mean)} m MSL. ${number(s.below, 0)} sampled heights at/below ${state.threshold} m MSL. This is sample screening, not flooded area, people, facilities or a forecast.`;
  else if (d.family === 'population') summary += ` Full prepared-grid sum: ${number(s.sum)} estimated people for this product only. Column-sample sums are not population totals.`;
  else if (state.metric === 'POP100' && d.family === 'onehealth') summary += ` ${number(s.sum, 0)} people in whole tracts; not bbox population.`;
  else if (d.family === 'onehealth') summary += ` Sample mean ${number(s.mean)} ${d.unit}; not an area mean.`;
  $('view-summary').textContent = summary;
  $('legend-min').textContent = `${number(s.min)} ${d.unit}`; $('legend-max').textContent = number(s.max);
  $('source-credit').textContent = `${d.credit} ${d.license}.`;
  $('source-link').href = d.sourceURL; $('source-link').textContent = 'Producer source ↗'; $('license-link').href = d.licenseURL; $('license-link').textContent = d.license;
  $('full-source').href = localURL(d.sourcePath);
  $('sampling-note').textContent = `${d.sampling} Full 2D maps and terrain scenes render all ${s.valid.toLocaleString()} finite prepared source values, preserving missing holes. Statistical columns and source-sample export use ${rendered.toLocaleString()} finite values of ${sample.indices.length.toLocaleString()} selected source records (cap 1,600). ${sample.description}`;
  $('data-limits').textContent = d.note;
  $('portfolio-summary').hidden = !d.portfolio;
  if (d.portfolio) $('portfolio-summary').textContent = `Separate whole supported portfolio · ${state.scenario}, ${state.year}: ${d.portfolio.potentially_flooded} / ${number(d.portfolio.facilities_2023, 0)} potentially flooded (${(100 * d.portfolio.potentially_flooded / d.portfolio.facilities_2023).toFixed(2)}%). Never sum this with city or district examples.`;
  showExplanation(d, sample, state.view);
  $('download').disabled = false; table();
}
function showExplanation(d, sample, view) {
  $('view-explanation').textContent = view === '3d-scene'
    ? `Actual corrected terrain; east/north axes are metres about ${((d.bounds[0][1] + d.bounds[1][1]) / 2).toFixed(4)}°, ${((d.bounds[0][0] + d.bounds[1][0]) / 2).toFixed(4)}°. Vertical exaggeration ${state.exaggeration}× changes aspect only. Hover heights remain metres MSL. Nulls remain holes. The ${state.threshold} m plane is an elevation reference, not a water/flood prediction.`
    : view === '3d-map'
      ? `Column heights encode ${d.unit}; they are statistical values, not buildings or physical terrain. Longitude/latitude axes are degrees; vertical axis uses independent measure units and normalized display aspect. ${sample.description} Zero values also have visible point marks.`
      : `North-up geographic map. Color represents ${d.unit}; transparent holes are missing, never assumed ocean or zero. Pan/zoom with controls or keyboard; click data to inspect a value. ${d.family === 'poster' ? 'Visible circles include zero counts and mark approximate public city anchors only.' : 'The table and attributed download expose original coordinates and values.'} ${d.family === 'terrain' && ['Lagos', 'Mombasa'].includes(state.city) ? 'Brown marker: actual UHSLC gauge; its independent historical window is charted below.' : ''}`;
}
async function draw() {
  const id = ++requestID, key = dataKey(), changed = key !== selectedKey;
  syncControls();
  if (changed) {
    selectedData = null; selectedKey = ''; tablePage = 0; $('download').disabled = true;
    $('teaching-table').replaceChildren(); $('view-summary').textContent = '';
    for (const id of ['view-explanation','legend-min','legend-max','sampling-note','data-limits','table-caption','page-label']) $(id).textContent = '';
    $('previous-page').disabled = true; $('next-page').disabled = true;
    $('source-credit').textContent = ''; $('portfolio-summary').hidden = true;
    $('view-title').textContent = 'Loading selected source…'; $('view-epoch').textContent = '';
    $('source-link').href = localURL('data/map-data.json'); $('source-link').textContent = 'Source ledger';
    $('license-link').href = localURL('THIRD_PARTY_NOTICES.md'); $('license-link').textContent = 'Source-specific terms';
    $('full-source').href = localURL('data/map-data.json');
    $('map-view').hidden = true; $('plot-view').hidden = true;
    status('Loading selected local source data…'); $('view-status').dataset.state = 'loading';
  }
  try {
    const d = changed ? await dataset({...state}) : selectedData;
    if (id !== requestID) return;
    selectedData = d; selectedKey = key;
    const s = statistics(d, Number(state.threshold)); describe(d, s);
    const selectedState = {...state};
    renderQueue = renderQueue.catch(() => {}).then(async () => {
      if (id !== requestID) return;
      if (selectedState.view === '2d') {
        clear3D(); $('plot-view').hidden = true; $('map-view').hidden = false;
        try {
          await ensureMapRenderer(); if (id !== requestID) return;
          renderMap(d, s, changed); setStreetTiles($('street-tiles').checked);
          if (gauges && d.family === 'terrain') showGaugeMarkers(gauges, selectedState.city);
          status('Ready · local geographic data. Street tiles are optional.');
        } catch (error) {
          if (id !== requestID) return;
          $('map-view').hidden = true;
          status(`${error.message} The selected real data are available in the table, full source and attributed download. Retry the renderer.`, true);
        }
      } else {
        if (changed) clear3D();
        $('map-view').hidden = true; $('plot-view').hidden = false;
        status('Loading local 3D renderer…'); $('view-status').dataset.state = 'loading';
        try {
          await render3D(d, s, selectedState, () => id === requestID);
          if (id === requestID) status(`Ready · ${selectedState.view === '3d-scene' ? 'real corrected terrain surface' : 'statistical columns'} · values and attribution below.`);
        } catch (error) {
          if (id !== requestID) return;
          clear3D(); $('plot-view').hidden = true; $('map-view').hidden = false;
          try {await ensureMapRenderer(); if (id !== requestID) return;
            renderMap(d, s, true); setStreetTiles($('street-tiles').checked);
            if (gauges && d.family === 'terrain') showGaugeMarkers(gauges, selectedState.city);
          } catch { $('map-view').hidden = true; }
          status(`${error.message} 2D/table/source alternatives use the same real selection. Retry or choose 2D.`, true);
          $('view-badge').textContent = '2D FALLBACK';
          showExplanation(d, sampleIndices(d), '2d');
        }
      }
    });
    await renderQueue;
  } catch (error) {
    if (id !== requestID) return;
    selectedData = null; selectedKey = ''; $('download').disabled = true;
    $('map-view').hidden = true; $('plot-view').hidden = true; clear3D();
    $('view-title').textContent = 'Selected data unavailable';
    $('view-summary').textContent = 'No synthetic replacement or previous dataset is being shown. Retry this selection or choose another source family.';
    status(error.message, true);
  }
}
function change(id) {
  state[id === 'mode' ? 'view' : id] = $(id).value;
  if (id === 'mode' && state.view === '3d-scene') state.family = 'terrain';
  if (id === 'family' && state.view === '3d-scene' && state.family !== 'terrain') state.view = '3d-map';
  if (id === 'city') syncGaugeCity();
  clearTimeout(timer);
  if (['rotation', 'tilt', 'exaggeration', 'threshold'].includes(id)) {syncControls(); timer = setTimeout(draw, 120);}
  else draw();
}
for (const id of ['mode', ...controls]) $(id).addEventListener('input', () => change(id));
$('previous-page').onclick = () => {tablePage--; table();}; $('next-page').onclick = () => {tablePage++; table();};
$('reset-view').onclick = () => {state.rotation = defaults.rotation; state.tilt = defaults.tilt; state.exaggeration = defaults.exaggeration;
  if (selectedData && state.view === '2d') {resetMap(selectedData); syncControls();} else draw();};
$('retry').onclick = () => {draw(); if (!gauges) loadGauges(); if (!gallery) loadGallery();};
$('use-2d').onclick = () => {state.view = '2d'; draw();};
$('street-tiles').onchange = () => setStreetTiles($('street-tiles').checked);
$('download').onclick = () => {
  if (!selectedData) return;
  const data = exportSelection(selectedData, state), blob = new Blob([JSON.stringify(data, null, 2) + '\n'], {type: 'application/geo+json'});
  const url = URL.createObjectURL(blob), link = document.createElement('a'); link.href = url;
  const selectionName = selectedData.title.normalize('NFKD').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  link.download = `atlas-${selectedData.family}-${selectionName}-source-sample.geojson`; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
};
function syncGaugeCity() {
  if (['Lagos', 'Mombasa'].includes(state.city)) {$('gauge-station').value = state.city; drawGauge();}
}
window.addEventListener('popstate', () => {state = readQuery(); syncGaugeCity(); draw();});
$('plot-view').addEventListener('atlas-render-lost', async () => {
  if (!selectedData || $('plot-view').hidden) return;
  const d = selectedData, id = requestID;
  clear3D(); $('plot-view').hidden = true; $('map-view').hidden = false;
  try {await ensureMapRenderer(); if (id !== requestID) return;
    renderMap(d, statistics(d, Number(state.threshold)), true);
    if (gauges && d.family === 'terrain') showGaugeMarkers(gauges, state.city);
  } catch {if (id === requestID) $('map-view').hidden = true;}
  if (id === requestID) {status('The WebGL context was lost. Showing the local 2D alternative with the same real table, source and download. Retry the selected view to restore 3D.', true); $('view-badge').textContent = '2D FALLBACK'; showExplanation(d, sampleIndices(d), '2d');}
});

function svg(tag, attrs, content) {
  const el = document.createElementNS('http://www.w3.org/2000/svg', tag);
  for (const [key, value] of Object.entries(attrs)) el.setAttribute(key, value);
  if (content !== undefined) el.textContent = content; return el;
}
function drawGauge() {
  if (!gauges) return;
  const station = gauges.stations.find(s => s.city === $('gauge-station').value), index = Number($('gauge-hour').value);
  const values = station.observed_anomaly_m.filter(finite), lo = Math.min(...values), hi = Math.max(...values);
  const x = i => 55 + i / 671 * 605, y = v => 185 - (v - lo) / (hi - lo) * 155;
  const chart = $('gauge-chart');
  for (const el of [...chart.children]) if (!['title', 'desc'].includes(el.tagName)) el.remove();
  chart.append(svg('line', {x1: 55, y1: y(0), x2: 660, y2: y(0), stroke: '#9aaea4', 'stroke-dasharray': '4 4'}));
  // Separate runs prevent ever joining across a missing source observation.
  let run = [];
  const flush = () => {if (run.length) chart.append(svg('polyline', {points: run.join(' '), fill: 'none', stroke: '#145f66', 'stroke-width': 1.6})); run = [];};
  station.observed_anomaly_m.forEach((v, i) => {if (finite(v)) run.push(`${x(i)},${y(v)}`); else flush();}); flush();
  chart.append(svg('text', {x: 10, y: 25, fill: '#153740', 'font-size': 12}, `${hi.toFixed(2)} m`),
    svg('text', {x: 10, y: 190, fill: '#153740', 'font-size': 12}, `${lo.toFixed(2)} m`),
    svg('text', {x: 55, y: 217, fill: '#153740', 'font-size': 12}, '1 July 1994 UTC'),
    svg('text', {x: 660, y: 217, 'text-anchor': 'end', fill: '#153740', 'font-size': 12}, '28 July 1994 UTC'));
  if (finite(station.observed_anomaly_m[index])) chart.append(svg('circle', {cx: x(index), cy: y(station.observed_anomaly_m[index]), r: 4, fill: '#9b421c', stroke: '#fff', 'stroke-width': 1.5}));
  $('gauge-chart-title').textContent = `${station.city}: 672 observed hourly anomalies, 1–28 July 1994`;
  $('gauge-time').textContent = gauges.time_utc[index].replace('T', ' ').replace('Z', ' UTC');
  $('gauge-reading').textContent = `${station.city} · ${station.sea_level_mm[index]} mm above record-specific station zero · ${number(station.observed_anomaly_m[index], 6)} m relative to its 28-day mean.`;
  $('gauge-status').textContent = `UHSLC ${station.uhslc_id} · record ${station.record_id}/${station.version} · ${station.latitude}°, ${station.longitude}° · 672 hours, no missing in this window. Mean ${number(station.window_mean_sea_level_mm, 6)} mm above station zero; not MSL.`;
}
async function loadGauges() {
  $('gauge-retry').hidden = true;
  try {gauges = await read(gaugePath); drawGauge();
    if (selectedData?.family === 'terrain') showGaugeMarkers(gauges, state.city);
  } catch (error) {$('gauge-retry').hidden = false; $('gauge-status').textContent = `Observed records unavailable: ${error.message} Use the linked original metadata/source files or retry these observations.`;}
}
$('gauge-station').oninput = drawGauge; $('gauge-hour').oninput = drawGauge;
$('gauge-retry').onclick = loadGauges;

const external = (text, url) => {const a = document.createElement('a'); a.textContent = text; a.href = url; a.rel = 'noopener'; return a;};
function drawGallery() {
  if (!gallery) return;
  const query = $('map-search').value.toLowerCase().trim(), type = $('map-type').value, dataClass = $('map-class').value;
  const rows = gallery.resources.filter(r => (type === 'all' || r.mode === type) &&
    (dataClass === 'all' || dataClass === 'actual' && ['real-source', 'published-aggregate'].includes(r.data_class) || r.data_class === dataClass) &&
    (!query || [r.title, r.repository, r.description, r.data_class].join(' ').toLowerCase().includes(query)));
  const pages = Math.max(1, Math.ceil(rows.length / 12)); galleryPage = Math.min(galleryPage, pages - 1);
  $('map-resources').replaceChildren(...rows.slice(galleryPage * 12, (galleryPage + 1) * 12).map(r => {
    const card = document.createElement('article'); card.className = 'resource';
    const badge = document.createElement('span'); badge.className = 'pill'; badge.textContent = `${r.mode} · ${r.data_class}`;
    const h = document.createElement('h3'); h.append(external(r.title + ' ↗', r.url));
    const description = document.createElement('p'); description.textContent = r.description;
    const repo = document.createElement('p'); repo.className = 'repo-name'; repo.textContent = r.repository;
    const evidence = document.createElement('p'); evidence.append(external('Pinned source evidence', r.evidence_url));
    const detail = document.createElement('small'); detail.textContent = `Revision ${r.source_commit || 'README evidence'} · entry ${r.entry_check?.status || 'unchecked'} on ${gallery.checked_on}; runtime not certified.`;
    evidence.append(detail); card.append(badge, h, repo, description, evidence); return card;
  }));
  if (!rows.length) {const p = document.createElement('p'); p.className = 'notice'; p.textContent = 'No matching entries. Change the evidence status, experience type or search.'; $('map-resources').append(p);}
  $('gallery-status').textContent = `${rows.length} matching experiences of ${gallery.resources.length} exact links · ${gallery.repository_coverage.length} public repositories reviewed. No remote previews loaded.`;
  $('gallery-page').textContent = `Page ${galleryPage + 1} of ${pages}`;
  $('gallery-previous').disabled = galleryPage === 0; $('gallery-next').disabled = galleryPage >= pages - 1;
}
async function loadGallery() {
  $('gallery-retry').hidden = true;
  try {
    gallery = await read('data/map-resources.json');
    options('map-type', [['all', 'All types'], ...[...new Set(gallery.resources.map(r => r.mode))].sort().map(mode => [mode, mode])]);
    $('repository-coverage').replaceChildren(...gallery.repository_coverage.map(r => {
      const li = document.createElement('li'); li.append(external(r.repository, r.url), document.createTextNode(' · ' + r.map_status)); return li;
    })); drawGallery();
  } catch (error) {$('gallery-retry').hidden = false; $('gallery-status').textContent = `Library unavailable: ${error.message} The local map and source lessons remain available. Retry the library.`;}
}
$('gallery-retry').onclick = loadGallery;
for (const id of ['map-search', 'map-type', 'map-class']) $(id).oninput = () => {galleryPage = 0; drawGallery();};
$('gallery-previous').onclick = () => {galleryPage--; drawGallery();}; $('gallery-next').onclick = () => {galleryPage++; drawGallery();};
$('coastal-lesson').href = localURL('book/courses/sea-level-rise/notebooks/14_vertical_datums.html');
$('population-lesson').href = localURL('book/courses/population-data-comparison/01_real_population.html');
$('onehealth-lesson').href = localURL('book/courses/onehealth/00_provenance_profile.html');
state = readQuery(); syncGaugeCity(); draw(); loadGauges(); loadGallery();
