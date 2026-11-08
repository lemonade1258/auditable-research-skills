---
name: evidence-revalidation
description: Judge whether existing evidence, claims, and ideas remain valid under a new version of a specification, guideline, standard, or evaluation protocol. Use after a version-delta map exists and the literature or evidence base was built under the previous version. Produces a revalidation ledger stating which evidence survives, which narrows, and which is invalidated.
---

# Evidence Revalidation

Take a delta map and a body of evidence produced under the old version, and
decide what survives. This is the step that turns "a rulebook changed" into
"these specific conclusions are now unsupported."

## Required inputs

- `delta-map.json` from the `version-delta` skill.
- An evidence set: records of type `evidence`, and any `claim` or `idea`
  records that were derived from them.
- The version id each evidence record was produced under.

If any evidence record lacks a version id, it is `unverified` until someone
supplies one. Do not guess which version produced a record.

## Procedure

1. **Bind evidence to deltas.** For each evidence record, find the deltas that
   touch its subject. An evidence record about search strategy binds to deltas
   about search and screening; an evidence record about bias assessment binds
   to deltas about risk-of-bias appraisal. If the binding is ambiguous, record
   `uncertain` as the status rather than forcing a match.

2. **Apply the delta's `resolution_requirement`.** This is the pivot. Each delta
   states what evidence a downstream claim must now carry. If the evidence
   record satisfies that requirement, the record is `valid`. If it meets it
   partially, the record is `narrowed`. If it cannot meet it without new
   work, the record is `invalidated`.

3. **Distinguish `invalidated` from `superseded`.** `invalidated` means the
   claim is now false under the new version. `superseded` means the claim was
   true and correct but has been replaced by a newer statement of the same
   thing. These demand different remediation, and conflating them hides
   whether prior work is wrong or merely outdated.

4. **Mark scope changes explicitly.** When a delta is `scope_narrowed`, the
   evidence inside the narrowed scope is usually still `valid`; the evidence
   that depended on the removed part is `invalidated`. Scope changes must not
   be applied as a blanket invalidation.

5. **Do not silently repair.** If evidence would need re-running an experiment,
   re-extracting data, or re-judging a paper, the status is `invalidated` or
   `needs_recheck` — not `valid` with a note. "Probably still fine" is
   `needs_recheck`.

6. **Propagate to ideas.** An idea inherits the worst status among the evidence
   it depends on, but never better. An idea whose supporting evidence was
   narrowed is `narrowed`, not `valid`.

## Tooling

`scripts/revalidate.py` performs steps 1 to 4 with a model-assisted binding
pass, then applies the deterministic status rules locally. The model proposes
which deltas bind to which evidence and writes the reasoning; the script
decides the status from the resolution requirements and the evidence content,
so the status logic is reviewable and repeatable.

Every model call writes a receipt under `04-evidence-map/revalidation-receipts/`.

## Required output

Write to `04-evidence-map/`:

- `revalidation-ledger.json`: one record per evidence item, validated with
  `validate_records(..., "evidence_revalidation")`.
- `idea-version-binding.json`: one record per affected idea, validated with
  `validate_records(..., "idea_version_binding")`.
- `revalidation-summary.md`: prose stating what broke, what survived, and what
  new work the change creates.

## Stop conditions

Stop and report `incomplete` when:

- the delta map has no `resolution_requirement` on any high-impact delta —
  without it, revalidation is guesswork;
- more than a third of evidence records lack a version id;
- the model cannot bind any delta to any evidence and the evidence set is
  larger than five records.

## What this skill does not do

It does not re-run the underlying studies, does not decide that a reviewer
should accept the new version, and does not produce a new claim set. It only
states the validity status of what already exists under the new baseline.
