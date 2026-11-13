"""Focused browser checks use source UI files and no assembled site/runtime."""
import os
import re
import json
import unittest
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

from playwright.sync_api import sync_playwright
from check_runtime import select_python
from map_test_support import source_route, ready, check_primary_maps, PREFIX

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
    def test_2d_renderer_failure_keeps_real_table_export_and_retries(self):
        page=self.browser.new_page()
        page.route('**/*',source_route)
        page.route('**/vendor/leaflet/dist/leaflet.js',lambda route:route.fulfill(status=503,body='2D renderer unavailable'))
        try:
            page.goto('http://atlas.test'+PREFIX+'teach/')
            page.wait_for_function("document.querySelector('#view-status').dataset.state==='error'")
            self.assertIn('selected real data are available',page.locator('#view-status').inner_text())
            self.assertEqual(page.locator('#teaching-table tr').count(),50)
            self.assertTrue(page.locator('#download').is_enabled())
            self.assertIn('Lagos',page.locator('#view-title').inner_text())
            page.unroute('**/vendor/leaflet/dist/leaflet.js');page.locator('#retry').click();ready(page)
            self.assertTrue(page.locator('#map-view').is_visible())
        finally:page.close()

    def test_real_maps_geography_controls_and_actual_3d(self):
        page=self.browser.new_page()
        page.route('**/*',source_route)
        try:
            check_primary_maps(page,'http://atlas.test'+PREFIX)
            for mode in ['3d-map','3d-scene']:
                page.locator('#mode').select_option(mode);ready(page)
                credit=page.locator('#plot-view').evaluate('el=>el.layout.annotations[0].text')
                self.assertIn('Seeger & Minderhoud / DEM creators',credit)
                self.assertIn('CC BY-NC-SA 4.0',credit)
                self.assertNotIn('Public-domain',credit)
            page.locator('#model').select_option('GLL-DTM v2 (global coastal lowlands)');ready(page)
            page.locator('#city').select_option('Bangkok');ready(page)
            before=page.locator('#view-summary').inner_text()
            aspect=page.locator('#plot-view').evaluate('''el=>{const s=el.layout.scene;
              return {z:s.aspectratio.z,expected:(s.zaxis.range[1]-s.zaxis.range[0])*100/Math.max(s.xaxis.range[1]-s.xaxis.range[0],s.yaxis.range[1]-s.yaxis.range[0]),first:el.data[0].z[0][0]};}''')
            self.assertAlmostEqual(aspect['z'],aspect['expected'],places=12)
            self.assertLess(aspect['z'],.02)
            page.locator('#exaggeration').focus();page.keyboard.press('End')
            page.wait_for_function('z=>Math.abs(document.querySelector("#plot-view").layout.scene.aspectratio.z-z*2)<1e-12',arg=aspect['z'])
            self.assertEqual(page.locator('#view-summary').inner_text(),before)
            self.assertEqual(page.locator('#plot-view').evaluate('el=>el.data[0].z[0][0]'),aspect['first'])
            page.locator('#plot-view').evaluate('el=>el.emit("plotly_webglcontextlost")')
            page.wait_for_function("document.querySelector('#view-status').textContent.includes('context was lost')")
            self.assertTrue(page.locator('#map-view').is_visible())
            self.assertTrue(page.locator('#download').is_enabled())
            self.assertEqual(page.locator('#view-summary').inner_text(),before)
            self.assertIn('North-up geographic map',page.locator('#view-explanation').inner_text())
            self.assertNotIn('reference',page.locator('#view-explanation').inner_text())
        finally:page.close()

    def test_all_real_data_adapters_masks_geometry_and_export(self):
        page=self.browser.new_page()
        page.route('**/*',source_route)
        try:
            page.goto('http://atlas.test'+PREFIX+'teach/');ready(page)
            result=page.evaluate('''async()=>{
              const m=await import('../map-data.js');
              const state={family:'terrain',city:'Lagos',model:m.MODELS[1][0],threshold:0};
              const terrain=[];
              for(const model of m.MODELS)for(const city of m.CITIES){
                const d=await m.dataset({...state,model:model[0],city});
                terrain.push({city,model:model[0],stats:m.statistics(d),first:d.record(0)});
              }
              const pop=[];
              for(const [product]of m.PRODUCTS){const d=await m.dataset({family:'population',product});
                pop.push({product,stats:m.statistics(d),first:d.record(0),sample:m.exportSelection(d,{family:'population',product})});}
              const tracts=await m.dataset({family:'onehealth',metric:'POP100'});
              const pixels=await m.dataset({family:'onehealth',metric:'temperature_c'});
              const poster=await m.dataset({family:'poster',scenario:'RCP 2.6',year:'2030',scope:'city'});
              const syntheticMask={family:'terrain',count:4,value:i=>[0,null,-1,3][i],record:i=>({id:String(i),lon:1,lat:2,value:[0,null,-1,3][i]}),
                bounds:[[1,1],[3,3]],metadata:{},unit:'m',note:'test fixture only'};
              return {terrain,pop,tracts:{stats:m.statistics(tracts),first:tracts.record(0),note:tracts.note},
                pixels:{stats:m.statistics(pixels),first:pixels.record(0)},
                poster:{rows:Array.from({length:poster.count},(_,i)=>poster.record(i)),portfolio:poster.portfolio},
                mask:m.statistics(syntheticMask),maskExport:m.exportSelection(syntheticMask,{threshold:0})};
            }''')
            expected=[166,898,783,300,65,22500,22499,22475,22500,22500,15517,21687,20453,9981,12994]
            self.assertEqual([t['stats']['valid'] for t in result['terrain']],expected)
            first=result['terrain'][5]['first']
            self.assertAlmostEqual(first['lon'],-4.179,places=9);self.assertAlmostEqual(first['lat'],5.479,places=9)
            self.assertEqual(first['value'],23.78)
            self.assertEqual(sum(t['stats']['valid'] for t in result['terrain']),195318)
            for p,valid,missing,zero,total in zip(result['pop'],[126065,110648,1478,2107],[76436,91853,538,0],[2,0,70,561],[11681101.053525183,10759970.49508071,18551545,11842522.187477237]):
                self.assertEqual((p['stats']['valid'],p['stats']['missing'],p['stats']['zero']),(valid,missing,zero))
                self.assertAlmostEqual(p['stats']['sum'],total,places=5)
                exported=p['sample'];self.assertLessEqual(len(exported['features']),1600)
                self.assertIn('citation',exported['atlas_metadata']['source_metadata'])
                self.assertTrue(all(len(f['geometry']['coordinates'])==2 for f in exported['features']))
            self.assertEqual(result['tracts']['stats']['count'],166)
            self.assertEqual(result['tracts']['stats']['sum'],764468)
            self.assertIn('Column anchors are Census-provided tract centroids (CENTLON/CENTLAT), not buildings.',result['tracts']['note'])
            self.assertEqual(result['tracts']['first']['geometry']['type'],'Polygon')
            self.assertEqual(result['pixels']['stats']['count'],6890)
            self.assertAlmostEqual(result['pixels']['first']['value'],43.9413876,places=7)
            self.assertEqual([r['value'] for r in result['poster']['rows']],[1,13,0,0,0])
            self.assertEqual(result['poster']['portfolio']['facilities_2023'],25873)
            self.assertEqual(result['mask']['valid'],3);self.assertEqual(result['mask']['missing'],1)
            self.assertEqual(result['mask']['zero'],1);self.assertEqual(result['mask']['below'],2)
            self.assertEqual([f['properties']['value'] for f in result['maskExport']['features']],[0,None,-1,3])
            page.locator('#family').select_option('poster');ready(page)
            self.assertEqual(page.locator('#teaching-table tr').count(),5)
            self.assertEqual(page.locator('.leaflet-tooltip').count(),5)
            self.assertIn('0 / 73',page.locator('#teaching-table').inner_text())
            self.assertIn('108 / 25,873',page.locator('#portfolio-summary').inner_text())
            page.locator('#scope').select_option('district');ready(page)
            self.assertIn('1 / 94',page.locator('#teaching-table').inner_text())
            page.locator('#family').select_option('onehealth');ready(page)
            page.locator('#metric').select_option('POP100');ready(page)
            self.assertIn('764,468',page.locator('#view-summary').inner_text())
            with page.expect_download() as downloaded:page.locator('#download').click()
            export=json.loads(Path(downloaded.value.path()).read_text())
            self.assertEqual(export['features'][0]['geometry']['type'],'Polygon')
            self.assertIn('whole-tract',export['atlas_metadata']['scientific_limits'])
        finally:page.close()

    def test_map_failure_retry_webgl_fallback_and_stale_fetch(self):
        page=self.browser.new_page()
        page.route('**/*',source_route)
        page.add_init_script('''const original=window.fetch.bind(window);window.fetch=async(...args)=>{
          const response=await original(...args);
          if(String(args[0]).includes('population.json'))await new Promise(r=>setTimeout(r,700));return response;};''')
        try:
            page.goto('http://atlas.test'+PREFIX+'teach/');ready(page)
            page.locator('#family').select_option('population')
            page.locator('#family').select_option('poster');ready(page)
            page.wait_for_timeout(900)
            self.assertIn('reporting scope',page.locator('#view-title').inner_text())
            self.assertEqual(page.locator('#teaching-table tr').count(),5)
            page.route('**/population.json',lambda route:route.fulfill(status=503,body='test source unavailable'))
            page.locator('#family').select_option('population')
            # The earlier request is cached: a fresh navigation tests the failing source.
            page.goto('http://atlas.test'+PREFIX+'teach/?family=population')
            page.wait_for_function("document.querySelector('#view-status').dataset.state==='error'")
            self.assertTrue(page.locator('#download').is_disabled());self.assertEqual(page.locator('#teaching-table tr').count(),0)
            self.assertIn('No synthetic replacement',page.locator('#view-summary').inner_text())
            page.unroute('**/population.json')
            page.locator('#retry').click();ready(page)
            self.assertIn('people',page.locator('#view-summary').inner_text())
        finally:page.close()
        page=self.browser.new_page()
        page.route('**/*',source_route)
        page.add_init_script('''const get=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(type,...args){
          return String(type).includes('webgl')?null:get.call(this,type,...args);};''')
        try:
            page.goto('http://atlas.test'+PREFIX+'teach/?view=3d-scene&family=population')
            page.wait_for_function("document.querySelector('#view-status').dataset.state==='error'")
            self.assertEqual(page.locator('#family').input_value(),'terrain')
            self.assertTrue(page.locator('#map-view').is_visible());self.assertTrue(page.locator('#download').is_enabled())
            self.assertIn('WebGL is unavailable',page.locator('#view-status').inner_text())
            self.assertIn('North-up geographic map',page.locator('#view-explanation').inner_text())
            self.assertNotIn('reference plane',page.locator('#view-explanation').inner_text())
            self.assertEqual(page.locator('#teaching-table tr').count(),50)
            page.locator('#use-2d').click();ready(page)
            self.assertEqual(page.locator('#mode').input_value(),'2d')
        finally:page.close()

    def test_gauge_gallery_query_and_mobile(self):
        page=self.browser.new_page(viewport={'width':390,'height':844})
        errors=[];requests=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('request',lambda r:requests.append(r.url))
        page.route('**/*',source_route)
        try:
            page.goto('http://atlas.test'+PREFIX+'teach/?family=population&product=ghspop-2025');ready(page)
            self.assertIn('561 valid zero',page.locator('#view-summary').inner_text())
            self.assertIn('product=ghspop-2025',page.url)
            self.assertTrue(page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'))
            page.wait_for_function("document.querySelector('#gauge-status').textContent.includes('672 hours')")
            self.assertIn('1,745.227679',page.locator('#gauge-status').inner_text())
            page.locator('#gauge-station').select_option('Mombasa')
            self.assertIn('1011/A',page.locator('#gauge-status').inner_text())
            self.assertIn('2,901.65625',page.locator('#gauge-status').inner_text())
            for city,raw,anomaly,lo,hi in [('Lagos',1605,-.140228,-.698228,.584772),('Mombasa',2037,-.864656,-1.660656,1.786344)]:
                page.locator('#gauge-station').select_option(city)
                page.locator('#gauge-hour').focus();page.keyboard.press('Home');page.keyboard.press('ArrowRight')
                self.assertEqual(page.locator('#gauge-hour').input_value(),'1')
                self.assertEqual(page.locator('#gauge-time').inner_text(),'1994-07-01 01:00:00 UTC')
                reading=page.locator('#gauge-reading').inner_text()
                self.assertIn(f'{raw} mm above record-specific station zero',reading)
                self.assertIn(f'{anomaly} m relative',reading)
                marker=page.locator('#gauge-chart circle')
                self.assertAlmostEqual(float(marker.get_attribute('cx')),55+605/671,places=8)
                self.assertAlmostEqual(float(marker.get_attribute('cy')),185-(anomaly-lo)/(hi-lo)*155,places=6)
            page.wait_for_function("document.querySelector('#gallery-status').textContent.includes('matching experiences')")
            self.assertTrue(all('synthetic' not in t for t in page.locator('#map-resources .pill').all_inner_texts()))
            page.locator('#map-search').fill('no-such-map-zzzzz')
            self.assertIn('No matching',page.locator('#map-resources').inner_text())
            page.locator('#map-search').fill('');page.locator('#map-class').select_option('synthetic')
            self.assertTrue(all('synthetic' in t for t in page.locator('#map-resources .pill').all_inner_texts()))
            self.assertFalse(any('tile.openstreetmap.org' in r for r in requests))
            self.assertFalse(errors,errors)
        finally:page.close()

    def test_source_export_filenames_optical_metrics_and_pagination(self):
        page=self.browser.new_page()
        page.route('**/*',source_route)
        try:
            page.goto('http://atlas.test'+PREFIX+'teach/?family=onehealth&city=Mombasa');ready(page)
            def source_row(locator, identifier, lon, lat, value):
                cells=locator.locator('th,td').all_inner_texts()
                self.assertEqual(cells[0],identifier)
                for actual,expected in zip(cells[1:4],[lon,lat,value]):self.assertAlmostEqual(float(actual.replace(',','')),expected,places=5)
            self.assertTrue(page.locator('#previous-page').is_disabled())
            source_row(page.locator('#teaching-table tr').first,'r5c35',-119.8977172,36.8987271,43.9413876)
            page.locator('#next-page').click()
            source_row(page.locator('#teaching-table tr').first,'r15c375',-119.7832721,36.8987618,46.0092897)
            page.locator('#previous-page').click()
            source_row(page.locator('#teaching-table tr').first,'r5c35',-119.8977172,36.8987271,43.9413876)
            page.locator('#next-page').evaluate('(button)=>{for(let i=0;i<137;i++)button.click();}')
            self.assertEqual(page.locator('#teaching-table tr').count(),40)
            source_row(page.locator('#teaching-table tr').first,'r935c405',-119.7642382,36.6504815,40.5302036)
            source_row(page.locator('#teaching-table tr').last,'r945c745',-119.650154,36.6503726,44.3686401)
            self.assertTrue(page.locator('#next-page').is_disabled())
            self.assertTrue(page.locator('#previous-page').is_enabled())
            page.locator('#next-page').evaluate('(button)=>button.click()')
            self.assertEqual(page.locator('#page-label').inner_text(),'Page 138 of 138')
            for metric,golden,label in [('ndvi',.2342719,'vegetation proxy'),('ndwi',-.3877197,'water proxy')]:
                page.locator('#metric').select_option(metric);ready(page)
                self.assertIn(label,page.locator('#value-heading').inner_text())
                self.assertIn(metric.upper(),page.locator('#view-title').inner_text())
                source_row(page.locator('#teaching-table tr').first,'r5c35',-119.8977172,36.8987271,golden)
                with page.expect_download() as downloaded:page.locator('#download').click()
                self.assertIn('atlas-onehealth-fresno-',downloaded.value.suggested_filename)
                self.assertNotIn('mombasa',downloaded.value.suggested_filename)
                exported=json.loads(Path(downloaded.value.path()).read_text())
                self.assertEqual(exported['features'][0]['properties']['value'],golden)
                self.assertEqual(exported['features'][0]['geometry']['coordinates'],[-119.8977172,36.8987271])
                self.assertEqual(exported['atlas_metadata']['source_metadata']['selected_metric'],metric)
                self.assertIn('Bounded source sample',exported['atlas_metadata']['sample_scope'])
            page.locator('#family').select_option('population');ready(page)
            with page.expect_download() as downloaded:page.locator('#download').click()
            self.assertIn('atlas-population-greater-lagos-worldpop',downloaded.value.suggested_filename)
            self.assertNotIn('mombasa',downloaded.value.suggested_filename)
            self.assertIn('source sample',page.locator('#download').inner_text())
            self.assertIn('Full 2D maps and terrain scenes render all',page.locator('#sampling-note').inner_text())
        finally:page.close()

    def test_query_steps_and_initial_history_gauge_city(self):
        page=self.browser.new_page()
        page.route('**/*',source_route)
        try:
            page.goto('http://atlas.test'+PREFIX+'teach/?city=Mombasa&threshold=0.25&rotation=37&tilt=33&exaggeration=12.5');ready(page)
            page.wait_for_function("document.querySelector('#gauge-status').textContent.includes('1011/A')")
            self.assertEqual(page.locator('#gauge-station').input_value(),'Mombasa')
            values={'threshold':'0.5','rotation':'35','tilt':'35','exaggeration':'13'}
            query=parse_qs(urlsplit(page.url).query)
            for key,value in values.items():
                self.assertEqual(page.locator('#'+key).input_value(),value)
                self.assertEqual(query[key],[value])
            self.assertIn('at/below 0.5 m MSL',page.locator('#view-summary').inner_text())
            with page.expect_download() as downloaded:page.locator('#download').click()
            exported=json.loads(Path(downloaded.value.path()).read_text())
            for key,value in values.items():self.assertEqual(exported['atlas_metadata']['selection'][key],value)
            page.evaluate("history.pushState(null,'','?city=Lagos');dispatchEvent(new PopStateEvent('popstate'))")
            ready(page)
            self.assertEqual(page.locator('#gauge-station').input_value(),'Lagos')
            page.evaluate("history.pushState(null,'','?city=Mombasa');dispatchEvent(new PopStateEvent('popstate'))")
            ready(page)
            self.assertEqual(page.locator('#city').input_value(),'Mombasa')
            self.assertEqual(page.locator('#gauge-station').input_value(),'Mombasa')
            self.assertIn('1011/A',page.locator('#gauge-status').inner_text())
        finally:page.close()

    def test_canvas_pixels_geography_masks_and_bounded_renderers(self):
        page=self.browser.new_page()
        page.route('**/*',source_route)
        try:
            page.goto('http://atlas.test'+PREFIX+'teach/?city=Abidjan&model=GLL-DTM%20v2%20(global%20coastal%20lowlands)');ready(page)
            pixels=page.evaluate('''async()=>{
              const data=await import('../map-data.js'),renderer=await import('../map-renderers.js');
              const d=await data.dataset({family:'terrain',city:'Abidjan',model:'GLL-DTM v2 (global coastal lowlands)'});
              const map=renderer.renderMap(d,data.statistics(d));
              const canvas=document.querySelector('.atlas-data-canvas'),ratio=canvas.width/map.getSize().x;
              return [[-3.935,5.465],[-3.935,5.195],[-4.045,5.255],[-4.045,5.405]].map(([lon,lat])=>{
                const p=map.latLngToContainerPoint([lat,lon]);return Array.from(canvas.getContext('2d').getImageData(Math.round(p.x*ratio),Math.round(p.y*ratio),1,1).data);
              });}''')
            self.assertEqual(pixels,[[109,164,115,255],[0,0,0,0],[36,124,131,255],[0,0,0,0]])
            for _ in range(5):
                page.locator('#family').select_option('poster');ready(page)
                page.locator('#family').select_option('onehealth');ready(page)
                page.locator('#metric').select_option('POP100');ready(page)
                self.assertLessEqual(page.locator('#map-view canvas').count(),3)
        finally:page.close()

    def test_stalled_plotly_script_times_out_and_allows_later_2d(self):
        page=self.browser.new_page()
        page.clock.install()
        pending=[]
        page.route('**/*',source_route)
        page.route('**/plotly.min.js',lambda route:pending.append(route))
        try:
            page.goto('http://atlas.test'+PREFIX+'teach/');ready(page)
            page.locator('#mode').select_option('3d-scene')
            page.wait_for_function("document.querySelector('script[src$=\"plotly.min.js\"]')!==null")
            page.locator('#mode').select_option('2d')
            page.clock.fast_forward(30001);ready(page)
            self.assertTrue(page.locator('#map-view').is_visible())
            self.assertEqual(page.locator('script[src$="plotly.min.js"]').count(),0)
            self.assertEqual(page.locator('#teaching-table tr').count(),50)
        finally:
            for route in pending:route.abort()
            page.close()

    def test_mobile_scene_fits_and_resize_preserves_dragged_orientation(self):
        page=self.browser.new_page(viewport={'width':1440,'height':1100})
        page.route('**/*',source_route)
        try:
            page.goto('http://atlas.test'+PREFIX+'teach/?view=3d-scene');ready(page)
            plot=page.locator('#plot-view');plot.scroll_into_view_if_needed()
            box=plot.bounding_box()
            initial=plot.evaluate('el=>structuredClone(el._fullLayout.scene.camera)')
            page.mouse.move(box['x']+box['width']*.5,box['y']+box['height']*.45)
            page.mouse.down();page.mouse.move(box['x']+box['width']*.5+70,box['y']+box['height']*.45-30,steps=10);page.mouse.up()
            before=plot.evaluate('el=>structuredClone(el._fullLayout.scene.camera)')
            self.assertNotEqual(initial['eye'],before['eye'],'The test must orbit the actual interactive scene before resizing')
            page.set_viewport_size({'width':390,'height':844})
            page.wait_for_function("document.querySelector('#plot-view')._fullLayout.width<400")
            page.wait_for_timeout(500)
            after=plot.evaluate('el=>structuredClone(el._fullLayout.scene.camera)')
            def direction(camera):
                eye=camera['eye'];length=sum(v*v for v in eye.values())**.5
                return [eye[k]/length for k in ['x','y','z']]
            for a,b in zip(direction(before),direction(after)):self.assertAlmostEqual(a,b,places=6)
            self.assertEqual(before['up'],after['up']);self.assertEqual(before['center'],after['center'])
            self.assertAlmostEqual(sum(v*v for v in after['eye'].values())**.5,4.8,places=6)
            self.assertTrue(page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'))
            output=ROOT/'_build/map-review';output.mkdir(exist_ok=True)
            page.locator('.view-panel').screenshot(path=str(output/'mobile-scene-settled.png'))
            page.goto('http://atlas.test'+PREFIX+'teach/?view=3d-scene');ready(page)
            page.wait_for_timeout(500)
            page.locator('.view-panel').screenshot(path=str(output/'mobile-scene-default.png'))
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
