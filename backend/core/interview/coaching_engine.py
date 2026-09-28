"""
Career Coaching and Learning Roadmap Engine for Phase 11.
Computes Interview Readiness Score, identifies Strong & Weak areas,
and generates structured 4-week skill development roadmaps.
"""
from typing import Any, Dict, List, Optional
from core.logging import get_logger

logger = get_logger("interview.coaching_engine")


class CareerCoachingEngine:
    """
    Synthesizes candidate interview telemetry and profile skills into actionable
    coaching insights, readiness scores, and progressive study milestones.
    """

    def generate_coaching_insights(
        self,
        role: str,
        candidate_skills: List[str],
        completed_evaluations: List[Dict[str, Any]],
        mock_sessions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Calculates interview readiness score and generates structured coaching guidance.
        """
        eval_scores = [ev.get("score", 0.0) for ev in completed_evaluations if ev.get("score") is not None]
        mock_scores = [ms.get("score", 0.0) for ms in mock_sessions if ms.get("score") is not None]

        # 1. Compute Interview Readiness Score (0 - 100)
        # Factors: Average question score (40%), Mock interview average (30%), Practice Volume (15%), Skill Breadth (15%)
        avg_eval = (sum(eval_scores) / len(eval_scores)) if eval_scores else 65.0
        avg_mock = (sum(mock_scores) / len(mock_scores)) if mock_scores else (avg_eval - 5.0)
        volume_factor = min(len(eval_scores) * 5.0, 100.0)  # Max out at 20 practiced questions
        skill_factor = min(len(candidate_skills) * 4.0, 100.0)

        readiness_score = round(
            (avg_eval * 0.40) + (avg_mock * 0.30) + (volume_factor * 0.15) + (skill_factor * 0.15),
            1
        )
        readiness_score = max(35.0, min(98.0, readiness_score))

        # 2. Strong & Weak Areas based on category breakdown
        category_scores: Dict[str, List[float]] = {}
        for ev in completed_evaluations:
            cat = ev.get("category", "General")
            sc = ev.get("score")
            if sc is not None:
                category_scores.setdefault(cat, []).append(sc)

        strong_areas: List[str] = []
        weak_areas: List[str] = []

        all_categories = ["Technical", "System Design", "Behavioral", "Project-Based", "HR"]
        for cat in all_categories:
            scores = category_scores.get(cat, [])
            if scores:
                avg = sum(scores) / len(scores)
                if avg >= 75:
                    strong_areas.append(f"{cat} ({round(avg)}%)")
                else:
                    weak_areas.append(f"{cat} ({round(avg)}%)")
            else:
                # Untested categories flagged as focus areas
                if cat in ["System Design", "Behavioral"]:
                    weak_areas.append(f"{cat} (Needs Practice)")
                else:
                    strong_areas.append(f"{cat} (Fundamentals)")

        if not strong_areas:
            strong_areas = ["Core Language Syntax", "Foundational Problem Solving", "Resume Overview"]
        if not weak_areas:
            weak_areas = ["High-Scale System Design", "Edge-Case Handling", "STAR Quantified Results"]

        # 3. Skill Development Recommendations
        skill_recommendations = [
            {
                "skill": "High-Throughput System Design",
                "category": "Architecture",
                "priority": "High",
                "action": "Master distributed caching (Redis Cache-Aside), message queue partitioning (Kafka), and database sharding.",
                "estimatedDays": 7,
            },
            {
                "skill": "STAR Behavioral Articulation",
                "category": "Behavioral",
                "priority": "High",
                "action": "Prepare 5 structured STAR stories highlighting conflict resolution, leadership, and technical post-mortems with quantified impact.",
                "estimatedDays": 4,
            },
            {
                "skill": "Algorithmic Complexity & Edge Cases",
                "category": "Technical",
                "priority": "Medium",
                "action": "Practice Medium/Hard dynamic programming, graph traversals, and concurrency synchronization problems.",
                "estimatedDays": 6,
            },
            {
                "skill": "Model Architecture & Tradeoffs",
                "category": "AI/ML & Domain",
                "priority": "Medium",
                "action": "Prepare deep-dive explanations of your primary projects (e.g. U-Net segmentation, metrics, loss functions, and inference latency).",
                "estimatedDays": 5,
            },
        ]

        # 4. 4-Week Structured Learning Roadmap
        learning_roadmap = [
            {
                "phase": "Week 1",
                "title": "Core Foundations & Data Structures",
                "focus": "Algorithmic Complexity, Concurrency, and System Primitives",
                "duration": "7 Days",
                "milestones": [
                    "Implement LRU Cache with O(1) operations in pure Python",
                    "Review async/multiprocessing concurrency models and lock contention",
                    "Practice 10 LeetCode Medium data structure problems",
                ],
            },
            {
                "phase": "Week 2",
                "title": "Scalable System Design & Data Tier",
                "focus": "Distributed Caching, Sharding, Replication & Consistency",
                "duration": "7 Days",
                "milestones": [
                    "Design real-time notification feed for 50M active users",
                    "Analyze SQL vs NoSQL trade-offs (PostgreSQL vs Cassandra / DynamoDB)",
                    "Whiteboard rate limiting, idempotency keys, and circuit breakers",
                ],
            },
            {
                "phase": "Week 3",
                "title": "Domain Mastery & Portfolio Deep Dive",
                "focus": f"Role-Specific Architecture ({role}) & Project Defenses",
                "duration": "7 Days",
                "milestones": [
                    "Draft comprehensive architectural blueprint for your primary portfolio project",
                    "Rehearse trade-off defense: Why specific models/frameworks were chosen over alternatives",
                    "Conduct peer review of API contracts and data schemas",
                ],
            },
            {
                "phase": "Week 4",
                "title": "Behavioral Excellence & Mock Interview Simulations",
                "focus": "STAR Framework Drills & Full-Length Timed Sessions",
                "duration": "7 Days",
                "milestones": [
                    "Complete 3 full-length timed mock interviews on AI Job Copilot",
                    "Refine 5 STAR stories covering failure, disagreement, and cross-functional leadership",
                    "Verify all response delivery stays within the optimal 2-3 minute window",
                ],
            },
        ]

        return {
            "role": role,
            "interviewReadinessScore": readiness_score,
            "strongAreas": strong_areas[:5],
            "weakAreas": weak_areas[:5],
            "skillDevelopmentRecommendations": skill_recommendations,
            "learningRoadmap": learning_roadmap,
        }
