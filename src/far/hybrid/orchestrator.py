"""Universal orchestrator ("The Platform")."""
from __future__ import annotations

import time
from typing import Callable, Dict

from .cortex import SemanticVectorCortex
from .ledger import ImmutableEventLedger
from .logging_config import get_logger
from .types import MemoryItem

logger = get_logger(__name__)


class UniversalOrchestrator:
    """Central dispatch that routes queries to the appropriate subsystem."""

    def __init__(self):
        self.ledger = ImmutableEventLedger(":memory:")
        self.cortex = SemanticVectorCortex()
        self.skills: Dict[str, Callable[[str, str], str]] = {}
        logger.info("Universal Orchestrator Initialized. System Ready.")

    def register_capability(self, name: str, handler_func: Callable[[str, str], str]) -> None:
        """Register a domain-specific handler."""
        logger.info("Registering Capability: '%s'", name)
        self.skills[name.lower()] = handler_func

    def ingest_data(self, source_name: str, content: str, content_type: str = "text") -> MemoryItem:
        """Unified ingestion pipeline that writes to the ledger and cortex."""
        self.ledger.record_event("SYSTEM", "INGEST_INITIATED", {"source": source_name, "type": content_type})
        memory_id = self.cortex.absorb_knowledge(content, source_name)
        logger.info("Ingested artifact: %s", source_name)
        return next(item for item in self.cortex.kb if item.id == memory_id)

    def execute_query(self, user_query: str) -> str:
        """Execute a multi-hop resolution of the user query."""
        start_time = time.time()
        self.ledger.record_event("USER", "QUERY_RECEIVED", {"text": user_query})

        relevant_memories = self.cortex.associative_recall(user_query, top_k=3)
        context_block = "\n".join([f"[{m.metadata.get('source_id', 'UNKNOWN')}] {m.content}" for m in relevant_memories])

        active_skill, final_answer = self._dispatch_to_skill(user_query, context_block)
        if final_answer is None:
            final_answer = self._default_response(context_block)

        latency_ms = (time.time() - start_time) * 1000
        logger.info("Query Processed. Latency: %.2fms. Routing: %s", latency_ms, active_skill)
        return f"[{active_skill}] {final_answer}"

    def _dispatch_to_skill(self, user_query: str, context_block: str) -> tuple[str, str | None]:
        for skill_name, handler in self.skills.items():
            if skill_name in user_query.lower():
                try:
                    return skill_name.title(), handler(user_query, context_block)
                except Exception as exc:  # pragma: no cover - defensive
                    logger.error("Skill '%s' failed: %s", skill_name, exc)
                    return skill_name.title(), "Error executing domain skill."
        return "General Intelligence", None

    @staticmethod
    def _default_response(context_block: str) -> str:
        if context_block:
            return f"Based on available context:\n{context_block}"
        return "No relevant context found in knowledge base."
