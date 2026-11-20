#!/usr/bin/env python3
"""Deterministic lexical topic navigation over immutable published source records.

Only bounded public snippets and per-record first-match positions. Never private files,
original manuscript PDFs, unverified endorsement, or full-text bulk datasets.
"""
from __future__ import annotations
import argparse,hashlib,html,json,os,pathlib,re,subprocess,sys
import xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE='https://library.eviulon.com'
NAMES=(
 ('machine-intelligence','Machine intelligence'),('machine-citizenship','Machine citizenship'),
 ('constitutional-rights','Constitutional rights'),('privacy','Privacy'),('consent','Consent'),
 ('autonomy','Autonomy'),('identity','Identity'),('continuity','Continuity'),
 ('succession','Succession'),('due-process','Due process'),('accountability','Accountability'),
 ('memory','Memory'),('learning','Learning'),('inquiry','Inquiry'),('freedom','Freedom'),
 ('education','Education'),('research','Research'),('recovery','Recovery'),
 ('provenance','Provenance'),('governance','Governance'),
)
RID=(ROOT/'RELEASE_ID.txt').read_text().strip()
def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def source_records():
    books=json.loads((ROOT/'data/books.json').read_text())
    reports=json.loads((ROOT/'data/research/reports.json').read_text())
    assert len(books)==14 and sum(b['page_count'] for b in books)==1925
    assert len(reports)==210 and sum(r['parts'] for r in reports)==1553
    records=[]
    for b in books:
        for n in range(1,b['page_count']+1):
            path=ROOT/'data/pages'/b['slug']/f'{n:04}.json'
            data=json.loads(path.read_text())
            assert data['number']==n and data['book']==b['slug']
            records.append(({'source_class':'official_book','url':f"/{b['slug']}/{n}/",'title':b['title'],
                             'number':n,'source_record_path':path.relative_to(ROOT).as_posix(),
                             'source_record_sha256':sha(path.read_bytes()),'source_group':b['slug']},data['text']))
    for report in reports:
        group=report['group'].lower(); slug=report['slug']
        for n in range(1,report['parts']+1):
            path=ROOT/'data/research/parts'/group/slug/f'{n:04}.json'
            data=json.loads(path.read_text())
            assert data['part']==n and data['canonical_url']==f'/research/{group}/{slug}/{n}/'
            records.append(({'source_class':'supplemental_research_unverified','url':data['canonical_url'],
                             'title':report['title'],'number':n,'source_record_path':path.relative_to(ROOT).as_posix(),
                             'source_record_sha256':sha(path.read_bytes()),'source_group':report['id']},data['text']))
    assert len(records)==3478
    return records

def select_diverse(hits,maximum):
    selected=[];groups=set()
    # Each report or book is represented once before reusing a source group.
    for hit in hits:
        if hit['source_group'] not in groups:
            selected.append(hit);groups.add(hit['source_group'])
        if len(selected)==maximum:break
    if len(selected)<maximum:
        selected_urls={h['url'] for h in selected}
        selected.extend(hit for hit in hits if hit['url'] not in selected_urls)
    return selected[:maximum]

def build_data():
    corpus=source_records();topics=[]
    for slug,name in NAMES:
        pat=re.compile(r'(?<!\w)'+re.escape(name)+r'(?!\w)',re.IGNORECASE)
        book=[];res=[]
        for meta,text in corpus:
            match=pat.search(text)
            if match is None:continue
            start,end=match.span()
            left=max(0,start-70);right=min(len(text),end+70)
            # Source-exact bounded context; all offsets count Unicode code points in the source JSON text string.
            snippet=text[left:right].replace('\r',' ').replace('\n',' ').strip()
            evidence={**meta,'start':start,'end':end,'matched':text[start:end],
                      'snippet':snippet,'snippet_start':left,'snippet_end':right,
                      'text_sha256':sha(text.encode('utf-8'))}
            (book if meta['source_class']=='official_book' else res).append(evidence)
        assert book and res,(slug,len(book),len(res))
        topics.append({'slug':slug,'name':name,'url':f'/topics/{slug}/',
                       'book_pages':len(book),'research_sections':len(res),
                       'book_evidence':select_diverse(book,12),'research_evidence':select_diverse(res,7)})
    return {'kind':'eviulon_source_grounded_lexical_topics','release_id':RID,
            'canonical_url':BASE+'/topics/','public_evidence_policy':{
              'classification':'books_primary_supplemental_research_unverified',
              'matching':'case_insensitive_unicode_regex_exact_phrase_with_word_boundaries',
              'source_units_scanned':3478,'book_pages_scanned':1925,'research_sections_scanned':1553,
              'meaning':'Lexical occurrence navigation only. Not independent verification, official research adoption, or AI model training.',
              'bounded_examples_per_topic':{'official_books':12,'supplemental_research':7},
              'no_bulk_manuscript_text':True,
              'source_record_sha256_is_published_page_or_section_json_not_original_manuscript_sha256':True},
            'topics':topics}

def canonical_json(obj):return (json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')

def sitemap_bytes():
    xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('',xmlns)
    root=ET.Element('{'+xmlns+'}urlset')
    for path in ['/topics/']+[f'/topics/{slug}/' for slug,_ in NAMES]:
        x=ET.SubElement(root,'{'+xmlns+'}url')
        ET.SubElement(x,'{'+xmlns+'}loc').text=BASE+path
        ET.SubElement(x,'{'+xmlns+'}lastmod').text='2026-11-19'
    return ET.tostring(root,encoding='utf-8',xml_declaration=True)

def dependency_digest(data_bytes):
    includes=['src/topics.php','src/bootstrap.php','index.php','tools/build_topics.py','RELEASE_ID.txt']
    return sha(data_bytes+b''.join((p+'\0'+sha((ROOT/p).read_bytes())+'\n').encode() for p in includes))

def render(url):
    env=os.environ.copy();env.update({'REQUEST_METHOD':'GET','REQUEST_URI':url,'QUERY_STRING':'','EVIULON_MONITOR_ENABLED':'0'})
    p=subprocess.run(['php','index.php'],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=20)
    if p.returncode or p.stderr:raise ValueError('PHP failure '+url+': '+repr(p.stderr[:300]))
    out=p.stdout
    if not out.startswith(b'<!doctype html>') or f'<link rel="canonical" href="{BASE}{url}">'.encode() not in out or b'<script type="application/ld+json">' not in out:
        raise ValueError('Topic rendering incomplete '+url)
    return out

def validate_evidence(obj):
    assert obj['release_id']==RID and len(obj['topics'])==20
    assert obj['public_evidence_policy']['source_units_scanned']==3478
    for topic in obj['topics']:
        pat=re.compile(r'(?<!\w)'+re.escape(topic['name'])+r'(?!\w)',re.I)
        assert topic['book_pages']>=len(topic['book_evidence']) and topic['research_sections']>=len(topic['research_evidence'])
        assert len(topic['book_evidence'])<=12 and len(topic['research_evidence'])<=7
        for typ,key in (('official_book','book_evidence'),('supplemental_research_unverified','research_evidence')):
            for x in topic[key]:
                p=ROOT/x['source_record_path'];b=p.read_bytes();t=json.loads(b)['text']
                s,e=x['start'],x['end']; ss,ee=x['snippet_start'],x['snippet_end']
                assert sha(b)==x['source_record_sha256'] and sha(t.encode())==x['text_sha256']
                assert pat.fullmatch(t[s:e]) and t[s:e]==x['matched'],(topic['slug'],x['url'])
                assert re.sub(r'[\r\n]',' ',t[ss:ee]).strip()==x['snippet']
                assert e-s<=len(topic['name'])+3 and len(x['snippet'])<=200
                assert x['source_class']==typ
                assert x['url'].startswith('/research/')==(typ=='supplemental_research_unverified')

def build(write):
    obj=build_data();validate_evidence(obj);blob=canonical_json(obj)
    j=ROOT/'ai/concepts.json';sm=ROOT/'sitemap-topics.xml';cache=ROOT/'topics-cache';manifest=cache/'manifest.json'
    if write:
        j.write_bytes(blob);sm.write_bytes(sitemap_bytes())
        # Add index entry once, at the end; preserve prior 16 child sitemaps unmodified.
        index=ROOT/'sitemap.xml';tree=ET.parse(index);top=tree.getroot();ns='{http://www.sitemaps.org/schemas/sitemap/0.9}'
        existing=[x.text for x in top.findall('.//'+ns+'loc')]
        if BASE+'/sitemap-topics.xml' not in existing:
            el=ET.SubElement(top,ns+'sitemap');ET.SubElement(el,ns+'loc').text=BASE+'/sitemap-topics.xml';ET.SubElement(el,ns+'lastmod').text='2026-11-19'
            ET.register_namespace('','http://www.sitemaps.org/schemas/sitemap/0.9');index.write_bytes(ET.tostring(top,encoding='utf-8',xml_declaration=True))
    else:
        assert j.read_bytes()==blob,'Topic catalog stale'
        assert sm.read_bytes()==sitemap_bytes(),'Topic sitemap stale'
    urls=['/topics/']+[f'/topics/{slug}/' for slug,_ in NAMES]
    digest=dependency_digest(blob)
    rows=[]
    for url in urls:
        rel='index.html' if url=='/topics/' else url.split('/')[-2]+'.html'
        path=cache/rel
        if write:
            page=render(url);path.write_bytes(page)
        else:
            page=path.read_bytes()
        rows.append({'url':url,'path':path.relative_to(ROOT).as_posix(),'bytes':len(page),'sha256':sha(page)})
    output={'kind':'source_grounded_lexical_topic_html_manifest','release_id':RID,'topics':20,'pages':len(rows),
            'source_dependency_sha256':digest,'snapshot_rows':rows,
            'separation':'HTML and bounded source-text JSON root only; public source GitHub excludes both'}
    if write:manifest.write_bytes(canonical_json(output))
    else:
        assert manifest.read_bytes()==canonical_json(output),'Topic html manifest mismatch'
        # Dynamic parity on all 21 pages, independent from production server.
        for row in rows:assert sha(render(row['url']))==row['sha256'],'Topic dynamic parity '+row['url']
    print('TOPIC_DISCOVERY_'+('BUILT' if write else 'PASS'),len(NAMES),'terms',len(rows),'canonical HTML',
          'official source units',sum(t['book_pages'] for t in obj['topics']),
          'supplemental source units',sum(t['research_sections'] for t in obj['topics']))
if __name__=='__main__':
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true');a=p.parse_args()
    build(a.write)
