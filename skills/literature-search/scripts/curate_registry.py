"""Curate an OpenAlex discovery file into retained and rejected registries."""
from __future__ import annotations
import argparse, json, re
from collections import defaultdict
from pathlib import Path

TERMS = {
    "task": ("benchmark", "dataset", "task", "evaluation"),
    "method": ("retrieval", "reasoning", "model", "learning", "generation"),
    "evidence": ("citation", "attribution", "factual", "verification", "grounding", "evidence"),
    "application": ("finance", "legal", "medical", "regulat", "audit", "compliance"),
}


def norm(text: str) -> str: return re.sub(r"[^a-z0-9]+", " ", (text or "").lower())


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("input", type=Path); p.add_argument("project", type=Path)
    p.add_argument("--keep", type=int, default=140); p.add_argument("--keyword", action="append", default=[])
    args = p.parse_args(); records = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(records, list): raise SystemExit("input must be a JSON array")
    ranked = []
    for item in records:
        text = norm(f"{item.get('title', '')} {item.get('abstract', '')}")
        categories = [name for name, words in TERMS.items() if any(word in text for word in words)]
        keyword_bonus = sum(text.count(norm(word)) for word in args.keyword)
        score = 6 * len(categories) + 4 * len(item.get("anchor_ids", [])) + keyword_bonus
        score += min(int(item.get("cited_by_count", 0)), 500) ** 0.5
        score += 3 if int(item.get("year") or 0) >= 2023 else 0
        item["categories"] = categories; item["curation_score"] = round(score, 3)
        ranked.append(item)
    ranked.sort(key=lambda x: (x.get("authority_tier") != "A", -x["curation_score"], -int(x.get("cited_by_count", 0))))
    retained = ranked[:args.keep]; retained_ids = {x.get("paper_id") for x in retained}
    for item in retained:
        item["retained"] = True; item.setdefault("inclusion_reason", "authority/relevance score")
    rejected = []
    for item in ranked[args.keep:]:
        item["retained"] = False; item["exclusion_reason"] = "lower authority or relevance score"; rejected.append(item)
    out = args.project.resolve() / "03-literature"; out.mkdir(parents=True, exist_ok=True)
    (out / "retained_registry.json").write_text(json.dumps(retained, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "rejected_registry.json").write_text(json.dumps(rejected, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "anchors.json").write_text(json.dumps([x for x in retained if x.get("is_anchor") or "anchor" in str(x.get("discovery_routes"))], ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"input": len(records), "retained": len(retained), "rejected": len(rejected), "output": str(out)}, ensure_ascii=False)); return 0


if __name__ == "__main__": raise SystemExit(main())

