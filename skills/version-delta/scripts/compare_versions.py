"""Compare two versions of a normative artifact and emit an auditable delta map.

The script performs three mechanical steps and one model-assisted step:

1. mechanical  -- segment both versions into comparable units.
2. mechanical  -- align units one-to-one on normalized title similarity.
3. model       -- classify each aligned pair that differs, with a worked example.
4. mechanical  -- validate and write, keeping every model receipt on disk.

Nothing here decides that a change is real. Every delta is written with
``machine_proposed`` status so a person still has to confirm it.

Usage:
  python compare_versions.py PROJECT --old old.txt --new new.txt \
      --old-id v1 --new-id v2 [--model qwen-max] [--dry-run]
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
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


SEGMENT_PATTERNS = (
    # "3.2.1 Title" / "Section 4. Title" / "## Heading" / "Article 12: ..."
    re.compile(r"^\s*(?:section\s+)?(\d+(?:\.\d+)*)[.)]?\s+([^\n]{3,140})$", re.I),
    re.compile(r"^\s*(?:section|article|chapter|clause)\s+(\d+(?:\.\d+)*)[.:)]?\s*([^\n]{3,140})$", re.I),
    re.compile(r"^\s*#{1,6}\s+([^\n]{3,140})$"),
    re.compile(r"^\s*([A-Z][A-Za-z ]{4,80}):\s*([^\n]{3,200})$"),
)

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "for", "on", "with",
    "shall", "must", "should", "may", "be", "is", "are", "by", "at", "from",
    "that", "this", "these", "those", "it", "its", "as", "any", "all",
}


def normalize(text: str) -> str:
    lowered = text.lower()
    words = [w for w in re.split(r"[^a-z0-9一-鿿]+", lowered) if w and w not in STOPWORDS]
    return " ".join(words)


def segment(text: str) -> list[dict]:
    """Split a document into units keyed by heading-like lines."""
    lines = text.splitlines()
    units: list[dict] = []
    current: dict | None = None

    def flush() -> None:
        if current is not None:
            current["text"] = "\n".join(current.pop("_body")).strip()
            if current["text"]:
                units.append(current)

    for number, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if not stripped:
            if current is not None:
                current["_body"].append("")
            continue
        matched = None
        for pattern in SEGMENT_PATTERNS:
            found = pattern.match(stripped)
            if found:
                matched = found
                break
        if matched:
            flush()
            groups = [g.strip() for g in matched.groups() if g and g.strip()]
            label = groups[-1] if groups else stripped
            unit_id = groups[0] if len(groups) > 1 else f"s{number}"
            current = {
                "unit_id": unit_id,
                "title": label,
                "start_line": number,
                "_body": [],
            }
        elif current is not None:
            current["_body"].append(raw)
        else:
            current = {
                "unit_id": f"pre{number}",
                "title": stripped[:140],
                "start_line": number,
                "_body": [raw],
            }
    flush()
    return units


def load_units(path: Path) -> list[dict]:
    """Load comparison units from either a JSON unit file or a plain-text file.

    The JSON form is what ``extract_clauses.py --format json`` produces and is
    the preferred one: it carries explicit unit ids and titles. The text form
    falls back to heading-based segmentation.
    """
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = None
        if isinstance(payload, list) and payload and isinstance(payload[0], dict):
            units = []
            for index, item in enumerate(payload):
                unit_id = str(item.get("unit_id") or item.get("item_number") or index + 1)
                title = str(item.get("topic") or item.get("item_number") or unit_id)
                body = str(item.get("text") or "").strip()
                if not body:
                    continue
                units.append({
                    "unit_id": unit_id,
                    "title": title,
                    "text": body,
                    "kind": item.get("kind", "checklist_item"),
                })
            if units:
                return units
    return segment(text)


def align(old_units: list[dict], new_units: list[dict]) -> tuple[list[dict], list[dict]]:
    """Align units one-to-one.

    Numbered checklists are the trap here. Two editions of a guideline often
    reuse item numbers for *different* topics (PRISMA 2009 item 9 is "Study
    selection"; PRISMA 2020 item 9 is "Data collection process"), so pairing
    by number produces confident nonsense.

    The aligner therefore trusts the unit's *topic/title* first: a pair is
    accepted only when the titles agree closely. Item ids are used as a
    tie-breaker and for reporting, never as the sole basis of a pair. Units
    whose topic genuinely disappears become ``removed``; units with no
    counterpart become ``added``.
    """
    pairs: list[dict] = []
    used_new: set[int] = set()

    # Pass 1: pair on title similarity. Highest-confidence pairs first so a
    # strong match is not stolen by a weaker one.
    scored: list[tuple[float, int, int]] = []
    for old_index, old in enumerate(old_units):
        old_key = normalize(old["title"])
        for new_index, new in enumerate(new_units):
            score = difflib.SequenceMatcher(None, old_key, normalize(new["title"])).ratio()
            if score >= 0.72:
                scored.append((score, old_index, new_index))

    scored.sort(key=lambda t: (-t[0], t[1], t[2]))

    # Greedy assignment, but a pair is only kept when it is the best remaining
    # option on BOTH sides, which avoids a strong title being matched to a
    # second candidate that is itself a better match for something else.
    best_for_old: dict[int, tuple[float, int]] = {}
    best_for_new: dict[int, tuple[float, int]] = {}
    for score, old_index, new_index in scored:
        if old_index not in best_for_old or score > best_for_old[old_index][0]:
            best_for_old[old_index] = (score, new_index)
        if new_index not in best_for_new or score > best_for_new[new_index][0]:
            best_for_new[new_index] = (score, old_index)

    old_paired: dict[int, int] = {}
    new_paired: dict[int, int] = {}
    for old_index, (score, new_index) in best_for_old.items():
        reciprocal = best_for_new.get(new_index)
        if reciprocal is None or reciprocal[1] != old_index:
            continue
        old_paired[old_index] = new_index
        new_paired[new_index] = old_index

    for old_index, old in enumerate(old_units):
        new_index = old_paired.get(old_index)
        if new_index is None:
            pairs.append({
                "old_unit_id": old["unit_id"],
                "new_unit_id": None,
                "old_title": old["title"],
                "new_title": None,
                "alignment": "removed",
                "similarity": 0.0,
                "aligned_by": "title_similarity",
            })
            continue
        new = new_units[new_index]
        pairs.append({
            "old_unit_id": old["unit_id"],
            "new_unit_id": new["unit_id"],
            "old_title": old["title"],
            "new_title": new["title"],
            "alignment": "matched",
            "similarity": round(best_for_old[old_index][0], 3),
            "aligned_by": "title_similarity",
        })

    for new_index, new in enumerate(new_units):
        if new_index not in new_paired:
            pairs.append({
                "old_unit_id": None,
                "new_unit_id": new["unit_id"],
                "old_title": None,
                "new_title": new["title"],
                "alignment": "added",
                "similarity": 0.0,
                "aligned_by": "title_similarity",
            })

    return pairs, [old_units, new_units]


def find_unit(units: list[dict], unit_id: str | None) -> dict | None:
    if unit_id is None:
        return None
    for unit in units:
        if unit["unit_id"] == unit_id:
            return unit
    return None


CLASSIFY_SYSTEM = """You compare two versions of a normative document and classify differences.

Rules you must follow:
- Classify only what is written in the provided passages. Never infer intent.
- Every difference must get exactly one change_type from: field_added, field_removed,
  field_renamed, semantic_shift, scope_narrowed, scope_broadened, requirement_added,
  requirement_removed.
- Use field_renamed only when the meaning is identical and only the label changed.
- Use semantic_shift when the same words carry a different operational meaning. You MUST
  give a concrete worked example: one concrete case that means X under the old version and
  means Y under the new version.
- impact_level is high when prior conclusions or compliance status change; medium when the
  protocol changes but the answer to an existing question does not; low for wording only.
- resolution_requirement states what evidence a downstream claim must now carry. Empty
  string is allowed only when impact_level is low.
- uncertainty must be 'low', 'medium' or 'high'. If you are unsure whether the change is
  semantic or cosmetic, say 'high'.
- Return ONLY a JSON array. No prose, no code fence."""

CLASSIFY_USER = """Compare this aligned pair of clauses.

OLD VERSION ({old_id}) - unit {old_unit_id}: {old_title}
{old_text}

NEW VERSION ({new_id}) - unit {new_unit_id}: {new_title}
{new_text}

If the two passages say the same thing in different words, still return one record with
change_type field_renamed and impact_level low. Return a JSON array with exactly one
object having these keys:
delta_id, change_type, impact_level, interpretation, worked_example, impact_summary,
resolution_requirement, uncertainty, old_excerpt, new_excerpt"""


def classify_batch(batch: list[dict], old_id: str, new_id: str, config: LLMConfig) -> tuple[list[dict], object]:
    """Classify a batch of aligned pairs with one model call."""
    parts = []
    for item in batch:
        parts.append(CLASSIFY_USER.format(
            old_id=old_id,
            new_id=new_id,
            old_unit_id=item["old_unit_id"] or "-",
            new_unit_id=item["new_unit_id"] or "-",
            old_title=item["old_title"] or "-",
            new_title=item["new_title"] or "-",
            old_text=item["old_text"][:6000],
            new_text=item["new_text"][:6000],
        ))
    payload, result = chat_json(
        [{"role": "user", "content": "\n\n====\n\n".join(parts)}],
        config,
        system=CLASSIFY_SYSTEM,
    )
    if isinstance(payload, dict):
        payload = [payload]
    return payload, result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("--old", type=Path, required=True)
    parser.add_argument("--new", type=Path, required=True)
    parser.add_argument("--old-id", required=True)
    parser.add_argument("--new-id", required=True)
    parser.add_argument("--model")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    project = args.project.resolve()
    if not (project / "manifest.json").exists():
        raise SystemExit(f"not a research project: {project}")

    old_text = args.old.read_text(encoding="utf-8")
    new_text = args.new.read_text(encoding="utf-8")
    old_units = load_units(args.old)
    new_units = load_units(args.new)
    pairs, _ = align(old_units, new_units)

    # Only pairs whose text actually differs are worth a model call.
    candidates: list[dict] = []
    for pair in pairs:
        old_unit = find_unit(old_units, pair["old_unit_id"])
        new_unit = find_unit(new_units, pair["new_unit_id"])
        pair["old_text"] = old_unit["text"] if old_unit else ""
        pair["new_text"] = new_unit["text"] if new_unit else ""
        if pair["old_text"].strip() != pair["new_text"].strip():
            candidates.append(pair)

    out_dir = project / "02-versions"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "segmentation.json").write_text(json.dumps({
        "old_version": {"id": args.old_id, "source": str(args.old), "units": old_units},
        "new_version": {"id": args.new_id, "source": str(args.new), "units": new_units},
        "retrieved_at": date.today().isoformat(),
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "old_units": len(old_units), "new_units": len(new_units),
        "aligned_pairs": len(pairs), "differing_pairs": len(candidates),
    }, ensure_ascii=False))

    if args.dry_run:
        (out_dir / "alignment-preview.json").write_text(
            json.dumps(pairs, ensure_ascii=False, indent=2), encoding="utf-8")
        return 0

    try:
        config = resolve_config({"model": args.model} if args.model else None)
    except LLMUnavailable as exc:
        raise SystemExit(str(exc))

    deltas: list[dict] = []
    receipts_dir = out_dir / "diff-receipts"
    for start in range(0, len(candidates), args.batch_size):
        batch = candidates[start : start + args.batch_size]
        if not batch:
            continue
        raw, result = classify_batch(batch, args.old_id, args.new_id, config)
        write_receipt(
            receipts_dir / f"batch-{start // args.batch_size + 1:03d}.json",
            raw, result,
            purpose="version-delta.classify",
            extra={"old_id": args.old_id, "new_id": args.new_id,
                   "pair_keys": [p["old_unit_id"] for p in batch]},
        )
        for offset, record in enumerate(raw):
            pair = batch[min(offset, len(batch) - 1)]
            deltas.append({
                "delta_id": record.get("delta_id") or f"D{start + offset + 1:04d}",
                "source_version": args.old_id,
                "target_version": args.new_id,
                "change_type": record.get("change_type", "semantic_shift"),
                "impact_level": record.get("impact_level", "medium"),
                "interpretation": record.get("interpretation", ""),
                "worked_example": record.get("worked_example", ""),
                "impact_summary": record.get("impact_summary", ""),
                "resolution_requirement": record.get("resolution_requirement", ""),
                "uncertainty": record.get("uncertainty", "medium"),
                "old_unit_id": pair["old_unit_id"],
                "new_unit_id": pair["new_unit_id"],
                "old_excerpt": record.get("old_excerpt", ""),
                "new_excerpt": record.get("new_excerpt", ""),
                "source_location": f"{args.old_id}:{pair['old_unit_id']} -> {args.new_id}:{pair['new_unit_id']}",
                "verification_status": "machine_proposed",
                "reviewed_at": date.today().isoformat(),
            })
        time.sleep(0.2)

    errors = validate_records(deltas, "delta")
    (out_dir / "delta-map.json").write_text(
        json.dumps(deltas, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "deltas": len(deltas),
        "contract_errors": len(errors),
        "output": str(out_dir / "delta-map.json"),
    }, ensure_ascii=False))
    if errors:
        print("\n".join(errors[:20]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
