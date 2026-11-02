"""Meaningful static-app behavior checks under the real GitHub project subpath."""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import nbformat
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:8766/JupyterLite-Learning-Atlas/'


def check_coral(page, browser, records, output, checks):
    """Keep reef discovery, evidence links and rendered accessibility in the public gate."""
    record=next(r for r in records if r['slug']=='coral-reef-one-health')
    page.goto(BASE)
    earth=page.locator('a.path').filter(has=page.get_by_role('heading',name='Observe a changing Earth',exact=True))
    assert earth.get_attribute('href')=='book/index.html#observe-a-changing-earth'
    earth.click()
    route=page.locator('#observe-a-changing-earth')
    route.wait_for()
    assert route.locator('a[href="projects/coral-reef-one-health/index.html"]').count()==1
    checks.append('Earth route links to the Book path containing Coral')

    page.goto(BASE+'explore/');page.locator('#projects article').first.wait_for()
    page.locator('#theme').select_option(record['theme'])
    for provider in ['CoralNet','MERMAID','OBIS','Allen','Millennium']:
        page.locator('#query').fill(provider)
        card=page.locator('.resource[data-slug="coral-reef-one-health"]')
        assert card.is_visible(),provider+' must discover Coral'
        assert page.locator('#query').evaluate('(e)=>e===document.activeElement')
        assert page.locator('#theme').input_value()==record['theme']
        assert parse_qs(urlsplit(page.url).query)['q']==[provider]
        card.locator('summary').click()
        assert card.locator('details').evaluate('(e)=>e.open')
        for resource in record['resources']:
            assert card.locator(f'a[href="{resource["url"]}"]').is_visible()
        assert card.locator(f'a[href="{record["readme_url"]}"]').is_visible()
    page.screenshot(path=str(output/'coral-explorer.png'),full_page=True)
    checks.append('Coral provider/attribution searches preserve focus, filters, URL state and visible source disclosures')

    response=page.goto(BASE+record['book_path']);assert response and response.status==200
    run=page.get_by_role('link',name='Run this notebook in Lab');run.wait_for()
    assert run.get_attribute('href')=='/JupyterLite-Learning-Atlas/lite/lab/index.html?path=projects%2Fcoral-reef-one-health%2Findex.ipynb'
    for filename in ['01-reef-mapping.ipynb','02-one-health.ipynb']:
        pinned=f'{record["source_url"]}/blob/{record["source_commit"]}/content/{filename}'
        source_lab='https://jltobias.github.io/JupyterLite-Coral-Reef-One-Health/lite/lab/index.html?path='+filename
        assert page.locator(f'a[href="{pinned}"]').count()>=1
        assert page.locator(f'a[href="{source_lab}"]').count()>=1
    for url in [record['readme_url'],'https://doi.org/10.1016/j.jip.2021.107538',
                'https://allencoralatlas.org/methods/','https://allencoralatlas.org/tou/',
                'https://www.livingoceansfoundation.org/mapping-the-worlds-coral-reefs/',
                'https://landsat.gsfc.nasa.gov/wp-content/uploads/2012/07/coral-l7.pdf',
                'https://www.who.int/health-topics/one-health',
                'https://github.com/luismmontilla/awesome-coral-research/blob/master/LICENCE.md',
                *[r['url'] for r in record['resources'][5:]]]:
        assert page.locator(f'a[href="{url}"]').count()>=1,url
    page.screenshot(path=str(output/'coral-book-desktop.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    page.wait_for_function('document.documentElement.scrollWidth<=innerWidth+2',timeout=10000)
    page.screenshot(path=str(output/'coral-book-mobile.png'),full_page=True)
    page.set_viewport_size({'width':1440,'height':1000})
    notebook=nbformat.read(ROOT/'content'/record['notebook'],as_version=4)
    figures=[o.data['image/svg+xml'] for c in notebook.cells if c.cell_type=='code'
             for o in c.outputs if 'image/svg+xml' in o.get('data',{})]
    assert figures,'Expected executed Coral SVG'
    # The Book theme retains its live DOM; a separate, clean page owns SVG layout checks.
    figure_page=browser.new_page(viewport={'width':1440,'height':1000})
    try:
        for i,figure in enumerate(figures):
            figure_page.set_content(figure)
            clipped=figure_page.locator('svg').evaluate('''s=>{const v=s.viewBox.baseVal;return [...s.querySelectorAll('text')].filter(t=>{const b=t.getBBox();return b.x<0||b.y<0||b.x+b.width>v.width||b.y+b.height>v.height}).map(t=>t.textContent)}''')
            assert not clipped,clipped
            figure_page.screenshot(path=str(output/f'coral-figure-{i}.png'))
    finally:figure_page.close()
    checks.append('Coral source/pinned notebooks, primary citations, Book-to-Lab handoff, mobile width and SVG clipping')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--browser-executable');args=parser.parse_args()
    output=ROOT/'_build/browser';output.mkdir(parents=True,exist_ok=True)
    records=json.loads((ROOT/'catalog/repositories.json').read_text(encoding='utf-8'))['repositories']
    total=len(records)
    counts={category:sum(r['category']==category for r in records) for category in ['jupyterlite','related']}
    log=(output/'server.log').open('w',encoding='utf-8')
    server=subprocess.Popen([sys.executable,'scripts/serve.py','--port','8766'],cwd=ROOT,stdout=log,stderr=log)
    checks=[]
    try:
        for _ in range(40):
            try:urllib.request.urlopen(BASE,timeout=1).close();break
            except OSError:time.sleep(.25)
        else:raise RuntimeError('Preview server did not start')
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,executable_path=args.browser_executable)
            page=browser.new_page(viewport={'width':1440,'height':1000})
            errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
            page.goto(BASE);page.locator('h1').wait_for();assert 'A browser.' in page.locator('h1').inner_text()
            page.screenshot(path=str(output/'hub-desktop.png'),full_page=True)
            checks.append('hub loads under project subpath')
            page.goto(BASE+'explore/');page.locator('#projects article').first.wait_for()
            assert page.locator('#projects article').count()==counts['jupyterlite']
            assert page.locator('#related article').count()==counts['related']
            source_record=next(r for r in records if r['resources'])
            page.locator('#query').fill(source_record['name'])
            details=page.locator(f'.resource[data-slug="{source_record["slug"]}"] details')
            details.locator('summary').click()
            assert details.evaluate('(element)=>element.open'),'First summary click after typing must open source details'
            source_links=details.locator('a')
            assert source_links.count()==len(source_record['resources'])+2
            assert all(anchor.is_visible() for anchor in source_links.all())
            checks.append('one source-summary click immediately after a catalog-derived repository search opens visible source links')
            page.locator('#query').fill('privacy')
            assert 0<page.locator('.resource').count()<total
            page.locator('#query').fill('no-such-topic-zzzzz')
            assert page.locator('#empty').is_visible()
            page.locator('#empty-reset').click();page.wait_for_function("n=>document.querySelectorAll('.resource').length===n",arg=total)
            assert page.locator('#query').evaluate('(e)=>e===document.activeElement')
            page.locator('#kind').select_option('scene-3d')
            assert page.locator('.resource').count()>0
            for d in page.locator('.resource details').all():
                d.locator('summary').click()
                assert d.locator('a').count()>=3
            page.locator('#reset').click();page.wait_for_function("n=>document.querySelectorAll('.resource').length===n",arg=total)
            page.locator('#status').select_option('revised variant')
            assert page.locator('.resource').count()==sum(r['status']=='revised variant' for r in records)
            page.goto(BASE+'explore/?theme=Global%20health');page.locator('#projects article').first.wait_for()
            assert page.locator('#theme').input_value()=='Global health'
            for section,category in [('projects','jupyterlite'),('related','related')]:
                actual=set(page.locator(f'#{section} article').evaluate_all('(cards)=>cards.map(c=>c.dataset.slug)'))
                expected={r['slug'] for r in records if r['theme']=='Global health' and r['category']==category}
                assert actual==expected,(section,actual,expected)
            checks.append('search, theme/type/status filters, URL state, empty state, reset/focus, source disclosure, related separation')
            check_coral(page,browser,records,output,checks)
            page.goto(BASE+'teach/');page.locator('#teaching-table tr').first.wait_for()
            assert page.locator('#teaching-table tr').count()==16
            before=page.locator('#view-summary').inner_text()
            page.locator('#water').focus()
            for _ in range(4):page.keyboard.press('ArrowRight')
            assert page.locator('#view-summary').inner_text()!=before
            assert page.locator('#teaching-table').inner_text().count('Yes')==6
            summary=page.locator('#view-summary').inner_text()
            assert '6 of 16 cells' in summary and '84 of 227 invented demand units (37%)' in summary,summary
            page.locator('#mode').select_option('3d-map')
            assert page.locator('#view polygon').count()>60
            old=page.locator('#view polygon').first.get_attribute('points')
            page.locator('#rotation').focus();page.keyboard.press('ArrowRight')
            assert page.locator('#view polygon').first.get_attribute('points')!=old
            page.locator('#mode').select_option('3d-scene')
            assert 'connectivity' in page.locator('#view-explanation').inner_text()
            page.screenshot(path=str(output/'teaching-3d.png'),full_page=True)
            checks.append('2D/3D-map/3D-scene controls, water summary/table parity, keyboard camera rotation')
            for route,notebook in [('book/','index.ipynb'),('book/projects/rewiring-global-health/','projects%2Frewiring-global-health%2Findex.ipynb'),('book/projects/rewiring-global-health/index.html','projects%2Frewiring-global-health%2Findex.ipynb')]:
                page.goto(BASE+route)
                run=page.get_by_role('link',name='Run this notebook in Lab')
                run.wait_for()
                assert run.get_attribute('href')=='/JupyterLite-Learning-Atlas/lite/lab/index.html?path='+notebook
            checks.append('Book root, directory alias and explicit project Book-to-Lab handoffs preserve the project subpath')
            for suffix in ['','explore/','teach/','about/','book/index.html','lite/lab/index.html']:
                response=page.goto(BASE+suffix);assert response and response.status==200,suffix
            page.set_viewport_size({'width':390,'height':844})
            for suffix in ['','explore/','teach/','about/']:
                page.goto(BASE+suffix)
                if suffix=='explore/':page.locator('#projects article').first.wait_for()
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),suffix+' horizontal overflow'
            page.goto(BASE);page.screenshot(path=str(output/'hub-mobile.png'),full_page=True)
            assert not errors,errors
            checks.append('six entry responses, mobile 390px overflow and no app JavaScript errors')
            browser.close()
    finally:
        server.terminate();server.wait(timeout=10);log.close()
    (output/'results.json').write_text(json.dumps({'checks':checks,'limits':'Does not prove real Pyodide kernel execution, external source runtime functionality or publication.'},indent=2)+'\n',encoding='utf-8')
    for check in checks:print('PASS',check)


if __name__=='__main__':main()
