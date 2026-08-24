# Project artifact layout

Create a stable slug under the workspace and keep all project-specific material inside it:

```text
projects/<slug>/
  00-input/
  01-question-map/
  02-search/
  03-literature/
    papers/
    paper-cards/
  04-evidence-map/
  05-reviewer-taste/
  06-ideas/
  07-discussion/
  90-logs/
  99-temp/
```

Keep source artifacts unchanged in `00-input`. Put raw search/API responses and query logs in `02-search` or `90-logs`; do not mix them with curated paper records. Use `99-temp` only for temporary renderings and downloads. Create dated manifests when rerunning a stage so later outputs identify exact inputs and cutoff dates.
