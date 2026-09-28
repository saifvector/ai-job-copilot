import os
import time
import uuid
import pytest
from core.exceptions import AuthenticationException, BadRequestException, TokenExpiredException, TokenRevokedException, ValidationException
from core.security.file_security import EICAR_SIGNATURE, FileSecurityValidator, MockCleanMalwareScanner, QuarantineManager
from core.security.rate_limiter import SlidingWindowRateLimiter
from core.security.sanitization import InputSanitizer
from core.security.tokens import SecretKeyManager, TokenBlacklist, TokenService


@pytest.mark.asyncio
async def test_jwt_generation_and_verification():
    user_id = uuid.uuid4()
    access_token, jti, expires_in = TokenService.create_access_token(
        user_id=user_id,
        role="candidate",
        expires_delta_seconds=60,
    )

    assert access_token is not None
    assert jti is not None
    assert expires_in == 60

    payload = TokenService.verify_token(access_token, expected_type="access")
    assert payload["sub"] == str(user_id)
    assert payload["jti"] == jti
    assert payload["role"] == "candidate"


@pytest.mark.asyncio
async def test_jwt_token_expiration():
    user_id = uuid.uuid4()
    # Expire immediately
    token, _, _ = TokenService.create_access_token(
        user_id=user_id,
        expires_delta_seconds=-10,
    )
    with pytest.raises(TokenExpiredException):
        TokenService.verify_token(token, expected_type="access")


@pytest.mark.asyncio
async def test_refresh_token_rotation_and_family_revocation():
    user_id = uuid.uuid4()
    # 1. Issue initial refresh token
    refresh_token, jti_1, family_id, _ = TokenService.create_refresh_token(user_id=user_id)

    # 2. Perform rotation
    new_access, new_refresh, rotated_uid = TokenService.rotate_refresh_token(refresh_token)
    assert new_access is not None
    assert new_refresh is not None
    assert rotated_uid == user_id

    # 3. Old refresh token should now be blacklisted
    with pytest.raises(TokenRevokedException):
        TokenService.verify_token(refresh_token, expected_type="refresh")

    # 4. Attempting to reuse old refresh token should trigger family revocation
    with pytest.raises(AuthenticationException):
        TokenService.rotate_refresh_token(refresh_token)


@pytest.mark.asyncio
async def test_token_explicit_revocation():
    user_id = uuid.uuid4()
    token, jti, _ = TokenService.create_access_token(user_id=user_id)

    # Valid prior to revocation
    payload = TokenService.verify_token(token, expected_type="access")
    assert payload["jti"] == jti

    # Revoke
    TokenService.revoke_token(token)

    with pytest.raises(TokenRevokedException):
        TokenService.verify_token(token, expected_type="access")


@pytest.mark.asyncio
async def test_rate_limiter_sliding_window():
    limiter = SlidingWindowRateLimiter(default_limit=3, window_seconds=60)
    key = "test_client_ip_1"

    # First 3 requests should be permitted
    allowed1, rem1, _ = limiter.is_allowed(key)
    allowed2, rem2, _ = limiter.is_allowed(key)
    allowed3, rem3, _ = limiter.is_allowed(key)

    assert allowed1 is True
    assert allowed2 is True
    assert allowed3 is True
    assert rem3 == 0

    # 4th request must be rejected
    allowed4, rem4, reset_in = limiter.is_allowed(key)
    assert allowed4 is False
    assert rem4 == 0
    assert reset_in > 0


@pytest.mark.asyncio
async def test_file_security_validation_clean_pdf(tmp_path):
    validator = FileSecurityValidator()
    # Valid PDF header
    valid_pdf_content = b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"

    is_clean, safe_name, sha256, engine = validator.validate_and_scan(
        raw_data=valid_pdf_content,
        filename="../../../malicious_path/resume.pdf",
    )

    assert is_clean is True
    assert ".." not in safe_name
    assert "/" not in safe_name
    assert safe_name.endswith(".pdf")
    assert len(sha256) == 64


@pytest.mark.asyncio
async def test_file_security_rejection_of_mime_spoofing():
    validator = FileSecurityValidator()
    # Executable content with a .pdf extension
    fake_pdf = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00"

    with pytest.raises(ValidationException) as exc:
        validator.validate_and_scan(
            raw_data=fake_pdf,
            filename="trojan.pdf",
        )
    assert "MIME validation failed" in str(exc.value.message)


@pytest.mark.asyncio
async def test_file_security_rejection_of_eicar_signature():
    validator = FileSecurityValidator()
    # EICAR signature inside a txt file
    eicar_content = EICAR_SIGNATURE

    with pytest.raises(BadRequestException) as exc:
        validator.validate_and_scan(
            raw_data=eicar_content,
            filename="test_virus.txt",
        )
    assert "threat scanner" in str(exc.value.message)


def test_input_sanitizer_xss_and_injection():
    dirty_html = "<script>alert('XSS')</script><b>Staff Engineer</b>"
    cleaned = InputSanitizer.sanitize_string(dirty_html, strip_html=True)
    assert "<script>" not in cleaned
    assert "alert" not in cleaned
    assert cleaned == "Staff Engineer"

    # Recursive dictionary sanitization
    dirty_dict = {
        "title": "Lead Architect <script>stealCookies()</script>",
        "skills": ["Python", "<img src=x onerror=alert(1)>", "FastAPI"],
    }
    cleaned_dict = InputSanitizer.sanitize_dict(dirty_dict)
    assert cleaned_dict["title"] == "Lead Architect"
    assert cleaned_dict["skills"][1] == ""
