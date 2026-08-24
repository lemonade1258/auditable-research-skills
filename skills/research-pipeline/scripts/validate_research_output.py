"""Validate evidence, reading depth, freshness, and report coverage.

Usage: python validate_research_output.py registry.json report.md
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


def present(record: dict, field: str) -> bool:
    value = record.get(field)
    return value not in (None, "", [], {})


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: validate_research_output.py registry.json report.md")
        return 2

    records = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    report = Path(sys.argv[2]).read_text(encoding="utf-8").lower()
    if not isinstance(records, list):
        print("INVALID\n- registry must be a JSON array")
        return 1

    errors: list[str] = []
    if len(records) < 60:
        errors.append(f"retained records={len(records)}; need at least 60")

    tiers = Counter(record.get("authority_tier") for record in records)
    if tiers["A"] < 8:
        errors.append(f"tier-A records={tiers['A']}; need at least 8")

    anchors = {record.get("paper_id") for record in records if record.get("is_anchor")}
    anchors.discard(None)
    if len(anchors) < 8:
        errors.append(f"independent anchors={len(anchors)}; need at least 8")

    reading = Counter(record.get("reading_level", "metadata") for record in records)
    if reading["compact"] + reading["deep"] < 20:
        errors.append("need at least 20 compact-or-deep paper reads")
    if reading["deep"] < 8:
        errors.append("need at least 8 deep reads for core/nearest papers")

    explained = [
        record for record in records
        if record.get("reading_level") in {"compact", "deep"}
        and present(record, "plain_language_summary")
        and all(present(record, field) for field in ("motivation", "method", "contribution", "insight"))
    ]
    if len(explained) < 20:
        errors.append(f"complete paper explanation cards={len(explained)}; need at least 20")

    required_groups = {
        "question map": ["question map", "问题地图", "研究问题"],
        "search protocol": ["search protocol", "检索方案", "检索记录"],
        "author/lab tracing": ["author trajectory", "lab trajectory", "作者轨迹", "实验室轨迹"],
        "related work": ["related work", "相关工作"],
        "paper understanding": ["paper card", "论文卡", "论文说明"],
        "reviewer taste": ["reviewer taste", "科研品味", "研究品味"],
        "freshness": ["freshness", "当前缺口复核", "实时性复核"],
        "nearest prior": ["nearest prior", "最近工作", "近邻工作"],
        "falsification": ["falsification", "证伪", "推翻"],
        "external validation": ["external validation", "外部验证", "跨数据"],
        "scope": ["scope", "范围", "不做什么"],
    }
    for label, alternatives in required_groups.items():
        if not any(phrase in report for phrase in alternatives):
            errors.append(f"report missing section/evidence: {label}")

    if errors:
        print("INVALID")
        print("\n".join(f"- {error}" for error in errors))
        return 1

    print(
        "VALID "
        f"records={len(records)} tier_a={tiers['A']} anchors={len(anchors)} "
        f"compact={reading['compact']} deep={reading['deep']} cards={len(explained)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
