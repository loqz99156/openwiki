from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from openwiki import qmd


def test_allowed_wiki_markdown_paths():
    assert qmd.is_allowed_wiki_markdown("index.md")
    assert qmd.is_allowed_wiki_markdown("explorations.md")
    assert qmd.is_allowed_wiki_markdown("categories/ai/paper.md")
    assert qmd.is_allowed_wiki_markdown("concepts/attention.md")
    assert qmd.is_allowed_wiki_markdown("explorations/ai/result.md")


def test_disallowed_wiki_markdown_paths():
    assert not qmd.is_allowed_wiki_markdown("sources/paper.md")
    assert not qmd.is_allowed_wiki_markdown("reports/lint.md")
    assert not qmd.is_allowed_wiki_markdown("AGENTS.md")
    assert not qmd.is_allowed_wiki_markdown("log.md")
    assert not qmd.is_allowed_wiki_markdown("raw/paper.md")


def test_normalize_result_file_filters_to_wiki_layer(tmp_path):
    kb = tmp_path / "my-wiki"
    wiki = kb / "wiki"
    wiki.mkdir(parents=True)
    assert qmd.normalize_result_file(str(wiki / "categories" / "ai" / "paper.md"), kb) == "categories/ai/paper.md"
    assert qmd.normalize_result_file(str(wiki / "sources" / "paper.md"), kb) is None
    assert qmd.normalize_result_file(str(tmp_path / "elsewhere.md"), kb) is None


def test_filter_results_adds_wiki_path_and_dedupes(tmp_path):
    kb = tmp_path / "kb"
    results = [
        {"file": "categories/ai/paper.md", "score": 1},
        {"file": "categories/ai/paper.md", "score": 0.9},
        {"file": "sources/paper.md", "score": 0.8},
        {"path": "concepts/attention.md", "score": 0.7},
    ]
    filtered = qmd.filter_results(results, kb)
    assert [item["wiki_path"] for item in filtered] == [
        "categories/ai/paper.md",
        "concepts/attention.md",
    ]


def test_search_reports_required_qmd_missing(tmp_path):
    with patch("openwiki.qmd.qmd_available", return_value=False):
        result = qmd.search(tmp_path, "attention")
    assert result["available"] is False
    assert result["fallback"] == "wiki_structure"
    assert result["results"] == []


def test_search_parses_and_filters_json(tmp_path):
    proc = MagicMock()
    proc.returncode = 0
    proc.stdout = '[{"file":"categories/ai/paper.md","score":1},{"file":"sources/paper.md","score":1}]'
    proc.stderr = ""
    with patch("openwiki.qmd.qmd_available", return_value=True), \
         patch("openwiki.qmd.subprocess.run", return_value=proc):
        result = qmd.search(tmp_path, "attention")
    assert result["available"] is True
    assert [item["wiki_path"] for item in result["results"]] == ["categories/ai/paper.md"]
