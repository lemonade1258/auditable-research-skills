# Auditable Research Skills

一套把研究问题推进到“可核查、可复现、可证伪”的科研工作流。它不是一个会生成漂亮综述的超级提示词，也不是自动保证新颖性的论文机器人。

它把研究拆成明确的 skill、项目文件、证据记录和阶段门禁：模型负责理解、比较和提出候选；脚本负责路径、字段、计数、版本和完整性检查；研究者负责事实裁决、实验真实性和最终判断。

## 先读这三份文档

1. [系统总览](docs/system-overview.md)：项目解决什么问题，哪些已经实现，哪些仍需人工判断。
2. [使用手册](docs/using-the-pipeline.md)：从创建项目到文献、实验、写作、发布和技术转化的实际命令。
3. [架构说明](docs/architecture.md)：路由层、skill 层、资源层、项目状态层如何协作。

## 它解决的具体问题

直接问模型“这个方向有没有人做过、还能做什么”，常见结果是：只覆盖熟悉论文，混淆论文贡献和方法，遗漏引用链与近期工作，在证据不足时过早提出 idea。

本仓库把这些风险拆成可检查的阶段：

```text
问题定义
  -> 多路线检索与策展
  -> 引用、作者、实验室和数据集追踪
  -> metadata / compact / deep 论文阅读
  -> claim-evidence 矩阵
  -> 当前日期 freshness 复核
  -> 小而可证伪的 idea
  -> 实验运行登记
  -> claim ledger 驱动论文写作
  -> 独立审阅、rebuttal 和发布审计
  -> 专利交底或技术转化
```

箭头是门禁，不是装饰。没有完成前一阶段的证据，不能把后一阶段的文字当成结论。

## 六个核心 skill

| Skill | 负责什么 | 主要产物 |
|---|---|---|
| `research-pipeline` | 协调整个调查、维护阶段门禁 | 项目 manifest、阶段状态、研究报告 |
| `literature-search` | 独立路线检索、来源分级、保留和排除 | 搜索协议、OpenAlex 发现集、策展注册表 |
| `citation-tracing` | 顺着 references、cited-by、作者、实验室、数据集追踪 | 文献图谱、关系边、分支台账 |
| `paper-extraction` | 按深度阅读并解释论文 | PDF 文本、compact/deep paper card |
| `reviewer-profile` | 分析公开 venue/领域评审品味 | 主题统计、数据范围和执行风险 |
| `idea-mining` | 在 evidence 和 freshness 通过后形成候选 | 最近工作比较、证伪实验、外部验证 |

配套脚本还提供：实验 `run registry`、论文 `claim ledger`、写作事实检查、投稿包审计和专利/技术转化 intake。

## 最短可用入口

```bash
python skills/research-pipeline/scripts/projectctl.py init my-topic \
  --root projects \
  --question "一个可测量的研究问题" \
  --domain finance \
  --venue NeurIPS

python skills/literature-search/scripts/openalex_collect.py projects/my-topic \
  --query "直接问题" \
  --query "同义概念" \
  --query "任务或 benchmark"

python skills/literature-search/scripts/curate_registry.py \
  projects/my-topic/02-search/openalex_discovered.json \
  projects/my-topic --keep 60
```

随后入库核心 PDF，补齐 paper cards，建立 evidence matrix，运行 freshness 检查，再进入 idea 和实验。完整命令见 [使用手册](docs/using-the-pipeline.md)。

## 为什么它可信

- 原始输入、检索日志、排除记录、PDF、论文卡、实验和旧版本分开保存。
- 重要判断需要来源、原文位置、实验运行或明确标注为未核验推断。
- `metadata` 不等于读过论文；空目录和空 JSON 不能通过阶段门禁。
- `events.jsonl` 记录初始化、导入、阶段通过、失败和人工裁决。
- 共享 artifact contract 防止不同模块各自发明互不兼容的字段。
- 系统明确保留 `incomplete`、`unverified`、`blocked`，不把缺证据包装成完成。

## AI 防御性写作规则

写作模块遵循 anti-AI defensive writing 的边界：保留作者事实、数字、引用、公式和合理不确定性；不添加不存在的实验、统计、指标、机制、引用或 reviewer 话术；不使用空泛免责声明掩盖范围；不把润色变成改变作者观点。

修改前后可以运行：

```bash
python skills/research-pipeline/scripts/check_writing_integrity.py before.md after.md
```

投稿包必须明确采用 `none`、`single-blind` 或 `double-blind`，再运行 release audit。文本扫描不能替代视觉 PDF 检查和 venue 政策确认。

## 当前边界

这套系统已经提供可运行的项目控制器、artifact schema、OpenAlex 适配器、PDF 入库、证据/新鲜度/实验/claim 记录、review 适配、写作检查、发布审计和专利转化 scaffold。

它不自动裁决论文事实、新颖性、可发表性或专利法律结论。论文表格与图、实验真实性、竞争解释、venue 政策和技术事实仍需研究者或专业人员确认。

## 安装

```bash
npx skills@latest add lemonade1258/auditable-research-skills --skill '*' --agent '*' --copy
```

也可以直接使用本仓库的 `skills/<skill-name>/SKILL.md` 和对应 `scripts/`。

## 验证

```bash
python -m pytest -q
python tests/validate_skills.py
python -m compileall -q skills
```

本仓库是研究工作流和审计基础设施，不是文献数据库，也不承诺自动发现新颖 idea。它的价值在于让研究判断有来源、有过程、有失败状态，也能在下一轮研究中复用。
