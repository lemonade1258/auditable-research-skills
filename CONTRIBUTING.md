# Contributing

## 新增或修改 skill

1. 一个 skill 一个目录：`skills/<skill-name>/`。
2. 必须包含 `SKILL.md`，并通过 frontmatter、命名和结构检查。
3. 复杂细节放进 `references/`；重复内容应抽成共享 reference，而不是复制到多个 skill。
4. 脚本必须可重复运行，并在最小 fixture 上测试。
5. 研究类改动必须注明来源、检索日期、阅读层级和未完成门禁。
6. 不把项目私有数据、API key、全文 PDF 或运行缓存提交进 skill 仓库。

## 提交前检查

- 运行 `python tests/validate_skills.py`。
- 检查每个 `SKILL.md` 的 name 与目录名一致。
- 检查 README 中的 skill 清单与实际目录一致。
- 对研究流程变更，确认 discovery、extraction、evidence 和 freshness 阶段没有断链。
