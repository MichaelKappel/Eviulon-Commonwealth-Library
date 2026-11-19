#!/usr/bin/env python3
"""Source-derived heading navigability test; not an AI understanding benchmark.

Tests first and median chapter heading from each of the 14 canonical books.
The cases are created on demand from immutable section metadata; no public gold
answer keys or philosophical model answers are shipped with this website.
"""
import argparse
import re
import sys
from retrieval_quality import ROOT, read_json, evaluate


def chapter_cases(root):
    books=read_json(root/'data/books.json');cases=[]
    for b in books:
        landmarks=read_json(root/'data/sections'/f'{b["slug"]}.json')
        chapters=[x for x in landmarks if x['category']=='chapter']
        if not chapters:raise RuntimeError('No source-verified chapters: '+b['slug'])
        for idx,s in enumerate([chapters[0],chapters[len(chapters)//2]],1):
            query=re.sub(r'^Chapter\s+(?:\d+|[IVXLCDM]+|One|Two|Three|Four|Five|Six|Seven|Eight|Nine|Ten)\s*[:.\-—·–]*\s*','',s['title'],flags=re.I)
            query=query.strip().replace('—',' ').replace('·',' ').replace('–',' ')
            cases.append({'id':f'C{int(b["number"]):02d}_{idx}', 'category':'chapter_citation',
                'query':query,'scope':['books'],'match':'any',
                'expected':[{'type':'book','slug':b['slug'],'page':int(s['page'])}]})
    return cases


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--http',required=True);ap.add_argument('--root',default=ROOT,type=__import__('pathlib').Path)
    args=ap.parse_args();suite={'schema_version':'1.0','suite_name':'ephemeral-28-chapter-navigation-probes','cases':chapter_cases(args.root)}
    result=evaluate(args.http,suite,k=5)
    metrics=result['metrics']
    print('SOURCE-DERIVED CHAPTER NAVIGATION:',metrics['retrieval_cases'],'queries',
          'Hit@5=',metrics['hit_at_k'],'MRR@5=',metrics['mrr_at_k'],
          'Citation=',metrics['citation_integrity_rate'])
    for x in result['cases']:
        if x['hit_at_k']!=1 or x['errors']:print('MISSED',x['id'],x['errors'])
    return 0 if (metrics['retrieval_cases']==28 and metrics['hit_at_k']==1.0 and
                 metrics['mrr_at_k']>=0.90 and metrics['citation_integrity_rate']==1.0
                 and not result['errors']) else 1

if __name__=='__main__':sys.exit(main())
