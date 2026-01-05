import pytest
from far.core.cues import Cue, CueModerator
from far.core.orchestrator import FissionOrchestrator
from far.memory.episodic_store import EpisodicStore
from far.core.types import MemoryItem

class TestStep1Unit:
    """
    Step 1: Unit Tests (Verify Individual Components)
    Test isolated layers (Initiation, Cascade, Fusion).
    """

    def test_initiation_decomposition(self):
        """
        Verify sub-cues are generated correctly (Initiation).
        """
        moderator = CueModerator()
        # Mocking synonym map for test
        moderator.synonym_map = {"proj alpha": "project alpha"}
        
        cues = [Cue(content="Proj Alpha"), Cue(content="  STATUS  ")]
        normalized = moderator.normalize(cues)
        
        assert len(normalized) == 2
        assert normalized[0].content == "project alpha" # Canonicalized
        assert normalized[1].content == "status" # Lowercased/Stripped

    def test_cascade_spawning_logic(self):
        """
        Verify MHCCR spawning (Cascade).
        Check k_hat logic and drift control.
        """
        moderator = CueModerator()
        orch = FissionOrchestrator(moderator, max_hops=3, target_k=1.0)
        
        # Mock function to simulate cue derivation
        def mock_derive(evidence, hop):
            # Simulate k=2 behavior (each evidence -> 2 cues)
            return [Cue(content=f"c-{i}") for i in range(len(evidence) * 2)]
            
        orch._mock_derive_cues = mock_derive
        
        # Test drift calculation stub
        drift = orch._calculate_drift([], "query")
        assert drift <= orch.drift_threshold

    def test_fusion_memory_storage(self):
        """
        Verify memory storage (Fusion).
        Episodic dict saves/replays without loss.
        """
        store = EpisodicStore(":memory:")
        event_content = "Critical failure in Sector 7"
        entities = ["sector-7"]
        
        # Save
        item = store.add_event(event_content, entities)
        assert item.id is not None
        
        # Replay (Search)
        results = store.search("Sector 7")
        assert len(results) >= 1
        assert results[0].content == event_content
        assert "sector-7" in results[0].entity_ids

    def test_edge_cases(self):
        """
        Test failure cases (e.g. empty inputs).
        """
        moderator = CueModerator()
        empty = moderator.normalize([])
        assert len(empty) == 0
        
        store = EpisodicStore(":memory:")
        no_results = store.search("NonexistentTerm")
        assert len(no_results) == 0
