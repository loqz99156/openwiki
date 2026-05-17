在当前知识库目录中初始化一个新的 OpenWiki 知识库。通常应先进入安装后创建的 `my-wiki/` 目录，再执行 `/init`。不要在 `/init` 中再创建 `my-wiki/` 子目录；也不要把知识库文件直接写进项目源码根目录或包含系统文件的目录。按以下步骤直接操作：

## 步骤

### 1. 确认当前目录是知识库目录
`/init` 必须在 `my-wiki/` 目录内执行。

如果当前目录名不是 `my-wiki`，或当前目录看起来是项目源码目录/系统目录（例如存在 `pyproject.toml`、`.git/`、`.claude/commands/`、`openwiki/`），不要初始化；提醒用户先进入安装后创建的 `my-wiki/` 目录再执行 `/init`。

如果当前目录已存在 `.openwiki/`，告知用户"知识库已经初始化过了"并停止。

### 2. 询问配置
询问用户以下内容：
- **模型**：默认 `gpt-5.4-mini`，使用 LiteLLM 格式（如 `anthropic/claude-sonnet-4-6`）
- **API Key**：可选，输入后写入 `.env`（设为 0600 权限）

### 3. 创建目录结构
在当前知识库目录下创建目录：
```bash
mkdir -p raw wiki/sources/images wiki/summaries wiki/concepts
```

### 4. 写入 wiki 文件

**wiki/AGENTS.md** — 写入以下内容：

```markdown
# Wiki Schema

## Directory Structure
- sources/ — Document content. Short docs as .md, long docs as .json (per-page). Do not modify directly.
- sources/images/ — Extracted images from documents, referenced by sources.
- summaries/ — One per source document. Summary of key content.
- concepts/ — Cross-document topic synthesis. Created when a theme spans multiple documents.
- explorations/ — Saved query results, analyses, and comparisons worth keeping.
- reports/ — Lint health check reports. Auto-generated.

## Special Files
- index.md — Content catalog: every page with link, one-line summary, organized by category.
- log.md — Chronological append-only record of operations (ingests, queries, lints).

## Page Types
- **Summary Page** (summaries/): Key content of a single source document.
- **Concept Page** (concepts/): Cross-document topic synthesis with [[wikilinks]].
- **Exploration Page** (explorations/): Saved query results — analyses, comparisons, syntheses.
- **Index Page** (index.md): One-liner summary of every page in the wiki. Auto-maintained.

## Index Page Format
index.md lists all documents, concepts, and explorations with metadata:
- Documents: name, one-liner description, type (short|pageindex), detail access path
- Concepts: name, one-liner description
- Explorations: name, one-liner description

## Log Format
Each log entry: `## [YYYY-MM-DD HH:MM:SS] operation | description`
Operations: ingest, query, lint

## Format
- Use [[wikilink]] to link other wiki pages (e.g., [[concepts/attention]])
- Standard Markdown heading hierarchy
- Keep each page focused on a single topic
- Do not include YAML frontmatter (---) in generated content; it is managed by code
```

**wiki/index.md**：
```markdown
# Knowledge Base Index

## Documents

## Concepts

## Explorations
```

**wiki/log.md**：
```markdown
# Operations Log
```

### 5. 创建 .openwiki/ 状态目录
```bash
mkdir -p .openwiki
```

写入 `.openwiki/config.yaml`：
```yaml
language: en
model: <用户选择的模型>
pageindex_threshold: 20
```

写入 `.openwiki/hashes.json`：
```json
{}
```

### 6. 写入 .env（如果用户提供了 API Key）
权限设为 0600：
```
LLM_API_KEY=<用户提供的key>
```

### 7. 注册到全局配置
读取 `~/.config/openwiki/global.yaml`（如不存在则视为空），将当前知识库目录的绝对路径加入 `known_kbs` 并设为 `default_kb`，写回。

### 8. 告知用户初始化完成
列出可用的下一步操作：
- `/add <文件>` 添加文档
- `/query 问题` 提问
- `/chat` 开始对话
