"""Focused browser checks use source UI files and no assembled site/runtime."""
import os
import re
import unittest
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright
from check_runtime import select_python

ROOT=Path(__file__).resolve().parents[1]


def luminance(css):
    if css.startswith('#'):
        rgb=[int(css[i:i+2],16) for i in [1,3,5]]
    else:rgb=[float(n) for n in re.findall(r'[\d.]+',css)[:3]]
    linear=[n/255/12.92 if n/255<=0.04045 else ((n/255+.055)/1.055)**2.4 for n in rgb]
    return sum(v*w for v,w in zip(linear,[.2126,.7152,.0722]))


class UiRepairs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright=sync_playwright().start()
        cls.browser=cls.playwright.chromium.launch(headless=True,executable_path=os.environ.get('ATLAS_TEST_BROWSER_EXECUTABLE'))

    @classmethod
    def tearDownClass(cls):cls.browser.close();cls.playwright.stop()

    def test_book_root_and_directory_alias_handoffs(self):
        page=self.browser.new_page()
        script=(ROOT/'content/_static/atlas-launch.js').read_text(encoding='utf-8')
        page.route('**/*',lambda route:route.fulfill(status=200,content_type='text/html',body='<article class="bd-article"></article><script>'+script+'</script>'))
        try:
            for route,notebook in [('/prefix/book/','index.ipynb'),('/prefix/book','index.ipynb'),('/prefix/book/projects/rustgis/','projects%2Frustgis%2Findex.ipynb'),('/prefix/book/projects/rustgis/index.html','projects%2Frustgis%2Findex.ipynb')]:
                page.goto('http://atlas.test'+route)
                self.assertEqual(page.get_by_role('link',name='Run this notebook in Lab').get_attribute('href'),'/prefix/lite/lab/index.html?path='+notebook)
        finally:page.close()

    def test_teaching_threshold_arithmetic_and_text_contrast(self):
        page=self.browser.new_page()
        def source_route(route):
            relative=urlsplit(route.request.url).path.lstrip('/')
            path=ROOT/'site'/relative
            if path.is_dir():path=path/'index.html'
            if path.is_file():route.fulfill(path=str(path))
            else:route.fulfill(status=404,body='Source fixture has no such asset')
        page.route('**/*',source_route)
        try:
            page.goto('http://atlas.test/teach/')
            page.locator('#teaching-table tr').first.wait_for()
            page.locator('#water').focus()
            for _ in range(4):page.keyboard.press('ArrowRight')
            text=page.locator('#view-summary').inner_text()
            self.assertIn('6 of 16 cells',text)
            self.assertIn('84 of 227 invented demand units (37%)',text)
            pairs=page.locator('#view > rect').evaluate_all('(rects)=>rects.slice(1).map(r=>[getComputedStyle(r).fill,getComputedStyle(r.nextElementSibling).fill])')
            self.assertEqual(len(pairs),16)
            for background,foreground in pairs:
                a,b=sorted([luminance(background),luminance(foreground)])
                self.assertGreaterEqual((b+.05)/(a+.05),4.5,(background,foreground))
            page.locator('#mode').select_option('3d-map')
            pairs=page.locator('#view > text').evaluate_all('(texts)=>texts.map(t=>[getComputedStyle(t.previousElementSibling).fill,getComputedStyle(t).fill])')
            self.assertEqual(len(pairs),16)
            for background,foreground in pairs:
                a,b=sorted([luminance(background),luminance(foreground)])
                self.assertGreaterEqual((b+.05)/(a+.05),4.5,(background,foreground))
        finally:page.close()

    def test_kernel_dialog_selects_python_and_auto_started_kernel_is_allowed(self):
        page=self.browser.new_page()
        try:
            page.set_content('''<div class="jp-Dialog" role="dialog"><p>Select Kernel</p><select><option value="none">No Kernel</option><option value="python">Python (Pyodide)</option></select><button onclick="window.chosen=document.querySelector('select').value;this.parentElement.remove()">Select</button></div>''')
            select_python(page,1000)
            self.assertEqual(page.evaluate('window.chosen'),'python')
            page.set_content('<button class="jp-KernelName">Python (Pyodide)</button>')
            select_python(page,1000)
            self.assertEqual(page.locator('.jp-KernelName').inner_text(),'Python (Pyodide)')
        finally:page.close()


if __name__=='__main__':unittest.main()
