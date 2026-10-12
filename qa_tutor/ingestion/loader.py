"""Combine any number of sources (files and links) into ONE text document, with caching."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from qa_tutor.config import Settings
from qa_tutor.ingestion.readers import (
    fetch_url, is_complete_pdf, is_pdf, is_url, read_html, read_pdf, read_text_file,
)

INCOMPLETE_PDF = (
    "{name} is not a complete PDF (the download may have been cut off). "
    "Save the full file from your browser and upload it instead."
)


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def clean_source(source: str) -> str:
    return source.strip().strip('"').strip("'")


def _fingerprint(source: str) -> str:
    """Identify a source. For local files, include size + modified time so edits are noticed."""
    path = Path(source)
    if not is_url(source) and path.exists():
        stat = path.stat()
        return f"{path.resolve()}|{stat.st_size}|{int(stat.st_mtime)}"
    return source


def sources_key(sources: list[str]) -> str:
    """One short id for a set of sources. All cache files for this set start with it."""
    return _hash("\n".join(sorted(_fingerprint(clean_source(s)) for s in sources)))


def save_upload(filename: str, data: bytes, cache_dir: Path) -> str:
    """Save a file uploaded in the UI and return its path. Same content = same file."""
    safe = re.sub(r"[^A-Za-z0-9._-]", "_", filename)
    folder = cache_dir / "uploads"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{hashlib.sha256(data).hexdigest()[:8]}_{safe}"
    if not path.exists():  # don't rewrite, so the modified time (and the cache) stays stable
        path.write_bytes(data)
    return str(path)


def read_source(source: str, settings: Settings) -> str:
    """Read one source (link or file path) and return plain text."""
    source = clean_source(source)

    if is_url(source):
        data = fetch_url(source)
        if not is_pdf(data):
            return read_html(data)
        if not is_complete_pdf(data):
            raise RuntimeError(INCOMPLETE_PDF.format(name=source))
        folder = settings.cache_dir / "downloads"
        folder.mkdir(parents=True, exist_ok=True)
        pdf_path = folder / f"{_hash(source)}.pdf"
        pdf_path.write_bytes(data)
        return read_pdf(pdf_path, settings.use_docling)

    path = Path(source).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}. Check the spelling and folder.")
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        if not is_complete_pdf(path.read_bytes()):
            raise RuntimeError(INCOMPLETE_PDF.format(name=path.name))
        return read_pdf(path, settings.use_docling)
    if suffix in {".txt", ".md"}:
        return read_text_file(path)
    raise ValueError(f"Unsupported file type '{suffix}'. Use PDF, TXT, MD, or a web link.")


def display_name(source: str) -> str:
    source = clean_source(source)
    return source if is_url(source) else Path(source).name


def load_sources(sources: list[str], settings: Settings) -> str:
    """Read every source, join them into one document, and cache the result."""
    cache_path = settings.cache_dir / f"{sources_key(sources)}.md"
    if cache_path.exists() and not settings.refresh_cache:
        return cache_path.read_text(encoding="utf-8")

    parts = [f"# Source: {display_name(s)}\n\n{read_source(s, settings)}" for s in sources]
    text = "\n\n---\n\n".join(parts)

    if len(text) > settings.max_document_chars:
        text = text[: settings.max_document_chars] + "\n\n[Document shortened to fit the model.]"

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(text, encoding="utf-8")
    return text
