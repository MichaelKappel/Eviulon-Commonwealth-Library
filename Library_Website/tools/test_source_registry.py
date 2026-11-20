#!/usr/bin/env python3
"""Validate metadata-only JSON-LD catalog and HTTP delivery/fallback contract."""
from __future__ import annotations
import argparse,hashlib,json,pathlib,urllib.error,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]
PATH='/ai/source-registry.jsonld';URL='https://library.eviulon.com'+PATH

def request(base,path,method='GET',headers=None,data=None):
 try:
  with urllib.request.urlopen(urllib.request.Request(base.rstrip('/')+path,method=method,headers=headers or {},data=data),timeout=30) as r:return r.status,r.headers,r.read()
 except urllib.error.HTTPError as ex:return ex.code,ex.headers,ex.read()

def validate():
 from build_source_registry import build
 want=build();actual=json.loads((ROOT/PATH.lstrip('/')).read_text())
 assert actual==want
 nodes=actual['@graph'];assert len(nodes)==227
 b=[n for n in nodes if n.get('@type')=='Book'];r=[n for n in nodes if n.get('@type')=='Report']
 assert len(b)==14 and len(r)==210
 assert sum(len(n['hasPart']) for n in b)==1925
 assert sum(len(n['hasPart']) for n in r)==1553
 canonical={x['url'] for n in b+r for x in n['hasPart']};assert len(canonical)==3478
 assert all(u.startswith('https://library.eviulon.com/') for u in canonical)
 assert all(x['@id']==x['url']+'#print-page' and x['isPartOf']=={'@id':n['@id']} and x['@type']=='CreativeWork'
            for n in b for x in n['hasPart'])
 assert all(n['@id']==n['url']+'#research' for n in r)
 assert all(x['@id']==x['url']+'#section' and x['isPartOf']=={'@id':n['@id']} and x['@type']=='CreativeWork'
            and x['creativeWorkStatus']=='supplemental_research_unverified'
            for n in r for x in n['hasPart'])
 assert all(n.get('creativeWorkStatus') for n in r)
 assert all('unverified' in n['creativeWorkStatus'].lower() for n in r)
 assert all('Working paperback edition' in n['creativeWorkStatus'] for n in b)
 # Block body fields and base64/bulk content indicators in public structured metadata.
 prohibited={'text','articleBody','encoding','hasDigitalDocument','contentUrl','associatedMedia','downloadUrl','license','doi','sameAs','excerpt','passage','snippet'}
 def walk(node):
  if isinstance(node,dict):
   assert not prohibited.intersection(node),(prohibited.intersection(node),node.get('@id'))
   for value in node.values():walk(value)
  elif isinstance(node,list):
   for value in node:walk(value)
 walk(actual)
 return actual

def run_http(base,strict=False):
 actual=validate();bytes_expected=(ROOT/PATH.lstrip('/')).read_bytes();count=0
 def check(expr,label):
  nonlocal count
  count+=1
  if not expr:raise AssertionError(label)
 s,h,b=request(base,PATH)
 check(s==200,'JSON-LD HTTP 200')
 check(b==bytes_expected,'byte parity')
 check('application/ld+json' in h.get('Content-Type',''),'JSON-LD mime')
 check(json.loads(b)==actual,'JSON-LD parse')
 check(h.get('ETag') is not None,'ETag')
 check('max-age=' in h.get('Cache-Control',''),'cache')
 etag=h.get('ETag')
 status,headers,body=request(base,PATH,headers={'If-None-Match':etag or ''})
 check(status==304 and not body,'conditional GET 304')
 status,headers,body=request(base,PATH,method='HEAD')
 check(status==200 and not body,'HEAD')
 status,headers,body=request(base,PATH,method='POST',data=b'x')
 check(status==405,'non-GET/HEAD 405')
 check('no-store' in headers.get('Cache-Control',''),'405 no-store')
 if strict:
  check(not h.get('X-Powered-By'),'Apache static served no PHP')
 print('SOURCE_REGISTRY_HTTP_PASS',count,'checks','224 works 3478 linked unit URLs')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--http');p.add_argument('--strict-web-server',action='store_true');a=p.parse_args()
 validate();print('SOURCE_REGISTRY_STRUCTURE_PASS 14 books 210 reports 3478 source-unit links')
 if a.http:run_http(a.http,a.strict_web_server)
