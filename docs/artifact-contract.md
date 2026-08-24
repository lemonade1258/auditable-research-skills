# Artifact contract

The exact field names may vary by project, but every complete run should preserve the following information.

## Literature record

```json
{
  "paper_id": "stable-id",
  "title": "verified title",
  "authors": ["author"],
  "year": 2024,
  "venue": "venue or preprint status",
  "doi": "doi or null",
  "source_url": "official landing page",
  "discovery_routes": ["direct", "cited-by"],
  "authority_tier": "A|B|C",
  "authority_reason": "why this tier",
  "inclusion_reason": "relation to the question",
  "reading_level": "metadata|compact|deep",
  "retrieved_at": "YYYY-MM-DD"
}
```

## Paper card

Every compact/deep card should explain in connected prose:

- problem and motivation;
- method and inputs/outputs;
- data, baselines, and evaluation;
- observed result and what it does not establish;
- limitations and assumptions;
- insight for the current question;
- source quotes or table/figure references for important claims.

Keep `motivation`, `method`, `contribution`, and `insight` as separate fields. A contribution is not just the method name; an insight is not a restated abstract.

## Citation edge

```json
{
  "source": "paper-a",
  "target": "paper-b",
  "edge_type": "cites|extends|uses_dataset|compares_with|contradicts|addresses_limitation|same_author_line|same_lab_line",
  "evidence": "reference entry, source sentence, or scholarly metadata endpoint",
  "evidence_type": "direct|inferred",
  "confidence": "high|medium|low"
}
```

## Candidate idea

Every retained idea should state the measured unresolved limitation, supporting and contradicting work, exact nearest-work difference, hypothesis, competing explanation, smallest method, falsification experiment, external validation, exclusions, implementation risk, reviewer objection, and confidence.

## Status values

- `discovery`: found but not yet verified.
- `retained`: included in the curated registry.
- `compact`: important paper read at compact depth.
- `deep`: core or nearest paper read at deep depth.
- `verified`: claim checked against a source.
- `incomplete`: a required gate or evidence item remains missing.
