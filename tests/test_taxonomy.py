"""Tests for taxonomy category assignment helpers."""
from __future__ import annotations

import json

from openwiki.taxonomy import create_taxonomy, reclassify_document


def test_reclassify_document_moves_document_page_but_keeps_source_path(tmp_path):
    create_taxonomy(tmp_path, "Research", "AI, Product")
    wiki = tmp_path / "wiki"
    (wiki / "summaries").mkdir(parents=True, exist_ok=True)
    (wiki / "sources").mkdir(parents=True, exist_ok=True)
    (wiki / "index.md").write_text(
        "# Knowledge Base Index\n\n## Categories\n\n## Documents\n\n## Concepts\n",
        encoding="utf-8",
    )
    (wiki / "summaries" / "paper.md").write_text(
        "---\ndoc_type: short\nfull_text: sources/paper.md\ncategory: product\n---\n\n# Paper\n",
        encoding="utf-8",
    )
    (wiki / "sources" / "paper.md").write_text("# Source\n", encoding="utf-8")
    hashes_path = tmp_path / ".openwiki" / "hashes.json"
    hashes_path.write_text(
        json.dumps({"abc": {"name": "paper.pdf", "type": "pdf", "category": "product"}}),
        encoding="utf-8",
    )

    old_link, new_link = reclassify_document(tmp_path, "paper", "AI")

    assert old_link == "summaries/paper"
    assert new_link == "categories/ai/paper"
    assert not (wiki / "summaries" / "paper.md").exists()
    assert (wiki / "categories" / "ai" / "paper.md").is_file()
    assert (wiki / "sources" / "paper.md").is_file()
    assert not (wiki / "sources" / "ai").exists()
    summary_text = (wiki / "categories" / "ai" / "paper.md").read_text(encoding="utf-8")
    assert "category: ai" in summary_text
    category_text = (wiki / "categories" / "ai" / "index.md").read_text(encoding="utf-8")
    assert "[[categories/ai/paper]]" in category_text
    hashes = json.loads(hashes_path.read_text(encoding="utf-8"))
    assert hashes["abc"]["category"] == "ai"
