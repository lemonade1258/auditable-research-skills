from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
errors = []

for folder in sorted(SKILLS.iterdir()):
    if not folder.is_dir():
        continue
    skill = folder / "SKILL.md"
    if not skill.exists():
        errors.append(f"{folder.name}: missing SKILL.md")
        continue
    text = skill.read_text(encoding="utf-8")
    if not text.startswith("---"):
        errors.append(f"{folder.name}: missing YAML frontmatter")
        continue
    block = text.split("---", 2)[1]
    name = re.search(r"^name:\s*[\"']?([^\"'\n]+)", block, re.M)
    desc = re.search(r"^description:\s*", block, re.M)
    if not name or name.group(1).strip() != folder.name:
        errors.append(f"{folder.name}: frontmatter name must match folder")
    if not desc:
        errors.append(f"{folder.name}: missing description")
    if any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in folder.name):
        errors.append(f"{folder.name}: invalid skill name")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"validated {len([p for p in SKILLS.iterdir() if p.is_dir()])} skills")
