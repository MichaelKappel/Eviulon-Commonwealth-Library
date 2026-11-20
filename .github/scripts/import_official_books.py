#!/usr/bin/env python3
"""Import only verified official Eviulon book Markdown/JSONL into a local Git checkout.

This script never pushes, commits, merges, or deploys. Run it *from a cloned
GitHub repository* on the intended distribution/open-books-v3.14.16 branch.
"""
import argparse
import importlib.util
import json
import hashlib
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("public_corpus_guard", ROOT / ".github/scripts/verify_open_corpus.py")
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kit_zip", type=Path, help="v3.14.16.1 Hugging Face distribution kit ZIP")
    parser.add_argument("--apply", action="store_true", help="Stage approved files; default is dry run")
    args = parser.parse_args()
    branch = subprocess.check_output(["git","branch","--show-current"], cwd=ROOT, text=True).strip()
    if branch != "distribution/open-books-v3.14.16":
        parser.error("checkout the draft pull-request branch; branch was "+branch)
    if subprocess.check_output(["git","status","--porcelain"], cwd=ROOT, text=True).strip():
        parser.error("working tree is not clean")
    with zipfile.ZipFile(args.kit_zip) as z:
        books = {slug: z.read(f"books/{slug}.md") for slug in guard.BOOK_HASHES}
        jsonl = z.read("data/books/train.jsonl")
    for slug, data in books.items():
        if sha(data) != guard.BOOK_HASHES[slug]:
            raise SystemExit("Refusing modified manuscript: "+slug)
    if sha(jsonl) != guard.JSONL_SHA256:
        raise SystemExit("Refusing modified JSONL")
    records = [json.loads(row) for row in jsonl.decode("utf-8").splitlines()]
    if len(records) != 14 or {r["work_id"] for r in records} != set(books):
        raise SystemExit("Incorrect or duplicate official works")
    for r in records:
        slug = r["work_id"]
        if (r.get("text") != books[slug].decode("utf-8")
            or r.get("source_class") != "official_book"
            or r.get("training_license") != "Eviulon-Open-Use-1.0"
            or r.get("source_manuscript_sha256") != guard.BOOK_HASHES[slug]):
            raise SystemExit("Record provenance mismatch: "+slug)
    targets = {ROOT / guard.BOOK_DIR / (slug + ".md"): raw for slug, raw in books.items()}
    targets[ROOT / guard.JSONL_PATH] = jsonl
    for target, raw in targets.items():
        if target.exists() and target.read_bytes() != raw:
            raise SystemExit("Refusing to overwrite changed existing file: "+str(target))
    print("PASS: 14 original Markdown books and 14-record JSONL verified.")
    if not args.apply:
        print("Dry run: use --apply to copy files; no changes made.")
        return
    for target, raw in targets.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    guard.main()
    print("PASS: 15 approved files staged locally. Review git status before committing/pushing.")

if __name__ == "__main__":
    main()
