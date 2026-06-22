---
name: openwiki-init
description: 初始化知识库。只在用户要创建或配置 OpenWiki 知识库目录时使用，生成 .openwiki 状态、wiki 脚手架、分类体系，并安装 OpenWiki skills。
---

# OpenWiki Init

Initialize only inside the intended KB directory, usually `my-wiki/`. Do not
initialize inside the OpenWiki source repository, a system directory, or any
directory containing project files such as `pyproject.toml`, `.git/`, or
`openwiki/`.

## Steps

1. Stop if `.openwiki/` already exists.
2. Ask only for:
   - KB purpose, default `个人知识库`
   - category names, default `通用`
3. Do not ask for model names or API keys on the skill path.
4. Create:

```text
raw/
.openwiki/
.codex/skills/
.claude/skills/
wiki/
  AGENTS.md
  index.md
  explorations.md
  log.md
  sources/images/
  concepts/
  categories/
```

5. Write `.openwiki/config.yaml`:

```yaml
language: en
model: gpt-5.4-mini
pageindex_threshold: 30
retrieval:
  engine: auto
  qmd_mode: search
  fallback: wiki_structure
```

6. Write empty `.openwiki/hashes.json`.
7. Write `.openwiki/taxonomy.yaml` with the requested categories and always add:

```yaml
- id: uncategorized
  name: 未分类
  description: 暂时无法自动归类或需要稍后整理的文档。
```

8. Create `wiki/categories/<id>/index.md` for every category.
9. Install all OpenWiki skills into both `.codex/skills/` and `.claude/skills/`
   when the source templates are available.
10. Verify qmd is available:

```bash
python3 -m openwiki.qmd status --kb-dir <kb-root>
```

If qmd is missing, stop and tell the user to rerun the project installer after
installing Node.js/npm. qmd is required for OpenWiki.
11. Create or refresh the qmd collection for this KB:

```bash
python3 -m openwiki.qmd setup --kb-dir <kb-root>
```

12. Register the KB in `~/.config/openwiki/global.yaml` as `default_kb`.

## Completion Message

Tell the user:

- Put original files in `raw/`.
- Use `openwiki-add` to add documents.
- Use `openwiki-chat` to ask questions.
- Use `openwiki-category` to manage categories.
