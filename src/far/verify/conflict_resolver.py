from typing import List, Optional
from far.core.types import MemoryItem, TrustTier

class ConflictResolver:
    """
    Hard Requirement E: Conflict Resolution.
    Trust Tier > Version > Recency.
    """
    
    def resolve(self, items: List[MemoryItem]) -> Optional[MemoryItem]:
        """
        Returns the single 'winner' item from a list of conflicting items (e.g. same ID/Topic).
        """
        if not items:
            return None
            
        tiers = {
            TrustTier.SYSTEM: 4,
            TrustTier.SIGNED_DOC: 3,
            TrustTier.TOOL: 2,
            TrustTier.USER: 1,
            TrustTier.UNTRUSTED: 0
        }
        
        # Sort by:
        # 1. Trust Tier (Desc)
        # 2. Version (Desc)
        # 3. Timestamp (Desc)
        
        sorted_items = sorted(
            items,
            key=lambda x: (
                tiers.get(x.trust_tier, 0),
                x.version,
                x.timestamp.timestamp()
            ),
            reverse=True
        )
        
        return sorted_items[0]
