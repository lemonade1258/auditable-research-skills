import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/research-pipeline/scripts/projectctl.py"


def run(*args, cwd=ROOT):
    return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=cwd,
                          text=True, capture_output=True, check=False)


def test_init_event_gate_and_validate(tmp_path):
    result = run("init", "demo-project", "--root", str(tmp_path), "--question", "Does X work?")
    assert result.returncode == 0, result.stderr
    project = tmp_path / "demo-project"
    manifest = json.loads((project / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "1.0"
    event = run("event", str(project), "--type", "question.created", "--stage", "question")
    assert event.returncode == 0, event.stderr
    (project / "01-question-map" / "question-map.md").write_text("# Question map\n", encoding="utf-8")
    gate = run("gate", str(project), "question")
    assert gate.returncode == 0, gate.stdout
    valid = run("validate", str(project))
    assert valid.returncode == 0, valid.stdout


def test_gate_reports_missing_artifacts(tmp_path):
    result = run("init", "demo-project", "--root", str(tmp_path))
    assert result.returncode == 0
    project = tmp_path / "demo-project"
    gate = run("gate", str(project), "discovery")
    assert gate.returncode == 1
    assert "coverage-ledger.json" in gate.stdout


def test_import_artifact_validates_and_refuses_conflicts(tmp_path):
    result = run("init", "demo-project", "--root", str(tmp_path))
    assert result.returncode == 0
    project = tmp_path / "demo-project"
    source = tmp_path / "papers.json"
    source.write_text(json.dumps([{
        "paper_id": "p1", "title": "Paper", "source_url": "https://example.org/p",
        "discovery_routes": ["direct"], "authority_tier": "A",
        "reading_level": "metadata", "retrieved_at": "2026-09-08"
    }]), encoding="utf-8")
    imported = subprocess.run([
        sys.executable, str(ROOT / "skills/research-pipeline/scripts/import_artifact.py"),
        str(project), str(source), "03-literature/retained_registry.json", "literature"
    ], cwd=ROOT, text=True, capture_output=True)
    assert imported.returncode == 0, imported.stdout + imported.stderr
    source.write_text("[]", encoding="utf-8")
    conflict = subprocess.run([
        sys.executable, str(ROOT / "skills/research-pipeline/scripts/import_artifact.py"),
        str(project), str(source), "03-literature/retained_registry.json", "literature"
    ], cwd=ROOT, text=True, capture_output=True)
    assert conflict.returncode == 1
    assert "CONFLICT" in conflict.stdout
