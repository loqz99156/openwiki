from __future__ import annotations

from pathlib import Path

AGENTS_MD = """\
# Wiki Schema

## Directory Structure
- sources/ — Stable converted document content. Short docs as .md, long docs as .json (per-page). Do not modify directly or group by category.
- sources/images/ — Extracted images from documents, referenced by sources.
- categories/<category>/ — User-facing document pages grouped by category. Short documents keep converted Markdown content here; PageIndex long documents keep a structure page here and point to full paged content in sources/.
- concepts/ — Cross-document topic synthesis. Created when a theme spans multiple documents.
- explorations/ — Saved query results, analyses, and comparisons worth keeping.
- reports/ — Lint health check reports. Auto-generated.

## Special Files
- index.md — Content catalog: documents and concepts with one-line summaries. Explorations links to explorations.md.
- explorations.md — Saved explorations with one-line summaries. Linked from index.md.
- log.md — Chronological append-only record of operations (ingests, queries, lints).

## Page Types
- **Short Document Page** (categories/<category>/<document>.md, doc_type: short): Converted Markdown source content with light frontmatter and concept backlinks.
- **PageIndex Document Page** (categories/<category>/<document>.md, doc_type: pageindex): PageIndex structure page with section/page ranges and `full_text: sources/<document>.json`; use paged source content for details.
- **Concept Page** (concepts/): Cross-document topic synthesis with [[wikilinks]].
- **Category Index** (categories/<category>/index.md): Curated document list for one taxonomy category.
- **Exploration Page** (explorations/): Saved query results — analyses, comparisons, syntheses.
- **Index Page** (index.md): One-liner summary of every page in the wiki. Auto-maintained.

## Index Page Format
index.md lists all documents and concepts with metadata:
- Categories: links to categories/<category>/index.md
- Documents: name, one-liner description, type (short|pageindex), category document path
- Concepts: name, one-liner description
- Explorations: links to explorations.md for the full list

explorations.md lists saved explorations with name and one-liner description.

## Log Format
Each log entry: `## [YYYY-MM-DD HH:MM:SS] operation | description`
Operations: ingest, query, lint

## Format
- Use [[wikilink]] to link other wiki pages (e.g., [[concepts/attention]])
- Standard Markdown heading hierarchy
- Keep each page focused on a single topic
- Do not include YAML frontmatter (---) in generated content; it is managed by code
"""

# Backward compat alias
SCHEMA_MD = AGENTS_MD


def get_agents_md(wiki_dir: Path) -> str:
    """Return the AGENTS.md content, reading from disk if available.

    Args:
        wiki_dir: Path to the wiki directory (containing AGENTS.md).

    Returns:
        Content of wiki_dir/AGENTS.md if it exists, otherwise the hardcoded
        AGENTS_MD default.
    """
    agents_file = wiki_dir / "AGENTS.md"
    if agents_file.exists():
        return agents_file.read_text(encoding="utf-8")
    return AGENTS_MD
