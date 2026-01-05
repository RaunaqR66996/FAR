from abc import ABC, abstractmethod
from typing import List
from far.core.cues import Cue

class LLMProvider(ABC):
    """
    Abstract interface for LLM operations.
    Allows swapping between Mock, OpenAI, Anthropic, or Local LLMs.
    """
    
    @abstractmethod
    async def extract_cues(self, text: str, context: str = "") -> List[Cue]:
        """
        Extracts memory cues (entities, intents) from text.
        """
        pass

    @abstractmethod
    async def summarize(self, text: str, query: str) -> str:
        """
        Generates a concise summary answer.
        """
        pass

class MockLLM(LLMProvider):
    """
    Rule-based mock for testing without API keys.
    """
    async def extract_cues(self, text: str, context: str = "") -> List[Cue]:
        cues = []
        # Heuristic: Extract capitalized words as entities
        words = text.replace(".", "").split()
        for w in words:
            if w[0].isupper() and len(w) > 2:
                cues.append(Cue(content=w, type="entity"))
        
        # Heuristic: Extract "status" or "plan" keywords
        lower = text.lower()
        if "status" in lower:
            cues.append(Cue(content="status", type="intent"))
        if "plan" in lower:
            cues.append(Cue(content="plan", type="intent"))
            
        return cues

    async def summarize(self, text: str, query: str) -> str:
        return f"Mock Summary: Based on {len(text)} chars of evidence, the answer to '{query}' is [Data Found]."
