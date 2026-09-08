"""Import a validated JSON artifact into a project and record the operation.

Usage:
  python import_artifact.py PROJECT SOURCE.json TARGET.json KIND
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from skills.shared.artifact_contract import validate_records  # noqa: E402
from skills.shared.project_events import append_event  # noqa: E402


def project_path(value: str) -> Path:
    path = Path(value).resolve()
    if not (path / "manifest.json").exists():
        raise argparse.ArgumentTypeError(f"not a research project: {path}")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=project_path)
    parser.add_argument("source", type=Path)
    parser.add_argument("target", help="project-relative destination")
    parser.add_argument("kind", choices=("literature", "evidence", "idea", "claim", "paper_card", "freshness", "run", "transfer"))
    parser.add_argument("--stage", default="artifact")
    args = parser.parse_args()

    source = args.source.resolve(strict=True)
    records = json.loads(source.read_text(encoding="utf-8"))
    errors = validate_records(records, args.kind)
    if errors:
        print("INVALID")
        print("\n".join(f"- {error}" for error in errors))
        return 1

    destination = (args.project / args.target).resolve()
    if args.project not in destination.parents:
        print("INVALID\n- target must remain inside the project")
        return 1
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        existing = destination.read_bytes()
        incoming = source.read_bytes()
        if existing != incoming:
            print(f"CONFLICT\n- refusing to overwrite {destination}")
            return 1
    else:
        destination.write_bytes(source.read_bytes())

    record_count = len(records) if isinstance(records, list) else 1
    append_event(args.project, "artifact.imported", stage=args.stage, status="verified",
                 details={"source": str(source), "target": str(destination.relative_to(args.project)),
                          "kind": args.kind, "records": record_count,
                          "imported_at_utc": datetime.now(timezone.utc).isoformat()})
    print(f"IMPORTED target={destination.relative_to(args.project)} records={record_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
