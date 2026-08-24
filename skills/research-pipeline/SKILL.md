---
name: research-pipeline
description: "Run a source-audited, time-aware research investigation from a broad question to defensible idea candidates. Use for serious topic discovery combining authoritative literature, citation and author/lab tracing, recent community signals, full-paper understanding, independent reviewer-taste analysis, current novelty checks, and scoped external validation."
---

# Research Pipeline

Run every stage and preserve stage artifacts. Treat the user's prior work as context or a transfer target, never as external authority or proof of novelty.

## Setup

Collect the question, domain, target venues, contribution type, time window, known work, practical limits, and source artifacts. Convert broad themes into research tensions and observable behaviors without choosing a method early.

Create one isolated project directory before producing artifacts. Follow `references/project-layout.md`; never mix registries, PDFs, notes, or conclusions across projects.

## Stages and gates

1. Write a question map: central question, importance, competing explanations, observable behaviors, task families, and non-goals.
2. Invoke `literature-search` for 8-12 independent anchors spanning theory, method, measurement/evaluation, task/benchmark, and application domain. Include at least three top-conference/top-journal works and three works external to the user's own work.
3. Invoke `citation-tracing`. Trace Related Work, references, cited-by work, shared tasks/datasets, author trajectories, and lab trajectories. Separately scan the latest 3-6 months of arXiv and current venue programs. Discover at least 120 records and retain at least 60 unless the field is demonstrably smaller.
4. Invoke `paper-extraction`. Populate metadata for all retained papers, compact explanation cards for the important set, and evidence-backed deep reads for the core and nearest-prior set. A title list or abstract paraphrase does not pass.
5. Build an evidence map by `motivation`, `method`, `contribution`, and `insight`, then task, assumptions, data, evaluation, and failure mode. Separate author claims, observed results, pipeline synthesis, and unresolved inference.
6. Invoke `reviewer-profile`. Produce a standalone research-taste brief about attractive questions and evidence stories before applying it to candidate selection.
7. Recheck every claimed gap as of the execution date using `references/freshness-gate.md`. A model-memory gap is not a gap.
8. Invoke `idea-mining` only after the evidence map and current gap check pass. Return no more than five candidates tied to independent evidence and a measurable unresolved limitation.
9. Apply `references/scope-gate.md`. Prefer one central mechanism plus at most one supporting component. Require a minimal falsifiable experiment and one validation setting independent of the project's own data or benchmark.

## Required output

Produce a plain-language report and machine-readable artifacts: question map, dated search protocol, anchors, coverage ledger, related-work graph, authority decisions, retained/rejected records, paper cards, evidence matrix, reviewer-taste brief, gap ledger, candidate ideas, nearest-work checks, smallest falsification experiment, external validation, scope exclusions, and unresolved verification items.

Use counts as coverage floors, not quality targets. Do not propose ideas while core papers remain metadata-only, freshness checks are incomplete, or nearest-work comparisons lack evidence. If a gate fails, label the run incomplete and continue the missing stage.

Use the shared schemas in `../shared/`. Define technical terms and always explain what a paper tried to do, how it did it, what it found, what it did not establish, and why it matters here.
