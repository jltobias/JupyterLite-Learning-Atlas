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
from phi_case_material import CASES as PHI_CASES

ROOT=Path(__file__).resolve().parents[1]
NOTEBOOK='foundations/learning-a-model.ipynb'
CORAL_NOTEBOOK='projects/coral-reef-one-health/index.ipynb'
EO_NOTEBOOK='projects/eo-satellite-guide/index.ipynb'
EO_ASSERTIONS='''assert len(candidates) == 5 and len({row['mission'] for row in candidates}) == 4
assert counts == {'draft':1, 'incompatible':2, 'unmapped':1, 'browse-static':1, 'check-api':0}
assert [p['intent']['candidate'] for p in proposals] == ['optical-sr']
assert proposals[0]['simulation'] is True and proposals[0]['status'] == 'proposal-only'
assert proposals[0]['search'] == {'collections':['demo-optical-sr'], 'bbox':[-10,-5,10,5], 'datetime':'2024-06-01T00:00:00Z/2024-06-30T23:59:59Z', 'limit':3}
changed, totals, drafts = discovery_plan(candidates, 'backscatter', 'GRD', bbox, start, end, limit)
assert totals == {'draft':1, 'incompatible':4, 'unmapped':0, 'browse-static':0, 'check-api':0}
assert [p['intent']['candidate'] for p in drafts] == ['radar-grd']
edited = [dict(row) for row in candidates]
edited[0]['item_search'] = False
assert discovery_plan(edited, target_property, target_processing, bbox, start, end, limit)[1]['check-api'] == 1
assert discovery_plan(edited, target_property, target_processing, bbox, start, end, limit)[2] == []
edited[0]['item_search'] = True
edited[0]['collection'] = None
assert discovery_plan(edited, target_property, target_processing, bbox, start, end, limit)[1]['unmapped'] == 2
assert discovery_plan(edited, target_property, target_processing, bbox, start, end, limit)[2] == []
for bad_bbox, bad_start, bad_limit in [([10,-5,-10,5], start, limit), (bbox, '2024-07-01T00:00:00Z', limit), (bbox, '2024-6-1T00:00:00Z', limit), (bbox, start, 0)]:
    try:
        discovery_plan(candidates, target_property, target_processing, bad_bbox, bad_start, end, bad_limit)
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid query edits must stop before draft')'''
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

PHI_RUNTIME = [
    ('cholera-1854-basic', '''assert total == 14 and positive == 5 and len(rows) == 6
assert unweighted == (28/6, 2) and weighted == (30/14, 26/14)
edited = [(name, x, y, 14 if name == 'B3' else count) for name, x, y, count in rows]
assert centres(edited) == (28, unweighted, (156/28, 54/28))
assert centres([(name, x, y, 0) for name, x, y, count in rows])[2] is None''',
     'Synthetic Cholera Basic: dots and centres'),
    ('cholera-1854-advanced-1', '''assert costs == {'S':0, 'A':2, 'B':1, 'C':4, 'D':2, 'E':3, 'U':None}
assert len(reached) == 5 and boundary == ['E']
assert sum(value is not None and value <= 2 for value in costs.values()) == 4
changed = shortest_costs(nodes, [edge for edge in edges if edge[:2] != ('B', 'D')], 'S')
assert changed['E'] == 8 and changed['D'] == 9 and changed['U'] is None
assert sum(value is not None and value <= 3 for value in changed.values()) == 3''',
     'Synthetic Cholera Advanced1: network access'),
    ('cholera-1854-advanced-2', '''assert len(samples) == 35 and len(buildings) == 6
assert grid_counts == {'A':15, 'B':15, 'tie':5, 'outside':0}
assert building_counts == {'A':2, 'B':2, 'tie':1, 'outside':1}
moved = {'A':(1, 1), 'B':(4, 1)}
labels = [nearest_site(point, moved, domain) for point in samples]
assert {label:labels.count(label) for label in ['A','B','tie','outside']} == {'A':15, 'B':20, 'tie':0, 'outside':0}
labels = [nearest_site(point, moved, domain) for point in buildings.values()]
assert {label:labels.count(label) for label in ['A','B','tie','outside']} == {'A':2, 'B':3, 'tie':0, 'outside':1}
labels = [nearest_site(point, pumps, (1, 5, 0, 4)) for point in samples]
assert {label:labels.count(label) for label in ['A','B','tie','outside']} == {'A':10, 'B':10, 'tie':5, 'outside':10}''',
     'Synthetic Cholera Advanced2: sampled nearest sites'),
    ('mdr-tb-thailand-2005', '''assert components == [['A','B','C'], ['D','E'], ['F']] and sizes == [3,2,1]
assert summary == {'mdr':3, 'known':4, 'unknown':2, 'fraction':0.75}
observed = dst.copy()
assert contact_components(dst, contacts, True) == [['A','B','C','D','E'], ['F']]
assert dst == observed
assert dst_summary(dict(dst, C='MDR')) == {'mdr':4, 'known':5, 'unknown':1, 'fraction':0.8}
assert dst_summary(dict.fromkeys(dst)) == {'mdr':0, 'known':0, 'unknown':6, 'fraction':None}''',
     'Synthetic MDR-TB: contacts and observed DST'),
]


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
                for slug, assertions, expected_svg in PHI_RUNTIME:
                    assert slug in PHI_CASES
                    results.append(execute_case(browser,base,output,args.timeout,
                        f'projects/{slug}/index.ipynb',assertions,expected_svg,slug))
                results.append(execute_case(browser,base,output,args.timeout,EO_NOTEBOOK,EO_ASSERTIONS,
                    'Fictional capability → discovery routes','eo'))
                (output/'results.json').write_text(json.dumps({'status':'passed','cases':results,
                    'method':'Separate fresh browser context per case, Python kernel, canonical code plus numerical assertions and a unique marker; actual loaded SVG from the newly executed cell.',
                    'limits':'Canonical ML, Coral, four original PHI fixtures and original EO proposal fixture only; no certification of external companion services.'},indent=2)+'\n',encoding='utf-8')
            finally:browser.close()
    finally:server.terminate();server.wait(timeout=10);log.close()


if __name__=='__main__':main()
