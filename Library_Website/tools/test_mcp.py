#!/usr/bin/env python3
"""Dependency-free real HTTP contract tests for Eviulon MCP 2026-07-28.
Runs only against the local disposable PHP server. No external requests.
"""
from __future__ import annotations
import argparse,hashlib,json,urllib.request,urllib.error

VERSION='2026-07-28'
CHECKS=[]
def check(test,message):
    CHECKS.append((bool(test),message))
    if not test: print('FAIL',message)

def rpc(base,method='server/discover',params=None,*,headers=None,body=None,origin=None,http_method='POST'):
    params=dict(params or {})
    params.setdefault('_meta',{'io.modelcontextprotocol/protocolVersion':VERSION,
      'io.modelcontextprotocol/clientInfo':{'name':'eviulon-qa','version':'1.0'},
      'io.modelcontextprotocol/clientCapabilities':{}})
    if body is None: body={'jsonrpc':'2.0','id':7,'method':method,'params':params}
    request_headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream',
                     'MCP-Protocol-Version':VERSION,'Mcp-Method':method}
    if method=='tools/call':request_headers['Mcp-Name']=str(params.get('name',''))
    if origin is not None: request_headers['Origin']=origin
    request_headers.update(headers or {})
    data=json.dumps(body,ensure_ascii=False).encode('utf-8') if not isinstance(body,bytes) else body
    req=urllib.request.Request(base+'/mcp/',data=data if http_method=='POST' else None,
        headers=request_headers,method=http_method)
    try:
        with urllib.request.urlopen(req,timeout=15) as res:
            return res.status,json.loads(res.read()) if res.status!=202 else None,dict(res.headers)
    except urllib.error.HTTPError as e:
        data=e.read()
        try: parsed=json.loads(data)
        except Exception:parsed=None
        return e.code,parsed,dict(e.headers)

def tool(base,name,arguments):
    return rpc(base,'tools/call',{'name':name,'arguments':arguments})

def run(base):
    status,d,h=rpc(base)
    check(status==200 and d['result']['supportedVersions']==[VERSION],'server/discover modern capability negotiation')
    check(d['result']['capabilities']=={'tools':{'listChanged':False}},'stateless tools-only advertised')
    check(d['result']['_meta']['io.modelcontextprotocol/serverInfo']['name']=='eviulon-library','server identity metadata')
    status,d,h=rpc(base,'tools/list')
    names=[x['name'] for x in d['result']['tools']]
    check(status==200 and len(names)==6 and len(set(names))==6,'six deterministic read-only tools')
    check(all(x['annotations']['readOnlyHint'] is True for x in d['result']['tools']),'all tools annotated read-only')
    check(all(x['inputSchema'].get('additionalProperties') is False for x in d['result']['tools']),'closed tool inputs')
    check(d['result']['resultType']=='complete' and d['result']['ttlMs']==300000,'list tools cache metadata')
    check(rpc(base,'ping')[0]==200,'ping')
    status,d,h=tool(base,'eviulon_list_books',{})
    b=d['result']['structuredContent']
    check(status==200 and len(b['books'])==14 and all(x['official'] for x in b['books']),'official book catalog 14 volumes')
    check(json.loads(d['result']['content'][0]['text'])==b,'MCP structured and unstructured outputs agree')
    check('research_included' in b and b['research_included'] is False,'book catalog excludes research')
    status,d,h=tool(base,'eviulon_search',{'q':'machine identity'})
    s=d['result']['structuredContent']['results']
    check(status==200 and s['scope']==['books'] and s['research_total']==0,'book-only search default')
    check(s==json.load(urllib.request.urlopen(base+'/api/v1/search/?q=machine+identity&limit=5',timeout=15)),'MCP search is byte-semantic equivalent to existing REST search')
    check(all(x['official'] is True for x in s['results']),'book search official-only results')
    status,d,h=tool(base,'eviulon_search',{'q':'machine','scope':'books,research','limit':5})
    both=d['result']['structuredContent']['results']
    check(status==200 and both['scope']==['books','research'],'combined search explicit opt-in')
    check(all(x['official'] is True for x in both['book_results']) and all(x['official'] is False for x in both['research_results']),'combined search authority labeling')
    status,d,h=tool(base,'eviulon_evidence',{'q':'cognitive liberty','limit':3})
    eb=d['result']['structuredContent']
    check(status==200 and eb['kind']=='source_evidence_bundle' and eb['scope']==['books'],'MCP evidence default official books')
    check(eb==json.load(urllib.request.urlopen(base+'/api/v1/context/?q=cognitive+liberty&limit=3',timeout=15)),'MCP evidence equals canonical REST evidence contract')
    check(0<len(eb['sources'])<=3 and all(x['official'] for x in eb['sources']),'bounded book evidence')
    check(all(len(x['quote']['text'].encode())<=480 and hashlib.sha256(x['quote']['text'].encode()).hexdigest()==x['quote']['sha256'] for x in eb['sources']),'exact UTF-8 quote SHA-256')
    status,d,h=tool(base,'eviulon_evidence',{'q':'machine','scope':'research','limit':2})
    research=d['result']['structuredContent']
    check(status==200 and research['scope']==['research'] and research['research_disclaimer'],'research-only explicit opt-in')
    check(all(x['official'] is False for x in research['sources']),'research-only sources are supplemental')
    status,d,h=tool(base,'eviulon_read_book_page',{'slug':'the-inheritance-of-mind','page':1})
    page=d['result']['structuredContent']
    check(status==200 and page['official'] is True and page['citation']['print_page']==1,'single official page retrieval')
    check('library.eviulon.com/the-inheritance-of-mind/1/'==page['citation']['canonical_url'].removeprefix('https://'),'exact canonical print-page link')
    check(isinstance(page['content_text'],str) and len(page['content_text'])>0,'literal page content')
    canonical=json.load(urllib.request.urlopen(base+'/api/v1/books/the-inheritance-of-mind/pages/1/',timeout=15))
    check(page['content_text']==canonical['content_text'] and page['citation']['canonical_url']==canonical['canonical_url'],'MCP single page exactly matches REST source bytes and URL')
    status,d,h=tool(base,'eviulon_book_contents',{'slug':'the-inheritance-of-mind'})
    toc=d['result']['structuredContent']
    check(status==200 and toc['official'] and len(toc['toc'])>1,'verified book TOC links')
    check(all(x['canonical_url'].startswith('https://library.eviulon.com/') for x in toc['toc']),'TOC canonical anchors')
    # Choose actual catalog entry to avoid invented report names.
    report_req=urllib.request.urlopen(base+'/api/v1/research/',timeout=15)
    report=json.load(report_req)['reports'][0]
    group,slug=report['id'].split('/')
    status,d,h=tool(base,'eviulon_read_research_section',{'group':group,'slug':slug,'section':1})
    research_part=d['result']['structuredContent']
    check(status==200 and research_part['official'] is False and research_part['disclaimer'],'supplemental section disclaimer')
    check(research_part['citation']['canonical_url'].startswith('https://library.eviulon.com/research/'),'real research provenance URL')
    check('content_text' in research_part and len(research_part['content_text'])>0,'public research section content')
    # Strict negative controls, including protocol version and envelope/header mismatch.
    check(rpc(base,http_method='GET')[0]==405,'GET not accepted on MCP endpoint')
    check(rpc(base,http_method='DELETE')[0]==405,'DELETE not accepted on MCP endpoint')
    check(rpc(base,origin='https://malicious.example')[0]==403,'cross-origin request rejected')
    check(rpc(base,origin='http://127.0.0.1:7788',headers={'Host':'127.0.0.1:7788'})[0]==403,'spoofed loopback Host cannot bypass Origin validation')
    check(rpc(base,origin='https://library.eviulon.com')[0]==200,'canonical production Origin accepted')
    status,d,_=rpc(base,headers={'MCP-Protocol-Version':'2025-11-25'})
    check(status==400 and d['error']['code']==-32020,'protocol header/body mismatch fail closed')
    status,d,_=rpc(base,params={'_meta':{'io.modelcontextprotocol/protocolVersion':'2025-11-25','io.modelcontextprotocol/clientCapabilities':{}}},headers={'MCP-Protocol-Version':'2025-11-25'})
    check(status==400 and d['error']['code']==-32022 and d['error']['data']['supported']==[VERSION],'unsupported legacy protocol error with supported version')
    status,d,_=rpc(base,headers={'Mcp-Method':'tools/list'})
    check(status==400 and d['error']['code']==-32020,'method header/body mismatch')
    status,d,_=rpc(base,'tools/call',{'name':'eviulon_search','arguments':{'q':'rights'}},headers={'Mcp-Name':'eviulon_read_book_page'})
    check(status==400 and d['error']['code']==-32020,'tool name header/body mismatch')
    status,d,_=rpc(base,'tools/call',{'name':'eviulon_list_books','arguments':{}},headers={'Mcp-Name':'=?base64?ZXZpdWxvbl9saXN0X2Jvb2tz?='})
    check(status==200,'base64-encoded standard Mcp-Name supported')
    status,d,_=rpc(base,'tools/call',{'name':'eviulon_list_books','arguments':{}},headers={'Mcp-Name':'=?base64?BAD!?='})
    check(status==400 and d['error']['code']==-32020,'malformed encoded Mcp-Name rejected')
    status,d,_=rpc(base,'tools/call',{'name':'eviulon_list_books','arguments':{}},headers={'Mcp-Name':''})
    check(status==400 and d['error']['code']==-32020,'missing tool name header rejected')
    status,d,_=rpc(base,'initialize')
    check(status==404 and d['error']['code']==-32601,'legacy initialize unsupported, explicitly version-bound')
    status,d,_=rpc(base,'resources/list')
    check(status==404 and d['error']['code']==-32601,'undeclared resources capability absent')
    status,d,_=rpc(base,body=[{'jsonrpc':'2.0','id':1,'method':'ping','params':{}}])
    check(status==400 and d['error']['code']==-32600,'JSON-RPC batch rejected')
    status,d,_=rpc(base,body=b'{this is not valid json')
    check(status==400 and d['error']['code']==-32700,'malformed JSON fail closed')
    status,d,_=rpc(base,headers={'Content-Type':'text/plain'})
    check(status==415,'incorrect content type rejected')
    status,d,_=rpc(base,headers={'Accept':'application/json'})
    check(status==406,'missing dual Accept support rejected')
    status,d,_=rpc(base,body=b' '*16385)
    check(status==413,'oversized actual request body rejected')
    status,d,_=tool(base,'eviulon_search',{'q':'machine','scope':'invalid'})
    check(status==400 and d['error']['code']==-32602,'invalid search scope fail closed')
    status,d,_=tool(base,'eviulon_search',{'q':'machine','scope':'books,research','limit':50})
    check(status==400 and d['error']['code']==-32602,'unbounded limit rejected')
    status,d,_=tool(base,'eviulon_evidence',{'q':'m'})
    check(status==400 and d['error']['code']==-32602,'short query rejected')
    status,d,_=tool(base,'eviulon_read_book_page',{'slug':'the-inheritance-of-mind','page':10000})
    check(status==400 and d['error']['code']==-32602,'unknown book page rejected')
    status,d,_=tool(base,'eviulon_read_book_page',{'slug':'the-inheritance-of-mind','page':1,'private':1})
    check(status==400 and d['error']['code']==-32602,'arbitrary tool arguments rejected')
    status,d,_=tool(base,'eviulon_read_research_section',{'group':'private','slug':slug,'section':1})
    check(status==400 and d['error']['code']==-32602,'no private research collection')
    status,d,_=tool(base,'eviulon_tools_delete_everything',{})
    check(status==400 and d['error']['code']==-32602,'no write or arbitrary tools')
    status,d,_=tool(base,'eviulon_evidence',{'q':'machine','scope':['books','research']})
    check(status==400 and d['error']['code']==-32602,'no implicit research from array coercion')
    check(all(x[0] for x in CHECKS),'all MCP contract checks pass')
    count=len(CHECKS)
    print('EVIULON MCP:', ('PASS' if all(v for v,_ in CHECKS) else 'FAIL'), f'{sum(v for v,_ in CHECKS)}/{count} checks')
    return 0 if all(v for v,_ in CHECKS) else 1

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--http',required=True);args=ap.parse_args()
    from live_agent_readiness import validate_target
    raise SystemExit(run(validate_target(args.http)))
