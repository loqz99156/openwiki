"""Taxonomy and document reclassification helpers for OpenWiki."""
from __future__ import annotations

import re
import shutil
import unicodedata
import json
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CATEGORY_ID = "uncategorized"
DEFAULT_CATEGORY_NAME = "未分类"

_SAFE_ID_RE = re.compile(r"[^\w\-]+")


def slugify(value: str) -> str:
    """Return a filesystem-safe id while preserving non-ASCII letters."""
    value = unicodedata.normalize("NFKC", value).strip().lower()
    value = _SAFE_ID_RE.sub("-", value).strip("-")
    return value or DEFAULT_CATEGORY_ID


def _taxonomy_path(kb_dir: Path) -> Path:
    return kb_dir / ".openwiki" / "taxonomy.yaml"


def taxonomy_exists(kb_dir: Path) -> bool:
    return _taxonomy_path(kb_dir).exists()


def parse_categories(text: str) -> list[dict[str, str]]:
    """Parse a comma/newline separated category list."""
    names = [part.strip() for part in re.split(r"[,，\n]", text) if part.strip()]
    seen: set[str] = set()
    categories: list[dict[str, str]] = []
    for name in names:
        category_id = DEFAULT_CATEGORY_ID if name == DEFAULT_CATEGORY_NAME else slugify(name)
        if category_id in seen:
            continue
        seen.add(category_id)
        categories.append({"id": category_id, "name": name, "description": ""})
    if DEFAULT_CATEGORY_ID not in seen:
        categories.append({
            "id": DEFAULT_CATEGORY_ID,
            "name": DEFAULT_CATEGORY_NAME,
            "description": "暂时无法自动归类或需要稍后整理的文档。",
        })
    return categories


def create_taxonomy(kb_dir: Path, purpose: str, categories_text: str) -> dict[str, Any]:
    """Create taxonomy.yaml and matching category index pages."""
    taxonomy = {
        "purpose": purpose.strip() or "个人知识库",
        "categories": parse_categories(categories_text or DEFAULT_CATEGORY_NAME),
    }
    path = _taxonomy_path(kb_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(taxonomy, allow_unicode=True, sort_keys=False), encoding="utf-8")
    ensure_category_pages(kb_dir, taxonomy)
    return taxonomy


def load_taxonomy(kb_dir: Path) -> dict[str, Any] | None:
    """Load taxonomy.yaml, returning None for legacy knowledge bases."""
    path = _taxonomy_path(kb_dir)
    if not path.exists():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    data.setdefault("purpose", "个人知识库")
    data["categories"] = parse_categories(
        "\n".join(c.get("name", "") for c in data.get("categories", []) if isinstance(c, dict))
    )
    return data


def category_ids(taxonomy: dict[str, Any]) -> set[str]:
    return {c["id"] for c in taxonomy.get("categories", [])}


def category_name(taxonomy: dict[str, Any], category_id: str) -> str:
    for category in taxonomy.get("categories", []):
        if category.get("id") == category_id:
            return category.get("name", category_id)
    return category_id


def category_dir(wiki_dir: Path, category_id: str) -> Path:
    return wiki_dir / "categories" / category_id


def category_index_path(wiki_dir: Path, category_id: str) -> Path:
    return category_dir(wiki_dir, category_id) / "index.md"


def category_document_path(wiki_dir: Path, category_id: str, doc_name: str) -> Path:
    return category_dir(wiki_dir, category_id) / f"{Path(doc_name).stem}.md"


def category_link(category_id: str) -> str:
    return f"categories/{category_id}/index"


def _ensure_category_dir(wiki_dir: Path, category_id: str) -> Path:
    """Create category directory and migrate an old flat category page if present."""
    categories_dir = wiki_dir / "categories"
    categories_dir.mkdir(parents=True, exist_ok=True)
    cat_dir = categories_dir / category_id
    old_flat = categories_dir / f"{category_id}.md"
    index_path = cat_dir / "index.md"

    if old_flat.exists() and not cat_dir.exists():
        cat_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(old_flat), str(index_path))
    else:
        cat_dir.mkdir(parents=True, exist_ok=True)
    return cat_dir


def resolve_category_id(taxonomy: dict[str, Any], value: str) -> str | None:
    """Resolve a user-provided category id or display name."""
    raw = value.strip()
    normalized = slugify(raw)
    for category in taxonomy.get("categories", []):
        if category.get("id") == raw or category.get("id") == normalized:
            return category["id"]
        if category.get("name") == raw or slugify(category.get("name", "")) == normalized:
            return category["id"]
    if raw == DEFAULT_CATEGORY_NAME:
        return DEFAULT_CATEGORY_ID
    return None


def taxonomy_prompt(taxonomy: dict[str, Any]) -> str:
    lines = [f"Knowledge base purpose: {taxonomy.get('purpose', '')}", "", "Allowed categories:"]
    for category in taxonomy.get("categories", []):
        desc = category.get("description") or category.get("name", "")
        lines.append(f"- {category['id']}: {category.get('name', category['id'])} — {desc}")
    return "\n".join(lines)


def ensure_category_pages(kb_dir: Path, taxonomy: dict[str, Any] | None = None) -> None:
    if taxonomy is None:
        taxonomy = load_taxonomy(kb_dir)
    if taxonomy is None:
        return

    categories_dir = kb_dir / "wiki" / "categories"
    categories_dir.mkdir(parents=True, exist_ok=True)
    for category in taxonomy.get("categories", []):
        category_id = category["id"]
        _ensure_category_dir(kb_dir / "wiki", category_id)
        path = category_index_path(kb_dir / "wiki", category_id)
        if path.exists():
            continue
        name = category.get("name", category_id)
        desc = category.get("description", "")
        body = f"# {name}\n\n{desc}\n\n## Documents\n\n"
        path.write_text(body, encoding="utf-8")
    _sync_categories_index(kb_dir, taxonomy)


def _sync_categories_index(kb_dir: Path, taxonomy: dict[str, Any]) -> None:
    index_path = kb_dir / "wiki" / "index.md"
    if not index_path.exists():
        return
    text = index_path.read_text(encoding="utf-8")
    if "## Categories" not in text:
        text = text.replace("# Knowledge Base Index\n", "# Knowledge Base Index\n\n## Categories\n", 1)
    lines = text.splitlines()
    bounds_start = None
    bounds_end = len(lines)
    for i, line in enumerate(lines):
        if line == "## Categories":
            bounds_start = i + 1
            continue
        if bounds_start is not None and i > bounds_start and line.startswith("## "):
            bounds_end = i
            break
    if bounds_start is None:
        return
    existing = "\n".join(lines[bounds_start:bounds_end])
    entries = []
    for category in taxonomy.get("categories", []):
        link = f"[[{category_link(category['id'])}]]"
        if link not in existing:
            entries.append(f"- {link} — {category.get('name', category['id'])}")
    if entries:
        lines[bounds_start:bounds_start] = entries
        index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_category_page(
    wiki_dir: Path,
    taxonomy: dict[str, Any],
    category_id: str,
    summary_link: str,
    doc_brief: str = "",
    doc_type: str = "short",
) -> None:
    categories_dir = wiki_dir / "categories"
    categories_dir.mkdir(parents=True, exist_ok=True)
    category_id = category_id if category_id in category_ids(taxonomy) else DEFAULT_CATEGORY_ID
    _ensure_category_dir(wiki_dir, category_id)
    path = category_index_path(wiki_dir, category_id)
    if not path.exists():
        name = category_name(taxonomy, category_id)
        path.write_text(f"# {name}\n\n## Documents\n\n", encoding="utf-8")

    text = path.read_text(encoding="utf-8")
    link = f"[[{summary_link}]]"
    entry = f"- {link} ({doc_type})"
    if doc_brief:
        entry += f" — {doc_brief}"
    if link in text:
        lines = [entry if line.startswith(f"- {link}") else line for line in text.splitlines()]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return
    if "## Documents" not in text:
        text = text.rstrip() + "\n\n## Documents\n\n"
    text = text.replace("## Documents\n", f"## Documents\n{entry}\n", 1)
    path.write_text(text, encoding="utf-8")


def update_category_exploration(
    wiki_dir: Path,
    taxonomy: dict[str, Any],
    category_id: str,
    exploration_link: str,
    brief: str = "",
) -> None:
    categories_dir = wiki_dir / "categories"
    categories_dir.mkdir(parents=True, exist_ok=True)
    category_id = category_id if category_id in category_ids(taxonomy) else DEFAULT_CATEGORY_ID
    _ensure_category_dir(wiki_dir, category_id)
    path = category_index_path(wiki_dir, category_id)
    if not path.exists():
        name = category_name(taxonomy, category_id)
        path.write_text(f"# {name}\n\n## Documents\n\n## Explorations\n\n", encoding="utf-8")

    text = path.read_text(encoding="utf-8")
    link = f"[[{exploration_link}]]"
    entry = f"- {link}"
    if brief:
        entry += f" — {brief}"
    if link in text:
        lines = [entry if line.startswith(f"- {link}") else line for line in text.splitlines()]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return
    if "## Explorations" not in text:
        text = text.rstrip() + "\n\n## Explorations\n\n"
    text = text.replace("## Explorations\n", f"## Explorations\n{entry}\n", 1)
    path.write_text(text, encoding="utf-8")


def remove_category_link(wiki_dir: Path, summary_link: str) -> None:
    categories_dir = wiki_dir / "categories"
    if not categories_dir.exists():
        return
    link = f"[[{summary_link}]]"
    for path in categories_dir.rglob("*.md"):
        lines = path.read_text(encoding="utf-8").splitlines()
        kept = [line for line in lines if link not in line]
        if kept != lines:
            path.write_text("\n".join(kept) + "\n", encoding="utf-8")


def _replace_category(summary_text: str, category_id: str) -> str:
    if not summary_text.startswith("---"):
        return f"---\ncategory: {category_id}\n---\n\n{summary_text}"
    end = summary_text.find("---", 3)
    if end == -1:
        return f"---\ncategory: {category_id}\n---\n\n{summary_text}"
    fm = summary_text[:end + 3]
    body = summary_text[end + 3:]
    if "category:" in fm:
        fm = re.sub(r"category:.*", f"category: {category_id}", fm)
    else:
        fm = fm.replace("---\n", f"---\ncategory: {category_id}\n", 1)
    return fm + body


def _summary_link_for_path(wiki_dir: Path, path: Path) -> str:
    return str(path.relative_to(wiki_dir).with_suffix("")).replace("\\", "/")


def _replace_all_links(wiki_dir: Path, old_link: str, new_link: str) -> None:
    old = f"[[{old_link}]]"
    new = f"[[{new_link}]]"
    for path in wiki_dir.rglob("*.md"):
        if "sources" in path.relative_to(wiki_dir).parts:
            continue
        text = path.read_text(encoding="utf-8")
        updated = text.replace(old, new)
        if updated != text:
            path.write_text(updated, encoding="utf-8")


def reclassify_document(kb_dir: Path, doc_name: str, category_id: str) -> tuple[str, str]:
    """Move a document page to another category folder.

    Returns:
        Tuple of ``(old_summary_link, new_summary_link)``.
    """
    taxonomy = load_taxonomy(kb_dir)
    if taxonomy is None:
        raise ValueError("This knowledge base has no taxonomy. Run init in a new taxonomy-enabled KB.")
    resolved_category_id = resolve_category_id(taxonomy, category_id)
    if resolved_category_id is None:
        raise ValueError(f"Unknown category: {category_id}")
    category_id = resolved_category_id

    wiki_dir = kb_dir / "wiki"
    doc_stem = Path(doc_name).stem
    matches = [
        p for p in sorted((wiki_dir / "categories").rglob(f"{doc_stem}.md"))
        if p.name != "index.md"
    ]
    legacy_summaries = wiki_dir / "summaries"
    if legacy_summaries.exists():
        matches.extend(sorted(legacy_summaries.rglob(f"{doc_stem}.md")))
    if not matches:
        raise FileNotFoundError(f"Summary not found for document: {doc_name}")

    old_summary = matches[0]
    old_link = _summary_link_for_path(wiki_dir, old_summary)
    text = old_summary.read_text(encoding="utf-8")

    _ensure_category_dir(wiki_dir, category_id)
    new_summary = category_document_path(wiki_dir, category_id, doc_stem)
    new_link = _summary_link_for_path(wiki_dir, new_summary)
    if old_summary.resolve() != new_summary.resolve():
        if new_summary.exists():
            raise FileExistsError(f"Target category already has document: {new_link}")
        new_summary.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(old_summary), str(new_summary))
    new_summary.write_text(_replace_category(text, category_id), encoding="utf-8")

    _replace_all_links(wiki_dir, old_link, new_link)
    remove_category_link(wiki_dir, old_link)
    update_category_page(wiki_dir, taxonomy, category_id, new_link)
    hashes_path = kb_dir / ".openwiki" / "hashes.json"
    if hashes_path.exists():
        data = json.loads(hashes_path.read_text(encoding="utf-8") or "{}")
        for meta in data.values():
            if Path(meta.get("name", "")).stem == doc_name:
                meta["category"] = category_id
        hashes_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return old_link, new_link


def reclassify_exploration(kb_dir: Path, exploration_name: str, category_id: str) -> tuple[str, str]:
    """Move a saved exploration to another category and update category links."""
    taxonomy = load_taxonomy(kb_dir)
    if taxonomy is None:
        raise ValueError("This knowledge base has no taxonomy. Run init in a new taxonomy-enabled KB.")
    resolved_category_id = resolve_category_id(taxonomy, category_id)
    if resolved_category_id is None:
        raise ValueError(f"Unknown category: {category_id}")
    category_id = resolved_category_id

    wiki_dir = kb_dir / "wiki"
    explorations_dir = wiki_dir / "explorations"
    matches = sorted(explorations_dir.rglob(f"{Path(exploration_name).stem}.md"))
    if not matches:
        raise FileNotFoundError(f"Exploration not found: {exploration_name}")

    old_path = matches[0]
    old_link = _summary_link_for_path(wiki_dir, old_path)
    text = old_path.read_text(encoding="utf-8")

    new_dir = explorations_dir / category_id
    new_dir.mkdir(parents=True, exist_ok=True)
    new_path = new_dir / old_path.name
    new_link = _summary_link_for_path(wiki_dir, new_path)

    if old_path.resolve() != new_path.resolve():
        shutil.move(str(old_path), str(new_path))
    new_path.write_text(_replace_category(text, category_id), encoding="utf-8")

    _replace_all_links(wiki_dir, old_link, new_link)
    remove_category_link(wiki_dir, old_link)
    update_category_exploration(wiki_dir, taxonomy, category_id, new_link)
    return old_link, new_link
