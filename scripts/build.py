"""Strict local Book/Lite assembly; no publication or version-control operations."""
from __future__ import annotations
import os
import json
from importlib.metadata import distribution
import shutil
import subprocess
import sys
from pathlib import Path
from atlas_paths import content_files

ROOT=Path(__file__).resolve().parents[1]
PYODIDE_EXTENSION='@jupyterlite/pyodide-kernel-extension'


def pyodide_extension_assets(installed=None):
    """Locate only the kernel distribution's prebuilt extension, including user installs."""
    installed=installed or distribution('jupyterlite-pyodide-kernel')
    suffix=f'/labextensions/{PYODIDE_EXTENSION}/package.json'
    candidates=[installed.locate_file(p).resolve() for p in installed.files or []
                if ('/'+str(p).replace('\\','/')).endswith(suffix)]
    if len(candidates)!=1:
        raise RuntimeError('Installed jupyterlite-pyodide-kernel must own one prebuilt labextension package.json')
    package=candidates[0]
    metadata=json.loads(package.read_text(encoding='utf-8'))
    load=metadata.get('jupyterlab',{}).get('_build',{}).get('load')
    if metadata.get('name')!=PYODIDE_EXTENSION or not load or not (package.parent/load).is_file():
        raise RuntimeError(f'Incomplete installed Pyodide extension: {package}')
    return package.parent


def prepare_lite_project(project):
    """An explicit, isolated extension set avoids sys.prefix/user-site differences."""
    project=Path(project)
    extensions=project/'extensions'
    shutil.copytree(pyodide_extension_assets(),extensions/PYODIDE_EXTENSION)
    shutil.copyfile(ROOT/'jupyter-lite.json',project/'jupyter-lite.json')
    config={
        'LiteBuildConfig':{'ignore_sys_prefix':['federated_extensions']},
        'FederatedExtensionAddon':{'extra_labextensions_path':[str(extensions.resolve())]},
    }
    (project/'jupyter_lite_config.json').write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')


def run(*args, cwd=ROOT):
    print('+',' '.join(str(x) for x in args),flush=True)
    subprocess.run([str(x) for x in args],cwd=cwd,check=True)


def clean(path):
    target=path.resolve()
    assert target==ROOT/'_site' or target.is_relative_to(ROOT/'_build'), f'Unsafe build target: {target}'
    if target.exists():shutil.rmtree(target)
    target.mkdir(parents=True)


def main():
    temporary=ROOT/'_build/tmp'
    temporary.mkdir(parents=True,exist_ok=True)
    for name in ['TMP','TEMP','TMPDIR']:os.environ[name]=str(temporary)
    os.environ['PYTHONUTF8']='1'
    run(sys.executable,'scripts/generate.py')
    run(sys.executable,'scripts/validate.py')
    stage=ROOT/'_build/lite-contents';lite=ROOT/'_build/lite';book=ROOT/'_build/book';site=ROOT/'_site';project=ROOT/'_build/lite-project'
    for target in [stage,lite,book,site,project]:clean(target)
    run(sys.executable,'-c','from jupyter_book.cli.main import main; main()','build','content','--path-output',book,'--warningiserror','--keep-going','--nitpick')
    for path in content_files():
        if path.is_file() and (path.suffix=='.ipynb' or 'assets' in path.parts):
            dest=stage/path.relative_to(ROOT/'content');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dest)
    prepare_lite_project(project)
    # doit keeps its state relative to cwd. The disposable project must own it:
    # the pinned CLI's --force forgets tasks only after its build has run.
    run(sys.executable,'-c','from jupyterlite_core.app import main; main()','build','--force','--contents',stage,'--output-dir',lite,'--lite-dir',project,cwd=project)
    shutil.copytree(ROOT/'site',site,dirs_exist_ok=True)
    shutil.copytree(ROOT/'assets',site/'assets',dirs_exist_ok=True)
    shutil.copytree(ROOT/'catalog',site/'catalog',dirs_exist_ok=True)
    shutil.copytree(book/'_build/html',site/'book',dirs_exist_ok=True)
    shutil.copytree(lite,site/'lite',dirs_exist_ok=True)
    for name in ['README.md','REFERENCES.md','DATA_SOURCES.md','THIRD_PARTY_NOTICES.md','LICENSE','LICENSE-CONTENT.md','CITATION.cff','VALIDATION.md','CONTRIBUTING.md']:
        if (ROOT/name).exists():shutil.copyfile(ROOT/name,site/name)
    (site/'.nojekyll').touch()
    run(sys.executable,'scripts/validate.py','--built')
    print('Built _site/. Preview: python scripts/serve.py. No deployment performed.')


if __name__=='__main__':main()
