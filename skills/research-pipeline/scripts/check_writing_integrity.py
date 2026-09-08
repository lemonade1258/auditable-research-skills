"""Deterministic before/after academic rewrite integrity checker."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

NUMBER = re.compile(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?%?")
CITATION = re.compile(r"(?:\\cite\w*\{[^}]+\}|\[[0-9][^]]*\]|https?://\S+)")


def tokens(pattern, text): return sorted(set(pattern.findall(text)))


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("before", type=Path); p.add_argument("after", type=Path); p.add_argument("--allow-new-analysis", action="store_true"); args = p.parse_args()
    before, after = args.before.read_text(encoding="utf-8"), args.after.read_text(encoding="utf-8")
    before_numbers, after_numbers = tokens(NUMBER, before), tokens(NUMBER, after)
    before_refs, after_refs = tokens(CITATION, before), tokens(CITATION, after)
    errors = []
    if not args.allow_new_analysis:
        errors += [f"new number: {x}" for x in after_numbers if x not in before_numbers]
        errors += [f"new citation/url: {x}" for x in after_refs if x not in before_refs]
    result = {"status": "PASS" if not errors else "BLOCKED", "before_numbers": before_numbers,
              "after_numbers": after_numbers, "before_citations": before_refs, "after_citations": after_refs, "errors": errors}
    print(json.dumps(result, ensure_ascii=False, indent=2)); return 0 if not errors else 1


if __name__ == "__main__": raise SystemExit(main())

