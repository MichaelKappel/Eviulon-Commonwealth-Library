#!/usr/bin/env python3
"""Exhaustive schema, canonical, Dublin Core and Open Graph metadata contracts.
Checks locally rendered HTML; this is NOT an external rich-result guarantee.
"""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from urllib.request import urlopen,Request
import xml.etree.ElementTree as ET
BASE='https://library.eviulon.com'
checked=0

def ok(condition,message):
    global checked
    checked+=1
    if not condition:raise AssertionError(message)

class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta={};self.canon=[];self.schema=[];self.js=False
        self.title='';self.in_title=False;self.lang=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='html':self.lang.append(a.get('lang'))
        if tag=='title':self.in_title=True
        if tag=='meta':
            for key in ('name','property'):
                if a.get(key):self.meta.setdefault(a[key],[]).append(a.get('content',''))
        if tag=='link' and a.get('rel')=='canonical':self.canon.append(a.get('href'))
        if tag=='script' and a.get('type')=='application/ld+json':self.js=True;self.schema.append('')
    def handle_endtag(self,tag):
        if tag=='title':self.in_title=False
        if tag=='script':self.js=False
    def handle_data(self,data):
        if self.in_title:self.title+=data
        if self.js:self.schema[-1]+=data

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--http');args=parser.parse_args()
    root=args.root
    books=json.loads((root/'data/books.json').read_text())
    reports=json.loads((root/'data/research/reports.json').read_text())
    bmap={b['slug']:b for b in books};rmap={r['url']:r for r in reports}
    ok(len(books)==14 and sum(x['page_count'] for x in books)==1925,'14 books and 1925 print pages')
    ok(len(reports)==210 and sum(x['parts'] for x in reports)==1553,'210 reports and 1553 sections')
    original_headings=0
    for b in books:
        headings=json.loads((root/'data/sections'/f'{b["slug"]}.json').read_text())
        original_headings+=sum(s['category']=='chapter' for s in headings)
    ok(original_headings==219,'219 source-verified chapter headings')
    url_list=[]
    for entry in ET.parse(root/'sitemap.xml').findall('.//{*}loc'):
        url_list.extend(node.text for node in ET.parse(root/entry.text.rsplit('/',1)[-1]).findall('.//{*}loc'))
    ok(len(url_list)==3708 and len(set(url_list))==3708,'3708 distinct canonical sitemap URLs')
    ok(BASE+'/research/' in url_list,'Research directory is crawlable')
    ok(sum(url.startswith(BASE+'/research/') for url in url_list)==1764,'All supplemental research URLs including directory')
    print('METADATA_STATIC_PASS',checked,'source/sitemap assertions',flush=True)
    if not args.http:return
    counts={'print_page':0,'book':0,'research_dir':0,'research':0,'research_section':0,'other':0}
    for url in url_list:
        path=urlsplit(url).path
        try:
            with urlopen(Request(args.http.rstrip('/')+path,headers={'Accept':'text/html'}),timeout=40) as response:
                html=response.read().decode('utf-8')
                ok(response.status==200,'HTTP 200 '+path)
                ok('text/html' in response.headers.get('Content-Type',''),'HTML MIME '+path)
        except Exception as e:raise AssertionError('Failed '+url+' : '+str(e)) from e
        page=Tags();page.feed(html)
        ok(page.lang==['en'],'HTML lang=en '+path)
        ok(bool(page.title.strip()),'HTML title '+path)
        ok(page.canon==[url],'Exactly one self canonical '+path)
        ok(bool(page.meta.get('description',[''])[0].strip()),'Meta description '+path)
        ok(page.meta.get('robots',[''])[0].startswith('index,follow'),'Canonical indexable '+path)
        ok(page.meta.get('og:url')==[url],'OG URL equals canonical '+path)
        ok(page.meta.get('DC.identifier')==[url],'Dublin Core canonical identifier '+path)
        ok(page.meta.get('DC.title')==[page.title],'Dublin Core title '+path)
        ok(page.meta.get('DC.language')==['en'],'Dublin Core language '+path)
        ok(page.meta.get('DC.type')==['Text'],'Dublin Core type '+path)
        ok(len(page.schema)==1,'Single JSON-LD script '+path)
        data=json.loads(page.schema[0]);graph=data.get('@graph')
        ok(data.get('@context')=='https://schema.org' and isinstance(graph,list),'Schema.org JSON-LD graph '+path)
        web=[n for n in graph if n.get('@type')=='WebSite']
        ok(len(web)==1 and web[0].get('@id')==BASE+'/#website','WebSite identity '+path)
        ids=[n['@id'] for n in graph if '@id' in n]
        ok(len(ids)==len(set(ids)),'Graph IDs unique '+path)
        og_type=page.meta.get('og:type')
        ok(len(og_type or [])==1,'One OG type '+path)
        ok(all('pagination' not in n for n in graph if n.get('@type')=='WebPage'),'No invalid WebPage.pagination '+path)
        s=path.strip('/').split('/') if path!='/' else []
        if len(s)==2 and s[0] in bmap and s[1].isdigit():
            b=bmap[s[0]];n=int(s[1]);ok(1<=n<=b['page_count'],'Book page bounds '+path)
            work=[x for x in graph if x.get('@id')==url+'#print-page']
            page_node=[x for x in graph if x.get('@type')=='WebPage']
            ok(len(work)==1 and work[0].get('@type')=='CreativeWork','Print page CreativeWork '+path)
            ok(work[0].get('identifier')==b['slug']+'/print-page/'+str(n),'Print page identity '+path)
            ok(work[0].get('isPartOf',{}).get('@id')==BASE+f'/{b["slug"]}/#book','Print work belongs to Book '+path)
            ok(len(page_node)==1 and page_node[0].get('mainEntity',{}).get('@id')==url+'#print-page','WebPage mainEntity original printed page '+path)
            ok(page_node[0].get('about',{}).get('@id')==BASE+f'/{b["slug"]}/#book','Print page about Book '+path)
            ok(og_type==['website'],'Book print page OG website '+path)
            counts['print_page']+=1
        elif len(s)==1 and s[0] in bmap:
            b=bmap[s[0]];node=[x for x in graph if x.get('@type')=='Book' and x.get('@id')==url+'#book']
            ok(len(node)==1,'Book schema '+path)
            sections=json.loads((root/'data/sections'/f'{b["slug"]}.json').read_text())
            chapters=[x for x in sections if x['category']=='chapter']
            parts=node[0].get('hasPart',[])
            ok(len(parts)==len(chapters),'Book hasPart chapter count '+path)
            for a,h in zip(parts,chapters):
                ok(a.get('@id')==BASE+h['url'] and a.get('url')==BASE+h['url'],'Chapter is original heading anchor '+path)
                ok(a.get('isPartOf',{}).get('@id')==url+'#book','Chapter parent Book '+path)
                ok('no verified full-chapter page range' in a.get('description',''),'Chapter range not fabricated '+path)
            ok(og_type==['book'],'OG book landing '+path)
            counts['book']+=1
        elif path=='/research/':
            coll=[x for x in graph if x.get('@type')=='CollectionPage']
            ok(len(coll)==1 and coll[0].get('@id')==url+'#collection','CollectionPage identity')
            items=coll[0]['mainEntity']['itemListElement']
            ok(coll[0]['mainEntity']['numberOfItems']==210 and len(items)==210,'210 reports enumerated')
            ok({x['url'] for x in items}=={BASE+r['url'] for r in reports},'Exact 210 report URLs')
            ok(og_type==['website'],'Research directory OG website')
            counts['research_dir']+=1
        elif path in rmap:
            r=rmap[path];rep=[x for x in graph if x.get('@id')==url+'#research']
            ok(len(rep)==1 and rep[0].get('@type')=='Report','Report type '+path)
            ok(rep[0].get('creativeWorkStatus')==r['status'],'Supplemental verification status '+path)
            ok(rep[0].get('identifier')==r['id'],'Source-backed report identifier '+path)
            ok(rep[0].get('isPartOf',{}).get('@id')==BASE+'/research/#collection','Report belongs to directory '+path)
            ok(len(rep[0].get('hasPart',[]))==r['parts'],'Report sections count '+path)
            for num,part in enumerate(rep[0]['hasPart'],start=1):
                ok(part.get('@id')==BASE+r['url']+str(num)+'/#section','Report hasPart section ID '+path)
                ok(part.get('isPartOf',{}).get('@id')==url+'#research','Report hasPart relationship '+path)
            webpages=[x for x in graph if x.get('@type')=='WebPage']
            ok(len(webpages)==1 and webpages[0].get('mainEntity',{}).get('@id')==url+'#research','Report WebPage mainEntity '+path)
            ok(og_type==['article'],'OG supplemental report landing '+path)
            counts['research']+=1
        elif len(s)==4 and s[0]=='research' and s[3].isdigit():
            report='/'+'/'.join(s[:3])+'/'
            r=rmap.get(report);ok(r is not None,'Research report exists '+path)
            n=int(s[3]);ok(1<=n<=r['parts'],'Research section bounds '+path)
            ent=[x for x in graph if x.get('@id')==url+'#section']
            ok(len(ent)==1 and ent[0].get('@type')=='CreativeWork','Section CreativeWork '+path)
            ok(ent[0].get('identifier')==r['id']+'/section-'+str(n),'Section identity '+path)
            ok(ent[0].get('isPartOf',{}).get('@id')==BASE+report+'#research','Section parent Report '+path)
            ok(ent[0].get('creativeWorkStatus')=='supplemental_research_unverified','Section supplemental status '+path)
            w=[x for x in graph if x.get('@type')=='WebPage']
            ok(len(w)==1 and w[0].get('mainEntity',{}).get('@id')==url+'#section','Section page mainEntity '+path)
            ok(og_type==['website'],'Section OG website '+path)
            counts['research_section']+=1
        else:counts['other']+=1
    ok(counts=={'print_page':1925,'book':14,'research_dir':1,'research':210,'research_section':1553,'other':5},'Exhaustive URL category coverage '+str(counts))
    for collection in ('Eviulon','Evulgare'):
        with urlopen(args.http.rstrip('/')+'/research/?collection='+collection,timeout=30) as response:
            ok(response.status==200,'Filter responds '+collection)
            page=Tags();page.feed(response.read().decode('utf8'))
        ok(page.canon==[BASE+'/research/'],'Filter canonicalized '+collection)
        ok(page.meta.get('robots')==['noindex,follow'],'Filter is noindex '+collection)
        graph=json.loads(page.schema[0])['@graph']
        ok(not any(n.get('@type')=='CollectionPage' for n in graph),'No falsely comprehensive list in filtered view '+collection)
    print(f'METADATA_HTTP_PASS {checked} assertions, {len(url_list)} canonical HTML URLs, two filtered Research views, {counts}',flush=True)

if __name__=='__main__':main()
