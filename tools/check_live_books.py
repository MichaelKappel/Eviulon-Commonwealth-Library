#!/usr/bin/env python3
"""Optional live HTTP check (requires internet), without downloading full-page content."""
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parent.parent
books=json.loads((root/'Library_Source/metadata/books.json').read_text())['books']
urls=[('home','https://library.eviulon.com/'),('sitemap','https://library.eviulon.com/sitemap.xml')]
for b in books:
    urls += [(f"{b['number']:02d} book",b['canonical_book_url']),
             (f"{b['number']:02d} first page",b['canonical_first_page_url']),
             (f"{b['number']:02d} final page",b['canonical_last_page_url'])]
failed=0
for label,url in urls:
    try:
        with urlopen(Request(url,headers={'User-Agent':'EviulonPublicRepoQA/1.0 (+https://library.eviulon.com/)','Accept':'text/html,application/xml'}),timeout=15) as r:
            code=r.status; final=r.url
    except HTTPError as e:code=e.code;final=url
    except URLError as e:code='NETWORK ERROR';final=str(e)
    ok=code==200
    print(f"{'OK' if ok else 'FAIL':4} {label:18} {code} {url} {final if final!=url else ''}")
    if not ok: failed+=1
print(f"Total {len(urls)} URLs; {failed} failed")
sys.exit(1 if failed else 0)
