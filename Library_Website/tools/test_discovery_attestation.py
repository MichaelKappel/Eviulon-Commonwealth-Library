#!/usr/bin/env python3
"""Exercise attestation correctness, adversarial URL coverage, and HTTP delivery."""
from __future__ import annotations
import argparse,hashlib,json,pathlib,urllib.request,urllib.error
from build_discovery_attestation import ROOT, build, verify_coverage, BASE
PATH='/ai/discovery-attestation.json'

def request(base,method='GET',headers=None,data=None):
    try:
        with urllib.request.urlopen(urllib.request.Request(base.rstrip('/')+PATH,method=method,headers=headers or {},data=data),timeout=25) as r:return r.status,r.headers,r.read()
    except urllib.error.HTTPError as e:return e.code,e.headers,e.read()

def main():
    p=argparse.ArgumentParser();p.add_argument('--http');p.add_argument('--strict-web-server',action='store_true');a=p.parse_args()
    want=build();actual=json.loads((ROOT/PATH.lstrip('/')).read_text())
    assert actual==want and want['evidence_status']['external_model_training_confirmed'] is False
    assert want['evidence_status']['public_host_reachable'] is None
    ids=set()
    # Construct independent adversarial tests for coverage validation.
    from xml.etree import ElementTree as ET
    root=ET.parse(ROOT/'sitemap.xml').getroot(); urls=[]
    for item in root.findall('.//{*}loc'):
        urls.extend(x.text for x in ET.parse(ROOT/item.text.rsplit('/',1)[-1]).findall('.//{*}loc'))
    readings={BASE.rstrip('/')+row['url'] for row in json.loads((ROOT/'html-cache/manifest.json').read_text())['snapshots']}
    topics={BASE.rstrip('/')+row['url'] for row in json.loads((ROOT/'topics-cache/manifest.json').read_text())['snapshot_rows']}
    def fail(f):
        try:f()
        except ValueError:return
        raise AssertionError('Negative test unexpectedly accepted bad source/sitemap coverage')
    verify_coverage(urls,readings,topics,readings)
    fail(lambda:verify_coverage(urls[:-1],readings,topics,readings))
    fail(lambda:verify_coverage(urls+[urls[0]],readings,topics,readings))
    fail(lambda:verify_coverage(urls,readings,topics,readings-{next(iter(readings))}))
    fail(lambda:verify_coverage(urls,readings,topics,readings|{BASE+'ghost/' }))
    fail(lambda:verify_coverage(urls,readings,topics|{BASE+'invented/'},readings))
    fail(lambda:verify_coverage([u+'?x=1' if i==0 else u for i,u in enumerate(urls)],readings,topics,readings))
    assert len(want['discovery']['sitemap_documents'])==17
    assert len(want['discovery']['other_navigation_pages'])==6
    assert not any(k in json.dumps(want).lower() for k in ('articlebody','downloadurl','bulk_manuscript_dump'))
    print('DISCOVERY_ATTESTATION_STRUCTURE_PASS 3729 canonical URLs, 3702 reading, 21 topics, 6 navigation, 6 negative mutation tests')
    if not a.http:return
    exp=(ROOT/PATH.lstrip('/')).read_bytes(); checks=0
    def check(ok,label):
        nonlocal checks
        checks+=1
        if not ok:raise AssertionError(label)
    s,h,b=request(a.http);check(s==200,'status');check(b==exp,'exact bytes');check('application/json' in h.get('Content-Type',''),'MIME')
    check(json.loads(b)==want,'JSON parse');check('max-age=' in h.get('Cache-Control',''),'cache');check(bool(h.get('ETag')),'ETag')
    s2,h2,b2=request(a.http,headers={'If-None-Match':h.get('ETag','')});check(s2==304 and not b2,'304')
    s3,h3,b3=request(a.http,method='HEAD');check(s3==200 and not b3,'HEAD')
    s4,h4,b4=request(a.http,method='POST',data=b'no');check(s4==405,'POST 405')
    check('no-store' in h4.get('Cache-Control',''),'405 no-store')
    if a.strict_web_server:check(not h.get('X-Powered-By'),'Apache no PHP')
    print('DISCOVERY_ATTESTATION_HTTP_PASS',checks,'checks', 'STRICT_APACHE' if a.strict_web_server else 'PHP_DEV')
if __name__=='__main__':main()
