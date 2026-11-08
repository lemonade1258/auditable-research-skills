---
name: version-delta
description: Compare two versions of a specification, guideline, standard, evaluation protocol, or regulatory rule and produce an auditable semantic difference map. Use when a rulebook has a new edition, a benchmark or annotation guideline changed, a venue policy was revised, or old evidence must be judged against a new normative baseline.
---

# Version Delta

Compare two versions of the same normative artifact. The goal is not a text diff.
The goal is to establish **what changed in meaning**, **which downstream artifacts
depend on it**, and **what is now unproven**.

## Required inputs

Two versioned sources, each with a stable identifier:

- `old_version`: id, effective date, authoritative URL or file, retrieval date.
- `new_version`: same fields, plus the effective date of the change.

If either version is missing, stop with `blocked`. Do not infer one version from
the other, and never treat a summary of a rulebook as the rulebook.

## Procedure

1. **Segment both versions into comparable units.** Identify the natural
   decomposition of the artifact: numbered clauses, sections, requirements,
   fields, metrics, scoring rubrics, evaluation stages, or definitions. Write
   the segmentation to `02-versions/segmentation.json` with a stable unit id
   per segment and its source location on both sides.

2. **Align units one-to-one.** A segment in the old version maps to zero, one,
   or many segments in the new version. Record the alignment explicitly. Do not
   let the LLM silently drop unmatched segments: a dropped segment is a change.

3. **Classify each difference.** For every aligned pair that differs, assign
   exactly one `change_type`:

   - `field_added` / `field_removed`: a unit that did not exist before, or is gone.
   - `field_renamed`: same meaning, different identifier or title.
   - `semantic_shift`: same words, different operational meaning. The hardest
     and the most valuable case. Requires a concrete worked example of the old
     reading and the new reading.
   - `scope_narrowed` / `scope_broadened`: the set of covered cases changed.
   - `requirement_added` / `requirement_removed`: a new obligation appears or an
     existing one is withdrawn.

4. **State the interpretive consequence.** Each delta must carry an
   `interpretation`: one sentence naming what a practitioner who read only the
   old version would now get wrong. If no such consequence exists, the change
   is cosmetic and should be `field_renamed` at most.

5. **Grade the impact.** Use `impact_summary` plus `impact_level`:

   - `high`: invalidates prior conclusions, changes what counts as compliant or
     correct, or alters a headline metric's meaning.
   - `medium`: changes the required protocol but not the answer to an existing
     question.
   - `low`: presentation, ordering, or wording only.

6. **Attach the semantic-resolution requirement.** For `semantic_shift`,
   `scope_narrowed`, `scope_broadened`, and both `requirement_*` types, state
   the `resolution_requirement`: what evidence a downstream claim must now
   carry. This is the field that later drives revalidation.

7. **Refuse the false positive.** Not every textual difference is a semantic
   change, and not every semantic change is captured by the text. Record
   `unchanged_units` with a reason, and record at least one `uncertain` delta
   where a human must decide. A delta map with zero uncertain items has not
   been checked hard enough.

## Tooling

Use `scripts/compare_versions.py` to run the alignment and classification. It
calls an OpenAI-compatible chat endpoint, writes the raw model reply and the
request digest next to the parsed output, and leaves every record at
`machine_proposed` verification status. Promote a record to `human_confirmed`
only after a person reads the two source passages.

The script does not decide that a change is real. It produces a reviewable
proposal with the source locations attached, so the semantic judgment stays
with the researcher.

## Required output

Write to `02-versions/`:

- `segmentation.json`: units and their locations in both versions.
- `delta-map.json`: one record per difference, validated with
  `validate_records(..., "delta")`.
- `diff-receipts/`: raw model replies and request digests for each batch.
- `delta-summary.md`: a plain-language account of what changed and why it
  matters, in prose a non-specialist can follow.

## Stop conditions

Stop and report `incomplete` when:

- the two versions cannot be aligned at the segment level;
- a high-impact change has no concrete old/new example;
- more than a third of the units are unmatched without an explicit reason;
- the model reply cannot be parsed as JSON after one retry — do not fall back
  to hand-writing deltas, because then the run has no provenance.

## What this skill does not do

It does not judge whether the new version is better, whether the old version
was broken, or whether downstream work is acceptable. It does not read the
literature for you, and it does not fetch the versions for you: retrieval
provenance is the caller's responsibility.
