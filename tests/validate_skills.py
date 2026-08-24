from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
errors = []
skill_dirs = sorted(p for p in SKILLS.iterdir() if p.is_dir() and p.name != "__pycache__")

if not SKILLS.exists():
    errors.append("missing skills/ directory")

expected = {
    "citation-tracing",
    "idea-mining",
    "literature-search",
    "paper-extraction",
    "research-pipeline",
    "reviewer-profile",
}
actual = {p.name for p in skill_dirs}
for missing in sorted(expected - actual):
    errors.append(f"missing canonical skill directory: {missing}")

for folder in skill_dirs:
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

    metadata = folder / "agents" / "openai.yaml"
    if not metadata.exists():
        errors.append(f"{folder.name}: missing agents/openai.yaml")

    # Catch broken local links before a release.
    for target in re.findall(r"\]\(([^)]+)\)", text):
        if target.startswith(("http://", "https://", "#")):
            continue
        link = (skill.parent / target).resolve()
        if not link.exists():
            errors.append(f"{folder.name}: broken local link {target}")

readme = ROOT / "README.md"
if readme.exists():
    readme_text = readme.read_text(encoding="utf-8")
    for skill_name in sorted(expected):
        if f"`{skill_name}`" not in readme_text:
            errors.append(f"README.md: missing skill {skill_name}")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"validated {len(skill_dirs)} skills")
