"""Validate paper-card JSON files without judging their scientific content."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from skills.shared.artifact_contract import validate_records


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("cards", type=Path); args = parser.parse_args()
    paths = sorted(args.cards.glob("*.json")) if args.cards.is_dir() else [args.cards]
    records = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    errors = validate_records(records, "paper_card")
    if errors:
        print("INVALID\n" + "\n".join(f"- {x}" for x in errors)); return 1
    print(f"VALID cards={len(records)}"); return 0


if __name__ == "__main__": raise SystemExit(main())

