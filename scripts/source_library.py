"""Publication inventory, runtime selection and recursive navigation for source courses.

Routine builds read the checked-in manifest; they never contact upstream repositories.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'catalog/source-library.json'
RUNTIMES = {'browser-local', 'browser-network', 'local-server', 'reference-only'}


def load_library():
    return json.loads(MANIFEST.read_text(encoding='utf-8')) if MANIFEST.exists() else {'courses': [], 'sections': [], 'support_files': [], 'dispositions': []}


def toc_files(node):
    """Yield root, chapters and arbitrarily nested sections, in editorial order."""
    if 'root' in node:
        yield node['root']
    if 'file' in node:
        yield node['file']
    for key in ('parts', 'chapters', 'sections'):
        for child in node.get(key, []):
            yield from toc_files(child)


def source_sections(library=None):
    return {s['notebook']: s for s in (library or load_library())['sections']}


def authored_support():
    path=ROOT/'catalog/authored-support.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'files':[], 'dependencies':{}}


def validate_authored_support():
    """Audit only explicitly declared first-party helpers; no blanket import allowance."""
    import ast
    import sys
    manifest=authored_support()
    declared={item['local_path'] for item in manifest['files']}
    assert len(declared)==len(manifest['files']), 'Duplicate authored support file'
    for item in manifest['files']:
        relative=Path(item['local_path'])
        path=(ROOT/'content'/relative).resolve()
        assert not relative.is_absolute() and path.is_relative_to((ROOT/'content').resolve()) and path.is_file(), 'Unsafe authored support path'
        assert sha256(path)==item['sha256'], f'Authored support hash differs; review and update the explicit manifest: {relative}'
        if path.suffix=='.py':
            tree=ast.parse(path.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                names=[n.name.split('.')[0] for n in node.names] if isinstance(node,ast.Import) else [(node.module or '').split('.')[0]] if isinstance(node,ast.ImportFrom) else []
                assert all(name in sys.stdlib_module_names and name not in {'urllib','socket','http','subprocess','os'} for name in names), f'Unsupported authored helper import: {relative}: {names}'
    allowed=declared | {item['local_path'] for item in load_library()['support_files']} | {'assets/browser-gis-pathways.json'}
    for notebook,dependencies in manifest['dependencies'].items():
        assert (ROOT/'content'/notebook).is_file() and notebook.endswith('.ipynb')
        assert set(dependencies)<=allowed, f'Undeclared authored dependency: {notebook}'
    return manifest


def publishable_files(root=ROOT / 'content'):
    try:
        from atlas_paths import content_files
    except ModuleNotFoundError:
        from .atlas_paths import content_files
    declared = {f['local_path'] for f in load_library()['support_files']} | {f['local_path'] for f in authored_support()['files']}
    return [p for p in content_files(root) if p.suffix == '.ipynb' or 'assets' in p.relative_to(root).parts or p.relative_to(root).as_posix() in declared]


def stage_dependencies(notebook, destination, library=None):
    """Stage a complete namespaced course in a fresh tree, without source checkouts."""
    library = library or load_library()
    section = source_sections(library).get(notebook)
    target = Path(destination) / notebook
    target.parent.mkdir(parents=True, exist_ok=True)
    if section:
        prefix = f"courses/{section['course']}/"
        for item in library['support_files']:
            if item['local_path'].startswith(prefix):
                dest = Path(destination) / item['local_path']
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / 'content' / item['local_path'], dest)
    for relative in authored_support()['dependencies'].get(notebook, []):
        dest=Path(destination)/relative
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'content'/relative,dest)
    return target.parent


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_library(library=None, verify_sources=False, catalog=None):
    library = library or load_library()
    catalog = catalog if catalog is not None else json.loads((ROOT / 'catalog/repositories.json').read_text(encoding='utf-8'))
    sections = source_sections(library)
    assert len(sections) == len(library['sections']), 'Duplicate source section'
    courses = {c['slug']: c for c in library['courses']}
    assert len(courses) == len(library['courses']), 'Duplicate source course'
    catalog_slugs = [r['slug'] for r in catalog['repositories']]
    assert len(catalog_slugs) == len(set(catalog_slugs)), 'Duplicate catalog course'
    assert set(courses) == set(catalog_slugs), 'Source course/catalog coverage differs'
    inventory = library['inventory']
    assert len(courses) == inventory['repositories'], 'Course inventory count differs'
    dispositions = library['dispositions']
    assert len(dispositions) == inventory['inspected_notebook_paths'], 'Notebook inventory count differs'
    assert len({(d['course'], d['source_path']) for d in dispositions}) == len(dispositions), 'Duplicate source disposition'
    assert len(sections) == inventory['imported_sections'], 'Section inventory count differs'
    assert sum(s['collection'] == 'authored' for s in sections.values()) == inventory['authored_sections']
    assert sum(s['collection'] == 'compatibility' for s in sections.values()) == inventory['compatibility_sections']
    assert sum(d['disposition'] == 'alias' for d in dispositions) == inventory['aliases']
    assert sum(d['disposition'] == 'excluded' for d in dispositions) == inventory['excluded_notebooks']
    assert sum(d['disposition'] == 'imported' for d in dispositions) == len(sections)
    assert len(library['support_files']) == inventory['support_files'], 'Support inventory count differs'
    for slug, course in courses.items():
        assert sum(d['course'] == slug for d in dispositions) == course['source_notebook_paths'], f'Source path accounting differs: {slug}'
    for d in dispositions:
        assert d['course'] in courses, 'Disposition has an unknown source course'
        assert d['disposition'] in {'imported', 'alias', 'excluded'}
        assert len(d['source_sha256']) == 64 and len(d['source_cell_sha256']) == 64
        if d['disposition'] != 'excluded':
            assert d['notebook'] in sections
            section = sections[d['notebook']]
            assert section['course'] == d['course'], 'Alias crosses source courses'
            if d['disposition'] == 'imported':
                assert section['source_path'] == d['source_path']
                assert section['source_sha256'] == d['source_sha256']
                assert section['source_cell_sha256'] == d['source_cell_sha256']
        else:
            assert d['reason'] and d['source_url']
        if verify_sources:
            source = ROOT / '_research/textbook-sources' / d['course'] / d['source_path']
            assert sha256(source) == d['source_sha256'], source
    for section in sections.values():
        assert section['runtime']['class'] in RUNTIMES
        assert section['runtime']['requirements'] and section['verification']['status']
        assert section['license'] and section['modifications']
        path = ROOT / 'content' / section['notebook']
        # Executing selected canonical files changes outputs, never their source digest.
        import nbformat
        nb = nbformat.read(path, as_version=4)
        assert nb.metadata.atlas.source_path == section['source_path']
        assert nb.metadata.atlas.source_commit == courses[section['course']]['commit']
        assert nb.metadata.atlas.runtime == section['runtime']['class']
        sources = [(c.cell_type, c.source) for c in nb.cells[1:]]
        assert hashlib.sha256(json.dumps(sources, ensure_ascii=False).encode()).hexdigest() == section['adapted_cell_sha256'], path
    local_paths = set()
    for item in library['support_files']:
        assert item['local_path'] not in local_paths, item['local_path']
        local_paths.add(item['local_path'])
        assert sha256(ROOT / 'content' / item['local_path']) == item['sha256'], item['local_path']
        if item.get('source_path'):
            if item['sha256'] != item['source_sha256']:
                assert isinstance(item.get('modifications'),list) and item['modifications'], f'Unrecorded support adaptation: {item["local_path"]}'
            if verify_sources:
                assert sha256(ROOT / '_research/textbook-sources' / item['course'] / item['source_path']) == item['source_sha256']
    return library
