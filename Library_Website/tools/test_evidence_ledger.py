#!/usr/bin/env python3
"""Self-contained evidence ledger regression suite (no live requests)."""
import csv, tempfile, unittest
from pathlib import Path
from evidence_ledger import FIELDS, validate

class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory()
        self.path=Path(self.directory.name)/'private-evidence.csv'
    def tearDown(self): self.directory.cleanup()
    def write(self, rows, headers=FIELDS):
        with self.path.open('w',newline='',encoding='utf8') as file:
            writer=csv.DictWriter(file,fieldnames=headers);writer.writeheader();writer.writerows(rows)
    def row(self,**overrides):
        row=dict(evidence_level='reachable',observed_at_utc='2026-11-18T16:30:00Z',canonical_url='https://library.eviulon.com/the-inheritance-of-mind/7/',source_or_provider='local HTTP test',status='observed',evidence_reference='private-runbook/2026-11-18.txt',reviewed_by='publisher',notes='Test synthetic fixture only')
        row.update(overrides);return row
    def test_template_empty(self):
        self.write([]);errors,counts=validate(self.path);self.assertEqual(errors,[]);self.assertEqual(counts,{})
    def test_real_structure(self):
        self.write([self.row()]);errors,counts=validate(self.path);self.assertEqual(errors,[]);self.assertEqual(counts,{'reachable':1})
    def test_bad_domain(self):
        self.write([self.row(canonical_url='https://somewhere.example/page')]);self.assertTrue(validate(self.path)[0])
    def test_training_needs_valid_level_name(self):
        self.write([self.row(evidence_level='training_maybe')]);self.assertTrue(validate(self.path)[0])
    def test_requires_provenance_fields(self):
        self.write([self.row(evidence_reference='')]);self.assertTrue(validate(self.path)[0])
    def test_requires_utc(self):
        self.write([self.row(observed_at_utc='2026-11-18T16:30:00-06:00')]);self.assertTrue(validate(self.path)[0])
    def test_private_password_in_url_rejected(self):
        self.write([self.row(canonical_url='https://user:pw@library.eviulon.com/')]);self.assertTrue(validate(self.path)[0])

if __name__=='__main__': unittest.main()
