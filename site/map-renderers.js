import {read, localURL, finite, sampleIndices} from './map-data.js';
let map, layer, contextLayer, stationLayer, tiles, canvasRenderer, plotPromise, mapPromise, resizeObserver;
const palette = ['#264b74', '#247c83', '#77a971', '#f1d66a'];
export function color(value, stats) {
  if (!finite(value)) return 'transparent';
  const t = stats.max === stats.min ? .5 : Math.max(0, Math.min(1, (value - stats.min) / (stats.max - stats.min)));
  const scaled = t * (palette.length - 1), n = Math.min(palette.length - 2, Math.floor(scaled));
  const a = palette[n].match(/\w\w/g).map(v => parseInt(v, 16)), b = palette[n + 1].match(/\w\w/g).map(v => parseInt(v, 16));
  return `rgb(${a.map((v, i) => Math.round(v + (b[i] - v) * (scaled - n))).join(',')})`;
}
const valueText = (v, unit) => finite(v) ? `${v.toLocaleString(undefined, {maximumFractionDigits: 6})} ${unit}` : 'Missing / unknown';
const SCRIPT_TIMEOUT_MS = 30000;
function loadRenderer(path, globalName, label) {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    const finish = error => {
      clearTimeout(timeout); script.onload = script.onerror = null;
      if (error) {script.remove(); reject(error);} else resolve(window[globalName]);
    };
    const timeout = setTimeout(() => finish(new Error(`${label} loading timed out. Retry or use the local table/source alternative.`)), SCRIPT_TIMEOUT_MS);
    script.src = localURL(path);
    script.onload = () => finish(window[globalName] ? null : new Error(`${label} did not initialize.`));
    script.onerror = () => finish(new Error(`${label} could not load.`));
    document.head.append(script);
  });
}
export async function ensureMapRenderer() {
  if (window.L) return;
  if (!mapPromise) mapPromise = loadRenderer('vendor/leaflet/dist/leaflet.js', 'L', 'The local 2D renderer')
    .catch(error => {mapPromise = null; throw error;});
  return mapPromise;
}
function info(record, d) {
  const node = document.createElement('div');
  node.textContent = `${record.id}: ${valueText(record.value, d.unit)} · ${record.lon.toFixed(6)}°, ${record.lat.toFixed(6)}°`;
  if (record.facilities_2023 !== undefined) node.append(document.createElement('br'),
    document.createTextNode(`${record.value} / ${record.facilities_2023} supported facilities (2023); ${record.scope} scope. Approximate city anchor.`));
  return node;
}

export function renderMap(d, stats, refit = true) {
  if (!window.L) throw new Error('The local 2D renderer could not load. The table, source and download remain available.');
  const L = window.L;
  if (!map) {
    canvasRenderer = L.canvas({padding: .3});
    map = L.map('map-view', {renderer: canvasRenderer, preferCanvas: true, zoomControl: true, zoomSnap: .25, keyboard: true, scrollWheelZoom: false});
    map.createPane('atlas-context').style.zIndex = '200';
    map.attributionControl.setPrefix('<a href="https://leafletjs.com">Leaflet 1.9.4</a>');
    const orientation = L.control({position: 'topright'});
    orientation.onAdd = () => {const el = L.DomUtil.create('div', 'map-orientation'); el.textContent = 'N ↑ · WGS84'; return el;};
    orientation.addTo(map);
    map.on('click', event => {
      if (!map._atlasData) return;
      const active = map._atlasData;
      if (active.grid) {
        const g = active.grid, col = Math.floor((event.latlng.lng - g.west) / g.dx), row = Math.floor((g.north - event.latlng.lat) / g.dy);
        if (row >= 0 && col >= 0 && row < g.height && col < g.width) L.popup().setLatLng(event.latlng).setContent(info(active.record(row * g.width + col), active)).openOn(map);
      } else if (!active.geojson && active.family === 'onehealth') {
        for (let i = 0; i < active.count; i++) {
          const r = active.record(i), [w, s, e, n] = r.bounds;
          if (event.latlng.lng >= w && event.latlng.lng <= e && event.latlng.lat >= s && event.latlng.lat <= n) {
            L.popup().setLatLng(event.latlng).setContent(info(r, active)).openOn(map); break;
          }
        }
      }
    });
    // Geographic context is deliberately coarse and optional to the local data.
    read('book/courses/sea-level-rise/data/natural-earth-land.geojson').then(geo => {
      contextLayer = L.geoJSON(geo, {pane: 'atlas-context', attribution: '<a href="https://www.naturalearthdata.com">Natural Earth</a> · public domain / coarse context', interactive: false, style: {color: '#acbdb1', weight: .8, fillColor: '#e9eee3', fillOpacity: .65}}).addTo(map);
      contextLayer.bringToBack();
    }).catch(() => {});
  }
  if (layer) map.removeLayer(layer);
  if (stationLayer) map.removeLayer(stationLayer);
  map._atlasData = d;
  if (d.geojson) {
    layer = L.geoJSON(d.geojson, {renderer: canvasRenderer,
      style: f => ({color: '#284f52', weight: 1, fillColor: color(f.properties.POP100, stats), fillOpacity: .8}),
      onEachFeature: (f, shape) => shape.bindPopup(info({id: f.properties.GEOID,
        lon: Number(f.properties.CENTLON), lat: Number(f.properties.CENTLAT), value: f.properties.POP100}, d)),
    }).addTo(map);
  } else if (d.family === 'poster') {
    layer = L.featureGroup(Array.from({length: d.count}, (_, i) => {
      const r = d.record(i);
      return L.circleMarker([r.lat, r.lon], {renderer: canvasRenderer, radius: 8 + Math.sqrt(r.value) * 3,
        color: '#153740', weight: 2, fillOpacity: .85, fillColor: color(r.value, stats)}).bindPopup(info(r, d))
        .bindTooltip(`${r.id}: ${r.value} / ${r.facilities_2023}`, {permanent: true, direction: 'top'});
    })).addTo(map);
  } else {
    const Raster = L.Layer.extend({
      onAdd(activeMap) {
        this._map = activeMap; this.canvas = L.DomUtil.create('canvas', 'atlas-data-canvas');
        this.canvas.setAttribute('aria-label', `${d.title}; full values in the table`);
        activeMap.getPanes().overlayPane.append(this.canvas);
        activeMap.on('moveend zoomend resize', this.draw, this); this.draw();
      },
      onRemove(activeMap) {activeMap.off('moveend zoomend resize', this.draw, this); this.canvas.remove();},
      draw() {
        const size = this._map.getSize(), canvas = this.canvas, ratio = Math.min(devicePixelRatio || 1, 2);
        canvas.width = size.x * ratio; canvas.height = size.y * ratio;
        canvas.style.width = size.x + 'px'; canvas.style.height = size.y + 'px';
        L.DomUtil.setPosition(canvas, this._map.containerPointToLayerPoint([0, 0]));
        const ctx = canvas.getContext('2d'); ctx.scale(ratio, ratio);
        if (d.grid) {
          const g = d.grid;
          const x = Array.from({length: g.width + 1}, (_, c) => this._map.latLngToContainerPoint([g.north, g.west + c * g.dx]).x);
          const y = Array.from({length: g.height + 1}, (_, r) => this._map.latLngToContainerPoint([g.north - r * g.dy, g.west]).y);
          for (let r = 0; r < g.height; r++) {
            if (y[r + 1] < 0 || y[r] > size.y) continue;
            for (let c = 0; c < g.width; c++) {
              if (x[c + 1] < 0 || x[c] > size.x) continue;
              const v = g.values[r * g.width + c]; if (!finite(v)) continue;
              ctx.fillStyle = color(v, stats); ctx.fillRect(x[c], y[r], x[c + 1] - x[c] + .3, y[r + 1] - y[r] + .3);
            }
          }
        } else {
          for (let i = 0; i < d.count; i++) {
            const r = d.record(i); if (!finite(r.value)) continue;
            const [west, south, east, north] = r.bounds;
            const a = this._map.latLngToContainerPoint([north, west]), b = this._map.latLngToContainerPoint([south, east]);
            if (b.x < 0 || a.x > size.x || b.y < 0 || a.y > size.y) continue;
            ctx.fillStyle = color(r.value, stats); ctx.fillRect(a.x, a.y, Math.max(.5, b.x - a.x), Math.max(.5, b.y - a.y));
          }
        }
      },
    });
    layer = new Raster().addTo(map);
  }
  map.invalidateSize();
  if (refit) map.fitBounds(d.bounds, {padding: [16, 16], maxZoom: 13, animate: false});
  return map;
}

export function setStreetTiles(enabled) {
  if (!map) return;
  if (enabled && !tiles) tiles = window.L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19, attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
    updateWhenIdle: true, keepBuffer: 1,
  });
  if (enabled && !map.hasLayer(tiles)) tiles.addTo(map).bringToBack();
  else if (!enabled && tiles && map.hasLayer(tiles)) map.removeLayer(tiles);
}

export function showGaugeMarkers(gauges, city) {
  if (!map) return;
  if (stationLayer) map.removeLayer(stationLayer);
  stationLayer = window.L.featureGroup(gauges.stations.filter(s => !city || s.city === city).map(s => {
    const node = document.createElement('div'); node.textContent = `${s.city} gauge · UHSLC ${s.uhslc_id}, record ${s.record_id}/${s.version}. 672 hourly readings, 1–28 July 1994. Station zero is not MSL.`;
    return window.L.circleMarker([s.latitude, s.longitude], {radius: 7, color: '#fff', weight: 2, fillColor: '#943f1a', fillOpacity: 1}).bindPopup(node);
  })).addTo(map);
}

export function resetMap(d) {if (map) map.fitBounds(d.bounds, {padding: [16, 16], maxZoom: 13, animate: false});}

async function plotly() {
  if (window.Plotly) return window.Plotly;
  if (!plotPromise) plotPromise = loadRenderer('book/courses/sea-level-rise/assets/plotly.min.js', 'Plotly', 'The local 3D renderer')
    .catch(error => {plotPromise = null; throw error;});
  return plotPromise;
}
function supportsWebGL() {
  const c = document.createElement('canvas');
  try {const gl = c.getContext('webgl2') || c.getContext('webgl'); if (!gl) return false;
    gl.getExtension('WEBGL_lose_context')?.loseContext(); return true;
  } catch {return false;}
}
function cameraRadius(width) {return width < 450 ? 4.8 : width < 650 ? 2.8 : 1.8;}
function terrainAxisLabels(width) {
  const compact = width < 450;
  return Object.fromEntries([
    ['xaxis', compact ? 'east (m)' : 'east of anchor (m)'],
    ['yaxis', compact ? 'north (m)' : 'north of anchor (m)'],
    ['zaxis', compact ? 'm MSL' : 'height (m MSL)'],
  ].map(([axis, text]) => [axis, {title: {text, font: {size: compact ? 10 : 12}}, tickfont: {size: compact ? 9 : 11}, nticks: 3}]));
}
function camera(state, width) {
  const angle = Number(state.rotation) * Math.PI / 180, tilt = Number(state.tilt) * Math.PI / 180;
  const radius = cameraRadius(width);
  return {eye: {x: radius * Math.cos(angle) * Math.cos(tilt), y: radius * Math.sin(angle) * Math.cos(tilt), z: radius * Math.sin(tilt)}, up: {x: 0, y: 0, z: 1}};
}
export async function render3D(d, stats, state, current) {
  if (!supportsWebGL()) throw new Error('WebGL is unavailable. Showing the local 2D map; table, source and download still describe this selection.');
  const Plotly = await plotly(); if (!current()) return;
  const traces = [], surfaceMode = state.view === '3d-scene';
  const scale = palette.map((c, i) => [i / (palette.length - 1), c]);
  const origin = [(d.bounds[0][1] + d.bounds[1][1]) / 2, (d.bounds[0][0] + d.bounds[1][0]) / 2];
  let scene;
  if (surfaceMode) {
    const g = d.grid, mx = 111320 * Math.cos(origin[1] * Math.PI / 180), my = 111320;
    const x = Array.from({length: g.width}, (_, c) => (g.west + (c + .5) * g.dx - origin[0]) * mx);
    const y = Array.from({length: g.height}, (_, r) => (g.north - (r + .5) * g.dy - origin[1]) * my);
    const z = Array.from({length: g.height}, (_, r) => g.values.slice(r * g.width, (r + 1) * g.width));
    const customdata = z.map((row, r) => row.map((value, c) => [g.west + (c + .5) * g.dx, g.north - (r + .5) * g.dy, value]));
    traces.push({type: 'surface', x, y, z, customdata, connectgaps: false, colorscale: scale, cmin: stats.min, cmax: stats.max,
      colorbar: {title: {text: 'm MSL'}, thickness: 12, len: .65}, name: 'Corrected real terrain',
      hovertemplate: '%{customdata[0]:.6f}° E · %{customdata[1]:.6f}° N<br>%{z:.2f} m above MSL<extra></extra>'});
    const t = Number(state.threshold);
    traces.push({type: 'surface', x: [x[0], x.at(-1)], y: [y[0], y.at(-1)], z: [[t, t], [t, t]],
      opacity: .18, showscale: false, colorscale: [[0, '#285d85'], [1, '#285d85']],
      name: 'Elevation reference only', hovertemplate: `${t} m MSL reference plane<br>No inundation prediction<extra></extra>`});
    const horizontal = Math.max(Math.abs(x.at(-1) - x[0]), Math.abs(y.at(-1) - y[0]));
    const low = Math.min(stats.min, t), high = Math.max(stats.max, t);
    // Ranges and aspect derive from the same unmodified metre values. No hidden
    // visual relief floor: even very flat GLL windows keep the requested factor.
    const zr = low === high ? [low - .5, high + .5] : [low, high];
    scene = {xaxis: {title: {text: 'east of anchor (m)'}, range: [x[0], x.at(-1)]},
      yaxis: {title: {text: 'north of anchor (m)'}, range: [y.at(-1), y[0]]},
      zaxis: {title: {text: 'height (m MSL)'}, range: zr, nticks: 3},
      aspectmode: 'manual', aspectratio: {x: Math.abs(x.at(-1) - x[0]) / horizontal, y: Math.abs(y.at(-1) - y[0]) / horizontal,
        z: (zr[1] - zr[0]) * Number(state.exaggeration) / horizontal}};
  } else {
    const sample = sampleIndices(d), records = sample.indices.map(i => d.record(i)).filter(r => finite(r.value));
    const mesh = {type: 'mesh3d', x: [], y: [], z: [], i: [], j: [], k: [], vertexcolor: [], text: [], flatshading: true,
      hovertemplate: '%{text}<extra></extra>', name: 'Statistical columns', showscale: false};
    const faces = [[0,1,2],[0,2,3],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]];
    for (const r of records) {
      const w = d.grid ? d.grid.dx * .35 : d.family === 'poster' ? .3 : .0009;
      const h = d.grid ? d.grid.dy * .35 : w;
      const base = mesh.x.length, text = info(r, d).textContent;
      const vertices = [[-w,-h,0],[w,-h,0],[w,h,0],[-w,h,0],[-w,-h,r.value],[w,-h,r.value],[w,h,r.value],[-w,h,r.value]];
      for (const [x,y,z] of vertices) {mesh.x.push(r.lon+x); mesh.y.push(r.lat+y); mesh.z.push(z); mesh.vertexcolor.push(color(r.value, stats)); mesh.text.push(text);}
      for (const [i,j,k] of faces) {mesh.i.push(base+i); mesh.j.push(base+j); mesh.k.push(base+k);}
    }
    traces.push(mesh, {type: 'scatter3d', mode: 'markers', x: records.map(r => r.lon), y: records.map(r => r.lat), z: records.map(r => r.value),
      text: records.map(r => info(r, d).textContent), marker: {size: 2.5, color: '#153740'}, hovertemplate: '%{text}<extra></extra>', name: 'Original values (including zero)'});
    scene = {xaxis: {title: {text: 'longitude (°)'}}, yaxis: {title: {text: 'latitude (°)'}}, zaxis: {title: {text: d.unit}},
      aspectmode: 'manual', aspectratio: {x: 1, y: 1, z: .7}};
  }
  const plotElement = document.getElementById('plot-view');
  if (surfaceMode) for (const [axis, labels] of Object.entries(terrainAxisLabels(plotElement.clientWidth))) Object.assign(scene[axis], labels);
  scene.camera = camera(state, plotElement.clientWidth); scene.bgcolor = '#f4f6ef';
  const credit = d.family === 'terrain' ? 'Seeger & Minderhoud / DEM creators<br>CC BY-NC-SA 4.0 · adapted display samples'
    : d.family === 'population' ? 'Selected population producer · full notices below<br>CC BY 4.0 · native cell sample'
      : d.family === 'poster' ? 'Tobias et al. · AIDS2024 THPEF698<br>Published counts · approximate city anchors'
        : 'USGS / NASA Landsat · US Census Bureau<br>Public-domain source data · samples / whole tracts';
  await Plotly.react('plot-view', traces, {margin: {l: 0, r: 10, b: 60, t: 10}, paper_bgcolor: '#fffefa', font: {color: '#153740'}, scene,
    showlegend: false, annotations: [{xref: 'paper', yref: 'paper', x: 0, y: -.08, text: credit, showarrow: false, xanchor: 'left', font: {size: 10}}]},
    {responsive: true, displaylogo: false, modeBarButtonsToRemove: ['toImage', 'sendDataToCloud'], scrollZoom: false});
  if (!current()) return;
  const el = document.getElementById('plot-view');
  if (!el.querySelector('canvas')) throw new Error('The 3D canvas did not initialize. Use the local 2D map and table.');
  el.dataset.rendered = state.view;
  el._atlasResponsiveRadius = cameraRadius(el.clientWidth);
  el._atlasWidth = el.clientWidth;
  el.removeAllListeners('plotly_webglcontextlost');
  el.on('plotly_webglcontextlost', () => el.dispatchEvent(new CustomEvent('atlas-render-lost')));
  if (!resizeObserver) {
    resizeObserver = new ResizeObserver(() => {
      if (el.hidden || !el.data || el.clientWidth <= 0 || el.clientWidth === el._atlasWidth) return;
      const live = structuredClone(el._fullLayout.scene.camera);
      const radius = cameraRadius(el.clientWidth), ratio = radius / el._atlasResponsiveRadius;
      // Retain dragged direction, centre, up vector and relative zoom. Only the
      // responsive distance changes, so narrow plots fit without resetting orbit.
      for (const axis of ['x', 'y', 'z']) live.eye[axis] *= ratio;
      el._atlasWidth = el.clientWidth; el._atlasResponsiveRadius = radius;
      const update = {'scene.camera': live};
      if (el.data[0].type === 'surface') for (const [axis, labels] of Object.entries(terrainAxisLabels(el.clientWidth)))
        for (const [key, value] of Object.entries(labels)) update[`scene.${axis}.${key}`] = value;
      Plotly.Plots.resize(el).then(() => {
        if (!el.hidden && el.data) return Plotly.relayout(el, update);
      }).catch(() => {});
    });
    resizeObserver.observe(el);
  }
}

export function clear3D() {
  const el = document.getElementById('plot-view');
  if (window.Plotly && el.data) window.Plotly.purge(el);
  delete el.dataset.rendered;
}
