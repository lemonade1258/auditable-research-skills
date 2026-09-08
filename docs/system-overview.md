# Auditable Research Skills：用户总览

## 先看结论

这套仓库已经实现了一个可运行的、可追踪的科研研究基础设施：它把“找文献、读论文、判断缺口、设计 idea、登记实验、写论文、审计投稿包和转技术交底”拆成相互衔接的阶段。

它不会自动证明一个 idea 新颖、论文可发表或技术可专利。它保存证据、暴露缺口、阻止未经支持的结论，并把下一步行动变成项目文件。

## 核心设计

```text
问题
  ↓
多路线检索与策展
  ↓
引用/作者/实验室关系
  ↓
metadata → compact → deep 论文阅读
  ↓
claim/evidence 矩阵
  ↓
当前日期 freshness 检查
  ↓
小而可证伪的 idea
  ↓
可复现的实验登记
  ↓
claim ledger 驱动写作
  ↓
独立审阅、rebuttal、发布审计
  ↓
论文发布或专利/技术转化
```

每个箭头都是阶段门禁。下一阶段不能把上一阶段缺失的证据当成已完成。

## 使用者只需理解三类东西

### 1. Skill：做什么

| Skill | 作用 | 不负责什么 |
|---|---|---|
| `research-pipeline` | 协调整条研究链路和门禁 | 不替人宣布新颖性 |
| `literature-search` | 多路线发现、来源分级、保留和排除 | 不等于论文已读 |
| `citation-tracing` | 沿引用、作者、实验室和数据集追踪 | 不把引用数当质量 |
| `paper-extraction` | 形成 compact/deep 论文卡 | 不从摘要编造细节 |
| `reviewer-profile` | 分析 venue/领域公开评审品味 | 不识别匿名 reviewer |
| `idea-mining` | 在证据和 freshness 通过后生成小候选 | 不在检索未完成时挖“新 idea” |

实验、写作、发布和专利是由研究 pipeline 下的确定性脚本与外部 skill 接入的工作面。

### 2. Artifact：留下什么

- `manifest.json`：项目身份、问题、目标 venue、阶段状态。
- `90-logs/events.jsonl`：初始化、导入、阶段通过、失败和人工决定。
- `retained_registry.json`：经过策展的论文记录。
- `paper-cards/*.json`：论文的 compact/deep 解释卡。
- `evidence-matrix.json`：claim 到来源和位置的绑定。
- `freshness-ledger.json`：按日期复核过的缺口。
- `run-registry.json`：代码、数据、配置、种子和实验状态。
- `claim-ledger.json`：正文声明与证据/实验的绑定。
- `reviews/`、`91-releases/`、`12-transfer/`：审稿、发布和技术转化产物。

### 3. Gate：什么时候能继续

```bash
python skills/research-pipeline/scripts/projectctl.py gate projects/<slug> <stage>
```

Gate 检查产物不是空文件、JSON 不是空数组、目录确实包含阶段产物、结构符合契约且事件日志可读。它不会伪装成科学裁判；内容判断仍要由研究者基于证据完成。

## 一次最短可用运行

```bash
python skills/research-pipeline/scripts/projectctl.py init my-topic \
  --root projects \
  --question "可测量的研究问题" \
  --domain finance \
  --venue NeurIPS

python skills/literature-search/scripts/openalex_collect.py projects/my-topic \
  --query "直接问题" \
  --query "同义概念" \
  --query "benchmark 或评价问题"

python skills/literature-search/scripts/curate_registry.py \
  projects/my-topic/02-search/openalex_discovered.json \
  projects/my-topic --keep 60
```

接着下载并入库核心 PDF，补齐论文卡；然后建立 evidence matrix，做 freshness 检查，才进入 idea 和实验阶段。完整命令见 [using-the-pipeline.md](using-the-pipeline.md)。

## 论文阅读的最低标准

`metadata` 只表示发现。`compact` 至少覆盖摘要、引言、方法概览、主实验、结论和局限。`deep` 还要核对任务构造、基线、消融、附录、表格/图和关键 claim。

论文卡必须分别回答：

1. 它想解决什么，为什么值得解决？
2. 它怎么做，输入和输出是什么？
3. 它用什么数据、基线和评价？
4. 哪些结果在原文表格/图中被观察到？
5. 它没有证明什么？
6. 它对当前问题改变了什么判断？

## AI 防御性写作规则

本仓库的写作检查遵循 anti-AI defensive writing 的四个测试：

1. **来源**：数字、引用、公式、方法细节和范围是否来自原文、实验或作者明确提供的材料？
2. **必要性**：该限定或免责声明是否真的影响任务、分析或 venue 要求？
3. **可解释性**：术语、指标、统计和因果表述是否被定义？
4. **决策价值**：它是否改变读者对证据的理解？

执行规则：

- 不添加不存在的数字、置信区间、显著性检验、指标、实验、引用或机制。
- 不把“may suggest”“while promising”“we cannot claim”等空泛防御语替代明确的范围条件。
- 结果在给定数据集和设定中成立，就直接写出该结果；不要无证据扩大到普遍结论。
- 保留作者真实判断和合理不确定性；只清理 AI 残留，不把文字改成统一模板。
- 写作修改前后运行 `check_writing_integrity.py`；P0 证据问题阻断交付。
- 投稿包必须先声明 `none`、`single-blind` 或 `double-blind`，再运行 release audit。文本扫描不能代替 PDF、metadata 和 venue 政策检查。

## 当前实现边界

### 已实现

- 项目初始化、manifest、阶段状态和事件日志。
- Literature、paper card、evidence、freshness、run、claim、transfer 的共享契约。
- OpenAlex 发现和策展适配器。
- PDF 入库、文本抽取和论文卡 scaffold。
- Reviewer 数据标准化统计适配器。
- 实验登记、claim ledger、写作数字/引用完整性检查。
- 投稿包身份扫描和未决项报告。
- 专利/技术转化事实优先的 intake/disclosure scaffold。

### 必须由研究者或外部工具完成

- 论文事实、表格、图和局限性的真正阅读与核验。
- 研究问题、竞争解释、idea 新颖性和可发表性的判断。
- 实验代码、数据、统计方法和失败分析。
- 视觉 PDF 检查、venue policy 确认和法律/专利专业判断。

### 不应被误解为已实现

- 自动获得“博士级研究”或“保证新颖”。
- 用多个模型角色的一致输出替代独立证据。
- 用引用量、自动评分或单一 benchmark 替代方法判断。
- 用文本扫描证明匿名发布包完全合规。
- 用技术交底草稿证明专利新颖性、创造性或保护范围。

## 判断一次运行是否可信

在 `07-discussion` 或交付报告中，至少能找到以下答案：

- 问题地图和非目标是什么？
- 哪些独立路线被检索，何时检索？
- 锚点和最近邻工作是什么？
- 核心论文达到什么阅读深度？
- 重要结论对应哪些证据位置？
- 当前日期 freshness 状态是什么？
- idea 的最小证伪实验和外部验证是什么？
- 论文 claim 是否绑定实验或来源？
- 未解决项、人工判断和发布限制是什么？

缺少其中任一项时，正确状态是 `incomplete` 或 `unverified`，而不是用更漂亮的文字掩盖缺口。
