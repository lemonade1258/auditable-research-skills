# Auditable Research Skills

Reusable skills for taking a research question from broad discovery to a defensible, current, and testable research direction.

这套 skill 解决的是一个很具体的问题：直接问模型“这个方向有没有人做过、还能做什么”时，回答往往只覆盖熟悉论文，混淆论文贡献与方法，忽略引用链和近期工作，并在证据不足时过早提出“新颖想法”。本仓库把这件事拆成可复跑、可检查的研究环节：广泛检索、引用扩展、论文解析、证据归纳、科研品味、近期缺口复核和小规模 idea 挖掘。

## What this repository provides

The repository contains six composable skills. `research-pipeline` is the coordinator; the other five skills are independently usable components.

| Skill | Responsibility | Main output |
|---|---|---|
| `research-pipeline` | Run the complete investigation and enforce stage gates | A dated research project with all required artifacts |
| `literature-search` | Search independent routes and preserve authority decisions and near-misses | Search protocol, anchors, registry, coverage ledger |
| `citation-tracing` | Expand every anchor through references, cited-by, related work, datasets, authors, and labs | Auditable literature graph and branch ledger |
| `paper-extraction` | Read papers at explicit depths and compare claims with evidence | Paper cards and evidence-backed reading notes |
| `reviewer-profile` | Analyze public venue-level research taste separately from generic paper advice | Time-aware reviewer-taste brief |
| `idea-mining` | Derive small candidates only after literature and freshness gates pass | Candidate ideas, nearest-work checks, falsification plans |

## How the pieces fit

```text
research question
      |
      v
research-pipeline ──> question map and scope
      |
      +── literature-search ──> broad discovery, anchors, near-misses
      |
      +── citation-tracing ──> per-anchor citation and author/lab graph
      |
      +── paper-extraction ──> compact/deep paper cards and evidence
      |
      +── evidence map ──> what each line of work actually establishes
      |
      +── reviewer-profile ──> venue taste and execution risks
      |
      +── freshness gate ──> current nearest-work check
      |
      +── idea-mining ──> small, falsifiable candidates and external validation
```

The arrows are gates, not suggestions. A title list cannot substitute for paper extraction. A model-memory gap cannot substitute for a freshness check. An idea cannot pass while its nearest work is metadata-only.

## Installation

### Install the complete package with `skills.sh`

```bash
npx skills@latest add lemonade1258/auditable-research-skills --skill '*' --agent '*' --copy
```

### Install selected skills

```bash
npx skills@latest add lemonade1258/auditable-research-skills \
  --skill research-pipeline \
  --skill literature-search \
  --skill citation-tracing \
  --agent codex --copy
```

The repository follows the same project-local, editable-file philosophy used by `mattpocock/skills`: skills are ordinary files in the project, UI metadata lives in `agents/openai.yaml`, and the lock/install tool can be used to update them later.

### Use from a local checkout

Each skill is available at `skills/<skill-name>/SKILL.md`. The folder can be copied into an agent's skill directory or installed with the command above.

## Which skill should I use?

Use `research-pipeline` when the request is broad and the result must be defensible: “investigate this topic”, “find a research gap”, “help us choose a paper idea”, or “map the field”.

Use `literature-search` when discovery is the task and no synthesis is needed yet.

Use `citation-tracing` when you already have anchor papers and need to follow their intellectual neighborhoods rather than collect another keyword list.

Use `paper-extraction` when the question is “what does this paper actually do, find, assume, or fail to establish?”.

Use `reviewer-profile` when venue taste, accepted-paper movement, public reviews, or likely reviewer objections matter.

Use `idea-mining` only after a verified literature map and current-gap check exist.

## The research contract

Every serious run should answer these questions:

1. What exactly is the question, and which competing explanations are plausible?
2. Which independent research lines were searched?
3. Which sources are authoritative, and why?
4. What did each important paper try to solve, build, measure, and establish?
5. What did the papers not establish?
6. What changed after citation, author/lab, and recent-work tracing?
7. Is the claimed gap still open as of the dated cutoff?
8. What is the smallest experiment that could falsify the candidate idea?
9. What validation setting is independent of the project's private benchmark?

If a required answer is missing, the report must say `incomplete` and list the missing artifact. It must not silently turn an unfinished search into a novelty claim.

## Evidence labels

Use these labels consistently in records, paper cards, evidence maps, and reports:

- `author_claim`: what the paper explicitly claims.
- `observed_result`: a result directly checked in a table, figure, appendix, or official benchmark report.
- `pipeline_synthesis`: a conclusion derived by comparing multiple sources.
- `unverified_inference`: a plausible interpretation that still needs checking.

Also record the reading level:

- `metadata`: title, venue, and index information only; discovery use, never “read”.
- `compact`: abstract, introduction, method overview, main experiment, conclusion, and limitations.
- `deep`: compact reading plus task construction, baselines, ablations, appendices, and claims checked against tables or figures.

## Output layout

The coordinator creates one isolated project per research question:

```text
projects/<slug>/
├── 00-input/                 # unchanged user sources
├── 01-question-map/          # question, tensions, observables, non-goals
├── 02-search/                # dated protocol, raw responses, coverage ledger
├── 03-literature/
│   ├── papers/               # downloaded papers when permitted
│   ├── paper-cards/          # compact/deep cards
│   └── retained_registry.*   # machine-readable records
├── 04-evidence-map/          # motivation/method/contribution/insight matrix
├── 05-reviewer-taste/        # venue-level taste and risk brief
├── 06-ideas/                 # freshness ledger, candidates, falsification
├── 07-discussion/            # plain-language handoff
├── 90-logs/                  # rerunnable scripts and run metadata
└── 99-temp/                  # temporary downloads/renderings only
```

Do not mix raw discovery, verified records, PDFs, conclusions, or temporary files. Keep the original input unchanged.

## Project initialization and validation

The coordinator includes scripts for creating the artifact tree and checking a completed report:

```bash
python skills/research-pipeline/scripts/init_research_project.py my-topic --root projects
python skills/research-pipeline/scripts/validate_research_output.py \
  projects/my-topic/03-literature/retained_registry.json \
  projects/my-topic/07-discussion/research-output.md
```

The validator checks coverage floors, authority tiers, anchors, compact/deep reading, explanation cards, freshness, nearest-work comparison, falsification, external validation, and scope. The floors are safety checks, not a target for padding the registry.

## Why this is not a single giant prompt

The skills are deliberately separated because the failure modes differ:

- Search must optimize coverage and authority.
- Citation tracing must preserve branch provenance.
- Paper extraction must prevent abstract paraphrases from masquerading as reading.
- Reviewer profiling must distinguish research taste from generic writing advice.
- Idea mining must resist attractive but already-covered gaps.

The coordinator connects them with explicit artifacts and gates. You can run a component alone, but a standalone component should not claim to have completed the full research process.

## Scope and limitations

This repository is a research workflow, not a literature database and not a guarantee of novelty. APIs can be incomplete, publisher pages can be inaccessible, public reviewer data is biased, and recent preprints can change. The workflow records those limitations instead of hiding them.

The skills do not automatically decide whether an idea is publishable. They produce an auditable basis for a human research decision.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for skill structure, evidence requirements, validation, and forward-testing guidance.

## Repository documentation

- [Architecture](docs/architecture.md): how routing metadata, skill procedures, resources, and stage gates fit together.
- [Artifact contract](docs/artifact-contract.md): the minimum fields for literature records, paper cards, citation edges, and idea candidates.
