"""Small, dependency-free validators for the cross-skill artifact contract.

The validators intentionally check structure and provenance fields only. They do
not pretend to decide whether a paper is correct or whether an idea is novel.
"""
from __future__ import annotations

from typing import Any, Iterable


STATUS_VALUES = {
    "discovery", "retained", "compact", "deep", "verified", "incomplete",
    "blocked", "superseded", "candidate", "experiment_ready", "validated",
    "rejected",
}
EVIDENCE_LABELS = {
    "author_claim", "observed_result", "pipeline_synthesis", "unverified_inference",
}


def missing(record: dict[str, Any], fields: Iterable[str]) -> list[str]:
    return [field for field in fields if record.get(field) in (None, "", [], {})]


def validate_literature(record: dict[str, Any]) -> list[str]:
    errors = [f"missing {field}" for field in missing(record, (
        "paper_id", "title", "source_url", "discovery_routes", "authority_tier",
        "reading_level", "retrieved_at",
    ))]
    if record.get("reading_level") not in {"metadata", "compact", "deep"}:
        errors.append("reading_level must be metadata|compact|deep")
    if record.get("authority_tier") not in {"A", "B", "C"}:
        errors.append("authority_tier must be A|B|C")
    return errors


def validate_evidence(record: dict[str, Any]) -> list[str]:
    errors = [f"missing {field}" for field in missing(record, (
        "evidence_id", "source_id", "source_location", "evidence_label",
        "verification_status", "retrieved_at",
    ))]
    if record.get("evidence_label") not in EVIDENCE_LABELS:
        errors.append("invalid evidence_label")
    if record.get("verification_status") not in {"unverified", "machine_checked", "human_checked"}:
        errors.append("invalid verification_status")
    return errors


def validate_idea(record: dict[str, Any]) -> list[str]:
    errors = [f"missing {field}" for field in missing(record, (
        "idea_id", "problem", "nearest_work_difference", "hypothesis",
        "falsification_experiment", "external_validation", "explicit_non_goals",
        "status",
    ))]
    if record.get("status") not in {"candidate", "experiment_ready", "validated", "rejected", "blocked"}:
        errors.append("invalid idea status")
    return errors


def validate_claim(record: dict[str, Any]) -> list[str]:
    errors = [f"missing {field}" for field in missing(record, (
        "claim_id", "text", "supporting_evidence", "claim_type", "integrity_status",
    ))]
    if record.get("integrity_status") not in {"verified", "needs-source", "overclaim", "blocked"}:
        errors.append("invalid integrity_status")
    return errors


def validate_records(records: Any, kind: str) -> list[str]:
    if not isinstance(records, list):
        return ["artifact must be a JSON array"]
    validator = {
        "literature": validate_literature,
        "evidence": validate_evidence,
        "idea": validate_idea,
        "claim": validate_claim,
    }.get(kind)
    if validator is None:
        return [f"unknown artifact kind: {kind}"]
    errors: list[str] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"record {index}: must be an object")
            continue
        errors.extend(f"record {index}: {error}" for error in validator(record))
    return errors

