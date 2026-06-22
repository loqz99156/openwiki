---
name: openwiki-add
description: 知识库添加资料。触发词包括：知识库添加资料、添加到知识库、存到知识库、保存到知识库、把文件加入知识库、导入知识库、处理知识库 raw 新文档。用于把文件、目录、上传文件或 raw/ 里的新文档加入 OpenWiki 知识库，转换文档，分类到知识库目录，更新概念页、索引和哈希记录。
---

# OpenWiki Add

Use this skill inside an existing OpenWiki KB. Locate the KB root by finding
`.openwiki/` in the current directory or an ancestor.

## Steps

1. Determine inputs:
   - If the user provided a path, process that file or directory.
   - If no path is provided, scan `raw/` for supported files not registered in
     `.openwiki/hashes.json`.
2. For each file:
   - Copy external files into `raw/`.
   - Convert short documents to `wiki/sources/<doc>.md`.
   - For long PDFs, build PageIndex and store paged content in
     `wiki/sources/<doc>.json`.
3. Generate an internal LLM summary for planning only.
4. Classify into one existing category from `.openwiki/taxonomy.yaml`.
   Use `uncategorized` if uncertain.
5. Write the user-visible document page:
   - Short doc: `wiki/categories/<category>/<doc>.md` containing converted
     Markdown source plus light frontmatter.
   - PageIndex doc: `wiki/categories/<category>/<doc>.md` containing the
     structure/page ranges and `full_text: sources/<doc>.json`.
6. Update or create concept pages in `wiki/concepts/`.
7. Add backlinks between document pages and concepts.
8. Update `wiki/index.md` and `wiki/categories/<category>/index.md`.
9. Append `wiki/log.md`.
10. Register the document hash only after all prior steps succeed.

## Rules

- Do not move `wiki/sources/` during classification.
- Do not write a large duplicate LLM summary into document pages.
- Keep the LLM summary for index/category brief text and concept planning.
- Preserve UTF-8 output.
