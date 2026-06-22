---
name: openwiki-chat
description: 知识库问答。触发词包括：知识库问答、问知识库、查知识库、基于知识库回答、在知识库里回答、知识库提问、知识库追问、知识库总结、知识库比较、保存知识库回答。用于基于已有 OpenWiki 知识库提问、追问、比较、总结、引用本地 wiki 证据，并把值得保留的回答保存到知识库探索记录。
---

# OpenWiki Chat

Use this skill inside an existing OpenWiki KB. Locate the KB root by finding
`.openwiki/` in the current directory or an ancestor.

If the user invokes only `/openwiki-chat` without a question, enter a
knowledge-base chat flow: read the wiki structure, tell the user the knowledge
base is ready, and ask what they want to explore. Treat subsequent user
messages as follow-up questions in the same OpenWiki context until the user
switches tasks. Saving a useful answer is an in-chat action; after saving,
remain in the same `/openwiki-chat` flow and continue accepting follow-up
questions. Do not ask the user to invoke `/openwiki-chat` again unless they
have switched to another skill or task.

## Retrieval Scope

Prefer human-readable wiki pages:

- `wiki/index.md`
- `wiki/categories/**/*.md`
- `wiki/concepts/**/*.md`
- `wiki/explorations.md`
- `wiki/explorations/**/*.md`

Use `wiki/sources/**` only when a document page points to `full_text` or more
detail is needed. Do not use `.openwiki/**`, `.claude/**`, `.codex/**`,
`raw/**`, `wiki/log.md`, or `wiki/reports/**` as answer sources.

## Retrieval Flow

Use Wiki structure navigation and required qmd recall together:

1. Read `wiki/index.md` and relevant category indexes to understand the
   knowledge-base structure.
2. Run qmd search:

```bash
python3 -m openwiki.qmd search "<user question>" --kb-dir <kb-root> --limit 10
```

3. Use returned `wiki_path` values as candidate pages. If qmd reports a
   collection/setup issue, run setup and retry once:

```bash
python3 -m openwiki.qmd setup --kb-dir <kb-root>
```

If qmd is missing, stop and tell the user to rerun the OpenWiki installer after
installing Node.js/npm. qmd is required.
4. Merge qmd candidates with structure candidates and remove duplicates.
5. Read candidate `categories/**`, `concepts/**`, and `explorations/**` pages.
6. For PageIndex documents, use page ranges from the category document page to
   inspect `wiki/sources/<doc>.json` only as needed.

Do not let qmd replace the wiki structure. QMD is a recall layer; the wiki
index, category pages, and concepts remain the source of organization.

## Answer

1. Read the index and relevant category/concept pages.
2. Use qmd candidates, then verify by reading the actual files.
3. Answer from the local wiki. If evidence is missing, say so.
4. Cite sources with `[[wikilinks]]`.
5. End by offering to save the useful answer. Do not ask for a category yet.
6. If the user replies with `保存`, `save`, or an equivalent save request,
   list the available categories from `.openwiki/taxonomy.yaml` and ask which
   category directory to save into. If the user does not choose, save to
   `uncategorized`.

## Save Useful Answers

When the user confirms saving and chooses a category, you must actually create
the wiki note. Do not only say that it was saved.

1. Resolve the chosen category by id or display name from
   `.openwiki/taxonomy.yaml`; fall back to `uncategorized`.
2. Create the category exploration directory if needed.
3. Write the latest useful Q&A turn to:

```text
wiki/explorations/<category>/<slug>.md
```

4. Include frontmatter:

```yaml
---
type: exploration
category: <category>
created: <YYYY-MM-DD>
sources: []
---
```

5. Include the original question, the answer, and any cited `[[wikilinks]]`.
6. Update `wiki/explorations.md` with a link to the new note.
7. Update `wiki/categories/<category>/index.md` under `## Explorations` with
   the same link.
8. Only after the file and indexes are written, tell the user the exact saved
   path. If file writing is unavailable, say that saving could not be completed
   instead of claiming success.
9. After saving succeeds or fails, stay in the current `/openwiki-chat` flow
   and ask what the user wants to explore next.
