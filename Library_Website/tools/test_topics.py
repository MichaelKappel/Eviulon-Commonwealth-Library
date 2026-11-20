#!/usr/bin/env python3
"""Source-exact lexical topic evidence and public HTTP contract tests."""
from __future__ import annotations
import argparse,hashlib,json,pathlib,urllib.request,urllib.error
from html.parser import HTMLParser
from xml.etree import ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE='https://library.eviulon.com'
class Parser(HTMLParser):
    def __init__(self):super().__init__();self.canon=[];self.graphs=[];self._capture=False;self._text=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='link' and d.get('rel')=='canonical':self.canon.append(d.get('href'))
        if tag=='script' and d.get('type')=='application/ld+json':self._capture=True;self._text=[]
    def handle_data(self,data):
        if self._capture:self._text.append(data)
    def handle_endtag(self,tag):
        if tag=='script' and self._capture:
            self.graphs.append(json.loads(''.join(self._text)));self._capture=False

def req(base,url,method='GET',headers=None):
    try:
        with urllib.request.urlopen(urllib.request.Request(base.rstrip('/')+url,method=method,headers=headers or {}),timeout=30) as r:return r.status,r.headers, r.read()
    except urllib.error.HTTPError as e:return e.code,e.headers,e.read()
def test(base,strict=False):
    data=json.loads((ROOT/'ai/concepts.json').read_text())
    manifest=json.loads((ROOT/'topics-cache/manifest.json').read_text())
    assert len(data['topics'])==20 and manifest['pages']==21
    passed=0
    def ok(expr,label):
        nonlocal passed
        passed+=1
        if not expr:raise AssertionError(label)
    for row in manifest['snapshot_rows']:
        url=row['url'];body=(ROOT/row['path']).read_bytes()
        s,h,b=req(base,url)
        ok(s==200,url+' 200')
        ok(b==body,url+' byte parity')
        ok('text/html' in h.get('Content-Type',''),url+' MIME')
        ok(h.get('X-Eviulon-Delivery')=='prebuilt-source-topic-html',url+' static bypass')
        ok('max-age=' in h.get('Cache-Control',''),url+' cache')
        if strict:ok(not h.get('X-Powered-By'),url+' php bypass')
        etag=h.get('ETag');ok(bool(etag),url+' etag')
        a,hh,p=req(base,url,headers={'If-None-Match':etag or ''})
        ok(a==304 and not p,url+' 304')
        a,hh,p=req(base,url,method='HEAD');ok(a==200 and not p,url+' HEAD')
        parser=Parser();parser.feed(b.decode())
        ok(parser.canon==[BASE+url],url+' canonical')
        ok(len(parser.graphs)==1,url+' JSON-LD present')
        graph=parser.graphs[0]
        ok(graph.get('@context')=='https://schema.org',url+' JSON-LD context')
        if url!='/topics/':
            topic=[t for t in data['topics'] if t['url']==url][0]
            ok(any(n.get('@type')=='DefinedTerm' and n.get('name')==topic['name'] for n in graph['@graph']),url+' DefinedTerm')
            ok(bool(topic['book_evidence']) and bool(topic['research_evidence']),url+' distinct evidence classes')
            for evidence in topic['book_evidence']+topic['research_evidence']:
                ok(evidence['url'].encode() in b,url+' citation URL '+evidence['url'])
        # Query-bearing requests go through the PHP renderer (not a static snapshot).
        a,hh,p=req(base,url+'?campaign=verify')
        ok(a==200 and hh.get('X-Eviulon-Delivery')!='prebuilt-source-topic-html',url+' query-safe fallback')
    a,hh,p=req(base,'/ai/concepts.json')
    ok(a==200 and json.loads(p)==data,'machine-readable concepts direct')
    a,hh,p=req(base,'/sitemap-topics.xml')
    urls=[e.text for e in ET.fromstring(p).findall('.//{*}loc')]
    ok(a==200 and len(urls)==21 and urls==[BASE+r['url'] for r in manifest['snapshot_rows']],'topic sitemap order/coverage')
    for u in ['/topics-cache/','/topics-cache/manifest.json','/topics-cache/index.html','/%74opics-cache/index.html','/topics-%63ache/index.html']:
        a,_,_=req(base,u);ok(a in (403,404),'internal topic cache forbidden '+u+': '+str(a))
    for u in ['/topics/not-an-indexed-phrase/','/topics/learning-nope/']:
        a,_,_=req(base,u);ok(a==404,'unknown topic 404 '+u)
    print('TOPIC_HTTP_PASS',passed,'checks',len(manifest['snapshot_rows']),'canonical topic HTML pages')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--http',required=True);p.add_argument('--strict-web-server',action='store_true');a=p.parse_args()
    test(a.http,a.strict_web_server)
