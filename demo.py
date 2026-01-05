import asyncio
import logging
import sys
import os

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from far.core.orchestrator import FissionOrchestrator
from far.core.cues import CueModerator
from far.memory.episodic_store import EpisodicStore
from far.memory.semantic_store import SemanticStore
from far.memory.procedural_store import ProceduralStore
from far.memory.state_store import StateStore
from far.retrieval.hybrid_search import HybridSearch
from far.retrieval.reranker import Reranker

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

async def main():
    print("Initializing FAR System (Demo Mode)...", flush=True)
    
    # 1. Setup Stores
    semantic = SemanticStore(":memory:")
    episodic = EpisodicStore(":memory:")
    procedural = ProceduralStore()
    state = StateStore() # In-memory default
    
    # 2. Seed Data
    print("Seeding Memory...", flush=True)
    semantic.add_fact("Project Alpha is a top-secret initiative.", ["project-alpha"], {})
    semantic.add_fact("Sector 7 is currently unstable due to power fluctuations.", ["sector-7"], {})
    
    episodic.add_event("Power surge detected in Sector 7.", ["sector-7"])
    episodic.add_event("Admin authorized emergency shutdown for Project Alpha.", ["project-alpha", "admin"])
    
    procedural.add_procedure("Emergency Shutdown", ["Isolate power", "Notify Admin", "Trigger Killswitch"])
    
    state.upsert("project_alpha_status", "ACTIVE", source="sensor")
    state.upsert("sector_7_power", "UNSTABLE", source="sensor")
    
    # 3. Setup Core
    moderator = CueModerator()
    searcher = HybridSearch(
        semantic_store=semantic, 
        episodic_store=episodic, 
        procedural_store=procedural,
        state_store=state
    )
    reranker = Reranker()
    
    orch = FissionOrchestrator(
        moderator=moderator,
        searcher=searcher,
        reranker=reranker,
        max_hops=3
    )
    
    # 4. Run Queries
    
    # Scenario A: Status Check (Should pass)
    query = "What is the status of Project Alpha and Sector 7?"
    print(f"\n--- Query: {query} ---")
    result = await orch.run_mhccr(query, intent="status")
    print(f"Summary: {result['summary']}")
    print(f"Stats: {result['stats']}")
    
    # Scenario B: Procedure Lookup (Should pass)
    query_proc = "How do I perform an emergency shutdown?"
    print(f"\n--- Query: {query_proc} ---")
    result_proc = await orch.run_mhccr(query_proc, intent="how-to")
    print(f"Summary: {result_proc['summary']}")
    
    # Scenario C: Missing Evidence (Coverage Gate Fail)
    query_fail = "What is the secret code for the vault?"
    print(f"\n--- Query: {query_fail} ---")
    result_fail = await orch.run_mhccr(query_fail, intent="factual")
    print(f"Summary: {result_fail['summary']}")

if __name__ == "__main__":
    asyncio.run(main())
