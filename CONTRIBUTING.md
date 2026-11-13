# Contribute to the learning atlas

The catalog drives navigation; **`content/**/*.ipynb` are the canonical authoring files** for both Book and Lab. The same bytes are copied into JupyterLite, preserving folders. Original Atlas companion code is MIT; original Atlas narrative, figures and synthetic fixtures are CC BY 4.0. Imported courses, software and datasets retain their individual licenses and notices in `catalog/source-library.json` and each course guide.

Editor checkpoints and hidden working folders are excluded from execution, chapter discovery and the published Lab. Run `python -m unittest discover -s tests` when changing content selection or packaging.

## Build and preview

Use Python 3.13 and an isolated environment. Node is not needed for this static Jupyter Book v1/JupyterLite build. Jupyter Book v1 is in maintenance mode; this project deliberately pins its stable Sphinx notebook renderer rather than claiming the latest Book generation.

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements-build.txt
python scripts/generate.py
python scripts/validate.py
python scripts/execute.py --write
python scripts/build.py
python scripts/serve.py
```

Open `http://localhost:8000/JupyterLite-Learning-Atlas/`. The preview deliberately uses the GitHub project subpath. `_site/` is generated output. Builds never publish, stage or commit anything. The first browser load of Pyodide still needs network. Original companion exercises use local fixtures; source lessons may require networks, credentials, native libraries or missing inputs, as their course guides explain. Notebook edits live in browser storage. Download work before clearing browser data or changing profiles. Rebuild the site after changing notebooks.

`scripts/build.py` regenerates navigation, validates source, runs a strict Book build, copies canonical content into a Lite staging folder, builds JupyterLite and assembles `_site/`. It does not execute notebooks implicitly: run `execute.py --write` before building changed code. CI executes them before its build. The build only replaces its own `_build/` staging subfolders and `_site/`; output paths are checked to stay under this repository. It preserves `.git` and the source tree.

## Add a project

1. Check the actual public source README and default branch. Add its public discovery record to `catalog/discovery.json`; do not include private or sensitive source metadata. Keep distinct editions separately named and explain their status.
2. Add a record to `catalog/repositories.json` following `catalog/repositories.schema.json`. Required fields include a unique kebab-case slug, title, theme, question, status/category, immutable reviewed README URL, source commit, notebook/Book/Lab paths, attribution and runtime limitations. `category` is `jupyterlite` for core prefixed projects owned by jltobias; use `related` for evidenced related browser/teaching projects, including external PHI sources regardless of name casing. External targeted reviews record `source_owner` and `source_review` with inspected notebook paths and launch provenance. Preserve **exact** source URLs and case from a reviewed README or an explicitly observed pinned deployment workflow/published manifest; label the evidence origin. Record status/date without calling an HTTP 200 a functional guarantee. If neither supplies a launcher, use an empty resources list and a source-only explanation.
3. Run `python scripts/generate.py`. It creates navigation and any missing project notebook. Unknown projects get an explicit incomplete scaffold. **Existing notebooks are never overwritten**, including manual edits and executed outputs. `scripts/lesson_material.py` contains initial seeding material, not a live replacement for canonical notebooks. Edit the new notebook directly and remove its `metadata.atlas.scaffold` flag only after the chapter is complete.
4. Author a distinct domain-specific exercise with a learning question, explained computation, generated visual and printed text alternative, interpretation, extension, exact source citation and continuation limits. Use stdlib and IPython display only, small deterministic fixtures, no installs/network/credentials. Label synthetic data or actual metadata accurately. Keep precise sensitive locations and health records out of source, output, screenshots, URLs and model contexts.
5. After changing theme counts, refresh only metadata artwork with `python -c "from scripts.make_assets import make_repository_overview; make_repository_overview()"`, then `python scripts/generate.py` to copy assets. Review `assets/PROVENANCE.md`. Add citations to `REFERENCES.md` and synchronize the narrative-only `content/references.ipynb` if that page changes. Similarly synchronize the contributor notebook when this guide changes; generator preserves it by design.
6. Execute changed notebooks, run validation/build/browser checks, and update `VALIDATION.md` with actual results and limits. Review canonical outputs and catalog diffs. The validation fails on omitted public prefixed projects, duplicates, missing notebooks, incomplete scaffolds, path mismatches and unsupported imports.

## Add or refresh a source course

Preserve source chapters as distinct editions. Review an immutable upstream commit, scoped licenses, dataset terms, sensitive inputs and embedded media before copying. The read-only checkouts used for an intentional import live in `_research/textbook-sources/<slug>`; normal builds never fetch them. `scripts/import_sources.py` records every inspected notebook as imported, an exact alias or a reasoned exclusion, with hashes, runtime requirements and adaptations in `catalog/source-library.json`. Extend its explicit course policy for a new source rather than silently skipping unfamiliar files. Never execute an upstream build script merely to collect its output. Run `python scripts/import_sources.py --check` against the reviewed checkouts after an import.

Add each copied helper, data file, license and notice to the support manifest with its source and hash. Give actual datasets a creator/version citation, terms, source link and modification statement in `catalog/data-attributions.json`; then run `python scripts/data_credits.py --write` to refresh the marked README, references and Book blocks. `python scripts/data_credits.py` checks that they agree and that required bundled data is credited. Keep mandatory copyright, attribution, share-alike and corresponding-source notices. Unclear or restricted material belongs in the exclusion ledger with a continuation link. Owner-authorized original work without a public license must not receive an invented public license.

Add the course guide and its ordered source sections to the generated TOC. The sidebar reads this recursive hierarchy without resolving the entire document tree on every page. Use `browser-local`, `browser-network`, `local-server` or `reference-only` to describe intended use; execution receipts are a separate fact. Select a lesson for automated execution only after reviewing its code and dependencies. New courses and existing sections can grow without changing a fixed chapter-count limit.

The .gitattributes rule disables Git newline conversion within content/courses/** so the audited data, helper and license bytes survive Windows/Linux commits and checkouts. Preserve that rule when extending the collection. Hashes describe the inspected source-checkout bytes; upstream Git pins and ordered cell-source hashes separately identify provenance.

## Validation and browser checks

```bash
python scripts/execute.py --write
python scripts/validate.py
python scripts/build.py
python scripts/validate.py --built
python -m pip install -r requirements-browser-test.txt
python -m playwright install chromium
python scripts/test_browser.py
python scripts/check_runtime.py
python scripts/check_source_runtime.py
# Or: python scripts/test_browser.py --browser-executable "C:/Program Files/Google/Chrome/Application/chrome.exe"
```

Execution uses a fresh temporary working directory per notebook, blocks Python-level data-service calls and audits imports. It is a reproducibility check, not proof of health validity. Browser checks exercise search, filters, empty/reset states, related-project separation, mobile overflow and local 2D/3D controls. The separate `python scripts/check_runtime.py` check creates a fresh browser context, explicitly selects Python/Pyodide, runs the canonical fitted-ML code, and requires a unique newly printed marker plus its SVG output. CI requires this check; a loaded Lab shell is insufficient. Use `--browser-executable "path/to/chrome"` for an installed Chrome/Chromium on any platform, or omit it for Playwright's Chromium. Initial runtime downloads need network; failures identify an unavailable kernel/runtime instead of claiming a pass.

The Lite build locates Pyodide assets through the installed `jupyterlite-pyodide-kernel` distribution metadata, including user-site installations. It copies only that extension into `_build/lite-project/extensions/`, disables unrelated environment-extension discovery, copies the custom app/storage configuration into that isolated project, and uses `--force` so stale task state cannot skip configuration patches after output cleanup. Built validation requires the kernel's metadata/JavaScript assets and all four custom app/storage values. See the official [configuration files](https://jupyterlite.readthedocs.io/en/stable/howto/configure/config_files.html) and [advanced extension](https://jupyterlite.readthedocs.io/en/stable/howto/configure/advanced/extensions.html) documentation.

Native WhiteboxTools, GDAL/Rasterio stacks, RustGIS Python and GPU/model services require their source's supported local/server environment. Begin with one tiny public/synthetic fixture, a five-minute trial and a memory/cost budget. An optional live model needs approved data flow and server-managed secrets; never embed long-lived keys in browser notebooks.

## Publish with GitHub Pages

The included `.github/workflows/pages.yml` validates pull requests and deploys successful builds on pushes to `main` (or a manual run on `main`). In GitHub **Settings → Pages → Build and deployment → Source**, choose **GitHub Actions**. The workflow needs Pages/write and OIDC permissions only in its deploy job. Consult the [repository workflow status](https://github.com/jltobias/JupyterLite-Learning-Atlas/actions/workflows/pages.yml) to confirm that a revision has passed validation and deployed successfully. Existing source-project availability is recorded independently.

## Sources for the build architecture

[Jupyter Book v1](https://jupyter-book.readthedocs.io/v1/intro.html), [JupyterLite content](https://jupyterlite.readthedocs.io/en/stable/howto/content/files.html), [JupyterLite deployment](https://jupyterlite.readthedocs.io/en/stable/howto/deployment/index.html), [Pyodide](https://pyodide.org/en/stable/), [GitHub Pages Actions](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages). These tools retain their own licenses and transitive notices.
