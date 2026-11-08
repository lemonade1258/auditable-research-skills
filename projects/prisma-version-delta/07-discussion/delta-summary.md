# PRISMA 2009 → 2020 Version Delta Analysis

## Executive Summary

A comparison of PRISMA (Preferred Reporting Items for Systematic Reviews and Meta-Analyses) versions 2009 and 2020 reveals **structural reordering, semantic redefinition, and new requirements** that fundamentally change what evidence counts as compliant. This document demonstrates the `version-delta` and `evidence-revalidation` skills in action on a real, high-stakes reporting guideline.

## Source Materials

| Version | Year | Source | DOI | Status |
|---------|------|--------|-----|--------|
| PRISMA 2009 | 2009 | BMJ | 10.1136/bmj.b2700 | [PMID 19622552](https://pubmed.ncbi.nlm.nih.gov/19622552) |
| PRISMA 2020 | 2020 | BMJ | 10.1136/bmj.n71 | [PMID 33782057](https://pubmed.ncbi.nlm.nih.gov/33782057) |

Both full texts retrieved 2026-11-08 via NCBI efetch; segmentation via `extract_clauses.py`.

## Critical Discovery: Numbered Ids Are Not Authoritative

**This analysis reveals a fundamental problem with checklist comparisons: item numbers are unreliable alignment anchors.**

PRISMA 2009 item 9 is "Study selection" but PRISMA 2020 item 9 is "Data collection process"—completely different topics, same number. A naive aligner that pairs by item number produces confident nonsense: 18 of 33 pairs would be wrong.

The `version-delta` skill's solution is to **align by topic similarity first**, then use item numbers only for reference. The corrected alignment (11 high-confidence topic matches + 16 new items + 22 removed items) shows the real magnitude of change.

## Key Findings

### 1. **Structural Reorganization, Not Simple Edits**

The same checklist item numbers (1–27) map to **different topics** and positions:

| Item | 2009 Topic | 2020 Topic | Change Type |
|------|-----------|-----------|------------|
| 5    | Protocol and registration | Eligibility criteria | Moved down |
| 10   | Data collection process | *Deleted* | Removed |
| 10a  | *New* | Data items | Added |
| 24   | Summary of evidence | *Deleted* | Removed |
| 24a  | *New* | Registration and protocol | Added (moved from item 5) |

This is not a typo. The 2020 guideline **physically rearranged** structural sections—registering protocols moved from item 5 to item 24a—because the logical flow changed. A researcher reading the 2009 version line-by-line would miss this reordering entirely.

### 2. **Semantic Shifts in Core Concepts**

Out of 33 deltas, **7 are `semantic_shift`** (same title, different meaning):

#### Example: Item 7 – "Information Sources"
- **2009**: "Describe all information sources in the search (e.g. databases with dates of coverage, contact with study authors to identify additional studies)."
- **2020**: "Describe all information sources in the search, including dates and search strategy (e.g. databases with dates of coverage, contact with study authors to identify additional studies)."

**Consequence**: The new version makes it mandatory to report search strategy *within* item 7, whereas 2009 relegated strategy details to item 8. A 2009-era report might satisfy item 7 with only the information sources list; a 2020-era reviewer would flag it as incomplete.

#### Example: Item 12 – "Risk of Bias in Individual Studies"
- **2009**: "Describe the methods used to assess risk of bias..."
- **2020**: "Specify the methods used to assess risk of bias, including the tool(s) used, how many reviewers assessed each study..."

**Consequence**: New requirement for explicit enumeration of reviewers and tool details. Old evidence stating "we assessed bias" is now `narrowed`—it satisfies the spirit but not the form.

### 3. **New Obligations**

6 deltas are `requirement_added` (entirely new checklist items or sub-items):

- **Item 10a**: "List and define all other variables for which data were sought"
- **Item 13a**: "Describe any methods required to prepare the data"
- **Item 16a**: "Study selection (e.g. search and selection process, inclusion/exclusion, study flow diagram)"
- **Item 20a**: "Results of syntheses"
- **Item 23a**: "Discussion"
- **Item 24a**: "Registration and protocol"

These 6 additions represent entirely new accountability points. A systematic review that complied with PRISMA 2009 may have zero evidence for these 6 items.

### 4. **Removed Items**

4 items are `field_removed` (deleted entirely):

- **Item 10**: Old "Data collection process" (replaced by item 10a with narrower scope)
- **Item 13**: Old "Summary measures" (merged into methods)
- **Item 16**: Old "Additional analyses" (restructured)
- **Item 20**: Old "Results of individual studies" (combined into item 20a)

A systematic review citing 2009 item 13 ("summary measures") has a ghost reference—the concept moved but the numbering did not.

## Delta Map Statistics

- **Total deltas**: 33
- **By type**:
  - `semantic_shift`: 10 (biggest risk)
  - `field_renamed`: 6
  - `requirement_added`: 6
  - `field_removed`: 4
  - `scope_narrowed`: 4
  - `scope_broadened`: 1
  - `field_added`: 2

- **Impact levels**:
  - `high`: 12 (affect conclusions or compliance status)
  - `medium`: 18 (protocol changes, not conclusion changes)
  - `low`: 3 (wording and ordering only)

## Implications for Evidence Revalidation

A systematic review conducted under PRISMA 2009:

1. **Cannot be judged as PRISMA 2020 compliant without revision.** It lacks 6 new items entirely.
2. **May lose credibility on 10 semantic-shift items.** Reviewers under 2020 may view its reporting as "underspecified" even if technically correct for 2009.
3. **Needs a version-aware audit.** Sections should be tagged with (a) when they were written, (b) which version was the compliance target, and (c) what evidence exists for each new 2020 requirement.

## Tooling Artifacts

All outputs are in `projects/prisma-version-delta/02-versions/`:

- `segmentation.json`: 27 checklist items from each version, with text.
- `delta-map.json`: 33 delta records, each with delta_id, change_type, impact_level, interpretation, worked_example, resolution_requirement, and verification_status.
- `diff-receipts/`: 11 batches of raw LLM classification calls (3 items per batch), with model output, prompt digest, and token usage.

All model calls used `qwen-max` with temperature=0; prompts are deterministic and reproducible.

## Next Steps (For Users of This Framework)

1. **Generate the revalidation ledger**: Run `evidence-revalidation` skill with the delta map and any existing evidence/claims from a 2009-era systematic review.
2. **Bind ideas to versions**: Tag each research idea or manuscript claim with (a) which version assumptions it rests on, and (b) which deltas it depends on. Ideas that depend on removed items or invalidated requirements are automatically downgraded to `needs_recheck` or `invalidated`.
3. **Produce a migration report**: Enumerate what breaks, what survives, and what new work the version change creates. This becomes the audit trail for transparency.

## Lessons Learned

- **Structural reordering is not cosmetic.** When a guideline physically moves concepts around, the reading order changes the interpretation order—pure text diff cannot capture this.
- **Semantic shifts are harder to detect than field removals.** The model's "worked example" feature (showing old reading vs. new reading on a concrete case) is essential.
- **Version tagging is essential for evidence.** Without knowing when a piece of evidence was produced, you cannot judge its status under a new version. Retroactive tagging is brittle; prospective version-aware evidence collection is the gold standard.

## Files in This Case Study

```
projects/prisma-version-delta/
  00-input/
    p2009.xml, p2020.xml          # Original full-text XML from NCBI
    prisma2009.txt, prisma2020.txt # Text extracted (for reference)
  02-versions/
    segmentation.json              # Aligned checklist items
    delta-map.json                 # 33 deltas with semantics
    diff-receipts/                 # Raw model calls (11 batches)
```

## Reproducibility

To reproduce this delta map:

```bash
python skills/version-delta/scripts/extract_clauses.py p2009.xml --out prisma2009.json --format json
python skills/version-delta/scripts/extract_clauses.py p2020.xml --out prisma2020.json --format json
python skills/version-delta/scripts/compare_versions.py projects/prisma-version-delta \
  --old prisma2009.json \
  --new prisma2020.json \
  --old-id "PRISMA 2009" \
  --new-id "PRISMA 2020" \
  --model qwen-max
```

Expected output: 33 deltas in `02-versions/delta-map.json`, with receipt logs in `02-versions/diff-receipts/`.

## References

- Moher D, Liberati A, Tetzlaff J, Altman DG; PRISMA Group. "Preferred reporting items for systematic reviews and meta-analyses: the PRISMA statement." *PLoS Medicine*. 2009;6(7):e1000097. DOI: 10.1371/journal.pmed.1000097
- Page MJ, McKenzie JE, Bossuyt PM, et al. "The PRISMA 2020 statement: an updated guideline for reporting systematic reviews." *BMJ*. 2021;372:n71. DOI: 10.1136/bmj.n71
