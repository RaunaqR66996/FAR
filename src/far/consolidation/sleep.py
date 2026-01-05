from typing import List
from far.core.types import MemoryItem, MemoryType
from far.memory.episodic_store import EpisodicStore
from far.memory.semantic_store import SemanticStore

class ConsolidationService:
    """
    Consolidation Rules (Sleep).
    Promote Episodic -> Semantic/Procedural.
    prevent "baking in" wrong summaries.
    """
    
    def __init__(self, episodic: EpisodicStore, semantic: SemanticStore):
        self.episodic = episodic
        self.semantic = semantic

    def sleep_cycle(self):
        """
        Runs offline consolidation.
        """
        # 1. Fetch recent unconsolidated events
        # events = self.episodic.get_unconsolidated()
        pass
        
    def promote_to_fact(self, event_ids: List[str], fact_content: str):
        """
        Creates a new fact derived from multiple events.
        """
        # Safeguard: Fact must be supported by > N events or high trust source
        if len(event_ids) < 3:
            # Log warning: insufficient evidence for promotion
            return
            
        self.semantic.add_fact(
            content=fact_content,
            entities=[], # Extract entities
            relations={"derived_from": event_ids}
        )
