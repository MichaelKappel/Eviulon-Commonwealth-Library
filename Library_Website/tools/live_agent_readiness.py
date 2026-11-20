#!/usr/bin/env python3
"""Read-only, bounded, fail-closed verification of the Eviulon agent discovery contract.

No credentials, private research questions, model calls or mutating requests. Only the
canonical HTTPS host and explicitly selected loopback HTTP development targets are allowed.
A passing readiness probe is NOT proof of indexing, bot verification, or model training.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from agent_answer_benchmark import ROOT, write_private, BenchmarkError

MAX_RESPONSE_BYTES = 1_200_000
READ_TIMEOUT = 10
DOMAIN = 'https://library.eviulon.com'

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

@dataclass(frozen=True)
class Response:
    status:int
    media_type:str
    body:bytes
    headers:dict

class CanonicalParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.canonicals=[];self.robots=[]
    def handle_starttag(self, tag, attrs):
        fields=dict(attrs)
        if tag=='link' and fields.get('rel')=='canonical':self.canonicals.append(fields.get('href'))
        if tag=='meta' and fields.get('name','').lower()=='robots':self.robots.append(fields.get('content'))


def validate_target(base:str)->str:
    """Allow only the canonical HTTPS production site or loopback development server."""
    try:parts=urllib.parse.urlsplit(base)
    except ValueError:raise ValueError('Invalid --base-url')
    if parts.username is not None or parts.password is not None or parts.query or parts.fragment or parts.path not in ('','/'):
        raise ValueError('Target must be a host root with no auth, path, query, or fragment')
    host=parts.hostname
    if parts.scheme=='https' and host=='library.eviulon.com' and parts.port in (None,443):
        return DOMAIN
    if parts.scheme=='http' and host in ('127.0.0.1','localhost','::1') and parts.port and 1<=parts.port<=65535:
        # Normalization to a known-safe host to prevent DNS rebinding via arbitrary names.
        return 'http://'+ ('[::1]' if host=='::1' else host)+f':{parts.port}'
    raise ValueError('Only canonical HTTPS production or explicit loopback HTTP with port is allowed')

class AgentProbe:
    def __init__(self,base,timeout=READ_TIMEOUT):
        self.base=validate_target(base)
        if not (1<=timeout<=30):raise ValueError('Timeout must be within 1–30 seconds')
        self.timeout=timeout
        self.opener=urllib.request.build_opener(NoRedirect)
    def fetch(self,path:str)->Response:
        if not path.startswith('/') or '\\' in path or any(x in path for x in ('..','#')) or re.search(r'[\r\n]',path):
            raise ValueError('Invalid requested path')
        url=self.base+path
        req=urllib.request.Request(url,method='GET',headers={'User-Agent':'EviulonOwnerReadiness/1.0','Accept':'text/html, application/json, application/xml, text/plain, */*'})
        try:
            with self.opener.open(req,timeout=self.timeout) as res:
                body=res.read(MAX_RESPONSE_BYTES+1)
                if len(body)>MAX_RESPONSE_BYTES:raise ValueError('Response exceeds bounded read limit')
                return Response(res.status, res.headers.get('Content-Type','').split(';')[0].lower(),body,dict(res.headers))
        except urllib.error.HTTPError as ex:
            try:body=ex.read(min(MAX_RESPONSE_BYTES,16384))
            finally:ex.close()
            return Response(ex.code,ex.headers.get('Content-Type','').split(';')[0].lower(),body,dict(ex.headers))


def run_probe(probe:AgentProbe)->dict:
    base=probe.base
    records=[]
    def check(key:str,path:str,test):
        try:
            result=probe.fetch(path)
            ok,detail=test(result)
            records.append({'check':key,'path':path,'status':result.status,'passed':bool(ok),'detail':detail[:180]})
        except (OSError,ValueError,UnicodeError,ET.ParseError,json.JSONDecodeError) as ex:
            records.append({'check':key,'path':path,'status':None,'passed':False,'detail':f'{type(ex).__name__}: {str(ex)[:150]}'})
    def html(response, canonical):
        parser=CanonicalParser();parser.feed(response.body.decode('utf-8'))
        ok=response.status==200 and parser.canonicals==[DOMAIN+canonical] and response.media_type=='text/html'
        return ok,'200 HTML and exact canonical URL' if ok else 'Unexpected HTML status/media/canonical'
    def json_api(response, expected=None):
        if response.status!=200 or response.media_type!='application/json':return False,'JSON endpoint not HTTP 200 application/json'
        value=json.loads(response.body)
        return ((expected(value) if expected else isinstance(value,dict)), 'Schema/authority/selection contract')
    check('canonical_home','/',lambda r:html(r,'/'))
    check('agent_guide','/for-agents/',lambda r: (html(r,'/for-agents/')[0] and b'books' in r.body.lower() and b'research' in r.body.lower(),'Agent guide must name books and supplemental research'))
    check('robots','/robots.txt',lambda r:(r.status==200 and 'text/plain' in r.media_type and b'Sitemap:' in r.body and b'Disallow: /data/' in r.body,'Robots and sitemap declaration'))
    check('sitemap','/sitemap.xml',lambda r:(r.status==200 and r.media_type in ('application/xml','text/xml') and len(ET.fromstring(r.body).findall('.//{*}loc'))==17,'Sitemap index has 17 expected child sitemaps'))
    check('openapi','/openapi.json',lambda r:json_api(r,lambda d:d.get('openapi','').startswith('3.1.') and isinstance(d.get('paths'),dict)))
    check('agent_directory','/api/v1/',lambda r:json_api(r,lambda d:d.get('search_default_scope')==['books'] and d.get('read_only') is True and d.get('bulk_downloads') is False))
    def book_count(d):
        if isinstance(d,list):return len(d)==14
        if isinstance(d,dict):
            books=d.get('books',[])
            return isinstance(books,list) and len(books)==14
        return False
    check('official_books','/api/v1/books/',lambda r:json_api(r,book_count))
    check('books_default','/api/v1/search/?q=identity',lambda r:json_api(r,lambda d:d.get('scope')==['books'] and d.get('research_total')==0 and isinstance(d.get('book_results'),list)))
    check('research_opt_in','/api/v1/search/?q=identity&scope=books,research',lambda r:json_api(r,lambda d:d.get('scope')==['books','research'] and all(x.get('official') is True for x in d.get('book_results',[])) and all(x.get('official') is False for x in d.get('research_results',[]))))
    check('evidence_books_default','/api/v1/context/?q=cognitive+liberty',
          lambda r:json_api(r,lambda d:d.get('kind')=='source_evidence_bundle' and d.get('scope')==['books'] and d.get('generated_answer') is False and 0<len(d.get('sources',[]))<=5 and all(x.get('official') is True and len(x.get('quote',{}).get('text','').encode('utf-8'))<=480 for x in d.get('sources',[]))))
    check('evidence_research_opt_in','/api/v1/context/?q=machine&scope=books,research',
          lambda r:json_api(r,lambda d:d.get('scope')==['books','research'] and bool(d.get('research_disclaimer')) and all(x.get('official') is True for x in d.get('sources',[]) if x.get('type')=='book') and all(x.get('official') is False for x in d.get('sources',[]) if x.get('type')=='research')))
    check('html_search_default','/search/',lambda r:(r.status==200 and b'name="scope[]" value="books" checked' in r.body and b'name="scope[]" value="research" checked' not in r.body,'Books checkbox selected, research checkbox unselected'))
    check('book_page','/the-inheritance-of-mind/1/',lambda r:(html(r,'/the-inheritance-of-mind/1/')[0] and b'PRINT PAGE' in r.body,'Canonical printed page 1 available'))
    check('book_citation','/api/v1/books/the-inheritance-of-mind/citations/1/',lambda r:json_api(r,lambda d:DOMAIN+'/the-inheritance-of-mind/1/' in json.dumps(d) and 'official_eviulon_book' in json.dumps(d)))
    check('book_toc','/api/v1/books/the-inheritance-of-mind/toc/',lambda r:json_api(r,lambda d:len(json.dumps(d))>250 and 'the-inheritance-of-mind' in json.dumps(d)))
    check('research_directory','/research/',lambda r:(r.status==200 and b'supplemental' in r.body.lower() and b'research' in r.body.lower(),'Supplemental research visibly labeled'))
    for path in ('/data/books.json','/src/bootstrap.php','/tools/agent_answer_benchmark.py','/data/research/reports.json','/.uai/public-metadata.uai'):
        check('protected_path',path,lambda r:(r.status in (403,404),'Protected path must return 403 or 404'))
    check('unknown_book','/api/v1/books/this-book-does-not-exist/',lambda r:(r.status==404,'Unknown book must return 404'))
    successes=sum(x['passed'] for x in records)
    return {'schema_version':'1.0','probe':'eviulon_agent_readiness_v3_8','base_url':base,
            'timestamp_utc':datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'status':'pass' if successes==len(records) else 'fail',
            'passed':successes,'failed':len(records)-successes,'checks':records,
            'limits':'Read-only HTTP observation. Does not prove crawler identity, indexing, training, or agent answer accuracy.'}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base-url',default=DOMAIN)
    p.add_argument('--timeout',type=int,default=READ_TIMEOUT)
    p.add_argument('--report-out',type=pathlib.Path,help='Optional PRIVATE JSON file outside document root, created exclusively')
    p.add_argument('--root',type=pathlib.Path,default=ROOT)
    args=p.parse_args(argv)
    try:
        probe=AgentProbe(args.base_url,args.timeout)
        report=run_probe(probe)
        if args.report_out: write_private(args.report_out,args.root,report)
        print(json.dumps({'status':report['status'],'target':report['base_url'],'passed':report['passed'],'failed':report['failed'],'failures':[x for x in report['checks'] if not x['passed']]},ensure_ascii=False,indent=2))
        return 0 if report['status']=='pass' else 2
    except (ValueError,OSError,BenchmarkError) as ex:
        print('ERROR: '+str(ex),file=sys.stderr);return 1
if __name__=='__main__':sys.exit(main())
