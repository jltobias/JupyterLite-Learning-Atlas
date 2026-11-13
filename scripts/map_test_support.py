"""Allowlisted source fixture for the map studio; no assembled Book needed."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
from prepare_maps import COURSE_INPUTS

ROOT = Path(__file__).resolve().parents[1]
PREFIX = '/JupyterLite-Learning-Atlas/'


def source_route(route):
    url = urlsplit(route.request.url)
    if url.hostname != 'atlas.test':
        route.fulfill(status=404, body='External requests disabled in source fixture')
        return
    relative = unquote(url.path)
    relative = relative[len(PREFIX):] if relative.startswith(PREFIX) else relative.lstrip('/')
    if relative.startswith('book/courses/'):
        support = relative[len('book/courses/'):]
        path = ROOT / 'content/courses' / support if support in COURSE_INPUTS else ROOT / '__not_allowed__'
    elif relative.startswith('assets/'):
        path = (ROOT / relative).resolve()
        if not path.is_relative_to(ROOT / 'assets'): path = ROOT / '__not_allowed__'
    else:
        path = (ROOT / 'site' / relative).resolve()
        if not path.is_relative_to(ROOT / 'site'): path = ROOT / '__not_allowed__'
        if path.is_dir(): path = path / 'index.html'
    if path.is_file(): route.fulfill(path=str(path))
    else: route.fulfill(status=404, body='Source fixture has no explicitly allowed asset')


def ready(page):
    page.wait_for_function("document.querySelector('#view-status').dataset.state === 'ready' && document.querySelectorAll('#teaching-table tr').length > 0")


def check_primary_maps(page, base, output=None):
    page.goto(base + 'teach/'); ready(page)
    assert page.locator('#teaching-table tr').count() == 50
    assert '22,500 valid of 22,500' in page.locator('#view-summary').inner_text()
    before = page.locator('#view-summary').inner_text()
    page.locator('#threshold').focus(); page.keyboard.press('ArrowRight')
    page.wait_for_function("document.querySelector('#view-summary').textContent.includes('0.5 m MSL')")
    assert page.locator('#view-summary').inner_text() != before
    page.locator('#mode').select_option('3d-map')
    page.wait_for_function("document.querySelector('#plot-view').dataset.rendered === '3d-map' || document.querySelector('#view-status').dataset.state === 'error'")
    assert page.locator('#plot-view').get_attribute('data-rendered') == '3d-map', page.locator('#view-status').inner_text()
    old = page.locator('#plot-view').evaluate('(el)=>JSON.stringify(el.layout.scene.camera)')
    page.locator('#rotation').focus(); page.keyboard.press('ArrowRight')
    page.wait_for_function("old=>JSON.stringify(document.querySelector('#plot-view').layout.scene.camera)!==old", arg=old)
    page.locator('#mode').select_option('3d-scene')
    page.wait_for_function("document.querySelector('#plot-view').dataset.rendered === '3d-scene'")
    assert page.locator('#plot-view').evaluate('(el)=>el.data[0].type') == 'surface'
    assert 'Vertical exaggeration' in page.locator('#view-explanation').inner_text()
    if output: page.screenshot(path=str(output / 'teaching-3d.png'), full_page=True)
