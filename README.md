<div align="center">

# OpenWiki - Open LLM Knowledge Base

<p align="center"><i>Continuously compile raw materials into readable, linkable, searchable Markdown wiki pages.</i></p>

<p align="center"><a href="README.cn.md">中文版</a></p>

</div>

---

## Introduction

OpenWiki is a local knowledge-base system for Obsidian, Claudian, Claude Code, Codex, and OpenClaw.

Instead of simply putting documents into a vector store and waiting for Q&A, OpenWiki converts, classifies, and compiles PDFs, Markdown, Word documents, PowerPoint files, HTML, spreadsheets, and text files into a plain Markdown wiki. You can read it in Obsidian, and you can use OpenWiki skills in Claudian, Claude Code, Codex, or OpenClaw to add materials, ask follow-up questions, save analysis, and organize categories.

Core capabilities:

- Create a knowledge-base directory that can be opened directly as an Obsidian vault.
- Organize knowledge with categories, document pages, concept pages, and exploration notes.
- Use qmd for local recall over user-visible Markdown wiki pages.
- Use PageIndex for PDFs of 30 pages or more, while keeping paged full-text traceability.
- Save valuable Q&A into `wiki/explorations/`, then reorganize them later if needed.

## qmd and PageIndex

OpenWiki does not rely on only one retrieval method. It separates regular wiki-page recall from long-document tracing: qmd quickly finds relevant Markdown pages, while PageIndex handles long PDFs.

### qmd: local recall over the wiki

qmd is OpenWiki's local retrieval layer. It searches the user-visible, readable Markdown wiki, not hidden state directories or raw files.

In OpenWiki, qmd mainly:

- Recalls relevant pages from `wiki/index.md`, `wiki/categories/`, `wiki/concepts/`, and `wiki/explorations/`.
- Helps `/openwiki-chat` find likely relevant document pages, concept pages, and saved explorations before answering.
- Works as a lightweight local search layer that complements the wiki category structure.

qmd does not search `raw/`, `.openwiki/`, `.codex/`, `.claude/`, or `wiki/sources/` by default. This keeps answers grounded in curated, user-readable knowledge-base content.

### PageIndex: structured tracing for long PDFs

PageIndex handles PDFs of 30 pages or more. Long PDFs are not suitable for sending to the model as one large full-text blob, so OpenWiki first uses PageIndex to build section structure and paged content.

In OpenWiki, PageIndex mainly:

- Generates structured tables of contents, section hierarchy, and page ranges for long PDFs.
- Stores paged full text in `wiki/sources/<document>.json`.
- Keeps the structure page and `full_text` pointer in the category document page, so details can be traced back by page.
- Lets `/openwiki-chat` return to specific pages when it needs long-PDF details, instead of relying only on summaries.

In short: qmd finds relevant pages in the curated wiki; PageIndex turns very long PDFs into traceable structure plus paged full text.

## Quick Start

Common requirements:

- Python 3.10 or later
- pip
- Git
- Node.js / npm, for the required qmd installation

### Option 1: Obsidian + Claudian

Install Obsidian first, then install the Claudian plugin in Obsidian.

#### Installation

```bash
git clone https://github.com/loqz99156/openwiki.git openwiki
cd openwiki
bash install.sh
```

On macOS, you can also double-click `install.command`. On Windows, use `install.bat` or `install.ps1`.

The installer prepares PageIndex and qmd together:

- Installs the `openwiki` Python package and Python dependencies, including PageIndex, MarkItDown, and PyMuPDF.
- Installs qmd through npm.
- Verifies that key dependencies such as PageIndex, qmd, and PyMuPDF are available.
- Creates the default knowledge-base directory `my-wiki/`.
- Installs the four OpenWiki skills into `my-wiki/.codex/skills/` and `my-wiki/.claude/skills/`.

After installation, finish plugin setup in Obsidian:

1. Open Obsidian.
2. Click `Obsidian vault` in the lower-left corner, then choose "Manage vaults".
3. Choose "Open local vault".
4. Select the installer-created `my-wiki/` as the vault folder.
5. Open Obsidian settings and enable community plugins.
6. Browse the community plugin marketplace, search for Claudian, and install it.
7. Enable the Claudian plugin.
8. In the Claude tab of the Claudian plugin, find `Commands and Skills` and confirm that `openwiki-init`, `openwiki-add`, `openwiki-chat`, and `openwiki-category` are loaded.

#### Usage

Open the whole knowledge-base directory in Obsidian:

```text
my-wiki/
```

It is both the Obsidian vault and the OpenWiki knowledge-base root. After initialization, you mainly read `wiki/index.md`, `wiki/categories/`, `wiki/concepts/`, and `wiki/explorations/`.

Do not initialize a knowledge base inside the OpenWiki source repository.

Initialize the knowledge base:

In the Obsidian Claudian chat box, enter:

```text
/openwiki-init
```

Then follow the prompts to fill in the knowledge-base purpose and categories. You can also write it in one line:

```text
/openwiki-init Initialize this knowledge base. Purpose: personal knowledge base. Categories: AI, history, investing.
```

`openwiki-init` creates `.openwiki/`, `raw/`, and `wiki/`, writes the taxonomy, and keeps a default `Uncategorized` category.

Add materials:

Put raw files into:

```text
my-wiki/raw/
```

Then enter:

```text
/openwiki-add
```

`/openwiki-add` automatically processes new documents in `raw/` that have not been added yet. You can also specify a file or directory:

```text
/openwiki-add add paper.pdf
/openwiki-add add documents from ~/Documents/research
```

Ask questions and save answers:

```text
/openwiki-chat
```

`/openwiki-chat` enters the knowledge-base Q&A flow and then accepts follow-up questions. You can also include a question directly:

```text
/openwiki-chat Answer from this knowledge base: what are the main findings in these materials?
```

`/openwiki-chat` first reads the knowledge-base structure, then uses qmd to recall related Markdown pages. It does not rerun PageIndex during chat. Only when a matched long-PDF document page has a `full_text` pointer and more detail is needed will it read the paged full text that PageIndex already generated. Answers should come from the local wiki; if evidence is missing, it should say so.

If an answer is worth keeping, just reply with `save`. The system will ask which category directory to save into, then write the Q&A as a wiki note under `wiki/explorations/<category>/`, update the exploration index, and update the corresponding category page. After saving, you stay in the same `/openwiki-chat` conversation and can continue asking follow-up questions; you do not need to enter `/openwiki-chat` again.

Organize categories:

```text
/openwiki-category
/openwiki-category list categories
/openwiki-category move paper to AI
/openwiki-category add a category called Product
```

If you enter only `/openwiki-category`, the system lists available category actions first and asks what you want to do next.

Category changes move only user-visible document pages or exploration notes. They do not move stable source content under `wiki/sources/`.

### Option 2: OpenClaw

OpenClaw does not require entering Obsidian or installing Claudian. Its role is to call the same OpenWiki skills for you from its own chat window.

OpenClaw can use four OpenWiki skills:

- `/openwiki-init` initializes a specified knowledge-base directory and creates `.openwiki/`, `raw/`, `wiki/`, the taxonomy, and OpenWiki skills.
- `/openwiki-add` adds materials by placing uploaded or specified files into the current knowledge base's `raw/`, then converting, classifying, and writing to `wiki/categories/<category>/`, `wiki/sources/`, `wiki/concepts/`, and index pages.
- `/openwiki-chat` asks questions, follows up, and compares using the current knowledge base's `wiki/` content. Answers come from the local wiki; useful answers are saved to `wiki/explorations/<category>/`.
- `/openwiki-category` organizes categories in the current knowledge base. It moves user-visible document pages or exploration notes, but does not move stable source content under `wiki/sources/`.

#### Installation

Send this message directly to OpenClaw:

```text
Please install OpenWiki for me: clone https://github.com/loqz99156/openwiki.git into a local folder named openwiki, enter that folder, and run the one-click installer for the current operating system. After installation, confirm that my-wiki/ has been created, and use my-wiki/ as the knowledge base I want to operate. After that, initialize and use this knowledge base through OpenWiki skills.
```

#### Usage

When OpenClaw uses OpenWiki, it must first determine the current knowledge base. If the user explicitly names a knowledge-base directory, operate on that directory. If not, use the default knowledge base.

When OpenClaw receives a natural-language request, it should route it to the matching skill:

- Add files, save uploaded files, import materials: call `/openwiki-add`.
- Ask, follow up, summarize, or compare based on the knowledge base: call `/openwiki-chat`.
- Save the current Q&A: stay in the current `/openwiki-chat`, ask for a category, then write an exploration note.
- View, move, add, rename, or delete categories: call `/openwiki-category`.

Common examples:

Initialize:

```text
Use my-wiki/ as the current knowledge base, call /openwiki-init to initialize it, and ask me for the knowledge-base purpose and categories during initialization.
```

OpenClaw should call `/openwiki-init` and let the user fill in the purpose and categories.

Add an uploaded file:

```text
Save the file I just uploaded into the my-wiki/ knowledge base.
```

OpenClaw should place the uploaded file into `my-wiki/raw/`, then call `/openwiki-add` to process the new document. When done, it should tell the user which category document page was generated.

Add a file or directory by path:

```text
Add ~/Downloads/paper.pdf to the my-wiki/ knowledge base.
```

OpenClaw should call `/openwiki-add`, copy the file into `my-wiki/raw/`, and then add it.

Ask from the knowledge base:

```text
In the my-wiki/ knowledge base, answer: how many years did Chinese emperors reign?
```

OpenClaw should call `/openwiki-chat` and answer based on the local content under `my-wiki/wiki/`. After entering `/openwiki-chat`, if the user has not switched to another skill, it should remain in the same knowledge-base Q&A state.

Save an answer:

```text
Save
```

OpenClaw should stay in the current `/openwiki-chat` state, ask which category to save into, write the Q&A to `my-wiki/wiki/explorations/<category>/`, and update `wiki/explorations.md` plus the corresponding category page.

Organize categories:

```text
Organize categories in the my-wiki/ knowledge base.
```

OpenClaw should call `/openwiki-category`. If no further detail is provided, it should list the available category actions and ask the user what to do next.

Move a document category:

```text
Move paper in the my-wiki/ knowledge base to the AI category.
```

OpenClaw should call `/openwiki-category`, move the user-visible document page under `wiki/categories/`, and update indexes, frontmatter, and links.

## Structure

An initialized knowledge base looks roughly like this:

```text
my-wiki/
  .openwiki/                    OpenWiki internal state and configuration
    config.yaml                 Knowledge-base configuration
    hashes.json                 Hash records for processed documents
    taxonomy.yaml               Category taxonomy
    chats/                      Chat session records
  .codex/                       Local skills available to Codex
    skills/openwiki-init/       Initialize the knowledge base
    skills/openwiki-add/        Add materials
    skills/openwiki-chat/       Knowledge-base Q&A
    skills/openwiki-category/   Category organization
  .claude/                      Local skills available to Claude Code / Claudian
    skills/openwiki-init/       Initialize the knowledge base
    skills/openwiki-add/        Add materials
    skills/openwiki-chat/       Knowledge-base Q&A
    skills/openwiki-category/   Category organization
  raw/                          Put original materials here
  wiki/                         User-readable and searchable Markdown knowledge base
    AGENTS.md                   Knowledge-base schema and LLM editing rules
    index.md                    Main knowledge-base index
    explorations.md             Entry page for saved explorations
    log.md                      Operation log
    sources/                    Stable converted source content
      images/                   Images extracted from documents
    concepts/                   Cross-document concept pages
    categories/                 User-visible document pages by category
      uncategorized/            Uncategorized content
        index.md                Uncategorized entry page
    explorations/               Saved Q&A, analyses, and comparisons
```

Important boundaries:

- `raw/` stores original materials.
- `wiki/` is the user-readable Markdown knowledge base.
- `wiki/sources/` stores stable converted source content. Do not move it during classification.
- `wiki/categories/<category>/` stores user-visible category document pages.
- `wiki/concepts/` stores cross-document concept pages.
- `wiki/explorations/` stores saved Q&A, analyses, and comparisons.
- `.openwiki/` stores configuration, hashes, sessions, and state.
- `wiki/AGENTS.md` inside the knowledge base is the runtime wiki schema generated by OpenWiki initialization.

## Principles

OpenWiki maintains the knowledge base in three layers.

The first layer is mechanical conversion. Short documents are converted to Markdown. Text and Markdown files are decoded safely. Office, HTML, and similar formats are converted through MarkItDown. Short PDFs have text and images extracted. PDFs of 30 pages or more go through PageIndex, which generates a structure page and paged full text.

The second layer is LLM compilation. Based on converted content and the current taxonomy, the model generates user-readable category document pages, short index descriptions, concept pages, and cross-links. For long PDFs, OpenWiki does not duplicate the entire body into the document page. Instead, the category page keeps structure, page ranges, and a `full_text: sources/<document>.json` pointer.

The third layer is retrieval and tracing. `openwiki-chat` first follows `index.md`, category pages, and concept pages to understand the knowledge base, then uses qmd to recall candidate pages from the user-visible Markdown layer. qmd does not search `raw/`, `.openwiki/`, `.codex/`, `.claude/`, or `wiki/sources/`. When long-PDF details are needed, OpenWiki follows the document-page pointer to read paged source content.

Default configuration is stored at:

```text
my-wiki/.openwiki/config.yaml
```

Common fields:

```yaml
language: en
model: gpt-5.4-mini
pageindex_threshold: 30
retrieval:
  engine: auto
  qmd_mode: search
  fallback: wiki_structure
```

The normal Claudian, Claude Code, and Codex skill paths do not require you to manually enter a model or API key. Model capability comes from the current session.

## Flow

```text
Install OpenWiki
  |
  v
Create or enter the knowledge-base directory
  |
  v
/openwiki-init
  |
  v
Put original materials into raw/
  |
  v
/openwiki-add
  |
  +-- Short documents -> Markdown -> category document pages
  |
  +-- Long PDFs -> PageIndex -> structure page + paged full text
  |
  v
Update categories/, concepts/, index.md, and log.md
  |
  v
/openwiki-chat ask, compare, summarize
  |
  +-- Read index.md, categories/, and concepts/ first
  |
  +-- Use qmd to recall related Markdown pages
  |
  +-- If long-PDF details are needed, trace through PageIndex paged full text
  |
  v
Save to explorations/, then reorganize with /openwiki-category if needed
```

When adding documents, OpenWiki registers the hash only after conversion, indexing, and LLM compilation all succeed. This prevents failed partial outputs from being treated as completed documents.

## License

Apache License 2.0. See [LICENSE](LICENSE).
