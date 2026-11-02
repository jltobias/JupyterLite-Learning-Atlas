"""Original bounded PHI case companions and their inspected source register.

Only original fixtures and stdlib calculations execute in the atlas. Source
notebooks, historical records, maps and their dependencies are linked, not copied.
"""
from __future__ import annotations

OWNER = "PHI-Case-Studies"
DATE = "2026-11-02"
CASES = {
    "cholera-1854-basic": {
        "name": "Jupyterlite-1854-Cholera-Basic",
        "commit": "476f6dd5a8430e6eb823e79614fda1d7e12a78fb",
        "branch": "main",
        "title": "1854 Cholera Basic: dots, counts and centres",
        "files": [
            ("NB01-Cholera-Case-Study-Folium-Map-Part-1.ipynb", "Tables, deaths/pumps, Folium layers and the information value cycle"),
            ("NB02-Cholera-Case-Study-Folium-Map-Part-2.ipynb", "Death-weighted mean centre and careful map interpretation"),
        ],
        "rights": "Root LICENSE: GNU GPLv3.",
        "runtime": "The source supplies a published JupyterLite course. Its pandas/Folium maps and external tiles have separate runtime and attribution requirements; their execution is not certified by entry checks.",
        "question": "How can two centres summarize the same dots differently, and what do neither of them establish?",
        "summary": "An original browser-safe companion to PHI-Case-Studies: explore six invented locations, distinguish zero from missingness, and compare listed-location and death-weighted centres before making a historical claim.",
    },
    "cholera-1854-advanced-1": {
        "name": "Jupyterlite-1854-Cholera-Outbreak-London-Advanced-1",
        "commit": "8bde848d13d71602b2b32c62e5d4b4957e4a45a1",
        "branch": "main",
        "title": "1854 Cholera Advanced1: routes and reachable nodes",
        "files": [
            ("content/NB01-Cholera-Case-Study-OpenStreetMaps-Networkx.ipynb", "OSMnx street graph and Folium overlay"),
            ("content/NB02-Cholera-Case-Study-OpenStreetMaps-Networkx.ipynb", "Pairwise network distances, nearest-node connectors and a 400 m walkability assumption"),
            ("content/NB03-Cholera-Case-Study-Isochrone-Map.ipynb", "Projected walking times and convex-hull/buffer approximations"),
            ("content/NB04-Cholera-Case-Study-Isochrone-Map.ipynb", "Point-location counts within isochrones, distinct from death weights"),
            ("content/NB05-Cholera-Case-Study-Inspiration-and-To-Do-List.ipynb", "Further work, including synthetic time series"),
        ],
        "rights": "Root LICENSE: GNU GPLv3; content/LICENSE: Apache 2.0, with Apache wording in the content README. Both layers are recorded; no blanket resolution is asserted.",
        "runtime": "This later Jupyterlite source is primary. Its published deployment and root notebook paths were observed in the pinned deployment workflow and public manifest; its generic template README's demo is not the Cholera course. OSMnx/NetworkX/Folium workflows and external tiles need separate support checks.",
        "question": "How do a travel budget and one missing connection change reachability while an unreachable node remains unknown?",
        "summary": "An original PHI-Case-Studies companion using seven invented graph nodes and edge times to expose topology, inclusive travel budgets, unreachable locations and the limits of an isochrone.",
    },
    "cholera-1854-advanced-2": {
        "name": "1854-Cholera-Outbreak-London-Advanced-2",
        "commit": "d1b56c135b0fab2f470b837a51e6777dfc20b286",
        "branch": "master",
        "title": "1854 Cholera Advanced2: nearest sites, ties and buildings",
        "files": [
            ("NB01-Intro-Voronoi-Diagrams.ipynb", "Introduction to Voronoi diagrams"),
            ("NB02-Computing-Convex-Hulls.ipynb", "Convex hull construction"),
            ("NB03-Constructing-Voronoi-Polygons.ipynb", "Voronoi polygon construction"),
            ("NB04-Interactive-Voronoi-Map-Folium.ipynb", "Interactive Folium Voronoi map"),
            ("NB05-Buildings-in-Voronoi-Cells.ipynb", "Building-footprint centroids and point-in-polygon counts"),
            ("NB99-Computing-Convex-Hulls-Part-2.ipynb", "Supplement: alpha shapes and further hull exploration"),
        ],
        "rights": "Root LICENSE: Apache 2.0.",
        "runtime": "The source documents native/server Notebook, Docker and Binder. No public JupyterLite counterpart was found. Its SciPy/Shapely/GeoPandas/OSMnx/Folium polygon and overlay workflow is a separate continuation, not executed by this browser-safe companion. A Binder entry response is not a running session; no Binder build was started.",
        "question": "What changes when a nearest-site rule preserves boundary ties and an outside-domain building instead of forcing a winner?",
        "summary": "An original PHI-Case-Studies browser companion compares 35 sampled nearest-site assignments with six invented building centroids, preserving ties and an outside-domain record instead of claiming exact polygons or population coverage.",
    },
    "mdr-tb-thailand-2005": {
        "name": "2005-MDR-TB-Outbreak-Thailand",
        "commit": "6d50f558cd39b40089cd3eea1fbc19425e5191d1",
        "branch": "master",
        "title": "2005 MDR-TB Thailand: contact evidence and unknown results",
        "files": [
            ("NB01-MDR-TB-Case-Study-Case-Intro.ipynb", "Investigation, genotyping and the information workflow"),
            ("NB02-World-TB-Notebook-Part-1.ipynb", "Historical WHO/World Bank TB, GDP, education and health-spending preparation"),
            ("NB03-World-TB-Notebook-Part-2.ipynb", "Country/year data merging"),
            ("NB04-World-TB-Notebook-Part-3.ipynb", "Plotly exploration and ecological summaries"),
            ("NB05-MDR-TB-Case-Study-Part-1.ipynb", "Mapping and genotype/DST joins"),
            ("NB06-MDR-TB-Case-Study-Part-2.ipynb", "Reported contacts, duplicate edges and secondary interviews; work in progress"),
            ("NB07-MDR-TB-Case-Study-Part-3.ipynb", "Social networks with NetworkX/Bokeh"),
        ],
        "rights": "Root LICENSE: Apache 2.0.",
        "runtime": "The source documents Binder/native Notebook, not a deployed JupyterLite course; no public JupyterLite counterpart was found. Its pandas, Plotly, NetworkX and Bokeh pipeline is separate. A Binder entry response is not a running session; no Binder build was started.",
        "question": "Can a weaker reported contact merge components without changing a single observed drug-susceptibility result?",
        "summary": "An original PHI-Case-Studies browser companion uses six invented IDs to separate reported contacts, missing laboratory evidence and connected components, while preserving an isolate and avoiding transmission claims.",
    },
}

CHOLERA_CITATIONS = """- **Snow, John (1855).** *On the Mode of Communication of Cholera*, 2nd ed., London: John Churchill, pp. 38–55. [Primary transcription and map context, UCLA](https://epi-snow.ph.ucla.edu/Stream2_BSPoutbreak_a.html). Credit Charles Frederick Cheffins for historical maps drawn for Snow, and Ralph R. Frerichs and contributors for UCLA archive/curation. Historical maps are linked, never reproduced.
- **Brody, H.; Rip, M. R.; Vinten-Johansen, P.; Paneth, N.; Rachman, S. (2000).** *Map-making and myth-making in Broad Street: the London cholera epidemic, 1854.* Lancet **356**(9223), 64–68. [DOI](https://doi.org/10.1016/S0140-6736(00)02442-9), [author reprint](https://epi-snow.ph.ucla.edu/Stream2_BSPoutbreak_f.html). Snow's water hypothesis preceded the famous map; a map alone did not establish an intervention effect.
- **UCLA Department of Epidemiology, Ralph R. Frerichs and contributors.** [Historical investigation](https://epi-snow.ph.ucla.edu/Stream2_BSPoutbreak_d.html) and [Henry Whitehead context](https://epi-snow.ph.ucla.edu/Stream2_BSPoutbreak_e.html). Household inquiries, Whitehead and local officials contributed; attacks were already declining before the pump handle was removed on 8 September 1854.
- **CDC (2004).** *150th Anniversary of John Snow and the Pump Handle.* MMWR **53**(34), 783. [Historical overview](https://www.cdc.gov/mmwr/preview/mmwrhtml/mm5334a1.htm). A retrospective account is not a randomized counterfactual comparison.
- **World Health Organization (29 September 2026).** [*Cholera* fact sheet](https://www.who.int/news-room/fact-sheets/detail/cholera). Contaminated food/water, safe water, sanitation and community work provide context; this activity supplies no burden or treatment estimate.
"""

MDR_CITATIONS = """- **Oeltmann, J. E.; Varma, J. K.; Ortega, L.; Liu, Y.; O'Rourke, T.; Cano, M.; et al. (2008).** *Multidrug-Resistant Tuberculosis Outbreak among US-bound Hmong Refugees, Thailand, 2005.* Emerging Infectious Diseases **14**(11), 1715–1721. [DOI](https://doi.org/10.3201/eid1411.071629), [primary article](https://wwwnc.cdc.gov/eid/article/14/11/07-1629_article). Credit the research authors, CDC, Thailand Ministry of Public Health and International Organization for Migration. Published tables, patient locations, networks and effect estimates are not reproduced in the atlas.
- **World Health Organization (20 May 2024).** [*Tuberculosis: Multidrug-resistant (MDR-TB) or rifampicin-resistant TB (RR-TB)*](https://www.who.int/news-room/questions-and-answers/item/tuberculosis-multidrug-resistant-tuberculosis-%28mdr-tb%29). MDR includes resistance to rifampicin and isoniazid; this exercise computes no diagnosis or treatment decision. Historical policies/data are not current clinical or immigration guidance.
"""

METHOD_CITATIONS = """- **NetworkX contributors.** [Weighted shortest paths](https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html) and [connected components](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.components.connected_components.html), algorithm background only. No NetworkX code/examples are copied and no package installation is needed.
- **SciPy contributors.** [Voronoi method documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.Voronoi.html), source-method context only. The atlas samples a finite nearest-site grid rather than constructing exact Voronoi polygons; SciPy is not installed by these activities.
- **OpenStreetMap contributors.** [Copyright and ODbL attribution](https://www.openstreetmap.org/copyright). Source streets/buildings and Folium/CARTO tiles have separate data/provider terms. All atlas geometry is invented; no OSM graph, footprint, tile or historical basemap is bundled or downloaded. Retain required attribution in source continuations.
- **Upstream software communities:** pandas, NumPy, Folium, OSMnx, NetworkX, GeoPandas, Shapely, SciPy, Bokeh and Plotly support the linked source courses. The original atlas activities execute only Python's standard library and IPython display, under the atlas's existing runtime notices.
"""

RIGHTS = "All summaries, code, synthetic fixtures and SVGs here are newly authored: MIT executable code; CC BY 4.0 narrative, fixtures and figures, James L. Tobias and JupyterLite Learning Atlas contributors (2026). No source code/prose/data/imagery, patient records, pickles, saved graphs or map tiles are copied. Source rights remain with their creators; public access and shared contributors imply no blanket relicensing or endorsement."


def source_overview(slug, heading_level=2):
    case = CASES[slug]
    repo = f"https://github.com/{OWNER}/{case['name']}"
    prefix = f"{repo}/blob/{case['commit']}/"
    credits = ("PHI-Case-Studies and contributors; the Cholera notebooks list contact credits for Herman Tolentino, Jan MacGregor, James Tobias and Zhanar Haimovich. Contacts do not establish sole authorship."
               if slug.startswith("cholera") else
               "PHI-Case-Studies and contributors as teaching-course creators, with John Oeltmann credited in the source. Research authors are credited separately below.")
    lines = [f"{'#' * heading_level} {case['title']}: inspected source notebooks\n\n**Creators:** {credits}\n\n**Repository:** [{OWNER}/{case['name']}]({repo}). [Reviewed README]({prefix}README.md), full commit `{case['commit']}`, branch `{case['branch']}`, inspected {DATE}.\n\n{case['runtime']}\n\n**Source rights:** {case['rights']}",
             "| Inspected source file | What the source teaches |\n|---|---|"]
    for path, description in case['files']:
        lines.append(f"| [{path}]({prefix}{path}) | {description} |")
    lines.append(f"\n[Root license at the inspected commit]({prefix}LICENSE).")
    if slug in ['cholera-1854-basic', 'cholera-1854-advanced-1']:
        manifest = f"https://phi-case-studies.github.io/{case['name']}/api/contents/all.json"
        lines.append(f"\nThe [published contents manifest]({manifest}) was inspected {DATE}. The [existing source audit](https://jltobias.github.io/JupyterLite-Learning-Atlas/catalog/launch-checks.json) records its dated URL, source commit, confirmed course notebook basenames and canonical-JSON SHA-256 under `manifest_evidence`, separate from launch rows. This confirms filenames, not source execution or provider behavior. " +
                     ("The reviewed Basic README supplies the course root; the manifest separately confirms its two root notebook filenames." if slug == 'cholera-1854-basic' else "The source deployment is also evidenced by its pinned workflow below."))
    if slug == "cholera-1854-advanced-1":
        lines.append(f"[Content license]({prefix}content/LICENSE) and [content README]({prefix}content/README.md) retain the separate Apache wording.")
        lines.append("\nThe [pinned deployment workflow]("+prefix+".github/workflows/deploy.yml) and [published manifest](https://phi-case-studies.github.io/Jupyterlite-1854-Cholera-Outbreak-London-Advanced-1/api/contents/all.json) establish the separately observed course route. The earlier [native original README](https://github.com/PHI-Case-Studies/1854-Cholera-Outbreak-London-Advanced-1/blob/97a1d13dfb23032387ed23804e3d6f4dbc99aec7/README.md), master commit `97a1d13dfb23032387ed23804e3d6f4dbc99aec7`, describes Notebook/Docker/Binder. It remains background continuation, not a duplicate atlas chapter.")
    if slug == 'mdr-tb-thailand-2005':
        lines.append("\n**Historical provider pipeline:** WHO and the World Bank are credited as providers in the pinned NB02–NB04 preparation/merge/exploration sequence. The inspected source snapshot is dated 2025-07-23; its preserved country/year TB, GDP, education and health-spending inputs are historical course material. No current provider feed is queried, no source table is imported, and country-level associations cannot identify individual risk. Provider attribution here is through those inspected source notebooks, rather than a claim to have refreshed their underlying datasets.")
    return "\n\n".join(lines[:1]) + "\n\n" + "\n".join(lines[1:])


def bibliography():
    return "## PHI outbreak cases: creators, sources and rights (2026-11-02)\n\n" + "\n\n".join(source_overview(slug, heading_level=3) for slug in CASES) + "\n\n### Historical and methodological works used\n\n" + CHOLERA_CITATIONS + "\n" + MDR_CITATIONS + "\n" + METHOD_CITATIONS + "\n" + RIGHTS


BASIC_CODE = '''from math import sqrt

# Six invented locations; arbitrary planar units, fictional death counts.
rows = [('A1', 1, 1, 6), ('A2', 1, 3, 4), ('A3', 3, 2, 2),
        ('B1', 7, 1, 1), ('B2', 7, 3, 1), ('B3', 9, 2, 0)]
pumps = {'P': (2, 0.4), 'Q': (8, 0.4)}  # illustrative only; no use observations

def centres(records):
    total = sum(row[3] for row in records)
    unweighted = tuple(sum(row[i] for row in records) / len(records) for i in (1, 2))
    weighted = (tuple(sum(row[i] * row[3] for row in records) / total for i in (1, 2))
                if total else None)
    return total, unweighted, weighted

total, unweighted, weighted = centres(rows)
positive = sum(row[3] > 0 for row in rows)
def point_label(value):
    return 'unknown' if value is None else f'({value[0]:.6f}, {value[1]:.6f})'
print('Invented rows (id, x, y, fictional deaths):', rows)
print(f'Listed locations: {len(rows)}; positive-death locations: {positive}/{len(rows)}; fictional deaths: {total}')
print('Unweighted listed-location centre, planar units:', point_label(unweighted))
print('Death-weighted centre, planar units:', point_label(weighted))
print('No at-risk population denominator: counts and centres are not attack rates, pump use or causal evidence.')

def project(x, y):
    return 55 + x * 60, 270 - y * 52
body = '<text x="22" y="30" font-size="18">Invented dots and two different centres</text>'
body += '<path d="M55 65V270H665" fill="none" stroke="#52676b"/>'
for identifier, x, y, count in rows:
    px, py = project(x, y)
    radius = sqrt(count) * 6 if count else 5
    fill = '#16756b' if count else '#ffffff'
    body += f'<circle cx="{px}" cy="{py}" r="{radius:.3f}" fill="{fill}" stroke="#123c45" stroke-width="2"/>'
    body += f'<text x="{px-22}" y="{py-26}" font-size="13">{escape(identifier)}: {count}</text>'
for identifier, (x, y) in pumps.items():
    px, py = project(x, y)
    body += f'<rect x="{px-5}" y="{py-5}" width="10" height="10" fill="#41449c"/><text x="{px+9}" y="{py+4}" font-size="12">pump {escape(identifier)}</text>'
ux, uy = project(*unweighted)
body += f'<path d="M{ux-9} {uy}H{ux+9}M{ux} {uy-9}V{uy+9}" stroke="#a34712" stroke-width="3"/>'
if weighted is not None:
    wx, wy = project(*weighted)
    body += f'<path d="M{wx} {wy-10}L{wx+10} {wy}L{wx} {wy+10}L{wx-10} {wy}Z" fill="#f3bd5c" stroke="#123c45"/>'
body += f'<text x="22" y="310" font-size="13">+ listed centre {escape(point_label(unweighted))}; diamond weighted {escape(point_label(weighted))}</text>'
body += f'<text x="22" y="336" font-size="12">{total} fictional deaths; {positive}/{len(rows)} positive locations; x/y arbitrary planar units</text>'
body += '<text x="22" y="360" font-size="12">Filled symbol area proportional to count; hollow circle = observed zero. No Soho basemap.</text>'
description = f'{len(rows)} invented locations, {positive} positive, {total} fictional deaths. Listed centre {point_label(unweighted)}; weighted centre {point_label(weighted)}. ' + '; '.join(f'{name}: {count}' for name, x, y, count in rows)
svg(body, 'Synthetic Cholera Basic: dots and centres', description, height=385)
'''

ACCESS_CODE = '''from heapq import heappop, heappush
from math import isfinite

# Undirected invented graph. Coordinates draw a schematic; edge times are assumed minutes.
nodes = {'S': (0, 0), 'A': (1, 0), 'B': (0, 1), 'C': (2, 0),
         'D': (1, 1), 'E': (2, 1), 'U': (3, 1)}
edges = [('S', 'A', 2), ('S', 'B', 1), ('B', 'D', 1),
         ('D', 'E', 1), ('A', 'C', 2), ('C', 'E', 4)]
budget = 3

def shortest_costs(node_names, links, origin):
    adjacency = {name: [] for name in node_names}
    for left, right, minutes in links:
        if not isfinite(minutes) or minutes <= 0:
            raise ValueError('Edge times must be positive finite minutes')
        adjacency[left].append((right, minutes))
        adjacency[right].append((left, minutes))
    costs = {name: None for name in node_names}
    costs[origin] = 0
    queue = [(0, origin)]
    while queue:
        cost, name = heappop(queue)
        if cost != costs[name]:
            continue
        for other, minutes in adjacency[name]:
            candidate = cost + minutes
            if costs[other] is None or candidate < costs[other]:
                costs[other] = candidate
                heappush(queue, (candidate, other))
    return costs

costs = shortest_costs(nodes, edges, 'S')
reached = [name for name, cost in costs.items() if cost is not None and cost <= budget]
boundary = [name for name, cost in costs.items() if cost == budget]
unknown = [name for name, cost in costs.items() if cost is None]
print('Assumed undirected edge minutes:', edges)
print('Shortest minutes from S:', {name: ('unknown (unreachable)' if value is None else value) for name, value in costs.items()})
print(f'Inclusive budget <= {budget} minutes: {len(reached)}/{len(nodes)} graph nodes; reached:', reached)
print('At budget boundary:', boundary, '; unreachable remains unknown:', unknown)
print('Graph-node denominator includes S and U. This is not an accessible-area polygon or observed pump use.')

def project(point):
    x, y = point
    return 75 + x * 180, 245 - y * 135
body = f'<text x="22" y="30" font-size="18">Invented access: &lt;= {budget} assumed minutes from S</text>'
for left, right, minutes in edges:
    x1, y1 = project(nodes[left]); x2, y2 = project(nodes[right])
    body += f'<path d="M{x1} {y1}L{x2} {y2}" stroke="#52676b" stroke-width="3"/>'
    body += f'<text x="{(x1+x2)/2+8}" y="{(y1+y2)/2-9}" font-size="13">{minutes} min</text>'
for name, coordinate in nodes.items():
    x, y = project(coordinate)
    fill = '#16756b' if name in reached else '#ffffff'
    stroke = '#a34712' if name in boundary else '#123c45'
    dash = ' stroke-dasharray="3 3"' if costs[name] is None else ''
    body += f'<circle cx="{x}" cy="{y}" r="20" fill="{fill}" stroke="{stroke}" stroke-width="3"{dash}/>'
    body += f'<text x="{x}" y="{y+5}" text-anchor="middle" font-size="14" fill="{("white" if name in reached else "#123c45")}">{escape(name)}</text>'
    label = 'unknown' if costs[name] is None else f'{costs[name]} min'
    body += f'<text x="{x}" y="{y+41}" text-anchor="middle" font-size="13">{label}</text>'
body += f'<text x="22" y="315" font-size="13">{len(reached)}/{len(nodes)} nodes reached; orange border = exact budget; dashed = unreachable</text>'
body += '<text x="22" y="341" font-size="12">Coordinates are schematic. Edge weights/minutes are assumptions, independent of drawn lengths.</text>'
description = f'Inclusive {budget}-minute budget reaches {len(reached)} of {len(nodes)} graph nodes. Boundary: {boundary}. ' + '; '.join(f'{name}: {"unknown" if value is None else str(value)+" minutes"}' for name, value in costs.items())
svg(body, 'Synthetic Cholera Advanced1: network access', description, height=365)
'''

CELLS_CODE = '''# A finite sampled nearest-site exercise, not an exact Voronoi polygon construction.
pumps = {'A': (1, 1), 'B': (5, 1)}
domain = (0, 6, 0, 4)  # inclusive x minimum/maximum, y minimum/maximum; planar units
samples = [(x, y) for y in range(5) for x in range(7)]
buildings = {'a': (1, 2), 'b': (2, 4), 'c': (4, 1),
             'd': (5, 3), 't': (3, 2), 'o': (8, 2)}

def nearest_site(point, sites, bounds):
    x, y = point
    xmin, xmax, ymin, ymax = bounds
    if not (xmin <= x <= xmax and ymin <= y <= ymax):
        return 'outside'
    distances = {name: (x-px)**2 + (y-py)**2 for name, (px, py) in sites.items()}
    minimum = min(distances.values())
    winners = [name for name, distance in distances.items() if distance == minimum]
    return winners[0] if len(winners) == 1 else 'tie'

grid_membership = {point: nearest_site(point, pumps, domain) for point in samples}
building_membership = {name: nearest_site(point, pumps, domain) for name, point in buildings.items()}
grid_counts = {label: sum(value == label for value in grid_membership.values()) for label in ['A', 'B', 'tie', 'outside']}
building_counts = {label: sum(value == label for value in building_membership.values()) for label in ['A', 'B', 'tie', 'outside']}
print('Invented pump seeds, planar units:', pumps, '; inclusive domain:', domain)
print(f'Grid samples / {len(samples)}:', grid_counts)
print(f'Building centroids / {len(buildings)}:', building_counts)
print('Each building:', building_membership)
print("Exact squared-distance ties use this fixture's finite integer coordinates; fractional/finer-grid extensions need an explicit numerical policy.")
print('Samples are not area; buildings are not people or a population denominator.')

colors = {'A': '#b8d8cd', 'B': '#c7c9eb', 'tie': '#f3bd5c', 'outside': '#ffffff'}
def project(point):
    x, y = point
    return 65 + x * 64, 325 - y * 54
body = '<text x="22" y="28" font-size="18">Invented nearest-site samples and building centroids</text>'
for point, membership in grid_membership.items():
    x, y = project(point)
    body += f'<rect x="{x-20}" y="{y-20}" width="40" height="40" fill="{colors[membership]}" stroke="#52676b"/>'
    body += f'<text x="{x}" y="{y+5}" text-anchor="middle" font-size="12">{escape(membership)}</text>'
xmin, xmax, ymin, ymax = domain
left, top = project((xmin, ymax))
right, bottom = project((xmax, ymin))
body += f'<rect id="domain-frame" x="{left}" y="{top}" width="{right-left}" height="{bottom-top}" fill="none" stroke="#123c45" stroke-dasharray="6 4"/>'
for name, point in buildings.items():
    x, y = project(point)
    membership = building_membership[name]
    body += f'<circle cx="{x}" cy="{y}" r="9" fill="{colors[membership]}" stroke="#123c45" stroke-width="3"/>'
    body += f'<text x="{x+12}" y="{y-12}" font-size="13">{escape(name)}: {escape(membership)}</text>'
for name, point in pumps.items():
    x, y = project(point)
    body += f'<path d="M{x} {y-14}L{x+14} {y}L{x} {y+14}L{x-14} {y}Z" fill="#123c45"/><text x="{x}" y="{y+5}" text-anchor="middle" fill="white" font-size="12">{escape(name)}</text>'
body += f'<text x="22" y="385" font-size="13">Grid / {len(samples)}: A {grid_counts["A"]}, B {grid_counts["B"]}, tie {grid_counts["tie"]}, outside {grid_counts["outside"]}</text>'
body += f'<text x="22" y="411" font-size="13">Buildings / {len(buildings)}: A {building_counts["A"]}, B {building_counts["B"]}, tie {building_counts["tie"]}, outside {building_counts["outside"]}</text>'
body += '<text x="22" y="438" font-size="12">Squares = samples; circles = centroids; diamonds = seeds; gold = tie; hollow = outside.</text>'
sample_x = [point[0] for point in samples]
sample_y = [point[1] for point in samples]
body += f'<text x="22" y="462" font-size="12">Samples x {min(sample_x):g}..{max(sample_x):g}, y {min(sample_y):g}..{max(sample_y):g}; domain x {xmin:g}..{xmax:g}, y {ymin:g}..{ymax:g} (inclusive planar units).</text>'
description = f'{len(samples)} invented grid samples: {grid_counts}. {len(buildings)} invented building centroids: {building_counts}. Inclusive domain: {domain}. Seeds: {pumps}. ' + '; '.join(f'{name}: {label}' for name, label in building_membership.items())
svg(body, 'Synthetic Cholera Advanced2: sampled nearest sites', description, height=485)
'''

MDR_CODE = '''# Invented IDs and observed teaching labels, not historical patient records.
dst = {'A': 'MDR', 'B': 'MDR', 'C': None, 'D': 'non-MDR', 'E': None, 'F': 'MDR'}
contacts = [('A', 'B', 'strong'), ('B', 'C', 'strong'),
            ('C', 'D', 'weak'), ('D', 'E', 'strong')]
include_weak = False

def contact_components(ids, links, use_weak):
    adjacency = {name: set() for name in ids}  # preserves isolated IDs
    for left, right, evidence in links:
        if evidence not in ('strong', 'weak'):
            raise ValueError('Contact evidence must be strong or weak')
        if evidence == 'strong' or (evidence == 'weak' and use_weak):
            adjacency[left].add(right)
            adjacency[right].add(left)
    remaining = set(ids)
    components = []
    while remaining:
        todo = [min(remaining)]; group = set()
        while todo:
            name = todo.pop()
            if name in group:
                continue
            group.add(name)
            todo.extend(adjacency[name] - group)
        remaining -= group
        components.append(sorted(group))
    return sorted(components, key=lambda group: (-len(group), group))

def dst_summary(labels):
    if any(value not in ('MDR', 'non-MDR', None) for value in labels.values()):
        raise ValueError('DST labels must be MDR, non-MDR or None')
    known = sum(value in ('MDR', 'non-MDR') for value in labels.values())
    mdr = sum(value == 'MDR' for value in labels.values())
    return {'mdr': mdr, 'known': known, 'unknown': len(labels)-known,
            'fraction': mdr/known if known else None}

components = contact_components(dst, contacts, include_weak)
sizes = [len(group) for group in components]
summary = dst_summary(dst)
fraction_label = 'unknown' if summary['fraction'] is None else f'{summary["fraction"]:.1%}'
policy = 'strong + weak' if include_weak else 'strong only'
print('Invented observed DST labels:', {name: ('unknown' if value is None else value) for name, value in dst.items()})
print('Selected contact policy:', policy, '; components:', components, '; sizes:', sizes)
print(f'MDR / known DST: {summary["mdr"]}/{summary["known"]} ({fraction_label}); unknown DST / all IDs: {summary["unknown"]}/{len(dst)}')
print('Fixture summaries are not prevalence. Contact policy never changes observed DST; no directed transmission or clinical inference.')

coordinates = {'A': (85, 140), 'B': (225, 110), 'C': (365, 140),
               'D': (495, 210), 'E': (625, 150), 'F': (110, 270)}
body = f'<text x="22" y="28" font-size="18">Invented contact evidence: {escape(policy)}</text>'
for left, right, evidence in contacts:
    x1, y1 = coordinates[left]; x2, y2 = coordinates[right]
    selected = evidence == 'strong' or (evidence == 'weak' and include_weak)
    color = '#123c45' if selected else '#949494'
    dash = ' stroke-dasharray="7 5"' if evidence == 'weak' else ''
    body += f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{color}" stroke-width="3"{dash}/>'
    label = evidence + (' selected' if selected else ' excluded')
    body += f'<text x="{(x1+x2)/2-28}" y="{(y1+y2)/2-15}" font-size="11">{escape(label)}</text>'
for name, value in dst.items():
    x, y = coordinates[name]
    fill = '#f3bd5c' if value == 'MDR' else '#b8d8cd' if value == 'non-MDR' else '#ffffff'
    label = 'unknown' if value is None else value
    body += f'<circle cx="{x}" cy="{y}" r="24" fill="{fill}" stroke="#123c45" stroke-width="2"/>'
    body += f'<text x="{x}" y="{y+5}" text-anchor="middle" font-size="14">{escape(name)}</text><text x="{x}" y="{y+44}" text-anchor="middle" font-size="13">{escape(label)}</text>'
body += f'<text x="22" y="345" font-size="13">Component sizes: {escape(str(sizes))}; F remains isolated. Links are undirected reported contacts.</text>'
body += f'<text x="22" y="372" font-size="13">MDR / known DST {summary["mdr"]}/{summary["known"]} ({fraction_label}); unknown / all IDs {summary["unknown"]}/{len(dst)}</text>'
body += '<text x="22" y="399" font-size="12">Gold = MDR; green = non-MDR; hollow = unknown. Dashed = weak evidence, selected by policy.</text>'
description = f'Six invented IDs. Contact policy {policy}; component sizes {sizes}. MDR {summary["mdr"]} of {summary["known"]} known DST ({fraction_label}); unknown {summary["unknown"]} of {len(dst)} IDs. ' + '; '.join(f'{name}: {"unknown" if value is None else value}' for name, value in dst.items())
svg(body, 'Synthetic MDR-TB: contacts and observed DST', description, height=425)
'''

ACTIVITIES = {
    "cholera-1854-basic": (
        BASIC_CODE,
        "Before trusting a map, decide what each mark counts. The six invented rows contain IDs, x/y coordinates in arbitrary planar units and fictional death counts. Five locations have positive counts; B3 has an observed zero, not a missing record. A listed-location centre gives every row equal weight. A death-weighted centre gives each fictional death equal weight. Predict which centre will lie nearer the A locations. No source records or actual Soho coordinates are used.",
        "The default has 6 listed locations, 5 positive-death locations and 14 fictional deaths. The listed-location centre is (28/6, 12/6) = (4.666667, 2). The weighted centre is (30/14, 26/14) = (2.142857, 1.857143). The SVG gives positive circles area proportional to count and retains the hollow observed-zero circle. The plus and diamond answer different summary questions. Neither centre identifies who used a pump, an exposure, an infection source or a causal effect. Without an at-risk population denominator these are counts, not attack rates.",
        "Change only `('B3', 9, 2, 0)` to `('B3', 9, 2, 14)`. Predict, then rerun: 28 fictional deaths and weighted centre (156/28, 54/28), while the listed-location centre stays fixed. Read the text and look for the shifted diamond. Next set every count to zero: the weighted centre must say **unknown**, and every location must remain visible. Restore defaults before comparing with a partner. Explain why adding a population field would require a new rate calculation rather than renaming a count.",
        "Snow's 1854 investigation is compelling because maps were part of a wider inquiry into water and households. His water hypothesis preceded the famous map, and Whitehead, households and local officials contributed evidence. Attacks were already declining when the handle was removed on 8 September; a vivid before/after story does not identify a counterfactual effect. Read the linked primary account and historical reassessment below, and distinguish historical evidence from our six-row experiment. The source's first lesson develops tables/layers and an information value cycle; its second examines a weighted centre. This companion makes those two questions small enough to inspect in one browser session.",
    ),
    "cholera-1854-advanced-1": (
        ACCESS_CODE,
        "Start with [Basic](../cholera-1854-basic/index.ipynb), then ask why drawn distance and travel cost can disagree. Every edge here must have a positive finite time in assumed minutes and can be traversed both ways. Coordinates affect only the drawing. S is the origin; U has no connection. Predict whether E is included by an inclusive three-minute budget, and whether an unconnected U should be zero, large or unknown. The shortest-path calculation repeatedly extends the cheapest discovered route and keeps unknown until a route exists.",
        "From S the default costs are S=0, A=2, B=1, D=2, E=3, C=4 minutes; U is unreachable/unknown. The inclusive budget reaches **5/7 graph nodes**, counting the origin S and including E exactly at the boundary. The orange ring marks that equality; a dashed outline marks unknown. These seven nodes are the denominator, not seven households or a population sample. A node set is not an exact accessible-area polygon, and shortest routes under assumed weights are not observed walking behavior or pump use.",
        "Change `budget = 3` to `budget = 2`: the reached count becomes **4/7**. Restore 3, then remove only `('B', 'D', 1)` from `edges` (repair the list comma if needed). E now costs 8 and D 9 minutes through A–C–E; only S, A and B meet the budget, **3/7**. U must remain unknown in text and SVG. Restore the edge and record which conclusion changed because of a budget assumption and which changed because of topology. Do not silently treat unreachable as a zero-minute trip.",
        "The five source lessons progress from OSMnx/Folium graph construction to network distances and connectors, projected travel-time isochrones, counting locations, and further questions. A 400 m source assumption is a teaching choice, not a universal walkability standard. Convex hulls/buffers approximate a reachable shape and may include places with no supported route; point counts also differ from death-weighted counts in Basic. Real access involves crossings, speed, mobility, time, exclusion and actual routes. The later Jupyterlite source is the primary course here; the earlier native repository is linked as background only. Keep Snow's household/water-use inquiry in view: a route drawing does not establish use or cause.",
    ),
    "cholera-1854-advanced-2": (
        CELLS_CODE,
        "Continue from [Advanced1](../cholera-1854-advanced-1/index.ipynb), but change the question from network cost to nearest straight-line seed. For each integer grid centre x=0..6, y=0..4, compare squared Euclidean distances to A=(1,1) and B=(5,1). Squared distance preserves the comparison without a square root. Keep equal distances as **tie**. Exact comparison here uses finite integer coordinates. Fractional coordinates or a finer-grid extension need an explicit numerical policy for equality; this fixture chooses none for those extensions. For six invented building centroids, first check the inclusive declared domain [0,6] × [0,4]; o=(8,2) stays **outside**. Predict the vertical tie column and the effect of moving B left one unit.",
        "The default 35 grid samples split **A 15 / B 15 / tie 5 / outside 0**. The six building centroids split **A 2 / B 2 / tie 1 / outside 1**. These are two separate denominators and kinds of objects. The gold tie column is part of the result; assigning it arbitrarily would change counts. The outside centroid remains in the six-record accounting. The graphic samples a finite rule: colored squares are sample symbols, not computed Voronoi polygon boundaries or exact area fractions. Building centroids are points, not footprints; one building is not one person.",
        "Change only `'B': (5, 1)` to `'B': (4, 1)`. Predict, rerun and compare text/SVG: grid A/B/tie/outside **15 / 20 / 0 / 0**, buildings **2 / 3 / 0 / 1**. The equal-distance boundary lies between sampled integer columns, so no sampled grid point ties even though a geometric boundary still exists. The outside building stays outside. Restore defaults, then narrow `domain` to `(1, 5, 0, 4)`: all 35 samples remain accounted for as A/B/tie/outside **10 / 10 / 5 / 10**, with a matching domain frame and caption. Restore defaults, then discuss how a finer grid, a different domain, duplicate seeds or a missing building record would change what must be reported. Do not turn these sample counts into population risk.",
        "The five main source notebooks teach Voronoi diagrams, convex hulls, exact polygon construction, Folium interaction and building-centroid point-in-polygon counts; NB99 is a separate alpha-shape supplement. Those native geometric constructions differ from our finite nearest-site samples. A Euclidean nearest cell does not establish street access, pump use, a transmission boundary or a population at risk. Compare with Advanced1: one changes a travel network; the other changes a geometric rule. Neither replaces household and water-use evidence in the historical investigation.",
    ),
    "mdr-tb-thailand-2005": (
        MDR_CODE,
        "After the [Cholera sequence](../cholera-1854-advanced-2/index.ipynb), move from geometric rules to evidence joining. Six invented stable IDs carry an observed teaching drug-susceptibility-test (DST) label; `None` means unknown, never susceptible. Undirected reported contacts accept only strong or weak evidence; DST accepts only MDR, non-MDR or None, and unsupported categories stop the calculation. These are invented labels, no patient geography or reconstructed cohort. Predict whether including C–D can merge groups without changing anyone's DST. The component walk follows selected contacts while explicitly preserving every ID, including isolated F.",
        "Strong-only contacts produce **ABC / DE / F**, component sizes **3 / 2 / 1**. Observed labels give **3 MDR / 4 known DST**, and **2 unknown / 6 total IDs**. The first denominator excludes unknowns; the second includes everyone. Neither fraction is prevalence in a real population. Gold, green and hollow nodes represent MDR, non-MDR and unknown; line style represents evidence policy. There are no arrows because neither temporal direction nor transmission is established. Contact, component membership, genotype similarity and laboratory resistance are different evidence types.",
        "Set `include_weak = True`: components become **ABCDE / F**, sizes **5 / 1**, while every observed DST label stays the same. Restore `False`, then change only `'C': None` to `'C': 'MDR'`: **4 / 5 known DST**, with one unknown among six IDs. Finally set all DST values to `None`: the fraction must be **unknown**, not 0%, while components still follow contact policy. Restore defaults and draft a record-joining check: stable ID, duplicate-edge handling, missing lab result, interview confidence and who may access sensitive evidence.",
        "The 2005 investigation concerned US-bound Hmong refugees in Thailand. Read Oeltmann and colleagues' 2008 article with respect for people navigating displacement and access barriers; the historical setting does not justify stigmatizing a community. The source course moves through investigation/genotyping, historical WHO/World Bank country-year preparation and merges, Plotly ecological summaries, genotype/DST joins, secondary interviews and social networks. The contact lesson is marked work in progress. Country-level TB/GDP/education/spending summaries do not identify individual risk or mechanisms. Historical source data and policies are not current clinical or immigration guidance, and no historical API is called here. An actual diagnosis requires laboratory/clinical evidence; this exercise supplies none.",
    ),
}


def route_links(slug):
    order = list(CASES)
    links = [f"[{CASES[key]['title']}](../{key}/index.ipynb)" for key in order if key != slug]
    return "## Continue the investigation\n\nBasic → Advanced1 → Advanced2 → MDR-TB is the suggested order.\n\n" + " · ".join(links) + "\n\n[Browser Python](../../foundations/browser-python.ipynb) · [Spatial thinking](../../foundations/spatial-thinking.ipynb) · [Global-health synthesis](../../synthesis/global-health.ipynb) · [Learning routes](../../index.ipynb)"


def chapter_cells(record, md, code, helpers):
    slug = record['slug']
    case = CASES[slug]
    activity, predict, interpret, edit, context = ACTIVITIES[slug]
    resources = "\n".join(f"- [{r['label']}]({r['url']}) — {r['description']} **{r['availability']}; checked {r['checked_on']}.**" for r in record['resources'])
    citations = MDR_CITATIONS if slug.startswith('mdr') else CHOLERA_CITATIONS
    if slug != 'cholera-1854-basic':
        citations += "\n" + METHOD_CITATIONS
    return [
        md(f"# {case['title']}\n\n**PHI outbreak investigations · 20–30 minutes · original browser companion**\n\n{case['summary']}\n\n**Learning question:** {case['question']}\n\n**Data status:** original synthetic teaching fixture; no historical measurements, real patient records, source map or external data requests. This bounded companion runs with standard-library Python and IPython in the atlas Lab. Linked source courses have their own rights and runtimes."),
        md("## Predict before running\n\n" + predict + "\n\nWrite a prediction and an assumption. Run cells in order with **Shift+Enter** or **Run → Run All Cells**. The first code cell supplies local SVG display helpers; the next performs the calculation. Every figure has a title/description and printed values as a text alternative. Allow up to 60 seconds per cell on first runtime load; the fixture calculation normally takes seconds and needs no installs, account or credentials."),
        code(helpers), code(activity),
        md("## Interpret the result\n\n" + interpret + "\n\n## Change one thing\n\n" + edit + "\n\nSave your edited experiment with **File → Save and Export Notebook As → Notebook** or the file browser's Download command. Browser storage belongs to this browser/profile; it is not a GitHub commit or a shared patient database. Restart the kernel and Run All to check your saved version."),
        md("## Put the method in context\n\n" + context),
        md(source_overview(slug)),
        md("## Source launch resources and runtime limits\n\n" + resources + "\n\nThese dated GET checks establish entry reachability only. The Basic/Advanced1 notebook filenames were also present in published manifests; no source execution, widget, tile/provider behavior or Binder session is certified. No Binder build is triggered by these atlas activities. Source continuation may require packages, networking and provider terms absent from the default atlas runtime."),
        md("## Sources, attribution and use\n\n" + citations + "\n" + RIGHTS + "\n\n[Central references](../../references.ipynb) · [Visual provenance](../../visual-provenance.ipynb)"),
        md(route_links(slug)),
    ]
