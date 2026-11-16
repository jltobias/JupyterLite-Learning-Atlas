"""Self-contained append failures never replay or alter an existing source course."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import nbformat

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import import_sources as importer


class AppendCourses(unittest.TestCase):
    def test_prepare_failure_pin_collision_repeat_and_write_rollback_preserve_prior_bytes(self):
        work=ROOT/'_build/test-append';work.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=work) as folder:
            root=Path(folder);dest=root/'content';sources=root/'sources'
            previous={'courses':[{'slug':'existing'}],'sections':[], 'support_files':[], 'dispositions':[], 'asset_exclusions':[], 'inventory':{}}
            manifest=root/'catalog/source-library.json';manifest.parent.mkdir();manifest.write_text(json.dumps(previous))
            mirror=root/'site/data/source-library.json';mirror.parent.mkdir(parents=True);mirror.write_bytes(manifest.read_bytes())
            old=dest/'courses/existing/lesson.ipynb';old.parent.mkdir(parents=True);old.write_bytes(b'authored cells, metadata and outputs remain exact\r\n')
            checkout=sources/'c3s-atlas';(checkout/'content').mkdir(parents=True)
            nb=nbformat.v4.new_notebook(cells=[nbformat.v4.new_markdown_cell('# Fixture\n\n[Credits](credits.md)'),nbformat.v4.new_code_cell('print(2+3)')])
            nbformat.write(nb,checkout/'content/01-fixture.ipynb')
            (checkout/'content/index.md').write_text('# Source introduction\n\n[Lesson](01-fixture.ipynb)\n\n[Credits](credits.md)')
            (checkout/'content/01-fixture.md').write_text('# Source lesson narrative')
            (checkout/'content/credits.md').write_text('# Original source credits')
            (checkout/'LICENSE').write_text('Fixture license')
            originals={p:p.read_bytes() for p in [old,manifest,mirror]}
            def unchanged():self.assertEqual({p:p.read_bytes() for p in originals},originals)
            def git(args,**kwargs):
                if args[1]=='rev-parse':return 'a'*40+'\n'
                if args[1]=='status':return ''
                return b'content/01-fixture.ipynb\0content/index.md\0content/01-fixture.md\0content/credits.md\0LICENSE\0'
            with patch.multiple(importer,ROOT=root,DEST=dest,SOURCES=sources,
                APPEND_COURSES={'c3s-atlas':('Fixture','a'*40,1)},EXTRA={}),patch.object(importer.subprocess,'check_output',side_effect=git):
                with self.assertRaisesRegex(ValueError,'distinct'):importer.append_courses(['c3s-atlas','c3s-atlas'])
                with self.assertRaisesRegex(ValueError,'Unreviewed'):importer.append_courses(['unreviewed'])
                with patch.dict(importer.APPEND_COURSES,{'c3s-atlas':('Fixture','b'*40,1)}):
                    with self.assertRaisesRegex(ValueError,'Pin changed'):importer.append_courses(['c3s-atlas'])
                with patch.dict(importer.APPEND_COURSES,{'c3s-atlas':('Fixture','a'*40,2)}):
                    with self.assertRaisesRegex(ValueError,'Incomplete'):importer.append_courses(['c3s-atlas'])
                with patch.object(importer.subprocess,'check_output',side_effect=lambda args,**kw:' M content/01-fixture.ipynb' if args[1]=='status' else git(args,**kw)):
                    with self.assertRaisesRegex(ValueError,'local changes'):importer.append_courses(['c3s-atlas'])
                with patch.object(importer,'prepare_source_notebook',side_effect=ValueError('late preparation failure')):
                    with self.assertRaisesRegex(ValueError,'late preparation'):importer.append_courses(['c3s-atlas'])
                with patch.dict(importer.EXTRA,{'c3s-atlas':[('LICENSE','credits.md')]}):
                    with self.assertRaisesRegex(ValueError,'Conflicting support destination'):importer.append_courses(['c3s-atlas'])
                unchanged();self.assertFalse((dest/'courses/c3s-atlas').exists())
                # A destination collision is rejected without touching the file.
                collision=dest/'courses/c3s-atlas';collision.mkdir();(collision/'author.txt').write_text('keep')
                with self.assertRaises(FileExistsError):importer.append_courses(['c3s-atlas'])
                self.assertEqual((collision/'author.txt').read_text(),'keep');unchanged()
                (collision/'author.txt').unlink();collision.rmdir()
                write_bytes=Path.write_bytes
                def fail_mirror(path,data):
                    if path==mirror and data!=originals[mirror]:raise OSError('simulated publication mirror failure')
                    return write_bytes(path,data)
                with patch.object(Path,'write_bytes',fail_mirror):
                    with self.assertRaisesRegex(OSError,'mirror failure'):importer.append_courses(['c3s-atlas'])
                unchanged();self.assertFalse((dest/'courses/c3s-atlas').exists())
                real_open=Path.open
                for failure in ['write','close']:
                    injected=[False]
                    class BrokenStream:
                        def __init__(self,stream):self.stream=stream
                        def __enter__(self):self.stream.__enter__();return self
                        def write(self,data):
                            if failure=='write':
                                self.stream.write(data[:7]);raise OSError('injected mid-write failure')
                            return self.stream.write(data)
                        def __exit__(self,*args):
                            self.stream.__exit__(*args)
                            if failure=='close':raise OSError('injected close failure')
                    def broken_open(path,*args,**kwargs):
                        stream=real_open(path,*args,**kwargs)
                        if args and args[0]=='xb' and not injected[0]:
                            injected[0]=True;return BrokenStream(stream)
                        return stream
                    with patch.object(Path,'open',broken_open):
                        with self.assertRaisesRegex(OSError,'injected'):importer.append_courses(['c3s-atlas'])
                    unchanged();self.assertFalse((dest/'courses/c3s-atlas').exists())
                result=importer.append_courses(['c3s-atlas'])
                self.assertEqual(result['courses'][:1],previous['courses'])
                self.assertEqual(result['inventory']['imported_sections'],1)
                placements={s['local_path'] for s in result['support_files']}
                self.assertIn('courses/c3s-atlas/notices/source-documents/content/index.md',placements)
                self.assertIn('courses/c3s-atlas/notices/source-documents/content/01-fixture.md',placements)
                self.assertNotIn('courses/c3s-atlas/index.md',placements)
                self.assertNotIn('courses/c3s-atlas/01-fixture.md',placements)
                prepared=nbformat.read(dest/'courses/c3s-atlas/01-fixture.ipynb',4)
                self.assertIn('https://github.com/jltobias/Fixture/blob/'+'a'*40+'/content/credits.md',prepared.cells[1].source)
                self.assertEqual(prepared.cells[2].source,'print(2+3)')
                moved=(dest/'courses/c3s-atlas/notices/source-documents/content/index.md').read_text()
                self.assertIn('../../../01-fixture.ipynb',moved)
                self.assertEqual(old.read_bytes(),originals[old]);self.assertEqual(manifest.read_bytes(),mirror.read_bytes())
                state={p:p.read_bytes() for p in root.rglob('*') if p.is_file()}
                with self.assertRaisesRegex(ValueError,'Existing course'):importer.append_courses(['c3s-atlas'])
                self.assertEqual({p:p.read_bytes() for p in state},state)

    def test_stale_research_audit_cannot_remove_existing_courses(self):
        work=ROOT/'_build/test-append';work.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=work) as folder:
            root=Path(folder);(root/'catalog').mkdir();(root/'_research').mkdir()
            path=root/'catalog/source-library.json'
            path.write_text(json.dumps({'courses':[{'slug':'previous-course'}],'support_files':[]}))
            (root/'_research/textbook-source-audit.json').write_text(json.dumps({'repositories':[]}))
            before=path.read_bytes()
            with patch.object(importer,'ROOT',root),patch.object(sys,'argv',['import_sources.py']):
                with self.assertRaisesRegex(ValueError,'Stale research audit'):importer.main()
            self.assertEqual(path.read_bytes(),before)

    def test_four_courses_have_exact_accounting_and_runtime_boundaries(self):
        data=json.loads((ROOT/'catalog/source-library.json').read_text(encoding='utf-8'))
        for slug,(_,pin,count) in importer.APPEND_COURSES.items():
            course=next(c for c in data['courses'] if c['slug']==slug)
            self.assertEqual(course['commit'],pin);self.assertEqual(course['source_notebook_paths'],count)
            sections=[s for s in data['sections'] if s['course']==slug]
            self.assertEqual(len(sections),count)
            self.assertEqual(sum(d['course']==slug for d in data['dispositions']),count)
            self.assertTrue(all(not s['runtime']['execution_selected'] for s in sections))
            if slug=='terrio':
                self.assertTrue(all(s['runtime']['class']=='reference-only' for s in sections))
                for section in sections:
                    text=' '.join(section['runtime']['requirements'])
                    self.assertIn('Pyodide 0.29',text);self.assertIn('Atlas Pyodide 314',text)
                    self.assertIn('?path='+Path(section['source_path']).name,text)
            elif slug=='urbanity':self.assertTrue(all(s['runtime']['class']=='browser-local' for s in sections))


if __name__=='__main__':unittest.main()
