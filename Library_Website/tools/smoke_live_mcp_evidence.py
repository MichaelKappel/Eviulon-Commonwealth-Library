#!/usr/bin/env python3
"""Bounded public MCP evidence/citation smoke test for the Eviulon library.

Python 3.10+ standard library only. Makes read-only requests to Eviulon's
canonical public host, or loopback for local regression. Does not print
entire books or claim that models have learned from the returned data.
"""
import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

PROTOCOL = '2026-07-28'
CANONICAL = 'https://library.eviulon.com/mcp/'
TOOLS = {
    'eviulon_list_books','eviulon_search','eviulon_evidence',
    'eviulon_read_book_page','eviulon_book_contents',
    'eviulon_read_research_section',
}


def check(condition: bool, label: str) -> None:
    if not condition:
        raise RuntimeError('FAIL: ' + label)
    print('PASS: ' + label)


def post_mcp(url: str, method: str, params: dict | None = None) -> dict:
    params = dict(params or {})
    params['_meta'] = {
        'io.modelcontextprotocol/protocolVersion': PROTOCOL,
        'io.modelcontextprotocol/clientCapabilities': {},
        'io.modelcontextprotocol/clientInfo': {'name':'eviulon-public-smoke', 'version':'1.0'},
    }
    body = json.dumps({'jsonrpc':'2.0','id':7,'method':method,'params':params}).encode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'MCP-Protocol-Version': PROTOCOL,
        'Mcp-Method': method,
        'User-Agent': 'Eviulon-Source-Evidence-Smoke/1.0',
    }
    if method == 'tools/call':
        headers['Mcp-Name'] = params['name']
    req = urllib.request.Request(url, data=body, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            check(response.status == 200, method + ' HTTP 200')
            raw = response.read(1_500_001)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'{method}: HTTP {e.code}; '+e.read(1200).decode('utf-8','replace')) from e
    if len(raw)>1_500_000:
        raise RuntimeError('Response larger than operator smoke limit')
    parsed = json.loads(raw)
    check(parsed.get('jsonrpc') == '2.0' and 'result' in parsed and 'error' not in parsed,
          method + ' JSON-RPC result')
    return parsed['result']


def call(url: str, name: str, args: dict) -> dict:
    r = post_mcp(url, 'tools/call', {'name':name,'arguments':args})
    check(r.get('resultType') == 'complete' and r.get('isError') is False, name + ' successful result')
    content = r.get('structuredContent')
    check(isinstance(content,dict), name + ' structuredContent')
    return content


def get_json(url: str) -> dict:
    req = urllib.request.Request(url,headers={'User-Agent':'Eviulon-Source-Evidence-Smoke/1.0','Accept':'application/json'})
    with urllib.request.urlopen(req, timeout=20) as resp:
        check(resp.status==200, 'REST page HTTP 200')
        return json.loads(resp.read(300_000))


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--url',default=CANONICAL,help='Canonical HTTPS MCP URL (or localhost for offline test)')
    ap.add_argument('--expect-server-version',default='',help='Expected MCP implementation version after deploy')
    opts=ap.parse_args()
    url=opts.url
    p=urllib.parse.urlsplit(url)
    good_host=(p.scheme=='https' and p.netloc=='library.eviulon.com')
    localhost=(p.scheme=='http' and p.hostname in ('localhost','127.0.0.1') and p.username is None and p.password is None)
    if not (good_host or localhost) or p.path!='/mcp/' or p.query or p.fragment:
        ap.error('Only https://library.eviulon.com/mcp/ or explicit local loopback /mcp/ permitted')
    print('Eviulon MCP evidence smoke:',url)
    found = post_mcp(url,'server/discover')
    check(found.get('supportedVersions')==[PROTOCOL],'MCP stateless protocol advertised')
    if opts.expect_server_version:
        server=found.get('_meta',{}).get('io.modelcontextprotocol/serverInfo',{})
        check(server.get('version') == opts.expect_server_version,
              f'server implementation version = {opts.expect_server_version}')
    listed=post_mcp(url,'tools/list')
    names={x['name'] for x in listed['tools']}
    check(names==TOOLS,'all six read-only tools listed')
    check(all(x['annotations']['readOnlyHint'] is True for x in listed['tools']),
          'all tool annotations read-only')
    books=call(url,'eviulon_list_books',{})
    check(len(books.get('books',[]))==14,'all 14 official books returned')
    check(sum(x['print_pages'] for x in books['books'])==1925,'1,925 print-page source count')
    check(books.get('research_included') is False,'no implicit supplemental research')
    search=call(url,'eviulon_search',{'q':'machine identity','limit':3})
    s=search.get('results',{})
    check(s.get('scope')==['books'] and s.get('research_total')==0,'book-only search default')
    evidence=call(url,'eviulon_evidence',{'q':'cognitive liberty','limit':3})
    sources=evidence.get('sources',[])
    check(evidence.get('kind')=='source_evidence_bundle' and evidence.get('scope')==['books'],
          'bounded evidence officially scoped')
    check(1<=len(sources)<=3,'1–3 returned cited sources')
    for n,record in enumerate(sources,1):
        check(record.get('official') is True,f'evidence {n} labelled official')
        quote=record.get('quote',{})
        data=quote.get('text','').encode('utf-8')
        check(bool(data) and len(data)<=480,f'evidence {n} bounded UTF-8 quote')
        check(hashlib.sha256(data).hexdigest()==quote.get('sha256'),f'evidence {n} SHA-256')
        citation=record.get('citation',{})
        url_=citation.get('canonical_url') or record.get('canonical_url') or record.get('url')
        check(isinstance(url_,str) and url_.startswith('https://library.eviulon.com/'),
              f'evidence {n} canonical source link')
    page=call(url,'eviulon_read_book_page',{'slug':'the-inheritance-of-mind','page':1})
    check(page.get('official') is True and page.get('citation',{}).get('print_page')==1,
          'single original print page and citation')
    check(page.get('citation',{}).get('canonical_url')=='https://library.eviulon.com/the-inheritance-of-mind/1/',
          'stable canonical page URL')
    base=url.removesuffix('/mcp/')
    rest=get_json(base+'/api/v1/books/the-inheritance-of-mind/pages/1/')
    check(page.get('content_text')==rest.get('content_text') and
          page['citation']['canonical_url']==rest.get('canonical_url'),
          'MCP page text and citation agree with REST source')
    print('\nPASS: Eviulon MCP source evidence and citation smoke test. No live training claim.')
    return 0

if __name__=='__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print('\nFAIL:',str(exc), file=sys.stderr)
        sys.exit(1)
