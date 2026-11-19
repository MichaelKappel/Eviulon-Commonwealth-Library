#!/usr/bin/env python3
"""Live local private-monitor contract test; requires disposable QA server + temporary QA credentials.

Does not write data directly. Never point this at production with QA credentials.
"""
import argparse, base64, datetime, json, os, pathlib, urllib.error, urllib.parse, urllib.request

TEST_PASSWORD='qa-only-not-for-production-8675309'
TOKEN='not-allowed-in-monitor-records-EXACTTOKEN-7a9c'

def request(url, *, user=None, password=TEST_PASSWORD, ua=None, method='GET'):
    headers={}
    if user is not None:
        b64=base64.b64encode(f'{user}:{password}'.encode()).decode('ascii')
        headers['Authorization']='Basic '+b64
    if ua: headers['User-Agent']=ua
    req=urllib.request.Request(url,headers=headers,method=method)
    try:
        with urllib.request.urlopen(req,timeout=12) as response:
            return response.status,dict(response.headers),response.read()
    except urllib.error.HTTPError as error:
        return error.code,dict(error.headers),error.read()


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--http',default='http://127.0.0.1:8683')
    p.add_argument('--fixture-root',type=pathlib.Path,help='Temporary QA copy, never production')
    args=p.parse_args()
    root=args.http.rstrip('/')
    n=0
    def check(test,condition):
        nonlocal n
        n+=1
        if not condition: raise AssertionError(f'{test} failed')

    url=root+'/admin/crawlers/summary.json'
    status,headers,body=request(url)
    check('unauthenticated 401',status==401)
    check('no cache even on 401', 'no-store' in headers.get('Cache-Control',''))
    check('failed auth hides statistics',b'official_books' not in body)
    status,headers,body=request(url,user='admin',password='invalid')
    check('wrong password 401',status==401)
    status,headers,body=request(url,user='admin')
    check('authorized aggregate 200',status==200)
    check('authorized no-store','no-store' in headers.get('Cache-Control',''))
    check('robots exclusion','noindex' in headers.get('X-Robots-Tag',''))
    payload=json.loads(body)
    check('schema v1',payload['schema_version']=='1.0')
    check('claims unverified',payload['crawler_identity']=='self_reported_user_agent_unverified')
    check('all 14 book entries',len(payload['official_books'])==14)
    check('no raw request records',not any(k in payload for k in ['requests','user_agents','raw_logs','recent']))
    check('no private record fields',not any(k in payload for k in ['user_agent','referrer_host','remote_addr','cookie','ip_address','search_query']))
    check('no fabricated indexing',set(payload['no_claim_of']) >= {'search_indexing','model_training'})
    check('log completeness exists','completeness' in payload)
    baseline=payload['metrics']['requests']
    check('baseline nonnegative',baseline>=0)
    # The request below should produce a books-only PHP access record with no search-string retention.
    status,_,_=request(root+'/the-inheritance-of-mind/1/?q='+TOKEN,ua='GPTBot QA-SyntheticUserAgent-InternalOnly')
    check('canonical book request HTTP 200',status==200)
    status,_,_=request(root+'/research/',ua='GPTBot QA-SyntheticUserAgent-InternalOnly')
    check('research directory HTTP 200',status==200)
    status,_,_=request(root+'/api/v1/search/?q=cognitive+liberty&scope=books,research&secret='+TOKEN,ua='GPTBot QA-SyntheticUserAgent-InternalOnly')
    check('search API HTTP 200',status==200)
    status,_,body=request(url,user='admin')
    check('authorized follow-up',status==200)
    updated=json.loads(body)
    check('metrics increased for bot claim',updated['metrics']['requests']>=baseline+3)
    check('book source request categorized',updated['by_source'].get('books',0)>=1)
    check('research source request categorized',updated['by_source'].get('research',0)>=1)
    check('search not wrongly attributed',updated['by_source'].get('unattributed-search-or-agent',0)>=1)
    check('page request accounted',updated['metrics']['successful_book_pages']>=1)
    check('no secret query in aggregates',TOKEN.encode() not in body)
    check('no synthetic UA raw string in aggregates',b'QA-SyntheticUserAgent' not in body)
    if args.fixture_root:
        log=args.fixture_root/'data'/'monitor-logs'/('hits-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')+'.jsonl')
        check('log file exists after PHP request',log.is_file())
        text=log.read_text(encoding='utf8')
        check('raw request logs omit private search params',TOKEN not in text)
        check('raw request logs omit raw user agents','QA-SyntheticUserAgent' not in text)
        check('schema v2 appears in raw record', '"schema_version":2' in text)
        check('raw logs no referrer or UA fields',not any('\"'+f+'\"' in text for f in ['user_agent','referrer_host','remote_addr','cookie','search_query']))
    status,headers,body=request(root+'/admin/crawlers/',user='admin')
    check('dashboard 200',status==200)
    check('dashboard authoritative books',b'Official books remain authoritative' in body)
    check('dashboard research disclaimer',b'Research' in body and b'supplemental' in body)
    status,headers,body=request(url+'?days=999&filter=bogus',user='admin')
    check('bound filter scope',json.loads(body)['window_days']==7 and json.loads(body)['visitor_filter']=='bots')
    status,headers,body=request(url,user='admin',method='POST')
    check('methods rejected',status==405)
    print(f'PASS: {n}/{n} observability/auth/privacy/authority HTTP checks')

if __name__=='__main__':main()
