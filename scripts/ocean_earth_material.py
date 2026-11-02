"""Original offline activities and pinned source-course reading guides.

Source links were transcribed from the inspected course READMEs on 2026-11-01.
These seeds never download upstream material or overwrite canonical notebooks.
"""

OCEAN_COMMIT = "145a73e500cb06070f399a040206802cc279174e"
EARTH_COMMIT = "9a191f1fd30c40e09b48b9f92a9b5fdd9676509e"
OCEAN_REPO = "https://github.com/jltobias/JupyterLite-Global-Fishing-Watch-and-Dark-Vessels"
EARTH_REPO = "https://github.com/jltobias/JupyterLite-zarr-sql-views"
OCEAN_SITE = "https://jltobias.github.io/JupyterLite-Global-Fishing-Watch-and-Dark-Vessels/"
EARTH_SITE = "https://jltobias.github.io/JupyterLite-zarr-sql-views/"

OCEAN_CODE = '''from math import hypot

# Invented local planar kilometres and minutes from one arbitrary origin.
detections = [('S1', 0, 0, 0), ('S2', 5, 0, 10),
              ('S3', 10, 0, 20), ('S4', 15, 0, 30)]
ais_positions = [('A', 0.6, 0, 2), ('B', 4.5, 0, 10),
                 ('C', 5.5, 0, 11), ('D', 11, 0, 25),
                 ('E', 15.2, 0, 42)]
distance_gate_km = 1.0
time_gate_min = 5

def candidate_gate(detections, positions, distance_km, time_min):
    if distance_km < 0 or time_min < 0:
        raise ValueError('Gates must be nonnegative; inputs must be complete finite numbers.')
    return {sid: [aid for aid, ax, ay, at in positions
                  if hypot(ax-sx, ay-sy) <= distance_km and abs(at-st) <= time_min]
            for sid, sx, sy, st in detections}

candidates = candidate_gate(detections, ais_positions, distance_gate_km, time_gate_min)
counts = {'unique candidate': sum(len(ids) == 1 for ids in candidates.values()),
          'ambiguous': sum(len(ids) > 1 for ids in candidates.values()),
          'unmatched': sum(len(ids) == 0 for ids in candidates.values())}
denominator = len(detections)
print('Synthetic SAR detections (id, x km, y km, minute):', detections)
print('Synthetic AIS positions (id, x km, y km, minute):', ais_positions)
print(f'Inclusive gates: distance <= {distance_gate_km:g} km AND absolute time difference <= {time_gate_min:g} min')
print('Candidate IDs by detection:', candidates)
print('Counts / all synthetic SAR detections:', counts, '/', denominator)
print('Unmatched fraction:', counts['unmatched']/denominator if denominator else 'unknown (no detections)')
print(f"Current result: {counts['unique candidate']} unique-candidate, {counts['ambiguous']} ambiguous, {counts['unmatched']} unmatched of {denominator} detections.")
print('Candidates are retained, not assigned identities. No category determines legality or deliberate AIS suppression.')
bars(counts, f'Synthetic AIS–SAR: {distance_gate_km:g} km / {time_gate_min:g} min',
     f'SAR detections; denominator {denominator}')'''

CUBE_CODE = '''from datetime import date

# Invented support for two cells: eight days, then a shorter five-day final bin.
intervals = [('2021-12-19', '2021-12-27'), ('2021-12-27', '2022-01-01')]
interval_days = [(date.fromisoformat(end)-date.fromisoformat(start)).days
                 for start, end in intervals]
cube_rows = [
    {'cell': 'A', 'period': 0, 'burned_ha': 0,    'temperature_c': 20},
    {'cell': 'A', 'period': 1, 'burned_ha': 4,    'temperature_c': None},
    {'cell': 'B', 'period': 0, 'burned_ha': None, 'temperature_c': 30},
    {'cell': 'B', 'period': 1, 'burned_ha': 6,    'temperature_c': 10},
]

def summarize_support(rows, durations):
    possible_days = sum(durations[row['period']] for row in rows)
    result = {}
    for variable in ['burned_ha', 'temperature_c']:
        observed = [row for row in rows if row[variable] is not None]
        covered_days = sum(durations[row['period']] for row in observed)
        # Extensive hectares already describe a cell-period: do not multiply by days.
        total = sum(row[variable] for row in observed) if observed else None
        # An intensive weather mean uses its own observed cell-day support.
        weighted_mean = (sum(row[variable]*durations[row['period']] for row in observed)
                         / covered_days) if covered_days else None
        result[variable] = {'covered_cell_days': covered_days,
                            'possible_cell_days': possible_days,
                            'observed_rows': len(observed),
                            'observed_total': total if variable == 'burned_ha' else None,
                            'weighted_mean': weighted_mean if variable == 'temperature_c' else None}
    return result

support = summarize_support(cube_rows, interval_days)
print('Synthetic half-open intervals [start, end):', intervals, '; durations in days:', interval_days)
print('Invented cell-period rows:', cube_rows)
for variable, stats in support.items():
    metric = stats['observed_total'] if variable == 'burned_ha' else stats['weighted_mean']
    unit = 'ha observed total' if variable == 'burned_ha' else 'C weighted mean'
    value_text = f'{metric:.3f}' if metric is not None else 'unknown'
    print(f"{variable}: {value_text} {unit}; {stats['observed_rows']}/{len(cube_rows)} rows; "
          f"coverage {stats['covered_cell_days']}/{stats['possible_cell_days']} cell-days")
print('Zero is observed; None is missing. Each variable has its own mask. Incomplete coverage is not an estimate of the missing support.')
coverage_bars = {name: stats['covered_cell_days'] for name, stats in support.items()}
coverage_bars['possible support'] = support['burned_ha']['possible_cell_days']
bars(coverage_bars,
     'Synthetic cube: variable-specific coverage',
     'cell-days; possible support is a reference')'''

OCEAN_LESSON = (
    "Observe vessels, preserve uncertainty", "Terrain & Earth observation",
    "Ocean Watch connects historical Global Fishing Watch (GFW) study products, radar, environmental evidence and One Health questions across nine source lessons. GFW maps vessel activity from several data sources. The Automatic Identification System (AIS) broadcasts vessel-reported identity, position and time; satellite synthetic aperture radar (SAR) observes radar backscatter that may contain vessel-like detections.",
    "How do inclusive distance and time gates change AIS–SAR candidate ambiguity?",
    "Compare four invented SAR detections with five invented AIS position records. Coordinates are local planar kilometres, not longitude/latitude; times are minutes from an arbitrary origin. Detection labels S1–S4 and AIS position-record labels A–E are unique in this fixture. A candidate refers to a position record, not a confirmed vessel identity. Repeated reports require a deliberate identity-grouping policy before interpreting candidate counts as vessels. Keep every candidate within both inclusive gates. Zero candidates means unmatched, one means a unique candidate, and more than one remains ambiguous. Count categories over all four detections. This is an original candidate screen, not the source's matching algorithm or a one-to-one identity assignment. All fixture coordinates and times are complete finite numbers; gates must be nonnegative. It omits motion, position error, radar displacement, reception and uneven satellite coverage.",
    OCEAN_CODE,
    "At the default 1 km / 5 min gates, S1 has A; S2 retains B and C; S3 has D exactly at both boundaries; S4 has none. Thus 2/4 detections have a unique candidate, 1/4 is ambiguous and 1/4 is unmatched. The printed result and SVG recompute after edits. A unique candidate is only a candidate under a rule. An unmatched detection is not proof of illegal fishing, deliberate AIS suppression, or even a correctly detected vessel. These invented four detections cannot estimate fleet prevalence; real coverage and detection denominators differ.",
    "Set `time_gate_min = 15`, predict the candidates, then rerun: E becomes a candidate for S4, giving 3 unique-candidate, 1 ambiguous and 0 unmatched detections. Restore 5 minutes and reduce `distance_gate_km` to 0.99: boundary candidate D is excluded, giving 1 unique-candidate, 1 ambiguous and 2 unmatched. Explain why selecting the nearest candidate would hide ambiguity. Candidates may be reused across detections; this screen imposes no global assignment. State what independent identity and coverage evidence a real investigation would need.",
    "The pinned Ocean Watch course separates historical 2017–2021 study products, actual Sentinel-1 pixels and NOAA derivatives, synthetic experiments and optional live services. This atlas copies none of those data, code, imagery or the conceptual AI cover. Source 3D views need their own graphics/runtime support; current platform exports have product-specific access and rights."
)

CUBE_INTRO = """## Add an experiment: intervals and missing coverage

**Learning question:** How can a zero, a missing value and a short final interval change a cube summary?

This original **Python analogue of SQL** groups four invented cell-period rows. It does not read Zarr, execute SQL or load LexCube. The source course supplies actual SQL and LexCube capabilities through the links below. The two cells have equal teaching weight; weather is weighted by observed cell-days, not geographical area.

Retain one row per declared cell-period: two cells × two periods here. Missing measurements use `None`; do not drop their rows. This complete declared grid makes the possible-support denominator meaningful. A sparse or filtered table needs an independently declared expected grid before calculating complete-support coverage; the rows remaining in that table cannot establish the expected support by themselves.

Predict the summaries for intervals [2021-12-19, 2021-12-27) and [2021-12-27, 2022-01-01). Derive 8 and 5 days from the end dates, including the final closing boundary. `burned_ha` is extensive hectares per cell-period; sum observed values without multiplying by duration. `temperature_c` is an intensive period mean in invented degrees Celsius; multiply by duration and divide by that variable's covered cell-days. (The source SeasFire temperature uses kelvin.) `None` is unavailable, while numeric zero remains observed. Inputs must be finite numbers or None; each row's period must name a positive-duration interval.

In SQL terms these are separate `IS NOT NULL` masks, a guarded `SUM(burned_ha)`, and `SUM(temperature_c * days) / SUM(days)` over observed temperature rows. A truthiness filter would incorrectly drop zero. An all-missing variable must yield unknown, with coverage zero.
"""

CUBE_INTERPRET = """## Interpret the coverage result

The default observed burned total is **10 ha**, covering **18/26 cell-days** and three of four rows. It is not a complete-support total or a unique burned footprint. The observed temperature mean is **450/21 = 21.429 °C**, covering **21/26 cell-days** and three rows. Its unweighted row mean would be 20 °C. Neither denominator may be borrowed from the other variable. The zero burned value contributes eight observed days. Missing values are excluded without inventing zeros; the printed summaries and coverage SVG follow current inputs. The possible-support bar is a reference for the declared grid, not another measured variable.

## Change one thing

Replace both interval endpoints with a continuous pair of eight-day bins and predict the changed weather weighting. Then restore the dates and set every `burned_ha` to `None`: the burned total must print **unknown**, with **0/26 cell-days**; temperature remains unchanged. Finally set every temperature to None: its mean is unknown with zero coverage. A true observed zero total and an unknown total need different captions. Do not fill gaps to make a prettier time cube.

The source SeasFire studio retains shorter year-end intervals and variable-specific masks. Its burned area is historical hectares, not active-fire fronts; weather, vegetation and fire have different support. Seasonal associations or lags do not establish causes, forecasts, smoke exposure, crop losses or health effects. No actual SeasFire values enter this exercise.
"""

OCEAN_LESSONS = [
    ("01", "Observed ocean", "Historical 2017–2021 SAR-derived activity; coverage and denominators", "01_observed_ocean.ipynb"),
    ("02", "Ocean in 3D", "Observed map and a separate conceptual satellite-to-ecosystem scene", "02_ocean_in_3d.ipynb"),
    ("03", "Matching and uncertainty", "Synthetic AIS–SAR gates and assignments", "03_matching_and_uncertainty.ipynb"),
    ("04", "SAR detection", "Actual Sentinel-1 crop and a separate synthetic detector", "04_sar_detection.ipynb"),
    ("05", "Satellite catalog", "Saved real metadata and optional live STAC search", "05_satellite_catalog.ipynb"),
    ("06", "Environment and health", "NOAA analysis, separate synthetic series and confounding", "06_environment_and_health.ipynb"),
    ("07", "Food and equity", "Scenario accounting for retention, yield, loss and access", "07_food_and_equity.ipynb"),
    ("08", "Fish stocks", "Attributed FAO context and a hypothetical biomass model", "08_fish_stocks.ipynb"),
    ("09", "GFW workbench", "Synthetic CSV schema until a user supplies an export", "09_gfw_workbench.ipynb"),
]


def ocean_overview():
    rows = [f"| {n} · {title} | {description} | [Pinned notebook]({OCEAN_REPO}/blob/{OCEAN_COMMIT}/content/{filename}) |"
            for n, title, description, filename in OCEAN_LESSONS]
    return "\n".join([
        "## Nine source lessons: Ocean Watch",
        "James L. Tobias / jltobias, *Ocean Watch: Fishing, Dark Vessels & One Health*, inspected 2026-11-01. The following are source files at the reviewed commit, not unverified reconstructed Lab launchers.",
        "\n| Lesson | Evidence / purpose | Source file |\n|---|---|---|", *rows,
        "\n## Connect the idea: One Health",
        "Marine ecosystems, aquatic foods, livelihoods, labor conditions and coastal environmental exposures can interact with human, animal and ecosystem health. Use the [WHO/OHHLEP One Health definitions and principles](https://www.who.int/publications/m/item/one-health-definitions-and-principles) to ask which pathway and measurements a study needs. Vessel activity alone measures neither catch, stock abundance, dietary intake, contaminants nor disease; these fixtures support no causal health inference. Invite affected communities into framing and interpretation.",
        "\n## Ocean citations, rights and use",
        "- Paolo, F. S., Kroodsma, D., Raynor, J., et al. (2024). *Satellite mapping reveals extensive industrial activity at sea*. Nature **625**, 85–91. [Paper](https://doi.org/10.1038/s41586-023-06825-8). The 2017–2021 [analysis-data deposit](https://doi.org/10.6084/m9.figshare.24309475.v4), Paolo, Kroodsma, Davis & Hochberg (2024), version 4, is **CC BY 4.0**. It is linked context, not an input to this atlas.",
        "- Global Fishing Watch, [apparent-fishing guidance](https://globalfishingwatch.org/dataset-and-code-fishing-activity/) and [platform terms](https://globalfishingwatch.org/terms-of-use/), inspected 2026-11-01: **CC BY-NC 4.0** for the described services; retain product-specific metadata. The deposit's CC BY license does not automatically cover new platform exports.",
        "- NOAA NCEI, [OISST v2.1](https://www.ncei.noaa.gov/products/optimum-interpolation-sst), and [Sentinel-1 RTC / Microsoft Planetary Computer](https://planetarycomputer.microsoft.com/dataset/sentinel-1-rtc) are source-course inputs only. Source acknowledgement: Contains modified Copernicus Sentinel data (2024), processed by Microsoft Planetary Computer. Natural Earth coastline is public domain. No pixels, coastline or temperature observations are copied here; product-specific terms apply.",
        "- FAO (2025), *Review of the state of world marine fishery resources – 2025*, supplies source-course stock context; [assessment announcement](https://www.fao.org/newsroom/detail/fao-releases-the-most-detailed-global-assessment-of-marine-fish-stocks-to-date). [ICEYE's dark-vessel article](https://www.iceye.com/blog/dark-vessels-in-northern-europe-and-how-iceyes-satellites-find-them) motivates the commercial-SAR discussion; no vendor graphics, detections or performance claims are reproduced.",
        f"\nThe [pinned source register]({OCEAN_REPO}/blob/{OCEAN_COMMIT}/content/sources.md) and [methods]({OCEAN_REPO}/blob/{OCEAN_COMMIT}/content/methods.md) retain exact queries, attribution and further provider references. Source software is MIT; source prose/figures are CC BY 4.0 where applicable. This atlas's candidate fixture, code and SVG are original, separately licensed under MIT (code) and CC BY 4.0 (prose/figures/fixtures). No institutional endorsement is implied.",
    ])


def earth_overview(lessons):
    groups = [(1, 12, "Foundations", "Browser experiments, Zarr chunks/SQL rows, observed DE Africa water, linked maps/cubes, C3S warming levels, synthetic heat/coasts/air/water/food questions, STAC/GeoLibre and an evidence-led capstone."),
              (13, 16, "AR6 port-city studio", "Archive/chunk access, gauge proxies, regional grids/3D/time cubes and threshold uncertainty. Conditional projections are not gauge observations or flood probabilities; one workflow's percentiles are not the assessed p-box. Scenarios have no assigned probabilities; no rates or first-crossing dates are supported."),
              (17, 21, "GeoTessera studio", "Annual vectors/quantization, cosine similarity/SQL, shared PCA/3D, clusters/transfer and annual differences. Learned representations and observation counts are not hazard measurements, class probabilities or model confidence."),
              (22, 25, "Global FTW studio", "Discovery, three-class probability/SQL/3D, polygons/confidence/selection and annual food–water questions. Predicted fields are not legal parcels or ownership. Pixel probability differs from the separate 500 m confidence layer; annual differences need independent validation."),
              (26, 30, "SeasFire and LexCube studio", "Discovery/masks/units, historical fire maps/SQL/animation, seasons/lags, actual LexCube slicing and linked comparisons. Source uses two 16×16 native windows in 2001–2021; masks and shorter year-end intervals matter. Hectares differ from duration-weighted weather means. No forecast or causal/health claim is supported.")]
    sections = ["## Thirty source lessons: Earth in the Browser",
                f"James L. Tobias / jltobias, *Earth in the Browser*, inspected 2026-11-01, [commit `{EARTH_COMMIT[:12]}`]({EARTH_REPO}/blob/{EARTH_COMMIT}/README.md). Every Run URL below is transcribed from that README. They open the external source course. HTTP GET returned 200 on 2026-11-01 for the entry documents; query-target execution, graphics and providers were not certified. The original atlas chunk exercise above is preserved; the coverage exercise is additive."]
    for first, last, title, summary in groups:
        sections.extend([f"\n### {first:02d}–{last:02d} · {title}", summary,
                         "\n| Lesson and investigation | Source Lab |\n|---|---|"])
        sections.extend(f"| {n} · {label} | [Run {n}]({url}) |" for n, label, url in lessons if first <= int(n) <= last)
    sections.append(f"\nLessons 29–30 run **LexCube 2.0.1** in the source JupyterLite kernel, separately from the SQL/deck.gl map/cube explorer. See [corresponding source, GPL license and Pyodide adaptation]({EARTH_SITE}vendor/lexcube/README.md). The documented adaptation uses WebAssembly-compatible dependencies and disables a native psutil memory diagnostic; this index embeds none of its wheel, frontend or source archive. Source first launch downloads runtimes/dependencies; 3D needs WebGL2. Native data preparation remains separate. The local atlas exercises use only standard-library Python and IPython display.")
    sections.append(EARTH_CITATIONS)
    return "\n".join(sections)


EARTH_CITATIONS = f"""## Earth studio citations, rights and use

- Alonso, L., Gans, F., Karasante, I., et al. (2024). *SeasFire Cube: A Global Dataset for Seasonal Fire Modeling in the Earth System*, **v0.4**, [Zenodo](https://doi.org/10.5281/zenodo.13834057), **CC BY 4.0**. Karasante, I., et al. (2025), *SeasFire cube — a multivariate dataset for global wildfire modeling*, Scientific Data **12**, 368, [paper](https://doi.org/10.1038/s41597-025-04546-3). Credit the SeasFire consortium/ESA; EC JRC/GWIS burned area; ECMWF/Copernicus ERA5 weather; NASA MODIS MOD13C1 v6 NDVI; ESA EarthCODE/CloudFerro Zarr hosting. VPD and cell area are derived, not independent observations. [GWIS](https://gwis.jrc.ec.europa.eu/) · [ERA5](https://doi.org/10.24381/cds.adbb2d47) · [MOD13C1 v6](https://doi.org/10.5067/MODIS/MOD13C1.006).
- Söchting, M., Scheuermann, G., Montero, D., & Mahecha, M. D. (2025). *Interactive Earth system data cube visualization in Jupyter notebooks*. Big Earth Data **9(2)**, **321–335**. [DOI](https://doi.org/10.1080/20964471.2025.2471646). **LexCube 2.0.1**, Maximilian Söchting and contributors, **GPL-3.0-or-later**; credit RSC4Earth/Leipzig University and ESA DeepESDL/DFG NFDI4Earth. [Upstream](https://github.com/msoechting/lexcube) · [source adaptation]({EARTH_SITE}vendor/lexcube/README.md). The source course's ISC license does not relicense LexCube.
- Robinson, C., Muhawenayo, G., Khanal, S., et al. (2026). *The first global agricultural field boundary map at 10 m resolution*. [arXiv:2605.11055](https://doi.org/10.48550/arXiv.2605.11055). [Global Fields of the World](https://source.coop/ftw/global-data), alpha predictions **2024/2025**, **CC BY 4.0**. Credit Taylor Geospatial and collaborators, Microsoft AI for Good, participating universities, Copernicus Sentinel-2 and Source Cooperative/Radiant Earth. No predictions or polygons are copied here.
- Feng, Z., et al. (2025; revised 2026). *TESSERA: Temporal Embeddings of Surface Spectra for Earth Representation and Analysis*. [arXiv:2506.20380](https://doi.org/10.48550/arXiv.2506.20380). Source uses **TESSERA v1.1 / dClimate**. Credit TESSERA/University of Cambridge and collaborators, dClimate global inference/hosting and GeoTessera contributors. [Terms](https://github.com/ucam-eo/tessera/blob/master/aup.md) explicitly declare data **CC0**, with advisory ethical guidance and inconsistent legacy CC-BY wording retained upstream; GeoTessera code is MIT. No embeddings or model weights are copied here.
- Garner, G. G., et al. (2021). *IPCC AR6 Sea Level Projections*, **v20210809**, [dataset](https://doi.org/10.5281/zenodo.5914709), **CC BY 4.0**. Also credit Fox-Kemper et al. (2021), WG1 Chapter 9, [DOI](https://doi.org/10.1017/9781009157896.011), and Kopp et al. (2023), FACTS v1.0, GMD **16**, 7461–7489, [DOI](https://doi.org/10.5194/gmd-16-7461-2023). Thank the projection authors, supporting funding agencies and NASA Sea Level Change Team for the projection tool. The [pinned Rutgers-ESSP guide](https://github.com/Rutgers-ESSP/IPCC-AR6-Sea-Level-Projections/tree/8ee75128d8f6d9a8ba9825f47c92d11955d0651e) and [NASA tool](https://sealevel.nasa.gov/ipcc-ar6-sea-level-projection-tool) retain assessed-product guidance. No projection extract is copied here.

The source adaptation credits [dzole0311/zarr-sql-views](https://github.com/dzole0311/zarr-sql-views), ISC. The source course's original code, lessons and SVG artwork remain **ISC**; its data and LexCube have the separate terms above. This index uses original synthetic fixtures, MIT code and CC BY 4.0 prose/figures, without copying source datasets, code or artwork. Complete provider notices and transformations are in the [pinned source credits]({EARTH_REPO}/blob/{EARTH_COMMIT}/book/credits.md), [SeasFire guide]({EARTH_REPO}/blob/{EARTH_COMMIT}/book/seasfire.md), [FTW guide]({EARTH_REPO}/blob/{EARTH_COMMIT}/book/fields.md), [GeoTessera guide]({EARTH_REPO}/blob/{EARTH_COMMIT}/book/embeddings.md) and [AR6 guide]({EARTH_REPO}/blob/{EARTH_COMMIT}/book/sea-level.md). No institutional endorsement is implied.
"""


EARTH_LESSONS = [('01',
  'A browser is a scientific workspace',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=01_start_here.ipynb'),
 ('02',
  'From Zarr chunks to SQL rows',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=02_zarr_sql.ipynb'),
 ('03',
  'Lake Ngami: water observations and missing evidence',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=03_deafrica_water.ipynb'),
 ('04',
  '2D maps, 3D maps, and a space–time cube',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=04_maps_and_cubes.ipynb'),
 ('05',
  'C3S Atlas: scenarios, warming levels, and model spread',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=05_c3s_atlas.ipynb'),
 ('06',
  'Global heat questions, African heat laboratory',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=06_heat_stress.ipynb'),
 ('07',
  'Sea-level rise and the meaning of a 3D scene',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=07_coastal_scenes.ipynb'),
 ('08',
  'Air quality: a map is not an exposure estimate',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=08_air_quality.ipynb'),
 ('09',
  'Water quality: from optical signal to a testable hypothesis',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=09_water_quality.ipynb'),
 ('10',
  'Food and water insecurity',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=10_food_water.ipynb'),
 ('11',
  'STAC discovery and GeoLibre handoff',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=11_stac_geolibre.ipynb'),
 ('12',
  'Capstone: an evidence-led climate story',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=12_capstone.ipynb'),
 ('13',
  'Open the AR6 archive without downloading the world',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=13_ar6_archive.ipynb'),
 ('14',
  'Five port cities, four tide-gauge proxies',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=14_ar6_port_cities.ipynb'),
 ('15',
  'Regional grids, 3D maps, and sea-level time cubes',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=15_ar6_grid_maps.ipynb'),
 ('16',
  'Threshold questions without false flood probabilities',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=16_ar6_uncertainty.ipynb'),
 ('17',
  'GeoTessera: from satellite years to embedding vectors',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=17_tessera_embeddings.ipynb'),
 ('18',
  'Similarity search: vectors, maps, Zarr and SQL',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=18_tessera_similarity.ipynb'),
 ('19',
  'PCA colors and a three-dimensional embedding space',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=19_tessera_pca.ipynb'),
 ('20',
  'Clusters, transfer and the need for independent labels',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=20_tessera_clusters.ipynb'),
 ('21',
  'Annual embedding differences and coastal evidence',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=21_tessera_change.ipynb'),
 ('22',
  'Global FTW: discover fields, probabilities and confidence',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=22_ftw_discovery.ipynb'),
 ('23',
  'FTW probability cubes: maps, SQL and 3D',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=23_ftw_probability_sql.ipynb'),
 ('24',
  'Field polygons, confidence and selection bias',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=24_ftw_fields_confidence.ipynb'),
 ('25',
  'Annual field predictions and food–water questions',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=25_ftw_change_food_water.ipynb'),
 ('26',
  'SeasFire: read the cube before reading the fire',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=26_seasfire_discovery.ipynb'),
 ('27',
  'Burned area: maps, SQL and a moving season',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=27_seasfire_maps_sql.ipynb'),
 ('28',
  'Seasons, anomalies and lagged relationships',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=28_seasfire_seasons_lags.ipynb'),
 ('29',
  'LexCube: slice a real fire cube in the browser',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=29_seasfire_lexcube.ipynb'),
 ('30',
  'LexCube comparisons: fire, dryness and evidence',
  'https://jltobias.github.io/JupyterLite-zarr-sql-views/lite/lab/index.html?path=30_seasfire_lexcube_compare.ipynb')]
