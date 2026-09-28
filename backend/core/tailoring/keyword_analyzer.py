"""
Keyword Analyzer for Phase 7 AI Resume Tailoring Engine.
Extracts keywords from job descriptions and calculates candidate keyword alignment.
"""
import re
from typing import Dict, List, Set, Tuple


COMMON_TECH_KEYWORDS = {
    "python", "javascript", "typescript", "react", "next.js", "node.js", "fastapi",
    "django", "flask", "postgresql", "mysql", "mongodb", "redis", "docker", "kubernetes",
    "aws", "gcp", "azure", "graphql", "rest", "api", "git", "ci/cd", "linux", "sql",
    "nosql", "tailwind", "prisma", "sqlalchemy", "microservices", "kafka", "rabbitmq",
    "pandas", "numpy", "pytorch", "tensorflow", "scikit-learn", "gemini", "openai", "llm",
    "unit testing", "pytest", "vitest", "jest", "agile", "scrum", "devops", "cloud",
    "system design", "html", "css", "vue", "angular", "golang", "rust", "c++", "java"
}


class KeywordAnalyzer:
    """
    Analyzes job descriptions for required/preferred skills and computes keyword match coverage.
    """

    @staticmethod
    def extract_keywords_heuristic(text: str) -> Dict[str, List[str]]:
        """
        Deterministic fallback keyword extraction when offline or during unit tests.
        Extracts technologies, skills, and common keywords from text.
        """
        lower_text = text.lower()
        found_keywords: Set[str] = set()

        for kw in COMMON_TECH_KEYWORDS:
            # Match word boundary or token boundary
            pattern = r"(?:\b|_)" + re.escape(kw) + r"(?:\b|_)"
            if re.search(pattern, lower_text):
                found_keywords.add(kw.title() if len(kw) > 3 else kw.upper())

        # Extract words near "requirements", "experience with", "proficient in"
        req_pattern = r"(?:experience with|proficient in|knowledge of|familiarity with|strong skills in)\s+([a-zA-Z0-9\+\#\.\,\s]{3,50})"
        for match in re.finditer(req_pattern, lower_text):
            chunk = match.group(1)
            parts = [p.strip().title() for p in re.split(r"[,;]|\band\b", chunk) if p.strip()]
            for p in parts[:3]:
                if len(p) > 2 and len(p) < 30:
                    found_keywords.add(p)

        keyword_list = sorted(list(found_keywords))
        mid = len(keyword_list) // 2
        return {
            "required_skills": keyword_list[:max(mid, 3)] if keyword_list else ["Python", "FastAPI"],
            "preferred_skills": keyword_list[max(mid, 3):] if keyword_list else ["Docker", "PostgreSQL"],
            "technologies": keyword_list,
            "responsibilities": [
                "Design and maintain scalable backend services and APIs",
                "Collaborate with cross-functional teams to deliver production features",
            ],
            "keywords": keyword_list,
        }

    @staticmethod
    def compute_alignment(
        candidate_skills: List[str],
        candidate_experiences: List[dict],
        job_keywords: List[str],
        required_skills: List[str],
    ) -> Tuple[List[str], List[str], float]:
        """
        Determines matched keywords vs missing keywords based on candidate's verified profile.
        Returns (matched_keywords, missing_keywords, coverage_percentage).
        """
        # Build candidate competency set (lowercase for comparison)
        candidate_tokens: Set[str] = set()
        for s in candidate_skills:
            clean_s = s.strip().lower()
            candidate_tokens.add(clean_s)
            # Add individual tokens
            for part in clean_s.split():
                if len(part) > 2:
                    candidate_tokens.add(part)

        # Also add terms explicitly appearing in authentic experience descriptions
        for exp in candidate_experiences:
            exp_text = (exp.get("description", "") + " " + " ".join(exp.get("bullet_points", []))).lower()
            for kw in job_keywords:
                if kw.lower() in exp_text:
                    candidate_tokens.add(kw.lower())

        all_target = list(dict.fromkeys(job_keywords + required_skills))
        if not all_target:
            return [], [], 100.0

        matched: List[str] = []
        missing: List[str] = []

        for target in all_target:
            target_clean = target.strip()
            target_lower = target_clean.lower()

            # Check exact or token match
            is_matched = (
                target_lower in candidate_tokens
                or any(t in candidate_tokens for t in target_lower.split() if len(t) > 2)
                or any(target_lower in c for c in candidate_tokens if len(target_lower) > 3)
            )

            if is_matched:
                matched.append(target_clean)
            else:
                missing.append(target_clean)

        coverage = round((len(matched) / max(len(all_target), 1)) * 100, 1)
        return matched, missing, coverage
