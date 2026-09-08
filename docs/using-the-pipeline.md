# 如何使用这套科研 Pipeline

这套系统的设计脉络是：先把研究问题和证据保存下来，再让各个 skill 在明确边界内工作。每个阶段都留下文件和事件，下一阶段读取这些产物，而不是读取一段无法复核的聊天摘要。

## 1. 从项目开始

```bash
python skills/research-pipeline/scripts/projectctl.py init credit-risk \
  --root projects \
  --question "在设定 X 下，方法 Y 是否改善风险识别？" \
  --domain finance \
  --venue NeurIPS \
  --source notes.md
```

项目目录是唯一工作边界。`00-input` 中的原始输入不覆盖；`90-logs/events.jsonl` 记录每次重要操作；`99-temp` 可以清理。

## 2. 文献发现和注册

OpenAlex 适配器接受多条独立查询，写入搜索日志和原始发现集：

```bash
python skills/literature-search/scripts/openalex_collect.py projects/credit-risk \
  --query "credit risk language models" \
  --query "financial reasoning benchmark" \
  --query "uncertainty calibration finance" \
  --per-query 50
```

它只产生 `metadata` 级记录。记录有来源 URL、检索日期、查询路线、权威层级和摘要，但不能被称为已经读过论文。后续策展结果应通过 `import_artifact.py` 导入 `03-literature/retained_registry.json`。

## 3. PDF 与论文卡

```bash
python skills/paper-extraction/scripts/paper_ingest.py projects/credit-risk paper.pdf \
  --paper-id W123 --level deep
```

工具复制 PDF、尝试用 `pdftotext` 生成文本，并创建论文卡空架构。`motivation`、`method`、`contribution`、`insight` 等字段必须由阅读者补充；空字段会被 validator 阻断。这是为了避免“下载了 PDF”被误报为“完成深读”。

## 4. 证据和近期缺口

```bash
python skills/research-pipeline/scripts/build_evidence_matrix.py projects/credit-risk \
  --claim "方法在设定 X 上提高指标 M" --source W123 \
  --claim "作者没有评估跨时间稳定性" --source W123 \
  --label observed_result

python skills/research-pipeline/scripts/freshness_check.py projects/credit-risk \
  --idea-id idea-001 --status open \
  --query "最新查询式" --nearest W123 --evidence "recent-search-log.json"
```

`freshness-ledger.json` 必须带执行日期、查询、最近工作和证据。`open` 是可进入 idea 阶段的唯一状态；`partially_open`、`likely_closed` 和 `unverified` 都不能被包装成新颖性结论。

## 5. Reviewer profile

把公开 review 导出为 JSON/JSONL 后适配：

```bash
python skills/reviewer-profile/scripts/adapt_reviews.py reviews.json \
  projects/credit-risk/05-reviewer-taste/iclr-finance.json \
  --venue ICLR --year 2025 \
  --scope-note "第三方公开镜像；不代表完整 OpenReview census；不推断 reviewer 身份"
```

输出是主题统计和逐条标准化 review，不是对某个匿名 reviewer 的心理画像。缺失字段、镜像偏差和评分口径要保留在 `scope_note`。

## 6. 实验与论文 claim

```bash
python skills/research-pipeline/scripts/register_run.py projects/credit-risk \
  --run-id run-001 --idea-id idea-001 --code-commit abc123 \
  --data-version data-v2 --config configs/run-001.yaml \
  --model model-v1 --seed 1 --seed 2 --seed 3 --status complete

python skills/research-pipeline/scripts/extract_claims.py projects/credit-risk manuscript/results.txt
```

实验登记保存代码版本、数据版本、配置、种子、原始输出、摘要结果和失败模式。claim ledger 保存正文句子与 evidence/run 的关联；没有支持证据的 claim 默认为 `needs-source`。

## 7. 写作清理和发布审计

```bash
python skills/research-pipeline/scripts/check_writing_integrity.py before.md after.md

python skills/research-pipeline/scripts/check_release_package.py submission/ \
  --release review --anonymity double-blind --identity-term "Author Name"
```

写作检查只做确定性事实保护：发现新增数字、引用或 URL 时阻断，除非明确允许新增分析。它不判断文字“像不像 AI”。发布审计会检查身份词和匿名政策，但视觉 PDF 检查、venue 规则和 metadata 仍需人工确认，状态可能是 `UNRESOLVED`。

## 8. 专利/技术转化出口

```bash
python skills/research-pipeline/scripts/patent_transfer.py projects/credit-risk \
  --case-id risk-engine-v1 --mode disclosure \
  --fact "输入为……" --fact "核心处理步骤为……" \
  --question "需要发明人确认的技术边界" \
  --source 09-experiments/run-registry.json
```

该出口只把研发事实整理成交底工作包。它不会从论文结果推断专利新颖性，不会自动产生法律结论，也不会在缺事实时补写。`application` 和 `docket` 是显式模式，不能由写论文流程自动触发。

## 9. 阶段门禁和状态

```bash
python skills/research-pipeline/scripts/projectctl.py gate projects/credit-risk question
python skills/research-pipeline/scripts/projectctl.py status projects/credit-risk
python skills/research-pipeline/scripts/projectctl.py validate projects/credit-risk
```

控制器检查文件是否存在、结构化记录是否符合 contract、事件日志是否可读。它不替研究者判断论文正确性、idea 新颖性或是否应该投稿。所有未完成内容要保留为 `incomplete` 或 `unverified`，不能为了得到绿色状态而伪造字段。

## 10. 一句话理解

使用者可以把它看成一条有档案的研究流水线：

```text
问题 → 检索 → 关系图 → 分层阅读 → 证据矩阵 → 当前缺口 → 小 idea
     → 实验登记 → claim ledger → 独立审阅 → 发布审计 / 专利转化
```

每一步都有自己的产物、输入、失败状态和复核方式；AI 负责解释和提出候选，确定性脚本负责路径、字段、计数、版本和完整性。

