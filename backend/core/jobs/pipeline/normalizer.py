import re
from typing import Optional, Tuple
from core.jobs.providers.base import RawJob


class JobNormalizer:
    """
    Normalizes raw job fields into consistent database-ready canonical formats.
    """

    @staticmethod
    def normalize_location(raw_loc: Optional[str]) -> str:
        """
        Normalizes location string:
        'Remote', 'REMOTE', 'remote', 'Telecommute' -> 'Remote'
        'San Francisco, CA / Remote' -> 'San Francisco, CA (Remote)'
        """
        if not raw_loc or not raw_loc.strip():
            return "Remote"

        loc = raw_loc.strip()

        # Pure remote detection
        pure_remote_patterns = [
            r"^(remote|anywhere|worldwide|telecommute|wfh|work from home)$",
            r"^remote\s*[-–—/]\s*(anywhere|worldwide|global|us|usa|europe|latam)$",
            r"^worldwide\s*\(remote\)$",
        ]
        for pattern in pure_remote_patterns:
            if re.match(pattern, loc, re.IGNORECASE):
                return "Remote"

        # Hybrid/Location with remote note
        if re.search(r"\b(remote|wfh|telecommute)\b", loc, re.IGNORECASE):
            # Clean up separators
            clean = re.sub(r"\s*[/|–—]\s*(remote|telecommute)\s*", " (Remote)", loc, flags=re.IGNORECASE)
            clean = re.sub(r"\s*\(Remote\)\s*\(Remote\)", " (Remote)", clean)
            if "(Remote)" not in clean:
                clean = f"{clean} (Remote)"
            return clean.strip()

        # Capitalize and clean spaces
        return re.sub(r"\s+", " ", loc).strip()

    @staticmethod
    def normalize_employment_type(raw_type: Optional[str]) -> str:
        """
        Normalizes employment type:
        'Full-time', 'FULLTIME', 'Permanent', 'full_time' -> 'Full-time'
        'Part-time', 'contractor', 'internship', etc.
        """
        if not raw_type or not raw_type.strip():
            return "Full-time"

        t = raw_type.strip().lower()

        if any(term in t for term in ["full", "perm", "regular"]):
            return "Full-time"
        if any(term in t for term in ["part"]):
            return "Part-time"
        if any(term in t for term in ["contract", "temp", "freelance"]):
            return "Contract"
        if any(term in t for term in ["intern", "co-op", "trainee"]):
            return "Internship"

        return "Full-time"

    @staticmethod
    def normalize_salary(
        salary_min: Optional[float],
        salary_max: Optional[float],
        currency: Optional[str] = "USD",
    ) -> Tuple[Optional[float], Optional[float], str]:
        """
        Standardizes salary boundaries and currency.
        """
        curr = (currency or "USD").upper().strip()
        s_min = float(salary_min) if salary_min and salary_min > 0 else None
        s_max = float(salary_max) if salary_max and salary_max > 0 else None

        if s_min and s_max and s_min > s_max:
            s_min, s_max = s_max, s_min

        return s_min, s_max, curr

    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Strips tracking parameters and whitespace from URLs for accurate deduplication.
        """
        if not url:
            return ""
        clean = url.strip()
        # Remove tracking query params (utm_*, ref, etc.)
        clean = re.sub(r"[?&](utm_[^&]+|ref=[^&]+|source=[^&]+)", "", clean)
        # Clean trailing question mark if all params removed
        clean = re.sub(r"\?$", "", clean)
        return clean.rstrip("/")

    @classmethod
    def normalize(cls, raw: RawJob) -> RawJob:
        """
        Runs full normalization pass on a RawJob instance.
        """
        raw.location = cls.normalize_location(raw.location)
        raw.employment_type = cls.normalize_employment_type(raw.employment_type)
        raw.salary_min, raw.salary_max, raw.currency = cls.normalize_salary(
            raw.salary_min, raw.salary_max, raw.currency
        )
        raw.apply_url = cls.normalize_url(raw.apply_url)
        raw.title = raw.title.strip()
        raw.company = raw.company.strip()
        raw.description = raw.description.strip()
        return raw
