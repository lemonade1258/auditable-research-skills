"""Normalize public review exports into a venue-neutral reviewer dataset.

Input can be a JSON array or JSONL. It intentionally preserves dataset scope
and does not infer reviewer identities.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path


def load(path: Path):
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".jsonl": return [json.loads(x) for x in text.splitlines() if x.strip()]
    value = json.loads(text); return value if isinstance(value, list) else value.get("records", [])


THEMES = {
    "novelty": ("novel", "novelty", "incremental", "prior work"),
    "evaluation": ("dataset", "benchmark", "evaluation", "split", "leakage"),
    "baselines": ("baseline", "sota", "comparison"),
    "ablations": ("ablation", "remove", "component"),
    "clarity": ("unclear", "clarity", "confusing", "writing"),
    "reproducibility": ("code", "reproduc", "hyperparameter", "seed"),
    "limitations": ("limitation", "weakness", "failure", "cannot"),
    "ethics": ("ethic", "bias", "privacy", "harm"),
}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("input", type=Path); parser.add_argument("output", type=Path)
    parser.add_argument("--venue", required=True); parser.add_argument("--year", type=int); parser.add_argument("--scope-note", required=True)
    args = parser.parse_args(); rows = load(args.input); reviews = []
    for row in rows:
        blob = " ".join(str(row.get(k, "")) for k in ("summary", "strengths", "weaknesses", "questions", "review" )).lower()
        rating = row.get("rating"); match = re.search(r"\d+", str(rating))
        reviews.append({"paper_id": row.get("paper_id") or row.get("id"), "year": row.get("year") or args.year,
                        "venue": args.venue, "decision": row.get("decision"), "rating": int(match.group()) if match else None,
                        "text": blob, "themes": [name for name, words in THEMES.items() if any(word in blob for word in words)]})
    stats = {}
    for theme in THEMES:
        subset = [x for x in reviews if theme in x["themes"]]; papers = {x["paper_id"] for x in subset if x["paper_id"]}
        accepted = {x["paper_id"] for x in subset if str(x.get("decision", "")).lower().startswith("accept")}
        stats[theme] = {"reviews": len(subset), "papers": len(papers), "accepted_papers": len(accepted),
                        "accept_rate": round(len(accepted) / max(1, len(papers)), 3)}
    output = {"schema_version": "1.0", "dataset": str(args.input), "scope_note": args.scope_note,
              "retrieved_at": date.today().isoformat(), "venue": args.venue, "reviews": reviews, "theme_stats": stats}
    args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"reviews": len(reviews), "output": str(args.output)}, ensure_ascii=False)); return 0


if __name__ == "__main__": raise SystemExit(main())

