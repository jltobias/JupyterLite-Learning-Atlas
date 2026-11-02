# Validation record

Verified locally on **2026-11-01** with Windows, Python 3.13.14, pinned build dependencies and headless Chrome. Remote validation/publication results are recorded in the [GitHub Actions workflow](https://github.com/jltobias/JupyterLite-Index-Repo/actions/workflows/pages.yml).

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
| Source entry links | All122 exact source entry URLs checked for the two refreshed courses returned200. The curated catalog has134 dated launch resources:132 HTTP200 and two retained earlier HTTP404 results. This establishes entry reachability, not external notebook/widget/provider functionality. |
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

Install pinned browser-test requirements and Playwright Chromium first. An installed Chrome/Chromium can be selected with --browser-executable; ATLAS_TEST_BROWSER_EXECUTABLE selects it for source-UI tests. The standard runtime gate runs the ML foundation. The additional local Ocean/Earth smoke executed unmodified canonical code plus numerical assertions and a unique marker, and checked the newly loaded SVG in the same executed cell; notebook windowing was handled by following that unique output to its actual cell.

Ignored local evidence: _build/ocean-earth-execution-results.json, ocean-earth-execution-results-initial.json, ocean-earth-preservation-results.json, ocean-earth-units.log, ocean-earth-final-build.log, ocean-earth-browser.log, ocean-earth-browser/results.json and ocean-earth-runtime/results.json, with screenshots in the browser folders. Earlier baseline evidence is retained. Windows kernel connection files and browser processes required authorized execution outside the filesystem sandbox.

## Limits

Initial Python/runtime downloads require internet access. Other browser engines and every external source notebook/widget combination were not certified. The index fixtures are synthetic; they establish no actual identity, illegality, health outcome, causal effect or forecast. The coverage exercise is a Python analogue of SQL; actual SQL and LexCube remain external course capabilities. Linked source data/software retain their provider terms. Publication availability follows the successful GitHub Actions deployment for a revision.
