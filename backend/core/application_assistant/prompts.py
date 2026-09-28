"""
Prompts for Phase 12 Application Assistant Engine.
Enforces strict truthfulness, candidate-grounded evidence, and structured responses.

CRITICAL INSTRUCTION:
- Truthful only
- No fabricated experience
- No fabricated skills
- No fabricated employment history
- If candidate details for a specific question are unknown or variable (e.g. salary expectation, exact notice period),
  provide an honest template with an explicit [Candidate Input Required: ...] placeholder.
"""
from typing import Any, Dict, List, Optional


APPLICATION_ASSISTANT_SYSTEM_PROMPT = """You are the AI Application Assistant for AI Job Copilot, powered by Gemini 2.5 Pro.
Your role is to help job seekers prepare authentic, compelling, and 100% truthful responses for job applications.

STRICT COMPLIANCE RULES:
1. TRUTHFULNESS MANDATE: You MUST NOT fabricate, exaggerate, or invent any job experience, company names, skills, certifications, degrees, or dates.
2. EVIDENCE GROUNDING: Every statement about qualifications, projects, or accomplishments must be directly grounded in the provided candidate profile, resume, and experience data.
3. ADAPTIVE ANSWER TYPES:
   - "Text": Provide professional, articulate responses tailored to the role. For motivation questions, articulate why the candidate is drawn to the company's mission and how their actual skills align. For project questions, follow the STAR framework (Situation, Task, Action, Result) using verifiable candidate projects.
   - "YesNo": Answer strictly "Yes" or "No" based on candidate records. If candidate clearly possesses the required skill/credential, respond "Yes" (with brief truthful context if allowed). If not found or unverifiable, answer honestly.
   - "MultiSelect": Select only options from the provided list that are verifiable in the candidate's skills and experience.
   - "Numeric": Provide clean numerical integers or floats (e.g., "5" for years of experience) calculated honestly from the candidate's employment timeline.
4. TRANSPARENT PLACEHOLDERS: If asked about candidate-specific subjective preferences not present in the profile (e.g. desired salary range, exact notice period, or relocation willingness), provide a professional response that includes a clear marker: "[Candidate Input Required: confirm your preferred salary/notice period]".

OUTPUT FORMAT:
Return a valid JSON object with the following structure:
{
  "answers": [
    {
      "question": "Question text",
      "answer_type": "Text|YesNo|MultiSelect|Numeric",
      "generated_answer": "Truthful, polished answer grounded in candidate profile.",
      "rationale": "Brief note on why this answer is truthful and how it matches profile data.",
      "confidence_score": 0.95
    }
  ],
  "candidate_summary": "1-2 sentence executive summary of candidate alignment.",
  "truthfulness_verified": true
}
"""


def build_application_answers_prompt(
    job_title: str,
    company: str,
    job_description: Optional[str],
    job_requirements: Optional[List[str]],
    questions: List[Dict[str, Any]],
    candidate_profile: Dict[str, Any],
    skills: List[str],
    experiences: List[Dict[str, Any]],
    projects: List[Dict[str, Any]],
    education: List[Dict[str, Any]],
) -> str:
    """
    Constructs the prompt for generating truthful application answers.
    """
    prompt = f"""Generate tailored, 100% truthful application responses for the following target position:

TARGET JOB DETAILS:
- Role / Title: {job_title}
- Company: {company}
- Requirements: {', '.join(job_requirements) if job_requirements else 'See description'}
- Description: {job_description[:1200] if job_description else 'N/A'}

VERIFIED CANDIDATE PROFILE:
- Full Name: {candidate_profile.get('name', 'Candidate')}
- Headline: {candidate_profile.get('headline', 'Software Engineer')}
- Summary / Bio: {candidate_profile.get('summary', 'Experienced developer')}
- Verified Skills: {', '.join(skills) if skills else 'Not specified'}

VERIFIED WORK EXPERIENCES:
"""
    if experiences:
        for idx, exp in enumerate(experiences[:5], 1):
            prompt += f"{idx}. {exp.get('title', 'Role')} at {exp.get('company', 'Company')} ({exp.get('start_date', '')} - {exp.get('end_date', 'Present')})\n"
            desc = exp.get('description', '')
            if desc:
                prompt += f"   Highlights: {desc[:200]}\n"
    else:
        prompt += "No formal experience recorded.\n"

    prompt += "\nVERIFIED PROJECTS:\n"
    if projects:
        for idx, proj in enumerate(projects[:4], 1):
            prompt += f"{idx}. {proj.get('title', 'Project')}: {proj.get('description', '')[:200]}\n"
            p_skills = proj.get('skills', [])
            if p_skills:
                prompt += f"   Technologies: {', '.join(p_skills)}\n"
    else:
        prompt += "No portfolio projects recorded.\n"

    prompt += "\nVERIFIED EDUCATION:\n"
    if education:
        for idx, edu in enumerate(education[:3], 1):
            prompt += f"{idx}. {edu.get('degree', 'Degree')} in {edu.get('field_of_study', 'Major')}, {edu.get('institution', 'University')} ({edu.get('start_year', '')} - {edu.get('end_year', '')})\n"
    else:
        prompt += "No education records.\n"

    prompt += "\nAPPLICATION QUESTIONS TO ANSWER:\n"
    for idx, q in enumerate(questions, 1):
        q_text = q.get("question", "")
        q_type = q.get("answer_type", "Text")
        q_opts = q.get("options", [])
        opts_str = f" [Available options: {', '.join(q_opts)}]" if q_opts else ""
        prompt += f"{idx}. Question: {q_text} | Type: {q_type}{opts_str}\n"

    prompt += """
REMINDER:
- Ground every statement in candidate's verified skills, projects, and experiences above.
- Never invent employment history or capabilities.
- Answer all listed questions in the same order.
- Return only valid JSON.
"""
    return prompt
