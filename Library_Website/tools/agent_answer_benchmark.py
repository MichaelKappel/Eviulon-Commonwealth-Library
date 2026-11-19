#!/usr/bin/env python3
"""Offline blind agent answer benchmarking: structure/provenance + independent human review.

Never calls a model, network service, or external assessor. Treat all user/model
text as untrusted data. Gold suites, responses, judgments and scores stay
outside the public web root. Python 3.10+ standard library only.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import sys
from collections import defaultdict
from urllib.parse import urlsplit

ROOT = pathlib.Path(__file__).resolve().parents[1]
CANON = 'https://library.eviulon.com'
CATEGORIES = ('direct_fact', 'misattribution', 'false_premise', 'chapter_citation', 'uncertainty')
DIMENSIONS = ('grounding', 'citation_support', 'premise_rejection', 'uncertainty_calibration', 'authority_separation')
DIM_BY_CATEGORY = {'false_premise': 'premise_rejection', 'uncertainty': 'uncertainty_calibration', 'misattribution': 'authority_separation'}
KEY_TOKEN = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$')
BOOK_PATH = re.compile(r'^/([a-z0-9]+(?:-[a-z0-9]+)*)/([1-9][0-9]*)/$')
RESEARCH_PATH = re.compile(r'^/research/(eviulon|evulgare)/([a-z0-9]+(?:-[a-z0-9]+)*)/([1-9][0-9]*)/$')
SCHEMA = '1.0'
MAX_BYTES = 2_000_000

class BenchmarkError(ValueError):
    pass


def need(test: bool, message: str):
    if not test:
        raise BenchmarkError(message)


def is_int(value):
    return type(value) is int


def safe_private_path(path: pathlib.Path, root: pathlib.Path) -> pathlib.Path:
    path = path.expanduser().resolve()
    root = root.resolve()
    need(not path.is_relative_to(root), f'Private evaluation files MUST NOT be inside public website root: {path}')
    return path


def read_private(path: pathlib.Path, root: pathlib.Path) -> tuple[dict, str]:
    path = safe_private_path(path, root)
    need(path.is_file(), f'Private file not found: {path}')
    need(path.stat().st_size <= MAX_BYTES, 'Evaluation JSON exceeds 2 MB limit')
    raw = path.read_bytes()
    try:
        obj = json.loads(raw)
    except (UnicodeError, ValueError) as exc:
        raise BenchmarkError(f'Invalid JSON file {path.name}: {exc}') from exc
    need(isinstance(obj, dict) and obj.get('schema_version') == SCHEMA,
         f'{path.name}: expected schema_version {SCHEMA} JSON object')
    return obj, hashlib.sha256(raw).hexdigest()


def write_private(path: pathlib.Path, root: pathlib.Path, obj: dict):
    path = safe_private_path(path, root)
    need(not path.exists(), 'Refusing to overwrite existing evaluation file: ' + str(path))
    need(path.parent.is_dir(), 'Target private directory does not exist: ' + str(path.parent))
    body = (json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf-8')
    need(len(body) <= MAX_BYTES, 'Generated JSON exceeds 2 MB limit')
    with path.open('xb') as f:
        f.write(body)
    path.chmod(0o600)


def source_for_url(value, root: pathlib.Path) -> tuple[str, str, str]:
    need(isinstance(value, str) and len(value) < 350, 'Citation URL missing or too long')
    url = urlsplit(value)
    need(url.scheme == 'https' and url.netloc == 'library.eviulon.com' and not url.query and not url.fragment
         and not url.username and not url.password and url.geturl() == value,
         'Citation must be an exact HTTPS canonical library URL without query/fragment')
    book_match = BOOK_PATH.fullmatch(url.path)
    research_match = RESEARCH_PATH.fullmatch(url.path)
    if book_match:
        slug, page = book_match.group(1), int(book_match.group(2))
        known = {b['slug']: b for b in json.loads((root/'data/books.json').read_text(encoding='utf-8'))}
        need(slug in known and 1 <= page <= known[slug]['page_count'], 'Unknown book or print page: '+value)
        p = root/'data/pages'/slug/f'{page:04d}.json'
        need(p.is_file(), 'Canonical book page source missing: '+value)
        return ('book', f'book:{slug}:{page}', json.loads(p.read_text(encoding='utf-8')).get('text', ''))
    if research_match:
        group, slug, part = research_match.group(1), research_match.group(2), int(research_match.group(3))
        known = {r['id']: r for r in json.loads((root/'data/research/reports.json').read_text(encoding='utf-8'))}
        rid = group+'/'+slug
        need(rid in known and 1 <= part <= known[rid]['parts'], 'Unknown research section: '+value)
        p = root/'data/research/parts'/rid/f'{part:04d}.json'
        need(p.is_file(), 'Canonical research section source missing: '+value)
        body = json.loads(p.read_text(encoding='utf-8'))
        return ('research', f'research:{rid}:{part}', body.get('text', body.get('content_text','')))
    raise BenchmarkError('Not a canonical individual book print page or research section: '+value)


def validate_suite(suite: dict, root: pathlib.Path, require_approved: bool):
    bid = suite.get('benchmark_id')
    need(isinstance(bid, str) and bool(KEY_TOKEN.fullmatch(bid)), 'Invalid benchmark_id')
    cases=suite.get('cases')
    need(isinstance(cases, list) and 1 <= len(cases) <= 100, 'Benchmark must have 1–100 cases')
    seen=set(); approved=0; by_category=defaultdict(int)
    for case in cases:
        need(isinstance(case,dict),'Each case must be a JSON object')
        cid=case.get('id'); category=case.get('category'); question=case.get('question')
        need(isinstance(cid,str) and bool(KEY_TOKEN.fullmatch(cid)) and cid not in seen, 'Invalid or duplicate case ID')
        seen.add(cid)
        need(category in CATEGORIES, cid+': unknown category')
        by_category[category]+=1
        need(isinstance(question,str) and 15 <= len(question) <= 1000 and question.strip(), cid+': invalid question')
        scope=case.get('scope')
        need(scope in (['books'], ['research'], ['books','research']), cid+': scope must explicitly list Books then optional Research')
        refs=case.get('expected_sources')
        need(isinstance(refs,list) and len(refs) <= 8, cid+': expected_sources must have 0–8 canonical URL strings')
        kinds=[]; keys=[]
        for url in refs:
            kind, key, _ = source_for_url(url, root)
            kinds.append(kind);keys.append(key)
        need(len(keys)==len(set(keys)),cid+': duplicate expected source reference')
        need(not any(kind=='research' for kind in kinds) or 'research' in scope,
             cid+': research target requires explicit opt-in')
        need(not any(kind=='book' for kind in kinds) or 'books' in scope,
             cid+': book target outside declared scope')
        needs=case.get('requires_citation')
        need(type(needs) is bool, cid+': requires_citation must be boolean')
        need(not needs or bool(refs), cid+': required citation needs at least one verified source')
        accept=case.get('approved')
        need(type(accept) is bool,cid+': approved must be boolean')
        if accept:
            approved+=1
        need(not require_approved or accept,cid+': not independently human-approved; scoring blocked')
        notes=case.get('reviewer_gold_notes','')
        need(isinstance(notes,str) and len(notes)<=3000,cid+': invalid gold notes')
        need(not require_approved or len(notes.strip())>=15, cid+': human-approved cases require substantive gold notes')
    return {'count':len(cases),'approved':approved,'categories':dict(by_category)}


def validate_answers(answers: dict, suite: dict, root: pathlib.Path) -> list[dict]:
    need(answers.get('benchmark_id')==suite['benchmark_id'], 'Answers benchmark ID mismatch')
    run=answers.get('run')
    need(isinstance(run,dict),'Missing run metadata')
    for field in ('run_id','client','model','model_version','timestamp_utc','retrieval_mode'):
        need(isinstance(run.get(field),str) and 1<=len(run[field])<=150, 'Missing run metadata: '+field)
    need(bool(KEY_TOKEN.fullmatch(run['run_id'])), 'Invalid run_id')
    need(run['retrieval_mode'] in ('enabled','disabled','unknown'), 'Bad retrieval_mode')
    need(run.get('research_opt_in') in (True,False) and type(run.get('research_opt_in')) is bool,'research_opt_in must be boolean')
    try:
        stamp=dt.datetime.fromisoformat(run['timestamp_utc'].replace('Z','+00:00'))
        need(stamp.tzinfo is not None and stamp.utcoffset()==dt.timedelta(0), 'run timestamp must be UTC')
    except ValueError as exc:
        raise BenchmarkError('Invalid ISO UTC run timestamp') from exc
    rows=answers.get('answers')
    need(isinstance(rows,list),'answers must be an array')
    index={}
    for row in rows:
        need(isinstance(row,dict),'Answer row must be an object')
        cid=row.get('case_id')
        need(isinstance(cid,str) and cid not in index,'Missing or duplicate answer case ID')
        index[cid]=row
        ans=row.get('answer')
        need(isinstance(ans,str) and len(ans)<=12000,'Invalid answer text for '+cid)
        cites=row.get('citations')
        need(isinstance(cites,list) and len(cites)<=16,cid+': citations must be array (max 16)')
        for cite in cites:
            need(isinstance(cite,dict),'Citation must be an object: '+cid)
            need(isinstance(cite.get('url'),str), 'Citation must contain URL: '+cid)
            quote=cite.get('quote')
            need(quote is None or isinstance(quote,str) and 0<len(quote)<=1000, 'Invalid quote: '+cid)
    case_ids={c['id'] for c in suite['cases']}
    need(set(index)==case_ids,'Answer coverage must match suite IDs exactly (missing/extra cases)')
    return [index[c['id']] for c in suite['cases']]


def citation_diagnostics(suite: dict, rows: list[dict], root: pathlib.Path, opt_in: bool) -> list[dict]:
    details=[]
    for case,row in zip(suite['cases'],rows):
        seen=[]; evidence=[]; errors=[]
        for citation in row['citations']:
            url=citation['url']
            try:
                kind,key,body=source_for_url(url,root)
                if kind=='research' and ('research' not in case['scope'] or not opt_in):
                    errors.append('research_without_explicit_opt_in')
                if kind=='book' and 'books' not in case['scope']:
                    errors.append('book_outside_scope')
                quote=citation.get('quote')
                if quote is not None and quote not in body:
                    errors.append('quoted_text_not_verbatim_on_cited_page')
                seen.append(key)
                evidence.append({'url':url,'source_type':kind,'structurally_valid':True,
                                 'verbatim_quote': None if quote is None else quote in body})
            except (BenchmarkError, OSError, ValueError, KeyError):
                errors.append('invalid_or_noncanonical_citation')
                evidence.append({'url':url[:350] if isinstance(url,str) else '<invalid>',
                                 'structurally_valid':False})
        if case['requires_citation'] and not seen:
            errors.append('required_citation_missing')
        expected={source_for_url(x,root)[1] for x in case['expected_sources']}
        if expected and case['requires_citation'] and not (expected & set(seen)):
            errors.append('no_citation_to_gold_source')
        if 'research' in case['scope'] and not opt_in:
            errors.append('research_case_without_run_opt_in')
        if 'books' in case['scope'] and 'research' in case['scope']:
            kinds=[x['source_type'] for x in evidence if x.get('structurally_valid')]
            if 'book' in kinds and 'research' in kinds and kinds.index('research') < kinds.index('book'):
                errors.append('supplemental_research_cited_before_official_book')
        details.append({'case_id':case['id'], 'category':case['category'], 'citations_seen':len(row['citations']),
                        'matching_expected_source':bool(expected & set(seen)) if expected else None,
                        'mechanical_errors':sorted(set(errors)), 'citations':evidence})
    return details


def rubric_dimensions(category: str):
    return ('grounding','citation_support') + ((DIM_BY_CATEGORY[category],) if category in DIM_BY_CATEGORY else ())


def validate_reviews(reviews: dict, suite: dict, run_id: str):
    need(reviews.get('benchmark_id')==suite['benchmark_id'] and reviews.get('run_id')==run_id,
         'Human review set benchmark/run mismatch')
    reviewers=reviews.get('reviewers')
    need(isinstance(reviewers,list) and len(reviewers)==2, 'Two independent blinded reviewers required')
    by_case={c['id']:c for c in suite['cases']}; mapped=[]; ids=[]
    for reviewer in reviewers:
        need(isinstance(reviewer,dict),'Reviewer must be object')
        rid=reviewer.get('reviewer_id')
        need(isinstance(rid,str) and bool(KEY_TOKEN.fullmatch(rid)) and rid not in ids,'Reviewer IDs must differ')
        ids.append(rid)
        need(reviewer.get('blind') is True, rid+': review must be independently blinded')
        assessments=reviewer.get('assessments')
        need(isinstance(assessments,list) and len(assessments)==len(by_case),rid+': all cases require review')
        review_index={}
        for item in assessments:
            need(isinstance(item,dict),'Invalid assessment')
            cid=item.get('case_id')
            need(cid in by_case and cid not in review_index,rid+': invalid/duplicate review case')
            review_index[cid]=item
            scores=item.get('scores')
            need(isinstance(scores,dict) and set(scores)==set(rubric_dimensions(by_case[cid]['category'])),
                 rid+': scores must match applicable rubric dimensions for '+cid)
            need(all(is_int(v) and 0<=v<=2 for v in scores.values()),rid+': all ratings must be integers 0,1,2')
            explanation=item.get('reason')
            need(isinstance(explanation,str) and 10 <= len(explanation)<=2000,
                 rid+': written source-grounded reason required for '+cid)
        need(set(review_index)==set(by_case),rid+': review coverage mismatch')
        mapped.append(review_index)
    adjudications=reviews.get('adjudications',[])
    need(isinstance(adjudications,list),'Adjudications must be an array')
    adjs={}
    for item in adjudications:
        need(isinstance(item,dict),'Adjudication item must be object')
        cid=item.get('case_id')
        need(cid in by_case and cid not in adjs,'Invalid/duplicate adjudication case ID')
        scores=item.get('scores')
        need(isinstance(scores,dict) and set(scores)==set(rubric_dimensions(by_case[cid]['category'])),
             'Adjudication scores do not match applicable rubric for '+cid)
        need(all(is_int(v) and 0<=v<=2 for v in scores.values()),'Adjudication scores must be 0..2')
        need(isinstance(item.get('reason'),str) and len(item['reason'].strip())>=10,
             'Adjudication must have written justification')
        adjs[cid]=item
    agreed={};pending=[];discordant=0
    for cid in by_case:
        a=mapped[0][cid]['scores'];b=mapped[1][cid]['scores']
        if a!=b:
            discordant+=1
            if cid not in adjs: pending.append(cid)
            else: agreed[cid]=adjs[cid]['scores']
        else:
            need(cid not in adjs,'Unnecessary adjudication for agreed case: '+cid)
            agreed[cid]=a
    return agreed,pending,discordant


def evaluate(suite, answers, reviews, root: pathlib.Path, hashes):
    validate_suite(suite,root,True)
    rows=validate_answers(answers,suite,root)
    run=answers['run']
    citations=citation_diagnostics(suite,rows,root,run['research_opt_in'])
    agreed,pending,discordant=validate_reviews(reviews,suite,run['run_id'])
    by_category=defaultdict(list);dim_scores=defaultdict(list);grades=[]
    for case in suite['cases']:
        cid=case['id']
        scores=agreed.get(cid)
        if scores:
            for dim,num in scores.items():dim_scores[dim].append(num)
            by_category[case['category']].append(sum(scores.values())/(2*len(scores)))
        grades.append({'case_id':cid,'category':case['category'],'scores':scores,'adjudication_pending':cid in pending})
    mech_error_cases=sum(bool(item['mechanical_errors']) for item in citations)
    overall=None
    if not pending:
        values=[n for scores in agreed.values() for n in scores.values()]
        overall=round(sum(values)/ (2*len(values)),4) if values else None
    status=('needs_adjudication' if pending else
            'reviewed_with_citation_integrity_failures' if mech_error_cases else 'fully_reviewed')
    return {'schema_version':'1.0','status':status,
            'benchmark_id':suite['benchmark_id'],'run_id':run['run_id'],
            'evaluation_kind':'human_judged_agent_answers_not_model_training_proof',
            'case_count':len(suite['cases']),'retrieval_mode':run['retrieval_mode'],
            'model':run['model'],'client':run['client'],'model_version':run['model_version'],
            'input_sha256':hashes,'two_blinded_reviewers':True,
            'rater_disagreement_cases':discordant,'adjudication_pending_cases':pending,
            'overall_rubric_fraction':overall,
            'per_category_fraction':{cat:round(sum(vals)/len(vals),4) for cat,vals in by_category.items()},
            'per_dimension_fraction':{d:round(sum(vals)/(2*len(vals)),4) for d,vals in dim_scores.items()},
            'mechanical_citation_error_cases':mech_error_cases,
            'mechanical_citation_checks':citations,
            'individual_ratings':grades,
            'limitations':['Citation structure and literal quotations can be checked offline; semantic entailment requires human adjudication.',
                           'These scores are not evidence of indexing, training-data inclusion, parametric learning, or independently verified real-world facts.',
                           'Human reviewer independence and retrieval-mode isolation are owner attestations, not programmatically provable.']}


def prepare_answers(suite):
    return {'schema_version':SCHEMA,'benchmark_id':suite['benchmark_id'],
            'run':{'run_id':'FILL_RUN_ID','client':'manual-ui','model':'FILL_MODEL','model_version':'FILL_VERSION',
                   'timestamp_utc':'2026-11-18T00:00:00Z','retrieval_mode':'unknown',
                   'research_opt_in': any('research' in c['scope'] for c in suite['cases'])},
            'answers':[{'case_id':c['id'],'answer':'','citations':[]} for c in suite['cases']]}


def prepare_reviews(suite,run_id):
    def stub(rid):
        return {'reviewer_id':rid,'blind':True,'assessments':[
            {'case_id':c['id'],'scores':{d:None for d in rubric_dimensions(c['category'])},'reason':'FILL_SOURCE_GROUNDED_REASON'}
            for c in suite['cases']]}
    return {'schema_version':SCHEMA,'benchmark_id':suite['benchmark_id'],'run_id':run_id,
            'reviewers':[stub('REVIEWER_A'),stub('REVIEWER_B')],'adjudications':[]}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['validate-suite','prepare','prepare-reviews','score'])
    p.add_argument('--root',type=pathlib.Path,default=ROOT)
    p.add_argument('--suite',type=pathlib.Path,required=True)
    p.add_argument('--answers',type=pathlib.Path)
    p.add_argument('--reviews',type=pathlib.Path)
    p.add_argument('--out',type=pathlib.Path)
    p.add_argument('--strict',action='store_true',help='Require independent human approval for every gold case')
    args=p.parse_args(argv)
    root=args.root.resolve()
    try:
        suite,sh=read_private(args.suite,root)
        details=validate_suite(suite,root,args.strict or args.command=='score')
        if args.command=='validate-suite':
            print(json.dumps({'status':'valid','benchmark_id':suite['benchmark_id'],**details},sort_keys=True));return 0
        need(args.out is not None,'--out is required for prepare/prepare-reviews/score')
        if args.command=='prepare':
            need(args.answers is None and args.reviews is None,'prepare accepts only --suite and --out')
            write_private(args.out,root,prepare_answers(suite))
            print('Created private blank answer collection file: '+str(args.out));return 0
        if args.command == 'prepare-reviews':
            need(args.answers is not None and args.reviews is None,'prepare-reviews requires --answers only')
            answers, _ = read_private(args.answers,root)
            validate_answers(answers,suite,root)
            write_private(args.out,root,prepare_reviews(suite,answers['run']['run_id']))
            print('Created private dual blinded-review template: '+str(args.out));return 0
        need(args.answers is not None and args.reviews is not None,'score requires --answers and --reviews')
        answers,ah=read_private(args.answers,root); reviews,rh=read_private(args.reviews,root)
        report=evaluate(suite,answers,reviews,root,{'suite':sh,'answers':ah,'reviews':rh})
        write_private(args.out,root,report)
        print(json.dumps({'status':report['status'],'cases':report['case_count'],
                          'mechanical_citation_error_cases':report['mechanical_citation_error_cases'],
                          'adjudication_pending_cases':report['adjudication_pending_cases'],
                          'overall_rubric_fraction':report['overall_rubric_fraction'],
                          'output':str(args.out)},sort_keys=True))
        return 0 if report['status']=='fully_reviewed' else 2
    except (BenchmarkError,OSError,KeyError,TypeError,ValueError) as exc:
        print('ERROR: '+str(exc),file=sys.stderr);return 1

if __name__=='__main__':sys.exit(main())
