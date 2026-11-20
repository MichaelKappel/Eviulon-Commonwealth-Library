#!/usr/bin/env python3
"""Dependency-free release/deployment checks for v3.3 discovery and HTTP contracts.

Run locally: python3 tools/validate_discovery.py --http http://127.0.0.1:8683
Run against a deployed host only when public: --http https://library.eviulon.com
This does not submit sitemaps, identify bot IPs, or assert indexing.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, subprocess, sys, urllib.request, urllib.error, urllib.parse, xml.etree.ElementTree as ET
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE='https://library.eviulon.com'
ATOM='{http://www.w3.org/2005/Atom}'
class LinkParser(HTMLParser):
    def __init__(self):super().__init__();self.canonicals=[];self.feeds=[];self.robots=[];self.schemas=[];self._schema_parts=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='script' and a.get('type')=='application/ld+json':self._schema_parts=[]
        if tag!='link':return

        if a.get('rel')=='canonical':self.canonicals.append(a.get('href'))
        if a.get('type')=='application/atom+xml':self.feeds.append(a.get('href'))
    def handle_data(self,data):
        if self._schema_parts is not None:self._schema_parts.append(data)
    def handle_endtag(self,tag):
        if tag=='script' and self._schema_parts is not None:
            try:self.schemas.append(json.loads(''.join(self._schema_parts)))
            except json.JSONDecodeError:self.schemas.append(None)
            self._schema_parts=None

class Audit:
    def __init__(self):self.failures=[];self.successes=[]
    def check(self,cond,label):
        (self.successes if cond else self.failures).append(label)
    def report(self):
        print('Eviulon v3.3 Discovery and Security Contract')
        for t in self.successes:print('PASS',t)
        for t in self.failures:print('FAIL',t)
        print(f'RESULT {len(self.successes)} passed; {len(self.failures)} failed')
        return not self.failures

def read_url(base,path,method='GET',headers=None,data=None):
    req=urllib.request.Request(base.rstrip('/')+path,method=method,headers=headers or {},data=data)
    try:
        with urllib.request.urlopen(req,timeout=15) as resp:return resp.status,resp.headers,resp.read()
    except urllib.error.HTTPError as ex:return ex.code,ex.headers,ex.read()

def static_checks(root: pathlib.Path,a:Audit):
    books=json.loads((root/'data/books.json').read_text(encoding='utf8'))
    a.check(len(books)==14 and sum(b['page_count'] for b in books)==1925,'Fourteen authoritative book records / 1,925 print pages')
    sections=sum(len(json.loads((root/'data/sections'/f"{b['slug']}.json").read_text())) for b in books)
    a.check(sections==347,'347 source-derived chapter landmarks')
    feed=ET.parse(root/'feeds/books.atom').getroot()
    entries=feed.findall(f'{ATOM}entry')
    expected=[BASE+'/'+b['slug']+'/' for b in books]
    feed_urls=[e.findtext(f'{ATOM}id') for e in entries]
    a.check(feed_urls==expected and len(entries)==14, 'Atom contains exactly 14 official books in canonical order')
    a.check(all((e.find(f'{ATOM}category') is not None and e.find(f'{ATOM}category').attrib.get('term')=='official-eviulon-book') for e in entries),'Atom contains no research entries')
    a.check(feed.findtext(f'{ATOM}updated') is not None and all(e.findtext(f'{ATOM}updated') for e in entries),'Atom dates are structurally complete')
    sitemap_index=ET.parse(root/'sitemap.xml').getroot()
    sm=[e.text for e in sitemap_index.findall('.//{*}loc')]
    a.check(len(sm)==17 and sm[0]==BASE+'/sitemap-books.xml' and sm[-2]==BASE+'/sitemap-research.xml' and sm[-1]==BASE+'/sitemap-topics.xml','Sitemap index lists books, supplemental research, then bounded lexical topics')
    all_sitemaps=[];all_urls=[]
    for loc in sm:
        name=loc.rsplit('/',1)[-1]
        if not (root/name).is_file():a.check(False,'Sitemap file exists: '+name);continue
        all_sitemaps.append(name)
        all_urls.extend(x.text for x in ET.parse(root/name).findall('.//{*}loc'))
    a.check(len(all_urls)==3729 and len(set(all_urls))==3729,'3,729 distinct canonical URLs including 21 source-grounded topic pages')
    a.check(all(x.startswith(BASE+'/') and not ('?' in x or '#' in x) for x in all_urls),'Sitemaps contain only same-origin canonical URLs')
    book_sitemap=[x.text for x in ET.parse(root/'sitemap-books.xml').findall('.//{*}loc')]
    a.check(BASE+'/search/' not in all_urls,'Noindex search interface excluded from sitemap')
    a.check(all(x in book_sitemap for x in expected),'Every official book has a sitemap landing URL')
    a.check(len([x for x in all_urls if x.startswith(BASE+'/research/')])==1764,'Research directory plus 210 reports and 1,553 sections discoverable')
    a.check((root/'openapi.json').is_file() and (root/'llms.txt').is_file() and (root/'ai/source-registry.jsonld').is_file(),'OpenAPI and agent discovery retained')
    a.check('Disallow: /data/' in (root/'robots.txt').read_text(), 'Robots guidance retained; not used as access control')
    no_bulk=[x for x in root.rglob('*') if x.is_file() and (x.suffix.lower() in ('.zip','.pdf','.epub','.mobi','.uai') or 'monitor-logs' in x.parts)]
    a.check(not no_bulk,'No manuscript bulk downloads, private runes, or monitoring logs in release')
    return books

def test_http(base:str,books:list,a:Audit,full:bool):
    st,h,body=read_url(base,'/feeds/books.atom')
    a.check(st==200 and h.get('Content-Type','').startswith('application/atom+xml') and len(body)>1500,'Atom endpoint content type and response')
    etag=h.get('ETag');last=h.get('Last-Modified')
    a.check(bool(etag) and bool(last),'Atom strong ETag and Last-Modified headers')
    st,hh,b=read_url(base,'/feeds/books.atom',headers={'If-None-Match':etag or ''})
    a.check(st==304 and not b,'Atom conditional GET returns empty HTTP 304')
    st,hh,b=read_url(base,'/feeds/books.atom',headers={'If-None-Match':'"bogus"','If-Modified-Since':last or ''})
    a.check(st==200,'If-None-Match takes precedence over If-Modified-Since')
    st,hh,b=read_url(base,'/feeds/books.atom',headers={'If-Modified-Since':last or ''})
    a.check(st==304,'Atom modified-since conditional GET')
    st,hh,b=read_url(base,'/feeds/books.atom',method='HEAD')
    a.check(st==200 and not b,'Atom HEAD returns no body')
    st,hh,b=read_url(base,'/feeds/books.atom',method='POST',data=b'{}')
    a.check(st==405 and hh.get('Cache-Control')=='no-store','Atom rejects POST with non-cacheable error')
    st,hh,b=read_url(base,'/api/v1/books/')
    a.check(st==200 and hh.get('ETag') is not None,'JSON API exposes a stable ETag')
    st,h2,b=read_url(base,'/api/v1/books/',headers={'If-None-Match':hh.get('ETag','')})
    a.check(st==304 and not b,'JSON API 304 reuse')
    st,hh,b=read_url(base,'/api/v1/books/invalid-slug/')
    a.check(st==404 and hh.get('Cache-Control')=='no-store','JSON 404 is not publicly cached')
    st,hh,body=read_url(base,'/')
    p=LinkParser();p.feed(body.decode('utf-8',errors='replace'))
    a.check(st==200 and p.canonicals==[BASE+'/'],'Homepage exposes exactly one canonical')
    a.check('/feeds/books.atom' in p.feeds,'Atom link discoverable in HTML head')
    st,hh,body=read_url(base,'/search/')
    text=body.decode('utf-8',errors='replace')
    a.check('name="scope[]" value="books" checked' in text and 'name="scope[]" value="research" checked' not in text,'Books checked; Research unchecked in HTML search')
    st,hh,b=read_url(base,'/api/v1/search/?q=identity')
    q=json.loads(b)
    a.check(st==200 and q['scope']==['books'] and q['research_total']==0,'API defaults to official books only')
    st,hh,b=read_url(base,'/api/v1/search/?q=identity&scope=books,research')
    q=json.loads(b)
    a.check(st==200 and q['scope']==['books','research'] and all(x['official'] for x in q['book_results']) and all(not x['official'] for x in q['research_results']),'Research requires explicit opt-in and is identified correctly')
    for path in ['/data/books.json','/src/bootstrap.php','/tools/indexnow_prepare.py','/data/research/manifest.json']:
        st,_,_=read_url(base,path);a.check(st in (403,404),'Protected route rejected: '+path)
    st,_,_=read_url(base,'/ag-ui/',method='OPTIONS')
    a.check(st==204,'AG-UI CORS preflight handled safely')
    st,hh,_=read_url(base,'/ag-ui/',method='POST',data=b'{}',headers={'Content-Type':'text/plain'})
    a.check(st==415 and hh.get('Cache-Control')=='no-store','AG-UI rejects wrong media type')
    st,hh,_=read_url(base,'/ag-ui/',method='POST',data=b'{' + b'x'*32768 + b'}',headers={'Content-Type':'application/json'})
    a.check(st==413,'AG-UI rejects oversized requests')
    st,hh,b=read_url(base,'/ag-ui/',method='POST',data=json.dumps({'state':{'action':'search','query':'machine identity'}}).encode(),headers={'Content-Type':'application/json'})
    a.check(st==200 and b'RUN_STARTED' in b and b'RUN_FINISHED' in b and b'SUPPLEMENTAL RESEARCH' not in b,'AG-UI book-only default preserved')
    # Spot-check all fourteen editions plus first and last pages of each.
    bookpaths=['/'+x['slug']+'/'+str(p)+'/' for x in books for p in (1,x['page_count'])]
    if full:bookpaths=['/'+x['slug']+'/'+str(p)+'/' for x in books for p in range(1,x['page_count']+1)]
    failures=[]
    for path in bookpaths:
        st,headers,body=read_url(base,path)
        parsed=LinkParser();parsed.feed(body.decode('utf-8',errors='replace'))
        graph=parsed.schemas[0].get('@graph',[]) if len(parsed.schemas)==1 and isinstance(parsed.schemas[0],dict) else []
        target_page=[x for x in graph if x.get('@type')=='WebPage' and x.get('url')==BASE+path]
        target_book=[x for x in graph if x.get('@type')=='Book']
        if not(st==200 and parsed.canonicals==[BASE+path] and b'PRINT PAGE' in body and len(target_page)==1 and len(target_book)==1 and b'name="robots" content="index,follow' in body):failures.append(path)
    a.check(not failures, f'Canonical print-page HTML {len(bookpaths)-len(failures)}/{len(bookpaths)} (failed: {failures[:2]})')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=pathlib.Path,default=ROOT);ap.add_argument('--http',help='Site URL for HTTP checks');ap.add_argument('--full-pages',action='store_true',help='HTTP-check all 1,925 canonical print pages')
    opt=ap.parse_args()
    a=Audit();books=static_checks(opt.root,a)
    if opt.http:test_http(opt.http,books,a,opt.full_pages)
    raise SystemExit(0 if a.report() else 1)
if __name__=='__main__':main()
