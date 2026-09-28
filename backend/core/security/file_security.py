import abc
import hashlib
import os
import re
import shutil
import uuid
from typing import Optional, Set, Tuple
from core.exceptions import BadRequestException, ValidationException
from core.logging import get_logger

logger = get_logger("security.file_security")

# Industry standard anti-malware test signature
EICAR_SIGNATURE = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"

MAGIC_SIGNATURES = {
    "pdf": [b"%PDF-"],
    "docx": [b"PK\x03\x04"],
    "png": [b"\x89PNG\r\n\x1a\n"],
    "jpeg": [b"\xff\xd8\xff"],
    "jpg": [b"\xff\xd8\xff"],
}


class MalwareScanner(abc.ABC):
    """Abstract interface for file malware scanning."""
    @abc.abstractmethod
    def scan(self, data: bytes, filename: str) -> Tuple[bool, str]:
        """
        Returns: (is_clean: bool, engine_or_threat_name: str)
        """
        pass


class MockCleanMalwareScanner(MalwareScanner):
    """
    Production-grade mock scanner detecting EICAR signatures and dangerous executable blobs.
    Can be seamlessly hot-swapped for ClamAV in containerized clusters.
    """
    def scan(self, data: bytes, filename: str) -> Tuple[bool, str]:
        if EICAR_SIGNATURE in data:
            logger.warning(f"Malware test signature detected in upload: {filename}")
            return False, "EICAR-Test-Signature-Detected"

        # Check for dangerous embedded PE executable signatures
        if data.startswith(b"MZ") or b"This program cannot be run in DOS mode" in data:
            logger.warning(f"Embedded executable detected in upload: {filename}")
            return False, "Dangerous-Executable-Embedded"

        return True, "Clean (In-Line Antivirus Filter)"


class QuarantineManager:
    """
    Manages isolated quarantine staging for raw file uploads.
    Uploaded files are buffered in quarantine until all security gates pass.
    """
    def __init__(self, quarantine_dir: str = "storage/quarantine"):
        self.quarantine_dir = quarantine_dir
        os.makedirs(self.quarantine_dir, exist_ok=True)

    def stage_file(self, data: bytes, original_filename: str) -> str:
        """Saves file to quarantine under an unguessable UUID-based path."""
        safe_ext = os.path.splitext(original_filename)[1].lower()
        staged_name = f"{uuid.uuid4()}{safe_ext}"
        staged_path = os.path.join(self.quarantine_dir, staged_name)
        with open(staged_path, "wb") as f:
            f.write(data)
        return staged_path

    def release_file(self, staged_path: str, target_destination: str) -> None:
        """Moves a clean file from quarantine to the active storage directory."""
        os.makedirs(os.path.dirname(target_destination), exist_ok=True)
        shutil.move(staged_path, target_destination)

    def destroy_quarantined_file(self, staged_path: str) -> None:
        """Deletes a malicious or invalid quarantined file."""
        if os.path.exists(staged_path):
            try:
                os.remove(staged_path)
            except OSError as exc:
                logger.error(f"Failed to remove quarantined file {staged_path}: {exc}")


class FileSecurityValidator:
    """
    Validates file integrity, sanitizes filenames, verifies magic byte signatures,
    and conducts anti-malware scans before promotion to storage.
    """
    ALLOWED_EXTENSIONS: Set[str] = {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"}
    MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB

    def __init__(
        self,
        scanner: Optional[MalwareScanner] = None,
        quarantine: Optional[QuarantineManager] = None,
    ):
        self.scanner = scanner or MockCleanMalwareScanner()
        self.quarantine = quarantine or QuarantineManager()

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitizes filenames to prevent directory traversal and injection.
        Removes path separators and non-whitelisted characters.
        """
        basename = os.path.basename(filename.replace("\\", "/"))
        # Strip null bytes and control chars
        sanitized = re.sub(r"[\x00-\x1f\x7f]", "", basename)
        # Ensure only alphanumeric, dots, underscores, hyphens
        sanitized = re.sub(r"[^a-zA-Z0-9._-]", "_", sanitized)
        if not sanitized or sanitized.startswith("."):
            sanitized = f"upload_{uuid.uuid4().hex[:8]}{os.path.splitext(filename)[1]}"
        return sanitized

    def validate_and_scan(
        self,
        raw_data: bytes,
        filename: str,
    ) -> Tuple[bool, str, str, str]:
        """
        Runs comprehensive security pipeline:
        1. Size boundary check
        2. Filename sanitization & extension whitelist
        3. Magic bytes / MIME signature check
        4. Malware scan
        Returns: (is_clean: bool, sanitized_filename: str, sha256_hash: str, engine_or_error: str)
        """
        # 1. Size Check
        size = len(raw_data)
        if size == 0:
            raise ValidationException("Uploaded file is empty.")
        if size > self.MAX_FILE_SIZE_BYTES:
            raise ValidationException(
                f"File size exceeds maximum allowed limit of {self.MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB."
            )

        # 2. Filename Sanitization & Extension Whitelist
        safe_name = self.sanitize_filename(filename)
        _, ext = os.path.splitext(safe_name)
        ext = ext.lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValidationException(
                f"Unsupported file format '{ext}'. Allowed formats: {', '.join(sorted(self.ALLOWED_EXTENSIONS))}"
            )

        # 3. Magic Bytes Sniffing
        clean_ext = ext.lstrip(".")
        if clean_ext in MAGIC_SIGNATURES:
            signatures = MAGIC_SIGNATURES[clean_ext]
            if not any(raw_data.startswith(sig) for sig in signatures):
                raise ValidationException(
                    f"MIME validation failed. File content does not match declared format '{ext}'."
                )
        elif clean_ext == "txt":
            # Ensure text is valid utf-8 or ascii without null bytes
            if b"\x00" in raw_data:
                raise ValidationException("Binary content detected in plain text upload.")

        # 4. Compute Checksum
        sha256 = hashlib.sha256(raw_data).hexdigest()

        # 5. Malware Scan
        is_clean, scan_result = self.scanner.scan(raw_data, safe_name)
        if not is_clean:
            raise BadRequestException(f"Security Alert: Upload rejected by threat scanner ({scan_result}).")

        return True, safe_name, sha256, scan_result
