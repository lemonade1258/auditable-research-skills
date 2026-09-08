"""Project-aware OpenAlex collector.

This is a conservative adapter: it records raw route counts and provenance,
does not call a title list "read", and writes all outputs inside one project.
"""
from __future__ import annotations

import argparse
import json
import re
import time
from datetime import date
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen


API = "https://api.openalex.org"
TOP = {"acl", "emnlp", "naacl", "neurips", "icml", "iclr", "kdd", "sigir", "jair", "aaai"}


def get(path: str, params: dict[str, str]) -> dict:
    query = "&".join(f"{quote(str(k))}={quote(str(v))}" for k, v in params.items())
    request = Request(f"{API}{path}?{query}", headers={"User-Agent": "auditable-research-skills/1.0"})
    with urlopen(request, timeout=60) as response:  # noqa: S310 - fixed HTTPS API
        return json.loads(response.read().decode("utf-8"))


def abstract(work: dict) -> str:
    index = work.get("abstract_inverted_index") or {}
    return " ".join(word for _, word in sorted((pos, word) for word, positions in index.items() for pos in positions))


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def record(work: dict, route: str) -> dict:
    location = work.get("primary_location") or {}
    source = location.get("source") or {}
    venue = source.get("display_name") or ""
    tier = "A" if any(marker in venue.lower() for marker in TOP) else ("B" if venue else "C")
    return {
        "paper_id": work.get("id", "").rsplit("/", 1)[-1],
        "openalex_id": work.get("id"),
        "title": work.get("title"),
        "authors": [x.get("author", {}).get("display_name") for x in work.get("authorships", [])[:20]],
        "year": work.get("publication_year"), "venue": venue, "doi": work.get("doi"),
        "source_url": work.get("doi") or work.get("id"), "authority_tier": tier,
        "authority_reason": "venue marker" if tier == "A" else ("indexed venue" if tier == "B" else "other source"),
        "abstract": abstract(work), "cited_by_count": work.get("cited_by_count", 0),
        "discovery_routes": [route], "reading_level": "metadata", "retrieved_at": date.today().isoformat(),
        "inclusion_reason": "discovered via configured route", "exclusion_reason": "",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("--query", action="append", required=True)
    parser.add_argument("--per-query", type=int, default=50)
    args = parser.parse_args()
    project = args.project.resolve()
    if not (project / "manifest.json").exists():
        raise SystemExit(f"not a project: {project}")
    store: dict[str, dict] = {}
    counts: dict[str, int] = {}
    for query in args.query:
        payload = get("/works", {"search": query, "per-page": str(args.per_query)})
        results = payload.get("results", [])
        counts[query] = len(results)
        for work in results:
            item = record(work, f"openalex:search:{query}")
            key = work.get("doi") or normalize(work.get("title") or "")
            if not key:
                continue
            if key in store:
                if item["discovery_routes"][0] not in store[key]["discovery_routes"]:
                    store[key]["discovery_routes"].append(item["discovery_routes"][0])
            else:
                store[key] = item
        time.sleep(0.1)
    records = list(store.values())
    search_dir = project / "02-search"
    search_dir.mkdir(parents=True, exist_ok=True)
    (search_dir / "openalex_search_log.json").write_text(json.dumps({"queries": args.query, "counts": counts, "retrieved_at": date.today().isoformat()}, ensure_ascii=False, indent=2), encoding="utf-8")
    (search_dir / "openalex_discovered.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    registry = project / "03-literature" / "retained_registry.json"
    registry.parent.mkdir(parents=True, exist_ok=True)
    if not registry.exists():
        registry.write_text("[]\n", encoding="utf-8")
    print(json.dumps({"discovered": len(records), "queries": len(args.query), "output": str(search_dir / "openalex_discovered.json")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

