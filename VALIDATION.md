# Validation record

The **2 November 2026 EO update** uses the unchanged README PNG in the opening Book/Lab notebook and adds the EO Satellite Guide chapter, an original routing demonstration, and a proposed STAC/EarthCODE connection. The [publication workflow](https://github.com/jltobias/JupyterLite-Learning-Atlas/actions/workflows/pages.yml) records remote validation and deployment for each commit.

| Current check | Result |
|---|---|
| Coverage | 32 core JupyterLite repositories plus seven related projects; 39 project chapters, 48 canonical notebooks (45 code/three narrative), 65 discovery records and 300 local notebook links. Every canonical notebook appears exactly once in the Book. |
| Regressions | All 65 unit tests passed, including 14 EO tests covering default/edited routes, unknown mapping, static archive, invalid/canonical UTC/bbox/page inputs, actual marker lanes, query contents, source/seed/non-overwrite behavior and the unchanged cover. Preservation tests now permit future unrelated additions while protecting baseline paths/records. |
| Review | Three independent review lenses completed. Fixes cover portable artwork hashes, escaped SVG identifiers, derived figure totals, printed compatibility evidence/JSON assertions, mobile reading guidance and current reproduction instructions. No unresolved or deferred review issue remains. |
| Native execution | New EO and updated introduction executed in separate fresh kernels and temporary directories with Python data-service networking blocked. No saved errors. EO was re-executed after the review fixes. |
| Preservation | All 47 previous notebook code sequences are preserved except the introductory metadata-count list. STAC code and raw outputs, 38 source records, 64 discovery records, 158 launch rows and two prior manifest observations are unchanged. All five non-count SVGs and the cover PNG retain their bytes (SVG comparison normalizes checkout line endings). |
| Strict assembly | Full strict Book/Lite build passed, including all 48 canonical notebook byte-identical Lab copies, Book routes, runtime assets/settings and exact catalog/evidence copies. |
| Browser | All three source-UI tests and the retained complete Chrome behavior suite passed. New checks cover EO/EarthCODE searches and disclosures, six pinned notebook links, ten source/ESA resources, primary citations, reciprocal STAC links, exact Lab handoff, 390px mobile width and unclipped accessible SVG. The new figure was visually inspected. |
| Shared cover | Book and a fresh Lab context both display the 1774 × 887 README PNG with alt text and AI-art credit. JupyterLite resolves it to a data URI; SHA-256 of the actual displayed bytes matches the committed image: 09b30e50095b2286df7ea0a1556fd447d1124c83b3ab5dfc68fab4c29877b0f9. No image generation or pixel changes were made. |
| Actual browser Python | All seven canonical cases passed in separate fresh Pyodide browser contexts: ML, Coral, four PHI cases and EO. Each ran canonical code plus numerical/edit assertions and a unique marker, then verified the newly loaded SVG from the executed cell. Saved outputs alone do not satisfy this check. |
| Sources and scope | Ten new entry GETs returned HTTP 200 on 2026-11-02; total 168 resources (166 HTTP 200/two historical HTTP 404). EO manifest confirms six root notebook filenames; its normalized checksum is retained separately. README, chapter and reference page cite source pins, creators, MIT/CC BY4 distinctions, Natural Earth, STAC/W3C standards and official ESA EarthCODE documentation. The integration is a proposal; no upstream merge, source execution certification, data/model request, cloud job or external publication is claimed. |

Local evidence: `_build/eo-review-units.log`, `eo-review-build.log`, `eo-parent-ui.log`, `eo-review-browser.log`, `eo-review-runtime.log`, `eo-native-execution.json`, `eo-parent-preservation.json`, `browser/results.json` and `runtime-browser/results.json`. These receipts describe local verification; use the workflow above for the publication result of a revision.

## Previous PHI outbreak verification

The **2 November 2026 PHI outbreak update** adds Cholera Basic, Advanced1, Advanced2 and MDR-TB Thailand as four original browser companions. Basic is the second learning chapter. The atlas now contains **38 project chapters and 47 canonical notebooks**. The [publication workflow](https://github.com/jltobias/JupyterLite-Learning-Atlas/actions/workflows/pages.yml) records deployment for each commit.

| Current check | Result |
|---|---|
| Coverage and ordering | 31 core jltobias JupyterLite repositories, three prior related projects and four external PHI courses; 47 notebooks (44 code / three narrative), 64 discovery records. Every canonical notebook appears once in the Book. Basic follows browser Python; Advanced1, Advanced2 and MDR form the ordered Outbreak investigations part. |
| Numerical and source regression | All 51 unit tests passed. New cases cover original defaults, instructed edits, zero totals, disconnected nodes, inclusive budgets, nearest-site ties/outside records, contact-policy components and all-unknown DST, plus narrowed-domain accounting, invalid edge/category rejection, external provenance and actual weighted-marker geometry. Assertions inspect actual calculations, printed values and SVG output. Source validation passed 292 local notebook links. |
| Fresh native execution | The four new chapters and updated introduction ran in separate fresh kernels and temporary working directories with Python data-service networking blocked. Three notebooks with reviewed calculation changes were re-executed in fresh guarded kernels; unchanged Basic/introduction code retains its earlier execution evidence. Saved outputs contain no errors. The other 43 notebooks' code was compared with baseline efbdff2202c860f665722c3b4ae82f3e965725fd; only the introductory catalog-theme list changed. |
| Preservation | All 145 prior launch rows, 34 prior source records and 60 prior discovery records retain their canonical digests. The cover is byte-identical; all five other non-count SVG compositions are preserved after line-ending normalization. |
| Strict Book/Lab assembly | Passed strict Jupyter Book/Sphinx build, all Book routes, loadable kernel assets/settings, exact canonical-to-Lab notebook bytes and exact public catalog/evidence copies. |
| Browser and visuals | All three source-UI tests and retained Chrome checks passed. The four new routes passed 20 pinned notebook links, 13 source launches, reciprocal navigation, exact Lab handoffs, 390px mobile layout and accessible SVG text-clipping checks. All four original figures were visually inspected. A font-metric stress check protects long immutable citations from Sphinx nested-span overflow. |
| Actual browser Python | All six retained cases passed in separate fresh Pyodide browser contexts: ML, Coral, Cholera Basic, Advanced1, Advanced2 and MDR-TB. Each executed canonical code with numerical/edit/unknown assertions, a new unique marker and a newly loaded SVG from that actual cell. Saved outputs alone do not satisfy this check. |
| Source evidence and attribution | The 13 new source entry GETs returned HTTP 200 on 2026-11-02; catalog total 158 resources (156 HTTP 200 / two retained historic HTTP 404s). Basic/Advanced1 published manifests confirm notebook filenames. Advanced2/MDR source Binder entries are native/server continuations; no browser manifest or source execution is claimed and no Binder build/session was started. All 20 source notebook paths, pinned versions, creators, historical/medical/method sources and license layers appear in README, central references and chapters. No source data/code/media or patient records are copied. |

Local evidence: `_build/phi-final-units.log`, `phi-final-build.log`, `phi-final-ui.log`, `phi-final-browser.log`, `phi-final-runtime.log`, `phi-execution-results.json`, `phi-review-execution-results.json`, `phi-preservation.json`, `browser/results.json` and `runtime-browser/results.json`. These local receipts precede publication; the workflow above is the authority for remote build/deploy status.

The Coral/rename/cover milestone at commit c62c6e211134e410f8826c6b4a68547f6ba96fa5 passed [Actions run 41457829971](https://github.com/jltobias/JupyterLite-Learning-Atlas/actions/runs/41457829971) and deployed successfully. Public hub, Coral chapter, README and Lab returned HTTP 200, and published cover bytes matched the committed hash. The four PHI companions follow that milestone in this revision.

## Previous Coral, cover and rename verification

The **2026-11-02** update adds Coral Reef One Health, the README cover and the repository rename to **JupyterLite-Learning-Atlas**. The local workspace folder retains its earlier name. Current publication status is available in the [GitHub Actions workflow](https://github.com/jltobias/JupyterLite-Learning-Atlas/actions/workflows/pages.yml).

| Current check | Result |
|---|---|
| Coverage | 31 JupyterLite-named plus three related projects; 34 project chapters, 43 canonical notebooks (40 code / three narrative), 60 public discovery records. The Coral source was a targeted addition; older sources were not fully reinspected. |
| Numerical and source checks | All 34 unit tests passed, including eight Coral tests for default/edit/zero/all-missing/error behavior, actual SVG values, seed preservation and primary citation links. Source validation passed with 242 local notebook links. |
| Native execution and preservation | New Coral and introduction code ran in fresh network-guarded native kernels. All 42 prior notebooks' code was compared with baseline cc0e120e51ebad702ab42b4c56dd7544ddf9466d: only the introductory catalog theme list changed. Five original non-count SVG compositions and all 134 previous launch-audit rows are preserved. |
| Strict assembly | Complete Book/Lite build passed, including every Book route, byte-identical canonical Lab copies, all four runtime settings, kernel assets and exact public catalog evidence copies. |
| Browser | Shared source-UI and Chrome behavior checks passed under /JupyterLite-Learning-Atlas/. Targeted Coral checks passed both pinned source notebook links, DOI/provider links, exact Book-to-Lab handoff, explorer disclosure, mobile overflow and SVG clipping checks. |
| Actual browser Python | Standard ML gate and the complete new Coral code sequence passed in separate fresh Pyodide browser contexts under the renamed prefix. New unique markers, numerical assertions and newly loaded SVGs prove execution. Coral assertions cover 0.65/0.35 defaults, unknown/75% coverage, reversed weights, observed zero, all-missing and invalid weights. An initial Coral kernel-startup timeout was retained in diagnostics; the fresh retry completed successfully. |
| Sources and rights | Eleven Coral/provider entry GETs returned 200 on 2026-11-02. Catalog totals: 145 resources, 143 HTTP 200 and two retained earlier 404s. Entry responses do not certify external service functions. README, central references and chapter record the full source commit, author, publication metadata and provider rights. Source has no repository-wide license selected; no source assets were copied. |
| Cover | Built-in OpenAI image generation produced the new 1774 ×887 README illustration, visually inspected and copied unchanged. Full prompt, date, attribution and SHA-256 appear in assets/SPLASH-PROVENANCE.md. Existing SVG artwork remains available for Book and website. |
| Rename | GitHub repository ID1441864612 is unchanged and public at jltobias/JupyterLite-Learning-Atlas; origin, Pages links, citation/build settings, self-exclusion and preview/browser prefixes are updated. catalog/repository-rename.json records identity verification. |

Current local evidence is in _build/coral-implementation-evidence.json, coral-preservation-results.json, coral-units.log, coral-build.log, coral-source-ui.log, coral-browser.log, coral-browser/results.json, coral-runtime/results.json and runtime-browser/results.json. Unchanged earlier execution evidence is retained. Publication results follow the successful Actions run for a commit.

The public `scripts/test_browser.py` now retains Coral provider search, source links, route, mobile and SVG assertions. `scripts/check_runtime.py` retains both fresh ML and Coral execution cases; its CLI is unchanged. A committed canonical digest protects the original 134 launch-audit rows, and a derived test checks the introduction's printed and plotted theme counts against the catalog.

## Previous Ocean Watch and Earth studio verification

Verified locally on **2026-11-01** with Windows, Python 3.13.14, pinned build dependencies and headless Chrome. Remote validation/publication results are recorded in the [GitHub Actions workflow](https://github.com/jltobias/JupyterLite-Learning-Atlas/actions/workflows/pages.yml).

| Check | Result |
|---|---|
| Public coverage | Passed: 30 JupyterLite-named plus three related projects, 33 project chapters, 42 canonical notebooks (39 code / three narrative), and 59 public discovery records. |
| Sources and navigation | Passed schema, unique chapter paths, immutable source README citations, 233 local notebook links, nine pinned Ocean source notebooks, all 30 exact Earth-course Lab links, and all ten original Rewiring lesson links. |
| Native execution | Ocean Watch, Zarr/SQL and the updated introduction completed in fresh temporary directories/kernels with Python data-service networking blocked. Zarr was re-executed after its coverage-reference change. Narrative-only Ocean revisions retained identical executed code/outputs; receipts distinguish execution and current artifact hashes. Previous unchanged code retains prior execution evidence. No saved errors. |
| Preservation | All 41 previous notebook code sources were compared with baseline 7623ef63db2f5d737ecd0b23324a5f6428f5ca87. Only the introduction's catalog-count cell changed; both original Zarr code cells are preserved and its new exercise is additive. Five non-count SVG compositions and all 83 prior launch-audit rows are preserved. |
| Numerical regressions | All 26 unit tests passed. New tests cover inclusive gates, ambiguity, default and edited plotted counts, observed zero, variable-specific None masks, all-missing unknown results, 8/5 versus 8/8-day weighting, the 26-cell-day reference, seed parity and exact source/audit links. |
| Strict Book/Lite assembly | Passed Jupyter Book 1.0.4.post1 / Sphinx 7.4.7 with --warningiserror --keep-going --nitpick, plus isolated JupyterLite assembly. The final validator checks loadable Pyodide assets, all four custom configuration values, all 33 Book routes, byte-identical copies of every canonical notebook into Lab and exact catalog/evidence copies. |
| Browser behavior | Passed shared Chrome checks for search, theme/type/status filters, reset/focus, URL state, related separation, 2D/3D controls, threshold arithmetic, Book aliases, six entry points and mobile layout. A new regression reproduced and then verified the first-click source-disclosure fix after typing a search. Final rendered checks passed Ocean/LexCube discovery and both exact Book-to-Lab handoffs. |
| Actual browser Python | Both updated chapters ran their complete canonical code sequences in separate fresh Pyodide browser contexts. Unique newly printed markers, loaded SVGs and numerical assertions verified Ocean counts2/1/1 and ambiguity, and Zarr intervals8/5, observed burned total10ha, coverage18/26 and21/26, and weighted temperature450/21. Saved outputs alone do not satisfy this check. |
| Visuals | Six original source SVGs passed XML/provenance and exact-copy checks; the overview counts33 projects across seven themes. All three executed figures in the two updated chapters passed Chrome text-clipping checks. Fresh browser-executed figures were visually inspected. |
| Source entry links | All122 exact source entry URLs checked for the two refreshed courses returned HTTP 200. The curated catalog has134 dated launch resources:132 HTTP200 and two retained earlier HTTP404 results. This establishes entry reachability, not external notebook/widget/provider functionality. |
| Attribution | README, central references and both chapters record source commits, versions, creators and license distinctions. The GFW deposit is pinned to DOI version4; deposit CC BY4 differs from platform CC BY-NC4. Source ISC content, LexCube GPL-3.0-or-later, linked datasets and original index MIT/CC BY4 material remain distinct. No source data, code, imagery, weights, source infographics or LexCube binaries were copied. |

## Reproduce

```bash
python -m unittest discover -s tests
python scripts/execute.py --write
python scripts/build.py
python scripts/test_ui_repairs.py
python scripts/test_browser.py
python scripts/check_runtime.py
```

Install pinned browser-test requirements and Playwright Chromium first. An installed Chrome/Chromium can be selected with --browser-executable; ATLAS_TEST_BROWSER_EXECUTABLE selects it for source-UI tests. The standard runtime gate runs the ML foundation, Coral, all four PHI case companions and EO in seven separate fresh browser contexts. The additional local Ocean/Earth smoke executed unmodified canonical code plus numerical assertions and a unique marker, and checked the newly loaded SVG in the same executed cell; notebook windowing was handled by following that unique output to its actual cell.

Ignored local evidence: _build/ocean-earth-execution-results.json, ocean-earth-execution-results-initial.json, ocean-earth-preservation-results.json, ocean-earth-units.log, ocean-earth-final-build.log, ocean-earth-browser.log, ocean-earth-browser/results.json and ocean-earth-runtime/results.json, with screenshots in the browser folders. Earlier baseline evidence is retained. Windows kernel connection files and browser processes required authorized execution outside the filesystem sandbox.

## Limits

Initial Python/runtime downloads require internet access. Other browser engines and every external source notebook/widget combination were not certified. The index fixtures are synthetic; they establish no actual identity, illegality, health outcome, causal effect or forecast. The coverage exercise is a Python analogue of SQL; actual SQL and LexCube remain external course capabilities. Linked source data/software retain their provider terms. Publication availability follows the successful GitHub Actions deployment for a revision.
