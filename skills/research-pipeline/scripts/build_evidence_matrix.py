"""Create and validate a claim/evidence matrix inside a project."""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("--claim", action="append", default=[])
    parser.add_argument("--source", action="append", default=[])
    parser.add_argument("--label", choices=("author_claim", "observed_result", "pipeline_synthesis", "unverified_inference"), default="unverified_inference")
    args = parser.parse_args(); project = args.project.resolve()
    if not (project / "manifest.json").exists(): raise SystemExit(f"not a project: {project}")
    if len(args.claim) != len(args.source): raise SystemExit("--claim and --source must be supplied in pairs")
    records = []
    for index, (claim, source) in enumerate(zip(args.claim, args.source), 1):
        records.append({"evidence_id": f"ev-{index:04d}", "claim": claim, "source_id": source,
                        "source_location": "needs-location", "quote": "", "evidence_label": args.label,
                        "verification_status": "unverified", "retrieved_at": date.today().isoformat(), "notes": ""})
    output = project / "04-evidence-map" / "evidence-matrix.json"; output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"records": len(records), "output": str(output)}, ensure_ascii=False)); return 0


if __name__ == "__main__": raise SystemExit(main())

