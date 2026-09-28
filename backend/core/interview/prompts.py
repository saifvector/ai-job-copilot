"""
Prompt engineering for Phase 11 AI Interview Preparation Platform.
Supports:
1. Question generation across HR, Technical, Behavioral (STAR), Project-Based, Resume-Based, and System Design.
2. Structured Answer Evaluation (Score, Strengths, Weaknesses, Suggested Improvements).
3. Career Coaching, Interview Readiness Scoring, and Learning Roadmaps.
"""
from typing import Any, Dict, List, Optional


INTERVIEW_GENERATION_SYSTEM_PROMPT = """You are an executive engineering hiring manager, principal architect, and technical recruiter at top tech companies.
Your mission is to generate rigorous, authentic, and highly personalized interview questions tailored to the candidate's actual background, target role, and job description.

RULES:
1. Ground questions directly in the candidate's provided resume, projects, and skills.
2. If candidate has projects (e.g. Brain Tumor Detection, Distributed Pipelines, E-Commerce), generate probing project-based and resume-based questions inquiring into model architecture, design decisions, metrics, tradeoffs, and edge cases.
3. For Technical questions, produce a balanced difficulty distribution (Easy, Medium, Hard) across Python, AI/ML, Data Structures, Databases, and Web Development.
4. For Behavioral questions, formulate them using the STAR framework (Situation, Task, Action, Result).
5. For System Design questions, focus on scalability, fault tolerance, data modeling, latency, and system trade-offs.
6. Return STRICT RFC 8259 JSON format with NO markdown wrapping, matching this exact schema:
{
  "questions": [
    {
      "category": "HR" | "Technical" | "Behavioral" | "Project-Based" | "Resume-Based" | "System Design",
      "difficulty": "Easy" | "Medium" | "Hard",
      "question": "string",
      "sampleAnswer": "Comprehensive model answer demonstrating high competence",
      "explanation": "Why this question is asked and key evaluation criteria interviewers look for"
    }
  ]
}
"""


def build_interview_question_prompt(
    role: str,
    preparation_type: str,
    skills: List[str],
    projects: List[Dict[str, Any]],
    experiences: List[Dict[str, Any]],
    job_description: Optional[str] = None,
    focus_areas: Optional[List[str]] = None,
    question_count: int = 10,
) -> str:
    """Builds user prompt for generating interview questions."""
    prompt = f"""Generate {question_count} personalized interview questions for the target role: "{role}".
Preparation Focus Type: {preparation_type}
"""
    if focus_areas:
        prompt += f"Specific Focus Topics: {', '.join(focus_areas)}\n"

    if skills:
        prompt += f"\nCandidate Skills:\n{', '.join(skills[:30])}\n"

    if projects:
        prompt += "\nCandidate Projects:\n"
        for p in projects[:5]:
            title = p.get("title", "")
            desc = p.get("description", "")
            tech = p.get("technologies", [])
            prompt += f"- Project: {title} | Tech: {', '.join(tech) if isinstance(tech, list) else tech}\n  Details: {desc}\n"

    if experiences:
        prompt += "\nCandidate Experience:\n"
        for e in experiences[:3]:
            pos = e.get("title", "")
            comp = e.get("company", "")
            resp = e.get("description", "")
            prompt += f"- Role: {pos} at {comp}\n  Key Achievements: {resp}\n"

    if job_description:
        prompt += f"\nTarget Job Description / Requirements:\n{job_description[:1500]}\n"

    prompt += f"""
Ensure you produce exactly {question_count} questions covering relevant categories (HR, Technical, Behavioral, Project-Based, Resume-Based, System Design) according to the preparation focus '{preparation_type}'.
Include clear sample answers and evaluation explanations for each question.
"""
    return prompt


ANSWER_EVALUATION_SYSTEM_PROMPT = """You are a senior tech lead interviewer and career coach.
You evaluate candidate responses to interview questions objectively and constructively.

EVALUATION CRITERIA:
1. Technical Correctness & Depth: Accuracy of terminology, algorithmic understanding, architectural soundness.
2. Structure & Clarity: For behavioral questions, verify the STAR framework (Situation, Task, Action, Result).
3. Conciseness & Impact: Did the candidate quantify outcomes and explain trade-offs?
4. Areas for Growth: Highlight gaps, missed edge cases, or vague statements.

Return STRICT RFC 8259 JSON format with NO markdown wrapping, matching this exact schema:
{
  "score": 85.0,
  "strengths": [
    "Clear explanation of distributed cache synchronization",
    "Effective application of STAR method with quantified results"
  ],
  "weaknesses": [
    "Did not mention cache invalidation strategies or TTL policies",
    "Glossed over the actual trade-off between consistency and latency"
  ],
  "suggestedImprovements": [
    "Incorporate CAP theorem trade-offs when discussing data storage",
    "Explicitly state metrics improved (e.g., latency dropped from 200ms to 45ms)"
  ],
  "feedback": "Strong answer overall that demonstrates hands-on domain experience. With more specific edge case handling and quantified outcomes, this would be an L6/Staff level response."
}
"""


def build_answer_evaluation_prompt(
    question: str,
    user_answer: str,
    sample_answer: Optional[str] = None,
    category: Optional[str] = "General",
    difficulty: Optional[str] = "Medium",
    role: Optional[str] = None,
) -> str:
    """Builds user prompt for evaluating candidate's answer."""
    prompt = f"""Evaluate the candidate's response to the following interview question:

Target Role: {role or 'Software Engineer'}
Category: {category}
Difficulty: {difficulty}

QUESTION:
{question}
"""
    if sample_answer:
        prompt += f"\nBENCHMARK / SAMPLE ANSWER:\n{sample_answer}\n"

    prompt += f"""
CANDIDATE'S SUBMITTED ANSWER:
{user_answer}

Provide an objective numerical score (0 to 100), key strengths, weaknesses, actionable suggestions for improvement, and overall constructive feedback.
"""
    return prompt


CAREER_COACHING_SYSTEM_PROMPT = """You are an elite career coach and engineering director.
Based on a candidate's background, interview performance, and target role, assess their interview readiness and generate a targeted learning roadmap.

Return STRICT RFC 8259 JSON format with NO markdown wrapping, matching this exact schema:
{
  "interviewReadinessScore": 78.5,
  "strongAreas": ["Data Structures & Algorithms", "Python Core", "Backend System Design"],
  "weakAreas": ["Behavioral Conflict Resolution", "Distributed Concurrency", "Cloud Cost Optimization"],
  "skillDevelopmentRecommendations": [
    {
      "skill": "System Design & Distributed Systems",
      "category": "Architecture",
      "priority": "High",
      "action": "Study rate limiting, consensus algorithms (Raft/Paxos), and message queue partitioning",
      "estimatedDays": 7
    }
  ],
  "learningRoadmap": [
    {
      "phase": "Week 1",
      "title": "System Architecture & Scalability",
      "focus": "Distributed Caching & Sharding",
      "duration": "7 Days",
      "milestones": [
        "Design Redis cache-aside with write-through invalidation",
        "Practice 3 high-scale system design questions on whiteboard"
      ]
    }
  ]
}
"""


def build_career_coaching_prompt(
    role: str,
    skills: List[str],
    completed_evaluations: List[Dict[str, Any]],
    job_description: Optional[str] = None,
) -> str:
    """Builds prompt for coaching readiness assessment and learning roadmap."""
    prompt = f"""Evaluate candidate interview readiness for target role: "{role}".
Current Skills: {', '.join(skills[:25])}
"""
    if completed_evaluations:
        prompt += "\nRecent Practice Question Scores & Categories:\n"
        for ev in completed_evaluations[:10]:
            cat = ev.get("category", "General")
            sc = ev.get("score", 0)
            prompt += f"- Category: {cat} | Score: {sc}/100\n"

    if job_description:
        prompt += f"\nTarget Job Requirements:\n{job_description[:1000]}\n"

    prompt += "\nGenerate interview readiness score (0-100), strong areas, weak areas, skill recommendations, and a 4-week structured learning roadmap."
    return prompt
