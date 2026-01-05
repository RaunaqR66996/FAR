from typing import List, Dict
from far.core.types import MemoryItem, MemoryType

class CoverageGate:
    """
    Hard Requirement B: Coverage Gate.
    Enforces that required buckets are present before answering.
    """
    
    REQUIRED_BUCKETS = {
        "factual": [MemoryType.FACT],
        "history": [MemoryType.EVENT],
        "how-to": [MemoryType.PROCEDURE],
        "status": [MemoryType.STATE]
    }

    def check(self, intent: str, evidence: List[MemoryItem]) -> Dict[str, bool]:
        """
        Returns a check report. 
        If required buckets are missing, report false.
        """
        required = self.REQUIRED_BUCKETS.get(intent, [])
        if not required:
            return {"passed": True}
        
        present_types = {item.type for item in evidence}
        missing = [t for t in required if t not in present_types]
        
        return {
            "passed": len(missing) == 0,
            "missing": missing,
            "present": list(present_types)
        }
