import json
from typing import Dict, List, Optional
from far.core.types import MemoryItem, MemoryType, TrustTier

class ProceduralStore:
    """
    PROCEDURES (How-to knowledge).
    Stores workflows, DAGs, and SOPs.
    """
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path
        self._procedures: Dict[str, MemoryItem] = {}
        if file_path:
            self._load()

    def _load(self):
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                for pid, pdata in data.items():
                    self._procedures[pid] = MemoryItem.parse_obj(pdata)
        except FileNotFoundError:
            pass

    def add_procedure(self, name: str, steps: List[str], version: int = 1) -> MemoryItem:
        import uuid
        item = MemoryItem(
            id=str(uuid.uuid4()),
            type=MemoryType.PROCEDURE,
            content=f"Procedure: {name}", # Summary content
            source="system_sop",
            trust_tier=TrustTier.SIGNED_DOC,
            version=version,
            metadata={
                "name": name,
                "steps": steps,
                "type": "sequential" # or 'dag'
            }
        )
        self._procedures[item.id] = item
        # In real app, save to file here
        return item

    def get_procedure(self, name: str) -> Optional[MemoryItem]:
        for item in self._procedures.values():
            if item.metadata.get("name") == name:
                return item
        return None

    def search(self, query: str) -> List[MemoryItem]:
        results = []
        for item in self._procedures.values():
            if query.lower() in item.content.lower():
                results.append(item)
        return results
