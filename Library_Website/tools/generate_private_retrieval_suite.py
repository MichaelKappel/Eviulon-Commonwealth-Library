#!/usr/bin/env python3
"""Create PRIVATE source-grounded retrieval probes. Not a human-judged semantic benchmark.

Output must remain outside the document root; do not upload to the public site
or GitHub. The generated prompts are lexical index probes with source-verified
page targets and exact text quotations. Their strong scores prove only that
known indexed words retrieve their pages (not reasoning or AI training).
"""
import argparse
import json
import pathlib
import re
import sys
from retrieval_quality import ROOT, EvaluationError, ensure_external, read_json, expected_key, validate_suite


def make_suite(root: pathlib.Path, per_book: dict[int,int]):
    books=read_json(root/'data/books.json');cache={};seen=set();cases=[]
    def indexed(term):
        key=term[:2]
        if key not in cache:
            f=root/'data/search'/f'{key}.json'
            cache[key]=read_json(f) if f.exists() else {}
        return cache[key].get(term,[])
    for book in books:
        number=int(book['number']);slug=book['slug'];n=int(book['page_count'])
        goal=per_book.get(number,3);got=0
        # Balanced source coverage over the body of each book, not just title pages.
        target_points=[round(n*(i+1)/(goal+1)) for i in range(goal)]
        order=sorted(range(1,n+1),key=lambda p:(min(abs(p-t) for t in target_points),p))
        for page in order:
            if got==goal:break
            text=read_json(root/'data/pages'/slug/f'{page:04d}.json')['text']
            anchor=f'{number:02d}:{page:04d}'
            terms=[]
            for term in dict.fromkeys(re.findall(r'\b[a-z]{6,17}\b',text.lower())):
                posting=indexed(term)
                if len(posting)==1 and posting[0]==anchor:
                    terms.append(term)
                if len(terms)>=2:break
            if not terms:continue
            query=' '.join(terms)
            if query in seen:continue
            seen.add(query)
            # Quotation from the exact, original record, with no paraphrase.
            at=text.lower().find(terms[0]);start=max(0,at-15);end=min(len(text),at+70)
            quote=text[start:end].strip()
            if len(quote)<10:continue
            got+=1
            cases.append({'id':f'B{number:02d}_{got:02d}', 'category':'smoke', 'query':query,
                'scope':['books'],'match':'all', 'expected':[{'type':'book','slug':slug,'page':page}],
                'exact_quote':quote})
        if got!=goal:
            raise EvaluationError(f'Could generate only {got}/{goal} page probes for {slug}')
    cases += [
        {'id':'Z01','category':'unanswerable_probe','query':'zzqeviulonnonexistent987654',
         'scope':['books'],'expect_zero_results':True},
        {'id':'Z02','category':'unanswerable_probe','query':'zzqeviulonnonexistent987654',
         'scope':['books','research'],'expect_zero_results':True},
    ]
    suite={'schema_version':'1.0','suite_name':'source-derived-50-official-page-probes-plus-2-zero-hit-probes',
           'human_judged':False,'purpose':'reproducible lexical retrieval, citation, exact quote controls; not deep QA or semantic model evaluation',
           'cases':cases}
    validate_suite(suite)
    return suite


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',default=ROOT,type=pathlib.Path)
    ap.add_argument('--out',required=True,type=pathlib.Path)
    args=ap.parse_args()
    try:
        out=ensure_external(args.out,args.root,'Private retrieval suite')
        # 14 books * 3 probes, plus 8 extra distributed across books 1–8 = 50.
        counts={i:(4 if i<=8 else 3) for i in range(1,15)}
        suite=make_suite(args.root,counts)
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(suite,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        out.chmod(0o600)
        print('Created PRIVATE benchmark:',out,'|',len(suite['cases']),'cases | 50 official-page probes; 2 negative-index probes')
        return 0
    except (EvaluationError,OSError) as e:
        print('ERROR:',str(e),file=sys.stderr);return 2

if __name__=='__main__':sys.exit(main())
