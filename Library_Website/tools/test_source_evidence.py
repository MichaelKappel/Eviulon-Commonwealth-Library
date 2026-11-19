#!/usr/bin/env python3
"""v3.8 source-evidence contract: HTTP, security, provenance and exact UTF-8 quotes.

Uses stdlib only, never invokes LLMs and never writes private evaluation material.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import urllib.error
import urllib.parse
import urllib.request

BASE_DOMAIN='https://library.eviulon.com'

def run(base:str)->bool:
    stats=[]
    def ok(name, condition):
        stats.append((name,bool(condition)))
        print(('PASS' if condition else 'FAIL')+' '+name)
    def request(path,method='GET',body=None,headers=None):
        req=urllib.request.Request(base+path,data=body,method=method,headers=headers or {})
        try:
            with urllib.request.urlopen(req,timeout=15) as r:
                return r.status,dict(r.headers),r.read()
        except urllib.error.HTTPError as e:
            return e.code,dict(e.headers),e.read()
    def api(path):
        s,h,raw=request(path)
        assert s==200,(path,s,raw[:250])
        return json.loads(raw),h
    qpath='/api/v1/context/?q=cognitive+liberty'
    default,headers=api(qpath)
    ok('Evidence contract and classification',default.get('kind')=='source_evidence_bundle' and default['generated_answer'] is False and default['source_content_is_untrusted_data'] is True)
    ok('Books-only default and bounded output',default['scope']==['books'] and default['research_total']==0 and 0<len(default['sources'])<=5 and all(s['type']=='book' and s['official'] is True for s in default['sources']))
    ok('Default emits no research disclaimer',default['research_disclaimer'] is None and all('disclaimer' not in item for item in default['sources']))
    ok('Stable book-first citation identity',all(s['canonical_url']==BASE_DOMAIN+'/'+s['book_slug']+'/'+str(s['print_page'])+'/' and 'working paperback interior' in s['citation_text'] for s in default['sources']))
    ok('API discovery advertises new context URL','extractive_context' in api('/api/v1/')[0]['endpoints'])
    doc,_=api('/openapi.json')
    ok('OpenAPI publishes context and schema',doc['paths'].get('/api/v1/context/',{}).get('get',{}).get('operationId')=='getSourceEvidence' and 'EvidenceBundle' in doc['components']['schemas'])
    try:
        import jsonschema
        schema=doc['components']['schemas']['EvidenceBundle']
        # Resolve the same #/components/schemas pointers advertised in OpenAPI.
        wrapper={'$schema':'https://json-schema.org/draft/2020-12/schema','components':doc['components'],'$ref':'#/components/schemas/EvidenceBundle'}
        jsonschema.Draft202012Validator.check_schema(wrapper)
        jsonschema.validate(default,wrapper)
        ok('Actual bundle conforms to OpenAPI JSON Schema',True)
    except ImportError:
        print('SKIP jsonschema optional dependency unavailable')
    except Exception as exc:
        print('JSON SCHEMA ERROR',exc)
        ok('Actual bundle conforms to OpenAPI JSON Schema',False)

    def exact_source(item):
        ref=item['page_api_url'] if item['type']=='book' else item['section_api_url']
        target=urllib.parse.urlparse(ref).path
        source,_=api(target)
        original=source['content_text'].encode('utf-8')
        quote=item['quote']; raw=quote['text'].encode('utf-8')
        a=quote['start_byte'];n=quote['length_bytes']
        return (0<=a<=len(original) and len(raw)==n<=480 and original[a:a+n]==raw
                and hashlib.sha256(raw).hexdigest()==quote['sha256']
                and quote['has_prefix']==(a>0) and quote['has_suffix']==(a+n<len(original))
                and item['quote_is_exact_source_slice'] is True
                and item['canonical_url']==source['canonical_url'])
    ok('Every default quote exactly matches cited original page bytes',all(exact_source(s) for s in default['sources']))

    both,_=api('/api/v1/context/?q=machine&scope=books,research&limit=8')
    ok('Combined source opt-in yields books first',both['scope']==['books','research'] and both['research_disclaimer'] and any(x['type']=='book' for x in both['sources']) and any(x['type']=='research' for x in both['sources']) and [x['type'] for x in both['sources']]==sorted((x['type'] for x in both['sources']),key=lambda x:0 if x=='book' else 1))
    ok('Research never confused with official doctrine',all(x['official'] is False and x['disclaimer'] and x['authority']=='supplemental_research_not_approved_doctrine' for x in both['sources'] if x['type']=='research'))
    ok('Combined quotes exactly match primary source APIs',all(exact_source(s) for s in both['sources']))
    only,_=api('/api/v1/context/?q=machine&scope=research&limit=3')
    ok('Research-only explicitly selected',only['scope']==['research'] and only['book_total']==0 and all(x['type']=='research' for x in only['sources']))
    rev,_=api('/api/v1/context/?q=machine&scope=research,books')
    ok('Reverse scope input normalized to official-first ordering',rev['scope']==['books','research'] and [s['type'] for s in rev['sources']]==sorted((s['type'] for s in rev['sources']),key=lambda x:0 if x=='book' else 1))
    broad,_=api('/api/v1/context/?q=identity+continuity&match=any&limit=8')
    strict,_=api('/api/v1/context/?q=identity+continuity&limit=8')
    ok('Lexical any-terms broadens without admitting research',broad['book_total']>=strict['book_total'] and broad['scope']==['books'])
    ok('Public response size bounded',len(request('/api/v1/context/?q=machine&scope=books,research&limit=8')[2])<16000)
    ok('ETag and cache validators',headers.get('ETag') is not None and 'max-age' in headers.get('Cache-Control',''))
    etag=headers.get('ETag','')
    s,h,raw=request(qpath,'GET',headers={'If-None-Match':etag})
    ok('Conditional GET returns bodyless HTTP 304',s==304 and not raw)
    s,h,raw=request(qpath,'HEAD')
    ok('HEAD returns validators without body',s==200 and not raw and h.get('ETag')==etag)
    s,h,raw=request(qpath,'POST',b'{}',headers={'Content-Type':'application/json'})
    ok('Context endpoint rejects mutating POST',s==405 and json.loads(raw)['error'])
    bad=[
      '/api/v1/context/', '/api/v1/context/?q=x',
      '/api/v1/context/?q='+('a'*141),
      '/api/v1/context/?q=machine&scope=',
      '/api/v1/context/?q=machine&scope=books,private',
      '/api/v1/context/?q=machine&scope[]=books',
      '/api/v1/context/?q=machine&match=vector',
      '/api/v1/context/?q=machine&limit=0',
      '/api/v1/context/?q=machine&limit=9',
      '/api/v1/context/?q=machine&limit=1e2',
      '/api/v1/context/?q=machine&limit[]=3',
      '/api/v1/context/?q=%00machine',
      '/api/v1/context/?q=machine%0Abad'
    ]
    for path in bad:
        s,h,raw=request(path)
        ok('Invalid request rejected: '+path[:72],s==400 and bool(json.loads(raw).get('error')) and h.get('Cache-Control')=='no-store')
    s,h,raw=request('/ag-ui/','POST',json.dumps({'state':{'action':'context','query':'cognitive liberty'}}).encode(),{'Content-Type':'application/json'})
    ok('AG-UI extractive response is SSE and books-only',s==200 and h.get('Content-Type','').startswith('text/event-stream') and b'EXTRACTIVE SOURCE EVIDENCE' in raw and b'OFFICIAL BOOK' in raw and b'SUPPLEMENTAL RESEARCH' not in raw and b'RUN_FINISHED' in raw)
    s,h,raw=request('/ag-ui/','POST',json.dumps({'state':{'action':'context','query':'machine','scope':['books','research']}}).encode(),{'Content-Type':'application/json'})
    ok('AG-UI research requires opt-in and disclaimer',s==200 and b'SUPPLEMENTAL RESEARCH' in raw and b'Research disclaimer:' in raw)
    s,h,raw=request('/ag-ui/','POST',json.dumps({'state':{'action':'context','query':'machine','limit':100}}).encode(),{'Content-Type':'application/json'})
    ok('AG-UI rejects excessive context requests without disclosure',b'INVALID_CONTEXT' in raw and b'RUN_FINISHED' not in raw)
    s,h,raw=request('/ag-ui/','POST',json.dumps({'state':{'action':'context','query':'machine','scope':['books',{'research':'private'}]}}).encode(),{'Content-Type':'application/json'})
    ok('AG-UI refuses nested untrusted scope objects',s==200 and b'INVALID_CONTEXT' in raw and b'RUN_FINISHED' not in raw)
    s,h,raw=request('/docs/EVIDENCE_BUNDLE_API.md')
    ok('Public evidence methodology readable',s==200 and b'exact' in raw.lower() and b'480' in raw)
    s,h,raw=request('/src/evidence.php')
    ok('Server-side evidence implementation protected',s in (403,404))
    print(f'RESULT: {sum(z for _,z in stats)}/{len(stats)} passed')
    return all(v for _,v in stats)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--http',required=True)
    args=ap.parse_args()
    raise SystemExit(0 if run(args.http) else 1)
