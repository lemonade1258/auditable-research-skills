"""Project controller for auditable research runs.

Examples:
  python projectctl.py init my-topic --root projects --question "..."
  python projectctl.py event projects/my-topic --type search.completed --stage discovery
  python projectctl.py status projects/my-topic
  python projectctl.py gate projects/my-topic discovery
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SCRIPT_ROOT))

from skills.shared.artifact_contract import validate_records  # noqa: E402
from skills.shared.project_events import append_event, read_events  # noqa: E402


DIRS = (
    "00-input", "01-question-map", "02-search", "03-literature/papers",
    "03-literature/paper-cards", "04-evidence-map", "05-reviewer-taste",
    "06-ideas", "07-discussion", "09-experiments", "10-manuscript",
    "11-reviews", "12-transfer", "90-logs", "91-releases", "99-temp",
)
STAGES = {
    "intake": ("manifest.json", "00-input"),
    "question": ("01-question-map/question-map.md",),
    "discovery": ("02-search/search-protocol.md", "02-search/coverage-ledger.json"),
    "reading": ("03-literature/retained_registry.json", "03-literature/paper-cards"),
    "evidence": ("04-evidence-map/evidence-matrix.json",),
    "freshness": ("06-ideas/freshness-ledger.json",),
    "idea": ("06-ideas/candidates.json",),
    "experiment": ("09-experiments/run-registry.json",),
    "manuscript": ("10-manuscript/claim-ledger.json",),
    "release": ("91-releases/release-audit.json",),
}


def slug(value: str) -> str:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,62}", value):
        raise argparse.ArgumentTypeError("slug must use 2-63 lowercase letters, digits, or hyphens")
    return value


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def init(args: argparse.Namespace) -> int:
    project = (args.root / args.slug).resolve()
    project.mkdir(parents=True, exist_ok=True)
    for relative in DIRS:
        (project / relative).mkdir(parents=True, exist_ok=True)
    manifest_path = project / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {
            "schema_version": "1.0",
            "project_slug": args.slug,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "updated_at_utc": None,
            "status": "initialized",
            "current_stage": "intake",
            "question": args.question,
            "domain": args.domain,
            "target_venues": args.venue,
            "literature_cutoff": args.cutoff,
            "inputs": [],
            "stage_status": {stage: "not_started" for stage in STAGES},
        }
    copied = list(manifest.get("inputs", []))
    for source in args.source:
        resolved = source.resolve(strict=True)
        target = project / "00-input" / resolved.name
        if target.exists() and target.read_bytes() != resolved.read_bytes():
            raise FileExistsError(f"refusing to overwrite different input: {target}")
        if not target.exists():
            shutil.copy2(resolved, target)
        item = {"source": str(resolved), "copy": str(target)}
        if item not in copied:
            copied.append(item)
    manifest["inputs"] = copied
    manifest["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    write_json(manifest_path, manifest)
    append_event(project, "project.initialized", stage="intake", status="initialized",
                 details={"question": args.question, "inputs": len(copied)})
    print(project)
    return 0


def project_path(value: str) -> Path:
    path = Path(value).resolve()
    if not (path / "manifest.json").exists():
        raise argparse.ArgumentTypeError(f"not a research project: {path}")
    return path


def event(args: argparse.Namespace) -> int:
    details = json.loads(args.details) if args.details else {}
    item = append_event(args.project, args.event_type, stage=args.stage,
                        status=args.status, details=details, actor=args.actor)
    print(json.dumps(item, ensure_ascii=False))
    return 0


def status(args: argparse.Namespace) -> int:
    manifest = json.loads((args.project / "manifest.json").read_text(encoding="utf-8"))
    events = read_events(args.project)
    output = {"manifest": manifest, "events": len(events), "last_event": events[-1] if events else None}
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


def gate(args: argparse.Namespace) -> int:
    required = STAGES[args.stage]
    missing = [item for item in required if not (args.project / item).exists()]
    manifest = json.loads((args.project / "manifest.json").read_text(encoding="utf-8"))
    if missing:
        print("BLOCKED")
        print(json.dumps({"stage": args.stage, "missing": missing}, ensure_ascii=False, indent=2))
        return 1
    manifest.setdefault("stage_status", {})[args.stage] = "passed"
    manifest["current_stage"] = args.stage
    manifest["status"] = "in_progress"
    manifest["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    write_json(args.project / "manifest.json", manifest)
    append_event(args.project, "stage.gate_passed", stage=args.stage, status="passed")
    print(f"PASSED stage={args.stage}")
    return 0


def validate(args: argparse.Namespace) -> int:
    errors: list[str] = []
    manifest_path = args.project / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"manifest: {exc}")
        manifest = {}
    for field in ("schema_version", "project_slug", "created_at_utc", "stage_status"):
        if not manifest.get(field):
            errors.append(f"manifest missing {field}")
    for path, kind in args.artifact:
        artifact_path = args.project / path
        try:
            records = json.loads(artifact_path.read_text(encoding="utf-8"))
            errors.extend(f"{path}: {error}" for error in validate_records(records, kind))
        except Exception as exc:
            errors.append(f"{path}: {exc}")
    try:
        read_events(args.project)
    except ValueError as exc:
        errors.append(str(exc))
    if errors:
        print("INVALID")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("VALID project=" + str(args.project))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    init_parser = sub.add_parser("init")
    init_parser.add_argument("slug", type=slug)
    init_parser.add_argument("--root", type=Path, default=Path("projects"))
    init_parser.add_argument("--source", type=Path, action="append", default=[])
    init_parser.add_argument("--question", default=None)
    init_parser.add_argument("--domain", default=None)
    init_parser.add_argument("--venue", action="append", default=[])
    init_parser.add_argument("--cutoff", default=None)
    init_parser.set_defaults(func=init)

    event_parser = sub.add_parser("event")
    event_parser.add_argument("project", type=project_path)
    event_parser.add_argument("--type", dest="event_type", required=True)
    event_parser.add_argument("--stage")
    event_parser.add_argument("--status")
    event_parser.add_argument("--actor", default="human-or-agent")
    event_parser.add_argument("--details")
    event_parser.set_defaults(func=event)

    for name, func in (("status", status), ("gate", gate), ("validate", validate)):
        command = sub.add_parser(name)
        command.add_argument("project", type=project_path)
        if name == "gate":
            command.add_argument("stage", choices=sorted(STAGES))
        if name == "validate":
            command.add_argument("--artifact", nargs=2, action="append", metavar=("PATH", "KIND"), default=[])
        command.set_defaults(func=func)
    return args_func(parser)


def args_func(parser: argparse.ArgumentParser) -> int:
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

