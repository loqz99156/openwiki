"""QMD retrieval helpers for OpenWiki chat skills.

QMD is an external CLI, not a Python dependency. OpenWiki installers require it,
and these helpers keep qmd results scoped to the human-readable wiki layer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

ALLOWED_MARKDOWN_ROOTS = ("categories/", "concepts/", "explorations/")
ALLOWED_MARKDOWN_FILES = {"index.md", "explorations.md"}
EXCLUDED_MARKDOWN_ROOTS = ("sources/", "reports/")
EXCLUDED_MARKDOWN_FILES = {"AGENTS.md", "log.md"}
DEFAULT_RETRIEVAL = {
    "engine": "auto",
    "qmd_mode": "search",
    "fallback": "wiki_structure",
}


def _load_retrieval(kb_dir: Path) -> dict[str, Any]:
    """Load retrieval config without making qmd helper depend on PyYAML."""
    config_path = kb_dir / ".openwiki" / "config.yaml"
    if not config_path.exists():
        return dict(DEFAULT_RETRIEVAL)
    try:
        import yaml
    except ImportError:
        return dict(DEFAULT_RETRIEVAL)
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    retrieval = data.get("retrieval", {})
    if not isinstance(retrieval, dict):
        return dict(DEFAULT_RETRIEVAL)
    merged = dict(DEFAULT_RETRIEVAL)
    merged.update(retrieval)
    return merged


def qmd_available() -> bool:
    """Return True when the qmd executable is available on PATH."""
    return shutil.which("qmd") is not None


def collection_name(kb_dir: Path) -> str:
    """Return a deterministic QMD collection name for a KB directory."""
    retrieval = _load_retrieval(kb_dir)
    configured = retrieval.get("qmd_collection")
    if configured:
        return str(configured)
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", kb_dir.name).strip("-").lower() or "kb"
    digest = hashlib.sha1(str(kb_dir.resolve()).encode("utf-8")).hexdigest()[:8]
    return f"openwiki-{slug}-{digest}"


def is_allowed_wiki_markdown(path: str | Path) -> bool:
    """Return True if a wiki-relative Markdown path is in the qmd search layer."""
    rel = str(path).replace("\\", "/").lstrip("/")
    if rel.startswith("wiki/"):
        rel = rel[len("wiki/"):]
    if not rel.endswith(".md"):
        return False
    if rel in EXCLUDED_MARKDOWN_FILES:
        return False
    if any(rel.startswith(prefix) for prefix in EXCLUDED_MARKDOWN_ROOTS):
        return False
    if rel in ALLOWED_MARKDOWN_FILES:
        return True
    return any(rel.startswith(prefix) for prefix in ALLOWED_MARKDOWN_ROOTS)


def normalize_result_file(file_value: str, kb_dir: Path) -> str | None:
    """Normalize a qmd result path to a wiki-relative path and filter it."""
    if not file_value:
        return None
    raw = str(file_value).replace("\\", "/")
    name = collection_name(kb_dir)
    if raw.startswith("qmd://"):
        raw = raw[len("qmd://"):]
    if raw.startswith(f"{name}/"):
        raw = raw[len(name) + 1:]

    path = Path(raw)
    wiki_dir = (kb_dir / "wiki").resolve()
    if path.is_absolute():
        try:
            raw = str(path.resolve().relative_to(wiki_dir)).replace("\\", "/")
        except ValueError:
            return None
    elif raw.startswith("wiki/"):
        raw = raw[len("wiki/"):]

    return raw if is_allowed_wiki_markdown(raw) else None


def _result_file(result: dict[str, Any]) -> str:
    for key in ("file", "path", "filename", "document", "source"):
        value = result.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def filter_results(results: list[dict[str, Any]], kb_dir: Path) -> list[dict[str, Any]]:
    """Filter qmd JSON results to OpenWiki's human-readable wiki layer."""
    filtered: list[dict[str, Any]] = []
    seen: set[str] = set()
    for result in results:
        rel = normalize_result_file(_result_file(result), kb_dir)
        if rel is None or rel in seen:
            continue
        item = dict(result)
        item["wiki_path"] = rel
        seen.add(rel)
        filtered.append(item)
    return filtered


def setup_collection(kb_dir: Path, name: str | None = None) -> subprocess.CompletedProcess[str]:
    """Create or refresh the QMD collection for a KB's wiki directory.

    Skills should call this after the KB wiki scaffold exists.
    """
    coll = name or collection_name(kb_dir)
    return subprocess.run(
        ["qmd", "collection", "add", str(kb_dir / "wiki"), "--name", coll, "--mask", "**/*.md"],
        text=True,
        capture_output=True,
        check=False,
    )


def search(kb_dir: Path, query: str, limit: int = 10, mode: str | None = None) -> dict[str, Any]:
    """Run a light qmd search and return filtered JSON results.

    ``mode`` defaults to config ``retrieval.qmd_mode`` and should usually be
    ``search`` for BM25 keyword retrieval. ``query`` is allowed but heavier.
    """
    coll = collection_name(kb_dir)
    retrieval = _load_retrieval(kb_dir)
    if not qmd_available():
        return {
            "available": False,
            "collection": coll,
            "results": [],
            "fallback": retrieval.get("fallback", "wiki_structure"),
            "reason": "qmd executable not found on PATH",
        }

    qmd_mode = mode or retrieval.get("qmd_mode", "search")
    if qmd_mode not in {"search", "query", "vsearch"}:
        qmd_mode = "search"

    proc = subprocess.run(
        ["qmd", qmd_mode, query, "-c", coll, "--format", "json", "-n", str(limit)],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return {
            "available": True,
            "collection": coll,
            "results": [],
            "fallback": retrieval.get("fallback", "wiki_structure"),
            "reason": proc.stderr.strip() or proc.stdout.strip() or f"qmd exited {proc.returncode}",
            "setup_command": f"python3 -m openwiki.qmd setup --kb-dir {kb_dir}",
        }

    try:
        parsed = json.loads(proc.stdout or "[]")
    except json.JSONDecodeError:
        return {
            "available": True,
            "collection": coll,
            "results": [],
            "fallback": retrieval.get("fallback", "wiki_structure"),
            "reason": "qmd returned non-JSON output",
            "raw": proc.stdout,
        }
    if not isinstance(parsed, list):
        parsed = parsed.get("results", []) if isinstance(parsed, dict) else []
    return {
        "available": True,
        "collection": coll,
        "mode": qmd_mode,
        "results": filter_results(parsed, kb_dir),
        "fallback": retrieval.get("fallback", "wiki_structure"),
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="QMD helper for OpenWiki.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    status = sub.add_parser("status")
    status.add_argument("--kb-dir", default=".", help="OpenWiki KB root.")
    setup = sub.add_parser("setup")
    setup.add_argument("--kb-dir", default=".", help="OpenWiki KB root.")
    setup.add_argument("--name", default=None, help="Override qmd collection name.")
    find = sub.add_parser("search")
    find.add_argument("query")
    find.add_argument("--kb-dir", default=".", help="OpenWiki KB root.")
    find.add_argument("-n", "--limit", type=int, default=10)
    find.add_argument("--mode", choices=["search", "query", "vsearch"], default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    kb_dir = Path(args.kb_dir).resolve()
    if args.cmd == "status":
        print(json.dumps({
            "available": qmd_available(),
            "collection": collection_name(kb_dir),
            "fallback": _load_retrieval(kb_dir).get("fallback", "wiki_structure"),
            "setup_command": f"python3 -m openwiki.qmd setup --kb-dir {kb_dir}",
        }, ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "setup":
        if not qmd_available():
            print("qmd executable not found on PATH. Install QMD first.", flush=True)
            return 1
        proc = setup_collection(kb_dir, args.name)
        if proc.stdout:
            print(proc.stdout, end="")
        if proc.stderr:
            print(proc.stderr, end="")
        return proc.returncode
    if args.cmd == "search":
        print(json.dumps(search(kb_dir, args.query, args.limit, args.mode), ensure_ascii=False, indent=2))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
