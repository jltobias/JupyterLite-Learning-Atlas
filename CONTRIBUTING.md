# Contribute to the learning atlas

The catalog drives navigation; **`content/**/*.ipynb` are the canonical authoring files** for both Book and Lab. The same bytes are copied into JupyterLite, preserving folders. Original notebook code is MIT; narrative, original figures and original synthetic fixtures are CC BY 4.0. Linked source works keep their own terms.

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

Open `http://localhost:8000/JupyterLite-Index-Repo/`. The preview deliberately uses the GitHub project subpath. `_site/` is generated output. Builds never publish, stage or commit anything. The first browser load of Pyodide still needs network; notebook computations need no remote data or credentials. Notebook edits live in browser storage. Download work before clearing browser data or changing profiles. Rebuild the site after changing notebooks.

`scripts/build.py` regenerates navigation, validates source, runs a strict Book build, copies canonical content into a Lite staging folder, builds JupyterLite and assembles `_site/`. It does not execute notebooks implicitly: run `execute.py --write` before building changed code. CI executes them before its build. The build only replaces its own `_build/` staging subfolders and `_site/`; output paths are checked to stay under this repository. It preserves `.git` and the source tree.

## Add a project

1. Check the actual public source README and default branch. Add its public discovery record to `catalog/discovery.json`; do not include private or sensitive source metadata. Keep distinct editions separately named and explain their status.
2. Add a record to `catalog/repositories.json` following `catalog/repositories.schema.json`. Required fields include a unique kebab-case slug, title, theme, question, status/category, immutable reviewed README URL, source commit, notebook/Book/Lab paths, attribution and runtime limitations. `category` is `jupyterlite` for prefixed projects or `related` for browser projects with explicit README evidence. Preserve **exact** source URLs and case. Record status/date without calling an HTTP 200 a functional guarantee. If no launcher is documented, use an empty resources list and a source-only explanation.
3. Run `python scripts/generate.py`. It creates navigation and any missing project notebook. Unknown projects get an explicit incomplete scaffold. **Existing notebooks are never overwritten**, including manual edits and executed outputs. `scripts/lesson_material.py` contains initial seeding material, not a live replacement for canonical notebooks. Edit the new notebook directly and remove its `metadata.atlas.scaffold` flag only after the chapter is complete.
4. Author a distinct domain-specific exercise with a learning question, explained computation, generated visual and printed text alternative, interpretation, extension, exact source citation and continuation limits. Use stdlib and IPython display only, small deterministic fixtures, no installs/network/credentials. Label synthetic data or actual metadata accurately. Keep precise sensitive locations and health records out of source, output, screenshots, URLs and model contexts.
5. Run `python scripts/make_assets.py` after changing theme counts, then `python scripts/generate.py` to copy assets. Review `assets/PROVENANCE.md`. Add citations to `REFERENCES.md` and synchronize the narrative-only `content/references.ipynb` if that page changes. Similarly synchronize the contributor notebook when this guide changes; generator preserves it by design.
6. Execute changed notebooks, run validation/build/browser checks, and update `VALIDATION.md` with actual results and limits. Review canonical outputs and catalog diffs. The validation fails on omitted public prefixed projects, duplicates, missing notebooks, incomplete scaffolds, path mismatches and unsupported imports.

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
# Or: python scripts/test_browser.py --browser-executable "C:/Program Files/Google/Chrome/Application/chrome.exe"
```

Execution uses a fresh temporary working directory per notebook, blocks Python-level data-service calls and audits imports. It is a reproducibility check, not proof of health validity. Browser checks exercise search, filters, empty/reset states, related-project separation, mobile overflow and local 2D/3D controls. The separate `python scripts/check_runtime.py` check creates a fresh browser context, explicitly selects Python/Pyodide, runs the canonical fitted-ML code, and requires a unique newly printed marker plus its SVG output. CI requires this check; a loaded Lab shell is insufficient. Use `--browser-executable "path/to/chrome"` for an installed Chrome/Chromium on any platform, or omit it for Playwright's Chromium. Initial runtime downloads need network; failures identify an unavailable kernel/runtime instead of claiming a pass.

The Lite build locates Pyodide assets through the installed `jupyterlite-pyodide-kernel` distribution metadata, including user-site installations. It copies only that extension into `_build/lite-project/extensions/`, disables unrelated environment-extension discovery, copies the custom app/storage configuration into that isolated project, and uses `--force` so stale task state cannot skip configuration patches after output cleanup. Built validation requires the kernel's metadata/JavaScript assets and all four custom app/storage values. See the official [configuration files](https://jupyterlite.readthedocs.io/en/stable/howto/configure/config_files.html) and [advanced extension](https://jupyterlite.readthedocs.io/en/stable/howto/configure/advanced/extensions.html) documentation.

Native WhiteboxTools, GDAL/Rasterio stacks, RustGIS Python and GPU/model services require their source's supported local/server environment. Begin with one tiny public/synthetic fixture, a five-minute trial and a memory/cost budget. An optional live model needs approved data flow and server-managed secrets; never embed long-lived keys in browser notebooks.

## Publish with GitHub Pages

The included `.github/workflows/pages.yml` validates pull requests and deploys successful builds on pushes to `main` (or a manual run on `main`). In GitHub **Settings → Pages → Build and deployment → Source**, choose **GitHub Actions**. The workflow needs Pages/write and OIDC permissions only in its deploy job. Consult the [repository workflow status](https://github.com/jltobias/JupyterLite-Index-Repo/actions/workflows/pages.yml) to confirm that a revision has passed validation and deployed successfully. Existing source-project availability is recorded independently.

## Sources for the build architecture

[Jupyter Book v1](https://jupyter-book.readthedocs.io/v1/intro.html), [JupyterLite content](https://jupyterlite.readthedocs.io/en/stable/howto/content/files.html), [JupyterLite deployment](https://jupyterlite.readthedocs.io/en/stable/howto/deployment/index.html), [Pyodide](https://pyodide.org/en/stable/), [GitHub Pages Actions](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages). These tools retain their own licenses and transitive notices.
