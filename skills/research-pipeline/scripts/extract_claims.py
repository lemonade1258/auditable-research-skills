"""Create a manuscript claim ledger from JSONL claims or a simple text file."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("project", type=Path); p.add_argument("input", type=Path); args = p.parse_args()
    text = args.input.read_text(encoding="utf-8")
    claims = []
    if args.input.suffix.lower() == ".jsonl":
        claims = [json.loads(line) for line in text.splitlines() if line.strip()]
    else:
        for i, line in enumerate(text.splitlines(), 1):
            line = line.strip()
            if line and not line.startswith("#"):
                claims.append({"claim_id": f"claim-{i:04d}", "text": line, "section": "unknown",
                               "supporting_evidence": [], "scope_conditions": [], "claim_type": "fact",
                               "integrity_status": "needs-source"})
    for i, claim in enumerate(claims, 1):
        claim.setdefault("claim_id", f"claim-{i:04d}"); claim.setdefault("supporting_evidence", [])
        claim.setdefault("scope_conditions", []); claim.setdefault("claim_type", "fact")
        claim.setdefault("integrity_status", "needs-source")
    output = args.project.resolve() / "10-manuscript" / "claim-ledger.json"; output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(claims, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"claims": len(claims), "output": str(output)}, ensure_ascii=False)); return 0


if __name__ == "__main__": raise SystemExit(main())

