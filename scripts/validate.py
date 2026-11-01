"""Fail on catalog omissions, unsupported notebooks or Book/Lab path divergence."""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit

import jsonschema
import nbformat
import yaml
from atlas_paths import canonical_notebooks

ROOT = Path(__file__).resolve().parents[1]
PYODIDE_EXTENSION='@jupyterlite/pyodide-kernel-extension'


def validate_lite_runtime(lite, source_config):
    """A Lab shell is insufficient: require the configured, loadable kernel bundle."""
    lite=Path(lite)
    expected=source_config['jupyter-config-data']
    config=json.loads((lite/'jupyter-lite.json').read_text(encoding='utf-8'))['jupyter-config-data']
    for key in ['appName','contentsStorageName','settingsStorageName','enableServiceWorkerCache']:
        assert key in config and type(config[key]) is type(expected[key]) and config[key]==expected[key],f'Lite custom config lost: {key}'
    extensions=config.get('federated_extensions',[])
    assert [e['name'] for e in extensions]==[PYODIDE_EXTENSION], 'Expected only the explicit Pyodide kernel extension'
    entry=extensions[0]
    package_root=lite/'extensions'/PYODIDE_EXTENSION
    package=json.loads((package_root/'package.json').read_text(encoding='utf-8'))
    metadata=package.get('jupyterlab',{}).get('_build',{})
    assert package.get('name')==PYODIDE_EXTENSION and metadata.get('extension'),'Missing Pyodide kernel metadata'
    assert entry.get('extension')==metadata['extension'],'Kernel entrypoint metadata differs'
    assert entry.get('load')==metadata.get('load'),'Kernel loader metadata differs'
    for reference in [entry.get('load'),metadata.get('load')]:
        assert reference and reference.endswith('.js'),'Missing kernel JavaScript loader'
        asset=(package_root/reference).resolve()
        assert asset.is_relative_to(package_root.resolve()) and asset.is_file() and asset.stat().st_size,'Missing kernel JavaScript asset'
    schema=package_root/'static/schema/kernel.v0.schema.json'
    assert schema.is_file() and json.loads(schema.read_text(encoding='utf-8')), 'Missing Pyodide kernel schema'
    return config


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--built',action='store_true');args=parser.parse_args()
    catalog=json.loads((ROOT/'catalog/repositories.json').read_text(encoding='utf-8'))
    schema=json.loads((ROOT/'catalog/repositories.schema.json').read_text(encoding='utf-8'))
    jsonschema.Draft202012Validator(schema,format_checker=jsonschema.FormatChecker()).validate(catalog)
    records=catalog['repositories']
    discovery=json.loads((ROOT/'catalog/discovery.json').read_text(encoding='utf-8'))['repositories']
    assert all(r['visibility']=='public' for r in discovery), 'Nonpublic discovery metadata'
    expected={r['name'] for r in discovery if r['name'].startswith('JupyterLite') and r['name']!='JupyterLite-Index-Repo'}
    actual={r['name'] for r in records if r['category']=='jupyterlite'}
    assert actual==expected, f'Coverage differs: missing={expected-actual}, unexpected={actual-expected}'
    related={r['name'] for r in records if r['category']=='related'}
    assert related <= {r['name'] for r in discovery}, 'Related project absent from public discovery'
    for field in ['name','slug','notebook','book_path','lab_path']:
        assert len({r[field] for r in records})==len(records), f'Duplicate {field}'
    for r in records:
        assert r['notebook']==f"projects/{r['slug']}/index.ipynb",r['name']
        assert r['book_path']==f"book/projects/{r['slug']}/index.html",r['name']
        assert r['lab_path']==f"lite/lab/index.html?path={r['notebook']}",r['name']
        assert f"/blob/{r['source_commit']}/README.md" in r['readme_url'], 'README not pinned'
        assert all(x['checked_on'] for x in r['resources'] if x['http_status']), 'Undated status'
    toc=yaml.safe_load((ROOT/'content/_toc.yml').read_text(encoding='utf-8'))
    nav=[toc['root']]+[c['file'] for p in toc['parts'] for c in p['chapters']]
    notebooks=canonical_notebooks()
    paths={p.relative_to(ROOT/'content').as_posix().removesuffix('.ipynb') for p in notebooks}
    assert len(nav)==len(set(nav)) and set(nav)==paths,'TOC/canonical notebook mismatch'
    assert {r['notebook'] for r in records}=={p.relative_to(ROOT/'content').as_posix() for p in notebooks if p.parts[-3]=='projects'}, 'Project/notebook mismatch'
    computations=[]; links=0
    allowed=set(sys.stdlib_module_names)|{'IPython'}
    for p in notebooks:
        nb=nbformat.read(p,as_version=4);nbformat.validate(nb)
        assert not nb.metadata.get('atlas',{}).get('scaffold'),f'Incomplete scaffold: {p}'
        code_cells=[c for c in nb.cells if c.cell_type=='code']
        if p.parent.parent.name=='projects':
            assert len(code_cells)>=2,f'No runnable exercise: {p}'
            assert any('image/svg+xml' in o.get('data',{}) for c in code_cells for o in c.get('outputs',[])), f'No executed visual: {p}'
            text='\n'.join(c.source for c in nb.cells if c.cell_type=='markdown')
            for phrase in ['Learning question','Interpret','Change one thing','Sources','synthetic']:
                assert phrase.lower() in text.lower(),f'Missing {phrase}: {p}'
            record=next(r for r in records if r['notebook']==p.relative_to(ROOT/'content').as_posix())
            assert record['readme_url'] in text, f'Missing source citation: {p}'
            computations.append(code_cells[-1].source)
        for c in code_cells:
            tree=ast.parse(c.source)
            for node in ast.walk(tree):
                if isinstance(node,ast.Import): imports=[n.name.split('.')[0] for n in node.names]
                elif isinstance(node,ast.ImportFrom): imports=[(node.module or '').split('.')[0]]
                else: continue
                assert all(x in allowed and x not in {'urllib','socket','http','subprocess','os'} for x in imports), f'Unsupported runtime import in {p}: {imports}'
            assert not any(o.output_type=='error' for o in c.get('outputs',[])),f'Saved error: {p}'
        for c in nb.cells:
            if c.cell_type!='markdown':continue
            for target in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)\)',c.source):
                u=urlsplit(target)
                if u.scheme or target.startswith('#'):continue
                resolved=(p.parent/unquote(u.path)).resolve()
                assert resolved.is_relative_to(ROOT/'content') and resolved.exists(),f'Broken notebook link: {p}: {target}'
                links+=1
    assert len(set(computations))==len(computations),'Duplicate project exercise'
    health=nbformat.read(ROOT/'content/projects/rewiring-global-health/index.ipynb',as_version=4)
    text='\n'.join(c.source for c in health.cells)
    from lesson_material import HEALTH_LESSONS
    for _,_,_,filename in HEALTH_LESSONS:assert '?path='+filename in text,f'Missing source lesson {filename}'
    for p in (ROOT/'assets').glob('*.svg'):
        svg=ET.fromstring(p.read_text(encoding='utf-8'))
        assert svg.find('{http://www.w3.org/2000/svg}title') is not None and svg.find('{http://www.w3.org/2000/svg}desc') is not None,p
        assert (ROOT/'content/assets'/p.name).read_bytes()==p.read_bytes(),f'Asset copy differs: {p}'
    if args.built:
        site=ROOT/'_site'
        validate_lite_runtime(site/'lite',json.loads((ROOT/'jupyter-lite.json').read_text(encoding='utf-8')))
        for name in ['index.html','explore/index.html','teach/index.html','about/index.html','book/index.html','lite/lab/index.html','lite/jupyter-lite.json']:
            assert (site/name).is_file(),f'Missing entry {name}'
        for r in records:assert (site/r['book_path']).is_file(),f'Missing Book chapter: {r["name"]}'
        for p in notebooks:
            relative=p.relative_to(ROOT/'content')
            assert (site/'lite/files'/relative).read_bytes()==p.read_bytes(),f'Lab bytes differ: {relative}'
        assert json.loads((site/'data/catalog.json').read_text(encoding='utf-8'))==catalog,'Explorer catalog differs'
        for evidence in (ROOT/'catalog').glob('*.json'):
            assert (site/'catalog'/evidence.name).read_bytes()==evidence.read_bytes(),f'Published catalog evidence differs: {evidence.name}'
        print('PASS assembled entry points, all Book chapters, exact canonical/Lab notebook bytes and explorer catalog')
    print(f'PASS schema, {len(expected)} public prefixed + {len(related)} related projects, {len(notebooks)} canonical notebooks, {links} local notebook links, 10 source lessons and SVG provenance')


if __name__=='__main__':main()
