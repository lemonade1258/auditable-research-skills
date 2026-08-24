# Contributing to Auditable Research Skills

## Before changing a skill

Read the target `SKILL.md`, its directly linked references, and the relevant section of `README.md`. Check whether the change belongs in the core workflow or in a reference file. Keep the core skill short enough to load without flooding the context window.

The repository follows the composable style used by `mattpocock/skills`:

- each skill is a self-contained folder;
- the trigger is expressed in frontmatter `description`;
- the body gives the procedure in imperative language;
- `agents/openai.yaml` contains display metadata only;
- detailed variants live in one-level-deep `references/`;
- deterministic repeated work belongs in `scripts/`;
- user-specific decisions belong in the consuming project, not inside a shared skill.

## Skill structure

```text
skills/<skill-name>/
├── SKILL.md
├── agents/openai.yaml
├── references/       # optional, directly linked from SKILL.md
├── scripts/          # optional, executable and tested
└── assets/           # optional, output resources only
```

Use lowercase hyphenated names, fewer than 64 characters, and make the folder name equal to the frontmatter `name`. Keep one canonical copy: do not add a second nested folder with the same skill name.

## Writing a SKILL.md

The frontmatter must contain only:

```yaml
---
name: example-skill
description: Explain what the skill does and the situations that should trigger it.
---
```

The description is the routing mechanism. Put trigger conditions there, not in a body section that is only loaded after triggering.

The body should make the next agent successful without reproducing general model knowledge. Include:

1. the first action;
2. the ordered workflow;
3. decisions and stopping rules;
4. required outputs;
5. failure conditions and uncertainty handling;
6. direct links to any reference files that may be needed.

Avoid README-like history, release notes, generic motivational text, and duplicated reference material inside a skill.

## Research-specific requirements

For research skill changes:

- start from the research question, not a preferred method;
- use independent search routes and at least three source classes where available;
- preserve rejected near-misses and the reason for rejection;
- separate peer-reviewed authority from recent preprint recency;
- preserve exact source URLs, retrieval date, query, authority reason, and relation to the question;
- never call metadata or abstract-only records “read”;
- require compact or deep cards before synthesis;
- label claims as `author_claim`, `observed_result`, `pipeline_synthesis`, or `unverified_inference`;
- require a freshness check before accepting a gap;
- require an external validation setting and a falsifiable experiment for an idea;
- mark the run `incomplete` when a gate is missing.

## Adding scripts and references

Add a script when the same deterministic operation would otherwise be rewritten or when correctness depends on exact mechanics. Test it on a small fixture and document its command in the relevant skill or README.

Add a reference when the material is useful only for a branch of the workflow. Keep references one level below the skill and link them directly from `SKILL.md`. For a reference longer than 100 lines, add a short table of contents.

Do not commit API keys, private datasets, downloaded full papers, model outputs containing sensitive data, temporary files, or Python caches.

## Validation checklist

Run from the repository root:

```bash
python tests/validate_skills.py
python skills/research-pipeline/scripts/init_research_project.py demo-topic --root /tmp/ars-test
```

If changing research validation logic, also run the validator against a representative fixture. Check that it catches a deliberately incomplete registry as well as accepting a complete fixture.

Review the diff for:

- duplicate skill copies;
- broken relative links;
- stale skill names in `agents/openai.yaml`;
- references not linked from `SKILL.md`;
- claims that no longer have evidence boundaries;
- accidental inclusion of generated artifacts.

## Forward-testing

For a substantial workflow change, use a fresh agent context and a small realistic research question. Pass the raw question and source artifacts, not the intended answer or your diagnosis of the bug. Inspect the emitted artifacts and check whether the agent obeyed the reading-depth and freshness gates.

Do not treat a forward-test as successful because the prose sounds good. Check the registry, paper cards, URLs, evidence labels, counts, and incomplete-state behavior.
