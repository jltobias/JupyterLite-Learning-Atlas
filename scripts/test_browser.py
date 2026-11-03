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
from phi_case_material import CASES as PHI_CASES
from eo_material import FILES as EO_FILES, PIN as EO_PIN

ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:8766/JupyterLite-Learning-Atlas/'


def check_mobile_book_width(page, label):
    """Keep failure evidence useful across browser engines and build hosts."""
    try:
        page.wait_for_function('document.documentElement.scrollWidth<=innerWidth+2',timeout=10000)
    except Exception:
        layout=page.evaluate('''()=>({url:location.href,width:innerWidth,scroll:document.documentElement.scrollWidth,
          styles:[...document.styleSheets].map(s=>s.href),
          blocks:[...document.querySelectorAll('main,article,.bd-main,.bd-content,.bd-article-container,.cell_output,table,img,svg,pre')]
            .map(e=>({tag:e.tagName,cls:String(e.className),width:e.getBoundingClientRect().width,right:e.getBoundingClientRect().right,scroll:e.scrollWidth,overflow:getComputedStyle(e).overflowX,text:e.textContent.slice(0,100)}))
            .filter(e=>e.right>innerWidth+2||e.scroll>e.width+2).slice(0,35)})''')
        print('BOOK_MOBILE_LAYOUT '+json.dumps({'label':label,**layout}),flush=True)
        page.screenshot(path=str(ROOT/'_build/browser'/('failure-'+label+'-mobile.png')),full_page=True)
        raise


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
    check_mobile_book_width(page,'coral')
    # A nested Sphinx span.pre used to defeat wrapping on Linux font metrics.
    stress=page.add_style_tag(content='.bd-article :not(pre)>code {font-size:16px!important;font-family:monospace!important}')
    check_mobile_book_width(page,'coral-inline-code-stress')
    stress.evaluate('(element)=>element.remove()')
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


def check_phi_cases(page, browser, records, output, checks):
    """Assert public learning order, source disclosures, handoffs and actual figures."""
    page.goto(BASE+'book/index.html')
    navigation=page.locator('nav.bd-links .toctree-l1 > a.reference.internal')
    navigation.first.wait_for()
    links=navigation.evaluate_all('(links)=>links.map(link=>link.getAttribute("href"))')
    assert links[:2]==['foundations/browser-python.html','projects/cholera-1854-basic/index.html'],links[:2]
    for slug in PHI_CASES:
        assert links.count(f'projects/{slug}/index.html')==1,slug
    assert [link for link in links if any('/'+slug+'/' in link for slug in PHI_CASES)]==[
        f'projects/{slug}/index.html' for slug in PHI_CASES]
    page.goto(BASE+'explore/?q=PHI-Case-Studies')
    page.locator('#related article').first.wait_for()
    assert page.locator('#projects article').count()==0
    assert set(page.locator('#related article').evaluate_all('(cards)=>cards.map(card=>card.dataset.slug)'))==set(PHI_CASES)
    for slug, case in PHI_CASES.items():
        record=next(r for r in records if r['slug']==slug)
        card=page.locator(f'.resource[data-slug="{slug}"]')
        card.locator('summary').click()
        assert card.locator('details').evaluate('(element)=>element.open')
        assert card.locator(f'a[href="{record["readme_url"]}"]').is_visible()
        for resource in record['resources']:
            assert card.locator(f'a[href="{resource["url"]}"]').is_visible()
    checks.append('PHI Basic second after browser Python; ordered investigations each once; four external explorer cards and source disclosures')

    figure_page=browser.new_page(viewport={'width':1440,'height':1000})
    try:
        for slug, case in PHI_CASES.items():
            record=next(r for r in records if r['slug']==slug)
            response=page.goto(BASE+record['book_path']);assert response and response.status==200
            article=page.locator('article.bd-article')
            run=page.get_by_role('link',name='Run this notebook in Lab');run.wait_for()
            assert run.get_attribute('href')==f'/JupyterLite-Learning-Atlas/lite/lab/index.html?path=projects%2F{slug}%2Findex.ipynb'
            for path, _ in case['files']:
                pinned=f'{record["source_url"]}/blob/{case["commit"]}/{path}'
                assert article.locator(f'a[href="{pinned}"]').count()>=1,pinned
            for resource in record['resources']:
                assert article.locator(f'a[href="{resource["url"]}"]').count()>=1,resource['url']
            for other in PHI_CASES:
                if other!=slug:
                    assert article.locator(f'a[href="../{other}/index.html"]').count()>=1,(slug,other)
            assert 'synthetic' in article.inner_text().lower()
            expected_states = ['tie', 'outside'] if slug == 'cholera-1854-advanced-2' else ['unknown']
            assert all(state in article.inner_text().lower() for state in expected_states),slug
            assert article.locator('.cell_output img, .cell_output svg').count()>=1,slug
            page.screenshot(path=str(output/(slug+'-book-desktop.png')),full_page=True)
            page.set_viewport_size({'width':390,'height':844})
            check_mobile_book_width(page,slug)
            page.screenshot(path=str(output/(slug+'-book-mobile.png')),full_page=True)
            page.set_viewport_size({'width':1440,'height':1000})
            notebook=nbformat.read(ROOT/'content'/record['notebook'],as_version=4)
            figures=[o.data['image/svg+xml'] for c in notebook.cells if c.cell_type=='code'
                     for o in c.outputs if 'image/svg+xml' in o.get('data',{})]
            assert figures,'Expected executed '+slug+' SVG'
            for i,figure in enumerate(figures):
                figure_page.set_content(figure)
                assert figure_page.locator('svg title').text_content()
                assert figure_page.locator('svg desc').text_content()
                clipped=figure_page.locator('svg').evaluate('''s=>{const v=s.viewBox.baseVal;return [...s.querySelectorAll('text')].filter(t=>{const b=t.getBBox();return b.x<0||b.y<0||b.x+b.width>v.width||b.y+b.height>v.height}).map(t=>t.textContent)}''')
                assert not clipped,(slug,clipped)
                figure_page.screenshot(path=str(output/f'{slug}-figure-{i}.png'))
    finally:
        figure_page.close()
    checks.append('Four PHI Book routes, 20 pinned source notebooks, 13 launch resources, reciprocal links, Lab handoffs, mobile width and unclipped accessible SVGs')


def check_eo(page, browser, records, output, checks):
    """Require the actual shared cover, EO discovery, reciprocal links and figure."""
    record=next(r for r in records if r['slug']=='eo-satellite-guide')
    page.goto(BASE+'book/index.html')
    article=page.locator('article.bd-article')
    cover=article.locator('img[src*="splash-v2.png"]')
    cover.wait_for()
    page.wait_for_function("image=>image.complete&&image.naturalWidth===1774&&image.naturalHeight===887",arg=cover.element_handle())
    assert cover.get_attribute('alt')=='The JupyterLite Learning Atlas: an open notebook becomes a coastal landscape and coral reef, with an Earth globe, satellite and people learning together.'
    assert article.locator('a[href="https://github.com/jltobias/JupyterLite-Learning-Atlas/blob/main/assets/SPLASH-PROVENANCE.md"]').count()==1
    assert article.locator('a[href="projects/eo-satellite-guide/index.html"]').count()==1
    page.screenshot(path=str(output/'opening-book-cover.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    check_mobile_book_width(page,'opening-cover')
    page.screenshot(path=str(output/'opening-book-cover-mobile.png'),full_page=True)
    page.set_viewport_size({'width':1440,'height':1000})

    context=browser.new_context(viewport={'width':1440,'height':1000})
    try:
        lab=context.new_page()
        response=lab.goto(BASE+'lite/lab/index.html?path=index.ipynb',wait_until='domcontentloaded')
        assert response and response.status==200
        lab.locator('.jp-Notebook').wait_for(timeout=90000)
        # JupyterLite resolves bundled Markdown images to data URLs.
        lab_cover=lab.get_by_role('img',name=cover.get_attribute('alt'),exact=True)
        lab_cover.wait_for(timeout=30000)
        lab.wait_for_function("image=>image.complete&&image.naturalWidth===1774&&image.naturalHeight===887",arg=lab_cover.element_handle())
        displayed_hash=lab_cover.evaluate("""async image=>{
            const bytes=await (await fetch(image.currentSrc||image.src)).arrayBuffer();
            const digest=await crypto.subtle.digest('SHA-256',bytes);
            return [...new Uint8Array(digest)].map(value=>value.toString(16).padStart(2,'0')).join('');
        }""")
        assert displayed_hash=='09b30e50095b2286df7ea0a1556fd447d1124c83b3ab5dfc68fab4c29877b0f9'
        assert 'open notebook becomes a coastal landscape' in lab_cover.get_attribute('alt')
        lab.screenshot(path=str(output/'opening-lab-cover.png'))
    finally:
        context.close()
    checks.append('Same 1774×887 README PNG actually loads in opening Book and fresh Lab, with alt/credit and mobile Book width')

    page.goto(BASE+'explore/')
    page.locator('#projects article').first.wait_for()
    page.locator('#theme').select_option(record['theme'])
    for query in ['EO Satellite Guide','EarthCODE']:
        page.locator('#query').fill(query)
        card=page.locator('.resource[data-slug="eo-satellite-guide"]')
        assert card.is_visible(),query
        assert page.locator('#query').evaluate('(element)=>element===document.activeElement')
        assert parse_qs(urlsplit(page.url).query)['q']==[query]
        card.locator('summary').click()
        assert card.locator('details').evaluate('(element)=>element.open')
        for resource in record['resources']:
            assert card.locator(f'a[href="{resource["url"]}"]').is_visible()
        assert card.locator(f'a[href="{record["readme_url"]}"]').is_visible()
    page.screenshot(path=str(output/'eo-earthcode-explorer.png'),full_page=True)

    response=page.goto(BASE+record['book_path']);assert response and response.status==200
    article=page.locator('article.bd-article')
    run=page.get_by_role('link',name='Run this notebook in Lab');run.wait_for()
    assert run.get_attribute('href')=='/JupyterLite-Learning-Atlas/lite/lab/index.html?path=projects%2Feo-satellite-guide%2Findex.ipynb'
    for filename,_ in EO_FILES:
        assert article.locator(f'a[href="{EO_PIN}notebooks/{filename}"]').count()>=1
    for resource in record['resources']:
        assert article.locator(f'a[href="{resource["url"]}"]').count()>=1
    for url in ['https://www.w3.org/TR/vocab-ssn/','https://www.w3.org/TR/vocab-dcat-3/',
                'https://www.w3.org/TR/prov-o/','https://www.naturalearthdata.com/about/terms-of-use/',
                'https://github.com/radiantearth/stac-api-spec/blob/v1.0.0/item-search/README.md']:
        assert article.locator(f'a[href="{url}"]').count()>=1,url
    assert article.locator('a[href="../stac-browser/index.html"]').count()>=1
    assert 'OGC API Records' in article.inner_text()
    assert article.locator('.cell_output img, .cell_output svg').count()>=1
    page.screenshot(path=str(output/'eo-book-desktop.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844})
    check_mobile_book_width(page,'eo')
    page.screenshot(path=str(output/'eo-book-mobile.png'),full_page=True)
    page.set_viewport_size({'width':1440,'height':1000})
    page.goto(BASE+'book/projects/stac-browser/index.html')
    assert page.locator('article.bd-article a[href="../eo-satellite-guide/index.html"]').count()==1

    notebook=nbformat.read(ROOT/'content'/record['notebook'],as_version=4)
    figures=[o.data['image/svg+xml'] for c in notebook.cells if c.cell_type=='code'
             for o in c.outputs if 'image/svg+xml' in o.get('data',{})]
    assert len(figures)==1,'Expected executed EO route figure'
    figure_page=browser.new_page(viewport={'width':1440,'height':1000})
    try:
        figure_page.set_content(figures[0])
        assert figure_page.locator('svg[role="img"][aria-label] title').text_content()
        assert 'unknown (None)' in figure_page.locator('svg desc').text_content()
        assert figure_page.locator('svg g[data-route]').count()==5
        assert figure_page.locator('svg g[data-route="draft"] .route-mark').get_attribute('x')=='440'
        clipped=figure_page.locator('svg').evaluate('''s=>{const v=s.viewBox.baseVal;return [...s.querySelectorAll('text')].filter(t=>{const b=t.getBBox();return b.x<0||b.y<0||b.x+b.width>v.width||b.y+b.height>v.height}).map(t=>t.textContent)}''')
        assert not clipped,clipped
        figure_page.screenshot(path=str(output/'eo-route-figure.png'))
    finally:
        figure_page.close()
    checks.append('EO/EarthCODE explorer, six pinned source lessons, ten resources, primary citations, reciprocal STAC links, Lab handoff, mobile width and actual unclipped route SVG')


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
            check_phi_cases(page,browser,records,output,checks)
            check_eo(page,browser,records,output,checks)
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
