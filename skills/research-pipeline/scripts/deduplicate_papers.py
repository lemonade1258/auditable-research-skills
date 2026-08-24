"""Deduplicate paper records from a JSON array or JSONL stream.

Usage: python deduplicate_papers.py input.json output.json
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path


def key(record: dict) -> tuple[str, str]:
    doi = re.sub(r"^https?://doi.org/", "", str(record.get("doi", "")).strip().lower())
    title = unicodedata.normalize("NFKC", str(record.get("title", ""))).lower()
    title = re.sub(r"[^a-z0-9]+", " ", title).strip()
    return (doi, title)


def load(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    value = json.loads(text)
    if not isinstance(value, list):
        raise ValueError("input must be a JSON array or JSONL file")
    return value


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: deduplicate_papers.py input.json output.json", file=sys.stderr)
        return 2
    records = load(Path(sys.argv[1]))
    unique = {}
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("each record must be an object")
        k = key(record)
        if k == ("", ""):
            raise ValueError("each record needs at least title or doi")
        unique.setdefault(k, record)
    Path(sys.argv[2]).write_text(json.dumps(list(unique.values()), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"input={len(records)} unique={len(unique)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
