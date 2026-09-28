import html
import re
from typing import Any, Dict, List, Union


class InputSanitizer:
    """
    Sanitizes user input to prevent Cross-Site Scripting (XSS), null byte injection,
    and dangerous control sequence exploitation.
    """
    SCRIPT_PATTERN = re.compile(r"<\s*script[^>]*>.*?<\s*/\s*script\s*>", re.IGNORECASE | re.DOTALL)
    HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
    SQL_INJECTION_PATTERN = re.compile(
        r"(\b(UNION\s+SELECT|DROP\s+TABLE|ALTER\s+TABLE|EXEC(\s|\+)+(s|x)p_)\b)",
        re.IGNORECASE
    )

    @classmethod
    def sanitize_string(cls, value: str, strip_html: bool = True, escape_output: bool = False) -> str:
        """Sanitizes a single text string."""
        if not isinstance(value, str):
            return value

        # Strip null bytes
        cleaned = value.replace("\x00", "")

        # Strip script blocks completely
        cleaned = cls.SCRIPT_PATTERN.sub("", cleaned)

        # Optionally strip all other HTML tags
        if strip_html:
            cleaned = cls.HTML_TAG_PATTERN.sub("", cleaned)

        # Escape HTML entities if requested
        if escape_output:
            cleaned = html.escape(cleaned)

        return cleaned.strip()

    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any], strip_html: bool = True) -> Dict[str, Any]:
        """Recursively sanitizes dictionary strings."""
        result = {}
        for key, val in data.items():
            if isinstance(val, str):
                result[key] = cls.sanitize_string(val, strip_html=strip_html)
            elif isinstance(val, dict):
                result[key] = cls.sanitize_dict(val, strip_html=strip_html)
            elif isinstance(val, list):
                result[key] = cls.sanitize_list(val, strip_html=strip_html)
            else:
                result[key] = val
        return result

    @classmethod
    def sanitize_list(cls, items: List[Any], strip_html: bool = True) -> List[Any]:
        """Recursively sanitizes list strings."""
        result = []
        for item in items:
            if isinstance(item, str):
                result.append(cls.sanitize_string(item, strip_html=strip_html))
            elif isinstance(item, dict):
                result.append(cls.sanitize_dict(item, strip_html=strip_html))
            elif isinstance(item, list):
                result.append(cls.sanitize_list(item, strip_html=strip_html))
            else:
                result.append(item)
        return result
