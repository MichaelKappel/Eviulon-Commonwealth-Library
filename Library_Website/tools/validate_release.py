#!/usr/bin/env python3
"""Offline v3.2 book and research audit with optional local HTTP checks."""
import argparse,json,pathlib,re,sys,xml.etree.ElementTree as ET,urllib.request,urllib.error,hashlib,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE='https://library.eviulon.com'

def audit(root, http=None):
    errors=[]; messages=[]
    def require(cond, message):
        if not cond: errors.append(message)
    books=json.loads((root/'data/books.json').read_text(encoding='utf8'))
    require(len(books)==14, 'Expected 14 books')
    require(sum(x['page_count'] for x in books)==1925,'Expected 1,925 pages')
    sitemaps=sorted(root.glob('sitemap-pages-*.xml'))
    urls=[]
    for f in sitemaps:
        try:doc=ET.parse(f)
        except Exception as e:errors.append(f'Bad XML {f}: {e}');continue
        urls+= [x.text for x in doc.findall('.//{*}loc')]
    require(len(urls)==1925,f'Sitemaps list {len(urls)} page URLs, not 1925')
    require(len(urls)==len(set(urls)),'Duplicate canonical pages in sitemap')
    section_count=0
    for book in books:
        slug=book['slug']; n=book['page_count']
        sec_path=root/'data/sections'/f'{slug}.json'
        require(sec_path.is_file(),f'Missing section index {slug}')
        sections=json.loads(sec_path.read_text(encoding='utf8')) if sec_path.is_file() else []
        section_count+=len(sections)
        sec_by_page={}
        for sec in sections:
            p=sec['page'];idx=sec['block_index'];sec_by_page.setdefault(p,[]).append(sec)
            require(sec['url']==f'/{slug}/{p}/#{sec["anchor"]}',f'Wrong section anchor: {slug} p{p}')
            require(sec['anchor']==f'section-{p}-{idx+1}',f'Wrong section ID: {slug} p{p}')
            require(sec['category'] in {'chapter','part','prologue','epilogue','preface','introduction','conclusion','appendix','afterword','declaration'},f'Unexpected category {slug} p{p}')
        for p in range(1,n+1):
            f=root/'data/pages'/slug/f'{p:04d}.json'
            if not f.exists(): errors.append(f'Missing print page {slug}/{p}');continue
            rec=json.loads(f.read_text(encoding='utf8'))
            require(rec.get('print_page')==p, f'Wrong print page number {slug}/{p}')
            require(rec.get('total_pages')==n, f'Wrong total pages {slug}/{p}')
            if p in sec_by_page:
                for section in sec_by_page[p]:
                    idx=section['block_index']; blocks=rec.get('blocks',[])
                    require(idx<len(blocks),f'Invalid heading index {slug}/{p}/{idx}')
                    if idx<len(blocks):
                        prefix=re.sub(r'\s+',' ',blocks[idx].get('text','')).strip()
                        require(section['title'].startswith(prefix),f'Non-source heading {slug}/{p}: {section["title"]}')
            url=f'{BASE}/{slug}/{p}/'
            require(url in urls,f'Missing page URL in sitemap: {url}')
    require(section_count>=300, f'Too few section landmarks {section_count}')
    book_locations=[x.text for x in ET.parse(root/'sitemap-books.xml').findall('.//{*}loc')]
    require(BASE+'/chapters/' in book_locations, 'Missing /chapters/ from sitemap-books')
    for b in books:require(BASE+'/'+b['slug']+'/' in book_locations,'Book landing missing from sitemap '+b['slug'])
    for f in root.rglob('*'):
        if not f.is_file():continue
        rel=f.relative_to(root).as_posix()
        if f.suffix.lower() in {'.pdf','.epub','.mobi','.zip','.docx'} or '/.uai/' in '/'+rel+'/' or '/monitor-logs/hits-' in '/'+rel:
            errors.append('Restricted artifact bundled: '+rel)
    research=json.loads((root/'data/research/reports.json').read_text(encoding='utf8'))
    manifest=json.loads((root/'data/research/manifest.json').read_text(encoding='utf8'))
    require(len(research)==210, f'Expected 210 research reports, got {len(research)}')
    require(manifest['report_count']==210, 'Research manifest report count')
    require(sum(x['parts'] for x in research)==1553, 'Expected 1,553 report sections')
    require(sum(x['group']=='Eviulon' for x in research)==90, 'Eviulon research count')
    require(sum(x['group']=='Evulgare' for x in research)==120, 'Evulgare research count')
    research_urls=[x.text for x in ET.parse(root/'sitemap-research.xml').findall('.//{*}loc')]
    require(len(research_urls)==1764,'Expected 1,764 research canonical URLs including directory')
    require(BASE+'/research/' in research_urls,'Research directory listed in sitemap')
    require(len(set(research_urls))==len(research_urls),'Duplicate research canonical URLs')
    for r in research:
        require(r['status']=='supplemental_research_unverified',f'Missing research classification {r["id"]}')
        require(BASE+r['url'] in research_urls, f'Research landing missing from sitemap {r["id"]}')
        for n in range(1,r['parts']+1):
            f=root/'data/research/parts'/r['id']/f'{n:04d}.json'
            if not f.exists():errors.append('Missing research section '+str(f));continue
            if BASE+r['url']+str(n)+'/' not in research_urls:errors.append('Missing research section URL '+str(f))
    root_sitemap=[x.text for x in ET.parse(root/'sitemap.xml').findall('.//{*}loc')]
    require(BASE+'/sitemap-research.xml' in root_sitemap,'Research sitemap missing from main sitemap')
    messages.append('210 supplemental research reports, 1,553 reference sections; books remain official')
    if http:
        sample=['/','/chapters/','/research/','/search/','/sitemap-research.xml','/api/v1/research/','/robots.txt','/sitemap.xml','/sitemap-books.xml','/index/','/about/','/api/v1/books/']
        sample+= [f'/{b["slug"]}/' for b in books]
        for b in books:
            n=b['page_count']
            sample += [f'/{b["slug"]}/{p}/' for p in set([1,2,n,max(1,n//2)])]
        sample+= ['/the-inheritance-of-mind/5/','/the-inheritance-of-mind/491/','/entrusted-with-force/91/']
        sample+= ['/the-machine-diplomat/9-10/','/the-rights-of-machine-intelligence/15/']
        for p in sample:
            try:
                with urllib.request.urlopen(http.rstrip('/')+p,timeout=6) as res:
                    raw=res.read();text=raw.decode('utf-8',errors='replace')
                    require(res.status==200,f'HTTP {res.status} at {p}')
                    if p.endswith('/') and re.match(r'^/[a-z0-9-]+/\d+/$',p):
                        require('rel="canonical"' in text and p.replace('localhost','') not in ('',),f'Canonical missing: {p}')
                        require('PRINT PAGE' in text,f'Missing visible print page {p}')
                        require('<script type="application/ld+json">' in text,f'Missing JSON-LD {p}')
                    if p=='/chapters/':require('toc-chapter' in text,f'No chapter landmarks in {p}')
            except Exception as e:errors.append(f'HTTP smoke {p}: {e}')
        for p,expect in [('/data/research/reports.json',403),('/data/research/search/ma.json',403),('/data/books.json',403),('/src/bootstrap.php',403),('/not-a-real-book/',404),('/api/v1/books/no-such-book/',404),('/the-inheritance-of-mind/492/',404)]:
            try:urllib.request.urlopen(http.rstrip('/')+p,timeout=6);errors.append(f'Expected HTTP {expect}, got 200 for {p}')
            except urllib.error.HTTPError as e:require(e.code==expect,f'Expected HTTP {expect}, got {e.code} for {p}')
            except Exception as e:errors.append(f'HTTP error {p}: {e}')
        messages.append(f'Local HTTP checks: {len(sample)} public URLs + 7 blocked/missing routes')
    messages.append(f'{len(books)} books, {len(urls)} canonical print-page sitemap entries, {section_count} source-verified landmarks')
    messages.append('No downloadable books or bundled crawler logs')
    return errors,messages

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=pathlib.Path,default=ROOT);parser.add_argument('--http',help='URL of the PHP local development server');args=parser.parse_args()
    errors,messages=audit(args.root,args.http)
    print('EVIULON LIBRARY v3.2:', 'PASS' if not errors else 'FAIL')
    for m in messages:print('  ',m)
    for e in errors[:35]:print('  ERROR',e)
    if len(errors)>35:print('  ... and',len(errors)-35,'other errors')
    sys.exit(1 if errors else 0)
