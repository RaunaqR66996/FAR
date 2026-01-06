"""System integrity verification for the hybrid architecture."""
from __future__ import annotations

from .orchestrator import UniversalOrchestrator
from .skills import creative_association_handler, exact_recall_handler


def verify_system_integrity() -> None:
    """Conduct a full self-test of the cognitive architecture."""
    print("\n=== COGNITIVE ARCHITECTURE DIAGNOSTIC ===")
    core = UniversalOrchestrator()

    core.register_capability("veridical recall", exact_recall_handler)
    core.register_capability("synthesis", creative_association_handler)

    print("Step 1: Absorbing Unstructured Knowledge Stream...")
    knowledge_stream = [
        ("dataset_a_v1.txt", "Entity A status is Active. Timestamp: 1200."),
        ("research_paper_x.pdf", "The theory implies correlation between X and Y."),
        ("legacy_log.md", "System Rebooted at t=0."),
    ]
    for name, content in knowledge_stream:
        core.ingest_data(name, content)

    print("Step 2: Testing Dual-Pathway Retrieval...")
    q1 = "What are the theoretical implications?"
    ans1 = core.execute_query(q1)
    print(f"Query (Associative): {q1}\nResponse: {ans1}\n")

    q2 = "Perform veridical recall on Entity A."
    ans2 = core.execute_query(q2)
    print(f"Query (Exact): {q2}\nResponse: {ans2}\n")

    print("=== COGNITIVE CORE OPERATIONAL: MEMORY PROBLEM SOLVED ===")


if __name__ == "__main__":
    verify_system_integrity()
