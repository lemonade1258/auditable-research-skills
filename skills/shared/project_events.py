"""Append-only project event log with stable event IDs."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def append_event(project: Path, event_type: str, *, stage: str | None = None,
                 status: str | None = None, details: dict[str, Any] | None = None,
                 actor: str = "human-or-agent") -> dict[str, Any]:
    log = project / "90-logs" / "events.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "event_id": str(uuid.uuid4()),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "stage": stage,
        "status": status,
        "actor": actor,
        "details": details or {},
    }
    with log.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    return event


def read_events(project: Path) -> list[dict[str, Any]]:
    log = project / "90-logs" / "events.jsonl"
    if not log.exists():
        return []
    events: list[dict[str, Any]] = []
    for line_number, line in enumerate(log.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid event at line {line_number}: {exc}") from exc
        if not isinstance(value, dict) or not value.get("event_id"):
            raise ValueError(f"invalid event at line {line_number}")
        events.append(value)
    return events

