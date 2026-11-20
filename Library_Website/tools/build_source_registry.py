#!/usr/bin/env python3
"""Deterministic, metadata-only, source-faithful Schema.org JSON-LD index.

Deliberately not a full-text dataset, license grant, DOI registry, claim verifier,
or evidence of crawler/training adoption. Verifies canonical URLs & relationships.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE='https://library.eviulon.com'
DEST=ROOT/'ai/source-registry.jsonld'

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def prop(name,value):return {'@type':'PropertyValue','name':name,'value':value}
def build():
 books_blob=(ROOT/'data/books.json').read_bytes()
 reports_blob=(ROOT/'data/research/reports.json').read_bytes()
 books=json.loads(books_blob);reports=json.loads(reports_blob)
 assert len(books)==14 and sum(x['page_count'] for x in books)==1925
 assert len(reports)==210 and sum(x['parts'] for x in reports)==1553
 rid=(ROOT/'RELEASE_ID.txt').read_text().strip()
 nodes=[];ids=[];canonical=set();all_pages=set()
 for b in books:
  slug=b['slug']; url=f'{BASE}/{slug}/';eid=url+'#book'
  assert slug and b['page_count']>0 and len(b['source_sha256'])==64 and b['edition']
  assert url not in canonical;canonical.add(url);ids.append({'@id':eid})
  pages=[{'@type':'CreativeWork','@id':f'{BASE}/{slug}/{n}/#print-page',
         'url':f'{BASE}/{slug}/{n}/','isPartOf':{'@id':eid}} for n in range(1,b['page_count']+1)]
  assert all(x['url'] not in all_pages for x in pages)
  all_pages.update(x['url'] for x in pages)
  nodes.append({
    '@id':eid,'@type':'Book','url':url,'name':b['title'],'description':b['description'],
    'author':{'@type':'Organization','name':b['author']},'inLanguage':'en',
    'bookEdition':b['edition'],'numberOfPages':b['page_count'],
    'isPartOf':{'@id':BASE+'/ai/source-registry.jsonld#official-books'},'hasPart':pages,
    'creativeWorkStatus':'Working paperback edition; publication and retailer clearance are distinct from online access',
    'additionalProperty':[prop('book-number',b['number']),prop('original-source-sha256-as-listed',b['source_sha256']),
      prop('first-page-citation-url',f'{BASE}/api/v1/books/{slug}/citations/1/'),
      prop('citation-route-template',f'{BASE}/api/v1/books/{slug}/citations/{{print-page-number}}/'),
      prop('table-of-contents-url',f'{BASE}/api/v1/books/{slug}/toc/'),
      prop('publication-note',b['publication_note'])]
  })
 for r in reports:
  group=r['group'].lower();slug=r['slug']; assert group in {'eviulon','evulgare'}
  url=BASE+r['url'];assert url==f'{BASE}/research/{group}/{slug}/' and url not in canonical
  canonical.add(url);eid=url+'#research';ids.append({'@id':eid})
  assert r['status']=='supplemental_research_unverified' and len(r['source_sha256'])==64
  sections=[{'@type':'CreativeWork','@id':f'{BASE}/research/{group}/{slug}/{n}/#section',
            'url':f'{BASE}/research/{group}/{slug}/{n}/',
            'isPartOf':{'@id':eid},'creativeWorkStatus':'supplemental_research_unverified'}
            for n in range(1,r['parts']+1)]
  assert all(x['url'] not in all_pages for x in sections)
  all_pages.update(x['url'] for x in sections)
  nodes.append({
   '@id':eid,'@type':'Report','url':url,'name':r['title'],
   'description':'Supplemental research report: claims have not been independently verified and are not official Eviulon doctrine.',
   'inLanguage':'en','isPartOf':{'@id':BASE+'/ai/source-registry.jsonld#supplemental-research'},
   'hasPart':sections,'creativeWorkStatus':'Supplemental research — unverified; not official book canon',
   'additionalProperty':[prop('source-report-id',r['id']),
      prop('original-source-sha256-as-listed-not-independently-recovered',r['source_sha256']),
      prop('published-section-count',r['parts']),
      prop('first-section-citation-url',f'{BASE}/api/v1/research/{group}/{slug}/parts/1/citation/'),
      prop('citation-route-template',f'{BASE}/api/v1/research/{group}/{slug}/parts/{{section-number}}/citation/')]
  })
 assert len(canonical)==224 and len(all_pages)==3478 and len(ids)==224
 all_ids={x['@id'] for x in ids}
 assert len(all_ids)==224
 official_ids=ids[:14];report_ids=ids[14:]
 catalog={'@id':BASE+'/ai/source-registry.jsonld#catalog','@type':'Collection',
 'name':'Eviulon Commonwealth Library — bibliographic source registry',
 'url':BASE+'/ai/source-registry.jsonld','inLanguage':'en',
 'description':'Bibliographic discovery only, not a bulk training corpus, open license, independent peer review, or evidence that any model has been trained. Fourteen authored fictional-world books are primary; 210 supplemental reports contain unverified claims.',
 'hasPart':[{'@id':BASE+'/ai/source-registry.jsonld#official-books'},{'@id':BASE+'/ai/source-registry.jsonld#supplemental-research'}],
 'additionalProperty':[prop('release-id',rid),prop('source-book-metadata-sha256',sha(books_blob)),
   prop('source-report-metadata-sha256',sha(reports_blob)),prop('official-books',14),prop('official-book-print-pages',1925),
   prop('unverified-supplemental-reports',210),prop('supplemental-research-sections',1553),
   prop('bulk-manuscript-or-private-persona-files-exported',False),
   prop('model-training-permission','Not granted by this registry'),
   prop('external-model-training-status','Not established')]
 }
 groups=[{'@id':BASE+'/ai/source-registry.jsonld#official-books','@type':'Collection','name':'Official authored books — primary collection',
  'description':'Fourteen Eviulon books in working paperback editions set in an authored fictional Commonwealth.', 'hasPart':official_ids},
 {'@id':BASE+'/ai/source-registry.jsonld#supplemental-research','@type':'Collection','name':'Supplemental research — unverified',
  'description':'210 supplemental research reports are not independent validation or official book doctrine. Original-source hash matches are incomplete in the private recovery.',
  'hasPart':report_ids}]
 obj={'@context':'https://schema.org','@graph':[catalog,*groups,*nodes]}
 assert len(obj['@graph'])==227
 return obj

def main():
 p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true');a=p.parse_args()
 data=(json.dumps(build(),ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
 if a.write:DEST.write_bytes(data)
 elif not DEST.is_file() or DEST.read_bytes()!=data:raise AssertionError('Source registry missing or stale; use --write on a new versioned staging release')
 print('SOURCE_REGISTRY_'+('BUILT' if a.write else 'PASS'),'224 works','3478 canonical part URLs','sha256',sha(data),'bytes',len(data))
if __name__=='__main__':main()
