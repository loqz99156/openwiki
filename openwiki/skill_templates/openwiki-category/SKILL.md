---
name: openwiki-category
description: 知识库分类整理。触发词包括：知识库分类整理、整理知识库分类、查看知识库分类、新增知识库分类、重命名知识库分类、删除知识库分类、移动知识库文档、把知识库文档移到分类、移动知识库探索记录。用于查看、新增、重命名、删除或整理 OpenWiki 知识库分类，移动知识库文档页或已保存的探索记录，并保持来源、链接、分类体系和索引同步。
---

# OpenWiki Category

Use this skill inside an existing OpenWiki KB. Locate the KB root by finding
`.openwiki/` in the current directory or an ancestor.

## Parse Intent

If the user invokes only `/openwiki-category` without a description, do not
perform an action yet. Show the available category actions and ask the user
what they want to do:

- 查看分类
- 新增分类
- 重命名分类
- 删除分类
- 移动文档到某个分类
- 移动已保存的探索记录到某个分类

After the user chooses an action, ask only for the missing details needed for
that action.

- list: `查看`, `列出`, `list`, `有哪些分类`
- add: `增加`, `新增`, `添加`, `创建`, `add`
- rename: `改成`, `改为`, `重命名`, `rename`
- delete: `删除`, `移除`, `delete`
- move: `移动`, `移到`, `归到`, `放到`, `move`

Ask a follow-up only when required information is missing.

## Rules

- `.openwiki/taxonomy.yaml` is the source of truth.
- Category directories live under `wiki/categories/<id>/`.
- Do not move `wiki/sources/`.
- Moving a document means moving only its user-visible category document page.
- Update frontmatter, wikilinks, category index pages, `wiki/index.md`, and
  `.openwiki/hashes.json` together.
- If deleting a non-empty category and no target is provided, move content to
  `uncategorized`.

## Actions

### list

Show each category name, id, and document count.

### add

Add the category to taxonomy, create `wiki/categories/<id>/index.md`, and update
`wiki/index.md`.

### rename

Rename taxonomy entry and directory, update all wikilinks and frontmatter, move
matching explorations, update hashes, then refresh indexes.

### delete

Move documents and explorations to the target category first, then remove the
category from taxonomy and delete the empty directory.

### move

For documents, use the same behavior as
`openwiki.taxonomy.reclassify_document(kb_dir, doc_name, target_category)`.
For saved answers, use the same behavior as
`openwiki.taxonomy.reclassify_exploration(kb_dir, name, target_category)`.
