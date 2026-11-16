"""No browser dependency is needed for build-time diagnostic safety tests."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from browser_runtime_diagnostics import attach_diagnostics, guarded_execution, sanitized_text, sanitized_url


class RuntimeDiagnostics(unittest.TestCase):
    def test_urls_and_console_text_discard_credentials_queries_and_fragments(self):
        url='https://user:password@cdn.example/pandas.whl?token=TOP_SECRET#credential'
        self.assertEqual(sanitized_url(url),'https://cdn.example/pandas.whl')
        text=sanitized_text('Authorization: Bearer SECRET_VALUE; api_key=ANOTHER_SECRET '+url)
        for secret in ['password','TOP_SECRET','SECRET_VALUE','ANOTHER_SECRET','?token','#credential']:
            self.assertNotIn(secret,text)
        self.assertEqual(sanitized_url('data:text/plain,SECRET'),'data:[redacted]')

    def test_failed_requests_http_and_loader_console_are_retained_without_secrets(self):
        callbacks={};context=SimpleNamespace(on=lambda name,callback:callbacks.__setitem__(name,callback))
        diagnostics=attach_diagnostics(context)
        callbacks['requestfailed'](SimpleNamespace(url='https://u:PASS@cdn.example/pandas.whl?token=SECRET',method='GET',resource_type='fetch',failure='net::ERR_FAILED'))
        callbacks['response'](SimpleNamespace(url='https://cdn.example/pandas.whl?key=SECRET',status=503))
        callbacks['console'](SimpleNamespace(type='error',text='Failed to load pandas https://cdn.example/pandas.whl?key=SECRET',location={'url':'https://cdn.example/loader.js?token=SECRET','lineNumber':5}))
        self.assertEqual(len(diagnostics['failed_requests']),1);self.assertEqual(len(diagnostics['http_errors']),1);self.assertEqual(len(diagnostics['console']),1)
        self.assertNotIn('SECRET',json.dumps(diagnostics));self.assertNotIn('PASS',json.dumps(diagnostics))

    def test_execution_guard_announces_actual_error_and_reraises_without_success(self):
        output=io.StringIO();state={}
        with redirect_stdout(output),self.assertRaises(ModuleNotFoundError):
            exec(guarded_execution("raise ModuleNotFoundError(\"No module named 'pandas'\", name='pandas')\nprint('FALSE_SUCCESS')",'UNIQUE_EXECUTION_ERROR'),state)
        self.assertIn('UNIQUE_EXECUTION_ERROR ModuleNotFoundError',output.getvalue());self.assertNotIn('FALSE_SUCCESS',output.getvalue())
        output=io.StringIO()
        with redirect_stdout(output):exec(guarded_execution("answer=42\nprint('REAL_SUCCESS')",'UNIQUE_EXECUTION_ERROR'),state)
        self.assertEqual(state['answer'],42);self.assertIn('REAL_SUCCESS',output.getvalue());self.assertNotIn('UNIQUE_EXECUTION_ERROR',output.getvalue())


if __name__=='__main__':unittest.main()
