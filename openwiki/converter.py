"""Document conversion pipeline for OpenWiki."""
from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

import pymupdf
from markitdown import MarkItDown

from openwiki.config import load_config
from openwiki.images import copy_relative_images, extract_base64_images, convert_pdf_with_images
from openwiki.state import HashRegistry

logger = logging.getLogger(__name__)

TEXT_EXTENSIONS = {".md", ".markdown", ".txt", ".csv"}
TEXT_ENCODINGS = ("utf-8-sig", "utf-8", "gb18030", "big5", "cp1252", "latin-1")
MOJIBAKE_MARKERS = ("Ã", "Â", "â", "ä", "å", "æ", "è", "é", "¤", "€", "�")


@dataclass
class ConvertResult:
    """Result returned by :func:`convert_document`."""

    raw_path: Path | None = None
    source_path: Path | None = None
    is_long_doc: bool = False
    skipped: bool = False
    file_hash: str | None = None  # For deferred hash registration


def get_pdf_page_count(path: Path) -> int:
    """Return the number of pages in the PDF at *path* using pymupdf."""
    with pymupdf.open(str(path)) as doc:
        return doc.page_count


def _decode_text_file(path: Path) -> str:
    """Read text-like sources without assuming every user file is UTF-8."""
    data = path.read_bytes()
    last_error: UnicodeDecodeError | None = None
    for encoding in TEXT_ENCODINGS:
        try:
            return data.decode(encoding)
        except UnicodeDecodeError as exc:
            last_error = exc
    if last_error:
        logger.warning("Falling back to replacement decoding for %s: %s", path, last_error)
    return data.decode("utf-8", errors="replace")


def _text_quality_score(text: str) -> int:
    """Higher is better; used only to accept obvious mojibake repairs."""
    cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    replacement = text.count("\ufffd")
    markers = sum(text.count(marker) for marker in MOJIBAKE_MARKERS)
    controls = sum(1 for ch in text if ord(ch) < 32 and ch not in "\n\r\t")
    return cjk * 2 - markers * 6 - replacement * 20 - controls * 20


def _repair_mojibake(text: str) -> str:
    """Repair common UTF-8 mojibake such as 'ä¸­æ–‡' when it is safe."""
    if not any(marker in text for marker in MOJIBAKE_MARKERS):
        return text

    candidates = [text]
    for wrong_encoding in ("latin-1", "cp1252"):
        try:
            candidates.append(text.encode(wrong_encoding).decode("utf-8"))
        except UnicodeError:
            pass

    best = max(candidates, key=_text_quality_score)
    if _text_quality_score(best) > _text_quality_score(text):
        return best
    return text


def _normalize_markdown_text(markdown: str) -> str:
    """Normalize converted text before it is persisted as UTF-8 markdown."""
    return _repair_mojibake(markdown).replace("\r\n", "\n").replace("\r", "\n")


def convert_document(src: Path, kb_dir: Path) -> ConvertResult:
    """Convert a document and integrate it into the knowledge base.

    Steps:
    1. Hash-check — skip if already known.
    2. Copy source to ``raw/``.
    3. If PDF and page count >= threshold → return :attr:`ConvertResult.is_long_doc`.
    4. If text-like — decode safely, process relative images, save to ``wiki/sources/``.
    5. Otherwise — run MarkItDown, normalize text, save to ``wiki/sources/``.
    6. Register hash in the registry.
    """
    # ------------------------------------------------------------------
    # Load config & state
    # ------------------------------------------------------------------
    openwiki_dir = kb_dir / ".openwiki"
    config = load_config(openwiki_dir / "config.yaml")
    threshold: int = config.get("pageindex_threshold", 20)
    registry = HashRegistry(openwiki_dir / "hashes.json")

    # ------------------------------------------------------------------
    # 1. Hash check
    # ------------------------------------------------------------------
    file_hash = HashRegistry.hash_file(src)
    if registry.is_known(file_hash):
        logger.info("Skipping already-known file: %s", src.name)
        return ConvertResult(skipped=True)

    # ------------------------------------------------------------------
    # 2. Copy to raw/
    # ------------------------------------------------------------------
    raw_dir = kb_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_dest = raw_dir / src.name
    if raw_dest.resolve() != src.resolve():
        shutil.copy2(src, raw_dest)

    # ------------------------------------------------------------------
    # 3. PDF long-doc detection
    # ------------------------------------------------------------------
    if src.suffix.lower() == ".pdf":
        page_count = get_pdf_page_count(src)
        if page_count >= threshold:
            logger.info(
                "Long PDF detected (%d pages >= %d threshold): %s",
                page_count,
                threshold,
                src.name,
            )
            return ConvertResult(raw_path=raw_dest, is_long_doc=True, file_hash=file_hash)

    # ------------------------------------------------------------------
    # 4/5. Convert to Markdown
    # ------------------------------------------------------------------
    sources_dir = kb_dir / "wiki" / "sources"
    sources_dir.mkdir(parents=True, exist_ok=True)
    images_dir = kb_dir / "wiki" / "sources" / "images" / src.stem
    images_dir.mkdir(parents=True, exist_ok=True)

    doc_name = src.stem

    if src.suffix.lower() in TEXT_EXTENSIONS:
        markdown = _decode_text_file(src)
        markdown = copy_relative_images(markdown, src.parent, doc_name, images_dir)
    elif src.suffix.lower() == ".pdf":
        # Use pymupdf dict-mode for PDFs: text + images inline at correct positions
        markdown = convert_pdf_with_images(src, doc_name, images_dir)
    else:
        # Non-PDF, non-MD: use markitdown (docx, pptx, html, etc.)
        mid = MarkItDown()
        result = mid.convert(str(src))
        markdown = result.text_content
        markdown = extract_base64_images(markdown, doc_name, images_dir)

    markdown = _normalize_markdown_text(markdown)
    dest_md = sources_dir / f"{doc_name}.md"
    dest_md.write_text(markdown, encoding="utf-8")

    return ConvertResult(raw_path=raw_dest, source_path=dest_md, file_hash=file_hash)
