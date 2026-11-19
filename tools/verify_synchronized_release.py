#!/usr/bin/env python3
"""Verify synchronized Eviulon private/site/GitHub packages without extracting.

Usage:
 python verify_synchronized_release.py --private Eviulon_PRIVATE_MASTER_...zip \
   --root Library.Eviulon.com_ROOT_DEPLOY_...zip \
   --github Eviulon_Public_GitHub_...zip

The exact same RELEASE_SYNC.json and ID must occur in all three.
The complete current root and public trees must be mirrored byte-for-byte
inside the private master. The public code must equal the root code; public
GitHub must not contain private memory, manuscript or full-text search assets.
"""
import argparse,collections,hashlib,json,re,sys,zipfile
from pathlib import Path

def sha(data):return hashlib.sha256(data).hexdigest()
def inventory(z,prefix=''):
 d={}
 for info in z.infolist():
  if info.is_dir():continue
  n=info.filename
  if not n.startswith(prefix):continue
  key=n[len(prefix):]
  if not key:continue
  assert key not in d,('duplicate ZIP path',n)
  assert not key.startswith('/') and '..' not in Path(key).parts,('bad ZIP path',n)
  d[key]=sha(z.read(n))
 return d

def tree_signature(mapping):
 lines=[(name+'\0'+hashvalue+'\n').encode('utf8') for name,hashvalue in sorted(mapping.items()) if name!='RELEASE_SYNC.json']
 return {'files':len(lines),'tree_sha256':sha(b''.join(lines))}

def main():
 ap=argparse.ArgumentParser()
 for arg in ['private','root','github']:ap.add_argument('--'+arg,type=Path,required=True)
 opt=ap.parse_args()
 for field in vars(opt).values():
  if not field.is_file():ap.error('not found: '+str(field))
 with zipfile.ZipFile(opt.private) as private,zipfile.ZipFile(opt.root) as root,zipfile.ZipFile(opt.github) as github:
  for name,z in [('PRIVATE_MASTER',private),('ROOT_DEPLOY',root),('PUBLIC_GITHUB',github)]:
   bad=z.testzip();assert bad is None,(name,'CRC fail',bad)
   print('PASS CRC',name,len(z.infolist()))
  a=private.read('RELEASE_CONTROL/RELEASE_SYNC.json')
  assert a==root.read('RELEASE_SYNC.json')==github.read('RELEASE_SYNC.json'),'VERSION MANIFEST DRIFT'
  p=json.loads(a)
  release=p['release_id']
  assert release and all(release in z.read(name).decode().strip() for z,name in [
      (private,'RELEASE_CONTROL/RELEASE_ID.txt'),(root,'RELEASE_ID.txt'),(github,'RELEASE_ID.txt')]),'Release ID mismatch'
  root_files=inventory(root)
  public_files=inventory(github)
  original_files=inventory(private,'PRIVATE_SOURCE/')
  prior_public=inventory(private,'GITHUB_ORIGINAL/')
  master_site=inventory(private,'SITE_ROOT/')
  master_public=inventory(private,'GITHUB_PUBLIC/')
  assert root_files==master_site,'Private master SITE_ROOT differs from deploy ZIP'
  assert public_files==master_public,'Private master GITHUB_PUBLIC differs from GitHub ZIP'
  for typ,actual in [('site_root',root_files),('github_public',public_files),('private_source',original_files),('original_github',prior_public)]:
   assert tree_signature(actual)==p['files_and_trees'][typ],(typ,'hash drift')
  print('PASS master mirrors and all tree SHA256',release)
  assert len([n for n in root_files if re.fullmatch(r'data/pages/[^/]+/\d{4}\.json',n)])==1925
  assert len([n for n in root_files if re.fullmatch(r'data/research/parts/[^/]+/[^/]+/\d{4}\.json',n)])==1553
  assert 'index.php' in root_files and '.htaccess' in root_files
  assert 'tools/verify_synchronized_release.py' in root_files
  assert 'RELEASE_MANIFEST.json' in root_files
  assert json.loads(root.read('VERSION.json'))['release_id']==release
  assert 'RELEASE_MANIFEST.json' in public_files.get('Library_Website/RELEASE_MANIFEST.json','') or public_files.get('Library_Website/RELEASE_MANIFEST.json')==root_files['RELEASE_MANIFEST.json']
  # No private full-text assets inside public ZIP.
  for n in public_files:
   assert '/.uai/' not in '/'+n and not n.lower().endswith(('.uai','.pdf','.epub','.mobi','.azw','.zip')),('PRIVATE FILE IN GITHUB',n)
   assert not n.startswith(('Library_Website/data/pages/','Library_Website/data/search/','Library_Website/data/research/parts/','Library_Website/data/research/search/','Library_Source/Library/','Library_Source/Shared_Research_and_UAI/')),('PUBLIC DATA LEAK',n)
  # Runtime can't contain source PDFs or private memory, regardless of hash.
  for n in root_files:
   assert not n.lower().endswith(('.uai','.pdf','.epub','.mobi')),('SOURCE/PRIVATE FILE IN DEPLOY',n)
  paths=json.loads(private.read('RELEASE_CONTROL/PUBLIC_SHARED_PATHS.json'))
  for n in paths:
   assert root_files[n]==public_files['Library_Website/'+n],('Mismatch in public code path',n)
  fp=sha(b''.join((n+'\0'+root_files[n]+'\n').encode() for n in sorted(paths)))
  assert fp==p['public_mirror_sha256']
  assert len(paths)==p['public_mirror_file_count']
  print('PASS public source code parity',len(paths),'files')
  runic=json.loads(private.read('PRIVATE_SOURCE/RUNIC_MEMORY_MANIFEST.json'))
  assert runic['count']==259
  for n,d in runic['files'].items():
   assert original_files[n]==d['encoded_sha256'],('Runic memory corruption',n)
  print('PASS 259/259 protected encoded memory SHA256')
  books=json.loads(root.read('data/books.json'))
  hashes=set(original_files.values())
  assert len(books)==14 and all(b['source_sha256'] in hashes for b in books)
  print('PASS 14/14 matching original book PDF/source hashes')
  reports=json.loads(root.read('data/research/reports.json'))
  matched=sum(r['source_sha256'] in hashes for r in reports)
  assert len(reports)==210 and matched==p['source_provenance']['reports_found_in_private']
  print('REPORT PROVENANCE:',matched,'matched original source hashes;',210-matched,'not matched in provided private source. All published section JSONs retained.')
  print('PASS ALL ARTIFACTS are one synchronized release:',release)

if __name__=='__main__':
 try:main()
 except Exception as error:
  print('FAIL:',error,file=sys.stderr)
  raise
