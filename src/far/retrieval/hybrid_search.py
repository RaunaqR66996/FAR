from typing import List, Dict, Any, TYPE_CHECKING
from far.core.types import MemoryItem, MemoryType
from far.core.cues import Cue

if TYPE_CHECKING:
    from far.memory.state_store import StateStore
    from far.memory.episodic_store import EpisodicStore
    from far.memory.semantic_store import SemanticStore
    from far.memory.procedural_store import ProceduralStore

class HybridSearch:
    """
    Retrieval Layer.
    Combines Keyword (BM25) + Vector Search + Metadata Filtering.
    """
    
    def __init__(
        self,
        state_store: 'StateStore' = None,
        episodic_store: 'EpisodicStore' = None,
        semantic_store: 'SemanticStore' = None,
        procedural_store: 'ProceduralStore' = None,
        vector_index_stub: Any = None
    ):
        self.state_store = state_store
        self.episodic_store = episodic_store
        self.semantic_store = semantic_store
        self.procedural_store = procedural_store
        self.vector_index = vector_index_stub

    def search(self, cues: List[Cue], filters: Dict[str, Any] = None) -> List[MemoryItem]:
        """
        Executed search across all active memory stores based on cues.
        """
        results = []
        
        for cue in cues:
            # 1. Facts (Semantic)
            if self.semantic_store:
                facts = self.semantic_store.search(cue.content)
                results.extend(facts)
            
            # 2. Events (Episodic)
            if self.episodic_store:
                events = self.episodic_store.search(cue.content)
                results.extend(events)
                
            # 3. Procedures
            if self.procedural_store:
                procs = self.procedural_store.search(cue.content)
                results.extend(procs)
            
            # 4. State
            if self.state_store:
                # Direct lookup if cue looks like a variable, or broad search
                states = self.state_store.search(cue.content)
                results.extend(states)

        # Basic deduplication by ID
        unique_results = {item.id: item for item in results}
        return list(unique_results.values())
