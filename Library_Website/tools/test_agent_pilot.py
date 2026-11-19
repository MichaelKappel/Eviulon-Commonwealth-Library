#!/usr/bin/env python3
"""Offline tests only. All approval notes in these tests are SYNTHETIC fixtures."""
import copy, json, pathlib, tempfile, unittest, sys
from unittest.mock import patch
from agent_answer_benchmark import ROOT, BenchmarkError, safe_private_path, read_private, validate_suite, write_private
from generate_agent_answer_draft import build
from agent_pilot_operator import create_kit, subset_for_pilot, prompts_only
from live_agent_readiness import AgentProbe, Response, validate_target, run_probe

class PilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.source=build(ROOT)
    def test_unapproved_candidate_refused(self):
        with self.assertRaisesRegex(BenchmarkError,'not independently human-approved'):
            subset_for_pilot(self.source,2,ROOT)
    def test_balanced_approved_subset(self):
        sample=copy.deepcopy(self.source)
        counts={}
        for item in sample['cases']:
            cat=item['category'];counts[cat]=counts.get(cat,0)+1
            if counts[cat]<=2:
                item['approved']=True
                item['reviewer_gold_notes']='SYNTHETIC UNIT TEST NOTE, NOT HUMAN REVIEW OR A REAL GOLD ANSWER.'
        result=subset_for_pilot(sample,2,ROOT)
        self.assertEqual(len(result['cases']),10)
        self.assertEqual({i['category'] for i in result['cases']},set(counts))
        self.assertTrue(all(i['approved'] for i in result['cases']))
        prompt=prompts_only(result)
        self.assertEqual(prompt.count('### '),10)
        self.assertNotIn('expected_sources',prompt)
        self.assertNotIn('reviewer_gold_notes',prompt)
        self.assertNotIn('SYNTHETIC UNIT TEST NOTE',prompt)
        self.assertNotIn('https://library.eviulon.com/the-inheritance-of-mind/1/',prompt)
    def test_incomplete_category_fails_closed(self):
        sample=copy.deepcopy(self.source)
        sample['cases']=[i for i in sample['cases'] if i['category']!='uncertainty']
        with self.assertRaisesRegex(BenchmarkError,'lacks enough cases'):
            subset_for_pilot(sample,1,ROOT)
    def test_invalid_limit_rejected(self):
        for val in (-1,0,11):
            with self.subTest(val=val):
                with self.assertRaises(BenchmarkError):subset_for_pilot(self.source,val,ROOT)
    def test_creates_private_kit_mode_and_no_secret_in_agent_prompts(self):
        sample=copy.deepcopy(self.source)
        seen={}
        for item in sample['cases']:
            seen[item['category']]=seen.get(item['category'],0)+1
            if seen[item['category']]<=1:
                item['approved']=True
                item['reviewer_gold_notes']='SYNTHETIC REVIEW ENTRY FOR AUTOMATED TEST ONLY.'
        with tempfile.TemporaryDirectory() as temp:
            p=pathlib.Path(temp)
            gold=p/'unpublished-suite.json'
            write_private(gold,ROOT,sample)
            result=create_kit(gold,p/'pilot',ROOT,1)
            kit=p/'pilot'
            self.assertEqual(result['cases'],5)
            self.assertEqual(kit.stat().st_mode & 0o777,0o700)
            self.assertTrue(all(x.stat().st_mode & 0o777==0o600 for x in kit.iterdir()))
            self.assertEqual(len(list(kit.iterdir())),4)
            prompt=(kit/'AGENT_QUESTIONS_ONLY.md').read_text()
            self.assertNotIn('SYNTHETIC REVIEW ENTRY',prompt)
            self.assertNotIn('expected_sources',prompt)
            self.assertNotIn('PRIVATE_GOLD_SUBSET.json',prompt)
            original=json.loads((kit/'PRIVATE_GOLD_SUBSET.json').read_text())
            self.assertEqual(validate_suite(original,ROOT,True)['count'],5)
            answers=json.loads((kit/'agent_answers.json').read_text())
            self.assertEqual(answers['benchmark_id'],original['benchmark_id'])
            self.assertEqual(len(answers['answers']),5)
            with self.assertRaises(BenchmarkError):create_kit(gold,kit,ROOT,1)
    def test_cannot_write_kit_inside_public_root(self):
        with self.assertRaises(BenchmarkError):
            safe_private_path(ROOT/'private-pilot',ROOT)

class ProbeTests(unittest.TestCase):
    def test_canonical_host_only(self):
        self.assertEqual(validate_target('https://library.eviulon.com/'),'https://library.eviulon.com')
        self.assertEqual(validate_target('http://127.0.0.1:8911'),'http://127.0.0.1:8911')
    def test_forbid_other_hosts_or_credentials(self):
        for url in ['http://library.eviulon.com','https://evil.example','https://library.eviulon.com.evil.net',
                    'https://user:pw@library.eviulon.com','https://library.eviulon.com/secret',
                    'https://library.eviulon.com/?x=1','http://example.com:8911',
                    'http://127.0.0.1:8911/?token=secret']:
            with self.subTest(url=url):
                with self.assertRaises(ValueError):validate_target(url)
    def test_timeout_bounds(self):
        for value in (0,-5,31):
            with self.assertRaises(ValueError):AgentProbe('http://127.0.0.1:8790',value)
    def test_bad_probe_data_fails_closed(self):
        # A blocked source endpoint returning 200 must never be counted as secure.
        class FauxProbe:
            base='http://127.0.0.1:9999'
            def fetch(self,path):
                if path.startswith('/data/') or path.startswith('/tools/') or path.startswith('/src/'):
                    return Response(200,'application/json',b'{}',{})
                return Response(404,'text/plain',b'not found',{})
        report=run_probe(FauxProbe())
        self.assertEqual(report['status'],'fail')
        self.assertGreater(report['failed'],0)
        self.assertTrue(any(not x['passed'] for x in report['checks'] if x['check']=='protected_path'))
    def test_only_get_is_used(self):
        self.assertTrue('GET' in AgentProbe.fetch.__code__.co_consts)

if __name__=='__main__':unittest.main(verbosity=2)
