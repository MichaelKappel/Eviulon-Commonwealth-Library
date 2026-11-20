#!/usr/bin/env python3
"""Unit tests for opt-in discovery notifications; never send network requests."""
import importlib.util, pathlib, tempfile, unittest, json, contextlib,io
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('indexnow_prepare',ROOT/'tools/indexnow_prepare.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class IndexNowSafetyTests(unittest.TestCase):
    def test_default_uses_offline_book_metadata_only(self):
        with patch.object(module.urllib.request,'urlopen',side_effect=AssertionError('Unexpected network call')):
            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                self.assertEqual(module.main(['--root',str(ROOT)]),0)
            response=json.loads(stdout.getvalue())
            self.assertEqual(response['mode'],'dry-run')
            self.assertFalse(response['research_included'])
            self.assertEqual(response['url_count'],19) # site pages + 14 book landing pages
            self.assertTrue(all('/research/' not in x for x in response['urls']))
    def test_changed_files_must_be_canonical(self):
        with tempfile.TemporaryDirectory() as d:
            f=pathlib.Path(d)/'changed.txt';f.write_text('https://evil.example.com/\n')
            with self.assertRaises(ValueError):module.urls_to_publish(ROOT,'books',False,f)
    def test_book_pages_without_research(self):
        urls=module.urls_to_publish(ROOT,'book-pages',False,None)
        self.assertEqual(len(urls),1944)
        self.assertIn('https://library.eviulon.com/the-inheritance-of-mind/491/',urls)
        self.assertFalse(any('/research/' in x for x in urls))
    def test_research_requires_explicit_opt_in(self):
        with self.assertRaises(ValueError):module.urls_to_publish(ROOT,'all',False,None)
        self.assertEqual(len(module.urls_to_publish(ROOT,'all',True,None)),3729)
    def test_requires_key_before_network(self):
        with patch.object(module.urllib.request,'urlopen',side_effect=AssertionError('Unexpected network call')):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):module.main(['--root',str(ROOT),'--submit'])
    def test_page_change_filter(self):
        with tempfile.TemporaryDirectory() as d:
            f=pathlib.Path(d)/'changed.txt'
            target='https://library.eviulon.com/the-inheritance-of-mind/491/'
            f.write_text(target+'\n')
            self.assertEqual(module.urls_to_publish(ROOT,'book-pages',False,f),[target])
if __name__=='__main__':unittest.main(verbosity=2)
