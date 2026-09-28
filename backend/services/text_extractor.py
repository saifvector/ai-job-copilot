"""
Text Extraction and Normalization Service for PDF and DOCX documents.
Extracts raw text and cleans whitespace, non-printable characters, and formatting artifacts.
"""
import io
import re
import unicodedata
from pathlib import Path
from typing import Union
import docx
import pypdf
from core.exceptions import ValidationException
from core.logging import get_logger

logger = get_logger("services.text_extractor")


class TextExtractor:
    """
    Production-grade text extraction from PDF and DOCX files.
    """

    @staticmethod
    def clean_text(raw_text: str) -> str:
        """
        Normalizes and sanitizes extracted text:
        - Normalizes Unicode (NFKD)
        - Removes non-printable control characters
        - Collapses repeated horizontal whitespaces
        - Collapses excessive newlines (max 2 consecutive)
        - Strips bounding whitespace
        """
        if not raw_text:
            return ""

        # Normalize Unicode characters
        text = unicodedata.normalize("NFKD", raw_text)

        # Remove non-printable control characters except standard whitespaces
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)

        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Replace non-breaking spaces with standard space
        text = text.replace("\u00a0", " ")

        # Collapse horizontal whitespaces within lines
        text = re.sub(r"[ \t]+", " ", text)

        # Collapse 3 or more consecutive newlines to 2 newlines
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Strip lines individually and join
        lines = [line.strip() for line in text.split("\n")]
        cleaned = "\n".join(lines).strip()

        return cleaned

    @classmethod
    def extract_from_pdf(cls, file_source: Union[str, Path, bytes, io.BytesIO]) -> str:
        """
        Extracts all textual content from a PDF document using pypdf.
        """
        try:
            if isinstance(file_source, (str, Path)):
                reader = pypdf.PdfReader(str(file_source))
            elif isinstance(file_source, bytes):
                reader = pypdf.PdfReader(io.BytesIO(file_source))
            else:
                reader = pypdf.PdfReader(file_source)

            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception:
                    raise ValidationException("PDF is password protected and cannot be extracted.")

            extracted_pages = []
            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    extracted_pages.append(page_text)

            raw_combined = "\n\n".join(extracted_pages)
            return cls.clean_text(raw_combined)

        except ValidationException:
            raise
        except Exception as exc:
            logger.error("Failed to extract text from PDF", extra={"error": str(exc)})
            raise ValidationException(f"Failed to read PDF file: {str(exc)}")

    @classmethod
    def extract_from_docx(cls, file_source: Union[str, Path, bytes, io.BytesIO]) -> str:
        """
        Extracts textual content from DOCX paragraphs and tables using python-docx.
        """
        try:
            if isinstance(file_source, (str, Path)):
                doc = docx.Document(str(file_source))
            elif isinstance(file_source, bytes):
                doc = docx.Document(io.BytesIO(file_source))
            else:
                doc = docx.Document(file_source)

            text_parts = []

            # Extract standard paragraphs
            for paragraph in doc.paragraphs:
                p_text = paragraph.text.strip()
                if p_text:
                    text_parts.append(p_text)

            # Extract text from tables (often used in resume layouts)
            for table in doc.tables:
                for row in table.rows:
                    row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_cells:
                        # De-duplicate cell values that span columns
                        unique_cells = []
                        for cell in row_cells:
                            if not unique_cells or cell != unique_cells[-1]:
                                unique_cells.append(cell)
                        text_parts.append(" | ".join(unique_cells))

            raw_combined = "\n".join(text_parts)
            return cls.clean_text(raw_combined)

        except Exception as exc:
            logger.error("Failed to extract text from DOCX", extra={"error": str(exc)})
            raise ValidationException(f"Failed to read DOCX file: {str(exc)}")

    @classmethod
    def extract_text(cls, file_source: Union[str, Path, bytes, io.BytesIO], file_type: str) -> str:
        """
        Routes extraction based on file format ('pdf' or 'docx').
        """
        lowered = file_type.lower().strip()
        if "pdf" in lowered:
            cleaned = cls.extract_from_pdf(file_source)
        elif "word" in lowered or "docx" in lowered or "doc" in lowered or "officedocument" in lowered:
            cleaned = cls.extract_from_docx(file_source)
        else:
            raise ValidationException(f"Unsupported file format for resume text extraction: {file_type}")


        if not cleaned or len(cleaned) < 30:
            raise ValidationException(
                "Extracted resume text is empty or insufficient. If this is a scanned image, please upload a text-based PDF or DOCX."
            )

        return cleaned
