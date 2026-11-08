"""Bind ideas and claims to the version context under which they were derived.

This runs after ``revalidate.py``: it takes the revalidation ledger and the
existing idea / claim records and states, for each, which version assumption
it rests on and which deltas it depends on. An idea's version status is the
worst status among the evidence it leans on — never better.

Usage:
  python bind_ideas.py PROJECT --ledger 04-evidence-map/revalidation-ledger.json \
      --ideas 05-ideas/ideas.json --out 05-ideas/idea-version-binding.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from skills.shared.artifact_contract import validate_records  # noqa: E402

STATUS_RANK = {
    "valid": 0,
    "narrowed": 1,
    "needs_recheck": 2,
    "unverified": 3,
    "superseded": 4,
    "invalidated": 5,
}


def load_records(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        for key in ("records", "items", "results"):
            if isinstance(payload.get(key), list):
                return payload[key]
        return [payload]
    return payload if isinstance(payload, list) else []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--ideas", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    project = args.project.resolve()
    ledger = load_records(project / args.ledger)
    ideas = load_records(project / args.ideas)

    by_evidence = {r.get("evidence_id"): r for r in ledger}

    records: list[dict] = []
    for idea in ideas:
        idea_id = idea.get("idea_id")
        support = idea.get("supporting_evidence") or idea.get("evidence_ids") or []
        if isinstance(support, str):
            support = [support]

        bound = [by_evidence[e] for e in support if e in by_evidence]
        statuses = [b.get("status", "unverified") for b in bound]
        worst = max(statuses, key=lambda s: STATUS_RANK.get(s, 3)) if statuses else "unverified"

        dependencies = sorted({
            binding.get("delta_id")
            for record in bound
            for binding in record.get("bindings", [])
            if binding.get("delta_id")
        })

        assumptions = [
            f"Derived under {record.get('prior_version')}."
            for record in bound
            if record.get("prior_version")
        ]
        assumptions.append(
            "The delta map between versions was treated as the only source of change."
        )

        records.append({
            "idea_id": idea_id,
            "version_id": bound[0].get("new_version") if bound else None,
            "version_assumptions": assumptions,
            "version_dependencies": dependencies,
            "version_status": worst,
            "unbound_evidence": [
                e for e in support if e not in by_evidence
            ],
            "checked_at": date.today().isoformat(),
        })

    errors = validate_records(records, "idea_version_binding")
    out_path = project / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    counts: dict[str, int] = {}
    for record in records:
        counts[record["version_status"]] = counts.get(record["version_status"], 0) + 1
    print(json.dumps({"ideas": len(records), "contract_errors": len(errors),
                      "status_counts": counts, "out": str(out_path)}, ensure_ascii=False))
    if errors:
        print("\n".join(errors[:20]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
