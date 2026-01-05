from typing import List
from far.core.types import MemoryItem

class Reranker:
    """
    Reranks retrieved candidates based on relevance to the current context.
    """
    
    def rank(self, candidates: List[MemoryItem], query_context: str) -> List[MemoryItem]:
        """
        Scores and sorts candidates.
        """
        # 1. Deduplicate by ID
        unique = {c.id: c for c in candidates}
        items = list(unique.values())
        
        # 2. Score (Mock scoring)
        # Real impl would use Cross-Encoder or bi-encoder similarity
        scored = []
        for item in items:
            score = self._score(item, query_context)
            scored.append((score, item))
            
        # 3. Sort desc
        scored.sort(key=lambda x: x[0], reverse=True)
        
        return [item for _, item in scored]

    def _score(self, item: MemoryItem, context: str) -> float:
        # Simple heuristic: higher trust tier = higher score
        base_score = 0.5
        if item.trust_tier == "SYSTEM":
            base_score += 0.4
        elif item.trust_tier == "SIGNED_DOC":
            base_score += 0.3
        
        # Content overlap match (very naive)
        if any(w in item.content.lower() for w in context.lower().split()):
            base_score += 0.2
            
        return min(base_score, 1.0)
