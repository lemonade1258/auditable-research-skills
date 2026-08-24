---
name: paper-extraction
description: Explain and compare academic papers at multiple reading depths with traceable evidence. Use when the user needs to understand what each paper wanted to solve, why, how, what it contributed and found, what assumptions or limits remain, and how it changes the current research question.
---

# Paper Extraction

Use explicit reading levels. `metadata` supports discovery only. `compact` covers abstract, introduction, method overview, main experiments, conclusion, and limitations. `deep` additionally inspects task construction, data, baselines, ablations, appendices, and claims against tables. Every core or nearest-prior paper requires a deep read; important supporting papers require at least a compact read.

Write a connected plain-language card before synthesis. Explain what problem the paper sees, why it matters, what the authors built or tested, what data and comparisons make the result credible, what the result does and does not establish, and why the paper changes this investigation. Someone unfamiliar with the title should understand the work from this card.

Classify every important paper along four independent dimensions: `motivation`, `method`, `contribution`, and `insight`. Do not collapse contribution into method or restate the abstract as insight. Also capture task, inputs, outputs, data, assumptions, baselines, evaluation, results, limitations, and relation to other papers using the shared schema.

For important claims, store the exact quote or table/figure reference, page/section, URL, evidence type, and confidence. Label each statement `author_claim`, `observed_result`, `pipeline_synthesis`, or `unverified_inference`.

When relevant, apply `references/finance-checks.md`. Record unknown details as unknown.

Finish with a consistency pass: compare abstract claims with tables, verify comparable settings, identify negative and boundary results, and flag contradictions or inaccessible evidence. Never call an abstract-only record read.
