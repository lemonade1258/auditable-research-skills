# Repository architecture

## Design goal

Turn a broad research request into an auditable decision record without forcing every task through one oversized prompt. The unit of composition is a skill plus its artifacts.

## Three layers

### Routing layer

`agents/openai.yaml` provides the display name, short description, and default prompt used by compatible agent tooling. It does not contain workflow rules.

### Skill layer

`SKILL.md` contains the trigger description and the minimum ordered procedure. It should answer: what starts this skill, what does it do first, what inputs does it require, what does it produce, and when must it stop or mark incomplete?

### Resource layer

`references/` contains branch-specific policy, schemas, and checks. `scripts/` contains deterministic file/API operations. Resources are loaded only when the relevant branch needs them.

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

## Component boundaries

`literature-search` discovers and curates records; it should not decide the final idea.

`citation-tracing` explains how records are intellectually connected; it should not treat citation count as correctness.

`paper-extraction` explains papers; it should not silently fill unknowns from model memory.

`reviewer-profile` analyzes aggregate public evidence; it should not infer anonymous reviewer identities.

`idea-mining` proposes candidates only after the evidence and freshness artifacts exist.

## Compatibility with Matt Pocock-style skills

The repository adopts the same useful conventions: small composable skills, explicit invocation metadata, progressive disclosure, local editable files, and a setup/validation path. The research-specific addition is the evidence contract: reading levels, claim labels, source provenance, citation branches, and incomplete gates.
