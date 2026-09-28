"""
ATS (Applicant Tracking System) Evaluation Engine for Phase 7.
Calculates 0-100 score across 5 key dimensions:
1. Keyword Match (30%)
2. Skill Match (25%)
3. Section Quality (15%)
4. Experience Relevance (15%)
5. Formatting Structure (15%)

Also enforces the Truthfulness Mandate.
"""
import re
from typing import Any, Dict, List, Set, Tuple
from schemas.tailoring import ATSScoreBreakdownDTO, ResumeVersionDTO


ACTION_VERBS = {
    "architected", "developed", "engineered", "designed", "implemented", "spearheaded",
    "optimized", "scaled", "automated", "built", "created", "led", "managed", "orchestrated",
    "reduced", "increased", "accelerated", "streamlined", "enhanced", "resolved", "delivered"
}


class ATSEngine:
    """
    Evaluates tailored resumes against ATS parser criteria and enforces truthfulness.
    """

    @classmethod
    def calculate_ats_score(
        cls,
        version: ResumeVersionDTO,
        job_keywords: List[str],
        required_skills: List[str],
        preferred_skills: List[str],
        job_title: str,
        job_description: str,
        candidate_genuine_skills: List[str],
    ) -> ATSScoreBreakdownDTO:
        """
        Calculates ATS composite score (0-100) and factor breakdown.
        """
        # 1. Keyword Match (30%)
        # Check occurrence of job keywords in version content (summary, experience bullets, skills)
        resume_text_blob = cls._get_resume_text_blob(version)
        matched_kw_count = 0
        total_kw = list(dict.fromkeys(job_keywords + required_skills))
        if total_kw:
            for kw in total_kw:
                if re.search(r"(?:\b|_)" + re.escape(kw.lower()) + r"(?:\b|_)", resume_text_blob):
                    matched_kw_count += 1
            keyword_match = min(100.0, round((matched_kw_count / max(len(total_kw), 1)) * 100, 1))
        else:
            keyword_match = 85.0

        # 2. Skill Match (25%)
        # Genuine skills candidate possesses that match job requirements
        candidate_skills_lower = {s.lower().strip() for s in candidate_genuine_skills}
        req_and_pref = list(dict.fromkeys(required_skills + preferred_skills))
        if req_and_pref:
            matched_skills = sum(
                1 for s in req_and_pref
                if s.lower().strip() in candidate_skills_lower
                or any(t in candidate_skills_lower for t in s.lower().split() if len(t) > 2)
            )
            skill_match = min(100.0, round((matched_skills / max(len(req_and_pref), 1)) * 100, 1))
        else:
            skill_match = 80.0

        # 3. Section Quality (15%)
        # Summary quality + Action verbs in bullets + Quantifiable metrics
        section_quality = cls._evaluate_section_quality(version)

        # 4. Experience Relevance (15%)
        # Overlap between candidate roles and target job title/description
        experience_relevance = cls._evaluate_experience_relevance(version, job_title, job_description)

        # 5. Formatting Structure (15%)
        # ATS standard sections, bullet count, clean layout
        formatting_structure = cls._evaluate_formatting_structure(version)

        # Weighted calculation
        overall_score = round(
            (0.30 * keyword_match) +
            (0.25 * skill_match) +
            (0.15 * section_quality) +
            (0.15 * experience_relevance) +
            (0.15 * formatting_structure),
            1
        )
        overall_score = max(0.0, min(100.0, overall_score))

        # Generate constructive suggestions
        suggestions: List[str] = []
        if keyword_match < 75:
            suggestions.append(f"Incorporate more target keywords in experience bullet points (current keyword match: {keyword_match}%).")
        if skill_match < 70:
            suggestions.append("Job requires competencies currently absent from your verified profile. Highlight transferable skills or take online certifications.")
        if section_quality < 80:
            suggestions.append("Enhance bullet points with more quantifiable business impact (e.g., percentages, scale, throughput metrics).")
        if experience_relevance < 75:
            suggestions.append(f"Reframe recent project accomplishments to more closely reflect responsibilities of a {job_title}.")
        if formatting_structure < 85:
            suggestions.append("Ensure each position has at least 3 distinct, action-oriented bullet points for optimal ATS parsing.")

        if not suggestions:
            suggestions.append("Excellent alignment! Resume is highly optimized for both automated ATS filters and hiring managers.")

        return ATSScoreBreakdownDTO(
            overall_score=overall_score,
            keyword_match=keyword_match,
            skill_match=skill_match,
            section_quality=section_quality,
            experience_relevance=experience_relevance,
            formatting_structure=formatting_structure,
            suggestions=suggestions,
        )

    @classmethod
    def enforce_truthfulness(
        cls,
        version: ResumeVersionDTO,
        authentic_skills: List[str],
    ) -> Tuple[ResumeVersionDTO, List[str]]:
        """
        Anti-Hallucination Guardrail:
        Strips any skill from version.skills that the candidate does not legitimately possess.
        Returns the sanitized ResumeVersionDTO and a list of stripped hallucinated skills.
        """
        authentic_set: Set[str] = {s.strip().lower() for s in authentic_skills}
        # Also include individual tokens (e.g. "React" from "React.js")
        for s in authentic_skills:
            for part in s.strip().lower().split():
                if len(part) > 2:
                    authentic_set.add(part)

        stripped_skills: List[str] = []
        sanitized_groups = []

        for group in version.skills:
            kept_in_group = []
            for skill in group.skills:
                skill_clean = skill.strip()
                skill_lower = skill_clean.lower()
                is_authentic = (
                    skill_lower in authentic_set
                    or any(part in authentic_set for part in skill_lower.split() if len(part) > 2)
                    or any(skill_lower in a for a in authentic_set if len(skill_lower) > 3)
                )

                if is_authentic:
                    kept_in_group.append(skill_clean)
                else:
                    stripped_skills.append(skill_clean)

            if kept_in_group:
                group.skills = kept_in_group
                sanitized_groups.append(group)

        version.skills = sanitized_groups
        return version, stripped_skills

    @staticmethod
    def _get_resume_text_blob(version: ResumeVersionDTO) -> str:
        parts: List[str] = [version.summary.lower()]
        for g in version.skills:
            parts.extend([s.lower() for s in g.skills])
        for exp in version.experience:
            parts.append(exp.role.lower())
            parts.append(exp.company.lower())
            parts.append(exp.description.lower())
            parts.extend([b.lower() for b in exp.bullet_points])
        for proj in version.projects:
            parts.append(proj.title.lower())
            parts.append(proj.description.lower())
            parts.extend([b.lower() for b in proj.bullet_points])
        return " ".join(parts)

    @staticmethod
    def _evaluate_section_quality(version: ResumeVersionDTO) -> float:
        score = 60.0

        # Summary check (80-600 characters is ideal)
        sum_len = len(version.summary.strip())
        if 80 <= sum_len <= 600:
            score += 15.0
        elif sum_len > 30:
            score += 8.0

        # Check for action verbs in bullet points
        all_bullets = []
        for exp in version.experience:
            all_bullets.extend(exp.bullet_points)
        for proj in version.projects:
            all_bullets.extend(proj.bullet_points)

        if all_bullets:
            verbs_found = 0
            metrics_found = 0
            for b in all_bullets:
                lower_b = b.lower()
                words = lower_b.split()
                if words and words[0] in ACTION_VERBS:
                    verbs_found += 1
                elif any(v in lower_b for v in ACTION_VERBS):
                    verbs_found += 1

                # Check for metrics: digits, %, $, 'x to y'
                if re.search(r"\d+%|\$\d+|\b\d+\b|\b\d+x\b", lower_b):
                    metrics_found += 1

            verb_ratio = verbs_found / max(len(all_bullets), 1)
            metric_ratio = metrics_found / max(len(all_bullets), 1)

            score += min(15.0, verb_ratio * 15.0)
            score += min(10.0, metric_ratio * 10.0)

        return min(100.0, round(score, 1))

    @staticmethod
    def _evaluate_experience_relevance(version: ResumeVersionDTO, job_title: str, job_description: str) -> float:
        if not version.experience:
            return 40.0

        score = 65.0
        title_tokens = [t.lower() for t in job_title.split() if len(t) > 2]

        for exp in version.experience:
            role_lower = exp.role.lower()
            if any(t in role_lower for t in title_tokens):
                score += 15.0
                break

        # Check for overlap between job description key terms and experience
        desc_sample = set(re.findall(r"\b[a-zA-Z]{4,}\b", job_description.lower()))
        exp_sample = set(re.findall(r"\b[a-zA-Z]{4,}\b", " ".join(
            [e.description + " " + " ".join(e.bullet_points) for e in version.experience]
        ).lower()))

        overlap = len(desc_sample.intersection(exp_sample))
        if overlap > 20:
            score += 20.0
        elif overlap > 10:
            score += 12.0
        elif overlap > 5:
            score += 6.0

        return min(100.0, round(score, 1))

    @staticmethod
    def _evaluate_formatting_structure(version: ResumeVersionDTO) -> float:
        score = 40.0
        # Check standard sections
        if version.summary and len(version.summary.strip()) > 20:
            score += 15.0
        if version.skills and len(version.skills) > 0:
            score += 15.0
        if version.experience and len(version.experience) > 0:
            score += 15.0
            # Check bullet count per experience
            avg_bullets = sum(len(e.bullet_points) for e in version.experience) / len(version.experience)
            if avg_bullets >= 2.5:
                score += 10.0
            elif avg_bullets >= 1.5:
                score += 5.0
        if version.education and len(version.education) > 0:
            score += 5.0

        return min(100.0, round(score, 1))
