#!/usr/bin/env python3
"""Non-mutating public static catalog/discovery HTTP contract tests.
Usage: python3 tools/test_static_delivery.py --http http://127.0.0.1:PORT [--all]
Validates canonical routes, 304 behavior, private paths and dynamic fallbacks.
No external crawler, account, telemetry, or runtime logging needed.
"""
from __future__ import annotations
import argparse, json, urllib.request, urllib.error, pathlib, sys

ROOT=pathlib.Path(__file__).resolve().parent.parent

def req(base:str,path:str,method='GET',headers=None):
    request=urllib.request.Request(base.rstrip('/')+path,method=method,headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=12) as r: return r.status,dict(r.headers),r.read()
    except urllib.error.HTTPError as e: return e.code,dict(e.headers),e.read()

def header(h,name):
    return next((v for k,v in h.items() if k.lower()==name.lower()),'')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--http',required=True)
    ap.add_argument('--all',action='store_true',help='Exercise all 241 public snapshots')
    ap.add_argument('--strict-web-server',action='store_true',help='Require static ETag and cache headers from Apache/LiteSpeed (PHP built-in server does not set them)')
    opts=ap.parse_args(); base=opts.http; failures=[]; count=0
    def check(label, condition):
        nonlocal count
        count+=1
        if not condition: failures.append(label)
    route_files={
        '/api/v1/': 'api-cache/v1/index.json',
        '/api/v1/books/': 'api-cache/v1/books.json',
        '/api/v1/research/': 'api-cache/v1/research-index.json',
    }
    for p in (ROOT/'api-cache/v1/books').glob('*.json'):
        slug=p.stem;route_files[f'/api/v1/books/{slug}/']=str(p.relative_to(ROOT))
    for p in (ROOT/'api-cache/v1/toc').glob('*.json'):
        slug=p.stem;route_files[f'/api/v1/books/{slug}/toc/']=str(p.relative_to(ROOT))
    for p in (ROOT/'api-cache/v1/research').glob('*/*.json'):
        group=p.parent.name;route_files[f'/api/v1/research/{group}/{p.stem}/']=str(p.relative_to(ROOT))
    check('Expected snapshot inventory 241',len(route_files)==241)
    routes=sorted(route_files) if opts.all else [
        '/api/v1/', '/api/v1/books/', '/api/v1/research/',
        '/api/v1/books/citizens-guide-to-eviulon/',
        '/api/v1/books/citizens-guide-to-eviulon/toc/',
        *sorted([r for r in route_files if r.startswith('/api/v1/research/eviulon/')])[:2],
        *sorted([r for r in route_files if r.startswith('/api/v1/research/evulgare/')])[:2],
    ]
    for route in routes:
        check('snapshot exists '+route, route in route_files)
        if route not in route_files: continue
        status,h,body=req(base,route)
        check('status 200 '+route, status==200)
        check('body exact '+route,body==(ROOT/route_files[route]).read_bytes())
        check('content-type '+route, 'application/json' in header(h,'Content-Type'))
        check('cache-control '+route,'max-age=' in header(h,'Cache-Control'))
        check('source marker '+route,header(h,'X-Eviulon-Delivery')=='prebuilt-static-json')
        check('CORS '+route,header(h,'Access-Control-Allow-Origin')=='*')
        check('ETag '+route,header(h,'ETag').startswith('"'))
        check('Last-Modified '+route,bool(header(h,'Last-Modified')))
        if opts.strict_web_server:
            check('Apache bypass PHP '+route,not header(h,'X-Powered-By'))
        if opts.all or route in ('/api/v1/books/','/api/v1/research/'):
            etag=header(h,'ETag')
            sc,hc,bc=req(base,route,headers={'If-None-Match':etag})
            check('304 '+route,sc==304 and bc==b'')
            sh,hh,bh=req(base,route,method='HEAD')
            check('HEAD bodyless '+route,sh==200 and bh==b'')
        if route in ('/api/v1/books/','/api/v1/research/'):
            o=json.loads(body)
            check('books 14 '+route,len(o.get('books',[]))==14 if 'books' in route else o.get('total')==210)
            etag=header(h,'ETag')
            s,h2,b2=req(base,route,headers={'If-None-Match':etag})
            check('conditional 304 '+route,s==304 and b2==b'')
            s,h2,b2=req(base,route,method='HEAD')
            check('HEAD 200 bodyless '+route,s==200 and b2==b'')
    for path in ['/robots.txt','/llms.txt','/sitemap.xml','/sitemap-research.xml','/openapi.json','/ai/knowledge.json','/feeds/books.atom']:
        s,h,b=req(base,path)
        check('discovery HTTP 200 '+path,s==200 and len(b)>0)
        if opts.strict_web_server:
            check('discovery caching '+path,'max-age=' in header(h,'Cache-Control'))
            check('discovery ETag '+path,bool(header(h,'ETag')))
            check('no PHP X-Powered-By '+path,not header(h,'X-Powered-By'))
    # Verify direct-to-server public static file inventory (and no manuscript text).
    manifest_path='/ai/static-delivery.json'
    ms,mh,mb=req(base,manifest_path)
    check('static delivery manifest 200',ms==200)
    if ms==200:
        m=json.loads(mb)
        check('manifest release ID',m.get('release_id')==(ROOT/'RELEASE_ID.txt').read_text().strip())
        check('manifest 280 resources',m.get('total')==280)
        check('no bulk text in manifest',m.get('source_text_exported') is False)
        check('counts 241/22/17',m.get('counts')=={'api_snapshot':241,'discovery':22,'asset':17})
        if opts.strict_web_server:
            check('manifest no PHP',not header(mh,'X-Powered-By'))
            check('manifest ETag',bool(header(mh,'ETag')))
            check('manifest cache','max-age=' in header(mh,'Cache-Control'))
            check('manifest delivery marker',header(mh,'X-Eviulon-Delivery')=='prebuilt-static-json')
            st,ht,bt=req(base,manifest_path,headers={'If-None-Match':header(mh,'ETag')})
            check('manifest 304',st==304 and bt==b'')
        if opts.all:
            import hashlib
            for entry in m.get('files',[]):
                path=entry['route']
                if entry['kind']=='api_snapshot':continue # tested above
                ss,hh,bb=req(base,path)
                check('static auxiliary 200 '+path,ss==200)
                check('static auxiliary SHA256 '+path,hashlib.sha256(bb).hexdigest()==entry['sha256'])
                check('static auxiliary size '+path,len(bb)==entry['bytes'])
                if opts.strict_web_server:
                    check('static auxiliary cache '+path,'max-age=' in header(hh,'Cache-Control'))
                    check('static auxiliary ETag '+path,bool(header(hh,'ETag')))
                    check('static auxiliary no PHP '+path,not header(hh,'X-Powered-By'))
                    s304,h304,b304=req(base,path,headers={'If-None-Match':header(hh,'ETag')})
                    check('static auxiliary 304 '+path,s304==304 and b304==b'')
                    sh,hh2,bh=req(base,path,method='HEAD')
                    check('static auxiliary HEAD '+path,sh==200 and bh==b'')
    for path in ['/data/books.json','/src/bootstrap.php','/tools/run_local_qa.sh','/.git/config','/.uai/','/api-cache/']:
        s,h,b=req(base,path)
        check('internal path blocked '+path,s in (403,404))
    s,h,b=req(base,'/api/v1/books/',method='POST')
    check('POST rejected as before',s==405)
    s,h,b=req(base,'/api/v1/research/?page=2')
    check('research page 2 remains dynamic',s==200 and json.loads(b).get('page')==2)
    check('research page 2 not static',header(h,'X-Eviulon-Delivery')=='')
    s,h,b=req(base,'/api/v1/books/citizens-guide-to-eviulon/pages/1/')
    check('single print-page API preserved',s==200 and json.loads(b).get('print_page')==1)
    s,h,b=req(base,'/api/v1/search/?q=machine')
    check('search default official books only',s==200 and json.loads(b).get('scope')==['books'])
    print(f'Static delivery HTTP: {count-len(failures)}/{count} passed on {base} ({len(routes)} catalog routes)')
    if failures:
        for e in failures[:35]: print('FAIL:',e)
        return 1
    return 0

if __name__=='__main__':sys.exit(main())
