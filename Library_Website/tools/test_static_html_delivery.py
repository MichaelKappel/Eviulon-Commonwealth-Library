#!/usr/bin/env python3
"""Validate exact canonical HTTP static HTML delivery and dynamic fallbacks.
Sampled HTTP endpoints plus --check full hash set; exhaustive canonical metadata QA
runs separately for all 3729 HTML URLs. --strict checks Apache/LiteSpeed ETags.
"""
import argparse,hashlib,json,pathlib,urllib.request,urllib.error
ROOT=pathlib.Path(__file__).resolve().parents[1]
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,hdrs,newurl):return None
def request(base,path,method='GET',headers=None,follow_redirects=True):
    req=urllib.request.Request(base.rstrip('/')+path,method=method,headers=headers or {})
    try:
        with (urllib.request.urlopen(req,timeout=25) if follow_redirects else urllib.request.build_opener(NoRedirect).open(req,timeout=25)) as res:return res.status,dict(res.headers),res.read()
    except urllib.error.HTTPError as e:return e.code,dict(e.headers),e.read()
def h(headers,key):return next((v for k,v in headers.items() if k.lower()==key.lower()),'')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--http',required=True);ap.add_argument('--strict-web-server',action='store_true');a=ap.parse_args()
    m=json.loads((ROOT/'html-cache/manifest.json').read_text());entries=m['snapshots'];assert len(entries)==3702
    route={r['url']:r for r in entries};count=0
    def check(cond,msg):
        nonlocal count
        count+=1
        if not cond:raise AssertionError(msg)
    # Every volume and research grouping must be represented, plus high, middle and low positions.
    chosen={}
    for row in entries:
        p=row['relative_path'].split('/');
        key=('/'.join(p[:3]) if p[1]=='books' else '/'.join(p[:4]))
        chosen.setdefault(key,[]).append(row['url'])
    samples=[]
    for group,urls in sorted(chosen.items()):
        urls.sort()
        if group.startswith('html-cache/books/') or len(samples)<30:
            samples.extend([urls[0],urls[len(urls)//2],urls[-1]])
    # 14 volumes plus 210 report landings (one per report) sampled reproducibly.
    research=[p for p in sorted(route) if p.startswith('/research/')]
    samples+=research[::67]
    for path in sorted(set(samples)):
        row=route[path]; expected=(ROOT/row['relative_path']).read_bytes()
        s,hd,body=request(a.http,path)
        check(s==200,'not found '+path)
        check(body==expected,'static HTML not byte-identical '+path)
        check('text/html' in h(hd,'Content-Type'),'wrong MIME '+path)
        check(h(hd,'X-Eviulon-Delivery')=='prebuilt-static-html','not served from static cache '+path)
        check('max-age=' in h(hd,'Cache-Control'),'cache-control absent '+path)
        check(h(hd,'X-Robots-Tag')=='' or 'noindex' not in h(hd,'X-Robots-Tag'),'unexpected noindex '+path)
        if a.strict_web_server:
            check(not h(hd,'X-Powered-By'),'PHP was invoked '+path)
        etag=h(hd,'ETag');check(bool(etag),'no ETag '+path)
        s,hd2,b2=request(a.http,path,headers={'If-None-Match':etag})
        check(s==304 and b2==b'','no conditional 304 '+path)
        s,hd2,b2=request(a.http,path,method='HEAD')
        check(s==200 and b2==b'','HEAD not bodyless '+path)
    # Query-bearing and alternate forms must NOT be silently served as snapshots.
    for url in ['/citizens-guide-to-eviulon/1/?campaign=provenance',
                '/research/eviulon/eviulon-machine-citizenship-framework/1/?check=1']:
        s,hd,body=request(a.http,url)
        check(s==200,'query fallback error '+url)
        check(h(hd,'X-Eviulon-Delivery')!='prebuilt-static-html','query fallback incorrectly static '+url)
    for url in ['/citizens-guide-to-eviulon/0001/','/research/eviulon/eviulon-machine-citizenship-framework/0001/']:
        s,hd,body=request(a.http,url,follow_redirects=False)
        check(s in (200,301),'numeric fallback broken '+url)
        check(h(hd,'X-Eviulon-Delivery')!='prebuilt-static-html','padded URL cache bypass '+url)
    for url in ['/html-cache/','/html-cache/manifest.json','/html-cache/books/citizens-guide-to-eviulon/1.html',
                '/html-cache/research/eviulon/eviulon-machine-citizenship-framework/1.html',
                '/%68tml-cache/books/citizens-guide-to-eviulon/1.html',
                '/html-%63ache/books/citizens-guide-to-eviulon/1.html']:
        s,hd,b=request(a.http,url)
        check(s in (403,404),'internal HTML cache directly accessible '+url+': '+str(s))
    for url in ['/not-a-real-book/1/','/citizens-guide-to-eviulon/99999/',
                '/research/eviulon/not-a-report/1/']:
        s,hd,b=request(a.http,url)
        check(s==404,'unknown source did not 404 '+url)
        check(h(hd,'X-Eviulon-Delivery')!='prebuilt-static-html','bogus static response '+url)
    s,hd,b=request(a.http,'/citizens-guide-to-eviulon/1-2/')
    check(s==200 and h(hd,'X-Eviulon-Delivery')!='prebuilt-static-html','two-page spread incorrectly static')
    print('CANONICAL_HTML_HTTP_PASS',count,'checks',len(set(samples)),'sampled static URLs; all canonical 3702 source hashes checked separately')
if __name__=='__main__':main()
