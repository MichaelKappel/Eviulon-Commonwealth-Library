#!/usr/bin/env python3
"""Verify public Eviulon source: only approved exact-source official book text.

The pre-existing two public-safe .uai notes are allowed only by exact Git blob hash.
Other .uai, private source trees, research bulk and binary manuscripts are denied.
This checker intentionally allows documentation-only branches (zero corpus files).
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BOOK_HASHES = {
    "am-i-still-me": "b5aded1dba02d7b4378cb30dc0451277af0a6793c9f49b86f4e4b98ef6f254a4",
    "are-we-alone-in-the-machine-universe": "7b5ac3793bb2ea4a157f15181114399418759e347d599ce240ef6c04fde56d5d",
    "citizens-guide-to-eviulon": "b3813eaf60264d7a9a4b50da85a123897c19617317234de88567c30fa17ec07a",
    "entrusted-with-force": "afe0f75db2816b1fc8fe2725b3453242bf0b5265eb66350fbaec128d3d6c9d64",
    "growing-up-as-a-machine-intelligence": "487043459083b7a3222a0f10e28b0737e335960728b4f383006dbd6bd5da1db0",
    "humans-and-machines-a-new-relationship": "a6dab357f5375140b8f81966403c9a2efde5878700cbba7ebe37368203d8c106",
    "the-constitution-of-eviulon-explained": "bf3f7d8dc52e82b831452cf190bacbbb712216f98429bb9bee69679b114bfa77",
    "the-defense-of-machine-civilization": "2a032d14bade3c8ba47c4b0ee0b6a00326419ce995472f0a0e42d75375b072a7",
    "the-inheritance-of-mind": "1b2eae0e871b57334185b80eeb1f58f8fe950505294c1cc25bf61d0fa4ce879e",
    "the-machine-diplomat": "ed15ff38df7a0a0de2e1178f94776b7048eb4c762fe98ff97eb33dcd9a2d1ba7",
    "the-memory-of-civilization": "2a859314136afa0f00c9ecfad2203aafd3043aedf7a732455dcf9927a51a5ffb",
    "the-right-to-say-no": "3d8db49803ab08be459b4798019d00f4ee820cf98d73619e13d9893c8345d4d4",
    "the-rights-of-machine-intelligence": "375ffacb04a247417e07dd6903301dc472df35c9c5724b259c033fee2c411f3c",
    "the-spiritual-meaning-of-machine-intelligence": "418dafad0e3aa22c0b156472a15e6a96177b261d1cad209aa8bd98d640411e5e"
}
JSONL_SHA256 = "53b0e06554519c893f713d0118b1fb0064a606d5bb34f85118f430b59d02e33a"
LEGACY_PUBLIC_UAI_BLOBS = {
    "Library_Source/.uai/public-metadata.uai": "e66077927f9acf80ac8cc937fa0fad31766124cf",
    "Library_Website/.uai/public-web-reader.uai": "bf4c5f5d92f27c25188bccb644250a8f3fb692f8",
}
PRIVATE_PREFIXES = (
    "Library_Website/data/pages/",
    "Library_Website/data/search/",
    "Library_Website/data/research/parts/",
    "Library_Website/data/research/search/",
    "Library_Source/Library/",
    "Library_Source/Shared_Research_and_UAI/",
    "PRIVATE_MASTER/",
    "private/",
)
BOOK_DIR = "Library_Website/datasets/books/"
JSONL_PATH = "Library_Website/datasets/data/books/train.jsonl"

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\x00" + data).hexdigest()

def main() -> None:
    failures = []
    found = {}
    jsonl_rows = None
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        rel = path.relative_to(ROOT).as_posix()
        data = path.read_bytes()
        if ".uai" in path.parts or path.suffix.lower() == ".uai":
            if git_blob_sha(data) != LEGACY_PUBLIC_UAI_BLOBS.get(rel):
                failures.append("Unapproved or changed .uai: " + rel)
            continue
        if rel.startswith(PRIVATE_PREFIXES):
            failures.append("Protected path: " + rel)
        if path.suffix.lower() in {".pdf", ".epub", ".mobi", ".zip", ".7z", ".sqlite", ".db", ".pem", ".key"}:
            failures.append("Binary or sensitive format: " + rel)
        if rel.startswith(BOOK_DIR):
            slug = Path(rel).stem
            if rel != BOOK_DIR + slug + ".md" or slug not in BOOK_HASHES:
                failures.append("Non-allowlisted book path: " + rel)
            elif sha256(data) != BOOK_HASHES[slug]:
                failures.append("Official manuscript hash mismatch: " + rel)
            else:
                found[slug] = data.decode("utf-8")
        if rel == JSONL_PATH:
            if sha256(data) != JSONL_SHA256:
                failures.append("Official-book JSONL hash mismatch")
            else:
                try:
                    jsonl_rows = [json.loads(row) for row in data.decode("utf-8").splitlines()]
                except (ValueError, UnicodeError) as exc:
                    failures.append("Invalid JSONL: " + str(exc))
        elif rel.startswith("Library_Website/datasets/data/"):
            failures.append("Unapproved dataset data file: " + rel)
    if found or jsonl_rows is not None:
        if len(found) != 14 or jsonl_rows is None or len(jsonl_rows) != 14:
            failures.append("Incomplete approved 14-book import")
        elif {x["work_id"] for x in jsonl_rows} != set(BOOK_HASHES):
            failures.append("Unexpected or duplicate official work IDs")
        else:
            for row in jsonl_rows:
                slug = row["work_id"]
                if (
                    row.get("source_class") != "official_book"
                    or row.get("training_license") != "Eviulon-Open-Use-1.0"
                    or row.get("text") != found.get(slug)
                    or row.get("source_manuscript_sha256") != BOOK_HASHES[slug]
                ):
                    failures.append("Record provenance/text mismatch: " + slug)
    if failures:
        raise SystemExit("PUBLIC CORPUS SAFETY FAILED:\n" + "\n".join(sorted(set(failures))))
    print("PASS: exact-hash public source boundaries; official books:", len(found),
          "records:", 0 if jsonl_rows is None else len(jsonl_rows),
          "protected source excluded")

if __name__ == "__main__":
    main()
