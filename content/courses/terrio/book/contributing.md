# Build, test, and contribute

The editable source notebooks live in `notebooks/`. The book and Lab are built from these same files. Shared helpers are in `notebooks/terrio_lab.py`. `scripts/create_notebooks.py` records the initial authored course and can regenerate the notebooks; running it overwrites source notebook edits, so update the generator as well when intentionally maintaining that workflow.

## Local build

Use Python 3.12. From the repository root:

```sh
python -m venv .venv
# Activate .venv using the command for your shell.
python -m pip install -r requirements.txt
python scripts/fetch_assets.py
python scripts/fetch_notices.py
python scripts/validate.py
python scripts/execute_notebooks.py
python scripts/build.py
python -m http.server 8000 --directory _site
```

Open `http://localhost:8000`. Windows activation is `.venv\Scripts\Activate.ps1`; on macOS/Linux use `source .venv/bin/activate`. The build uses the pinned **Jupyter Book v1 / Sphinx toolchain**, which is in maintenance mode. Do not upgrade to Book v2 without migrating the configuration and testing URL compatibility.

`fetch_assets.py` downloads the exact TerrIO 0.9.0 Pyodide wheel and checks its digest against `lite/wheel-lock.json`. The kernel is intentionally `jupyterlite-pyodide-kernel==0.8.0b0`, the upstream-supported Pyodide 0.29 pairing. Updating only the wheel or only the runtime can break installation.

Plotly, xarray, Narwhals, and packaging wheels are also served locally by the built site, with verified hashes in `lite/support-wheel-lock.json`. This avoids a large PyPI download for each new notebook kernel. Their unmodified wheels retain upstream license notices. The Pyodide runtime and its numerical packages, and Plotly's visualization script inside notebook frames, still require network access on first use.

## Browser verification

```sh
python -m playwright install chromium
python scripts/test_browser.py
```

The browser test serves the built site locally, checks the portal/galleries and runs every chapter through JupyterLite's notebook interface in a real browser. A separate UI smoke check confirms the Lab shell loads. Native execution and browser execution test different runtimes; neither should be claimed based only on a static notebook schema check. If an installed Chrome or Edge is preferred, pass `--channel chrome` or `--channel msedge`.

## GitHub Pages

Commit and push the reviewed files to `main`, then set **Settings → Pages → Build and deployment → Source → GitHub Actions**. The included workflow builds the book and Lab into one Pages artifact, tests them, and deploys only a successful main-branch build. Pull requests build and test without deploying. A manual main-branch workflow run can also publish.

Expected root: `https://jltobias.github.io/JupyterLite-terrio/`. Book: `/book/intro.html`. Lab: `/lite/lab/index.html`. Galleries: `/maps/2d.html`, `/maps/3d.html`, `/maps/scenes.html`. These paths become public only after a successful deployment; a local build does not create a live GitHub Pages website.

## Contribution checklist

- Explain the learning objective, units, coordinate system, uncertainty, and interpretation limits.
- Use original or verifiably reusable data; add provider, version, license, URL, retrieval date, changes, and checksum to the ledger.
- Keep downloads small. Avoid keys, personal data, embedded credentials, or services that require accounts for core exercises.
- Include a static or textual alternative to an interactive graphic.
- Run schema/content checks, native notebook execution, the book/Lite build, and browser tests after material changes.
- Preserve upstream copyright and license notices in redistributed dependency bundles.
