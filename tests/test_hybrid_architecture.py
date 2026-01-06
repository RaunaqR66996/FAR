import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from far.hybrid import (
    ImmutableEventLedger,
    SemanticVectorCortex,
    UniversalOrchestrator,
    creative_association_handler,
)


def test_immutable_event_ledger_records_and_replays():
    ledger = ImmutableEventLedger(":memory:")
    ledger.record_event("user-1", "LOGIN", {"detail": "successful"})
    ledger.record_event("user-1", "QUERY", {"text": "status"})

    history = ledger.replay_history("user-1")
    assert len(history) == 2
    assert [event.event_type for event in history] == ["LOGIN", "QUERY"]


def test_semantic_vector_cortex_absorb_and_recall_fallback():
    cortex = SemanticVectorCortex()
    cortex.absorb_knowledge("The sky is blue", "doc_a")
    cortex.absorb_knowledge("Grass is green", "doc_b")

    results = cortex.associative_recall("What color is the sky?", top_k=1)
    assert results
    assert "sky" in results[0].content.lower()


def test_orchestrator_skill_dispatch_and_context_builder():
    orchestrator = UniversalOrchestrator()
    orchestrator.register_capability("synthesis", creative_association_handler)
    orchestrator.ingest_data("paper.txt", "Quantum entanglement enables spooky action.")

    response = orchestrator.execute_query("Run synthesis on entanglement")
    assert response.startswith("[General Intelligence]") or response.startswith("[Synthesis]")
    assert bool(re.search(r"context tokens", response))

    fallback = orchestrator.execute_query("Unknown intent question")
    assert "Based on available context" in fallback or "No relevant context" in fallback
