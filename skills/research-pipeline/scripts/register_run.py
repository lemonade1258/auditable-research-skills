"""Append an experiment run to a project's run registry."""
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("project", type=Path); p.add_argument("--run-id", required=True)
    p.add_argument("--idea-id"); p.add_argument("--code-commit", required=True); p.add_argument("--data-version", required=True)
    p.add_argument("--config", required=True); p.add_argument("--model"); p.add_argument("--seed", action="append", type=int)
    p.add_argument("--status", choices=("running", "complete", "failed", "superseded"), default="running")
    p.add_argument("--raw-output"); p.add_argument("--summary"); p.add_argument("--failure", action="append", default=[])
    args = p.parse_args(); project = args.project.resolve()
    record = {"run_id": args.run_id, "idea_id": args.idea_id, "code_commit": args.code_commit,
              "data_version": args.data_version, "config": args.config, "model": args.model, "seeds": args.seed or [],
              "raw_outputs": args.raw_output, "summary_results": args.summary, "failure_modes": args.failure,
              "status": args.status, "registered_at_utc": datetime.now(timezone.utc).isoformat()}
    path = project / "09-experiments" / "run-registry.json"; path.parent.mkdir(parents=True, exist_ok=True)
    rows = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    rows = [x for x in rows if x.get("run_id") != args.run_id]; rows.append(record)
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(record, ensure_ascii=False)); return 0


if __name__ == "__main__": raise SystemExit(main())

