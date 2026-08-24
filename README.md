# Auditable Research Skills

一套把研究问题推进到可验证选题的组合 skill：先做广泛、可追溯的文献检索，再扩展引用关系、解释论文、检查近期新颖性，最后提出小而可证伪的研究方向。

## 推荐仓库名

**Auditable Research Skills**

推荐 slug：`auditable-research-skills`

这个名字比 `research-pipeline` 更适合作为开源仓库名：它强调来源可审计、论文真实核验和结论边界，同时不把仓库限制为一种固定编排方式。

其他可选名：

- `evidence-led-research-skills`：更强调证据驱动。
- `research-evidence-pipeline`：更强调流水线。
- `verifiable-idea-mining`：更强调从文献到选题。

## 目录约定

```text
.
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md              # 必须；只写触发条件和工作流程
│       ├── agents/
│       │   └── openai.yaml       # 推荐；界面显示信息
│       ├── references/            # 按需加载的细节和规范
│       ├── scripts/                # 可重复执行的确定性脚本
│       └── assets/                 # 模板、图标等输出资源
└── tests/
    ├── fixtures/                  # 最小输入样例
    └── validate_skills.py         # 结构和 frontmatter 检查
```

## 当前 skill

| Skill | 作用 | 是否建议自动触发 |
|---|---|---|
| `research-pipeline` | 总体编排和阶段门禁 | 是 |
| `literature-search` | 多路线、权威来源和近期检索 | 是 |
| `citation-tracing` | references、cited-by、related works 和作者路线 | 是 |
| `paper-extraction` | 按 compact/deep 层级解释论文 | 是 |
| `reviewer-profile` | 目标 venue 的科研品味 | 是 |
| `idea-mining` | 新颖性核查后提出小型可证伪 idea | 是 |

## 每个 SKILL.md 的最低要求

1. 文件夹名使用小写、数字和连字符，且与 frontmatter 的 `name` 一致。
2. YAML frontmatter 只保留 `name` 和 `description`。
3. `description` 明确说明做什么以及什么情况下触发。
4. 正文使用祈使句，核心流程控制在 500 行以内。
5. 详细规范放进一层 `references/`，不要复制到多个 skill。
6. 所有研究 skill 必须区分 discovery、compact、deep，不把标题或摘要列表写成已读论文。
7. 需要验证的结论必须保留来源 URL、证据类型和不确定性。

## 研究流程门禁

不得在核心论文未解析、近期近邻未检查或引用追踪未完成时输出“已证实的新颖性”。这种情况必须标记为 `incomplete`，并列出缺失环节。

## 旧目录说明

根目录下原来的六个同名目录是早期打包副本；新项目应只从 `skills/` 读取。后续发布前可删除旧副本，但本次保留它们以避免影响已有引用。
