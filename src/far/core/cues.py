from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import hashlib

class Cue(BaseModel):
    """
    Represents a 'Neutron' in the fission analogy.
    A signal that triggers retrieval in the memory system.
    """
    content: str = Field(..., description="The raw text content of the cue (e.g., 'Project Alpha')")
    type: str = Field(default="entity", description="Type of cue: entity, constraint, temporal, intent")
    weight: float = Field(default=1.0, description="Importance of this cue (energy level)")
    source_hop: int = Field(default=0, description="The generation/hop number where this cue was created")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context")

    def fingerprint(self) -> str:
        """Returns a stable hash of the cue content for deduplication."""
        return hashlib.md5(self.content.strip().lower().encode()).hexdigest()


class CueModerator:
    """
    Acts as the 'Moderator' in the nuclear reactor.
    Slows down (normalizes) fast neutrons (raw inputs) into thermal neutrons (useful cues).
    """
    
    def __init__(self):
        # In a real system, this would load from a synonym database or ontology
        self.synonym_map = {} 

    def normalize(self, cues: List[Cue]) -> List[Cue]:
        """
        Canonicalizes cues to reduce noise and ensures standard representation.
        """
        normalized = []
        seen_hashes = set()

        for cue in cues:
            # 1. Lowercase and strip
            clean_content = cue.content.strip().lower()
            
            # 2. Synonym mapping (Canonicalization)
            if clean_content in self.synonym_map:
                clean_content = self.synonym_map[clean_content]
            
            # Update the cue content
            # Create a new object to avoid mutating the original if needed, 
            # but here we modify or create new for the list.
            processed_cue = Cue(
                content=clean_content,
                type=cue.type,
                weight=cue.weight,
                source_hop=cue.source_hop,
                metadata=cue.metadata
            )

            # 3. Deduplication
            fp = processed_cue.fingerprint()
            if fp not in seen_hashes:
                seen_hashes.add(fp)
                normalized.append(processed_cue)
        
        return normalized

    def absorb_drift(self, cues: List[Cue], context_embedding: Any = None) -> List[Cue]:
        """
        Acts as a Control Rod.
        Removes cues that have drifted too far from the original intent.
        (Placeholder for vector-based semantic similarity check)
        """
        # TODO: Implement semantic drift check
        return cues
