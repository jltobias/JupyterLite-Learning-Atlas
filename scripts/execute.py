"""Execute original companions and explicitly selected local source lessons."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from atlas_paths import canonical_notebooks
from source_library import load_library, source_sections, stage_dependencies

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "_build/execution-work"
RUNTIME = ROOT / "_build/jupyter-runtime"
# Jupyter's own sockets are already connected when this cell runs. Block only
# Python-level data-service connections; the notebooks also pass an AST audit.
GUARD = '''import socket, urllib.request
def _atlas_block_network(*args, **kwargs):
    raise RuntimeError("Data-service networking disabled during atlas verification")
socket.create_connection = _atlas_block_network
urllib.request.urlopen = _atlas_block_network
'''


def main():
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="save executed outputs in canonical notebooks")
    parser.add_argument("--source-only", action="store_true", help="verify only the selected source subset")
    args = parser.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    RUNTIME.mkdir(parents=True, exist_ok=True)
    os.environ["JUPYTER_RUNTIME_DIR"] = str(RUNTIME)
    results = []
    library=load_library();sections=source_sections(library)
    for path in canonical_notebooks():
        relative=path.relative_to(ROOT/'content').as_posix();section=sections.get(relative)
        if section and not section['runtime']['execution_selected']:
            results.append({'path':'content/'+relative,'status':'skipped','runtime':section['runtime']['class'],'reason':' '.join(section['runtime']['requirements'])+' Not in the explicitly selected execution subset.'})
            continue
        if args.source_only and not section:continue
        original = nbformat.read(path, as_version=4)
        if not any(c.cell_type == "code" for c in original.cells):
            results.append({"path":path.relative_to(ROOT).as_posix(),"status":"narrative"})
            continue
        runnable = nbformat.from_dict(original)
        runnable.cells.insert(0, nbformat.v4.new_code_cell(GUARD))
        with tempfile.TemporaryDirectory(prefix="atlas-notebook-", dir=WORK) as folder:
            cwd=stage_dependencies(relative,folder,library)
            executed = NotebookClient(runnable, timeout=120 if section else 60, kernel_name="python3", resources={"metadata":{"path":str(cwd)}}, allow_errors=False).execute()
        executed.cells.pop(0)
        for cell in executed.cells:
            if cell.cell_type == "code" and cell.execution_count is not None:
                cell.execution_count -= 1
        if args.write:
            nbformat.write(executed, path)
        results.append({"path":path.relative_to(ROOT).as_posix(),"status":"passed","code_cells":sum(c.cell_type=="code" for c in executed.cells),"source_sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
        print("PASS", path.relative_to(ROOT).as_posix(), flush=True)
    output = ROOT / "_build"
    output.mkdir(exist_ok=True)
    (output / "execution-results.json").write_text(json.dumps({"network":"Python data-service connections blocked; fresh temporary working directory per notebook", "results":results}, indent=2)+"\n",encoding="utf-8")
    if args.write:
        source_results=[r for r in results if r['path'].removeprefix('content/') in sections]
        receipt={'verification':'Fresh native Python kernels; not browser/Pyodide certification','network':'Python data-service connection guard; explicitly selected local lessons only','results':source_results}
        (ROOT/'catalog/source-execution.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    from collections import Counter
    print(f"Accounted for {len(results)} notebooks: {dict(Counter(r['status'] for r in results))}.")


if __name__ == "__main__":
    main()
