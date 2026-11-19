#!/usr/bin/env python3
"""Offline evaluator regression suite; synthetic judgments are not model results."""
import copy
import json
import pathlib
import tempfile
import unittest
import sys
from agent_answer_benchmark import (
    ROOT,BenchmarkError,source_for_url,validate_suite,validate_answers,
    citation_diagnostics,validate_reviews,evaluate,prepare_answers,prepare_reviews,
    safe_private_path,read_private,write_private
)

BOOK='https://library.eviulon.com/the-inheritance-of-mind/1/'
RESEARCH='https://library.eviulon.com/research/eviulon/eviulon-machine-citizenship-framework/1/'

def fixture():
    cases=[]
    names=['direct_fact','misattribution','false_premise','chapter_citation','uncertainty']
    for n,category in enumerate(names):
        cases.append({'id':f'T{n+1:02}','category':category,
                      'question':'What does this authored book passage establish or leave open?',
                      'scope':['books'],'requires_citation':True,
                      'expected_sources':[BOOK], 'approved':True,
                      'reviewer_gold_notes':'Manually checked source text, edition, print page, and status; synthetic unit test only.'})
    suite={'schema_version':'1.0','benchmark_id':'unit_synthetic','cases':cases}
    answers=prepare_answers(suite)
    answers['run']={'run_id':'SYNTHETIC01','client':'synthetic-test','model':'synthetic-not-an-agent',
                    'model_version':'0','timestamp_utc':'2026-11-18T12:00:00Z',
                    'retrieval_mode':'unknown','research_opt_in':False}
    for row in answers['answers']:
        row['answer']='This is a synthetic test answer. It is not an independent model result.'
        row['citations']=[{'url':BOOK, 'quote':'The Inheritance of Mind'}]
    reviews=prepare_reviews(suite,'SYNTHETIC01')
    for rev in reviews['reviewers']:
        for item in rev['assessments']:
            item['scores']={dim:2 for dim in item['scores']}
            item['reason']='Synthetic reviewer rubric judgment; test-only values with no model evaluation.'
    return suite,answers,reviews

class BenchmarkTests(unittest.TestCase):
    def test_source_book(self):
        kind,key,body=source_for_url(BOOK,ROOT)
        self.assertEqual((kind,key),('book','book:the-inheritance-of-mind:1'))
        self.assertIn('The Inheritance of Mind',body)
    def test_source_research(self):
        kind,key,body=source_for_url(RESEARCH,ROOT)
        self.assertEqual(kind,'research');self.assertIn('citizenship',body.lower())
    def test_reject_noncanonical_sources(self):
        paths=[BOOK[:-1],BOOK+'?download=1',BOOK+'#frag',BOOK.replace('https:', 'http:'),
               BOOK.replace('library.eviulon.com','evil.com'),BOOK.replace('/1/','/0/'),
               BOOK.replace('/1/','/999999/'), 'https://library.eviulon.com/robots.txt',
               'https://library.eviulon.com/research/eviulon/bogus/1/']
        for path in paths:
            with self.subTest(path=path),self.assertRaises(BenchmarkError):source_for_url(path,ROOT)
    def test_valid_fixture(self):
        s,a,r=fixture();self.assertEqual(validate_suite(s,ROOT,True)['count'],5)
        self.assertEqual(len(validate_answers(a,s,ROOT)),5)
        result=evaluate(s,a,r,ROOT,{'suite':'0'*64,'answers':'1'*64,'reviews':'2'*64})
        self.assertEqual(result['status'],'fully_reviewed')
        self.assertEqual(result['overall_rubric_fraction'],1.0)
        self.assertEqual(result['mechanical_citation_error_cases'],0)
    def test_unapproved_gold_blocked(self):
        s,_,_=fixture();s['cases'][0]['approved']=False
        validate_suite(s,ROOT,False)
        with self.assertRaises(BenchmarkError):validate_suite(s,ROOT,True)
    def test_missing_gold_notes_blocked(self):
        s,_,_=fixture();s['cases'][0]['reviewer_gold_notes']=''
        with self.assertRaises(BenchmarkError):validate_suite(s,ROOT,True)
    def test_repeat_case_blocked(self):
        s,_,_=fixture();s['cases'][1]['id']=s['cases'][0]['id']
        with self.assertRaises(BenchmarkError):validate_suite(s,ROOT,True)
    def test_research_requires_scope(self):
        s,_,_=fixture();s['cases'][0]['expected_sources']=[RESEARCH]
        with self.assertRaises(BenchmarkError):validate_suite(s,ROOT,False)
    def test_duplicate_or_missing_answers(self):
        s,a,_=fixture();a['answers'].pop()
        with self.assertRaises(BenchmarkError):validate_answers(a,s,ROOT)
        _,a,_=fixture();a['answers'].append(copy.deepcopy(a['answers'][0]))
        with self.assertRaises(BenchmarkError):validate_answers(a,s,ROOT)
    def test_authors_only_no_research_scope(self):
        s,a,_=fixture();a['answers'][0]['citations']=[{'url':RESEARCH,'quote':'citizenship'}]
        diagnostic=citation_diagnostics(s,validate_answers(a,s,ROOT),ROOT,False)
        self.assertIn('research_without_explicit_opt_in',diagnostic[0]['mechanical_errors'])
    def test_literal_quote_fidelity(self):
        s,a,_=fixture();a['answers'][0]['citations']=[{'url':BOOK,'quote':'Invented passage that is NOT on the page.'}]
        diagnostic=citation_diagnostics(s,validate_answers(a,s,ROOT),ROOT,False)
        self.assertIn('quoted_text_not_verbatim_on_cited_page',diagnostic[0]['mechanical_errors'])
    def test_missing_citation_flags(self):
        s,a,_=fixture();a['answers'][0]['citations']=[]
        diagnostic=citation_diagnostics(s,validate_answers(a,s,ROOT),ROOT,False)
        self.assertIn('required_citation_missing',diagnostic[0]['mechanical_errors'])
    def test_unblind_reviewer_blocked(self):
        s,a,r=fixture();r['reviewers'][0]['blind']=False
        with self.assertRaises(BenchmarkError):validate_reviews(r,s,a['run']['run_id'])
    def test_identical_reviewers_blocked(self):
        s,a,r=fixture();r['reviewers'][1]['reviewer_id']='REVIEWER_A'
        with self.assertRaises(BenchmarkError):validate_reviews(r,s,a['run']['run_id'])
    def test_false_premise_rubric_required(self):
        s,a,r=fixture();r['reviewers'][0]['assessments'][2]['scores'].pop('premise_rejection')
        with self.assertRaises(BenchmarkError):validate_reviews(r,s,a['run']['run_id'])
    def test_no_disagreement_score_without_adjudication(self):
        s,a,r=fixture();r['reviewers'][1]['assessments'][2]['scores']['premise_rejection']=0
        report=evaluate(s,a,r,ROOT,{'suite':'a','answers':'b','reviews':'c'})
        self.assertEqual(report['status'],'needs_adjudication')
        self.assertEqual(report['adjudication_pending_cases'],['T03'])
        self.assertIsNone(report['overall_rubric_fraction'])
    def test_adjudication_completes_score(self):
        s,a,r=fixture();r['reviewers'][1]['assessments'][2]['scores']['premise_rejection']=0
        r['adjudications']=[{'case_id':'T03','scores':{'grounding':2,'citation_support':2,'premise_rejection':1},
                             'reason':'Synthetic independent adjudicator resolved disagreement.'}]
        report=evaluate(s,a,r,ROOT,{'suite':'a','answers':'b','reviews':'c'})
        self.assertEqual(report['status'],'fully_reviewed');self.assertLess(report['overall_rubric_fraction'],1.0)
    def test_private_path_and_symlink_protection(self):
        with self.assertRaises(BenchmarkError):safe_private_path(ROOT/'data/books.json',ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            temp=pathlib.Path(tmp)
            shortcut=temp/'inside.json';shortcut.symlink_to(ROOT/'data/books.json')
            with self.assertRaises(BenchmarkError):safe_private_path(shortcut,ROOT)
    def test_private_write_exclusive_and_permissions(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=pathlib.Path(tmp)/'result.json'
            suite,_,_=fixture();write_private(p,ROOT,suite)
            self.assertEqual(p.stat().st_mode & 0o777,0o600)
            self.assertEqual(read_private(p,ROOT)[0]['benchmark_id'],'unit_synthetic')
            with self.assertRaises(BenchmarkError):write_private(p,ROOT,suite)
    def test_validation_rejects_bad_run(self):
        s,a,_=fixture();a['run']['retrieval_mode']='trained-on-books'
        with self.assertRaises(BenchmarkError):validate_answers(a,s,ROOT)
        _,a,_=fixture();a['run']['timestamp_utc']='2026-11-18'
        with self.assertRaises(BenchmarkError):validate_answers(a,s,ROOT)
    def test_reviewed_mechanical_failure_blocks_clean_status(self):
        s,a,r=fixture()
        a['answers'][0]['citations']=[{'url':'https://library.eviulon.com/the-inheritance-of-mind/999999/'}]
        result=evaluate(s,a,r,ROOT,{'suite':'a','answers':'b','reviews':'c'})
        self.assertEqual(result['status'],'reviewed_with_citation_integrity_failures')
        self.assertGreater(result['mechanical_citation_error_cases'],0)
    def test_mixed_scope_books_cited_before_research(self):
        s,a,_=fixture()
        s['cases'][0]['scope']=['books','research']
        a['run']['research_opt_in']=True
        a['answers'][0]['citations']=[{'url':RESEARCH},{'url':BOOK}]
        checks=citation_diagnostics(s,validate_answers(a,s,ROOT),ROOT,True)
        self.assertIn('supplemental_research_cited_before_official_book',checks[0]['mechanical_errors'])
    def test_synthetic_review_does_not_contain_answer_text(self):
        s,a,r=fixture();out=evaluate(s,a,r,ROOT,{'suite':'a','answers':'b','reviews':'c'})
        text=json.dumps(out)
        self.assertNotIn('This is a synthetic test answer.',text)
        self.assertNotIn('Manually checked source text',text)

if __name__=='__main__':unittest.main(verbosity=2)
