#!/usr/bin/env python3
"""Produce/check the release's metadata-only local discovery attestation.

This is proof of deterministic *package* consistency, not proof of deployment,
crawling, indexing, license, factual verification, or AI model training.
Do not include manuscript/page body text in this public artifact.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = 'https://library.eviulon.com/'
OUT = ROOT / 'ai/discovery-attestation.json'
NS = '{http://www.sitemaps.org/schemas/sitemap/0.9}'


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(rel: str) -> str:
    return sha((ROOT / rel).read_bytes())


def digest_urls(urls: set[str]) -> str:
    return sha(('\n'.join(sorted(urls)) + '\n').encode('utf-8'))


def canonical(url: str) -> bool:
    return (isinstance(url, str) and url.startswith(BASE) and not any(ch in url for ch in ('?', '#', '\\'))
            and url.endswith('/') and url.count('https://') == 1)


def verify_coverage(all_urls: list[str], reading_urls: set[str], topic_urls: set[str], registry_urls: set[str]) -> dict:
    """Small independent test seam: fail closed on missing/duplicate/untrusted URLs."""
    if any(not canonical(u) for u in all_urls + list(reading_urls | topic_urls | registry_urls)):
        raise ValueError('noncanonical sitemap/reading/registry/topic URL')
    if len(all_urls) != len(set(all_urls)):
        raise ValueError('duplicate sitemap URL')
    if len(reading_urls) != 3702 or len(topic_urls) != 21 or len(registry_urls) != 3702:
        raise ValueError('source or topic URL count mismatch')
    if reading_urls != registry_urls:
        raise ValueError('registry/reading URL mismatch: ' + str((len(reading_urls-registry_urls),len(registry_urls-reading_urls))))
    sitemap = set(all_urls)
    if len(sitemap) != 3729 or not (reading_urls | topic_urls).issubset(sitemap):
        raise ValueError('sitemap missing canonical source or topic URLs')
    nav = sitemap - reading_urls - topic_urls
    expected = {BASE + x for x in ('', 'about/', 'chapters/', 'index/', 'for-agents/', 'research/')}
    if nav != expected:
        raise ValueError('unexpected or missing sitemap navigation URLs: ' + repr(sorted(nav ^ expected)))
    if reading_urls.intersection(topic_urls):
        raise ValueError('source and topic routes overlap')
    return {'sitemap_unique_urls':len(sitemap), 'reading_pages_and_landings':len(reading_urls),
            'topic_pages':len(topic_urls), 'other_navigation_pages':sorted(nav),
            'sitemap_url_set_sha256':digest_urls(sitemap), 'reading_url_set_sha256':digest_urls(reading_urls),
            'topic_url_set_sha256':digest_urls(topic_urls)}


def build() -> dict:
    release = (ROOT/'RELEASE_ID.txt').read_text(encoding='utf-8').strip()
    registry = json.loads((ROOT/'ai/source-registry.jsonld').read_text(encoding='utf-8'))
    graph = registry['@graph']; works = [n for n in graph if n.get('@type') in ('Book','Report')]
    books = [n for n in works if n['@type'] == 'Book']
    reports = [n for n in works if n['@type'] == 'Report']
    if len(books) != 14 or len(reports) != 210 or sum(len(x['hasPart']) for x in books) != 1925 or sum(len(x['hasPart']) for x in reports) != 1553:
        raise ValueError('registry source inventory inconsistent')
    ids = {x['@id'] for x in graph}
    if len(ids) != len(graph) or any(n['@id'] != n['url'] + ('#book' if n['@type']=='Book' else '#research') for n in works):
        raise ValueError('registry work entity ID mismatch')
    registry_urls = set()
    for work in works:
        registry_urls.add(work['url'])
        for entry in work['hasPart']:
            if entry['isPartOf']['@id'] != work['@id'] or entry['@id'] != entry['url'] + ('#print-page' if work['@type']=='Book' else '#section'):
                raise ValueError('registry part ID/parent mismatch')
            registry_urls.add(entry['url'])
    if len(registry_urls) != 3702:
        raise ValueError('registry canonical URLs are not unique')
    html = json.loads((ROOT/'html-cache/manifest.json').read_text(encoding='utf-8'))
    if html['release_id'] != release or html['total'] != 3702:
        raise ValueError('stale reading HTML manifest')
    reading_urls = {BASE.rstrip('/') + x['url'] for x in html['snapshots']}
    if len(reading_urls) != 3702:
        raise ValueError('duplicate reading HTML canonical URL')
    topics = json.loads((ROOT/'topics-cache/manifest.json').read_text(encoding='utf-8'))
    if topics['release_id'] != release or topics['pages'] != 21:
        raise ValueError('stale topic HTML manifest')
    topic_urls = {BASE.rstrip('/') + x['url'] for x in topics['snapshot_rows']}
    if len(topic_urls) != 21:
        raise ValueError('duplicate topic URL')
    idx = ET.parse(ROOT/'sitemap.xml').getroot()
    source_files = [x.text for x in idx.findall(NS+'sitemap/'+NS+'loc')]
    if len(source_files) != 17 or len(set(source_files)) != 17:
        raise ValueError('expected 17 distinct sitemap child documents')
    if source_files[0] != BASE+'sitemap-books.xml' or source_files[-2:] != [BASE+'sitemap-research.xml',BASE+'sitemap-topics.xml']:
        raise ValueError('sitemap order or document identities changed')
    all_urls,docs=[],[]
    for link in source_files:
        if not link.startswith(BASE) or '/' in link[len(BASE):] or not link.endswith('.xml'):
            raise ValueError('unsafe sitemap document URL')
        name=link[len(BASE):]
        locations=[x.text for x in ET.parse(ROOT/name).getroot().findall(NS+'url/'+NS+'loc')]
        all_urls.extend(locations)
        docs.append({'url':link,'url_count':len(locations),'sha256':file_sha(name)})
    coverage = verify_coverage(all_urls,reading_urls,topic_urls,registry_urls)
    if docs[-1]['url_count'] != 21:
        raise ValueError('topic sitemap incomplete')
    catalog=next(n for n in graph if n.get('@id') == BASE+'ai/source-registry.jsonld#catalog')
    rid=next(x['value'] for x in catalog['additionalProperty'] if x['name']=='release-id')
    if rid != release:
        raise ValueError('stale registry release ID')
    return {
      'schema': 'eviulon-discovery-package-attestation/v1',
      'release_id': release,
      'scope': 'local_release_package_only',
      'explanation': 'Cryptographic and set-equality assertions for published metadata, source URLs and local deployment files. Not proof of a live deployment, crawling, search indexing, source truth, training authorization or trained model.',
      'source_classes':{'official_books':14,'official_print_pages':1925,'supplemental_unverified_reports':210,'supplemental_report_sections':1553},
      'source_metadata_sha256':{'books_json':file_sha('data/books.json'),'reports_json':file_sha('data/research/reports.json')},
      'registry':{'url':BASE+'ai/source-registry.jsonld','sha256':file_sha('ai/source-registry.jsonld'),'work_entities':224,'canonical_reading_urls':3702,'full_text_exported':False},
      'topics':{'url':BASE+'ai/concepts.json','sha256':file_sha('ai/concepts.json'),'canonical_html_urls':21,'supplemental_evidence_unverified':True},
      'discovery':{'sitemap_index_url':BASE+'sitemap.xml','sitemap_index_sha256':file_sha('sitemap.xml'),
                   'sitemap_documents':docs,'robots_sha256':file_sha('robots.txt'),'llms_sha256':file_sha('llms.txt'),**coverage},
      'evidence_status':{'local_file_and_url_parity':True,'public_host_reachable':None,'external_crawling_confirmed':False,'search_indexing_confirmed':False,'corpus_training_rights_granted_here':False,'external_model_training_confirmed':False}
    }


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args()
    if a.write == a.check:p.error('specify exactly one of --write and --check')
    out = (json.dumps(build(),indent=2,sort_keys=True,ensure_ascii=False)+'\n').encode('utf-8')
    if a.write:OUT.write_bytes(out)
    elif not OUT.is_file() or OUT.read_bytes()!=out:raise SystemExit('FAIL stale or missing discovery attestation')
    print('DISCOVERY_ATTESTATION_PASS 3729 sitemap URLs = 3702 source + 21 topics + 6 navigation; 224 works 3478 units; release integrity', 'WRITE' if a.write else 'CHECK')
if __name__=='__main__':main()
