---
name: citation-tracing
description: Expand multiple independent anchor papers into an auditable literature graph. Use when tracing Related Work, references, cited-by work, shared tasks and datasets, later corrections, and author/lab research trajectories must produce a verified map rather than a citation dump.
---

# Citation Tracing

Run a separate branch for every anchor. A global search result cannot substitute for per-anchor tracing.

## Per-anchor procedure

1. Read Related Work and extract named lines of work.
2. Collect references for the direct problem, method, construct, benchmark, and evaluation.
3. Collect cited-by work, prioritizing later top-venue work, replications, critiques, corrections, and papers addressing limitations.
4. Follow benchmark, dataset, code, survey, and curated-list links only as discovery routes; verify papers separately.
5. Trace lead/corresponding authors and labs before and after the anchor when this clarifies a method line, construct, dataset, or changed assumption.
6. Expand one more hop for the most relevant branches. Stop only after the quota is met or two rounds add no relevant theme.

Default quotas are 15 discoveries and 6 retained records per anchor, with at least 60 retained overall. Deduplicate by DOI and normalized title/author while preserving every discovery path.

Record edges such as `cites`, `extends`, `uses_dataset`, `compares_with`, `contradicts`, `addresses_limitation`, `same_author_line`, and `same_lab_line`. Every retained edge needs a source sentence, reference entry, or scholarly metadata endpoint. Label inferred intellectual relations as inference.

Maintain a branch ledger: routes searched, discovered and retained counts, themes added, last relevant discovery, and stopping reason. Citation count is a ranking signal, not evidence of correctness.
