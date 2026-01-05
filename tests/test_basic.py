import sys
import os
import pytest
import asyncio

# Ensure src is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from far.core.cues import Cue, CueModerator
from far.core.orchestrator import FissionOrchestrator
from far.memory.state_store import StateStore
from far.memory.episodic_store import EpisodicStore
from far.memory.semantic_store import SemanticStore
from far.memory.procedural_store import ProceduralStore

def test_cue_moderator():
    mod = CueModerator()
    cues = [
        Cue(content=" TEST "),
        Cue(content="test"),
        Cue(content="unique")
    ]
    normalized = mod.normalize(cues)
    assert len(normalized) == 2
    assert normalized[0].content == "test"
    assert normalized[1].content == "unique"

def test_state_store():
    store = StateStore()
    store.upsert("status", "running", "sytem")
    item = store.get("status")
    assert item is not None
    assert item.content == "running"
    assert item.type == "STATE"

def test_episodic_store():
    store = EpisodicStore(":memory:")
    store.add_event("User logged in", ["user_1"])
    results = store.search("logged")
    assert len(results) == 1
    assert results[0].content == "User logged in"

def test_semantic_store():
    store = SemanticStore(":memory:")
    store.add_fact("The sky is blue", ["sky"], {"color": "blue"})
    results = store.search("sky")
    assert len(results) >= 1
    assert results[0].content == "The sky is blue"

def test_procedural_store():
    store = ProceduralStore()
    store.add_procedure("Deploy", ["Build", "Test", "Push"])
    item = store.get_procedure("Deploy")
    assert item is not None
    assert "Build" in item.metadata["steps"]

@pytest.mark.asyncio
async def test_orchestrator():
    mod = CueModerator()
    orch = FissionOrchestrator(mod)
    result = await orch.run_mhccr("project alpha status", "status")
    
    assert result is not None
    assert "summary" in result
    assert "trace_id" in result
    assert len(result["evidence"]) > 0
    # Check stats for mock values
    stats = result["stats"]
    assert len(stats) > 0
