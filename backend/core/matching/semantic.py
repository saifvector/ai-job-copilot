"""
Semantic Matching and Embedding Abstraction Layer.
Provides vector similarity and domain acronym/synonym resolution (e.g. ML <-> Machine Learning).
"""
import math
import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set, Tuple
from core.config import settings
from core.logging import get_logger

logger = get_logger("matching.semantic")


# Canonical Tech/Role Acronyms & Synonyms Registry
SYNONYM_GROUPS: List[Set[str]] = [
    {"machine learning", "ml", "deep learning", "dl"},
    {"artificial intelligence", "ai", "genai", "generative ai"},
    {"natural language processing", "nlp", "computational linguistics"},
    {"computer vision", "cv"},
    {"large language models", "large language model", "llm", "llms"},
    {"kubernetes", "k8s"},
    {"postgresql", "postgres", "psql"},
    {"javascript", "js", "ecmascript"},
    {"typescript", "ts"},
    {"python", "py", "python3"},
    {"golang", "go"},
    {"amazon web services", "aws"},
    {"google cloud platform", "google cloud", "gcp"},
    {"microsoft azure", "azure"},
    {"docker", "containers", "containerization"},
    {"continuous integration", "continuous deployment", "ci/cd", "cicd"},
    {"software engineer", "software developer", "swe", "software development engineer", "sde"},
    {"site reliability engineer", "site reliability engineering", "sre"},
    {"data scientist", "data science"},
    {"data engineer", "data engineering"},
    {"frontend", "front-end", "ui engineer", "client-side"},
    {"backend", "back-end", "server-side", "api engineer"},
    {"fullstack", "full-stack", "full stack"},
    {"qa engineer", "quality assurance", "test engineer", "sdet"},
    {"react", "reactjs", "react.js"},
    {"vue", "vuejs", "vue.js"},
    {"angular", "angularjs"},
    {"node", "nodejs", "node.js"},
    {"fastapi", "fast-api"},
    {"django", "django rest framework", "drf"},
    {"graphql", "gql"},
    {"rest api", "restful api", "rest", "restful"},
    {"sql", "relational database", "rdbms"},
    {"nosql", "non-relational database", "mongodb", "document db"},
]

# Build fast lookup map from alias to group identifier
ALIAS_MAP: Dict[str, int] = {}
for idx, group in enumerate(SYNONYM_GROUPS):
    for term in group:
        ALIAS_MAP[term] = idx


def normalize_term(term: str) -> str:
    """Strip punctuation and lowercase a term for consistent comparison."""
    cleaned = re.sub(r"[^\w\s\+\#]", " ", term.lower())
    return " ".join(cleaned.split())


class BaseEmbeddingProvider(ABC):
    """Abstract interface for embedding generation and semantic similarity."""

    @abstractmethod
    async def get_embedding(self, text: str) -> List[float]:
        """Compute float vector representation for text."""
        pass

    @abstractmethod
    def compute_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors in range [-1.0, 1.0]."""
        pass


class FastSemanticProvider(BaseEmbeddingProvider):
    """
    Sub-millisecond high-speed semantic provider using char n-grams,
    token sets, and the canonical tech acronym taxonomy.
    Guarantees sub-millisecond execution without external network latency.
    """

    def _get_char_ngrams(self, text: str, n: int = 3) -> Dict[str, int]:
        s = f" {text} "
        ngrams: Dict[str, int] = {}
        for i in range(len(s) - n + 1):
            gram = s[i:i + n]
            ngrams[gram] = ngrams.get(gram, 0) + 1
        return ngrams

    async def get_embedding(self, text: str) -> List[float]:
        # Fast provider uses direct similarity
        return []

    def compute_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm_a = math.sqrt(sum(a * a for a in vec1))
        norm_b = math.sqrt(sum(b * b for b in vec2))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return max(0.0, min(1.0, dot / (norm_a * norm_b)))

    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        t1 = normalize_term(text1)
        t2 = normalize_term(text2)

        if not t1 or not t2:
            return 0.0

        if t1 == t2:
            return 1.0

        # Check synonym groups
        grp1 = ALIAS_MAP.get(t1)
        grp2 = ALIAS_MAP.get(t2)
        if grp1 is not None and grp2 is not None and grp1 == grp2:
            return 0.98

        # Substring / token containment
        tokens1 = set(t1.split())
        tokens2 = set(t2.split())
        if tokens1 and tokens2:
            if tokens1.issubset(tokens2) or tokens2.issubset(tokens1):
                overlap = len(tokens1.intersection(tokens2)) / max(len(tokens1), len(tokens2))
                return max(0.85, overlap)

            jaccard = len(tokens1.intersection(tokens2)) / len(tokens1.union(tokens2))
            if jaccard >= 0.5:
                return jaccard

        # Character 3-gram cosine similarity for spelling / suffix variations
        g1 = self._get_char_ngrams(t1)
        g2 = self._get_char_ngrams(t2)
        all_grams = set(g1.keys()).union(set(g2.keys()))
        if not all_grams:
            return 0.0

        dot = sum(g1.get(g, 0) * g2.get(g, 0) for g in all_grams)
        norm1 = math.sqrt(sum(v * v for v in g1.values()))
        norm2 = math.sqrt(sum(v * v for v in g2.values()))
        if norm1 == 0 or norm2 == 0:
            return 0.0

        ngram_sim = dot / (norm1 * norm2)
        return max(0.0, min(1.0, ngram_sim))


class SemanticMatcher:
    """
    High-level Semantic Matching engine with caching and acronym resolution.
    Seamlessly resolves 'ML' <-> 'Machine Learning' and 'AI' <-> 'Artificial Intelligence'.
    """

    def __init__(self, provider: Optional[BaseEmbeddingProvider] = None):
        self.provider = provider or FastSemanticProvider()
        self._cache: Dict[Tuple[str, str], float] = {}

    def get_similarity(self, term1: str, term2: str) -> float:
        """
        Calculate semantic similarity score in range [0.0, 1.0].
        Results are cached for ultra-high throughput.
        """
        key = (term1.lower().strip(), term2.lower().strip())
        rev_key = (key[1], key[0])
        if key in self._cache:
            return self._cache[key]
        if rev_key in self._cache:
            return self._cache[rev_key]

        if isinstance(self.provider, FastSemanticProvider):
            score = self.provider.calculate_text_similarity(term1, term2)
        else:
            score = 0.0

        self._cache[key] = score
        return score

    def is_match(self, term1: str, term2: str, threshold: float = 0.80) -> Tuple[bool, float]:
        """
        Determine if two terms semantically match based on threshold.
        Returns (is_match, similarity_score).
        """
        sim = self.get_similarity(term1, term2)
        return (sim >= threshold, sim)

    def find_best_match(
        self,
        query: str,
        candidates: List[str],
        threshold: float = 0.75,
    ) -> Tuple[Optional[str], float]:
        """
        Find closest semantic match for a query among a list of candidate strings.
        """
        if not candidates:
            return None, 0.0

        best_candidate: Optional[str] = None
        best_score = 0.0

        for candidate in candidates:
            score = self.get_similarity(query, candidate)
            if score > best_score:
                best_score = score
                best_candidate = candidate

        if best_score >= threshold:
            return best_candidate, best_score
        return None, best_score


# Global default semantic matcher instance
default_semantic_matcher = SemanticMatcher()
