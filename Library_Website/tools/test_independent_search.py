#!/usr/bin/env python3
"""v3.10 end-to-end independent search and truthful facet regression checks.
Local fixture only; does not require or invoke paid external services.
"""
from __future__ import annotations
import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
        self.sections=[]
        self.checkboxes=[]
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=='a':self.links.append(attrs)
        if tag=='section' and 'id' in attrs:self.sections.append(attrs['id'])
        if tag=='input' and attrs.get('type')=='checkbox':self.checkboxes.append(attrs)


def run(base):
    checks=[]
    def check(label, condition):
        checks.append((label,bool(condition)))
        print(('PASS' if condition else 'FAIL')+' '+label)
    def request(path):
        with urllib.request.urlopen(base.rstrip('/')+path,timeout=30) as r:
            return r.status,r.headers,r.read().decode('utf-8')
    def get(path):return json.loads(request(path)[2])
    def page(**params):
        q=urllib.parse.urlencode(params,doseq=True)
        st,headers,body=request('/search/?'+q)
        parser=LinkParser();parser.feed(body)
        return headers,body,parser
    default_headers,default,default_parse=page()
    check('Search remains noindex', 'noindex' in default.lower())
    check('Books checked by default',any(x.get('value')=='books' and 'checked' in x for x in default_parse.checkboxes))
    check('Research unchecked by default',any(x.get('value')=='research' and 'checked' not in x for x in default_parse.checkboxes))
    check('Independent result count control default 50','<option value="50" selected>' in default)

    qp={'q':'machine','filters':'1','scope[]':['books','research'],'per_page':'50'}
    headers,both,links=page(**qp)
    bk=get('/api/v1/search/?q=machine&scope=books,research&per_page=50')
    check('Independent API mode is explicit',bk.get('pagination_mode')=='independent')
    check('Both sources produce 50 hits with no hidden 70/30 allocation',len(bk['book_results'])==50 and len(bk['research_results'])==50)
    check('All indexed result totals are represented', bk['total']==bk['book_total']+bk['research_total'])
    check('Page statistics are full-query totals not current page counts',f'{bk["book_total"]:,}' in both and f'{bk["research_total"]:,}' in both)
    bybook=bk['breakdown']['by_book']; bygroup=bk['breakdown']['by_research_collection'];
    check('Official book facet sums exactly',sum(x['pages'] for x in bybook)==bk['book_total'] and bk['breakdown']['books_matched']==len(bybook)<=14)
    check('Research collection facets sum exactly',sum(bygroup.values())==bk['research_total'] and set(bygroup)=={'Eviulon','Evulgare'})
    check('Research unique reports and top report excerpt are coherent',0<bk['breakdown']['reports_matched']<=210 and all(x['sections']>0 and x['report_id'].startswith(('eviulon/','evulgare/')) for x in bk['breakdown']['top_research_reports']))
    check('Both result regions and source authority notices present','book-results' in links.sections and 'research-results' in links.sections and 'Research disclaimer' in both)
    check('Both windows range 1–50',both.count('Showing <strong>1–50</strong>')==2)
    check('Independent book link preserves Research page',any('books_page=2' in (x.get('href') or '') and 'research-results' not in (x.get('href') or '') and '#book-results' in x.get('href','') for x in links.links))
    check('Independent research link preserves Books page',any('research_page=2' in x.get('href','') and '#research-results' in x.get('href','') for x in links.links))

    params=dict(qp);params.update(books_page=2,research_page=3)
    _,mixed,mixed_links=page(**params)
    check('HTML windows page independently', 'Showing <strong>51–100</strong>' in mixed and 'Showing <strong>101–150</strong>' in mixed)
    book_link=next((x['href'] for x in mixed_links.links if 'books_page=3' in x.get('href','') and '#book-results' in x['href']),None)
    research_link=next((x['href'] for x in mixed_links.links if 'research_page=4' in x.get('href','') and '#research-results' in x['href']),None)
    book_href=urllib.parse.parse_qs(urllib.parse.urlparse(html.unescape(book_link or '')).query)
    research_href=urllib.parse.parse_qs(urllib.parse.urlparse(html.unescape(research_link or '')).query)
    check('Book navigation preserves research_page=3 and selected scopes',book_href.get('research_page')==['3'] and book_href.get('books_page')==['3'] and set(v for k,vals in book_href.items() if k.startswith('scope[') for v in vals)=={'books','research'})
    check('Research navigation preserves books_page=2 and selected scopes',research_href.get('books_page')==['2'] and research_href.get('research_page')==['4'] and set(v for k,vals in research_href.items() if k.startswith('scope[') for v in vals)=={'books','research'})
    two=get('/api/v1/search/?q=machine&scope=books,research&per_page=50&books_page=2&research_page=3')
    check('JSON independent source window metadata',two['book_pagination']['from']==51 and two['research_pagination']['from']==101)
    check('Stable totals across pages and canonical references',two['book_total']==bk['book_total'] and two['research_total']==bk['research_total'] and all(x['canonical_url'].startswith('https://library.eviulon.com/') for x in two['results']))
    check('Source priority preserved in combined results', [x['type'] for x in two['results']]==['book']*len(two['book_results'])+['research']*len(two['research_results']))

    _,only,only_links=page(q='machine',filters='1',**{'scope[]':['books']})
    check('Books-only search has no research results or research metrics','research-results' not in only_links.sections and 'Matching supplemental research sections' not in only)
    _,research_only,research_only_links=page(q='machine',filters='1',**{'scope[]':['research']})
    check('Research-only search contains disclaimer but no official results','book-results' not in research_only_links.sections and 'Research disclaimer:' in research_only)
    _,none,none_links=page(q='machine',filters='1')
    check('No checkbox selected means no search scope','Select Books, Research, or both' in none and 'book-results' not in none_links.sections)
    _,xss,_=page(q='<script>alert(1)</script>',filters=1,**{'scope[]':['books']})
    check('User query is escaped in HTML', '<script>alert(1)</script>' not in xss and '&lt;script&gt;' in xss)
    small=get('/api/v1/search/?q=machine&scope=books,research&per_page=25')
    large=get('/api/v1/search/?q=machine&scope=books,research&per_page=100')
    check('25/50/100 apply PER SOURCE',len(small['book_results'])==len(small['research_results'])==25 and len(large['book_results'])==len(large['research_results'])==100)
    out_of_range=get('/api/v1/search/?q=machine&scope=books,research&per_page=100&books_page=9999&research_page=9999')
    check('Overlarge pages clamp to populated final pages',out_of_range['book_pagination']['page']==out_of_range['book_pagination']['pages'] and out_of_range['research_pagination']['page']==out_of_range['research_pagination']['pages'] and len(out_of_range['book_results'])>0 and len(out_of_range['research_results'])>0)
    legacy=get('/api/v1/search/?q=machine&scope=books,research')
    check('Existing REST interface keeps original shared-page contract',legacy.get('pagination_mode') is None and legacy.get('limit')==20 and legacy.get('page')==1 and len(legacy['results'])<=20)
    check('Book-first defaults remain in old API',get('/api/v1/search/?q=machine')['scope']==['books'])
    qnone=get('/api/v1/search/?q=madeupnotaword&scope=books,research&per_page=50')
    check('Zero-hit facets and pages are stable',qnone['total']==0 and qnone['book_pagination']['from']==0 and qnone['research_pagination']['to']==0)
    print(f'RESULT: {sum(v for _,v in checks)}/{len(checks)} passed')
    return all(ok for _,ok in checks)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--http',default='http://127.0.0.1:8898');a=p.parse_args()
    sys.exit(0 if run(a.http) else 1)
