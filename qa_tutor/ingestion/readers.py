"""Small functions that turn ONE thing (PDF, web page, text file) into plain text."""
from __future__ import annotations

import urllib.request
from pathlib import Path

MAX_DOWNLOAD_BYTES = 100 * 1024 * 1024


def is_url(text: str) -> bool:
    return text.lower().startswith(("http://", "https://"))


def fetch_url(url: str) -> bytes:
    """Download a link and return its raw bytes."""
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read(MAX_DOWNLOAD_BYTES + 1)
    if len(data) > MAX_DOWNLOAD_BYTES:
        raise ValueError(f"File at {url} is larger than 100 MB.")
    return data


def is_pdf(data: bytes) -> bool:
    return data[:1024].lstrip().startswith(b"%PDF-")


def is_complete_pdf(data: bytes) -> bool:
    """A finished PDF ends with 'startxref' and '%%EOF'. Truncated downloads don't."""
    tail = data[-65536:]
    return is_pdf(data) and b"startxref" in tail and b"%%EOF" in tail


def read_pdf(path: Path, use_docling: bool = False) -> str:
    if use_docling:
        try:
            from docling.document_converter import DocumentConverter

            return DocumentConverter().convert(str(path)).document.export_to_markdown()
        except Exception as error:  # Docling is heavy; fall back to the simple reader
            print(f"Docling failed ({type(error).__name__}); using pypdf instead.")

    from pypdf import PdfReader

    pages = []
    for number, page in enumerate(PdfReader(str(path), strict=False).pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append(f"## Page {number}\n\n{text}")
    if not pages:
        raise ValueError(f"No text found in {path.name}. It may be a scanned PDF (images only).")
    return "\n\n".join(pages)


def read_html(data: bytes) -> str:
    """Pull the readable text out of a web page."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(data, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "noscript"]):
        tag.decompose()
    root = soup.find("main") or soup.find("article") or soup.body or soup
    lines = (line.strip() for line in root.get_text("\n").splitlines())
    text = "\n".join(line for line in lines if line)
    if len(text) < 200:
        raise ValueError(
            "Very little readable text was found on that page. It may need JavaScript "
            "or a login. Try saving the page as a PDF and uploading it instead."
        )
    return text


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")
