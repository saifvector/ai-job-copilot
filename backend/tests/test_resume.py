import io
import os
import uuid
import zipfile
import pytest
from httpx import AsyncClient

from core.exceptions import BadRequestException
from core.storage.local import LocalStorageProvider
from core.storage.validator import FileValidator, MAX_FILE_SIZE_BYTES


# Helper utilities to generate valid test files
def make_dummy_pdf(content: str = "Test PDF Document") -> bytes:
    """Generate a minimal valid PDF-compliant byte stream."""
    return (
        f"%PDF-1.4\n"
        f"1 0 obj\n"
        f"<< /Title ({content}) >>\n"
        f"endobj\n"
        f"xref\n"
        f"0 1\n"
        f"0000000000 65535 f \n"
        f"trailer\n"
        f"<< /Size 1 >>\n"
        f"startxref\n"
        f"56\n"
        f"%%EOF\n"
    ).encode("latin-1")


def make_dummy_docx(text: str = "Candidate Resume") -> bytes:
    """Generate a valid docx ZIP container with [Content_Types].xml and word/document.xml."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            '</Types>',
        )
        zf.writestr(
            "word/document.xml",
            f'<?xml version="1.0" encoding="UTF-8"?>'
            f'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f'<w:body><w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:body>'
            f'</w:document>',
        )
    return buffer.getvalue()


# ==============================================================================
# 1. VALIDATION TESTS (FileValidator)
# ==============================================================================

class TestFileValidator:
    """Unit tests verifying FileValidator security rules, magic bytes, and limits."""

    def test_valid_pdf_passes(self):
        pdf_bytes = make_dummy_pdf()
        ext, mime = FileValidator.validate_resume_file(
            filename="Alex_Chen_Resume.pdf",
            content_type="application/pdf",
            content=pdf_bytes,
        )
        assert ext == ".pdf"
        assert mime == "application/pdf"

    def test_valid_docx_passes(self):
        docx_bytes = make_dummy_docx()
        ext, mime = FileValidator.validate_resume_file(
            filename="Senior_Engineer.docx",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            content=docx_bytes,
        )
        assert ext == ".docx"
        assert mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    def test_rejects_empty_file(self):
        with pytest.raises(BadRequestException) as exc_info:
            FileValidator.validate_resume_file(
                filename="empty.pdf",
                content_type="application/pdf",
                content=b"",
            )
        assert "empty" in str(exc_info.value).lower()

    def test_rejects_oversized_file(self):
        # Exceeds 10 MB limit by 1 byte
        oversized = b"0" * (MAX_FILE_SIZE_BYTES + 1)
        with pytest.raises(BadRequestException) as exc_info:
            FileValidator.validate_resume_file(
                filename="huge.pdf",
                content_type="application/pdf",
                content=oversized,
            )
        assert "10 mb" in str(exc_info.value).lower()

    def test_rejects_disallowed_extension(self):
        with pytest.raises(BadRequestException) as exc_info:
            FileValidator.validate_resume_file(
                filename="script.exe",
                content_type="application/octet-stream",
                content=b"MZ\x90\x00somecode",
            )
        assert "unsupported extension" in str(exc_info.value).lower()

    def test_rejects_fake_pdf_header(self):
        # .pdf extension but content doesn't start with %PDF
        fake_content = b"This is just a text file renamed to resume.pdf"
        with pytest.raises(BadRequestException) as exc_info:
            FileValidator.validate_resume_file(
                filename="resume.pdf",
                content_type="application/pdf",
                content=fake_content,
            )
        assert "corrupt or invalid pdf" in str(exc_info.value).lower()

    def test_rejects_executable_pe_magic_bytes(self):
        # Starts with Windows MZ header
        malicious = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00"
        with pytest.raises(BadRequestException) as exc_info:
            FileValidator.validate_resume_file(
                filename="resume.pdf",
                content_type="application/pdf",
                content=malicious,
            )
        assert "executable" in str(exc_info.value).lower()

    def test_rejects_executable_elf_magic_bytes(self):
        # Starts with Linux ELF header \x7fELF
        malicious = b"\x7fELF\x02\x01\x01\x00"
        with pytest.raises(BadRequestException) as exc_info:
            FileValidator.validate_resume_file(
                filename="resume.pdf",
                content_type="application/pdf",
                content=malicious,
            )
        assert "executable" in str(exc_info.value).lower()

    def test_rejects_image_file_magic_bytes(self):
        # Starts with PNG header \x89PNG
        png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        with pytest.raises(BadRequestException) as exc_info:
            FileValidator.validate_resume_file(
                filename="photo.pdf",
                content_type="application/pdf",
                content=png_bytes,
            )
        assert "image files" in str(exc_info.value).lower()

    def test_rejects_fake_docx_zip_structure(self):
        # ZIP archive but lacks required OpenXML parts
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as zf:
            zf.writestr("test.txt", "not a docx")
        corrupt_zip = buffer.getvalue()

        with pytest.raises(BadRequestException) as exc_info:
            FileValidator.validate_resume_file(
                filename="resume.docx",
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                content=corrupt_zip,
            )
        assert "not a valid microsoft word" in str(exc_info.value).lower()


# ==============================================================================
# 2. STORAGE PROVIDER TESTS (LocalStorageProvider)
# ==============================================================================

class TestLocalStorageProvider:
    """Unit tests for LocalStorageProvider file operations and path traversal security."""

    @pytest.mark.asyncio
    async def test_save_and_retrieve_file(self, temp_storage):
        provider, _ = temp_storage
        user_id = uuid.uuid4()
        rel_path = f"resumes/{user_id}/{uuid.uuid4()}.pdf"
        data = make_dummy_pdf()

        # Save
        saved_rel_path = await provider.save_file(
            content=data,
            relative_path=rel_path,
        )
        assert saved_rel_path == rel_path

        local_path = provider.get_local_path(rel_path)
        assert local_path is not None
        assert os.path.exists(local_path)

        # Exists
        exists = await provider.file_exists(rel_path)
        assert exists is True

        # Retrieve
        retrieved = await provider.get_file(rel_path)
        assert retrieved == data

        # Delete
        deleted = await provider.delete_file(rel_path)
        assert deleted is True
        assert await provider.file_exists(rel_path) is False

    @pytest.mark.asyncio
    async def test_path_traversal_protection_in_relative_dir(self, temp_storage):
        provider, _ = temp_storage
        malicious_path = "../../etc/passwd"
        with pytest.raises(BadRequestException) as exc_info:
            await provider.save_file(
                content=b"secret",
                relative_path=malicious_path,
            )
        assert "traversal" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_path_traversal_protection_in_stored_filename(self, temp_storage):
        provider, _ = temp_storage
        user_id = uuid.uuid4()
        with pytest.raises(BadRequestException) as exc_info:
            await provider.save_file(
                content=b"exploit",
                relative_path=f"resumes/{user_id}/../../../boot.ini",
            )
        assert "traversal" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_path_traversal_protection_in_get_file(self, temp_storage):
        provider, _ = temp_storage
        with pytest.raises(BadRequestException) as exc_info:
            await provider.get_file("../../some_file.txt")
        assert "traversal" in str(exc_info.value).lower()


# ==============================================================================
# 3. END-TO-END API TESTS (FastAPI Endpoints)
# ==============================================================================

class TestResumeAPI:
    """Integration tests verifying full upload, download, metadata, replace, and delete flow."""

    @pytest.mark.asyncio
    async def test_full_resume_lifecycle(self, client: AsyncClient):
        demo_user_id = "a0000000-0000-0000-0000-000000000001"
        headers = {"X-User-Id": demo_user_id}

        # Step 1: Ensure initial state has no resume (404)
        get_res = await client.get("/api/v1/resume", headers=headers)
        assert get_res.status_code == 404
        assert get_res.json()["error"]["code"] == "RESOURCE_NOT_FOUND"

        # Step 2: Upload a valid PDF resume
        pdf_bytes = make_dummy_pdf("Alex Chen - Staff Engineer")
        files = {
            "file": ("Alex_Chen_CV.pdf", pdf_bytes, "application/pdf")
        }
        upload_res = await client.post("/api/v1/resume/upload", headers=headers, files=files)
        assert upload_res.status_code == 201
        res_json = upload_res.json()
        assert res_json["success"] is True
        data = res_json["data"]

        # Validate response format
        assert data["originalFilename"] == "Alex_Chen_CV.pdf"
        assert data["fileType"] == "application/pdf"
        assert data["fileSize"] == len(pdf_bytes)
        assert data["userId"] == demo_user_id
        assert "downloadUrl" in data
        assert "/api/v1/resume/download" in data["downloadUrl"]
        # CRITICAL SECURITY CHECK: file_path / filePath must NEVER be exposed in API
        assert "filePath" not in data
        assert "file_path" not in data
        assert "storedFilename" not in data
        assert "stored_filename" not in data

        resume_id = data["id"]

        # Step 3: View resume metadata (GET /api/v1/resume)
        meta_res = await client.get("/api/v1/resume", headers=headers)
        assert meta_res.status_code == 200
        meta_json = meta_res.json()
        assert meta_json["success"] is True
        meta_data = meta_json["data"]
        assert meta_data["id"] == resume_id
        assert meta_data["originalFilename"] == "Alex_Chen_CV.pdf"
        assert meta_data["fileSize"] == len(pdf_bytes)
        assert "filePath" not in meta_data

        # Step 4: Download resume (GET /api/v1/resume/download)
        dl_res = await client.get("/api/v1/resume/download", headers=headers)
        assert dl_res.status_code == 200
        assert "attachment; filename=\"Alex_Chen_CV.pdf\"" in dl_res.headers["content-disposition"]
        assert dl_res.headers["content-type"] == "application/pdf"
        assert dl_res.content == pdf_bytes

        # Step 5: Replace resume with a DOCX file
        docx_bytes = make_dummy_docx("Alex Chen - Updated Experience")
        docx_files = {
            "file": (
                "Alex_Chen_Updated.docx",
                docx_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        }
        replace_res = await client.post("/api/v1/resume/upload", headers=headers, files=docx_files)
        assert replace_res.status_code == 201
        replaced_data = replace_res.json()["data"]
        assert replaced_data["originalFilename"] == "Alex_Chen_Updated.docx"
        assert replaced_data["fileType"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert replaced_data["fileSize"] == len(docx_bytes)

        # Step 6: Verify downloaded file is now the new DOCX
        dl_res_2 = await client.get("/api/v1/resume/download", headers=headers)
        assert dl_res_2.status_code == 200
        assert "attachment; filename=\"Alex_Chen_Updated.docx\"" in dl_res_2.headers["content-disposition"]
        assert dl_res_2.content == docx_bytes

        # Step 7: Delete resume (DELETE /api/v1/resume)
        del_res = await client.delete("/api/v1/resume", headers=headers)
        assert del_res.status_code == 200
        del_data = del_res.json()
        assert del_data["success"] is True

        # Step 8: Verify resume is gone
        get_res_after_del = await client.get("/api/v1/resume", headers=headers)
        assert get_res_after_del.status_code == 404

        dl_res_after_del = await client.get("/api/v1/resume/download", headers=headers)
        assert dl_res_after_del.status_code == 404

        # Step 9: Deleting again returns 404
        del_res_again = await client.delete("/api/v1/resume", headers=headers)
        assert del_res_again.status_code == 404

    @pytest.mark.asyncio
    async def test_upload_rejection_empty_file(self, client: AsyncClient):
        headers = {"X-User-Id": "a0000000-0000-0000-0000-000000000001"}
        files = {"file": ("empty.pdf", b"", "application/pdf")}
        res = await client.post("/api/v1/resume/upload", headers=headers, files=files)
        assert res.status_code == 400
        assert "empty" in res.json()["error"]["message"].lower()

    @pytest.mark.asyncio
    async def test_upload_rejection_executable(self, client: AsyncClient):
        headers = {"X-User-Id": "a0000000-0000-0000-0000-000000000001"}
        files = {"file": ("payload.exe", b"MZ\x90\x00malicious", "application/octet-stream")}
        res = await client.post("/api/v1/resume/upload", headers=headers, files=files)
        assert res.status_code == 400

    @pytest.mark.asyncio
    async def test_upload_rejection_image_file(self, client: AsyncClient):
        headers = {"X-User-Id": "a0000000-0000-0000-0000-000000000001"}
        png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        files = {"file": ("avatar.png", png_bytes, "image/png")}
        res = await client.post("/api/v1/resume/upload", headers=headers, files=files)
        assert res.status_code == 400

    @pytest.mark.asyncio
    async def test_upload_rejection_corrupt_pdf(self, client: AsyncClient):
        headers = {"X-User-Id": "a0000000-0000-0000-0000-000000000001"}
        files = {"file": ("corrupt.pdf", b"This file does not have a PDF header", "application/pdf")}
        res = await client.post("/api/v1/resume/upload", headers=headers, files=files)
        assert res.status_code == 400
        assert "corrupt or invalid pdf" in res.json()["error"]["message"].lower()
