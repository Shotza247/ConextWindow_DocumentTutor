import pytest

from qa_tutor.config import Settings
from qa_tutor.ingestion.loader import load_sources, save_upload, sources_key
from qa_tutor.ingestion.readers import is_complete_pdf, read_html


def test_html_keeps_article_text_and_drops_scripts():
    body = "Caching is useful. " * 20
    html = f"<html><body><nav>MENU</nav><script>bad()</script><article>{body}</article></body></html>"
    text = read_html(html.encode())
    assert "Caching is useful." in text and "MENU" not in text and "bad()" not in text


def test_html_with_no_text_gives_helpful_error():
    with pytest.raises(ValueError, match="JavaScript"):
        read_html(b"<html><body><div id='app'></div></body></html>")


def test_truncated_pdf_is_detected():
    assert not is_complete_pdf(b"%PDF-1.6 " + b"x" * 5000)
    assert is_complete_pdf(b"%PDF-1.6 " + b"x" * 5000 + b"\nstartxref\n0\n%%EOF")


def test_multiple_sources_are_combined_and_cached(tmp_path):
    a, b = tmp_path / "a.txt", tmp_path / "b.md"
    a.write_text("Alpha text", encoding="utf-8")
    b.write_text("Beta text", encoding="utf-8")
    settings = Settings(cache_dir=tmp_path / "cache")

    text = load_sources([str(a), str(b)], settings)
    assert "# Source: a.txt" in text and "Beta text" in text
    assert (settings.cache_dir / f"{sources_key([str(a), str(b)])}.md").exists()


def test_long_documents_are_shortened(tmp_path):
    a = tmp_path / "a.txt"
    a.write_text("x" * 500, encoding="utf-8")
    text = load_sources([str(a)], Settings(cache_dir=tmp_path / "c", max_document_chars=100))
    assert "shortened" in text


def test_missing_file_message(tmp_path):
    with pytest.raises(FileNotFoundError, match="not found"):
        load_sources([str(tmp_path / "nope.pdf")], Settings(cache_dir=tmp_path))


def test_save_upload_is_stable(tmp_path):
    first = save_upload("My Notes.pdf", b"data", tmp_path)
    assert first == save_upload("My Notes.pdf", b"data", tmp_path)
    assert " " not in first
