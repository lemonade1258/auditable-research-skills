"""Revalidate an existing evidence set against a version delta map.

The model is used for the part that needs judgment: which deltas bind to which
evidence, and whether the evidence content actually satisfies the delta's
resolution requirement. The *status* is then derived deterministically from
that binding plus the delta's scope semantics, so the decision rule is
auditable and stable across runs.

Usage:
  python revalidate.py PROJECT --deltas 02-versions/delta-map.json \
      --evidence 04-evidence-map/evidence-matrix.json \
      --out 04-evidence-map/revalidation-ledger.json [--model qwen-max]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from skills.shared.artifact_contract import validate_records  # noqa: E402
from skills.shared.llm_client import (  # noqa: E402
    LLMConfig,
    LLMUnavailable,
    chat_json,
    resolve_config,
    write_receipt,
)


# Deltas whose scope semantics require per-evidence judgment rather than a
# blanket invalidation.
SCOPE_TYPES = {"scope_narrowed", "scope_broadened"}


BIND_SYSTEM = """You audit whether research evidence produced under an OLD version of a
reporting guideline still holds under a NEW version.

For each evidence record you must:
1. Decide which deltas (changes between the versions) affect it. Bind by subject
   matter, not by keyword overlap: evidence about how studies were screened binds to
   deltas about eligibility and screening; evidence about risk-of-bias appraisal binds
   to deltas about appraisal methods; evidence about statistical synthesis binds to
   deltas about effect measures and synthesis methods.
2. For each bound delta, judge whether the evidence SATISFIES the delta's
   resolution_requirement (what evidence a downstream claim must now carry).
   Use exactly one of: 'satisfies', 'partially_satisfies', 'does_not_satisfy'.
3. Write a one-sentence reasoning per binding that says why, quoting the relevant
   part of the evidence text.
4. If no delta affects the evidence, bind nothing and set overall_requirement to
   'unaffected'.

Never judge whether the underlying study is correct. Judge only whether the
evidence still answers the question under the new version.
Return ONLY a JSON array, one object per evidence record."""

BIND_USER = """NEW VERSION CHANGES (deltas):

{deltas}

EVIDENCE RECORDS:

{evidence}

For each evidence record return an object with these keys:
evidence_id, overall_requirement (one of: unaffected, satisfied, partially_satisfied,
not_satisfied, uncertain), reasoning, bindings

Each binding is an object with keys:
delta_id, requirement_fit (satisfies | partially_satisfies | does_not_satisfy),
reasoning

Use no more than 6 bindings per evidence record, choosing the deltas that truly
affect it."""


def derive_status(delta: dict, fit: str) -> str:
    """Derive the revalidation status from one delta and one fit judgment."""
    change_type = delta.get("change_type")
    if fit == "does_not_satisfy":
        if change_type in SCOPE_TYPES:
            # A scope change does not invalidate what is still inside the scope.
            return "narrowed"
        if change_type == "requirement_removed":
            return "superseded"
        return "invalidated"
    if fit == "partially_satisfies":
        return "needs_recheck"
    return "valid"


STATUS_RANK = {
    "valid": 0,
    "narrowed": 1,
    "needs_recheck": 2,
    "unverified": 3,
    "superseded": 4,
    "invalidated": 5,
}


def worst(statuses: list[str]) -> str:
    if not statuses:
        return "unverified"
    return max(statuses, key=lambda s: STATUS_RANK.get(s, 3))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("--deltas", required=True)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--model")
    parser.add_argument("--batch-size", type=int, default=6)
    args = parser.parse_args()

    project = args.project.resolve()
    if not (project / "manifest.json").exists():
        raise SystemExit(f"not a research project: {project}")

    deltas = json.loads((project / args.deltas).read_text(encoding="utf-8"))
    evidence = json.loads((project / args.evidence).read_text(encoding="utf-8"))

    if not deltas:
        raise SystemExit("delta map is empty; run version-delta first")

    delta_index = {d.get("delta_id"): d for d in deltas}

    try:
        config = resolve_config({"model": args.model} if args.model else None)
    except LLMUnavailable as exc:
        raise SystemExit(str(exc))

    records: list[dict] = []
    receipts_dir = project / "04-evidence-map" / "revalidation-receipts"

    for start in range(0, len(evidence), args.batch_size):
        batch = evidence[start : start + args.batch_size]
        delta_view = json.dumps(
            [
                {
                    "delta_id": d.get("delta_id"),
                    "change_type": d.get("change_type"),
                    "interpretation": d.get("interpretation"),
                    "resolution_requirement": d.get("resolution_requirement"),
                    "impact_level": d.get("impact_level"),
                    "source_location": d.get("source_location"),
                }
                for d in deltas
            ],
            ensure_ascii=False,
            indent=2,
        )
        evidence_view = json.dumps(batch, ensure_ascii=False, indent=2)

        raw, result = chat_json(
            [{"role": "user", "content": BIND_USER.format(deltas=delta_view, evidence=evidence_view)}],
            config,
            system=BIND_SYSTEM,
        )
        if isinstance(raw, dict):
            raw = [raw]

        write_receipt(
            receipts_dir / f"batch-{start // args.batch_size + 1:03d}.json",
            raw, result,
            purpose="evidence-revalidation.bind",
            extra={"evidence_ids": [e.get("evidence_id") for e in batch]},
        )

        by_id = {str(item.get("evidence_id")): item for item in raw if isinstance(item, dict)}
        for record in batch:
            evidence_id = record.get("evidence_id")
            assessment = by_id.get(str(evidence_id), {})
            bindings = assessment.get("bindings") or []
            statuses: list[str] = []
            details = []
            for binding in bindings:
                delta = delta_index.get(binding.get("delta_id"))
                if delta is None:
                    continue
                status = derive_status(delta, binding.get("requirement_fit", "does_not_satisfy"))
                statuses.append(status)
                details.append({
                    "delta_id": binding.get("delta_id"),
                    "change_type": delta.get("change_type"),
                    "requirement_fit": binding.get("requirement_fit"),
                    "status": status,
                    "reasoning": binding.get("reasoning", ""),
                })

            overall = assessment.get("overall_requirement", "uncertain")
            if overall == "unaffected":
                status = "valid"
            elif not statuses:
                status = "unverified"
            else:
                status = worst(statuses)

            records.append({
                "revalidation_id": f"RV-{evidence_id}",
                "evidence_id": evidence_id,
                "source_id": record.get("source_id"),
                "prior_version": record.get("version_id") or record.get("last_verified_under_version"),
                "new_version": deltas[0].get("target_version") if deltas else None,
                "status": status,
                "overall_requirement": overall,
                "reasoning": assessment.get("reasoning", ""),
                "bindings": details,
                "checked_at": date.today().isoformat(),
            })
        time.sleep(0.2)

    errors = validate_records(records, "evidence_revalidation")
    out_path = project / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    counts: dict[str, int] = {}
    for record in records:
        counts[record["status"]] = counts.get(record["status"], 0) + 1
    print(json.dumps({"records": len(records), "contract_errors": len(errors),
                      "status_counts": counts, "out": str(out_path)}, ensure_ascii=False))
    if errors:
        print("\n".join(errors[:20]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
