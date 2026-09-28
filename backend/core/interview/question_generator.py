"""
Question Generation Engine for Phase 11 AI Interview Preparation Platform.
Uses Gemini 2.5 Pro (Primary) with Gemini 2.5 Flash (Fallback) via AIOrchestrator,
with a robust domain-grounded fallback template engine.
"""
import json
from typing import Any, Dict, List, Optional
from core.ai.orchestrator import AIOrchestrator
from core.interview.prompts import (
    INTERVIEW_GENERATION_SYSTEM_PROMPT,
    build_interview_question_prompt,
)
from core.logging import get_logger

logger = get_logger("interview.question_generator")


class InterviewQuestionGenerator:
    """
    Generates personalized interview questions grounded in the candidate's resume,
    skills, portfolio projects, and target job posting.
    """

    def __init__(self, orchestrator: Optional[AIOrchestrator] = None):
        self.orchestrator = orchestrator or AIOrchestrator()

    async def generate_questions(
        self,
        role: str,
        preparation_type: str = "Comprehensive",
        skills: Optional[List[str]] = None,
        projects: Optional[List[Dict[str, Any]]] = None,
        experiences: Optional[List[Dict[str, Any]]] = None,
        job_description: Optional[str] = None,
        focus_areas: Optional[List[str]] = None,
        question_count: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Executes question generation through AI with graceful domain fallback.
        """
        skills = skills or ["Python", "Machine Learning", "FastAPI", "React", "PostgreSQL", "Docker"]
        projects = projects or []
        experiences = experiences or []

        prompt = build_interview_question_prompt(
            role=role,
            preparation_type=preparation_type,
            skills=skills,
            projects=projects,
            experiences=experiences,
            job_description=job_description,
            focus_areas=focus_areas,
            question_count=question_count,
        )

        try:
            raw_json, telemetry = await self.orchestrator.execute_with_fallback(
                prompt=prompt,
                system_instruction=INTERVIEW_GENERATION_SYSTEM_PROMPT,
            )
            parsed = json.loads(raw_json)
            questions = parsed.get("questions", [])
            if questions and isinstance(questions, list) and len(questions) > 0:
                logger.info(
                    "AI interview question generation succeeded",
                    extra={"count": len(questions), "model": telemetry.get("model_used")},
                )
                return questions[:question_count]
        except Exception as exc:
            logger.warning(
                f"AI question generation failed ({exc}). Engaging domain-grounded generator fallback.",
                extra={"role": role, "error": str(exc)},
            )

        # High-fidelity domain-grounded fallback generator
        return self._generate_fallback_questions(
            role=role,
            preparation_type=preparation_type,
            skills=skills,
            projects=projects,
            experiences=experiences,
            question_count=question_count,
        )

    def _generate_fallback_questions(
        self,
        role: str,
        preparation_type: str,
        skills: List[str],
        projects: List[Dict[str, Any]],
        experiences: List[Dict[str, Any]],
        question_count: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Constructs deterministic, high-quality interview questions adhering to requirements:
        - Resume-based / Project-based questions (e.g. Brain Tumor Detection, U-Net, metrics)
        - Technical questions (Easy, Medium, Hard across Python, AI/ML, Data Structures, Databases, Web)
        - Behavioral questions (STAR format)
        - System Design questions
        """
        questions: List[Dict[str, Any]] = []

        # 1. Project-Based & Resume-Based Questions
        project_title = "Brain Tumor Detection"
        if projects and len(projects) > 0:
            first_project = projects[0]
            project_title = first_project.get("title", project_title)

        questions.append({
            "category": "Project-Based",
            "difficulty": "Hard",
            "question": f"For your '{project_title}' project, explain your model architecture in detail. Why did you choose U-Net over traditional CNNs or Vision Transformers, and what specific loss functions and evaluation metrics (e.g. Dice coefficient, IoU) did you use?",
            "sampleAnswer": f"In the {project_title} project, I implemented a modified 2D/3D U-Net architecture characterized by an encoder-decoder path with skip connections that preserve high-resolution spatial feature maps crucial for fine boundary localization. I selected U-Net because biomedical segmentation often operates under limited annotated data where pixel-level localization is critical. I utilized a combined Binary Cross-Entropy (BCE) and Soft Dice Loss to counteract extreme class imbalance (tumor pixels vs. healthy tissue), achieving a mean Dice score of 0.89 and IoU of 0.81.",
            "explanation": "Evaluates architectural comprehension, rationale behind framework decisions, and mathematical awareness of domain-specific loss functions.",
        })

        questions.append({
            "category": "Resume-Based",
            "difficulty": "Medium",
            "question": f"Walking through your background for this {role} opportunity, what was the most complex technical bottleneck you resolved in your recent experience, and how did you measure the business impact?",
            "sampleAnswer": "In my previous role, our distributed processing pipeline experienced severe memory pressure and 95th percentile latency spikes under peak ingestion. I profiled the asynchronous event workers, identified unbuffered database connection pools and unbounded queue memory leaks, and migrated the ingestion pipeline to a partitioned Kafka topic with async batched writes. This reduced p95 latency from 450ms to 78ms and cut compute infrastructure spend by 32%.",
            "explanation": "Assesses candidate self-awareness, technical leadership, profiling methodology, and ability to connect architectural changes to measurable business value.",
        })

        # 2. Technical Questions (Easy, Medium, Hard)
        # Technical: Python (Easy)
        questions.append({
            "category": "Technical",
            "difficulty": "Easy",
            "question": "How do Python's GIL (Global Interpreter Lock), multiprocessing, and asyncio differ in managing concurrency, and when should you choose each?",
            "sampleAnswer": "The GIL ensures only one native thread executes Python bytecode at any moment, protecting CPython memory management. For CPU-bound workloads (e.g. image processing or numerical computation), multiprocessing is necessary to bypass the GIL and utilize multiple CPU cores. For I/O-bound operations (e.g. web scraping, microservice HTTP calls, database querying), asyncio provides cooperative single-threaded asynchronous concurrency via an event loop without OS thread overhead.",
            "explanation": "Validates core Python concurrency primitives and architectural decision-making between I/O vs. CPU concurrency.",
        })

        # Technical: Data Structures & Algorithms (Medium)
        questions.append({
            "category": "Technical",
            "difficulty": "Medium",
            "question": "Describe how you would design an LRU (Least Recently Used) cache with O(1) time complexity for both get() and put() operations. What data structures are required?",
            "sampleAnswer": "An optimal O(1) LRU cache combines a Doubly Linked List with a Hash Map. The Hash Map stores keys mapped directly to doubly linked list nodes, giving O(1) lookup. The Doubly Linked List maintains node access order: the most recently accessed node is moved to the head, and the least recently used node is at the tail. Eviction removes the tail node in O(1) and deletes its key from the hash map.",
            "explanation": "Tests classic composite data structure design, pointer manipulation, and asymptotic complexity trade-offs.",
        })

        # Technical: Databases & Backend (Medium)
        questions.append({
            "category": "Technical",
            "difficulty": "Medium",
            "question": "Explain the difference between optimistic and pessimistic locking in relational databases like PostgreSQL. How do you prevent lost updates in concurrent transactions?",
            "sampleAnswer": "Pessimistic locking explicitly locks database rows at read time using 'SELECT ... FOR UPDATE', blocking other transactions until commit or rollback; it is best when collision probability is high. Optimistic locking does not lock rows on read; instead, it tracks a version number or timestamp and checks 'WHERE id = :id AND version = :expected_version' at write time. If another transaction modified the row, the update fails or retries, which is ideal for low-contention environments.",
            "explanation": "Verifies data consistency mastery, transaction isolation levels, and concurrency resilience in distributed systems.",
        })

        # Technical: AI/ML & Deep Learning (Hard)
        questions.append({
            "category": "Technical",
            "difficulty": "Hard",
            "question": "How does self-attention in Transformer models calculate token relationships, what is its mathematical computational complexity, and how do FlashAttention or linear attention techniques optimize it?",
            "sampleAnswer": "Self-attention computes Attention(Q, K, V) = softmax(Q * K^T / sqrt(d_k)) * V. For sequence length N and dimension D, calculating Q*K^T requires O(N^2 * D) operations and O(N^2) memory storage for the attention matrix. FlashAttention optimizes this by tiling matrix multiplications to fit within fast GPU SRAM memory and fusing the softmax computation without materializing the full N x N matrix in high-bandwidth memory (HBM), drastically speeding up execution and enabling longer context windows.",
            "explanation": "Probes deep understanding of modern deep learning foundation architectures, attention mechanics, and hardware-level memory bandwidth optimizations.",
        })

        # 3. Behavioral Questions (STAR Format)
        questions.append({
            "category": "Behavioral",
            "difficulty": "Medium",
            "question": "Describe a situation where you faced a significant technical project failure or missed a critical deadline. Using the STAR format, what happened, how did you respond, and what did you learn?",
            "sampleAnswer": "Situation: Two weeks before launch of a payment service, our staging stress tests revealed severe deadlock conditions during concurrent checkout. Task: As lead engineer, I had to prevent launch delay while ensuring absolute transaction integrity. Action: I immediately convened a post-mortem, traced the locks to mismatched acquisition ordering between order reservation and inventory ledger tables, restructured the transactions to follow strict alphabetical lock ordering, and implemented comprehensive chaos testing. Result: We patched the bug in 72 hours, launched on schedule, and processed over 50,000 transactions on launch day with zero deadlocks.",
            "explanation": "Evaluates honesty, resilience under pressure, structured communication (STAR), and capacity for constructive technical reflection.",
        })

        questions.append({
            "category": "Behavioral",
            "difficulty": "Medium",
            "question": "Tell me about a time you had a technical disagreement with a senior engineer or product manager. How did you resolve the conflict (STAR format)?",
            "sampleAnswer": "Situation: On a core API redesign, the lead architect wanted a pure GraphQL schema, while our mobile and telemetry teams required REST/gRPC for constrained bandwidth and predictable latency. Task: I was responsible for the core contract specification and needed to achieve consensus without stalling the sprint. Action: Rather than debating theoretical merits, I created a benchmarking prototype measuring mobile payload sizes, cacheability via CDNs, and client battery consumption. I presented the empirical metrics objectively in an engineering review. Result: The team agreed on a hybrid approach: REST/gRPC for high-throughput mobile endpoints and GraphQL for internal analytics dashboards.",
            "explanation": "Assesses collaboration, emotional intelligence, data-driven dispute resolution, and alignment with organizational goals.",
        })

        # 4. System Design Question
        questions.append({
            "category": "System Design",
            "difficulty": "Hard",
            "question": "Design a real-time notification and feed generation system that can deliver targeted updates to 50 million active users. Discuss data storage, message brokering, fan-out strategy (push vs. pull), and cache invalidation.",
            "sampleAnswer": "Architecture: Use an API Gateway with WebSocket/SSE connections for connected clients. An Ingestion Service publishes user events to Apache Kafka. For fan-out, implement a hybrid model: fan-out-on-write (push to Redis inbox) for users with under 25,000 followers, and fan-out-on-read (pull merge from source feeds) for celebrity/influencer accounts to avoid write amplification. Use Cassandra or DynamoDB for persistent timeline storage partitioned by userId, and Redis clusters with TTLs for active timeline caching.",
            "explanation": "Evaluates full-scale architectural thinking, fan-out trade-offs, caching, distributed queues, and high-availability design.",
        })

        # 5. HR Question
        questions.append({
            "category": "HR",
            "difficulty": "Easy",
            "question": f"Why are you targeting this {role} role at this stage of your career, and how do your long-term career goals align with our team's mission?",
            "sampleAnswer": f"Throughout my career, I have focused on building scalable, reliable distributed systems and production AI integrations. At this stage, I am looking to step into a {role} position where I can not only design high-impact technical architectures, but also mentor fellow engineers and bridge cross-functional requirements with product leadership. Your team's focus on innovative, reliable solutions directly matches my ambition to tackle complex distributed challenges at scale.",
            "explanation": "Checks candidate motivation, cultural fit, role alignment, and long-term career trajectory.",
        })

        return questions[:question_count]
