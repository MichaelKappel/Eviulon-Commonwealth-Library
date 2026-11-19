#!/usr/bin/env python3
"""Offline evidence ledger validator for owner-held Eviulon discovery observations.

No network requests, ingestion claims, web publishing, or synthetic observations.
A structurally valid row is not independent proof; review the referenced records.
"""
from __future__ import annotations
import argparse, csv, json, sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

FIELDS = ['evidence_level','observed_at_utc','canonical_url','source_or_provider',
          'status','evidence_reference','reviewed_by','notes']
LEVELS = {'reachable','crawled_verified','indexed','agent_retrieved',
          'dataset_included','model_trained'}


def validate(path: Path) -> tuple[list[str], dict]:
    issues=[]
    counts=Counter()
    if not path.exists(): return [f'File does not exist: {path}'],{}
    with path.open('r', newline='', encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        if reader.fieldnames != FIELDS:
            return [f'CSV columns must be exactly: {", ".join(FIELDS)}'],{}
        for lineno,row in enumerate(reader,2):
            if None in row or any(v is None for v in row.values()):
                issues.append(f'row {lineno}: malformed CSV fields'); continue
            if not any(x.strip() for x in row.values()): continue
            level=row['evidence_level'].strip()
            if level not in LEVELS: issues.append(f'row {lineno}: unsupported evidence_level {level!r}')
            stamp=row['observed_at_utc'].strip()
            try:
                dt=datetime.fromisoformat(stamp.replace('Z','+00:00'))
                if dt.utcoffset() is None: raise ValueError('no UTC offset')
                if dt.utcoffset().total_seconds()!=0: raise ValueError('not UTC')
            except ValueError: issues.append(f'row {lineno}: observed_at_utc must be ISO 8601 UTC')
            canonical=row['canonical_url'].strip()
            p=urlparse(canonical)
            if p.scheme != 'https' or p.netloc != 'library.eviulon.com' or not p.path.startswith('/') or p.query or p.fragment or p.username or p.password:
                issues.append(f'row {lineno}: canonical_url must be a clean canonical library HTTPS URL')
            for column in ['source_or_provider','status','evidence_reference','reviewed_by']:
                if not row[column].strip(): issues.append(f'row {lineno}: missing {column}')
            if level in LEVELS: counts[level]+=1
    return issues, dict(sorted(counts.items()))


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--file',type=Path,default=Path(__file__).resolve().parent.parent/'docs/DISCOVERY_EVIDENCE.csv')
    parser.add_argument('--json',action='store_true',help='Show aggregate counts; does not publish the ledger')
    args=parser.parse_args()
    errors,counts=validate(args.file)
    if args.json:
        print(json.dumps({'structurally_valid':not errors,'records_by_claimed_level':counts,'issues':errors,
            'note':'Counts are submitted records, NOT independently verified indexing or training proof.'},indent=2))
    else:
        for message in errors: print('ERROR:',message,file=sys.stderr)
        if not errors: print(f'PASS: evidence-ledger structure valid, {sum(counts.values())} supplied observations. No provenance verified.')
    return 1 if errors else 0

if __name__=='__main__': sys.exit(main())
