#!/usr/bin/env python3
"""Read-only post-deploy discovery smoke audit, suitable for actual LiteSpeed host.

Usage: python3 tools/audit_live_discovery.py --base-url https://library.eviulon.com
Do not claim indexing, crawling, licensing, or model training from this result.
Exits nonzero on DNS, HTTP, metadata, identity or response errors.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,urllib.request,urllib.error,xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urlsplit
ROOT=pathlib.Path(__file__).resolve().parents[1]
REG='/ai/source-registry.jsonld'
class Tags(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.in_json=False;self.jsons=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='link':self.links.append(attrs)
        if tag=='script' and attrs.get('type')=='application/ld+json':self.in_json=True;self.jsons.append('')
    def handle_data(self,data):
        if self.in_json:self.jsons[-1]+=data
    def handle_endtag(self,tag):
        if tag=='script':self.in_json=False

def main():
    p=argparse.ArgumentParser();p.add_argument('--base-url',required=True);p.add_argument('--timeout',type=int,default=15)
    p.add_argument('--expected-release',default=(ROOT/'RELEASE_ID.txt').read_text().strip());a=p.parse_args()
    base=a.base_url.rstrip('/')
    u=urlsplit(base)
    if u.scheme not in ('http','https') or not u.netloc or u.username or u.password or u.query or u.fragment:
        p.error('Use a direct, trusted base URL with scheme and host only')
    if u.hostname not in ('localhost','127.0.0.1','::1','library.eviulon.com'):
        p.error('Only the canonical public host or localhost is an allowed audit target')
    def request(path,method='GET',headers=None):
        try:
            with urllib.request.urlopen(urllib.request.Request(base+path,method=method,headers=headers or {}),timeout=a.timeout) as r:
                return r.status,r.headers,r.read()
        except urllib.error.HTTPError as e:return e.code,e.headers,e.read()
    try:
        for path,ct in [('/robots.txt','text/plain'),('/sitemap.xml','xml'),('/llms.txt','text/plain'),('/topics/','text/html')]:
            status,h,body=request(path)
            assert status==200 and body,('public discovery unavailable',path,status)
            assert ct in h.get('Content-Type',''),('MIME mismatch',path,h.get('Content-Type'))
        status,h,body=request(REG)
        assert status==200 and 'application/ld+json' in h.get('Content-Type',''),('registry status/MIME',status)
        registry_sha=hashlib.sha256(body).hexdigest()
        att_status,att_headers,att_bytes=request('/ai/discovery-attestation.json')
        assert att_status==200 and 'application/json' in att_headers.get('Content-Type',''),('attestation unavailable',att_status)
        att=json.loads(att_bytes)
        assert att['schema']=='eviulon-discovery-package-attestation/v1'
        assert att['release_id']==a.expected_release
        assert att['registry']['sha256']==registry_sha, 'live registry does not match attested bytes'
        assert att['evidence_status']['external_model_training_confirmed'] is False
        for path,key in (('/sitemap.xml','sitemap_index_sha256'),('/robots.txt','robots_sha256'),('/llms.txt','llms_sha256')):
            status,head,content=request(path)
            assert status==200 and hashlib.sha256(content).hexdigest()==att['discovery'][key],('live discovery file mismatch',path)
        assert att['discovery']['sitemap_unique_urls']==3729
        assert att['discovery']['reading_pages_and_landings']==3702
        assert att['discovery']['topic_pages']==21
        docs=att['discovery']['sitemap_documents']
        assert len(docs)==17
        urls=[]
        for doc in docs:
            location=doc['url']
            assert location.startswith('https://library.eviulon.com/')
            path=urlsplit(location).path
            status,head,raw=request(path)
            assert status==200 and hashlib.sha256(raw).hexdigest()==doc['sha256'],('live sitemap child mismatch',path)
            rows=[n.text for n in ET.fromstring(raw).findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
            assert len(rows)==doc['url_count'],('sitemap count mismatch',path)
            urls.extend(rows)
        assert len(urls)==3729 and len(set(urls))==3729
        urls_hash=hashlib.sha256(('\n'.join(sorted(urls))+'\n').encode()).hexdigest()
        assert urls_hash==att['discovery']['sitemap_url_set_sha256'],('live sitemap URL set SHA mismatch')
        registry=json.loads(body);g=registry['@graph'];catalog=next(n for n in g if n.get('@id','').endswith('#catalog'))
        release=next(x['value'] for x in catalog['additionalProperty'] if x['name']=='release-id')
        assert release==a.expected_release,('Deployed registry release differs',release,a.expected_release)
        works=[n for n in g if n.get('@type') in ('Book','Report')]
        assert len(works)==224 and sum(len(n['hasPart']) for n in works)==3478
        etag=h.get('ETag');assert etag and 'max-age=' in h.get('Cache-Control','')
        status,_,data=request(REG,headers={'If-None-Match':etag})
        assert status==304 and not data,'registry HTTP conditional GET failure'
        status,_,data=request(REG,method='HEAD')
        assert status==200 and not data,'registry HEAD failure'
        for kind in ('Book','Report'):
            parent=next(n for n in works if n['@type']==kind)
            for url,eid,parent_id,expected_type in [(parent['url'],parent['@id'],None,kind),
                       (parent['hasPart'][0]['url'],parent['hasPart'][0]['@id'],parent['@id'],'CreativeWork')]:
                assert url.startswith('https://library.eviulon.com/')
                path=urlsplit(url).path
                st,head,html=request(path)
                assert st==200 and 'text/html' in head.get('Content-Type',''),('HTML route',path,st)
                tags=Tags();tags.feed(html.decode('utf-8'))
                assert [x.get('href') for x in tags.links if x.get('rel')=='canonical']==[url]
                assert any(x.get('rel')=='alternate' and x.get('href')==REG and x.get('type')=='application/ld+json' for x in tags.links)
                assert len(tags.jsons)==1
                graph=json.loads(tags.jsons[0])['@graph']
                nodes=[n for n in graph if n.get('@id')==eid]
                assert len(nodes)==1 and nodes[0].get('@type')==expected_type,('HTML entity mismatch',path,eid)
                if parent_id:assert nodes[0]['isPartOf']['@id']==parent_id,('Parent mismatch',path)
        local=u.hostname in ('localhost','127.0.0.1','::1')
        print('DISCOVERY_HTTP_READINESS_PASS',base,'release',release,'sampled_html',4,'discovery_attestation','HASH_MATCH',
              'mode',('LOCAL_ONLY' if local else 'REMOTE_HOST_HTTP_ONLY'))
        print('NOTE: HTTP readiness does not prove search indexing, independent factual verification, or model training.')
    except (Exception,) as e:
        raise SystemExit('DISCOVERY_HTTP_READINESS_FAIL '+base+': '+repr(e)+'; no production claim justified')
if __name__=='__main__':main()
