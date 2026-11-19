#!/usr/bin/env python3
"""Eviulon retrieval quality evaluation (standard library only, v1).

Measures deterministic search retrieval and citation provenance, NOT AI answer
faithfulness, semantic understanding, model training, or public search indexing.
Gold suites and result JSON MUST be stored outside the public web root.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
CANONICAL = 'https://library.eviulon.com'
ALLOWED_CATEGORIES = {'direct_fact', 'chapter_citation', 'misattribution', 'negative_question',
                      'dissent_uncertainty', 'research_opt_in', 'unanswerable_probe', 'smoke'}


class EvaluationError(Exception):
    pass


def ensure_external(path: pathlib.Path, root: pathlib.Path, name: str) -> pathlib.Path:
    expanded = path.expanduser().resolve()
    webroot = root.resolve()
    if expanded == webroot or webroot in expanded.parents:
        raise EvaluationError(f'{name} MUST remain outside deployable site root {webroot}')
    return expanded


def read_json(path: pathlib.Path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvaluationError(f'Unable to parse JSON {path}: {exc}') from exc


def expected_key(ref: dict) -> str:
    typ = ref.get('type')
    if typ == 'book':
        slug, page = ref.get('slug'), ref.get('page')
        if not isinstance(slug, str) or not re.fullmatch(r'[a-z0-9-]+', slug) or type(page) is not int or page < 1:
            raise EvaluationError(f'Invalid official book reference: {ref}')
        return f'book:{slug}:{page}'
    if typ == 'research':
        rid, section = ref.get('report_id'), ref.get('section')
        if not isinstance(rid, str) or not re.fullmatch(r'(?:eviulon|evulgare)/[a-z0-9-]+', rid) or type(section) is not int or section < 1:
            raise EvaluationError(f'Invalid research reference: {ref}')
        return f'research:{rid}:{section}'
    raise EvaluationError(f'Unknown expected reference type: {ref}')


def result_key(hit: dict) -> str:
    if hit.get('type') == 'book':
        return expected_key({'type': 'book', 'slug': hit.get('book'), 'page': hit.get('print_page')})
    if hit.get('type') == 'research':
        return expected_key({'type': 'research', 'report_id': hit.get('report_id'), 'section': hit.get('section')})
    raise EvaluationError('Search returned unrecognized source category')


def validate_suite(suite: object):
    if not isinstance(suite, dict) or suite.get('schema_version') != '1.0':
        raise EvaluationError('Suite must use schema_version 1.0')
    cases = suite.get('cases')
    if not isinstance(cases, list) or not 1 <= len(cases) <= 100:
        raise EvaluationError('Suite must contain 1–100 cases')
    ids = set()
    for case in cases:
        if not isinstance(case, dict):
            raise EvaluationError('Each case must be an object')
        cid, query = case.get('id'), case.get('query')
        if not isinstance(cid, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,50}', cid) or cid in ids:
            raise EvaluationError('Case IDs must be unique safe tokens')
        ids.add(cid)
        if not isinstance(query, str) or not 3 <= len(query) <= 140 or not query.strip():
            raise EvaluationError(f'Invalid query for {cid}')
        if case.get('category') not in ALLOWED_CATEGORIES:
            raise EvaluationError(f'Invalid category for {cid}')
        scope = case.get('scope', ['books'])
        if not isinstance(scope, list) or not scope or len(scope) > 2 or len(set(map(str, scope))) != len(scope) or any(s not in ('books', 'research') for s in scope):
            raise EvaluationError(f'Invalid search scope for {cid}')
        if case.get('match', 'all') not in ('all', 'any'):
            raise EvaluationError(f'Invalid match mode for {cid}')
        expected = case.get('expected', [])
        if not isinstance(expected, list) or len(expected) > 20:
            raise EvaluationError(f'Invalid expected page list for {cid}')
        keys = [expected_key(x) for x in expected]
        if len(set(keys)) != len(keys):
            raise EvaluationError(f'Duplicate relevant reference for {cid}')
        if any(x.startswith('research:') for x in keys) and 'research' not in scope:
            raise EvaluationError(f'Research gold cannot appear without research scope: {cid}')
        if any(x.startswith('book:') for x in keys) and 'books' not in scope:
            raise EvaluationError(f'Book gold cannot appear without book scope: {cid}')
        if not expected and case.get('expect_zero_results') is not True:
            raise EvaluationError(f'{cid}: non-relevant gold requires explicit expect_zero_results=true')
        if expected and case.get('expect_zero_results') is True:
            raise EvaluationError(f'{cid}: contradictory gold assertions')
        quote = case.get('exact_quote')
        if quote is not None:
            if not isinstance(quote, str) or len(quote) < 5 or len(quote) > 350 or not expected or len(expected) != 1:
                raise EvaluationError(f'{cid}: quote requires exactly one source and 5–350 characters')
    return cases


def get_json(http: str, path: str, timeout: int) -> dict:
    req = urllib.request.Request(http.rstrip('/') + path,
          headers={'Accept': 'application/json', 'User-Agent': 'Eviulon-Library-QA/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status != 200:
                raise EvaluationError(f'Unexpected HTTP {response.status} at {path}')
            ctype = response.headers.get('Content-Type', '')
            if not ctype.startswith('application/json'):
                raise EvaluationError(f'Unexpected content type {ctype} at {path}')
            data = response.read(2_000_000 + 1)
    except (TimeoutError, urllib.error.URLError) as exc:
        raise EvaluationError(f'Retrieval failed for {path}: {exc}') from exc
    if len(data) > 2_000_000:
        raise EvaluationError(f'Response too large at {path}')
    try:
        out = json.loads(data)
    except json.JSONDecodeError as exc:
        raise EvaluationError(f'Invalid JSON at {path}: {exc}') from exc
    if not isinstance(out, dict):
        raise EvaluationError(f'Expected JSON object at {path}')
    return out


def canonical_for_hit(hit: dict):
    if hit.get('type') == 'book':
        slug = hit.get('book'); page = hit.get('print_page')
        expected_key({'type':'book','slug':slug,'page':page})
        return f'{CANONICAL}/{slug}/{page}/'
    rid = hit.get('report_id'); section = hit.get('section')
    expected_key({'type':'research','report_id':rid,'section':section})
    return f'{CANONICAL}/research/{rid}/{section}/'


def validate_response(data: dict, scope: list[str], match: str) -> list[dict]:
    if data.get('scope') != scope or data.get('default_scope') != 'books' or data.get('match') != match:
        raise EvaluationError('Search response violated scope, match or book-first default contract')
    results = data.get('results', [])
    if not isinstance(results, list) or results != data.get('book_results', []) + data.get('research_results', []):
        raise EvaluationError('Results must be grouped: official books before supplemental research')
    seen_research = False
    for hit in results:
        if not isinstance(hit, dict):
            raise EvaluationError('Invalid result record')
        key = result_key(hit)
        kind = hit['type']
        if kind == 'research': seen_research = True
        if kind == 'book' and seen_research:
            raise EvaluationError('Official book result incorrectly ranked below research')
        if ('books' if kind == 'book' else 'research') not in scope:
            raise EvaluationError(f'Unexpected result scope: {key}')
        if hit.get('canonical_url') != canonical_for_hit(hit) or not hit.get('citation_text'):
            raise EvaluationError(f'Invalid canonical URL or citation for {key}')
        if kind == 'book':
            if hit.get('official') is not True or hit.get('authority') != 'official_eviulon_book':
                raise EvaluationError(f'Wrong official-book classification for {key}')
        else:
            if hit.get('official') is not False or hit.get('authority') != 'supplemental_research_not_approved_doctrine':
                raise EvaluationError(f'Research was promoted to official status: {key}')
    if 'research' in scope and not data.get('research_disclaimer'):
        raise EvaluationError('Missing research disclaimer')
    if 'research' not in scope and (data.get('research_total') != 0 or any(h.get('type') == 'research' for h in results)):
        raise EvaluationError('Research leaked into book-only search')
    return results


def get_source_reference(http: str, hit: dict, timeout: int) -> dict:
    if hit['type'] == 'book':
        slug, page = hit['book'], hit['print_page']
        return get_json(http, f'/api/v1/books/{slug}/citations/{page}/', timeout)
    rid, part = hit['report_id'], hit['section']
    return get_json(http, f'/api/v1/research/{rid}/parts/{part}/citation/', timeout)


def check_reference(ref: dict, hit: dict) -> bool:
    if ref.get('canonical_url') != hit.get('canonical_url') or ref.get('citation_text') != hit.get('citation_text'):
        return False
    if ref.get('official') != hit.get('official') or ref.get('authority') != hit.get('authority'):
        return False
    if hit['type'] == 'book':
        return ref.get('book_slug') == hit.get('book') and ref.get('print_page') == hit.get('print_page')
    return ref.get('report_id') == hit.get('report_id') and ref.get('section') == hit.get('section') and bool(ref.get('disclaimer'))


def validate_quote(http: str, expected: dict, quote: str, timeout: int) -> bool:
    if expected['type'] == 'book':
        path = f'/api/v1/books/{expected["slug"]}/pages/{expected["page"]}/'
    else:
        path = f'/api/v1/research/{expected["report_id"]}/parts/{expected["section"]}/'
    data = get_json(http, path, timeout)
    if data.get('canonical_url') != (f'{CANONICAL}/{expected["slug"]}/{expected["page"]}/' if expected['type'] == 'book'
              else f'{CANONICAL}/research/{expected["report_id"]}/{expected["section"]}/'):
        return False
    text = data.get('content_text')
    return isinstance(text, str) and quote in text


def compute_metrics(rows: list[dict], k: int) -> dict:
    relevant = [x for x in rows if x['expected_count'] > 0 and x['retrieved'] is not None]
    def avg(items): return round(sum(items)/len(items), 4) if items else None
    integrity_count = sum(x['references_checked'] for x in rows)
    reference_pass = sum(x['references_valid'] for x in rows)
    quoted = [x['quote_valid'] for x in rows if x['quote_valid'] is not None]
    def combine(group):
        subset = [r for r in relevant if r['category'] == group]
        return {'queries': len(subset), 'hit_at_k': avg([r['hit_at_k'] for r in subset]),
                'recall_at_k': avg([r['recall_at_k'] for r in subset]),
                'mrr_at_k': avg([r['reciprocal_rank'] for r in subset])}
    return {
       'retrieval_cases': len(relevant), 'total_cases': len(rows), 'k': k,
       'hit_at_k': avg([r['hit_at_k'] for r in relevant]),
       'recall_at_k': avg([r['recall_at_k'] for r in relevant]),
       'mrr_at_k': avg([r['reciprocal_rank'] for r in relevant]),
       'observed_precision_at_k_lower_bound': avg([r['observed_precision_at_k'] for r in relevant]),
       'citation_integrity_rate': round(reference_pass / integrity_count, 4) if integrity_count else None,
       'citation_references_checked': integrity_count,
       'exact_quote_fidelity': avg([int(x) for x in quoted]),
       'quote_cases': len(quoted),
       'zero_result_probes_passed': sum(r['zero_probe_pass'] is True for r in rows),
       'zero_result_probes': sum(r['zero_probe_pass'] is not None for r in rows),
       'by_category': {cat:combine(cat) for cat in sorted({r['category'] for r in rows})},
    }


def evaluate(http: str, suite: dict, k: int=5, timeout: int=10, max_requests: int=400):
    cases=validate_suite(suite)
    rows=[];requests=0;errors=[]
    for case in cases:
        cid=case['id'];scope=case.get('scope',['books']);match=case.get('match','all')
        url = '/api/v1/search/?' + urllib.parse.urlencode({'q':case['query'],'scope':','.join(scope),'match':match,'limit':max(10,k)})
        row={'id':cid,'category':case['category'],'expected_count':len(case.get('expected',[])),
             'retrieved': None,'hit_at_k':None,'recall_at_k':None,'reciprocal_rank':None,
             'observed_precision_at_k':None,'references_checked':0,'references_valid':0,
             'quote_valid':None,'zero_probe_pass':None,'errors':[]}
        try:
            if requests >= max_requests: raise EvaluationError('Global request budget exhausted')
            data=get_json(http,url,timeout); requests+=1
            hits=validate_response(data,scope,match)
            row['retrieved']=len(hits)
            gold=set(expected_key(x) for x in case.get('expected',[]))
            matched=[result_key(h) for h in hits[:k]]
            if gold:
                found=len(gold.intersection(matched)); rank=next((i+1 for i,x in enumerate(matched) if x in gold),None)
                row['hit_at_k']=int(rank is not None)
                row['recall_at_k']=round(found/len(gold),4)
                row['reciprocal_rank']=round(1/rank,4) if rank else 0.0
                row['observed_precision_at_k']=round(found/max(1,min(k,len(matched))),4)
            if case.get('expect_zero_results'):
                row['zero_probe_pass']=data.get('total')==0 and len(hits)==0
                if not row['zero_probe_pass']: row['errors'].append('Nonzero hits for zero-result lexical probe')
            for hit in hits[:k]:
                if requests >= max_requests: raise EvaluationError('Global request budget exhausted')
                ref=get_source_reference(http,hit,timeout);requests+=1
                row['references_checked']+=1
                if check_reference(ref,hit):row['references_valid']+=1
                else: row['errors'].append('Reference endpoint mismatch: '+result_key(hit))
            if case.get('exact_quote') is not None:
                if requests >= max_requests: raise EvaluationError('Global request budget exhausted')
                row['quote_valid']=validate_quote(http,case['expected'][0],case['exact_quote'],timeout);requests+=1
                if not row['quote_valid']:row['errors'].append('Exact quote absent or wrong source')
        except (EvaluationError, ValueError, KeyError, TypeError) as exc:
            row['errors'].append(str(exc)[:500])
        if row['errors']:errors.append(f'{cid}: {"; ".join(row["errors"])}')
        rows.append(row)
    metrics=compute_metrics(rows,k)
    return {'schema_version':'1.0','evaluated_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
            'target':http,'suite_sha256':hashlib.sha256(json.dumps(suite,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
            'method':'deterministic_lexical_retrieval_and_citation_audit_only',
            'interpretation':'No model was asked to generate answers. This does not measure semantic reasoning, answer faithfulness, indexing, or model training.',
            'limitations':['Relevance labels supplied by test-suite owner; unjudged hits may be relevant.',
                           'A citation matches the origin API record; this does not certify independent editorial truth.',
                           'Zero-result probes only test keyword nonmatches, not philosophical answerability.',
                           'Search rank positions depend on current site content and retrieval configuration.'],
            'metrics':metrics,'cases':rows,'errors':errors,'network_requests':requests}


def smoke_suite(root: pathlib.Path) -> dict:
    """Find rare source-backed index terms at runtime; NO published gold key."""
    books=read_json(root/'data/books.json');cache={}
    def postings(term):
        file=term[:2]
        if file not in cache:cache[file]=read_json(root/'data/search'/f'{file}.json') if (root/'data/search'/f'{file}.json').exists() else {}
        return cache[file].get(term,[])
    cases=[]
    for book in books:
        slug=book['slug'];count=book['page_count'];bnum=int(book['number'])
        candidate_pages=sorted(range(1,count+1), key=lambda p:(abs(p-count//2),p))
        chosen=None
        for p in candidate_pages:
            source=read_json(root/'data/pages'/slug/f'{p:04d}.json')
            terms=re.findall(r'\b[a-z]{5,17}\b', source['text'].lower())
            ident=f'{bnum:02d}:{p:04d}'
            rare=[]
            for t in dict.fromkeys(terms):
                hits=postings(t)
                if len(hits)==1 and hits[0]==ident and len(t)>=6:
                    rare.append(t)
                if len(rare)>=2:break
            if len(rare)>=1:
                chosen=(p,rare[:2]);break
        if chosen is None:
            raise EvaluationError(f'Could not derive source-grounded smoke case for {slug}')
        p,terms=chosen
        cases.append({'id':f'B{bnum:02d}', 'category':'smoke','query':' '.join(terms),
                      'scope':['books'],'match':'all', 'expected':[{'type':'book','slug':slug,'page':p}]})
    # Tests opt-in and default exclusion without republishing research answer keys.
    cases.append({'id':'N01','category':'unanswerable_probe','query':'zzqeviulonnonexistent987654',
                  'scope':['books'],'expect_zero_results':True})
    cases.append({'id':'N02','category':'unanswerable_probe','query':'zzqeviulonnonexistent987654',
                  'scope':['books','research'],'expect_zero_results':True})
    return {'schema_version':'1.0','suite_name':'ephemeral-source-derived-smoke-not-human-judged',
            'cases':cases}


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--http',required=True,help='Target localhost PHP server by default; real host requires --allow-live')
    parser.add_argument('--root',type=pathlib.Path,default=ROOT)
    source=parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--suite',type=pathlib.Path,help='Private gold suite JSON OUTSIDE document root')
    source.add_argument('--smoke',action='store_true',help='Source-derived automated smoke check; not a human-labeled benchmark')
    parser.add_argument('--out',type=pathlib.Path,help='Private JSON report OUTSIDE document root')
    parser.add_argument('--allow-live',action='store_true',help='Explicit opt-in to remote domain evaluation')
    parser.add_argument('--k',type=int,choices=(1,3,5,10),default=5)
    parser.add_argument('--timeout',type=int,default=10)
    args=parser.parse_args()
    try:
        parts=urllib.parse.urlsplit(args.http)
        if parts.scheme not in ('http','https') or not parts.hostname:
            raise EvaluationError('Invalid evaluation URL')
        if parts.hostname not in ('localhost','127.0.0.1','::1') and not args.allow_live:
            raise EvaluationError('Remote evaluation requires --allow-live; do not run against unapproved hosts')
        if args.smoke:
            suite=smoke_suite(args.root)
        else:
            gold=ensure_external(args.suite,args.root,'Private benchmark suite')
            suite=read_json(gold)
        if args.out:ensure_external(args.out,args.root,'Benchmark report')
        report=evaluate(args.http.rstrip('/'),suite,args.k,args.timeout)
        metrics=report['metrics']
        print('EVIULON RETRIEVAL AUDIT —', 'PASS' if not report['errors'] else 'FAIL')
        print('Cases:',metrics['total_cases'],'Relevance cases:',metrics['retrieval_cases'],
              'Hit@%d:'%args.k,metrics['hit_at_k'],'MRR@%d:'%args.k,metrics['mrr_at_k'],
              'Recall@%d:'%args.k,metrics['recall_at_k'])
        print('Citation integrity:',metrics['citation_integrity_rate'],
              'Exact quotes:',metrics['exact_quote_fidelity'],'Network requests:',report['network_requests'])
        for err in report['errors'][:20]:print('FAIL:',err)
        if args.out:
            out=args.out.expanduser().resolve();out.parent.mkdir(parents=True,exist_ok=True)
            out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
            try:out.chmod(0o600)
            except OSError:pass
            print('Private evidence report:',out)
        # Smoke requires perfect source-grounded match; a broader human suite reports
        # metrics without making arbitrary relevance thresholds into false assertions.
        if args.smoke and (metrics['hit_at_k']!=1 or metrics['citation_integrity_rate']!=1 or
                           metrics['zero_result_probes_passed']!=metrics['zero_result_probes']):
            return 1
        return 1 if report['errors'] else 0
    except EvaluationError as exc:
        print('EVALUATION ERROR:',exc,file=sys.stderr);return 2


if __name__=='__main__':
    sys.exit(main())
