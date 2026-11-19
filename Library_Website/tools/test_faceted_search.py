#!/usr/bin/env python3
"""v3.11 black-box search filter tests, running only against caller-provided local host.
No external API, crawler, or paid service involved.
"""
import argparse
import html
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

class Parser(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':self.links.append(dict(attrs))

def run(base):
    assertions=[]
    def ok(name,assertion):
        assertions.append(bool(assertion));print(('PASS ' if assertion else 'FAIL ')+name)
    def request(route, **kwargs):
        url=base.rstrip('/')+route+('?' + urllib.parse.urlencode(kwargs,doseq=True) if kwargs else '')
        try:
            with urllib.request.urlopen(url,timeout=30) as r:return r.status,r.headers,r.read().decode('utf-8')
        except urllib.error.HTTPError as e:return e.code,e.headers,e.read().decode('utf-8')
    def api(**kw):
        status,_,body=request('/api/v1/search/',**kw)
        return status,json.loads(body)
    query=dict(q='machine',scope='books,research',per_page=50)
    st,all_hits=api(**query)
    ok('Both sources queried and independent mode active',st==200 and all_hits['pagination_mode']=='independent' and all_hits['book_total']>100 and all_hits['research_total']>100)
    book_facet=all_hits['breakdown']['by_book'][0]
    slug=book_facet['slug']
    st,b=api(**query,book_filter=slug)
    ok('Book facet uses exact matching print page total',st==200 and b['book_total']==book_facet['pages'] and b['book_pagination']['total']==book_facet['pages'])
    ok('Every book result is from selected official volume',b['book_results'] and all(r['book']==slug and r['official'] for r in b['book_results']))
    ok('Filtered book statistics have truthful selected distribution',b['breakdown']['books_matched']==1 and sum(x['pages'] for x in b['breakdown']['by_book'])==b['book_total'])
    ok('Available-book facets preserve all-query counts',b['breakdown']['available_by_book']==all_hits['breakdown']['by_book'] and b['breakdown']['available_book_total']==all_hits['book_total'])
    ok('Filtering Books does not alter Research totals',b['research_total']==all_hits['research_total'] and b['research_results']==all_hits['research_results'])
    st,ev=api(**query,research_collection='eviulon')
    ok('Eviulon research filter count is exact',st==200 and ev['research_total']==all_hits['breakdown']['by_research_collection']['Eviulon'])
    ok('Eviulon only research with supplemental provenance',ev['research_results'] and all(x['group']=='Eviulon' and not x['official'] for x in ev['research_results']))
    ok('Filtering Research preserves Book total/results',ev['book_total']==all_hits['book_total'] and ev['book_results']==all_hits['book_results'])
    ok('Research collection facet sums to filtered total',sum(ev['breakdown']['by_research_collection'].values())==ev['research_total'] and ev['breakdown']['by_research_collection']['Evulgare']==0)
    ok('All-query Research breakdown remains available',ev['breakdown']['available_by_research_collection']==all_hits['breakdown']['by_research_collection'] and ev['breakdown']['available_research_total']==all_hits['research_total'])
    st,vg=api(**query,research_collection='evulgare')
    ok('Evulgare research filter selects only Evulgare',st==200 and vg['research_total']==all_hits['breakdown']['by_research_collection']['Evulgare'] and all(x['group']=='Evulgare' for x in vg['research_results']))
    st,both=api(**query,book_filter=slug,research_collection='evulgare',books_page=2,research_page=3)
    ok('Combined independent filters preserve own windows',st==200 and both['book_total']==b['book_total'] and both['research_total']==vg['research_total'])
    ok('Book and Research ordering still authoritative',all(x['type']=='book' for x in both['book_results']) and all(x['type']=='research' for x in both['research_results']) and both['results']==both['book_results']+both['research_results'])
    ok('Filtered page windows bounded correctly',both['book_pagination']['page']<=both['book_pagination']['pages'] and both['research_pagination']['page']<=both['research_pagination']['pages'])
    html_params={'q':'machine','filters':'1','scope[]':['books','research'],'per_page':'50','book_filter':slug,'research_collection':'evulgare','books_page':'2','research_page':'3'}
    st,headers,body=request('/search/',**html_params)
    parser=Parser();parser.feed(body)
    ok('Human search returns source-filtered results',st==200 and 'Official book filter:' in body and 'Research collection filter:' in body)
    ok('Selected facet values retained in HTML controls',f'<option value="{slug}" selected>' in body and '<option value="evulgare" selected>' in body)
    book_links=[html.unescape(x.get('href','')) for x in parser.links if '#book-results' in x.get('href','') and 'books_page=' in x.get('href','')]
    research_links=[html.unescape(x.get('href','')) for x in parser.links if '#research-results' in x.get('href','') and 'research_page=' in x.get('href','')]
    ok('Book paginator preserves Research page and both facets',any('research_page=3' in x and 'book_filter='+slug in x and 'research_collection=evulgare' in x for x in book_links))
    ok('Research paginator preserves Book page and both facets',any('books_page=2' in x and 'book_filter='+slug in x and 'research_collection=evulgare' in x for x in research_links))
    ok('Facet clear links exist', 'Clear book filter' in body and 'Clear research filter' in body)
    st,_,only=request('/search/',q='machine',filters='1',**{'scope[]':['books'],'research_collection':'evulgare'})
    ok('Setting a research facet without opting in does not expose research',st==200 and 'research-results' not in only and 'Research disclaimer' not in only)
    status,books_only=api(q='machine',research_collection='evulgare')
    ok('API research facet alone remains Books-only',status==200 and books_only['scope']==['books'] and books_only['research_total']==0)
    for key,value in [('book_filter','nonexistent-book'),('research_collection','invalid'),('book_filter[]',['the-inheritance-of-mind','foo']),('research_collection[]',['eviulon','evulgare'])]:
        st,p=api(**query,**{key:value})
        ok('API invalid facet blocked: '+key+'='+str(value),st==400 and p['error']=='Invalid source filter')
    st,_,bad_page=request('/search/',q='machine',filters=1,book_filter='does-not-exist')
    ok('HTML invalid facet blocked with accessible recovery',st==400 and 'Return to search' in bad_page)
    st,legacy=api(q='machine',scope='books,research')
    ok('Legacy REST pagination remains unmodified',st==200 and 'pagination_mode' not in legacy and 'filters' not in legacy)
    st,default=api(q='machine')
    ok('Default Books-only official source unchanged',st==200 and default['scope']==['books'] and default['research_total']==0)
    print(f'FACET RESULT {sum(assertions)}/{len(assertions)}')
    return all(assertions)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--http',required=True);args=parser.parse_args()
    sys.exit(0 if run(args.http) else 1)
