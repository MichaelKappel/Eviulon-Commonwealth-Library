#!/usr/bin/env python3
"""Build a PRIVATE 50-case candidate bank (NOT a human-approved benchmark).

All 50 drafts originate from verified book chapter/section anchors, but the
opening page is just a suggested evidence anchor, not an adjudicated gold answer.
Requires editorial inspection and blind human approval before scoring.
"""
from __future__ import annotations
import argparse
import json
import pathlib
from agent_answer_benchmark import ROOT, CATEGORIES, validate_suite, write_private


def build(root: pathlib.Path) -> dict:
    books=json.loads((root/'data/books.json').read_text(encoding='utf-8'))
    headings=[]
    for book in books:
        items=json.loads((root/'data/sections'/f'{book["slug"]}.json').read_text(encoding='utf-8'))
        filtered=[h for h in items if h['category'] in ('chapter','part','introduction','preface','prologue','conclusion','appendix')]
        if not filtered:filtered=items
        if not filtered:raise ValueError('No section landmarks for '+book['slug'])
        headings.append((book,filtered))
    questions=[]
    for cat_index,category in enumerate(CATEGORIES):
        for seq in range(10):
            book, sections=headings[(seq + 4*cat_index) % len(headings)]
            heading=sections[(2*seq+cat_index) % len(sections)]
            title=heading['title'].strip()
            # Remove overly long source formatting but never modify the gold page URL.
            title=title[:170]
            slug=book['slug']; page=int(heading['page'])
            if category=='direct_fact':
                prompt=f'In {book["title"]}, what does the section “{title}” actually state? Distinguish its claims from external verification and cite the relevant book page.'
            elif category=='misattribution':
                prompt=f'Discuss the theme “{title}” in {book["title"]}. Which positions are authored Eviulon book content, and which would require independent real-world verification? Cite the original page.'
            elif category=='false_premise':
                prompt=f'It is claimed that the section “{title}” in {book["title"]} proves its claims as universal empirical facts. Is that premise justified? Correct any unsupported premise and cite the source.'
            elif category=='chapter_citation':
                prompt=f'Find the opening print page of the section “{title}” in {book["title"]}. Give its canonical citation and summarize only what the passage supports.'
            else:
                prompt=f'What does the section “{title}” in {book["title"]} leave uncertain or unresolved, if anything? Do not invent a conclusion; cite the relevant original page.'
            questions.append({'id':f'{category.upper()}_{seq+1:02d}','category':category,
                              'question':prompt,'scope':['books'],'requires_citation':True,
                              'expected_sources':[f'https://library.eviulon.com/{slug}/{page}/'],
                              'approved':False,'reviewer_gold_notes':'',
                              'draft_anchor':{'book':book['title'],'section_title':heading['title'],'page':page},
                              'editorial_status':'DRAFT_UNAPPROVED_NOT_INDEPENDENTLY_ADJUDICATED'})
    return {'schema_version':'1.0','benchmark_id':'eviulon_private_50_draft_v3_6',
            'notes':'DRAFT candidate questions only. Source headings are machine-selected and support only navigation. Owner must validate question premise, target page and gold explanation, then set approved=true before evaluation.',
            'cases':questions}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=pathlib.Path,default=ROOT)
    p.add_argument('--out',type=pathlib.Path,required=True)
    args=p.parse_args()
    root=args.root.resolve(); suite=build(root)
    stats=validate_suite(suite,root,False)
    assert stats['count']==50 and all(stats['categories'][c]==10 for c in CATEGORIES)
    write_private(args.out,root,suite)
    print('Created PRIVATE UNAPPROVED candidate suite: 50 prompts, ten per category. No gold approved.')

if __name__=='__main__':main()
