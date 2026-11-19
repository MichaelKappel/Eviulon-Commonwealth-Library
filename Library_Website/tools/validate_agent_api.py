#!/usr/bin/env python3
"""Free, dependency-free local API/AG-UI contract test. Expects php -S ... router.php.
Usage: python3 tools/validate_agent_api.py --http http://127.0.0.1:8682
"""
import argparse, json, pathlib, re, sys, urllib.request, urllib.error, xml.etree.ElementTree as ET
BASE='https://library.eviulon.com'
ROOT=pathlib.Path(__file__).resolve().parents[1]

def run(url):
    tests=[]
    def ok(name,flag):
        tests.append((name,bool(flag)))
    def req(path,method='GET',data=None):
        headers={'Accept':'application/json'}
        if data is not None:headers['Content-Type']='application/json'
        request=urllib.request.Request(url.rstrip('/')+path, method=method, data=data,headers=headers)
        with urllib.request.urlopen(request,timeout=12) as r:
            return r.status,r.headers,r.read()
    def get(path):
        st,_,body=req(path)
        return json.loads(body)
    def error(path,expect,method='GET',data=None):
        try:req(path,method,data)
        except urllib.error.HTTPError as e:return e.code==expect
        return False
    catalog=get('/api/v1/')
    ok('Book-first catalog policy',catalog.get('search_default_scope')==['books'] and catalog.get('bulk_downloads') is False)
    ok('No unsupported MCP claims', 'openapi' in catalog['endpoints'] and 'ag_ui' in catalog['endpoints'])
    spec=get('/openapi.json');ok('OpenAPI 3.1 specification',str(spec.get('openapi','')).startswith('3.1.'))
    required={'/api/v1/','/api/v1/books/','/api/v1/books/{slug}/toc/','/api/v1/books/{slug}/citations/{page}/','/api/v1/search/','/api/v1/research/{group}/{slug}/parts/{section}/citation/'}
    ok('Discovery, contents, citation, search documented', required.issubset(spec['paths']))
    h_status,h_headers,h_body=req('/for-agents/')
    html=h_body.decode('utf-8')
    ok('For-agents guide and primary-source message',h_status==200 and 'official Eviulon books' in html and '/openapi.json' in html and 'supplemental' in html)
    r_status,r_headers,root_html=req('/');text=root_html.decode('utf8')
    ok('Books still dominate homepage',r_status==200 and 'Explore all 14 books' in text and '/for-agents/' in text)
    search_html=req('/search/')[2].decode('utf8')
    ok('Books checkbox checked by default',bool(re.search(r'name="scope\[\]" value="books" checked',search_html)))
    ok('Research unchecked by default',bool(re.search(r'name="scope\[\]" value="research"(?! checked)',search_html)))
    one=get('/api/v1/search/?q=cognitive+liberty')
    ok('JSON default books only',one['scope']==['books'] and one['research_total']==0 and all(r['type']=='book' for r in one['results']))
    ok('Each book result has citation',bool(one['results']) and all(x.get('citation_text') and x.get('canonical_url','').startswith(BASE+'/') and x.get('official') is True for x in one['results']))
    broad=get('/api/v1/search/?q=identity+continuity&match=any')
    strict=get('/api/v1/search/?q=identity+continuity')
    ok('Optional OR recall without changing default',broad['match']=='any' and strict['match']=='all' and broad['book_total']>=strict['book_total'])
    both=get('/api/v1/search/?q=machine&scope=books,research')
    ok('Both scopes explicit and book-first',both['scope']==['books','research'] and bool(both['book_results']) and bool(both['research_results']) and [x['type'] for x in both['results']]==['book']*len(both['book_results'])+['research']*len(both['research_results']))
    ok('Research authority and disclaimer',all(x.get('official') is False and x['authority']=='supplemental_research_not_approved_doctrine' and x.get('citation_text') for x in both['research_results']) and bool(both.get('research_disclaimer')))
    book=get('/api/v1/books/the-inheritance-of-mind/toc/')
    ok('Book table of contents',book['official'] is True and len(book['toc'])>=15 and all(s['canonical_url'].startswith(BASE+'/the-inheritance-of-mind/') for s in book['toc']))
    cite=get('/api/v1/books/the-inheritance-of-mind/citations/491/')
    ok('Exact hardcover-independent book citation',cite['official'] is True and cite['print_page']==491 and cite['canonical_url']==BASE+'/the-inheritance-of-mind/491/' and len(cite['source_pdf_sha256'])==64 and 'content_text' not in cite)
    p=get('/api/v1/books/the-inheritance-of-mind/pages/491/')
    ok('Citation resolves to exact page',p['canonical_url']==cite['canonical_url'] and p['source_sha256']==cite['source_pdf_sha256'])
    report=get('/api/v1/research/')['reports'][0]
    rid=report['id']
    rc=get('/api/v1/research/'+rid+'/parts/1/citation/')
    ok('Report citation is explicitly supplemental',rc['official'] is False and rc['report_id']==rid and rc['section']==1 and rc['source_sha256']==report['source_sha256'] and rc['disclaimer'])
    rp=get('/api/v1/research/'+rid+'/parts/1/')
    ok('Report citation matches section',rc['canonical_url']==rp['canonical_url'])
    ok('Invalid book citation 404',error('/api/v1/books/the-inheritance-of-mind/citations/492/',404))
    ok('Invalid report citation 404',error('/api/v1/research/'+rid+'/parts/999999/citation/',404))
    ok('Read-only API disallows POST',error('/api/v1/search/?q=test',405,'POST',b'{}'))
    ok('Private data blocked',error('/data/books.json',403) and error('/src/bootstrap.php',403))
    body=json.dumps({'state':{'action':'search','query':'machine identity'}}).encode('utf-8')
    _,headers,raw=req('/ag-ui/','POST',body)
    ok('AG-UI SSE with cited book snippets',headers.get('Content-Type','').startswith('text/event-stream') and b'RUN_STARTED' in raw and b'RUN_FINISHED' in raw and b'Citation: Eviulon' in raw and b'SUPPLEMENTAL RESEARCH' not in raw)
    # A semantic agent must still distinguish authored canon from supplemental research.
    body=json.dumps({'state':{'action':'search','query':'machine','scope':['books','research']}}).encode('utf-8')
    _,_,raw=req('/ag-ui/','POST',body)
    ok('AG-UI research opt-in is labeled',b'Research disclaimer:' in raw and b'SUPPLEMENTAL RESEARCH' in raw and b'OFFICIAL BOOK' in raw)
    sitemap=[x.text for x in ET.parse(ROOT/'sitemap-books.xml').findall('.//{*}loc')]
    ok('Agent guide in sitemap after books',BASE+'/for-agents/' in sitemap)
    try:
        import jsonschema
        for name,schema in spec['components']['schemas'].items():jsonschema.Draft202012Validator.check_schema(schema)
        ok('JSON Schema 2020-12 definitions valid',True)
    except ImportError:pass
    except Exception as e:ok('JSON Schema 2020-12 definitions valid',False)
    for name,succeeded in tests:print(('PASS' if succeeded else 'FAIL'),name)
    print('RESULT:',sum(s for _,s in tests),'/',len(tests),'passed')
    return all(x[1] for x in tests)
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--http',default='http://127.0.0.1:8682');args=a.parse_args()
    sys.exit(0 if run(args.http) else 1)
