#!/usr/bin/env python3
"""Deterministically inventory deploy-time static files and validate their checksums.

This is an inventory of canonical public static responses. Individual reading HTML
contains the already-public text; no bulk text feed, private Runic records,
original manuscript PDFs or source document archives are released.
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
    for p in sorted((ROOT/'api-cache/v1/citations/books').glob('*/*.json')):
        mapping[f'/api/v1/books/{p.parent.name}/citations/{p.stem}/']=p.relative_to(ROOT).as_posix()
    for p in sorted((ROOT/'api-cache/v1/citations/research').glob('*/*/*.json')):
        mapping[f'/api/v1/research/{p.parent.parent.name}/{p.parent.name}/parts/{p.stem}/citation/']=p.relative_to(ROOT).as_posix()
    if len(mapping)!=3719:raise ValueError(f'Expected 3719 prebuilt JSON snapshots, got {len(mapping)}')
    categories={p:'api_snapshot' for p in mapping}
    html_manifest=json.loads((ROOT/'html-cache/manifest.json').read_text())
    if html_manifest['total']!=3702 or html_manifest['release_id']!=(ROOT/'RELEASE_ID.txt').read_text().strip():
        raise ValueError('Stale canonical reading HTML manifest')
    for r in html_manifest['snapshots']:
        url=r['url']
        if url in mapping:raise ValueError('Overlapping static source route: '+url)
        mapping[url]=r['relative_path'];categories[url]='canonical_html'

    # Include all 21 canonical lexical topic HTML endpoints, generated from source-backed evidence.
    topics=json.loads((ROOT/'topics-cache/manifest.json').read_text())
    if topics['pages']!=21 or topics['release_id']!=(ROOT/'RELEASE_ID.txt').read_text().strip():
        raise ValueError('Stale topic HTML manifest')
    for row in topics['snapshot_rows']:
        if row['url'] in mapping:raise ValueError('Duplicate topic URL '+row['url'])
        mapping[row['url']]=row['path'];categories[row['url']]='topic_html'
    extras=['robots.txt','llms.txt','openapi.json','ai/knowledge.json','feeds/books.atom','ai/concepts.json','ai/source-registry.jsonld','ai/discovery-attestation.json']
    sitemap_files=sorted(ROOT.glob('sitemap*.xml'))
    if len(sitemap_files)!=18:raise ValueError(f'Expected 18 sitemap files, got {len(sitemap_files)}')
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
    counts={k:sum(r['kind']==k for r in records) for k in ('api_snapshot','canonical_html','topic_html','discovery','asset')}
    if counts!={'api_snapshot':3719,'canonical_html':3702,'topic_html':21,'discovery':26,'asset':17}:raise ValueError(str(counts))
    return {
      'kind':'eviulon_static_delivery_inventory',
      'release_id':(ROOT/'RELEASE_ID.txt').read_text(encoding='utf-8').strip(),
      'description':'Public files intended for direct Apache/LiteSpeed delivery without PHP. SHA-256 fingerprints are for this exact release, not external indexing or model training proof.',
      'routing':'GET/HEAD query-free canonical book/report and source-grounded topic HTML is pre-rendered without PHP; metadata JSON, bounded lexical evidence, sitemaps and assets are static. Search, source-text APIs, MCP, AG-UI, alternate URL forms and query-bearing requests remain dynamic.',
      'cache_policy':'public, max-age=3600, stale-while-revalidate=86400',
      'source_text_exported':False,
      'individual_canonical_reading_html_contains_original_public_text':True,
      'bulk_manuscript_or_dataset_exported':False,
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
