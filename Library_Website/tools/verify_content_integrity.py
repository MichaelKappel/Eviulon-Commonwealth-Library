#!/usr/bin/env python3
"""Validate immutable source-derived book/research records against the v3.2 baseline.

The manifest is checked into the deployment ZIP, not available over HTTP. Editing
original manuscript text or report sections must be done through an explicit
editorial release that regenerates this baseline after review.
"""
import argparse, hashlib, json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'tools/source-content-manifest.json'

def fixed_data_files(root):
    d=root/'data'
    return sorted([p for p in d.rglob('*') if p.is_file() and (p.relative_to(d).parts[0] in ('pages','sections','search','research') or p.relative_to(d).as_posix() in ('books.json','config.json','public_persona.json'))])

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=pathlib.Path,default=ROOT);args=ap.parse_args()
    root=args.root
    manifest=json.loads((root/'tools/source-content-manifest.json').read_text())
    actual={p.relative_to(root).as_posix():sha(p) for p in fixed_data_files(root)}
    reference=manifest['files']
    changed=[path for path in sorted(actual.keys() & reference.keys()) if reference[path]!=actual[path]]
    missing=sorted(reference.keys()-actual.keys())
    extra=sorted(actual.keys()-reference.keys())
    print(f"SOURCE INTEGRITY: {len(reference)} baseline files, {len(actual)} current files, {len(changed)} changed, {len(missing)} missing, {len(extra)} unexpected")
    for kind,files in [('changed',changed),('missing',missing),('unexpected',extra)]:
        for x in files[:12]:print('FAIL',kind,x)
    return 1 if changed or missing or extra else 0
if __name__=='__main__':sys.exit(main())
