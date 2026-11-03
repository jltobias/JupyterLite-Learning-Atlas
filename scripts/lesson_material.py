"""Original, bounded teaching activities. Used only to seed missing canonical notebooks.

After generation, edit content/**/*.ipynb directly: generate.py never overwrites them.
All observations below are invented. No health records, model service, or remote data.
"""
from ocean_earth_material import OCEAN_LESSON
from coral_material import CORAL_LESSON

# key: short repository name; title, theme, summary, question, method, code,
# interpretation, extension, source-specific limitation.
LESSONS = {
    "Shiny-Live-Apps": (
        "Prototype a reactive rule before an app", "Foundations",
        "A title-only public source stub motivates an original browser-Python prototype; no Shiny app is supplied or verified.",
        "How should a displayed count respond when its input threshold changes?",
        "Treat an input, a pure calculation and a displayed result as three separate parts of a prototype. Predict counts at three thresholds for six invented values; this notebook does not run Shiny or reproduce source functionality. These fixtures have no missing values. Calculations require complete finite numeric values, including thresholds; define a missing-data rule before introducing missing data.",
        "observations = [1, 2, 4, 4, 7, 9]\nthresholds = [3, 5, 8]\ndef count_at_or_above(values, threshold):\n    return sum(value >= threshold for value in values)\ncounts = {str(t):count_at_or_above(observations, t) for t in thresholds}\nprint('Invented observations:', observations)\nprint('Input thresholds:', thresholds, '; rule: value >= threshold')\nbars(counts, 'Original synthetic app-rule prototype', 'values at or above input')",
        "The counts are 4, 2 and 1. Raising the threshold cannot increase this count. A working pure calculation is only one part of an app: it does not establish a reactive user interface, accessibility or a deployed service.",
        "Add threshold 4 and predict how ties are handled. Sketch an input label, a result caption and a text alternative, then state how you would check that changing an input updates the displayed result.",
        "The reviewed repository contains only README.md, whose sole content is its title. It is a source stub, with no supplied application, source Lab, dependencies, deployment guide or documented hosted URL. This atlas exercise is an original prototype motivated by that title. Do not infer an existing Shiny implementation or deployed app. Any future Shiny continuation needs separately reviewed source and runtime instructions."),
    "Spatial-Analysis": (
        "Neighborhoods change a summary", "Spatial methods",
        "A 90-element browser spatial-analysis collection describes compact synthetic notebooks and avoids heavy native GIS dependencies.",
        "How does widening a neighborhood change an invented local peak?",
        "Calculate focal means along five equally spaced fictional cells. Compare radius-one and radius-two index neighborhoods. At the ends, average only existing cells and print the denominator for each window. These fixtures have no missing values. Calculations require complete finite numeric values and a nonnegative integer focal radius; define a missing-data rule before introducing missing data.",
        "values = [1, 1, 10, 1, 1]\ndef focal_mean(values, radius):\n    windows = [values[max(0, i-radius):min(len(values), i+radius+1)] for i in range(len(values))]\n    return [sum(window)/len(window) for window in windows], [len(window) for window in windows]\nnear, near_n = focal_mean(values, 1)\nwide, wide_n = focal_mean(values, 2)\nprint('Synthetic cells in line order:', values)\nprint('Radius 1 denominators:', near_n, '; radius 2 denominators:', wide_n)\nlines({'raw cells':values, 'radius 1 mean':near, 'radius 2 mean':wide}, 'Synthetic focal means on a line', 'ordered cell index', 'arbitrary value')",
        "The central value falls from 10 to 4 with radius one and to 2.8 with radius two. The radius-two means are [4, 3.25, 2.8, 3.25, 4]: the truncated endpoint windows have only three cells and produce the highest smoothed values, 4. Their overall mean is 3.46, whereas the raw mean is 2.8; truncated-window smoothing need not preserve the overall mean. Smoothing and its boundary rule change the pattern; they do not show that the original observation was an error or that an effect extends to nearby places.",
        "Change the peak to an end cell. Compare truncated windows with a rule requiring a full window, and explain which boundary policy belongs in the map caption. This scaffold reports full-window means only at valid cell indices:\n\n```python\nradius = 2\nvalid_indices = list(range(radius, len(values)-radius))\nfull_means = [sum(values[i-radius:i+radius+1])/(2*radius+1) for i in valid_indices]\nunavailable_indices = [i for i in range(len(values)) if i not in valid_indices]\nprint('Full-window indices and means:', list(zip(valid_indices, full_means)))\nprint('Unavailable indices (omitted):', unavailable_indices)\n```\n\nAt radius two only index 2 has a full window. Report unavailable endpoints as omitted, rather than zero-filling them or passing None to the line helper. Any separate plot must preserve the actual valid cell indices.",
        "The source describes 90 element notebooks plus an index, inspired by GISGeography's Periodic Table for Spatial Analysis. It documents numpy/pandas/matplotlib teaching examples and explicitly avoids compiled GIS stacks. No exact hosted launch URL is documented. This original line-grid activity imports no source notebooks, definitions, periodic-table artwork or datasets. See the separately attributed GISGeography source in the central references."),
    "Maps-and-Spatial-Analyses": (
        "A buffer is a declared rule", "Spatial methods",
        "A distinct map-centric 90-element source edition describes Leaflet/OSM maps with synthetic observations; its documented launcher returned 404.",
        "Which fictional points meet a distance rule, including its boundary?",
        "Measure straight-line distance from an invented origin in arbitrary planar units. Include points at exactly the radius. The local SVG draws a declared geometric rule, not travel access or a real geographic buffer. These fixtures have no missing values. Calculations require complete finite numeric coordinates and a nonnegative finite buffer radius; define a missing-data rule before introducing missing data.",
        '''from math import hypot
points = {'A':(1,1), 'B':(3,0), 'C':(3,2), 'D':(-2,-2)}
radius = 3
distances = {name:hypot(x,y) for name,(x,y) in points.items()}
inside = {name:distance <= radius for name,distance in distances.items()}
print('Synthetic planar coordinates:', points, '; radius:', radius)
print('Distance and inclusion:', {name:(round(distances[name],3), inside[name]) for name in points})
title = f'Synthetic distance buffer: radius {radius:g}'
included = ', '.join(str(name) for name in points if inside[name]) or '(none)'
excluded = ', '.join(str(name) for name in points if not inside[name]) or '(none)'
description = f'Current radius: {radius:g} arbitrary planar units. Inside: {included}. Outside: {excluded}. Exact distances and inclusion are printed above.'
scale = 30
body = f'<circle cx="210" cy="180" r="{radius*scale}" fill="#dcebe0" stroke="#16756b"/><path d="M65 180H355M210 45V315" stroke="#53676b"/>'
for name,(x,y) in points.items():
    px, py = 210+x*scale, 180-y*scale
    color = '#116c61' if inside[name] else '#a34712'
    body += f'<circle cx="{px}" cy="{py}" r="6" fill="{color}"/><text x="{px+10}" y="{py+5}" font-family="sans-serif" font-size="14">{escape(str(name))}: {"inside" if inside[name] else "outside"}</text>'
body += f'<text x="20" y="30" font-family="sans-serif" font-size="18">{escape(title)}</text><text x="20" y="345" font-family="sans-serif" font-size="13">Origin at crosshair; arbitrary planar units, no basemap</text>'
svg(body, title, description, width=620, height=370)''',
        "A, B and D meet the rule. B lies exactly on the radius and is included by <=. A straight-line planar buffer says nothing about roads, obstacles, service eligibility or actual travel times. The invented coordinates have no geographic CRS.",
        "Change the radius to 2.5, then replace <= with < at radius 3. Predict the changed membership and explain why the boundary rule must accompany an exported layer.",
        "This source edition describes recognizable latitude/longitude locations, synthetic values and browser-side Leaflet/OpenStreetMap tiles; those external map requests have separate network and attribution requirements. None is loaded here. Its exact README launcher returned HTTP 404 on 2026-11-01 and remains listed as unavailable. Public source is usable independently of a deployed Pages site; no working source app is claimed."),
    "Geospatial-Analyses-and-Maps-old": (
        "A teaching extract is not a census", "Spatial methods",
        "The old repository's distinct revised learning edition describes local teaching extracts and a Pyodide-safe spatial helper module.",
        "Can an uneven teaching extract change a summary of the same invented cells?",
        "Compare the complete eight-cell fictional fixture with an uneven four-cell extract. Print group coverage before comparing means. Here the full fixture is known only because we invented it; actual teaching extracts do not supply a population census. These fixtures have no missing values. Calculations require complete finite numeric values; define a missing-data rule before introducing missing data.",
        "cells = [('L1','low',1), ('L2','low',2), ('L3','low',2), ('L4','low',3), ('H1','high',7), ('H2','high',8), ('H3','high',6), ('H4','high',7)]\nselected_ids = {'L1', 'H1', 'H2', 'H3'}\nextract = [row for row in cells if row[0] in selected_ids]\ncoverage = {group:{'full':sum(row[1]==group for row in cells), 'extract':sum(row[1]==group for row in extract)} for group in ['low','high']}\nmeans = {'complete invented fixture':sum(row[2] for row in cells)/len(cells), 'uneven teaching extract':sum(row[2] for row in extract)/len(extract)}\nprint('All cells are invented:', cells)\nprint('Extract IDs:', sorted(selected_ids), '; group coverage:', coverage)\nbars(means, 'Synthetic extract selection changes the mean', 'arbitrary cell value')",
        "The full invented mean is 4.5; the extract mean is 5.5. Both group imbalance and within-group selection matter: three of four selected cells come from the high group, whose full mean is 7, but the selected low cell L1=1 is below its group's full mean of 2. Group imbalance alone, retaining those group means, would give 5.75; selecting L1 lowers that to 5.5. The selected high cells still average 7. A compact extract can teach a method without representing a population. Completeness, selection and original units must be checked before transferring a conclusion.",
        "Select two cells from each group and compare again. Record the selection rule, missing groups and original source terms alongside any future real teaching extract.",
        "Keep this -old repository separate from Geospatial-Analyses-and-Maps, its -revised variant, and Maps-and-Spatial-Analyses. Although its README calls itself a revised learning edition, the repository name remains -old. It describes Meuse, SIDS-style, taxi, housing, Iris, earthquake and other teaching extracts, but this atlas copies none of those datasets or helpers and makes no rights claim about them. No exact hosted launch URL is documented."),
    "global-informal-settlements-storymap": (
        "A settlement label needs evidence", "Browser GIS",
        "A JupyterGIS/JupyterLite atlas distinguishes informal-settlement evidence from a GHSL urban-centre tour.",
        "Does a built-up-area measurement establish settlement status?",
        "Compare three invented records with explicit source definitions. Count known classifications separately from unknowns; never infer informal status from density alone.",
        "records = [('T1',80,'urban centre'), ('T2',90,'unknown'), ('T3',50,'source-defined informal')]\nclasses = ['urban centre','unknown','source-defined informal']\ncounts = {c:sum(label==c for _,_,label in records) for c in classes}\nprint('Fictional built-up index and source labels:', records)\nbars(counts, 'Synthetic classification provenance', 'records')",
        "The densest invented record is still unknown. GHSL urban centres describe human settlements; they are not a global informal-settlement classification.",
        "Add source, definition, date and license fields, then write a rejection rule for a classification inferred only from urban morphology.",
        "Source's GHSL tour fetches live JRC data during its build and maps external polygons. Its optional AI panel needs separately configured credentials or a controlled gateway. No GHSL data, AI service or informal-settlement geometry is bundled here."),
    "Cross-Border-Ebola-Risk-Mapping-Prototype": (
        "Sensitivity before a risk label", "Global health",
        "A native preparedness-analysis scaffold includes two supplementary JupyterLite-compatible synthetic notebooks.",
        "Can a change in assumed weights reverse an index ranking?",
        "Compare two invented cells under alternate weights for an interface indicator and access indicator. These index values are hypothetical and do not predict Ebola risk.",
        "cells = {'X':(.9,.2), 'Y':(.3,.8)}\nscores = {str(w):{k:w*a+(1-w)*b for k,(a,b) in cells.items()} for w in [.2,.5,.8]}\nprint('Alternate weighting results:', scores)\nbars({w:result['X']-result['Y']+.5 for w,result in scores.items()}, 'Synthetic X minus Y score, shifted by +0.5', 'index difference plus 0.5')",
        "Weights can reverse the order. The chart shifts differences by +0.5 to retain a zero baseline; inspect the printed unshifted scores. Neither a ranking nor a suitability index is a disease diagnosis or a causal effect.",
        "Find the crossover weight and list which governance, calibration and uncertainty checks would be required before any real preparedness analysis.",
        "The full scaffold uses native GDAL/raster/vector/modeling tools. Only notebooks_lite/ are described as browser-compatible; no hosted launch is documented. Sensitive line lists, exact locations and unreviewed readiness gaps stay out of public teaching material."),
    "JupyterGIS-StoryMap-Gaborone-TB-ABM": (
        "Storytelling needs a residual check", "Global health",
        "Three illustrative JupyterGIS storymaps accompany Gaborone TB agent-based-modeling work through a JupyterLite xeus environment.",
        "Could a good-looking scenario map conceal calibration error?",
        "Compare invented reference values with a hypothetical model-like series and plot absolute residuals. These are authored numbers, not TB observations or an executed ABM.",
        "reference = [10,20,15,25]\nscenario = [11,19,24,23]\nresiduals = {f'cell {i+1}':abs(a-b) for i,(a,b) in enumerate(zip(reference,scenario))}\nprint('Reference and scenario are synthetic:', reference, scenario)\nbars(residuals, 'Authored scenario absolute residuals', 'arbitrary units')",
        "Cell 3 has the largest mismatch. A persuasive storymap does not establish calibration, validation or the effectiveness of an intervention.",
        "Separate calibration cells from held-out cells before adjusting the series. Describe how community review and uncertainty should appear in a storymap caption.",
        "Source layers are explicitly illustrative placeholders, not official ward boundaries, facility registries or surveillance. It supplies .jGIS/environment bundles but no verified hosted Lab. A native ABM or xeus/JupyterGIS environment is a separate continuation."),
    "Data-Visualization": (
        "See the same evidence two ways", "Foundations",
        "A broad visualization catalog with browser notebooks and separately attributed evidence examples.",
        "How can a chart change the apparent size of a difference?",
        "Compare differences and ratios for four invented districts. Keep a zero baseline for bars; a ratio of 2 means twice a reference value, not twice the clinical risk.",
        "values = dict(North=12, East=18, South=15, West=24)\nreference = 12\nratios = {k: v/reference for k, v in values.items()}\nprint('Values:', values, '\\nRatios to North:', ratios)\nbars(values, 'Synthetic counts — zero baseline', 'count')",
        "West has twice North's count. Without population denominators these are not comparable disease rates. Chart selection cannot repair a missing denominator.",
        "Add district populations and compare count ranks with per-capita ranks. Which caption prevents a misleading interpretation?",
        "The full source has separately attributed packaged NASA/NOAA and other examples; this atlas does not redistribute those extracts. Optional map/GPU rendering and native GeoAI continue in their documented environments."),
    "South-Sudan-Dashboard": (
        "Service continuity as a dependency", "Global health",
        "A browser conversion of a Shiny dashboard, with pre-rendered terrain and explicit sample-data fallbacks.",
        "Can staffing and road access create different service gaps?",
        "Calculate a toy service capacity from staffed slots times a road-access fraction. Keep each dependency visible.",
        "sites = [('A', 40, .8), ('B', 30, .4), ('C', 20, 1.0), ('D', 35, .6)]\ncapacity = {name: round(slots*access, 1) for name, slots, access in sites}\nprint('Invented site, staffed slots, access fraction:', sites)\nbars(capacity, 'Fictional service continuity', 'accessible slots')",
        "Site B loses more nominal capacity to the assumed access fraction. These fictional sites represent no South Sudan facilities, conflicts, or operational service estimates.",
        "Set access to 0.5 for all sites. Compare the effects of access and staffing before proposing a community-reviewed question.",
        "Source removes Shiny, rasterio and ACLED from the browser runtime; terrain is prepared ahead of time, ACLED is sample data, and HDX/IDMC requests may hit CORS. No source launcher appears in its README."),
    "Geospatial-Analyses-and-Maps": (
        "Overlay with an explicit layer contract", "Spatial methods",
        "A 90-element map-first collection with bundled CSV/GeoJSON and clearly described synthetic boundaries.",
        "Which invented facilities overlap an assumed hazard cell?",
        "Join facilities to a four-cell hazard lookup by a declared cell ID. An unmatched cell should be reported rather than assigned a zero.",
        "hazard = {'A': 2, 'B': 7, 'C': 4, 'D': 9}\nfacilities = [('F1','A'), ('F2','D'), ('F3','B'), ('F4','X')]\njoined = {name: hazard[cell] for name,cell in facilities if cell in hazard}\nmissing = [name for name,cell in facilities if cell not in hazard]\nprint('Unmatched facilities:', missing)\nassert missing == ['F4']\nbars(joined, 'Synthetic overlay lookup', 'hazard index')",
        "The missing facility is unknown, not safe. A layer contract must state geography, units, identifiers and missing-value policy before overlay.",
        "Add a second time slice and distinguish missing cells from changing hazard. Which fields belong in the export?",
        "The source describes synthetic shapefiles, administrative outlines and health facilities. None is imported here or labeled as an actual administrative boundary. README gives deployment guidance but no exact launch URL."),
    "Geospatial-Analyses-and-Maps-revised": (
        "Show what aggregation hides", "Spatial methods",
        "A revised 12-lesson map-first edition with actual Montreal boundaries, local layers, and browser H3/deck.gl examples.",
        "Can the same values look different after regrouping?",
        "Aggregate a 4×4 invented raster into four 2×2 blocks. This demonstrates scale sensitivity without representing a real administrative geography.",
        "cells = [1,1,8,8, 2,2,9,9, 8,8,1,1, 9,9,2,2]\nblocks = [sum(cells[(r+dr)*4+c+dc] for dr in [0,1] for dc in [0,1])/4 for r,c in [(0,0),(0,2),(2,0),(2,2)]]\nprint('Block means:', blocks, '; overall mean:', sum(cells)/len(cells))\ngrid(blocks, 2, 'Synthetic block means — aggregation changes detail')",
        "The average is preserved but local variation disappears. Geographic grouping affects a map even when the underlying observations are unchanged.",
        "Regroup as horizontal stripes. Compare the apparent pattern, and describe the modifiable areal unit problem in your own words.",
        "This is a distinct revised variant. Source emphasizes real boundaries and clear data terms; the atlas exercise uses a labeled abstract grid, not invented administrative polygons. No source launch URL is documented."),
    "Global-Health-GIS": (
        "Weight burden without hiding assumptions", "Global health",
        "Browser GIS demonstrations linking JupyterLite, JupyterGIS and GeoLibre with explicitly synthetic burden data.",
        "How does population weighting change a program summary?",
        "Compare an unweighted mean of invented district rates with a population-weighted mean. These are arithmetic teaching values, not IHME or GBD estimates.",
        "rates = [20, 80, 40]\npopulation = [1000, 100, 500]\nplain = sum(rates)/len(rates)\nweighted = sum(r*p for r,p in zip(rates,population))/sum(population)\nprint('Rates:', rates, 'populations:', population)\nbars({'unweighted': plain, 'population weighted': weighted}, 'Synthetic summary sensitivity', 'rate index')",
        "The small high-rate district drives the unweighted mean. A weighted summary answers a different question; neither resolves equity priorities by itself.",
        "Propose one population-based and one equity-based objective. Keep them separate in a decision record and ask who should choose the tradeoff.",
        "Source warns its sample burden is not IHME. Approved IHME/GHDx exports require their terms. Its README uses a lowercase Pages URL; retain that exact spelling even if unavailable."),
    "HIVDB-Drug-Resistance-Maps": (
        "Audit the surveillance denominator", "Global health",
        "HIV drug-resistance teaching that separates the public 2015 surveillance snapshot, current HIVDB, and sequence interpretation.",
        "Why should a multi-country study not be counted in every country?",
        "Combine two invented single-country study proportions by their sample sizes. Exclude a multi-country record that lacks country-specific denominators.",
        "studies = [('A',100,.10), ('A',20,.30), ('A+B',90,.20)]\nsingle = [r for r in studies if r[0]=='A']\nweighted = sum(n*p for _,n,p in single)/sum(n for _,n,p in single)\nnaive = sum(p for _,_,p in single)/len(single)\nprint('Included denominator:', sum(n for _,n,_ in single), '; multi-country excluded')\nbars({'unweighted percent': 100*naive, 'weighted percent': 100*weighted}, 'Invented surveillance summary', 'percent')",
        "The weighted result is about 13.3%, while the simple mean is 20%. These invented values describe no population. Sequence interpretation does not supply country prevalence.",
        "Add a record with known country-specific denominators. State exactly when it becomes eligible, and distinguish historical coverage from current estimates.",
        "The source's default is the Rhee et al. 2015 snapshot, not current HIVDB. Later patient-level templates are conditional. No individual records are bundled; do not infer clinical treatment choices from this exercise."),
    "Whitebox": (
        "Trace downhill, then change runtimes", "Terrain & Earth observation",
        "WhiteboxTools API discovery and workflow design with explicit native-executable boundaries.",
        "Which neighbor receives flow in a tiny terrain grid?",
        "For one cell, calculate elevation drop to four orthogonal neighbors. This transparent toy is not a WhiteboxTools implementation or full hydrology model.",
        "terrain = [[8,7,6], [7,6,3], [6,4,2]]\ncenter = terrain[1][1]\nneighbors = {'north':terrain[0][1], 'east':terrain[1][2], 'south':terrain[2][1], 'west':terrain[1][0]}\ndrops = {k:max(0,center-z) for k,z in neighbors.items()}\ndirection = max(drops,key=drops.get) if any(drop > 0 for drop in drops.values()) else None\nprint('Steepest orthogonal descent:', direction if direction is not None else 'none (sink or flat)')\nbars(drops, 'Synthetic local elevation drop', 'height units')",
        "East has the largest drop. A real flow algorithm also needs cell spacing, flats, sinks, diagonal geometry and boundary rules.",
        "Set the center below all neighbors. Explain why this creates a sink and what a terrain analyst must decide next.",
        "WhiteboxTools is a native subprocess executable and cannot run in ordinary Pyodide. Continue in local Jupyter/Colab/Binder following the source; start with a ≤100×100 public raster and one tool, not bulk processing."),
    "AI-Agents-and-Orchestrator-Six-Thinking-Hats": (
        "Route perspectives before synthesis", "AI & human decisions",
        "Six role-based teaching agents plus an orchestrator, inspired by Edward de Bono's Six Thinking Hats.",
        "Does a synthesis include each required perspective?",
        "Route authored statements into six categories and inspect coverage. The strings are fixtures; no AI model is called and the count is not a quality score.",
        "roles = ['facts','feelings','risks','benefits','alternatives','process']\nstatements = [('facts','Counts lack denominators'), ('risks','Disclosure may harm'), ('benefits','A shared map may help'), ('process','Invite community review'), ('facts','Dates differ')]\ncoverage = {role:sum(r==role for r,_ in statements) for role in roles}\nprint('Missing perspectives:', [r for r,n in coverage.items() if n==0])\nbars(coverage, 'Authored teaching perspectives — not model output', 'statements')",
        "Feelings and alternatives have no entries. Routing reveals an omission; it does not establish that the populated perspectives are true, fair or complete.",
        "Write a respectful feelings entry and a competing alternative. Ask a human reviewer whether either was reduced to a stereotype.",
        "Source uses deterministic TeachingBackend and an optional real-service adapter. Live models require an approved authenticated server proxy; never put long-lived keys in browser notebooks. Six Hats is de Bono's framework; the orchestrator is a project addition."),
    "DRC-Population-Mobility-Border-Mapping": (
        "Flows are connections, not infections", "Global health",
        "Population-mobility notebooks and storymaps for the DRC/Great Lakes region, with careful provenance and privacy requirements.",
        "How do weighted connections change a fictional node's prominence?",
        "Sum incoming and outgoing flow weights for four fictional nodes. No node corresponds to a city, border post or individual movement.",
        "edges = [('A','B',20), ('A','C',10), ('C','B',5), ('B','D',15)]\nstrength = {n:sum(w for a,b,w in edges if n in (a,b)) for n in 'ABCD'}\nprint('Invented flows:', edges)\nbars(strength, 'Fictional mobility-node strength', 'flow units')",
        "B has the greatest connected weight in this toy network. Mobility is not evidence of transmission, infection, nationality or risk in a real community.",
        "Remove the A–B edge and recompute. Discuss what a missing observation would mean compared with a closed route.",
        "Source requires dated metadata and cautions against personal movement and sensitive locations. Notebook.link projects need a published source snapshot; external maps have separate network/runtime limits."),
    "Geospatial-Research-Awareness-Radar": (
        "Rank leads without endorsing claims", "AI & human decisions",
        "A literature-radar workflow for geospatial/public-health research discovery, deduplication and review.",
        "Can duplicate records distort a morning research shortlist?",
        "Normalize invented DOI strings, deduplicate, and score topic relevance against browser feasibility. All titles and scores are authored teaching metadata.",
        "hits = [('doi:toy-1',3,2), ('DOI:TOY-1',3,2), ('doi:toy-2',5,0), ('doi:toy-3',2,3)]\nunique = {doi.lower(): (topic,feasible) for doi,topic,feasible in hits}\nscores = {doi:topic+feasible for doi,(topic,feasible) in unique.items()}\nprint('Raw hits:', len(hits), '; unique:', len(unique))\nbars(scores, 'Fictional discovery score', 'arbitrary score')",
        "Deduplication prevents repeated metadata from masquerading as independent evidence. Relevance and feasibility rankings are review aids, not measures of scientific validity.",
        "Weight feasibility by 0, 1 and 2. Identify which ranking is most sensitive and write down why a human should inspect it.",
        "Actual live scans use remote APIs and optional keys; this exercise does not scrape services. Source notes GPU/HPC feasibility penalties. Export only reviewed metadata and respect provider terms and request limits."),
    "World-Monitor-Prototype": (
        "Put freshness in the situation report", "Emergency operations",
        "A global-health field guide connecting monitoring, spatial epidemiology and dated EOC situation reports.",
        "Does a high-severity signal remain useful when it is stale?",
        "Use an explicit assumed decay rule to compare four fictional signals. This is an inspectable prioritization heuristic, not validated emergency triage.",
        "signals = [('S1',8,1), ('S2',9,12), ('S3',5,2), ('S4',7,24)]\npriority = {name:severity/(1+age/6) for name,severity,age in signals}\nprint('Fictional signal, severity, age in hours:', signals)\nbars(priority, 'Teaching freshness-weighted signal', 'heuristic score')",
        "The freshest signal ranks above a more severe but stale item. A decay constant encodes a judgment and could suppress a slowly developing emergency.",
        "Compare 3-hour and 24-hour decay constants. Add an unverified flag and decide how to represent it without turning unknown into zero.",
        "Source distinguishes optional live USGS/context from bundled samples. External interactive libraries need network; this atlas is not a live monitoring service. Save dated reports with source and uncertainty."),
    "Astra-demos": (
        "Procedural terrain, transparent assumptions", "Terrain & Earth observation",
        "Geospatial reasoning and procedural 3D teaching worlds inspired by a creator-reported Astra demonstration directory.",
        "How does frequency change a generated landscape?",
        "Build a tiny analytic height field from sinusoids, then calculate horizontal roughness. This is a procedural rule, not a learned world model.",
        "from math import sin, cos\nheights = [[2+sin(x*.9)+cos(y*.8) for x in range(5)] for y in range(5)]\nflat = [v for row in heights for v in row]\nroughness = sum(abs(heights[y][x+1]-heights[y][x]) for y in range(5) for x in range(4))/20\nprint('Mean horizontal height difference:', round(roughness,3))\ngrid(flat, 5, 'Procedural synthetic terrain — not geographic truth')",
        "The smooth hills arise because the formula is smooth. A plausible landscape is not evidence of a place's actual topography or a model's geographic ability.",
        "Double the x frequency. Quantify the roughness change and explain which aspects remain visually plausible but unvalidated.",
        "Source explicitly says these are original educational reinterpretations, not GPT benchmark outputs. Its 3D scenes need graphics support; static figures provide an alternative. No model runs in this chapter."),
    "Gods-Eye-View-Satellite": (
        "Inspect the viewing geometry", "Terrain & Earth observation",
        "An independent God's Eye View learning companion connecting satellites, EOC maps and optional model-assisted interpretation.",
        "How does off-nadir angle change an idealized ground footprint?",
        "For a flat-plane approximation, multiply altitude by tangent of angle. State the missing Earth curvature, optics, atmosphere and terrain assumptions.",
        "from math import tan, radians\naltitude = 500\noffsets = {str(a)+' deg': altitude*tan(radians(a)) for a in [0,10,20,30,40]}\nprint('Assumed altitude:', altitude, 'km; flat-plane calculation')\nbars(offsets, 'Idealized viewing offset', 'km')",
        "Offsets grow nonlinearly with angle. The chart is not a satellite position, coverage product, image resolution calculation or live observation.",
        "Compare altitudes 400 and 800 km. Identify which quantities scale linearly and what additional metadata would be needed for a real sensor.",
        "Source is independent of Bilawal Sidhu's upstream app. NASA Worldview is a separate service. External Leaflet/Cesium resources and optional Astra services have separate availability; browser exercises call neither."),
    "WorldView": (
        "Allocate supplies with visible constraints", "Emergency operations",
        "A World View companion combining synthetic emergency operations, notebook analysis and 2D/Cesium teaching views.",
        "What does an equal shipment rule leave unresolved?",
        "Allocate a small fictional stock equally, then compare each district's unmet demand. Demand is an assumed input, not a population health observation.",
        "demand = {'A':12, 'B':30, 'C':18}\nstock = 30\nallocation = {k:stock/len(demand) for k in demand}\nunmet = {k:max(0,demand[k]-allocation[k]) for k in demand}\nprint('Allocation:', allocation, '; unused:', sum(max(0,allocation[k]-demand[k]) for k in demand))\nbars(unmet, 'Synthetic unmet demand after equal allocation', 'supply units')",
        "Equal shipments leave unequal shortfalls. No allocation rule is automatically equitable; community priorities and practical constraints must be explicit.",
        "Allocate in proportion to demand and compare residual fractions. Add a road-capacity constraint and explain why a map alone cannot choose a policy.",
        "Source does not bundle the upstream React/Express app or credentialed services. Optional inference runs outside the browser. Synthetic facilities and flights are not emergency evidence."),
    "Custom-GPT-Six-Thinking-Hats": (
        "Validate a structured conversation", "AI & human decisions",
        "A copy-and-paste workflow from Six Hats conversations to editable JSON, SVG maps and human-reviewed synthesis.",
        "What can a schema check establish about a discussion?",
        "Validate that a small authored JSON object contains six nonempty perspectives. The extra purple synthesis step is project-specific, not one of de Bono's original six.",
        'import json\nrequired_hats = (\'white\', \'red\', \'black\', \'yellow\', \'green\', \'blue\')\n\ndef validate_perspectives(record):\n    missing, empty, invalid = [], [], {}\n    counts = {hat: 0 for hat in required_hats}\n    if not isinstance(record, dict):\n        return counts, {\'missing\': list(required_hats), \'empty\': [], \'invalid\': {\'record\': \'Expected a JSON object\'}}\n    for hat in required_hats:\n        if hat not in record:\n            missing.append(hat)\n            continue\n        items = record[hat]\n        if not isinstance(items, list):\n            invalid[hat] = \'Expected a list of nonempty text entries\'\n        elif not items:\n            empty.append(hat)\n        else:\n            bad = [i for i, text in enumerate(items) if not isinstance(text, str) or not text.strip()]\n            counts[hat] = len(items) - len(bad)\n            if bad:\n                invalid[hat] = \'Invalid entry indices: \' + str(bad)\n    return counts, {\'missing\': missing, \'empty\': empty, \'invalid\': invalid}\n\nrecord = json.loads(\'{"white": ["Check source dates"], "red": ["Concern about exclusion"], "black": ["Privacy risk"], "yellow": ["Shared learning"], "green": [], "blue": ["Invite review"]}\')\ncounts, issues = validate_perspectives(record)\nprint(\'Missing perspectives:\', issues[\'missing\'])\nprint(\'Empty perspectives:\', issues[\'empty\'])\nprint(\'Invalid perspectives:\', issues[\'invalid\'])\nprint(\'Extra metadata keys:\', sorted(set(record)-set(required_hats)) if isinstance(record, dict) else [])\nbars(counts, \'Authored JSON perspective coverage\', \'valid text entries\')',
        "The green alternatives field is empty. Valid JSON and complete fields still cannot establish factual accuracy, consent or good judgment.",
        "Add an alternative and an evidence URL field. Separate structural validity, source verification and stakeholder approval into three checks.",
        "Source uses deliberate paste and no live calls. Optional ChatGPT plugin access depends on workspace permissions. Do not assume another learner has access; manually authored JSON is supported."),
    "GeoLibre-GeoAI": (
        "Check a spatial holdout", "AI & human decisions",
        "GeoLibre, RustGIS and GeoAI learning with browser-safe analyses and clearly separated native/model continuations.",
        "Can a rule fit one region and fail in another?",
        "Apply an authored linear rule to two invented spatial groups. Compare mean absolute errors to reveal a deliberate distribution shift. This is a fixed rule, not fitted model output.",
        "groups = {'near':[(1,3),(2,5),(3,7)], 'far':[(4,15),(5,18),(6,21)]}\nerrors = {g:sum(abs((2*x+1)-y) for x,y in pairs)/len(pairs) for g,pairs in groups.items()}\nprint('Prediction rule: 2*x+1; all targets synthetic')\nbars(errors, 'Synthetic spatial holdout error', 'mean absolute error')",
        "The rule is exact in the near group and biased in the far group. Random splitting could conceal this structured difference; low training error does not ensure geographic transfer.",
        "Create a third group and choose a holdout before changing the rule. Discuss data leakage and why evaluation units should match the deployment question.",
        "Real GeoAI inference/native packages stay in supported local/server environments. Source's optional Ollama assistant needs separate installation and browser-origin permissions; use one tiny reviewed public fixture and a bounded request."),
    "GPT-6-Astra-Geospatial": (
        "Evaluate claims against a contract", "AI & human decisions",
        "Sixteen geospatial labs on spatial reasoning, digital twins, evaluation and browser Rust/WASM concepts.",
        "Does an explanation satisfy an explicit spatial evidence contract?",
        "Score three authored candidate records against required source, units, uncertainty and geographic-scope fields. This tests metadata coverage, not an AI capability.",
        "required = {'source','units','uncertainty','scope'}\nrecords = {'A':{'source','units'}, 'B':{'source','units','uncertainty','scope'}, 'C':{'source','scope'}}\nscores = {k:len(fields & required)/len(required)*100 for k,fields in records.items()}\nprint('Missing fields:', {k:sorted(required-fields) for k,fields in records.items()})\nbars(scores, 'Authored spatial-contract coverage', 'percent of fields')",
        "B meets the field contract, yet its source could still be wrong. An evaluation must distinguish well-formed answers from supported answers and geographic truth.",
        "Add a check for an observation date and a human-verifiable source. Define one failure that should block a decision even when every field is filled.",
        "This source connects authored fixtures and optional Astra evaluation; no live model or benchmark result is supplied by this atlas. Large geospatial preprocessing and native inference require a separate supported environment."),
    "zarr-sql-views": (
        "Query a cube, account for the work", "Terrain & Earth observation",
        "An Earth-observation teaching atlas connecting Zarr, SQL, maps, space–time cubes and separately attributed small real derivatives.",
        "How does a time filter change the number of chunks touched?",
        "Construct a tiny 3-time, 4-cell synthetic cube. Model two time steps per chunk and sum one slice; this models access costs without claiming to read actual Zarr files.",
        "cube = [[10*t+c for c in range(4)] for t in range(3)]\nqueries = {'time 0':[0], 'time 1':[1], 'time 0–2':[0,1,2]}\nchunks = {name:len({t//2 for t in times}) for name,times in queries.items()}\nprint('Slice sums:', [sum(row) for row in cube], '; two times per conceptual chunk')\nbars(chunks, 'Conceptual chunk reads for a synthetic cube', 'chunks')",
        "A narrower query can touch fewer chunks, but adjacent slices may share one. Actual storage costs depend on layout, encoding, network and cache.",
        "Compare chunk sizes 1 and 3 for these queries. Explain why no single chunk layout is best for every access pattern.",
        "Inspired upstream by dzole0311/zarr-sql-views (ISC). Source includes real GeoTessera/AR6 derivatives with specific limitations; none is copied here. Native bulk source preparation stays separate from browser learning."),
    "Rewiring-Global-Health": (
        "Rewiring Global Health in the Age of AI", "Global health",
        "A ten-lesson source course connecting evidence, GIS, AI, digital twins, privacy, equity and accountable human decisions.",
        "Whose priorities change the next experiment?",
        "Compare two explicit stakeholder weight sets for three fictional options. Weights encode preferences; the inputs are assumed scores, not health evidence or causal effects.",
        "options = {'access pilot':(8,5,4), 'privacy review':(3,9,7), 'community workshop':(5,7,9)}\nweights = {'access led':(.6,.2,.2), 'community led':(.2,.3,.5)}\nscore = {group:{name:sum(a*b for a,b in zip(criteria,w)) for name,criteria in options.items()} for group,w in weights.items()}\nprint('Criteria: access, privacy, community agency. All scores invented.')\nfor group,values in score.items():\n    print(group, values, 'first:', max(values,key=values.get))\nbars(score['community led'], 'Synthetic priorities under community-led weights', 'assumed score')",
        "The ranking changes with whose priorities count. A numeric score cannot replace consent, evidence appraisal or community authority. Use it to expose a disagreement, then document an experiment and its stopping rule.",
        "Invite two people to propose weights, name an excluded stakeholder, and write a one-page decision record: question, evidence gaps, possible harm, reversible experiment, review date and accountable decision-maker.",
        "Source's seeded grid is synthetic, STAC entries are metadata only, and its models are uncalibrated teaching examples. Real AES-GCM in its privacy lesson is not a managed key service. Live chat is optional and separately configured. This atlas calls no model."),
    "Sea-Level-Rise": (
        "Separate hazard from service impact", "Global health",
        "Coastal Futures connects an AIDS 2024 PEPFAR poster with a browser course, scenario dashboard and explicitly fictional teaching labs.",
        "Does a raised floor preserve a service when the access road floods?",
        "Compare assumed water levels with fictional road and floor thresholds. A service works only if both remain accessible under this deliberately simple rule.",
        "water = [0,.4,.8,1.2,1.6]\nroads = [.5,.9,1.3]\nfloors = [1.1,1.5,1.8]\nopen_sites = {str(w):sum(w<r and w<f for r,f in zip(roads,floors)) for w in water}\nprint('Fictional road thresholds:', roads, '; floor thresholds:', floors)\nbars(open_sites, 'Synthetic water threshold experiment', 'accessible sites')",
        "Road thresholds interrupt access before floors are reached. This bathtub-style comparison has no storm surge, hydraulic connectivity, exposure validation or actual facility portfolio.",
        "Raise floors by 0.5 and then roads by 0.5. Explain why the two interventions may produce different results. What must a real local assessment include?",
        "Cite Tobias et al.'s AIDS 2024 poster separately. Source's sensitive/provider-governed facility records and report binaries are not distributed here. Anonymized IDs do not make precise facility coordinates open data."),
    "STAC-Browser": (
        "Discover assets without reading pixels", "Terrain & Earth observation",
        "A map-centric STAC field guide for public catalogs, metadata footprints, asset attribution and notebook reproduction.",
        "Which catalog items meet a declared cloud-cover filter?",
        "Filter three fictional STAC-like metadata records. Missing cloud metadata stays unknown; metadata search is not an imagery download or a cloud-free guarantee.",
        "items = [{'id':'toy-a','cloud':8,'assets':2}, {'id':'toy-b','cloud':45,'assets':3}, {'id':'toy-c','cloud':None,'assets':1}]\nselected = [i for i in items if i['cloud'] is not None and i['cloud']<=20]\nunknown = [i['id'] for i in items if i['cloud'] is None]\nprint('Selected:', [i['id'] for i in selected], '; unknown cloud:', unknown)\nbars({i['id']:i['assets'] for i in items}, 'Fictional STAC asset inventory', 'asset links')",
        "Only toy-a passes the filter; toy-c is unknown. Item-level cloud cover may not describe the study area, and asset links can have different CORS, authentication or license conditions.",
        "Add an observation date, bbox and license field. Define a metadata audit before considering a bounded image download in the original explorer.",
        "Source reports separate discovery/download/CORS checks and a historical Digital Earth Africa outage. Availability changes. The default here is fictional metadata and never requests catalog endpoints or pixels."),
    "Climate-and-Health": (
        "Count heat exposure, preserve uncertainty", "Global health",
        "A preserved 2024 heat-stress course with newer browser companion labs, maps and adaptation teaching views.",
        "How sensitive is a heat indicator to the chosen threshold?",
        "Count days at or above four arbitrary temperatures for a short invented series. A temperature threshold alone is not a physiological heat-stress model.",
        "temperature = [27,29,31,34,33,30,28,32,35,31]\ncounts = {str(t)+' C':sum(v>=t for v in temperature) for t in [28,30,32,34]}\nprint('Invented daily temperatures:', temperature)\nbars(counts, 'Synthetic threshold exceedance', 'days')",
        "Changing the threshold changes the count. Humidity, duration, nighttime heat, exposure and vulnerability could all change the health interpretation; no causal health effect is estimated.",
        "Introduce a missing day and show both complete-case counts and a bound assuming that day did/did not exceed the threshold. What uncertainty belongs in the caption?",
        "Source preserves historical notebooks that are not all verified end-to-end in Pyodide; native dependencies, downloads and credentials may require a full environment. Its companion labs and historical course are distinct."),
    "RustGIS": (
        "Export a small layer with a contract", "Browser GIS",
        "Ten notebooks bridge browser GeoJSON/metadata exercises with RustGIS Web and separately documented native RustGIS.",
        "What must survive a GeoJSON handoff?",
        "Build four fictional WGS84 points and inspect their bounding box and property coverage. GeoJSON coordinates use longitude, latitude; values do not describe actual places.",
        'import json\nfrom pathlib import Path\nfrom base64 import b64encode\nfrom IPython.display import HTML\n\nfeatures = [{\'type\':\'Feature\',\'geometry\':{\'type\':\'Point\',\'coordinates\':[20+i*.1, -10+i*.05]},\'properties\':{\'id\':f\'T{i}\',\'value\':i+1,\'units\':\'arbitrary index\',\'origin\':\'synthetic\',\'observation_status\':\'invented\'}} for i in range(4)]\ncoordinates = [f[\'geometry\'][\'coordinates\'] for f in features]\nbbox = [min(p[0] for p in coordinates), min(p[1] for p in coordinates),\n        max(p[0] for p in coordinates), max(p[1] for p in coordinates)]\nrequired_properties = [\'id\', \'value\', \'units\', \'origin\', \'observation_status\']\ncoverage = {key: {\'present\':sum(key in f[\'properties\'] for f in features),\n                  \'missing_ids\':[f[\'properties\'].get(\'id\', \'(no id)\') for f in features if key not in f[\'properties\']]}\n            for key in required_properties}\nlayer = {\'type\':\'FeatureCollection\',\'bbox\':bbox,\'features\':features}\nassert all(f[\'properties\'][\'origin\']==\'synthetic\' for f in features)\nprint(\'WGS84 bounding box [west, south, east, north]:\', bbox)\nprint(\'Property coverage:\', coverage)\npayload = json.dumps(layer, indent=2).encode(\'utf-8\')\nexport_path = Path(\'atlas-synthetic-rustgis.geojson\')\nexport_path.write_bytes(payload)\nprint(\'Portable GeoJSON bytes:\', len(payload))\nprint(\'Lab export:\', export_path.name, \'- written in the kernel working folder; use the download below or locate this file in the Lab file browser.\')\nencoded = b64encode(payload).decode(\'ascii\')\ndisplay(HTML(f\'<a download="atlas-synthetic-rustgis.geojson" href="data:application/geo+json;base64,{encoded}">Download the complete synthetic GeoJSON</a>\'))\nbars({f[\'properties\'][\'id\']:f[\'properties\'][\'value\'] for f in features}, \'Synthetic layer attributes\', \'arbitrary index\')',
        "The layer preserves IDs, values and provenance, but a valid file does not guarantee an appropriate map projection, truthful location or safe disclosure.",
        "Inspect the bounding box and property-coverage report. Add a source_note field, then include it in required_properties to audit coverage. Import the downloaded synthetic layer into the source's RustGIS Web route, then verify fields after export.",
        "RustGIS Python is native CPython; no native Rust package runs here. Official Web has its own limits. Optional STAC requests and local Ollama have network/origin requirements; the default is credential-free."),
    "Osiris": (
        "Turn signals into a reviewed brief", "Emergency operations",
        "An independent OSIRIS virtual EOC field lab with fictional mission boards, operations views and evidence review.",
        "Which signals are ready for a briefing, and which need verification?",
        "Assign authored reports an evidence state and count them. Do not promote repeated unverified claims to confirmed events.",
        "reports = [('R1','unverified'), ('R2','corroborated'), ('R3','unverified'), ('R4','reviewed'), ('R5','corroborated')]\nstates = ['unverified','corroborated','reviewed']\ncounts = {state:sum(s==state for _,s in reports) for state in states}\nprint('Review queue:', [r for r,s in reports if s!='reviewed'])\nbars(counts, 'Fictional evidence workflow', 'reports')",
        "Only one report is marked reviewed, and even that label depends on a real process definition. A dashboard state is not proof of an event or permission to act.",
        "Add source independence and timestamps. Draft a brief with a visible unknowns section and an accountable review step before any proposed action.",
        "Source is an independent teaching companion, not production OSIRIS. Sectors and measurements are fictional; the upstream live console is a separate service with its own terms and availability."),
    "PyScript": (
        "One data contract, two browser runtimes", "Browser GIS",
        "JupyterLite and PyScript teaching routes share small synthetic GeoJSON, maps, 3D scenes and chart examples.",
        "Can two runtimes agree on a portable table calculation?",
        "Serialize an invented point table as JSON, deserialize, filter and compare a weighted mean. Plain JSON becomes a narrow exchange contract instead of runtime-specific state.",
        "import json\npoints = [{'id':'A','visits':10,'wait':4}, {'id':'B','visits':30,'wait':8}, {'id':'C','visits':20,'wait':6}]\nroundtrip = json.loads(json.dumps(points))\nassert roundtrip == points\nweighted = sum(p['visits']*p['wait'] for p in roundtrip)/sum(p['visits'] for p in roundtrip)\nprint('Synthetic visit-weighted wait:', round(weighted,2), '; minutes')\nbars({p['id']:p['wait'] for p in roundtrip}, 'Synthetic browser exchange fixture', 'minutes')",
        "JSON preserves these simple values and IDs across the round trip. Runtime agreement on a calculation does not establish that the fictional measurements are real or representative.",
        "Add a missing wait and an explicit null policy. Compare expected results before opening the original PyScript companion app.",
        "Source apps need browser runtime/CDN/tiles on first load. Native RustGIS and JupyterGIS Lite have separate capabilities; preview limitations include collaboration and STAC search. No backend is needed here."),
}

LESSONS["Global-Fishing-Watch-and-Dark-Vessels"] = OCEAN_LESSON

LESSONS["Coral-Reef-One-Health"] = CORAL_LESSON

HEALTH_LESSONS = [
    ("00", "Rewiring global health", "Stakeholder connections, policy weights, sensitivity and a decision record", "00_rewiring_global_health.ipynb"),
    ("01", "Climate, C3S, and STAC", "Catalog metadata, provenance and synthetic climate anomalies", "01_climate_stac_c3s.ipynb"),
    ("02", "Geospatial intelligence", "2D/3D geography and population-weighted access sensitivity", "02_geospatial_intelligence_2d_3d.ipynb"),
    ("03", "GeoLibre and 3D scenes", "GeoJSON handoff, layer contracts and extrusion", "03_geolibre_3d_scene.ipynb"),
    ("04", "Time and spatial patterns", "Animation, small multiples and lag experiments", "04_animated_health_climate_timeseries.ipynb"),
    ("05", "Zarr and SQL views", "Chunking, local queries and space–time cubes", "05_zarr_sql_views.ipynb"),
    ("06", "GeoAI and world models", "Spatial holdouts, residuals and distribution shift", "06_geoai_world_models.ipynb"),
    ("07", "AI chat and orchestration", "Six perspectives, a teaching chat and gateway privacy", "07_ai_orchestrator_privacy.ipynb"),
    ("08", "Digital twins and spatial agents", "Synchronous transitions, paired scenarios and uncertainty", "08_digital_twin_global_health.ipynb"),
    ("09", "Geoprivacy and map encryption", "Masking, suppression, authenticated encryption and release review", "09_geoprivacy_map_encryption.ipynb"),
]

PATHS = [
    ("Start with a browser", "Browser Python → Cholera Basic → Foundations → Browser GIS", ["Jupyterlite-1854-Cholera-Basic", "Data-Visualization", "Shiny-Live-Apps", "PyScript", "RustGIS"]),
    ("Read a map critically", "Neighborhoods → distance rules → overlay → aggregation → extract provenance", ["Spatial-Analysis", "Maps-and-Spatial-Analyses", "Geospatial-Analyses-and-Maps", "Geospatial-Analyses-and-Maps-revised", "Geospatial-Analyses-and-Maps-old"]),
    ("Observe a changing Earth", "Terrain → EO capabilities → metadata → ocean/reef evidence → data cubes", ["Astra-demos", "Gods-Eye-View-Satellite", "Whitebox", "EO-Satellite-Guide", "STAC-Browser", "Global-Fishing-Watch-and-Dark-Vessels", "Coral-Reef-One-Health", "zarr-sql-views"]),
    ("Rewire global health", "Evidence → ecosystems → access → privacy → community review", ["Jupyterlite-1854-Cholera-Basic", "Jupyterlite-1854-Cholera-Outbreak-London-Advanced-1", "1854-Cholera-Outbreak-London-Advanced-2", "2005-MDR-TB-Outbreak-Thailand", "Rewiring-Global-Health", "Coral-Reef-One-Health", "Global-Health-GIS", "HIVDB-Drug-Resistance-Maps", "Climate-and-Health", "Sea-Level-Rise", "South-Sudan-Dashboard", "DRC-Population-Mobility-Border-Mapping"]),
    ("Inspect AI and decisions", "Structured perspectives → evaluation → human agency", ["AI-Agents-and-Orchestrator-Six-Thinking-Hats", "Custom-GPT-Six-Thinking-Hats", "GeoLibre-GeoAI", "GPT-6-Astra-Geospatial", "Geospatial-Research-Awareness-Radar"]),
    ("Build a common picture", "Signals → constraints → reviewed briefing", ["World-Monitor-Prototype", "WorldView", "Osiris"]),
]
