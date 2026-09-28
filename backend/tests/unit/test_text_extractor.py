import io
import pytest
import docx
from core.exceptions import ValidationException
from services.text_extractor import TextExtractor


def test_clean_text_normalizes_whitespace_and_unicode():
    raw = "  Alex   Chen \u00a0\n\n\n\nSoftware   Engineer\r\n\tPython, \x00FastAPI  "
    cleaned = TextExtractor.clean_text(raw)
    assert "Alex Chen" in cleaned
    assert "Software Engineer" in cleaned
    assert "Python, FastAPI" in cleaned
    assert "\x00" not in cleaned
    assert "\n\n\n" not in cleaned


def test_extract_docx_paragraphs_and_tables():
    doc = docx.Document()
    doc.add_paragraph("Alex Chen - Staff Software Engineer")
    doc.add_paragraph("Experienced in building high-throughput distributed systems in Python and Go.")

    # Add a table
    table = doc.add_table(rows=1, cols=2)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Languages"
    hdr_cells[1].text = "Python, TypeScript, SQL"

    buf = io.BytesIO()
    doc.save(buf)
    docx_bytes = buf.getvalue()

    extracted = TextExtractor.extract_from_docx(docx_bytes)
    assert "Alex Chen" in extracted
    assert "distributed systems" in extracted
    assert "Languages | Python, TypeScript, SQL" in extracted


def test_extract_unsupported_file_format():
    with pytest.raises(ValidationException) as exc:
        TextExtractor.extract_text(b"some text", "txt")
    assert "Unsupported file format" in str(exc.value)


def test_extract_insufficient_text_raises_validation_exception():
    doc = docx.Document()
    doc.add_paragraph("Short")  # Less than 30 chars
    buf = io.BytesIO()
    doc.save(buf)

    with pytest.raises(ValidationException) as exc:
        TextExtractor.extract_text(buf.getvalue(), "docx")
    assert "empty or insufficient" in str(exc.value)
