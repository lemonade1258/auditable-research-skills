"""Build a dated freshness ledger from a registry and explicit query records."""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("project", type=Path); parser.add_argument("--idea-id", required=True)
    parser.add_argument("--status", choices=("open", "partially_open", "likely_closed", "unverified"), required=True)
    parser.add_argument("--query", action="append", required=True); parser.add_argument("--nearest", action="append", default=[])
    parser.add_argument("--evidence", action="append", default=[]); parser.add_argument("--note", default="")
    args = parser.parse_args(); project = args.project.resolve()
    record = {"idea_id": args.idea_id, "checked_at": date.today().isoformat(), "status": args.status,
              "queries": args.query, "nearest_work_ids": args.nearest, "evidence": args.evidence, "notes": args.note}
    output = project / "06-ideas" / "freshness-ledger.json"; output.parent.mkdir(parents=True, exist_ok=True)
    existing = json.loads(output.read_text(encoding="utf-8")) if output.exists() else []
    existing = [x for x in existing if x.get("idea_id") != args.idea_id]; existing.append(record)
    output.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(record, ensure_ascii=False)); return 0


if __name__ == "__main__": raise SystemExit(main())

