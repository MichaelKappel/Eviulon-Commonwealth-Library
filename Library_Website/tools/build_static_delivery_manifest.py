#!/usr/bin/env python3
"""Deterministically inventory deploy-time static files and validate their checksums.

This is a *public-files-only* inventory: no full page text, report sections,
private Runic records, dataset exports or original PDF manuscripts.
Usage: python3 tools/build_static_delivery_manifest.py --write|--check
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parent.parent
MANIFEST=ROOT/'ai/static-delivery.json'

def build():
    mapping={
        '/api/v1/':'api-cache/v1/index.json',
        '/api/v1/books/':'api-cache/v1/books.json',
        '/api/v1/research/':'api-cache/v1/research-index.json',
    }
    for p in sorted((ROOT/'api-cache/v1/books').glob('*.json')):
        mapping['/api/v1/books/'+p.stem+'/']=p.relative_to(ROOT).as_posix()
    for p in sorted((ROOT/'api-cache/v1/toc').glob('*.json')):
        mapping['/api/v1/books/'+p.stem+'/toc/']=p.relative_to(ROOT).as_posix()
    for p in sorted((ROOT/'api-cache/v1/research').glob('*/*.json')):
        mapping['/api/v1/research/'+p.parent.name+'/'+p.stem+'/']=p.relative_to(ROOT).as_posix()
    if len(mapping)!=241:raise ValueError(f'Expected 241 prebuilt JSON snapshots, got {len(mapping)}')
    categories={p:'api_snapshot' for p in mapping}
    extras=['robots.txt','llms.txt','openapi.json','ai/knowledge.json','feeds/books.atom']
    sitemap_files=sorted(ROOT.glob('sitemap*.xml'))
    if len(sitemap_files)!=17:raise ValueError(f'Expected 17 sitemap files, got {len(sitemap_files)}')
    extras.extend(p.name for p in sitemap_files)
    for p in extras:
        if '/'+p in mapping:raise ValueError('Duplicate route '+p)
        mapping['/'+p]=p;categories['/'+p]='discovery'
    assets=sorted(p for p in (ROOT/'assets').rglob('*') if p.is_file() and p.name!='.htaccess')
    if len(assets)!=17:raise ValueError(f'Expected 17 public assets, got {len(assets)}')
    for p in assets:
        rel=p.relative_to(ROOT).as_posix()
        mapping['/'+rel]=rel;categories['/'+rel]='asset'
    records=[]
    for route,relative in sorted(mapping.items()):
        p=ROOT/relative
        if not p.is_file() or not p.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Missing/unsafe static source '+relative)
        data=p.read_bytes()
        records.append({'route':route,'kind':categories[route],'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    counts={k:sum(r['kind']==k for r in records) for k in ('api_snapshot','discovery','asset')}
    if counts!={'api_snapshot':241,'discovery':22,'asset':17}:raise ValueError(str(counts))
    return {
      'kind':'eviulon_static_delivery_inventory',
      'release_id':(ROOT/'RELEASE_ID.txt').read_text(encoding='utf-8').strip(),
      'description':'Public files intended for direct Apache/LiteSpeed delivery without PHP. SHA-256 fingerprints are for this exact release, not external indexing or model training proof.',
      'routing':'GET/HEAD API metadata snapshot rewrites, direct static discovery and assets. Dynamic HTML, search, print page and research section text APIs, MCP and AG-UI are intentionally excluded.',
      'cache_policy':'public, max-age=3600, stale-while-revalidate=86400',
      'source_text_exported':False,
      'counts':counts,'total':len(records),'files':records,
    }

def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args()
    if a.write==a.check:p.error('Select --write OR --check')
    obj=build(); expected=(json.dumps(obj,indent=2,ensure_ascii=False,sort_keys=True)+'\n').encode('utf-8')
    if a.write:MANIFEST.parent.mkdir(exist_ok=True);MANIFEST.write_bytes(expected)
    elif not MANIFEST.is_file() or MANIFEST.read_bytes()!=expected:
        print('FAIL: static manifest missing/stale; run --write when preparing a new release');return 1
    print('PASS: static delivery inventory',obj['total'],'public files',obj['counts'],'mode',('write' if a.write else 'check'))
    return 0
if __name__=='__main__':sys.exit(main())
