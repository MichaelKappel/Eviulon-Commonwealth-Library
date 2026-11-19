#!/usr/bin/env python3
"""Recover a complete, verified root only from the owner's private SITE_ROOT.

This script intentionally cannot conjure manuscripts from public metadata.
"""
from pathlib import Path
import argparse, json, shutil

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--private-site',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True)
 a=p.parse_args()
 root=a.private_site.resolve();dest=a.output.resolve()
 if dest.exists():p.error('Output already exists; use a fresh location outside GitHub')
 if not (root/'RELEASE_SYNC.json').is_file():p.error('Private site must have RELEASE_SYNC.json')
 if not (root/'data/pages').is_dir() or not (root/'data/research/parts').is_dir():p.error('Missing original public reading content')
 if dest==root or root in dest.parents:p.error('Output must not be inside source site')
 shutil.copytree(root,dest,symlinks=False)
 print('Recovered root deployment at',dest)
 print('Release',json.loads((dest/'RELEASE_SYNC.json').read_text())['release_id'])
 print('Verify server protects data/, src/, tools/ after deployment; do not commit the output to GitHub')
if __name__=='__main__':main()
