# Validation record

Verified locally on **2026-11-01**, using Windows, Python 3.13.14, pinned requirements and headless Chrome. Exactly four requested source repositories are now public, confirmed again through unauthenticated GitHub API requests. This record describes local verification. Remote CI and publication results are recorded by the [GitHub Actions workflow](https://github.com/jltobias/JupyterLite-Index-Repo/actions/workflows/pages.yml).

| Check | Result |
|---|---|
| Public coverage | Passed: 29 public JupyterLite-named repositories and three related public browser projects, from a fresh 58-record public inventory. All four requested sources are included. |
| Structure and sources | Passed: 32 project chapters, 41 canonical notebooks, matching navigation, 228 local notebook links, immutable source README citations and all ten original Rewiring lesson links. |
| Notebook execution | All four new notebooks completed in fresh temporary working directories with Python data-service networking blocked, with saved SVG outputs and text alternatives. The buffer notebook was re-executed after its code revision. The other three retained identical executed code and outputs after narrative refinements; their receipts distinguish executed and current artifact hashes. Existing code notebooks retain prior execution evidence. There are 38 code notebooks and three narrative pages, with no saved execution errors. The introduction's catalog count cell/output was refreshed. |
| Preservation | Compared all original 37 notebooks with the pre-expansion snapshot: code is unchanged except the required catalog-derived introduction count cell. Existing authored exercises and other original artwork were preserved. |
| Focused regressions | Passed all 20 unit tests. New checks assert threshold ties, default and edited buffer membership, dynamic SVG descriptions and XML escaping, focal means and edge denominators, the full-window extension, extract means/coverage, seed parity and assembly of public catalog evidence. Prior baseline source-UI tests also passed. |
| Strict Book | Passed final expanded assembly with Jupyter Book 1.0.4.post1 / Sphinx 7.4.7, using --warningiserror --keep-going --nitpick. The pinned v1 renderer is in maintenance mode. |
| Lite assembly | Passed expanded builds before and after review fixes. Distribution-owned Pyodide 0.8.3 assets are explicitly staged; the task database belongs to the disposable Lite project. Validation requires kernel JavaScript/schema and all four app/storage values. The prior baseline also passed two consecutive clean builds. |
| Book/Lab correspondence | Passed: all 41 canonical notebooks copied byte-for-byte into Lab, all 32 project Book routes exist, and explorer catalog/evidence copies match their sources. The new visibility audit is served successfully at catalog/public-visibility-changes.json (HTTP 200). Prior rendered GeoJSON export evidence is retained. |
| Browser behavior | Passed shared Chrome checks for search, actual theme membership, type/status filters, empty/reset/focus, related separation, threshold arithmetic, 2D/3D controls, keyboard rotation, Book aliases, six entry points and 390px mobile layout. Final checks passed for all four new source disclosures, Book pages and exact Book-to-Lab links. |
| Actual browser Python | Passed a fresh expanded JupyterLite/Pyodide run: canonical fitted-model code produced a unique new marker, newly executed SVG and expected held-out MAE **7.686**. The final content/evidence rebuild preserves the same validated kernel assets and configuration. |
| Visuals | Six original SVG assets passed XML/provenance and exact-copy checks. The theme infographic counts 32 projects across seven themes. All four final new exercise figures passed Chrome text-clipping checks; buffer and focal-mean figures were visually inspected. Printed values accompany the figures. |
| External launch links | All **83** resources have dated HTTP GET evidence: **81 returned 200**; the documented Global Health GIS and Maps-and-Spatial-Analyses URLs returned **404**. The exact URLs remain visible with dated status. This checks entry reachability, not external application functionality. |
| Source visibility | All four requested repositories returned anonymous GitHub API HTTP 200 with visibility public and private false. The normalized public audit contains only those four authorized changes. |

## Reproduce

```bash
python -m unittest discover -s tests
python scripts/execute.py --write
python scripts/build.py
python scripts/test_browser.py
python scripts/test_ui_repairs.py
python scripts/check_runtime.py
```

Install the pinned browser-test requirements and Playwright Chromium first; see CONTRIBUTING.md. An installed Chrome/Chromium can be selected with --browser-executable for browser/runtime checks; ATLAS_TEST_BROWSER_EXECUTABLE selects it for source-UI tests.

Local expansion evidence is under ignored _build/: public-four-execution-results.json, public-four-preservation-results.json, public-four-final-units.log, public-four-final-build.log, public-four-browser.log, public-four-runtime.log, browser/results.json, public-four-browser/results.json and runtime-browser/results.json. Screenshots are in the browser folders. Earlier full-notebook and source-UI evidence is retained. Windows sandbox restrictions required elevated local execution for kernel connection files, temporary directories and browser processes.

## Limits

The real-browser kernel check executes one complete canonical code sequence. All default exercise code has native execution evidence, but every notebook/UI combination and other browser engines were not separately certified. Initial runtime downloads need internet access; a fresh fully offline browser is not guaranteed to start.

Shiny-Live-Apps currently supplies only a title-only README; its atlas prototype is original code, not a source Shiny application. Public source visibility does not establish a deployed Pages site. External datasets, native/GPU continuations, live AI providers and linked apps retain their own requirements and rights. Synthetic exercises do not establish real health findings, causal effects or operational readiness. This index is published through GitHub Actions; confirm current availability in the [workflow status](https://github.com/jltobias/JupyterLite-Index-Repo/actions/workflows/pages.yml).
