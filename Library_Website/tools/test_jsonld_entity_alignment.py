#!/usr/bin/env python3
"""Exhaustive source-registry↔canonical HTML JSON-LD identity/relationship parity.

Reads prebuilt source HTML, never external websites by default; --http tests
representative local HTTP responses. Neither mode proves production indexing.
"""
from __future__ import annotations
import argparse,json,hashlib,pathlib,urllib.request
from html.parser import HTMLParser
from urllib.parse import urlsplit
from build_static_html import routes
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE='https://library.eviulon.com'
REGISTRY='/ai/source-registry.jsonld'

class HeadParser(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.script=[];self.in_script=False
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='link':self.links.append(a)
        if tag=='script' and a.get('type')=='application/ld+json':
            assert not self.in_script,'nested JSON-LD script'
            self.in_script=True;self.script.append('')
    def handle_data(self,data):
        if self.in_script:self.script[-1]+=data
    def handle_endtag(self,tag):
        if tag=='script':self.in_script=False

def parse(html:bytes):
    p=HeadParser();p.feed(html.decode('utf-8'))
    assert len(p.script)==1,'HTML must have exactly one JSON-LD script'
    obj=json.loads(p.script[0]);assert obj.get('@context')=='https://schema.org'
    return p,obj['@graph']

def expected():
    registry=json.loads((ROOT/REGISTRY.lstrip('/')).read_text())
    graph=registry['@graph'];works=[n for n in graph if n.get('@type') in ('Book','Report')]
    assert len(works)==224
    by_url={}
    for w in works:
        assert w['url'] not in by_url,'duplicate work URL'
        by_url[w['url']]=(w['@id'],w['@type'],None)
        for part in w['hasPart']:
            assert part['url'] not in by_url,'duplicate source part URL'
            by_url[part['url']]=(part['@id'],part['@type'],w['@id'])
    assert len(by_url)==3702
    assert sum(v[1]=='Book' for v in by_url.values())==14
    assert sum(v[1]=='Report' for v in by_url.values())==210
    return by_url

def validate_page(url:str,html:bytes,expected_id:str,typ:str,parent:str|None):
    p,graph=parse(html)
    canon=[n.get('href') for n in p.links if n.get('rel')=='canonical']
    assert canon==[url],('HTML canonical',url,canon)
    alts=[n for n in p.links if n.get('rel')=='alternate' and n.get('type')=='application/ld+json']
    assert len(alts)==1 and alts[0].get('href')==REGISTRY,('HTML registry alternate',url,alts)
    matching=[node for node in graph if node.get('@id')==expected_id]
    assert len(matching)==1,('Missing/duplicate HTML JSON-LD identity',url,expected_id)
    node=matching[0]
    assert node.get('@type')==typ,('Entity type mismatch',url,node.get('@type'),typ)
    if parent:
        assert node.get('isPartOf',{}).get('@id')==parent,('Parent mismatch',url,parent)
        assert typ=='CreativeWork'
    else:
        assert typ in ('Book','Report')
    # Both registry and HTML must use the same stable fragment identity.
    assert expected_id.startswith(url+'#'),('Fragment must be anchored at canonical URL',url,expected_id)
    if typ in ('Report','CreativeWork') and '/research/' in url:
        assert (typ!='Report' or 'unverified' in node.get('creativeWorkStatus','').lower()),('Research status',url)
    return 1

def main():
    p=argparse.ArgumentParser();p.add_argument('--http',default=None);a=p.parse_args()
    by_url=expected();mapping=routes();assert len(mapping)==3702
    assert set(by_url)=={BASE+route for route in mapping}
    count=0;byte_count=0
    for route,relative in mapping.items():
        f=ROOT/'html-cache'/relative
        assert f.is_file(),('Missing prebuilt canonical page',route)
        body=f.read_bytes();eid,typ,parent=by_url[BASE+route]
        count+=validate_page(BASE+route,body,eid,typ,parent)
        byte_count+=len(body)
    print('JSONLD_IDENTITY_CROSSGRAPH_PASS',count,'canonical HTML pages; 14 books 210 reports 3478 page/sections; html_bytes',byte_count,flush=True)
    if a.http:
        samples=[]
        for label in ('Book','Report'):
            url=next(url for url,(_,typ,par) in by_url.items() if typ==label)
            samples.append(url)
            parent_id=by_url[url][0]
            part=next(candidate for candidate,(_,kind,par) in by_url.items() if par==parent_id)
            samples.append(part)
        for url in samples:
            path=urlsplit(url).path
            with urllib.request.urlopen(a.http.rstrip('/')+path,timeout=30) as r:
                assert r.status==200 and 'text/html' in r.headers.get('Content-Type','')
                validate_page(url,r.read(),*by_url[url])
        with urllib.request.urlopen(a.http.rstrip('/')+REGISTRY,timeout=30) as r:
            assert r.status==200 and 'application/ld+json' in r.headers.get('Content-Type','')
            assert hashlib.sha256(r.read()).digest()==hashlib.sha256((ROOT/REGISTRY.lstrip('/')).read_bytes()).digest()
        print('JSONLD_IDENTITY_HTTP_PASS',len(samples),'sampled canonical endpoints and registry',flush=True)

if __name__=='__main__':main()
