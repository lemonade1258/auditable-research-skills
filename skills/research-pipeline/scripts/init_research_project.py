"""Create an isolated research-project artifact tree and optional input copies."""
from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


DIRS = (
    "00-input",
    "01-question-map",
    "02-search",
    "03-literature/papers",
    "03-literature/paper-cards",
    "04-evidence-map",
    "05-reviewer-taste",
    "06-ideas",
    "07-discussion",
    "90-logs",
    "99-temp",
)


def valid_slug(value: str) -> str:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,62}", value):
        raise argparse.ArgumentTypeError("slug must use 2-63 lowercase letters, digits, or hyphens")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("slug", type=valid_slug)
    parser.add_argument("--root", type=Path, default=Path("projects"))
    parser.add_argument("--source", type=Path, action="append", default=[])
    args = parser.parse_args()

    project = (args.root / args.slug).resolve()
    project.mkdir(parents=True, exist_ok=True)
    for relative in DIRS:
        (project / relative).mkdir(parents=True, exist_ok=True)

    manifest_path = project / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        copied = list(manifest.get("inputs", []))
    else:
        manifest = {
            "project_slug": args.slug,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "inputs": [],
            "literature_cutoff": None,
            "status": "initialized",
        }
        copied = []

    for source in args.source:
        resolved = source.resolve(strict=True)
        target = project / "00-input" / resolved.name
        item = {"source": str(resolved), "copy": str(target)}
        if target.exists():
            if target.read_bytes() != resolved.read_bytes():
                raise FileExistsError(f"refusing to overwrite different input: {target}")
            if item not in copied:
                copied.append(item)
            continue
        shutil.copy2(resolved, target)
        if item not in copied:
            copied.append(item)

    manifest["inputs"] = copied
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(project)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
