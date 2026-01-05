from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional

from far.core.orchestrator import FissionOrchestrator
from far.core.cues import CueModerator
from far.core.llm_interface import MockLLM
from far.memory.state_store import StateStore
from far.memory.episodic_store import EpisodicStore
from far.memory.semantic_store import SemanticStore
from far.memory.procedural_store import ProceduralStore
from far.retrieval.hybrid_search import HybridSearch
from far.retrieval.reranker import Reranker
from far.context.builder import ContextBuilder

app = FastAPI(title="FAR System API")

# --- Dependency Injection & Initialization ---
# 1. Initialize Memory Stores
state_store = StateStore()
episodic_store = EpisodicStore("events.db") # Persist to disk
semantic_store = SemanticStore("facts.db")  # Persist to disk
procedural_store = ProceduralStore("procedures.json")

# 2. Initialize Retrieval & Support
hybrid_search = HybridSearch(
    state_store=state_store,
    episodic_store=episodic_store,
    semantic_store=semantic_store,
    procedural_store=procedural_store
)
reranker = Reranker()
context_builder = ContextBuilder()
moderator = CueModerator()

# 3. Initialize Orchestrator
orchestrator = FissionOrchestrator(
    moderator=moderator,
    searcher=hybrid_search,
    reranker=reranker,
    builder=context_builder
)

class QueryRequest(BaseModel):
    query: str
    intent: str = "general"
    tenant_id: str = "default"

class IngestRequest(BaseModel):
    content: str
    type: str # fact, event, procedure, state
    metadata: Dict[str, Any] = {}

@app.post("/query")
async def query_endpoint(req: QueryRequest):
    """
    Main entry point for MHCCR queries.
    """
    try:
        result = await orchestrator.run_mhccr(req.query, req.intent)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def ingest_endpoint(req: IngestRequest):
    """
    Ingest endpoint for new memories.
    """
    try:
        if req.type == "fact":
             item = semantic_store.add_fact(req.content, entities=[], relations=req.metadata)
        elif req.type == "event":
             item = episodic_store.add_event(req.content, entities=req.metadata.get("entities", []))
        elif req.type == "procedure":
             item = procedural_store.add_procedure(req.metadata.get("name", "unknown"), steps=req.content.split("\n"))
        elif req.type == "state":
             key = req.metadata.get("key", "unknown")
             item = state_store.upsert(key, req.content, source="api")
        else:
            raise HTTPException(status_code=400, detail="Invalid type")
            
        return {"status": "success", "id": item.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug_trace/{trace_id}")
async def debug_trace(trace_id: str):
    """
    Retrieve logs for a specific fission trace.
    """
    # TODO: Fetch from observability store
    return {"trace_id": trace_id, "status": "not_implemented"}
