#!/usr/bin/env python3
"""Build/audit exactly source-rendered public book/research reading HTML snapshots.

No paraphrase or source modification. Never mirror html-cache/ into public GitHub.
--check validates complete hashes/dependency digest + deterministic dynamic byte parity
for 32 source-grounded samples. --write builds ALL 3,702 canonical reading URLs.
"""
from __future__ import annotations
import argparse,hashlib,json,os,pathlib,subprocess,sys
from concurrent.futures import ThreadPoolExecutor
ROOT=pathlib.Path(__file__).resolve().parents[1]
CACHE=ROOT/'html-cache'; MANIFEST=CACHE/'manifest.json'; CHECKPOINT=CACHE/'.render-checkpoint.json'
BASE='https://library.eviulon.com'
def sha(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def routes():
    books=json.loads((ROOT/'data/books.json').read_text())
    research=json.loads((ROOT/'data/research/reports.json').read_text())
    out={}
    for b in books:
        slug=b['slug']
        out[f'/{slug}/']=f'books/{slug}/landing.html'
        for n in range(1,b['page_count']+1):out[f'/{slug}/{n}/']=f'books/{slug}/{n}.html'
    for r in research:
        group=r['group'].lower();slug=r['slug']
        base=f'/research/{group}/{slug}/'; target=f'research/{group}/{slug}'
        out[base]=target+'/landing.html'
        for n in range(1,r['parts']+1):out[f'{base}{n}/']=f'{target}/{n}.html'
    assert len(out)==3702,(len(out),sum(b['page_count'] for b in books),sum(r['parts'] for r in research))
    return dict(sorted(out.items()))
def dependencies():
    """Hash every input influencing rendered HTML, not output or runtime logs."""
    include=[ROOT/'index.php',ROOT/'router.php',ROOT/'RELEASE_ID.txt',ROOT/'VERSION.json',ROOT/'tools/build_static_html.py']
    include+=list((ROOT/'src').rglob('*.php'))
    include+=list((ROOT/'data').rglob('*'))
    files=sorted((p for p in include if p.is_file()),key=lambda x:x.relative_to(ROOT).as_posix())
    return sha(b''.join((p.relative_to(ROOT).as_posix()+'\0'+sha(p.read_bytes())+'\n').encode() for p in files))
def render(route):
    env=os.environ.copy();env.update({'REQUEST_METHOD':'GET','REQUEST_URI':route,'QUERY_STRING':'','EVIULON_MONITOR_ENABLED':'0'})
    res=subprocess.run(['php','index.php'],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=25)
    if res.returncode or res.stderr:
        raise ValueError(f'PHP render failure {route}: return {res.returncode} stderr={res.stderr[:350]!r}')
    body=res.stdout
    if not body.startswith(b'<!doctype html>') or b'<script type="application/ld+json">' not in body or b'<main' not in body:
        raise ValueError('Not a complete canonical HTML page '+route)
    if f'<link rel="canonical" href="{BASE}{route}">'.encode() not in body:
        raise ValueError('Wrong canonical URL in '+route)
    if route.startswith('/research/') and b'Not official doctrine' not in body and b'not approved' not in body.lower():
        raise ValueError('Research authority disclaimer not present '+route)
    return body
def atomic_json(path, object):
    """A killed generator must never leave a truncated manifest or checkpoint."""
    temp = path.with_name(path.name+'.pending')
    temp.write_text(json.dumps(object,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    os.replace(temp,path)


def previously_verified_rows(current_digest):
    """Never trust mtimes. Reuse only snapshots recorded for these exact input bytes.

    A complete manifest from the previous run or a crash-resumable checkpoint
    authorizes reuse only when its whole-input content digest matches. Each
    individual page must also match its recorded SHA-256 and byte length.
    """
    rows={}
    for manifest in (MANIFEST,CHECKPOINT):
        if not manifest.is_file():continue
        try:
            candidate=json.loads(manifest.read_text(encoding='utf-8'))
            if candidate.get('dependency_sha256')!=current_digest:continue
            for row in candidate.get('snapshots',[]):
                if all(k in row for k in ('url','relative_path','sha256','bytes')):
                    rows[row['url']]=row
        except (ValueError,KeyError,TypeError):
            continue  # Corrupt/partial checkpoint cannot authorize reuse.
    return rows


def safe_to_reuse(row, route, relative):
    if not row or row['url']!=route or row['relative_path']!='html-cache/'+relative:
        return False
    path=CACHE/relative
    if not path.is_file() or not path.resolve().is_relative_to(CACHE.resolve()):
        return False
    body=path.read_bytes()
    if len(body)!=row['bytes'] or sha(body)!=row['sha256']:
        return False
    # Prevent reusing an invalid object even if it matches the old manifest.
    return (body.startswith(b'<!doctype html>')
            and b'<script type="application/ld+json">' in body
            and b'<main' in body
            and f'<link rel="canonical" href="{BASE}{route}">'.encode() in body)


def build():
    out=routes()
    start_digest=dependencies()
    previous=previously_verified_rows(start_digest)
    records=[]; reused=0; rendered=0
    CACHE.mkdir(parents=True,exist_ok=True)
    # The checkpoint starts with the CURRENT digest; when source bytes change,
    # even with preserved timestamps, old cache entries cannot be trusted.
    def checkpoint():
        atomic_json(CHECKPOINT,{'kind':'incomplete_static_html_build',
                  'dependency_sha256':start_digest,'snapshots':records})
    checkpoint()
    def one(item):
        route,relative=item;dest=CACHE/relative
        old=previous.get(route)
        if safe_to_reuse(old,route,relative):
            body=dest.read_bytes();did_reuse=True
        else:
            body=render(route);did_reuse=False
            dest.parent.mkdir(parents=True,exist_ok=True)
            tmp=dest.with_name(dest.name+'.pending')
            tmp.write_bytes(body);os.replace(tmp,dest)
        return ({'url':route,'relative_path':'html-cache/'+relative,
                 'bytes':len(body),'sha256':sha(body),
                 'kind':'supplemental_research_html' if route.startswith('/research/') else 'official_book_html'},did_reuse)
    with ThreadPoolExecutor(max_workers=8) as pool:
        for i,(row,was_reused) in enumerate(pool.map(one,out.items()),1):
            records.append(row)
            if was_reused:reused+=1
            else:rendered+=1
            if i%80==0:checkpoint()
            if i%400==0:print('PREBUILT_HTML',i,'/',len(out),'reused',reused,'rendered',rendered,flush=True)
    # Data or code changed mid-build => DO NOT publish a mixed-source manifest.
    if dependencies()!=start_digest:
        raise ValueError('Render dependencies changed during build; retry with a clean content digest')
    if len(records)!=len(out):raise ValueError('Incomplete static reading HTML corpus')
    result={'release_id':(ROOT/'RELEASE_ID.txt').read_text().strip(),
       'kind':'source_rendered_canonical_html_snapshot_manifest','total':len(records),
       'counts':{'official_book_html':1939,'supplemental_research_html':1763},
       'dependency_sha256':start_digest,
       'cache_integrity':{'reuse_requires_dependency_sha256_and_per_snapshot_sha256':True,
                          'interrupted_builds_resume_from_verified_checkpoint':True,
                          'mtime_heuristic_used':False},
       'guardrails':{'public_html_contains_only_text_already_available_at_canonical_html_urls':True,
         'direct_html_cache_urls_denied':True,'raw_source_manuscripts_in_github':False,
         'only_no_query_get_head_static':True},'snapshots':records}
    atomic_json(MANIFEST,result)
    CHECKPOINT.unlink(missing_ok=True)
    print('HTML_BUILD_COMPLETED',len(records),'reused',reused,'rendered',rendered,flush=True)
    return result

def check():
    if not MANIFEST.is_file():raise ValueError('Missing rendered HTML manifest')
    if CHECKPOINT.exists():raise ValueError('Interrupted HTML render checkpoint remains; finish --write before release')
    m=json.loads(MANIFEST.read_text());expected=routes()
    if m['release_id']!=(ROOT/'RELEASE_ID.txt').read_text().strip():raise ValueError('Stale release id')
    if m['total']!=3702 or len(m['snapshots'])!=3702:raise ValueError('Wrong snapshot count')
    if m['dependency_sha256']!=dependencies():raise ValueError('Source/runtime changed since rendering; rebuild static HTML')
    if not m.get('cache_integrity',{}).get('reuse_requires_dependency_sha256_and_per_snapshot_sha256'):
        raise ValueError('Missing content-hash-based build safety record')
    seen=set();kinds={}
    for row in m['snapshots']:
        url=row['url'];relative=row['relative_path'];p=ROOT/relative
        if url not in expected or 'html-cache/'+expected[url]!=relative or url in seen:raise ValueError('Unexpected cache entry '+url)
        seen.add(url); data=p.read_bytes()
        if row['sha256']!=sha(data) or row['bytes']!=len(data):raise ValueError('Hash/size mismatch for '+url)
        kinds[row['kind']]=kinds.get(row['kind'],0)+1
    if kinds!={'official_book_html':1939,'supplemental_research_html':1763}:raise ValueError(str(kinds))
    # Deterministic spread across every book and both research collections.
    urls=sorted(expected); samples=urls[::max(1,len(urls)//35)]
    book_pages=[u for u in urls if u.startswith('/citizens-guide-to-eviulon/')];samples+=book_pages[:2]
    samples+=['/the-inheritance-of-mind/491/','/entrusted-with-force/91/']
    for url in sorted(set(samples)):
        if sha(render(url))!=sha((CACHE/expected[url]).read_bytes()):raise ValueError('Dynamic rendering mismatch '+url)
    print('PASS: 3702 immutable source-grounded canonical HTML snapshots; 1939 book and 1763 research; dynamic parity samples',len(set(samples)))
if __name__=='__main__':
    p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true');args=p.parse_args()
    if args.write:
        m=build();print('BUILT_HTML',m['total'],m['counts'])
        # verify output tree and render dependency determinism
        check()
    else:check()
