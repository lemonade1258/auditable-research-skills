# Repository architecture

## Design goal

Turn a broad research request into an auditable decision record without forcing every task through one oversized prompt. The unit of composition is a skill plus its artifacts.

The system has two products at once:

1. A human-facing research workflow that explains what to do next.
2. A machine-readable project record that makes it possible to check what was actually done.

The second product is what prevents the first from becoming a polished conversation with no research history.

## Three layers

### Routing layer

`agents/openai.yaml` provides the display name, short description, and default prompt used by compatible agent tooling. It does not contain workflow rules.

### Skill layer

`SKILL.md` contains the trigger description and the minimum ordered procedure. It should answer: what starts this skill, what does it do first, what inputs does it require, what does it produce, and when must it stop or mark incomplete?

### Resource layer

`references/` contains branch-specific policy, schemas, and checks. `scripts/` contains deterministic file/API operations. Resources are loaded only when the relevant branch needs them.

### Project state layer

The coordinator also maintains a project manifest and append-only event log.
`skills/research-pipeline/scripts/projectctl.py` creates the canonical project
tree, records stage status, checks required artifacts, and emits events to
`90-logs/events.jsonl`. This is intentionally separate from model-generated
reports: a report can be persuasive while the project remains incomplete.

Cross-skill records use the small dependency-free helpers in `skills/shared/`.
They validate provenance-critical fields for literature, evidence, ideas, and
manuscript claims without pretending to judge truth or novelty.

## Coordinator contract

`research-pipeline` owns sequencing and gates. It invokes component skills conceptually through their artifacts:

| Gate | Required artifact | Failure state |
|---|---|---|
| Question | question map | question remains method-led or ambiguous |
| Discovery | dated protocol, anchors, coverage ledger | search is narrow or untraceable |
| Graph | branch ledger and relation edges | related work is a citation dump |
| Reading | compact/deep cards | abstract-only synthesis |
| Evidence | evidence matrix with claim labels | author claims mixed with synthesis |
| Taste | standalone venue brief | generic reviewer advice |
| Freshness | dated gap ledger and near-miss checks | novelty based on memory |
| Ideas | candidate cards and falsification | idea proposed before evidence |
| Scope | minimum experiment and external validation | benchmark/model/agent/platform sprawl |

The coordinator does not call every component in one hidden prompt. It checks the
artifact handoff between components. A component can be run alone, but it must
label the project incomplete if its required predecessor artifacts are absent.

## Runtime map

| Layer | Code or files | User-visible responsibility |
|---|---|---|
| Route | `agents/openai.yaml`, skill descriptions | Select the correct capability and avoid accidental task switching |
| Procedure | each `SKILL.md` | Define first action, required input, output, stop condition and evidence rules |
| Deterministic adapter | each skill's `scripts/` | Query APIs, copy PDFs, normalize records, register runs, check files |
| Shared contract | `skills/shared/artifact_contract.py` | Keep literature, evidence, claims, ideas and runs structurally compatible |
| Project controller | `projectctl.py`, `import_artifact.py` | Create projects, enforce artifact gates, log handoffs and prevent unsafe overwrites |
| Human/model interpretation | paper cards, evidence matrix, idea cards, reports | Explain findings and make decisions while preserving uncertainty |

The division is deliberate. Models are useful for interpretation; deterministic
code is better at paths, counts, IDs, versions, and integrity checks.

## Handoff sequence

```text
question-map.md
   ↓
02-search/openalex_discovered.json
   ↓ curate_registry.py
03-literature/retained_registry.json
   ↓ paper_ingest.py + human reading
03-literature/paper-cards/*.json
   ↓ evidence synthesis
04-evidence-map/evidence-matrix.json
   ↓ freshness_check.py
06-ideas/freshness-ledger.json
   ↓ human/model candidate review
06-ideas/candidates.json
   ↓ register_run.py
09-experiments/run-registry.json
   ↓ extract_claims.py + evidence binding
10-manuscript/claim-ledger.json
   ↓ writing/release checks
91-releases/ and 12-transfer/
```

`import_artifact.py` is the controlled boundary when a component writes an
artifact produced outside the project. It validates the record contract,
refuses to overwrite a different file, and records the source and destination
in `90-logs/events.jsonl`.

## What “complete” means

The controller can certify structure, not science. A complete research run must
therefore have both:

- **Structural completeness**: required artifacts exist, are non-empty, follow
  the contract, and have an event trail.
- **Evidence completeness**: claims have source locations or registered
  experiments, core papers have the required reading depth, freshness has a
  date and search trail, and unresolved items are visible.

The scripts enforce the first and expose missing parts of the second. They do
not turn a score, citation count, reviewer profile, or language-model agreement
into proof.

## User decision points

The workflow intentionally stops for human decisions at these boundaries:

1. Is the question important and measurable?
2. Is a source authoritative enough for this claim?
3. Did the paper actually establish the interpreted result?
4. Is the gap still open after the dated search?
5. What experiment could falsify the idea?
6. Does the evidence support the manuscript wording?
7. Is the package compliant with the venue or transfer policy?

These are not missing automation features. They are the decisions the system is
designed to make visible instead of silently guessing.

## Component boundaries

`literature-search` discovers and curates records; it should not decide the final idea.

`citation-tracing` explains how records are intellectually connected; it should not treat citation count as correctness.

`paper-extraction` explains papers; it should not silently fill unknowns from model memory.

`reviewer-profile` analyzes aggregate public evidence; it should not infer anonymous reviewer identities.

`idea-mining` proposes candidates only after the evidence and freshness artifacts exist.

## Compatibility with Matt Pocock-style skills

The repository adopts the same useful conventions: small composable skills, explicit invocation metadata, progressive disclosure, local editable files, and a setup/validation path. The research-specific addition is the evidence contract: reading levels, claim labels, source provenance, citation branches, and incomplete gates.
