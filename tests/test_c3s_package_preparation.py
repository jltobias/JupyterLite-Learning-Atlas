"""Fault injection for the inline C3S browser-only preparation contract."""
import asyncio
from contextlib import redirect_stdout
import importlib
import io
import json
from pathlib import Path
import sys
import textwrap
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from import_sources import C3S_BROWSER_PACKAGES


class C3sPackagePreparation(unittest.TestCase):
    def run_setup(self,*,missing=(),recover=False,dependency=None,installer_error=None,import_error=None):
        calls=[];available={'numpy','pandas','matplotlib','plotly'}-set(missing)
        async def install(requirements):
            calls.append(list(requirements))
            if installer_error:raise installer_error
            if recover and len(calls)==2:available.update(r.split('==')[0] for r in requirements)
        def imported(name):
            if name=='pandas' and dependency:raise ModuleNotFoundError('missing dependency',name=dependency)
            if name=='pandas' and import_error:raise import_error
            if name not in available:raise ModuleNotFoundError('missing '+name,name=name)
            return SimpleNamespace()
        state={};exec('async def prepare():\n'+textwrap.indent(C3S_BROWSER_PACKAGES,'    ')+'\n    return _atlas_browser_package_status\n',state)
        output=io.StringIO()
        with patch.dict(sys.modules,{'piplite':SimpleNamespace(install=install)}),patch.object(importlib,'import_module',side_effect=imported),redirect_stdout(output):
            try:result=asyncio.run(state['prepare']())
            except BaseException as error:return calls,output.getvalue(),error
        return calls,output.getvalue(),result

    def test_normal_setup_verifies_all_modules_without_retry(self):
        calls,output,status=self.run_setup()
        self.assertEqual(calls,[['numpy','pandas','matplotlib','plotly==6.5.0']])
        self.assertEqual(status,{'retried':[],'verified':['numpy','pandas','matplotlib','plotly']});self.assertNotIn('ATLAS_PACKAGE_RETRY',output)
        library=json.loads((ROOT/'catalog/source-library.json').read_text(encoding='utf-8'))
        sections=[s for s in library['sections'] if s['course']=='c3s-atlas'];self.assertEqual(len(sections),20)
        expected=textwrap.indent(C3S_BROWSER_PACKAGES,'    ')
        for section in sections:
            self.assertEqual(sum(m.get('adapter')=='c3s-package-verification-v1' for m in section['modifications']),1)
            nb=json.loads((ROOT/'content'/section['notebook']).read_text(encoding='utf-8'))
            setup=next(c['source'] for c in nb['cells'] if c['cell_type']=='code')
            self.assertIn(expected,''.join(setup) if isinstance(setup,list) else setup)
            self.assertEqual(nb['metadata']['atlas']['source_commit'],'b41c3e1098a4fb94cef48b3044fe19c6ce7c1a1a')

    def test_nonthrowing_missing_pandas_retries_only_pandas_once_and_verifies_recovery(self):
        calls,output,status=self.run_setup(missing=['pandas'],recover=True)
        self.assertEqual(calls,[['numpy','pandas','matplotlib','plotly==6.5.0'],['pandas']])
        self.assertEqual(status['retried'],['pandas']);self.assertIn('pandas',status['verified'])
        self.assertIn("ATLAS_PACKAGE_RETRY ['pandas']",output)

    def test_permanent_missing_module_fails_after_one_verified_retry(self):
        calls,output,error=self.run_setup(missing=['pandas'])
        self.assertEqual(calls[-1],['pandas']);self.assertEqual(len(calls),2)
        self.assertIsInstance(error,RuntimeError);self.assertIn('failed after one missing-module retry: pandas',str(error))
        self.assertIn("ATLAS_PACKAGE_RETRY ['pandas']",output)

    def test_dependency_installer_and_other_import_failures_are_not_retried(self):
        for options,kind in [({'dependency':'dateutil'},RuntimeError),({'installer_error':ValueError('installer failure')},ValueError),({'import_error':ImportError('binary mismatch')},ImportError)]:
            with self.subTest(options=options):
                calls,output,error=self.run_setup(**options)
                self.assertEqual(len(calls),1);self.assertIsInstance(error,kind);self.assertNotIn('ATLAS_PACKAGE_RETRY',output)


if __name__=='__main__':unittest.main()
