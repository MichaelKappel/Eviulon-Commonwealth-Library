#!/usr/bin/env python3
"""Prepare IndexNow notifications from canonical sitemaps (offline by default).

Enterprise safety invariants:
  * No outbound HTTP without explicit --submit.
  * Books-only is the default. Research opt-in is explicit.
  * URL input is checked against canonical sitemap entries and site origin.
  * No IndexNow key is provided in the release; owner provisions one separately.
  * This tool does not claim acceptance, indexing or ranking improvement.

Examples:
  python3 tools/indexnow_prepare.py
  python3 tools/indexnow_prepare.py --changed changed_urls.txt
  python3 tools/indexnow_prepare.py --source all --include-research
  python3 tools/indexnow_prepare.py --submit --key-file ./indexnow-key.txt --key-location https://library.eviulon.com/KEY.txt
"""
from __future__ import annotations
import argparse, json, pathlib, re, sys, urllib.parse, urllib.request, urllib.error, xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[1]
ORIGIN='https://library.eviulon.com'
ENDPOINT='https://api.indexnow.org/indexnow'

def sitemap_locs(path: pathlib.Path)->list[str]:
    return [str(x.text or '').strip() for x in ET.parse(path).findall('.//{*}loc')]

def canonical_set(root: pathlib.Path,include_research:bool)->tuple[list[str],set[str]]:
    preferred=sitemap_locs(root/'sitemap-books.xml')
    # The site index is authoritative: never send invented locations.
    all_urls=list(preferred)
    for f in sorted(root.glob('sitemap-pages-*.xml')):all_urls.extend(sitemap_locs(f))
    if include_research:
        all_urls.extend(sitemap_locs(root/'sitemap-research.xml'))
        # Non-book supplemental discovery topics are opt-in, like research.
        all_urls.extend(sitemap_locs(root/'sitemap-topics.xml'))
    canonical=set(all_urls)
    if len(canonical)!=len(all_urls):raise ValueError('Duplicate canonical sitemap URLs')
    for url in canonical:
        parsed=urllib.parse.urlsplit(url)
        if parsed.scheme!='https' or parsed.netloc!='library.eviulon.com' or parsed.query or parsed.fragment:
            raise ValueError('Noncanonical origin or URL: '+url)
    return preferred,canonical

def urls_to_publish(root:pathlib.Path,source:str,include_research:bool,changed:pathlib.Path|None)->list[str]:
    preferred,allowed=canonical_set(root,include_research)
    if source=='books':candidate=preferred
    elif source=='book-pages':
        candidate=preferred+sorted(x for x in allowed if x not in preferred and not '/research/' in x)
    else:
        if not include_research:raise ValueError('--source all requires --include-research to avoid publishing research unintentionally')
        candidate=preferred+sorted(allowed.difference(preferred))
    if changed is not None:
        selected=[s.strip() for s in changed.read_text(encoding='utf-8').splitlines() if s.strip() and not s.lstrip().startswith('#')]
        if len(selected)!=len(set(selected)):raise ValueError('Duplicate URL in changed-file')
        missing=[x for x in selected if x not in allowed]
        if missing:raise ValueError('Changed URL absent from canonical sitemap: '+missing[0])
        candidate=[x for x in candidate if x in set(selected)]
    return candidate

def main(argv:list[str]|None=None)->int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=pathlib.Path,default=ROOT)
    ap.add_argument('--source',choices=['books','book-pages','all'],default='books')
    ap.add_argument('--include-research',action='store_true')
    ap.add_argument('--changed',type=pathlib.Path,help='Explicit changed canonical URLs, one per line')
    ap.add_argument('--submit',action='store_true',help='EXPLICIT OPT-IN: make an outbound HTTPS POST')
    ap.add_argument('--key-file',type=pathlib.Path,help='Owner-maintained local key file, not bundled')
    ap.add_argument('--key-location',help='Already deployed public validation URL on library.eviulon.com')
    args=ap.parse_args(argv)
    try:urls=urls_to_publish(args.root,args.source,args.include_research,args.changed)
    except (ValueError,OSError,ET.ParseError) as e:ap.error(str(e))
    if not urls:ap.error('No URLs to submit; recheck changed file')
    if len(urls)>10000:ap.error('IndexNow maximum of 10,000 URLs per request exceeded')
    output={'mode':'submission' if args.submit else 'dry-run','host':'library.eviulon.com', 'selection':args.source,
            'research_included':any('/research/' in x for x in urls), 'url_count':len(urls),
            'urls':urls, 'note':'IndexNow notification is not evidence of indexing or ranking.'}
    if not args.submit:
        print(json.dumps(output,indent=2,ensure_ascii=False))
        return 0
    if args.key_file is None or not args.key_file.is_file():ap.error('--submit requires a separately provided --key-file')
    key=args.key_file.read_text(encoding='ascii').strip()
    if not re.fullmatch(r'[A-Za-z0-9-]{8,128}',key):ap.error('Invalid key contents; use the official IndexNow key format')
    if not args.key_location:ap.error('--submit requires --key-location pointing to the deployed verification file')
    u=urllib.parse.urlsplit(args.key_location)
    if u.scheme!='https' or u.netloc!='library.eviulon.com' or not u.path.endswith('/'+key+'.txt') or u.query or u.fragment:
        ap.error('--key-location must be an HTTPS URL to a same-host {key}.txt validation file')
    request_data=json.dumps({'host':'library.eviulon.com','key':key,'keyLocation':args.key_location,'urlList':urls}).encode('utf8')
    request=urllib.request.Request(ENDPOINT,data=request_data,headers={'Content-Type':'application/json; charset=utf-8','User-Agent':'Eviulon-IndexNowPublisher/1.0'},method='POST')
    try:
        with urllib.request.urlopen(request,timeout=12) as response:
            status=response.status
    except urllib.error.HTTPError as ex:status=ex.code
    except (urllib.error.URLError,TimeoutError) as ex:
        print('ERROR: Transport failed; no indexing acceptance can be inferred:',ex,file=sys.stderr)
        return 1
    # Do not print the API key or a full request payload.
    print(json.dumps({'status':status,'url_count':len(urls),'success':status in (200,202),
        'note':'HTTP acceptance confirms notification, not search indexing.'}))
    return 0 if status in (200,202) else 1

if __name__=='__main__':raise SystemExit(main())
