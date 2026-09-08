"""Create a fact-first patent/technical-transfer case file.

This adapter deliberately creates a structured intake/disclosure scaffold. It
does not infer patentability, novelty, inventorship, or legal conclusions.
"""
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("project", type=Path); p.add_argument("--case-id", required=True)
    p.add_argument("--mode", choices=("disclosure", "application", "docket"), default="disclosure")
    p.add_argument("--fact", action="append", default=[]); p.add_argument("--question", action="append", default=[])
    p.add_argument("--source", action="append", default=[]); p.add_argument("--max-rounds", type=int, default=3)
    args = p.parse_args(); project = args.project.resolve()
    case = {"case_id": args.case_id, "mode": args.mode, "status": "questions" if args.question else "intake",
            "created_at_utc": datetime.now(timezone.utc).isoformat(), "max_rounds": args.max_rounds,
            "round": 0, "technical_facts": args.fact, "open_questions": args.question, "source_materials": args.source,
            "patentability": "not_assessed", "inventorship": "requires_human_confirmation",
            "outputs": [], "guardrails": ["do not infer missing technical facts", "do not certify novelty", "keep disclosure and application separate"]}
    output = project / "12-transfer" / args.case_id / "case.json"; output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(case, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.mode == "disclosure":
        (output.parent / "disclosure-draft.md").write_text(
            "# 技术交底书草稿\n\n## 技术事实\n\n" + "\n".join(f"- {x}" for x in args.fact) +
            "\n\n## 待发明人确认\n\n" + "\n".join(f"- {x}" for x in args.question) +
            "\n\n## 禁止自动结论\n\n专利新颖性、创造性、保护范围和发明人信息需由专业人员与发明人确认。\n", encoding="utf-8")
    print(json.dumps({"case_id": args.case_id, "mode": args.mode, "status": case["status"], "output": str(output)}, ensure_ascii=False)); return 0


if __name__ == "__main__": raise SystemExit(main())

