"""Extract reporting-guideline checklist items from PMC article XML.

The extractor targets the main checklist table (usually Table 1) and emits
one unit per checklist item (e.g., item 1, 1a, 1b, 2, 2a, etc.) so the
version-delta script can align and compare two editions of the same guideline.

Usage:
  python extract_clauses.py article.xml --out clauses.txt [--format text|json]
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET


def clean_text(node: ET.Element) -> str:
    """Extract text from an XML node, stripping tags."""
    parts: list[str] = []
    if node.text:
        parts.append(node.text)
    for child in node:
        parts.append(clean_text(child))
        if child.tail:
            parts.append(child.tail)
    text = "".join(parts)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("xml", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    tree = ET.parse(args.xml)
    root = tree.getroot()

    units: list[dict] = []
    item_pattern = re.compile(r"^(\d{1,2}[a-z]?)$", re.I)

    # Extract only from the first table-wrap (usually the main checklist).
    for tw in root.findall(".//table-wrap"):
        caption = tw.find("caption")
        table_label = clean_text(caption) if caption is not None else ""

        table = tw.find(".//table")
        if table is None:
            continue

        for row in table.findall(".//tr"):
            cells = row.findall("./td") or row.findall("./th")
            if len(cells) < 3:
                continue

            # Column layout is: section/topic | item number | checklist text |
            # (optional) location. The item number lives in column 2.
            topic = clean_text(cells[0]).strip()
            head = clean_text(cells[1]).strip()
            body = clean_text(cells[2]).strip()

            if not body or not head:
                continue

            # Match item numbers like "1", "1a", "10b", etc.
            if item_pattern.fullmatch(head):
                units.append({
                    "unit_id": f"item-{head.lower()}",
                    "item_number": head,
                    "topic": topic,
                    "text": body,
                    "table": table_label,
                })
            elif units:
                # Continuation: append to the last item.
                if body:
                    units[-1]["text"] += f" {body}"

        # Only process the first checklist table.
        if units:
            break

    if args.format == "json":
        args.out.write_text(
            json.dumps(units, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    else:
        parts = [f"# {u['item_number']}\n{u['text']}\n" for u in units]
        args.out.write_text("".join(parts), encoding="utf-8")

    print(
        json.dumps(
            {
                "units": len(units),
                "out": str(args.out),
                "first_item": units[0]["unit_id"] if units else None,
                "last_item": units[-1]["unit_id"] if units else None,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
