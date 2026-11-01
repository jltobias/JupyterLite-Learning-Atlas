"""Require a fresh real Pyodide execution, not saved outputs or a loaded Lab shell."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.request
import uuid
from pathlib import Path

import nbformat
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
NOTEBOOK='foundations/learning-a-model.ipynb'


def select_python(page, timeout_ms):
    """Explicitly choose Python; never accept the dialog's No Kernel default."""
    dialog=page.get_by_role('dialog').filter(has_text='Select Kernel')
    python_running=page.locator('.jp-KernelName').filter(has_text=re.compile(r'Python|Pyodide',re.I))
    if python_running.count() and not dialog.is_visible():
        return
    try:
        dialog.wait_for(state='visible',timeout=5000)
    except Exception:
        # A single matching kernel may start automatically without any dialog.
        if page.locator('.jp-KernelName').filter(has_text=re.compile(r'Python|Pyodide',re.I)).count():
            return
        selector=page.get_by_role('button',name=re.compile(r'No Kernel|Select Kernel',re.I))
        if not selector.count():
            # The unique marker and SVG below remain the required proof.
            return
        selector.first.click()
        dialog.wait_for(state='visible',timeout=15000)
    select=dialog.locator('select').first
    select.wait_for(timeout=15000)
    page.wait_for_function("""()=>Array.from(document.querySelectorAll('.jp-Dialog select option')).some(o=>/python|pyodide/i.test(o.textContent))""",timeout=timeout_ms)
    options=select.locator('option').evaluate_all('(options)=>options.map(o=>({value:o.value,label:o.textContent}))')
    python=next((o for o in options if re.search(r'python|pyodide',o['label'],re.I)),None)
    if python is None:raise RuntimeError(f'Python/Pyodide is unavailable. Kernel options: {options}')
    select.select_option(python['value'])
    dialog.get_by_role('button',name='Select',exact=True).click()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--browser-executable',help='Optional installed Chromium/Chrome; otherwise use Playwright Chromium')
    parser.add_argument('--timeout',type=int,default=240,help='Runtime download/execution timeout in seconds')
    args=parser.parse_args()
    output=ROOT/'_build/runtime-browser';output.mkdir(parents=True,exist_ok=True)
    base='http://127.0.0.1:8767/JupyterLite-Index-Repo/'
    log=(output/'server.log').open('w',encoding='utf-8')
    server=subprocess.Popen([sys.executable,'scripts/serve.py','--port','8767'],cwd=ROOT,stdout=log,stderr=log)
    try:
        for _ in range(50):
            try:urllib.request.urlopen(base,timeout=1).close();break
            except OSError:time.sleep(.2)
        else:raise RuntimeError('Local atlas preview did not start')
        notebook=nbformat.read(ROOT/'content'/NOTEBOOK,as_version=4)
        marker='ATLAS_PYODIDE_PROOF_'+uuid.uuid4().hex
        source='\n\n'.join(c.source for c in notebook.cells if c.cell_type=='code')
        source+=f'\nprint({marker!r}, round(metrics["East held-out MAE"], 3))\n'
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(headless=True,executable_path=args.browser_executable)
            context=browser.new_context(viewport={'width':1440,'height':1000})
            page=context.new_page();errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            try:
                page.goto(base+'lite/lab/index.html?path='+NOTEBOOK,wait_until='domcontentloaded')
                page.locator('.jp-Notebook').wait_for(timeout=args.timeout*1000)
                try:select_python(page,args.timeout*1000)
                except Exception as exc:
                    raise RuntimeError('Python/Pyodide kernel unavailable: check federated kernel metadata/assets and runtime download access; No Kernel is not a pass.') from exc
                editor=page.locator('.jp-Notebook .jp-CodeCell .cm-content').first
                editor.wait_for(timeout=30000);editor.click()
                # Playwright's platform-aware modifier supports Linux/macOS/Windows.
                page.keyboard.press('ControlOrMeta+a');page.keyboard.insert_text(source)
                page.keyboard.press('Shift+Enter')
                first_cell=page.locator('.jp-Notebook .jp-CodeCell').first
                proof=first_cell.locator('.jp-OutputArea-output').filter(has_text=marker)
                proof.wait_for(timeout=args.timeout*1000)
                text=proof.inner_text()
                if '7.686' not in text:raise AssertionError(f'Unexpected canonical default ML result: {text}')
                # JupyterLab can render SVG MIME output as an image rather than
                # inline SVG. Check the actual loaded SVG in either rendering.
                graphic=first_cell.locator('.jp-OutputArea-output svg, .jp-OutputArea-output img').first
                graphic.wait_for(timeout=30000)
                rendered=graphic.evaluate("""element=>({tag:element.tagName.toLowerCase(),
                    source:element.tagName.toLowerCase()==='svg'
                        ? new XMLSerializer().serializeToString(element) : element.currentSrc||element.src})""")
                if rendered['tag']=='svg':
                    svg_source=rendered['source']
                else:
                    assert rendered['source'].startswith(('data:image/svg+xml','blob:')),'Expected a generated SVG image'
                    svg_source=page.evaluate('url=>fetch(url).then(response=>response.text())',rendered['source'])
                    assert graphic.evaluate('image=>image.complete && image.naturalWidth>0'),'SVG image failed to load'
                assert '<svg' in svg_source and 'Signed residuals, grouped schematically' in svg_source,'Expected canonical ML SVG content'
                assert not first_cell.locator('.jp-OutputArea .jp-mod-error').count(),'Canonical ML execution returned an error'
                assert not errors,errors
                page.screenshot(path=str(output/'executed-ml.png'))
                (output/'results.json').write_text(json.dumps({'status':'passed','notebook':NOTEBOOK,'marker':text,'svg_content_checked':'Signed residuals, grouped schematically','svg_rendering':rendered['tag'],'method':'Fresh browser context, Python kernel, unmodified canonical ML code plus a unique printed marker, and loaded SVG content in the same newly executed cell.','limits':'One complete canonical code sequence; no certification of external companion services.'},indent=2)+'\n',encoding='utf-8')
                print('PASS fresh JupyterLite/Pyodide canonical ML execution, marker and SVG',flush=True)
            except Exception:
                (output/'failure-body.txt').write_text(page.locator('body').inner_text(),encoding='utf-8')
                page.screenshot(path=str(output/'failure.png'))
                raise
            finally:context.close();browser.close()
    finally:server.terminate();server.wait(timeout=10);log.close()


if __name__=='__main__':main()
