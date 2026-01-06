"""Semantic vector cortex ("The Brain")."""
from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from .logging_config import get_logger
from .types import MemoryItem, MemoryType

logger = get_logger(__name__)

ML_ACCELERATION = False
SentenceTransformer: Any
util: Any

try:  # pragma: no cover - optional dependency
    import numpy as np  # noqa: F401
    from sentence_transformers import SentenceTransformer, util

    ML_ACCELERATION = True
except Exception:  # pragma: no cover - graceful degradation
    logger.warning(
        "Neural Engine (sentence_transformers) not active. Using Symbolic Fallback (Cognitive Token Overlap)."
    )
else:
    logger.info("Neural Engine Online. Vector Accelerators Active.")


class SemanticVectorCortex:
    """High-dimensional associative memory with a heuristic fallback."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = None
        self.kb: List[MemoryItem] = []

        if ML_ACCELERATION:
            self.model = self._initialize_model(model_name)

    def _initialize_model(self, model_name: str):  # pragma: no cover - heavy dependency
        try:
            logger.info("Initializing Neural Engine: %s...", model_name)
            model = SentenceTransformer(model_name)
            logger.info(
                "Neural Engine Online. GPU Acceleration: %s",
                "Enabled" if "cuda" in str(model.device) else "Disabled",
            )
            return model
        except Exception as exc:
            logger.error("Failed to load Neural Engine: %s", exc)
            return None

    def absorb_knowledge(self, content: str, source_id: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Ingest unstructured data into the vector space."""
        meta: Dict[str, Any] = metadata.copy() if metadata else {}
        meta["source_id"] = source_id

        embedding = None
        if self.model:
            embedding = self.model.encode(content)  # type: ignore[arg-type]

        uid = str(uuid.uuid4())
        item = MemoryItem(
            id=uid,
            type=MemoryType.SEMANTIC,
            content=content,
            metadata=meta,
            embedding=embedding,
        )
        self.kb.append(item)
        logger.info("Absorbed knowledge from %s", source_id)
        return uid

    def associative_recall(self, query: str, top_k: int = 3) -> List[MemoryItem]:
        """Perform semantic search or symbolic fallback."""
        if not self.kb:
            return []

        if self.model:
            query_embedding = self.model.encode(query)
            scores = []
            for item in self.kb:
                if item.embedding is not None:
                    score = util.cos_sim(query_embedding, item.embedding).item()  # type: ignore[attr-defined]
                    scores.append((score, item))

            scores.sort(key=lambda x: x[0], reverse=True)
            return [s[1] for s in scores[:top_k]]

        return self._heuristic_recall(query, top_k)

    def _heuristic_recall(self, query: str, top_k: int) -> List[MemoryItem]:
        logger.debug("Using heuristic retrieval strategy.")
        q_tokens = set(query.lower().split())
        scores = []
        for item in self.kb:
            c_tokens = set(item.content.lower().split())
            overlap = len(q_tokens.intersection(c_tokens))
            if c_tokens:
                score = overlap / (len(q_tokens) + len(c_tokens) - overlap)
                scores.append((score, item))
        scores.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scores[:top_k]]
