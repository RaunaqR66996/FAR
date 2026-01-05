from typing import List, Dict, Any
from far.core.types import MemoryItem

class ContextBuilder:
    """
    Hard Requirement: Context Builder (token budgets, dedupe, citations).
    """

    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens

    def build_context(self, evidence: List[MemoryItem]) -> Dict[str, Any]:
        """
        Constructs the final context string and citation map.
        """
        # 1. Deduplication (already done in orchestrator but good to double check)
        unique_evidence = {item.id: item for item in evidence}.values()
        
        # 2. Sort by relevance/score (assumed sorted)
        
        context_parts = []
        citation_map = {}
        current_tokens = 0
        
        for item in unique_evidence:
            # Simple token estimation (4 chars ~= 1 token)
            text_len = len(item.content)
            est_tokens = text_len / 4
            
            if current_tokens + est_tokens > self.max_tokens:
                break
            
            # Format: [ID] (Type) Content
            part = f"[{item.id}] ({item.type}) {item.content}"
            context_parts.append(part)
            citation_map[item.id] = item
            current_tokens += est_tokens
            
        final_context = "\n\n".join(context_parts)
        
        return {
            "context_text": final_context,
            "citations": citation_map,
            "token_count": int(current_tokens)
        }
