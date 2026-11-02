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
CORAL_NOTEBOOK='projects/coral-reef-one-health/index.ipynb'
CORAL_ASSERTIONS='''assert weights == (3.0, 1.0)
assert abs(results['A']['index'] - 0.65) < 1e-12
assert abs(results['B']['index'] - 0.35) < 1e-12
assert results['C']['index'] is None and results['C']['coverage'] == 0.75
assert abs(teaching_index((0.8, 0.2), (1.0, 3.0))['index'] - 0.35) < 1e-12
assert abs(teaching_index((0.2, 0.8), (1.0, 3.0))['index'] - 0.65) < 1e-12
assert abs(teaching_index((0.9, 0), weights)['index'] - 0.675) < 1e-12
assert teaching_index((None, None), weights)['index'] is None
assert teaching_index((None, None), weights)['coverage'] == 0
assert coverage_label(teaching_index((0.9, None), (1000.0, 1.0))) == '<100%'
assert coverage_label(teaching_index((0.9, None), (1.0, 1000.0))) == '>0%'
for bad_weights in [(0, 1), (-1, 1), (float('inf'), 1), (float('nan'), 1)]:
    try:
        teaching_index((0.8, 0.2), bad_weights)
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid weights must stop calculation')'''


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


def execute_case(browser, base, output, timeout, notebook_path, assertions, expected_svg, label, proof_value=None):
    """Require proof and a loaded figure from the actual executed cell, despite Lab windowing."""
    notebook=nbformat.read(ROOT/'content'/notebook_path,as_version=4)
    marker='ATLAS_PYODIDE_PROOF_'+uuid.uuid4().hex
    source='\n\n'.join(c.source for c in notebook.cells if c.cell_type=='code')
    source+='\n'+assertions+f'\nprint({marker!r}'+(', '+proof_value if proof_value else '')+')\n'
    context=browser.new_context(viewport={'width':1440,'height':1000})
    page=context.new_page();errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    try:
        page.goto(base+'lite/lab/index.html?path='+notebook_path,wait_until='domcontentloaded')
        page.locator('.jp-Notebook').wait_for(timeout=timeout*1000)
        try:select_python(page,timeout*1000)
        except Exception as exc:
            raise RuntimeError('Python/Pyodide kernel unavailable: check federated kernel metadata/assets and runtime download access; No Kernel is not a pass.') from exc
        editor=page.locator('.jp-Notebook .jp-CodeCell .cm-content').first
        editor.wait_for(timeout=30000);editor.click()
        page.keyboard.press('ControlOrMeta+a');page.keyboard.insert_text(source)
        assert marker in editor.inner_text()
        page.keyboard.press('ControlOrMeta+Enter')
        proof=page.locator('.jp-Notebook .jp-OutputArea-output').filter(has_text=marker)
        proof.wait_for(state='attached',timeout=timeout*1000)
        proof.scroll_into_view_if_needed()
        text=proof.inner_text();assert marker in text
        cell=proof.locator("xpath=ancestor::div[contains(@class, 'jp-CodeCell')][1]")
        graphic=cell.locator('.jp-OutputArea-output svg, .jp-OutputArea-output img').last
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
        assert '<svg' in svg_source and expected_svg in svg_source,f'Expected canonical {label} SVG content'
        assert not cell.locator('.jp-OutputArea .jp-mod-error').count(),f'Canonical {label} execution returned an error'
        assert not errors,errors
        graphic.scroll_into_view_if_needed()
        page.screenshot(path=str(output/f'executed-{label}.png'))
        print(f'PASS fresh JupyterLite/Pyodide canonical {label} execution, numerical assertions, marker and SVG',flush=True)
        return {'status':'passed','notebook':notebook_path,'marker':text,'numerical_assertions':assertions,
                'svg_content_checked':expected_svg,'svg_rendering':rendered['tag']}
    except Exception:
        (output/f'failure-{label}-body.txt').write_text(page.locator('body').inner_text(),encoding='utf-8')
        page.screenshot(path=str(output/f'failure-{label}.png'))
        raise
    finally:context.close()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--browser-executable',help='Optional installed Chromium/Chrome; otherwise use Playwright Chromium')
    parser.add_argument('--timeout',type=int,default=240,help='Runtime download/execution timeout in seconds')
    args=parser.parse_args()
    output=ROOT/'_build/runtime-browser';output.mkdir(parents=True,exist_ok=True)
    base='http://127.0.0.1:8767/JupyterLite-Learning-Atlas/'
    log=(output/'server.log').open('w',encoding='utf-8')
    server=subprocess.Popen([sys.executable,'scripts/serve.py','--port','8767'],cwd=ROOT,stdout=log,stderr=log)
    try:
        for _ in range(50):
            try:urllib.request.urlopen(base,timeout=1).close();break
            except OSError:time.sleep(.2)
        else:raise RuntimeError('Local atlas preview did not start')
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(headless=True,executable_path=args.browser_executable)
            try:
                results=[execute_case(browser,base,output,args.timeout,NOTEBOOK,
                         'assert round(metrics["East held-out MAE"], 3) == 7.686',
                         'Signed residuals, grouped schematically','ml','round(metrics["East held-out MAE"], 3)'),
                         execute_case(browser,base,output,args.timeout,CORAL_NOTEBOOK,CORAL_ASSERTIONS,
                         'Invented reef descriptors','coral')]
                (output/'results.json').write_text(json.dumps({'status':'passed','cases':results,
                    'method':'Separate fresh browser context per case, Python kernel, canonical code plus numerical assertions and a unique marker; actual loaded SVG from the newly executed cell.',
                    'limits':'Canonical ML and Coral fixtures only; no certification of external companion services.'},indent=2)+'\n',encoding='utf-8')
            finally:browser.close()
    finally:server.terminate();server.wait(timeout=10);log.close()


if __name__=='__main__':main()
