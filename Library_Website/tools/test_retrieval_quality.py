#!/usr/bin/env python3
"""Dependency-free regression tests for the retrieval auditor contract."""
import copy
import pathlib
import tempfile
import unittest
import retrieval_quality as q


class QualityContractTests(unittest.TestCase):
    def case(self):
        return {'id':'demo_1','category':'direct_fact','query':'machine identity',
                'scope':['books'],'expected':[{'type':'book','slug':'the-inheritance-of-mind','page':42}]}

    def suite(self, case=None):return {'schema_version':'1.0','cases':[case or self.case()]}

    def hit(self):return {'type':'book','book':'the-inheritance-of-mind','print_page':42,
              'canonical_url':q.CANONICAL+'/the-inheritance-of-mind/42/',
              'authority':'official_eviulon_book','official':True,'citation_text':'source' }

    def test_valid_gold_contract(self):
        self.assertEqual(1,len(q.validate_suite(self.suite())))

    def test_duplicate_ids_rejected(self):
        source=self.case()
        with self.assertRaises(q.EvaluationError):q.validate_suite({'schema_version':'1.0','cases':[source,source]})

    def test_research_requires_opt_in(self):
        case=self.case()
        case['expected']=[{'type':'research','report_id':'evulgare/sample','section':1}]
        with self.assertRaises(q.EvaluationError):q.validate_suite(self.suite(case))

    def test_empty_gold_requires_explicit_zero_probe(self):
        case=self.case();case['expected']=[]
        with self.assertRaises(q.EvaluationError):q.validate_suite(self.suite(case))
        case['expect_zero_results']=True
        q.validate_suite(self.suite(case))

    def test_no_private_gold_in_public_root(self):
        with self.assertRaises(q.EvaluationError):q.ensure_external(q.ROOT/'docs/private.json',q.ROOT,'suite')
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(pathlib.Path(tmp)/'private.json',q.ensure_external(pathlib.Path(tmp)/'private.json',q.ROOT,'suite'))

    def test_official_book_first_contract(self):
        hit=self.hit()
        d={'scope':['books'],'match':'all','default_scope':'books','results':[hit],
           'book_results':[hit],'research_results':[],'research_total':0}
        self.assertEqual([hit],q.validate_response(d,['books'],'all'))
        d['results'][0]['official']=False
        with self.assertRaises(q.EvaluationError):q.validate_response(d,['books'],'all')

    def test_research_cannot_leak_into_books_only(self):
        hit={'type':'research','report_id':'evulgare/example','section':1,
             'canonical_url':q.CANONICAL+'/research/evulgare/example/1/',
             'citation_text':'source','authority':'supplemental_research_not_approved_doctrine','official':False}
        d={'scope':['books'],'match':'all','default_scope':'books','results':[hit],
           'book_results':[],'research_results':[hit],'research_total':1}
        with self.assertRaises(q.EvaluationError):q.validate_response(d,['books'],'all')

    def test_research_must_have_disclaimer(self):
        hit={'type':'research','report_id':'evulgare/example','section':1,
             'canonical_url':q.CANONICAL+'/research/evulgare/example/1/',
             'citation_text':'source','authority':'supplemental_research_not_approved_doctrine','official':False}
        d={'scope':['books','research'],'match':'all','default_scope':'books','results':[self.hit(),hit],
           'book_results':[self.hit()],'research_results':[hit],'research_total':1}
        with self.assertRaises(q.EvaluationError):q.validate_response(d,['books','research'],'all')
        d['research_disclaimer']='Supplemental research'
        q.validate_response(d,['books','research'],'all')

    def test_strict_canonical_urls(self):
        hit=self.hit()
        self.assertEqual(q.CANONICAL+'/the-inheritance-of-mind/42/',q.canonical_for_hit(hit))
        self.assertFalse(q.check_reference({'canonical_url':'https://wrong.example/page','citation_text':'source',
           'official':True,'authority':'official_eviulon_book','book_slug':'the-inheritance-of-mind','print_page':42},hit))

    def test_metric_calculations_and_nulls(self):
        rows=[{'id':'a','category':'smoke','expected_count':1,'retrieved':2,'hit_at_k':1,
               'recall_at_k':1.,'reciprocal_rank':.5,'observed_precision_at_k':.5,
               'references_checked':2,'references_valid':2,'quote_valid':True,'zero_probe_pass':None},
              {'id':'b','category':'unanswerable_probe','expected_count':0,'retrieved':0,
               'hit_at_k':None,'recall_at_k':None,'reciprocal_rank':None,'observed_precision_at_k':None,
               'references_checked':0,'references_valid':0,'quote_valid':None,'zero_probe_pass':True}]
        result=q.compute_metrics(rows,5)
        self.assertEqual(.5,result['mrr_at_k']);self.assertEqual(1.,result['hit_at_k']);self.assertEqual(1,result['zero_result_probes_passed']);self.assertEqual(1.,result['exact_quote_fidelity'])

    def test_no_clandestine_gold_roundtrip(self):
        bad=self.case();bad['exact_quote']='x'
        with self.assertRaises(q.EvaluationError):q.validate_suite(self.suite(bad))


if __name__=='__main__':unittest.main(verbosity=2)
