#!/usr/bin/env python3
"""Exact UTF-8/binary memory transport using 16 Elder Futhark symbols.

This is an encoding of bytes, not an Old Norse translation. A file is encoded
byte-for-byte (each nibble => one rune); line wrapping is non-semantic.

Usage:
  python tools/elder_futhark_memory.py verify
  python tools/elder_futhark_memory.py view AGENTS.md
  python tools/elder_futhark_memory.py view .uai/totem.uai
  python tools/elder_futhark_memory.py restore --output ../Eviulon_Decoded_Working_Copy
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

RUNES = 'ᚠᚢᚦᚨᚱᚲᚷᚹᚺᚾᛁᛃᛇᛈᛉᛊ'
REV = {c: i for i, c in enumerate(RUNES)}
ROOT = Path(__file__).resolve().parent.parent
MANIFEST = Path('RUNIC_MEMORY_MANIFEST.json')


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encode_bytes(raw: bytes) -> bytes:
    glyphs = ''.join(RUNES[b >> 4] + RUNES[b & 15] for b in raw)
    wrapped = '\n'.join(glyphs[i:i+96] for i in range(0, len(glyphs), 96)) + '\n'
    return wrapped.encode('utf-8')


def decode_bytes(raw: bytes) -> bytes:
    text = raw.decode('utf-8')
    chars = ''.join(text.splitlines())
    if len(chars) % 2:
        raise ValueError('Odd number of Futhark glyphs')
    try:
        return bytes(16 * REV[chars[i]] + REV[chars[i+1]] for i in range(0, len(chars), 2))
    except KeyError as exc:
        raise ValueError('Non-Futhark glyph present') from exc


def get_manifest(root=ROOT):
    obj = json.loads((root / MANIFEST).read_text(encoding='utf-8'))
    if obj.get('format') != 'eviulon.elder-futhark-byte-nibbles.v1':
        raise ValueError('Unsupported format')
    return obj


def safe_path(root: Path, rel: str) -> Path:
    p = root / rel
    if not p.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'Unsafe path: {rel}')
    return p


def verify(root: Path, verbose=True) -> bool:
    m = get_manifest(root)
    files = m['files']
    errors=[]
    for rel, record in files.items():
        try:
            p = safe_path(root, rel)
            blob = p.read_bytes()
            if sha(blob) != record['encoded_sha256']:
                errors.append(f'encoded checksum: {rel}')
                continue
            plain = decode_bytes(blob)
            if sha(plain) != record['original_sha256']:
                errors.append(f'decode checksum: {rel}')
            if encode_bytes(plain) != blob:
                errors.append(f'noncanonical rune encoding: {rel}')
        except Exception as exc:
            errors.append(f'{rel}: {exc}')
    if verbose:
        print(json.dumps({'status':'PASS' if not errors else 'FAIL','files':len(files), 'errors':errors[:30]},ensure_ascii=False,indent=2))
    return not errors


def view(root: Path, rel: str) -> None:
    m=get_manifest(root)
    if rel not in m['files']:
        raise ValueError('File is not in the runic conversion manifest')
    data = decode_bytes(safe_path(root,rel).read_bytes())
    if sha(data) != m['files'][rel]['original_sha256']:
        raise ValueError('Integrity mismatch')
    sys.stdout.buffer.write(data)


def restore(root: Path, out: Path) -> None:
    if out.exists() and any(out.iterdir()):
        raise ValueError('Refusing to write into nonempty output directory')
    if out.resolve() == root.resolve() or out.resolve().is_relative_to(root.resolve()):
        raise ValueError('Output must be outside encoded source repository')
    if not verify(root,verbose=False):
        raise ValueError('Runic integrity check failed')
    m=get_manifest(root)
    skips = {'.git', '.runic-decoded', '__pycache__', '.venv'}
    for base, dirs, fnames in os.walk(root):
        dirs[:] = [d for d in dirs if d not in skips]
        base=Path(base)
        for fname in fnames:
            src=base/fname
            rel=src.relative_to(root)
            dst=out/rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_symlink():
                raise ValueError(f'Symlink not allowed: {rel}')
            if rel.as_posix() in m['files']:
                dst.write_bytes(decode_bytes(src.read_bytes()))
            else:
                shutil.copy2(src,dst)
    for rel, info in m['files'].items():
        if sha((out/rel).read_bytes()) != info['original_sha256']:
            raise ValueError(f'Restored file checksum mismatch: {rel}')
    print(f'Restored {len(m["files"])} original .uai/AGENTS files to {out}; remaining files copied unchanged')


def main() -> None:
    pa=argparse.ArgumentParser(description='Exact reversible Eviulon Elder Futhark memory transport')
    pa.add_argument('--root',type=Path,default=ROOT)
    sp=pa.add_subparsers(dest='command',required=True)
    sp.add_parser('verify')
    vp=sp.add_parser('view');vp.add_argument('path')
    rp=sp.add_parser('restore');rp.add_argument('--output',type=Path,required=True)
    ns=pa.parse_args()
    root=ns.root.resolve()
    if ns.command=='verify': sys.exit(0 if verify(root) else 1)
    if ns.command=='view': view(root,ns.path)
    if ns.command=='restore': restore(root,ns.output.resolve())

if __name__=='__main__': main()
