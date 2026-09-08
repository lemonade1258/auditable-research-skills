"""Deterministic release-package checks; unresolved visual/policy checks remain explicit."""
from __future__ import annotations
import argparse, json
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("package", type=Path); p.add_argument("--release", choices=("review", "publication"), required=True); p.add_argument("--anonymity", choices=("none", "single-blind", "double-blind")); p.add_argument("--identity-term", action="append", default=[]); args = p.parse_args()
    root = args.package.resolve(); files = [x for x in root.rglob("*") if x.is_file()]
    findings = []
    if args.release == "review" and not args.anonymity: findings.append({"severity": "P0", "finding": "anonymity policy not supplied"})
    for path in files:
        if path.suffix.lower() in {".md", ".tex", ".txt"}:
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            for term in args.identity_term:
                if term.lower() in text: findings.append({"severity": "P0", "file": str(path.relative_to(root)), "finding": f"identity term found: {term}"})
    findings.append({"severity": "UNRESOLVED", "finding": "visual PDF inspection and venue metadata policy require manual confirmation"})
    output = {"release": args.release, "anonymity": args.anonymity, "files": len(files), "findings": findings,
              "status": "NOT_READY" if any(x["severity"] == "P0" for x in findings) else "UNRESOLVED"}
    print(json.dumps(output, ensure_ascii=False, indent=2)); return 1 if output["status"] == "NOT_READY" else 0


if __name__ == "__main__": raise SystemExit(main())

