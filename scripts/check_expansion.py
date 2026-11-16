"""Fresh guarded native calculations for the four newly appended courses only.

TerrIO reading copies and five widget-only frontend cells are explicitly skipped.
No existing notebook or historical execution record is replayed or replaced.
"""
from __future__ import annotations
import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

import nbformat
from nbclient import NotebookClient
from execute import GUARD
from expansion_material import LESSONS
from source_library import ROOT, load_library, stage_dependencies
from expansion_runtime_contracts import reviewed_widget_indices

COMPANION_ASSERTIONS={
 'c3s-atlas':"assert abs(full_mean-3)<1e-12 and abs(missing_mean-4.5)<1e-12",
 'destination-earth-digital-twin':"assert abs(interpolated-25)<1e-12 and [round(weights[k],2) for k in ['SW','SE','NW','NE']]==[.24,.56,.06,.14]",
 'urbanity':"assert degrees=={'A':2,'B':4,'C':2,'D':3,'E':3,'F':2} and route==['A','B','C','F'] and len(edges)==8",
 'terrio':"assert (centre_x,centre_y)==(500315,4399385) and abs(scale['60 degrees']-2)<1e-12",
}
C3S_ASSERTIONS='''assert abs(area_mean(np.array([[0.,0.],[9.,9.]]),np.array([0.,60.]))-3)<1e-12
assert abs(area_mean(np.array([[0.,np.nan],[9.,9.]]),np.array([0.,60.]))-4.5)<1e-12
_windows=warming_levels()
assert len(_windows)==600
_known=_windows[(_windows.member=='CCCma_CanESM5_r1i1p1f1') & (_windows.scenario=='ssp585') & (_windows.level==2)].iloc[0]
assert (_known.start,_known.end,_known.midpoint)==(2013,2032,2022.5)
'''
DESTINE_ASSERTIONS='''_lat=np.array([-10.,0.,10.]);_lon=np.array([0.,10.,20.]);_xx,_yy=np.meshgrid(_lon,_lat)
assert abs(lab.bilinear(3*_xx+2*_yy,_lat,_lon,2,7)-25)<1e-12
_gx,_gy,_gz=lab.globe_xyz(np.array([0.,30.,60.]),np.array([0.,45.,90.]),radius=2)
assert np.allclose(_gx*_gx+_gy*_gy+_gz*_gz,4)
assert abs(lab.global_mean(np.ones((3,3))*8,np.array([-30.,0.,30.]))-8)<1e-12
_cube=lab.synthetic_cube()
assert _cube['temperature'].shape==(60,25,49) and _cube['lon'][-1]<180
'''
URBAN_ASSERTIONS="assert len(nodes)==6 and len(edges)==8 and {n:len(neighbors[n]) for n in nodes}=={'A':2,'B':4,'C':2,'D':3,'E':3,'F':2}\nassert route==['A','B','C','F']\n"


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true')
    parser.add_argument('--course',action='append',choices=LESSONS,help='Narrow refresh, merging a previously complete receipt')
    args=parser.parse_args()
    if sys.platform=='win32':asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    output=ROOT/'_build/expansion-native';output.mkdir(parents=True,exist_ok=True)
    runtime=output/'jupyter-runtime';runtime.mkdir(exist_ok=True);os.environ['JUPYTER_RUNTIME_DIR']=str(runtime)
    library=load_library();sections=[s for s in library['sections'] if s['course'] in LESSONS]
    paths=[(f'projects/{slug}/index.ipynb',slug,False) for slug in LESSONS]+[(s['notebook'],s['course'],True) for s in sections]
    previous=None
    if args.course:
        previous=json.loads((ROOT/'catalog/expansion-execution.json').read_text(encoding='utf-8'))
        assert len(previous['results'])==len(paths),'Targeted refresh requires a complete prior receipt'
        paths=[p for p in paths if p[1] in args.course]
    results=[]
    for relative,slug,source in paths:
        if source and slug=='terrio':
            results.append({'notebook':relative,'status':'skipped','reason':'TerrIO0.9.0 Pyodide0.29 ABI: matched source Lab continuation; no native/Atlas314 TerrIO execution.'});continue
        canonical=ROOT/'content'/relative;original=nbformat.read(canonical,4)
        skip=reviewed_widget_indices(relative,original) if source else []
        runnable=nbformat.from_dict(original);runnable.cells=[c for i,c in enumerate(runnable.cells) if i not in skip]
        runnable.cells.insert(0,nbformat.v4.new_code_cell(GUARD))
        assertion=COMPANION_ASSERTIONS[slug] if not source else C3S_ASSERTIONS if slug=='c3s-atlas' else DESTINE_ASSERTIONS if slug=='destination-earth-digital-twin' else URBAN_ASSERTIONS if relative.endswith('/street-networks.ipynb') else ''
        runnable.cells.append(nbformat.v4.new_code_cell(assertion+"\nprint('ATLAS_EXPANSION_NATIVE_ORACLE_PASSED')"))
        with tempfile.TemporaryDirectory(prefix='lesson-',dir=output) as folder:
            cwd=stage_dependencies(relative,folder,library)
            executed=NotebookClient(runnable,timeout=90,kernel_name='python3',resources={'metadata':{'path':str(cwd)}},allow_errors=False).execute()
        proof=executed.cells.pop();executed.cells.pop(0)
        for cell in executed.cells:
            if cell.cell_type=='code' and cell.execution_count is not None:cell.execution_count-=1
        by_id={c.id:c for c in executed.cells}
        for index,cell in enumerate(original.cells):
            if index not in skip:original.cells[index]=by_id[cell.id]
        graphics=[mime for c in original.cells if c.cell_type=='code' for o in c.outputs for mime in o.get('data',{}) if mime in {'image/svg+xml','image/png','text/html'}]
        if not source:assert 'image/svg+xml' in graphics,'Companion needs freshly executed SVG and text alternative'
        if args.write:nbformat.write(original,canonical)
        results.append({'notebook':relative,'status':'passed','code_cells':sum(c.cell_type=='code' for c in executed.cells),
            'skipped_widget_cells':skip,'graphics':graphics,'independent_oracle':bool(assertion),
            'canonical_sha256':hashlib.sha256(canonical.read_bytes()).hexdigest()})
        print('PASS',relative,'widget cells skipped:'+str(skip) if skip else '',flush=True)
    receipt={'checked_on':'2026-11-16','method':'Fresh native Python kernel and temporary course layout per notebook; Python data-service connections guarded; no upstream script execution.',
        'limits':'Native calculations only. Five widget-only frontend cells skipped. TerrIO source copies remain unexecuted reference copies; matching Pyodide0.29 source runtime required. Browser/CDN/WebGL/service certification is separate.', 'results':results}
    if previous:
        current={r['notebook']:r for r in results}
        receipt['results']=[current.get(r['notebook'],r) for r in previous['results']]
    (output/'results.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    if args.write:(ROOT/'catalog/expansion-execution.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print('Accounted:',len(results),'passed:',sum(r['status']=='passed' for r in results),'TerrIO reading copies skipped:',sum(r['status']=='skipped' for r in results))


if __name__=='__main__':main()
