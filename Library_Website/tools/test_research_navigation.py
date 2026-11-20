#!/usr/bin/env python3
"""Deterministic HTTP acceptance for human/non-JavaScript supplemental discovery."""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.stack = []
        self.nav_links = []
        self.current_link = None
        self.nav_name = None
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'nav':
            self.stack.append(self.nav_name)
            self.nav_name = a.get('aria-label')
        if tag == 'a':
            self.links.append((a.get('href',''),a))
            if self.nav_name:
                self.nav_links.append((self.nav_name,a.get('href',''),a))
    def handle_endtag(self, tag):
        if tag == 'nav' and self.stack:
            self.nav_name = self.stack.pop()

def get(base, path, method='GET'):
    with urlopen(Request(base.rstrip('/')+path, method=method, headers={'User-Agent':'Eviulon-local-navigation-test/1.0'}),timeout=20) as resp:
        data=resp.read().decode('utf-8','replace')
        assert resp.status == 200, (path,resp.status)
        assert 'text/html' in resp.headers.get('Content-Type',''), (path, resp.headers)
        return data

def links(html):
    parser=Links(); parser.feed(html); return parser

def main():
    p=argparse.ArgumentParser(); p.add_argument('--http',required=True);p.add_argument('--root',default=str(Path(__file__).resolve().parents[1])); a=p.parse_args()
    version=json.loads((Path(a.root)/'VERSION.json').read_text())['site_version']
    records=json.loads((Path(a.root)/'data/research/reports.json').read_text())
    groups={group:[record for record in records if record['group']==group] for group in ('Eviulon','Evulgare')}
    assert len(records)==210 and len(groups['Eviulon'])==90 and len(groups['Evulgare'])==120
    checks=0
    def ok(cond,msg):
        nonlocal checks
        assert cond,msg
        checks+=1

    for path in ('/','/about/','/index/','/chapters/','/search/','/research/',records[0]['url'], '/research/eviulon/'+groups['Eviulon'][0]['url'].split('/')[3]+'/1/'):
        page=get(a.http,path)
        parser=links(page)
        ok(any(nav=='Main navigation' and href=='/research/' for nav,href,_ in parser.nav_links),f'Research missing from persistent nav: {path}')
        ok(f'href="/assets/style.css?v={version}"' in page,f'Cache-busting stylesheet missing for v{version}: {path}')
        ok('href="/"' in page,f'Books lost: {path}')

    home=get(a.http,'/')
    ok(home.index('id="the-books"')<home.index('class="shell supplemental-discovery"'),'Research placed above official Books')
    ok('href="/research/"' in home,'No research entry point from home')
    ok('href="/research/?collection=Eviulon"' in home,'Missing Eviulon browse link')
    ok('href="/research/?collection=Evulgare"' in home,'Missing Evulgare browse link')
    ok('not approved Eviulon doctrine' in home,'Authority disclaimer missing on home')
    for title,count in (('Eviulon',90),('Evulgare',120)):
        ok(f'{count} reports' in home,f'Missing {title} report count')

    all_dir=get(a.http,'/research/'); lp=links(all_dir)
    expected={r['url'] for r in records}
    actual={href for href,attr in lp.links if href in expected}
    ok(actual==expected,f'Directory has {len(actual)} of {len(expected)} report landing links: {list(expected-actual)[:3]}')
    ok('Browse <strong>210 public reports</strong>' in all_dir,'Missing exact catalog total')
    ok('Research disclaimer:' in all_dir,'Directory disclaimer missing')
    ok(len([u for nav,u,attrs in lp.nav_links if nav=='Browse research collections'])==3,'Collection tabs not present')
    for group in ('Eviulon','Evulgare'):
        filtered=get(a.http,'/research/?collection='+quote(group))
        p=links(filtered)
        present={href for href,attr in p.links if href in expected}
        wanted={r['url'] for r in groups[group]}
        ok(present==wanted,f'Category {group} has {len(present)} of {len(wanted)} report links')
        ok(any(nav=='Browse research collections' and href=='/research/?collection='+group and attrs.get('aria-current')=='page' for nav,href,attrs in p.nav_links),f'Category state is not marked for screen readers: {group}')
        ok('not approved Eviulon doctrine' in filtered or 'not approved Eviulon doctrine' in all_dir,'Supplemental disclaimer missing')
    for report in (groups['Eviulon'][0],groups['Eviulon'][-1],groups['Evulgare'][0],groups['Evulgare'][-1]):
        page=get(a.http,report['url'])
        ok('href="/research/"' in page,f'Missing directory return path: {report["url"]}')
        ok('Research disclaimer:' in page,f'No report disclaimer: {report["url"]}')
        ok('href="'+report['url']+'1/"' in page,f'Missing first section link: {report["url"]}')
    for report in records:
        # HTTP HEAD confirms that each link found in the directory resolves
        # without downloading 210 full report landing pages.
        get(a.http,report['url'],'HEAD')
        checks+=1
    print(f'PASS: {checks} navigation, category, canonical-link, authority and HTTP assertions; all 210 report links resolve')

if __name__=='__main__':main()
