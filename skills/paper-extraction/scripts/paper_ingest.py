"""Ingest a PDF into a project and create a paper-card scaffold.

Text extraction is deterministic when `pdftotext` is available. The scaffold
leaves interpretation fields empty rather than pretending an abstract parse is
a deep read.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import date
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--level", choices=("compact", "deep"), default="compact")
    args = parser.parse_args()
    project = args.project.resolve(); source = args.pdf.resolve(strict=True)
    destination = project / "03-literature" / "papers" / f"{args.paper_id}.pdf"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        shutil.copy2(source, destination)
    text_path = destination.with_suffix(".txt")
    try:
        text = subprocess.check_output(["pdftotext", "-layout", str(destination), "-"], text=True, encoding="utf-8", errors="replace")
    except (FileNotFoundError, subprocess.CalledProcessError):
        text = ""
    text_path.write_text(text, encoding="utf-8")
    card = {
        "paper_id": args.paper_id, "reading_level": args.level, "source_pdf": str(destination.relative_to(project)),
        "text_extract": str(text_path.relative_to(project)), "retrieved_at": date.today().isoformat(),
        "motivation": "", "method": "", "contribution": "", "insight": "",
        "data_evaluation": "", "observed_result": "", "not_established": "", "limitations": "",
        "source_quotes": [], "status": "incomplete" if not text else "needs-human-reading",
    }
    cards = project / "03-literature" / "paper-cards"; cards.mkdir(parents=True, exist_ok=True)
    (cards / f"{args.paper_id}.json").write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"paper_id": args.paper_id, "pdf": str(destination), "text_chars": len(text), "card": str(cards / f"{args.paper_id}.json")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

