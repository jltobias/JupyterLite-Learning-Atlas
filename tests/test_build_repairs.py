"""Targeted build/config/TOC contracts, using small temporary fixtures only."""
import copy
import json
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path, PurePosixPath
from types import SimpleNamespace
from unittest.mock import patch

import yaml
from traitlets.config import Config
from jupyterlite_core.addons.federated_extensions import FederatedExtensionAddon
from jupyterlite_core.manager import LiteManager

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build
import generate
from validate import validate_lite_runtime,PYODIDE_EXTENSION


def fixture_extension(root):
    extension=root/PYODIDE_EXTENSION
    (extension/'static/schema').mkdir(parents=True)
    (extension/'static/remoteEntry.test.js').write_text('export const test = true;',encoding='utf-8')
    (extension/'static/schema/kernel.v0.schema.json').write_text('{"type":"object"}',encoding='utf-8')
    package={'name':PYODIDE_EXTENSION,'jupyterlab':{'_build':{'load':'static/remoteEntry.test.js','extension':'./extension'}}}
    (extension/'package.json').write_text(json.dumps(package),encoding='utf-8')
    return extension


class BuildRepairs(unittest.TestCase):
    def test_assembly_copies_public_catalog_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve()
            for name in ['site','assets','catalog']:(root/name).mkdir()
            evidence=b'{"repositories": [{"after": "public"}]}\n'
            (root/'catalog/public-visibility-changes.json').write_bytes(evidence)
            (root/'catalog/repositories.json').write_bytes(b'{"repositories": []}\n')
            (root/'README.md').write_text('[Audit](catalog/public-visibility-changes.json)',encoding='utf-8')
            def fake_run(*args,**kwargs):
                if '--path-output' in args:
                    (Path(args[args.index('--path-output')+1])/'_build/html').mkdir(parents=True)
            with patch.object(build,'ROOT',root),patch.object(build,'run',side_effect=fake_run),patch.object(build,'prepare_lite_project'),patch.object(build,'content_files',return_value=[]),patch.dict(build.os.environ):
                build.main()
            self.assertEqual((root/'_site/catalog/public-visibility-changes.json').read_bytes(),evidence)
            self.assertEqual((root/'_site/catalog/repositories.json').read_bytes(),(root/'catalog/repositories.json').read_bytes())
            self.assertIn('catalog/public-visibility-changes.json',(root/'_site/README.md').read_text(encoding='utf-8'))

    def test_distribution_metadata_finds_user_site_extension(self):
        with tempfile.TemporaryDirectory() as folder:
            extension=fixture_extension(Path(folder)/'user-site/share/jupyter/labextensions')
            installed=SimpleNamespace(files=[PurePosixPath('../../share/jupyter/labextensions')/PYODIDE_EXTENSION/'package.json'],locate_file=lambda _:extension/'package.json')
            self.assertEqual(build.pyodide_extension_assets(installed),extension.resolve())
            (extension/'static/remoteEntry.test.js').unlink()
            with self.assertRaisesRegex(RuntimeError,'Incomplete'):build.pyodide_extension_assets(installed)

    def test_isolated_project_has_only_explicit_kernel_and_source_config(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);extension=fixture_extension(root/'installed');project=root/'lite-project';project.mkdir()
            (root/'jupyter-lite.json').write_bytes((ROOT/'jupyter-lite.json').read_bytes())
            with patch.object(build,'ROOT',root),patch.object(build,'pyodide_extension_assets',return_value=extension):
                build.prepare_lite_project(project)
            config=json.loads((project/'jupyter_lite_config.json').read_text())
            self.assertEqual(config['LiteBuildConfig']['ignore_sys_prefix'],['federated_extensions'])
            addon=FederatedExtensionAddon(LiteManager(config=Config(config)),config=Config(config))
            self.assertEqual([p.parent for p in addon.env_extensions(Path(addon.extra_labextensions_path[0]))],[(project/'extensions'/PYODIDE_EXTENSION).resolve()])
            self.assertEqual((project/'jupyter-lite.json').read_bytes(),(ROOT/'jupyter-lite.json').read_bytes())

    def test_built_kernel_and_every_custom_config_value_are_required(self):
        source=json.loads((ROOT/'jupyter-lite.json').read_text())
        with tempfile.TemporaryDirectory() as folder:
            lite=Path(folder);extension=fixture_extension(lite/'extensions')
            config=copy.deepcopy(source)
            config['jupyter-config-data']['federated_extensions']=[{'name':PYODIDE_EXTENSION,'load':'static/remoteEntry.test.js','extension':'./extension'}]
            def write(value):(lite/'jupyter-lite.json').write_text(json.dumps(value),encoding='utf-8')
            write(config);validate_lite_runtime(lite,source)
            for key in source['jupyter-config-data']:
                changed=copy.deepcopy(config);changed['jupyter-config-data'][key]='lost'
                write(changed)
                with self.assertRaisesRegex(AssertionError,'custom config lost'):validate_lite_runtime(lite,source)
            changed=copy.deepcopy(config);changed['jupyter-config-data']['federated_extensions']=[];write(changed)
            with self.assertRaisesRegex(AssertionError,'Pyodide'):validate_lite_runtime(lite,source)
            write(config);(extension/'static/remoteEntry.test.js').unlink()
            with self.assertRaisesRegex(AssertionError,'JavaScript asset'):validate_lite_runtime(lite,source)

    def test_clean_rejects_nonbuild_workspace_paths(self):
        for path in [ROOT,ROOT/'content',ROOT/'.git',ROOT/'catalog']:
            with self.assertRaisesRegex(AssertionError,'Unsafe build target'):build.clean(path)

    def test_quoted_title_yaml_roundtrip_and_parent_foundation_preserved(self):
        record=copy.deepcopy(json.loads((ROOT/'catalog/repositories.json').read_text())['repositories'][0])
        record['title']='A "quoted": question\nwith a second line and \\ path'
        toc=generate.make_toc([record]);encoded=yaml.safe_dump(toc,sort_keys=False,allow_unicode=True)
        decoded=yaml.safe_load(encoded)
        titles=[c.get('title') for part in decoded['parts'] for c in part['chapters']]
        self.assertIn(record['name'].removeprefix('JupyterLite-')+' - '+record['title'],titles)
        self.assertIn('foundations/learning-a-model',[c['file'] for p in decoded['parts'] for c in p['chapters']])
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'content').mkdir();target=root/'content/unchanged.ipynb';target.write_bytes(b'authored canonical bytes')
            with patch.object(generate,'ROOT',root):generate.notebook('unchanged.ipynb',[])
            self.assertEqual(target.read_bytes(),b'authored canonical bytes')

    def test_resource_statuses_match_the_final_exact_url_audit(self):
        evidence=json.loads((ROOT/'catalog/launch-checks.json').read_text(encoding='utf-8'))
        baseline=evidence['baseline_results']
        self.assertEqual(baseline['source_commit'],'cc0e120e51ebad702ab42b4c56dd7544ddf9466d')
        self.assertEqual(baseline['count'],134)
        self.assertEqual(baseline['sha256'],'dd2009da29a0ebf5933afdddcd987adec1fc73b2d5082faf96cdb41312514e1b')
        preserved=json.dumps(evidence['results'][:baseline['count']],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')
        self.assertEqual(hashlib.sha256(preserved).hexdigest(),baseline['sha256'],'Historical launch evidence changed')
        expected={(r['repository'],r['url']):r for r in evidence['results']}
        catalog=json.loads((ROOT/'catalog/repositories.json').read_text())
        resources=[(r['name'],resource) for r in catalog['repositories'] for resource in r['resources']]
        self.assertEqual(len(resources),len(evidence['results']))
        for repository,resource in resources:
            row=expected[(repository,resource['url'])]
            self.assertEqual(resource['http_status'],row['status'])
            self.assertEqual(resource['checked_on'],row.get('checked_on',evidence.get('baseline_checked_on',evidence['checked_on'])))
            self.assertNotIn('Unverified',resource['availability'])


if __name__=='__main__':unittest.main()
