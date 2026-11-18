#!/usr/bin/env python3
"""Assemble deployable HTML reader from public source code + local private book data.

Output MUST be outside public git; original private books, .uai, docs, raw PDFs/EPUBs, logs and passwords are not copied.
"""
import argparse,shutil,sys,json
from pathlib import Path
parser=argparse.ArgumentParser()
parser.add_argument('--private-site',required=True,type=Path,help='Local private production Library_Website directory')
parser.add_argument('--output',required=True,type=Path,help='Outside this git repository; must not exist')
args=parser.parse_args()
root=Path(__file__).resolve().parent.parent
private=args.private_site.resolve();out=args.output.resolve()
if out.exists() or out.is_relative_to(root.resolve()) or out.is_relative_to(private):
    parser.error('Output must be new and outside both repository and private input')
if not (private/'data/pages').is_dir() or not (private/'data/search').is_dir():
    parser.error('Private website data/pages and data/search directories missing')
# Copy only the public operational website and approved book data. No .uai or src/manuscript documents.
public=root/'Library_Website'
for p in public.rglob('*'):
    if not p.is_file():continue
    rel=p.relative_to(public)
    if any(s in rel.parts for s in ('.uai','tools')) or rel.name in ('AGENTS.md','RUNIC_MEMORY_MANIFEST.json','README_DEPLOY.md','AGENT_DISCOVERY.md','README.md'):
        continue
    dest=out/rel; dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
for sub in ('pages','search'):
    shutil.copytree(private/'data'/sub,out/'data'/sub)
# Verify source and added corpus sizes/counters; required book JSON must match chapter data count.
books=json.loads((out/'data/books.json').read_text())
pages=list((out/'data/pages').rglob('*.json'))
want=sum(b['page_count'] for b in books)
if len(pages)!=want:
    shutil.rmtree(out);parser.error(f'Page mismatch {len(pages)} != {want}')
print(f'Prepared {out}: {len(books)} books / {len(pages)} page JSON records. Keep this output PRIVATE and do not commit it.')
