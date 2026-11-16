"""Original companions and reviewed metadata for the 2026-11-16 course append.

The constants are local editorial inputs, never a fetch or upstream execution.
"""
LESSONS = {
 'c3s-atlas': {
  'title':'Read a warming window without inventing an observation', 'theme':'Terrain & Earth observation',
  'summary':'Twenty complete source lessons connect anomalies, regions and uncertainty with a real model-window table, real generalized coastline, catalogue metadata and separately labelled synthetic arrays.',
  'question':'How do latitude weighting and missing coverage change the mean of a small synthetic climate field?',
  'method':'Equal-angle grid cells cover less area toward the poles. For this two-band thought experiment, use cosine(latitude) as a relative area weight and exclude missing values from both numerator and denominator. A warming-level window is a model/scenario time interval, not a measured temperature or a prediction for one city.',
  'exercise':'''from math import cos, radians
latitudes = [0, 60]
field = [[0, 0], [9, 9]]  # synthetic temperature changes, degrees C
def area_mean(values):
    pairs = [(value, cos(radians(lat))) for lat,row in zip(latitudes,values) for value in row if value is not None]
    if not pairs:
        raise ValueError('No valid area remains')
    return sum(value*weight for value,weight in pairs)/sum(weight for _,weight in pairs)
full_mean = area_mean(field)
missing_mean = area_mean([[0, None], [9, 9]])
print('Latitude bands:', latitudes, 'synthetic field:', field)
print('Valid cells: full 4; missing example 3. Missing is not zero.')
bars({'unweighted':4.5,'area weighted':full_mean,'one cell missing':missing_mean}, 'Synthetic latitude weighting and coverage', 'degrees C')''',
  'interpret':'The complete area-weighted mean is 3 degrees C; with one equatorial zero missing it is 4.5. The unweighted complete mean is also 4.5 for a different reason. Equal answers do not establish equivalent support. Cosine weighting here assumes equal longitude widths and representative band centres; real cell bounds and masks require their own weights.',
  'change':'Replace the missing cell with zero, then move the second latitude to 30 degrees. Predict the direction before rerunning. In source lesson 12 inspect the actual CMIP6 model/scenario/threshold window and distinguish its endpoints from its midpoint. In lesson 14 compare complete and masked coverage before reporting a mean.',
  'reading':'All 20 source notebooks, atlas_helpers.py, data manifest, licenses, credits, data guide and learning resources are bundled in the course. Browser setup prepares numpy, pandas, matplotlib and Plotly 6.5.0. Local figures and numerical alternatives remain available; optional interactive Plotly rendering needs its versioned CDN/WebGL. Authenticated CDS downloads, xarray/netCDF4 preparation, archives and native regridding remain source/desktop continuations.',
  'limits':'Original course MIT. Retain European Union/C3S/ECMWF, CSIC/Predictia and underlying CMIP6 modelling-group credit. The real warming-level auxiliary CSV is Apache-2.0, the Natural Earth coastline is public domain, and the CC BY 4.0 CDS catalogue snapshot is metadata rather than gridded climate data. monthly_series.csv and generated lesson arrays are explicitly synthetic (seed 381). The cleared original splash and its generation provenance are retained. References include Gutiérrez et al. (2024), DOI 10.21957/ah52ufc369; Iturbide et al. (2020), DOI 10.5194/essd-12-2959-2020; CDS dataset DOI 10.24381/cds.h35hb680.'},
 'destination-earth-digital-twin': {
  'title':'Check an interpolated field before calling it a twin', 'theme':'Terrain & Earth observation',
  'summary':'Thirty-two complete synthetic experiments introduce Destination Earth architecture, grids, interpolation, validation, ensembles and bounded service handoffs.',
  'question':'Can bilinear interpolation reproduce a planar synthetic field, and what does that check leave untested?',
  'method':'Bilinear interpolation blends four corner values using relative coordinates inside a rectangle. Its weights must sum to one. An affine plane gives an independent exact oracle; agreement tests the interpolation arithmetic without validating the physics, observations or an operational Digital Twin.',
  'exercise':'''south, north, west, east = 0, 10, 0, 10
latitude, longitude = 2, 7
tx = (longitude-west)/(east-west)
ty = (latitude-south)/(north-south)
weights = {'SW':(1-tx)*(1-ty),'SE':tx*(1-ty),'NW':(1-tx)*ty,'NE':tx*ty}
corners = {'SW':0,'SE':30,'NW':20,'NE':50}  # synthetic plane 3*lon+2*lat
interpolated = sum(weights[key]*corners[key] for key in weights)
oracle = 3*longitude+2*latitude
print('Synthetic bilinear result:', interpolated, '; independent plane oracle:', oracle)
print('Weight sum:', sum(weights.values()), '; absolute error:', abs(interpolated-oracle))
assert abs(interpolated-25) < 1e-12 and abs(sum(weights.values())-1) < 1e-12
bars(weights, 'Synthetic interpolation contributions', 'dimensionless weight')''',
  'interpret':'At latitude 2, longitude 7, the field is 25 synthetic units, with weights SW 0.24, SE 0.56, NW 0.06 and NE 0.14. A successful plane check does not establish validity at discontinuities, across longitude seams, outside the rectangle, or with missing corners. Neither interpolation nor a polished globe makes these values observations.',
  'change':'Move the target to a corner and then the centre. Add a bounds check before trying extrapolation. Replace one corner with a missing value and write an explicit policy rather than silently substituting zero. Continue with source lessons 11 and 13 to compare interpolation and forecast verification.',
  'reading':'All 32 source notebooks and earthlab.py are bundled, with the coverage/access guides and original BibTeX reference. Browser setup requests numpy, matplotlib, pandas, xarray and ipywidgets. Five optional widget branches require the source frontend; static plots and printed values are alternatives. Fresh native calculations and actual browser graphics are separate checks. Real DTE, Climate DT, Weather-Induced Extremes DT, Polytope, Data Lake, Earthkit, ML and HPC services remain external authorized continuations.',
  'limits':'Independent teaching companion; European Union initiative implemented by ECMWF, ESA and EUMETSAT, with no endorsement implied. All default numerical inputs are original synthetic equations/seeded arrays, not observations, operational forecasts or Digital Twin outputs. Code MIT; original prose/generated numerical data/artwork CC BY 4.0, with repository attribution and adaptation notice retained. Original splash generation provenance credits OpenAI image-generation assistance. ECMWF Generation 2 Climate DT DOI 10.21957/79c6af3105 is cited as metadata context: the dataset is not used. No accounts, credentials or real service/model calls occur.'},
 'urbanity': {
  'title':'Trace a synthetic street route and name its assumptions', 'theme':'Browser GIS',
  'summary':'Seven complete standard-library lessons connect streets, urban graphs, contextual summaries, synthetic imagery labels, visualisation and reproducible exports.',
  'question':'Which shortest path does breadth-first search find in a small unweighted street graph?',
  'method':'Treat each undirected edge as one traversable connection. Breadth-first search visits routes in increasing edge count; alphabetical neighbour order makes ties reproducible. This is a synthetic topological graph, with no street geometry, travel times, direction, accessibility or real OSM evidence.',
  'exercise':'''from collections import deque
edges = [('A','B'),('A','D'),('B','C'),('B','D'),('B','E'),('C','F'),('D','E'),('E','F')]
graph = {node:set() for edge in edges for node in edge}
for left,right in edges:
    graph[left].add(right);graph[right].add(left)
queue = deque([['A']]);visited = {'A'}
while queue:
    route = queue.popleft()
    if route[-1] == 'F':
        break
    for neighbor in sorted(graph[route[-1]]):
        if neighbor not in visited:
            visited.add(neighbor);queue.append(route+[neighbor])
else:
    raise ValueError('No synthetic route from A to F exists; the search is exhausted.')
degrees = {node:len(graph[node]) for node in sorted(graph)}
print('Synthetic graph:', len(graph), 'nodes;', len(edges), 'edges')
print('Deterministic shortest route:', ' -> '.join(route), '; edges:', len(route)-1)
bars(degrees, 'Synthetic street-node degrees', 'undirected connections')''',
  'interpret':'The graph has six nodes and eight edges. Degrees are A2, B4, C2, D3, E3, F2; the deterministic route A → B → C → F has three edges. Other equal-length paths may exist. Highest degree is neither best service access nor social importance. Invented labels and topology do not describe any real neighbourhood.',
  'change':'Remove B–C, rerun and compare the route. Add edge lengths only after replacing BFS with an appropriate weighted method. In the source urban-context lesson keep building area, population and zone area as separate quantities. Explain why the graph-ML held-out error is useful evidence rather than hiding it.',
  'reading':'All seven notebooks retain the authoritative source TOC order and the sibling notebooks/_static relation for the pipeline illustration. Executable source cells use only standard-library Python; they do not import Urbanity. The three local SVGs are original vector teaching artwork. Native Urbanity installation, OSM acquisition, compiled geospatial dependencies, imagery credentials and optional graph ML remain explicitly linked continuations.',
  'limits':'Owner-authorized original source companion; this source repository has no public license grant, and the MIT license of the separate Urbanity software package does not relicense it. Synthetic diagrams, graph records and imagery labels are not provider data. Independent companion with no Urbanity endorsement. Retain Yap, Stouffs & Biljecki (2023), DOI 10.1038/s42949-023-00125-w; streetscape DOI 10.1177/23998083221138832; global networks DOI 10.1038/s41597-023-02578-1; urban graphs DOI 10.17605/OSF.IO/ABYQH; conditional building-carbon reference DOI 10.1038/s41893-025-01615-8. Each external dataset/provider retains separate terms.'},
 'terrio': {
  'title':'Separate pixel positions, map coordinates and runtime compatibility', 'theme':'Browser GIS',
  'summary':'Thirteen complete TerrIO reading/editing copies preserve real Natural Earth countries, original SVG chapter cards, helpers and synthetic raster/vector/point-cloud workflows.',
  'question':'Where is a pixel centre in a projected raster, and why does a correct coordinate not establish runtime compatibility?',
  'method':'For a north-up raster with no rotation, a pixel centre lies half a pixel beyond its zero-based column and row origin. A negative vertical pixel size means row indices grow southward. Projected metres differ from longitude/latitude degrees; never attach an invented WGS84 CRS to projected coordinates.',
  'exercise':'''from math import cos, radians
origin_x, origin_y = 500000, 4400000
pixel_width, pixel_height = 30, -30
column, row = 10, 20
centre_x = origin_x+(column+0.5)*pixel_width
centre_y = origin_y+(row+0.5)*pixel_height
scale = {str(lat)+' degrees':1/cos(radians(lat)) for lat in [0,30,60]}
print('Synthetic projected pixel centre (metres):', (centre_x,centre_y))
print('Zero-based array index (row, column):', (row,column))
assert (centre_x,centre_y) == (500315,4399385)
bars(scale, 'Idealized Mercator local length scale', 'map distance / ground distance')''',
  'interpret':'Column 10, row 20 has centre (500315, 4399385) projected metres. This coordinate is synthetic and has no declared real CRS. Ideal spherical Mercator scale is 1 at the equator and 2 at 60 degrees: equal map lengths can represent different ground lengths. This stdlib exercise runs in Atlas independently of the TerrIO wasm package.',
  'change':'Double the pixel size while keeping the origin fixed; predict the centre displacement. Then change the row to zero and explain the half-pixel offset. Before transferring an actual vector/raster export, keep CRS, affine transform, NoData, units and source receipt together; reproject with a verified tool before using the WGS84 GIS workbench.',
  'reading':'All 13 source notebooks and terrio_lab.py, countries.geojson, sources.json, chapter SVGs, chapter registry and attribution/resources guides are retained. The imported TerrIO notebooks are reading/editing copies in Atlas: TerrIO 0.9.0 has a pyemscripten_2025_0 wasm ABI for Pyodide 0.29. The source pins kernel 0.8.0b0, whose default is Pyodide 0.29.4; Atlas uses Pyodide 314. Run TerrIO in the matched [source Lab](https://jltobias.github.io/JupyterLite-terrio/lite/lab/index.html?path=01-first-contact.ipynb). Do not install its incompatible wheel or downgrade Atlas. Source Plotly 6.3.1/xarray 2025.10.1, CDN and WebGL requirements remain explicit; static and numerical alternatives are available. Native HTTP range I/O and specialized drivers remain optional native continuations.',
  'limits':'Original code MIT; original teaching prose/synthetic data/13 chapter SVGs CC0. No TerrIO wheel is redistributed. Keep TerrIO/dependency/EPSG/IOGP notices separate. The sole bundled real geographic dataset is Natural Earth countries v5.1.2, 177 generalized features, public domain: Made with Natural Earth; Patterson, Kelso and contributors. It is not authoritative boundary evidence. All terrain, reflectance, stations, points and cube examples are explicitly synthetic. Cite Wu, Fitzgerald & Morales Sanchez (2026), TerrIO software concept DOI 10.5281/zenodo.23642204, separately from software version 0.9.0 and this course commit; the course has no assigned DOI.'},
}

COURSE_VISUALS={
 'c3s-atlas':('assets/atlas-splash.png','Original conceptual climate Atlas illustration; not observational imagery.',
    'Original C3S companion artwork, MIT to the extent licensable. [Generation provenance](https://github.com/jltobias/JupyterLite-C3S-Atlas/blob/b41c3e1098a4fb94cef48b3044fe19c6ce7c1a1a/assets/PROVENANCE.md); no logos or third-party satellite textures.'),
 'destination-earth-digital-twin':('assets/splash.png','Original abstract Earth and synthetic weather streamlines; not a Digital Twin output.',
    'JupyterLite-Destination-Earth-Digital-Twin, with OpenAI image-generation assistance; original artwork CC BY 4.0 to the extent licensable. [Generation provenance](https://github.com/jltobias/JupyterLite-Destination-Earth-Digital-Twin/blob/0e32b2477ba5c0030985e25f1071d94cddabf130/assets/GENERATION.md). Atlas placement/adaptation; no agency endorsement.'),
 'urbanity':('_static/urbanity-splash.svg','Original vector illustration introducing a synthetic urban learning graph.',
    'Owner-authorized original Urbanity companion illustration; no public repository license inferred. No provider imagery or real OSM data are depicted.'),
 'terrio':('assets/01-first-contact.svg','Original TerrIO first-contact chapter diagram using local vector shapes and text.',
    'Original code-generated teaching diagram, CC0. TerrIO software and dependency terms remain separate in the retained notices.'),
}

PROFILE_DETAILS = {
 'c3s-atlas': ('C3S Atlas', 'B + O', 'How does a real coastline context differ from a synthetic climate field and a model warming window?',
  'The bundled Natural Earth coastline is real generalized geography. The C3S warming-level CSV has model/scenario windows; the CDS snapshot is catalogue metadata. Seeded monthly values are synthetic and have no point geometry.',
  [('warming windows','12-global-warming-levels.ipynb'),('region weights','14-regions-and-weights.ipynb'),('Natural Earth coastline','data/reference/ne_110m_coastline.geojson'),('source manifest','data/manifest.json')],
  'Inspect a bounded copy of the attributed coastline and its CRS before import. Keep synthetic climate values separate; do not turn model-window rows into measured local temperatures.',
  'Compare the same coastline extent and one feature identifier with RustGIS. Use a separate synthetic geographic layer only after explicitly defining its support, units and fixture status.',
  'Explain why the supplied model/scenario window and synthetic monthly series cannot establish a local observed trend.',
  'A later regional emulator needs independent held-out model/time windows and a stated target; latitude weights and map styling are deterministic analysis.',
  'Retain Natural Earth credit, model/scenario/threshold/endpoints, synthetic labels and valid-area denominator.'),
 'destination-earth-digital-twin': ('Destination Earth Digital Twin', 'O; C continuation', 'Can a synthetic interpolation check support a bounded map handoff without claiming a real Digital Twin product?',
  'All 32 source lessons use original equations and seeded synthetic arrays. earthlab.py and the access guide are bundled; no real DestinE output or observational dataset is packaged.',
  [('interpolation','11-interpolation.ipynb'),('validation','13-verification.ipynb'),('official access boundary','book/official-access.md')],
  'Build a tiny explicitly synthetic WGS84 fixture from the exercise only after declaring coordinates and units; compare one interpolated value to the plane oracle before exporting.',
  'Import that same synthetic fixture and compare feature IDs, 25-unit oracle value and missingness. Actual authorized DestinE exports need their own provenance and service terms.',
  'Identify which supplied results are synthetic arithmetic checks and which claims would require independent observations or a real DestinE service.',
  'A later learned surrogate needs independent observations, spatial/time holdouts and uncertainty; a Canvas globe or interpolation is not a validated twin.',
  'Reconcile IDs, bilinear weights summing to one, units, synthetic labels and explicit exclusion of real-service certification.'),
 'urbanity': ('Urbanity', 'O; N continuation', 'Which assumptions are lost when a synthetic unweighted street graph is drawn as a geographic network?',
  'Seven standard-library lessons use synthetic graph/context/imagery-label records without real OSM, provider imagery or Urbanity package execution. No public repository license is inferred.',
  [('street graph','notebooks/street-networks.ipynb'),('urban context','notebooks/urban-context.ipynb'),('held-out graph exercise','notebooks/graph-ml.ipynb')],
  'Use a declared synthetic geographic graph only if coordinates and a CRS are explicitly added; preserve its invented status and compare six nodes/eight edges. Topological labels alone are not geographic data.',
  'Compare the same synthetic nodes and route A–B–C–F in a second view; record differences between edge count and distance. Native Urbanity/OSM/imagery work needs its own licensed inputs and environment.',
  'Explain how degree and unweighted shortest paths can misrepresent accessibility using the supplied synthetic node IDs.',
  'The source toy held-out classification is a learning exercise; real urban graph ML needs independent places, defensible labels and leakage checks.',
  'Keep six node IDs, eight edge pairs, route tie-breaking, synthetic labels and owner-authorized source scope visible.'),
 'terrio': ('TerrIO', 'B + O; matched source runtime', 'Which CRS and provenance checks must accompany a TerrIO export before a geographic browser handoff?',
  'Natural Earth countries v5.1.2 are real public-domain generalized geography; remaining raster/point/cube fixtures are synthetic. Atlas copies are reference-only because TerrIO 0.9.0 requires Pyodide 0.29 rather than Atlas 314.',
  [('coordinate checks','02-coordinates.ipynb'),('country vectors','03-vectors-2d-maps.ipynb'),('interoperability','12-interoperability.ipynb'),('Natural Earth sources','data/sources.json')],
  'For a direct geography exercise, use an attributed bounded copy of the bundled WGS84 Natural Earth countries. For TerrIO-created exports, run the matched source Lab and verify the reopened file/CRS before import.',
  'Import the same reviewed country subset and compare ADMIN-name multisets, selected count and attribution. Keep projected pixel coordinates out of WGS84 exports until a verified transformation.',
  'Audit the supplied CRS, transform, NoData, ADMIN names and separate synthetic/real status; state what cannot be inferred from generalized boundaries.',
  'Future raster classification requires independent imagery/labels and spatial holdouts; format conversion, NDVI thresholds and terrain styling are not fitting.',
  'Retain Made with Natural Earth, version 5.1.2, 177-feature source count, subset IDs, CRS and TerrIO 0.29 ABI source-runtime boundary.'),
}


def profiles():
    result=[]
    for slug,(title,route,question,readiness,links,rust,geo,ai,extension,check) in PROFILE_DETAILS.items():
        result.append({'slug':slug,'title':title,'route':route,'question':question,'data_readiness':readiness,
            'source_links':[{'label':label,'path':f'courses/{slug}/{path}'} for label,path in links],
            'rustgis_task':rust,'geolibre_task':geo,'ai_prompt':ai,'geoai_extension':extension,'evidence_check':check})
    return result
