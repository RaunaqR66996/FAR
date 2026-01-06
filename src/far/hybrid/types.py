"""Shared type definitions for the hybrid architecture."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class MemoryType(Enum):
    """Supported memory modalities."""
    SEMANTIC = "semantic"
    EPISODIC = "episodic"
    PROCEDURAL = "procedural"
    VISUAL = "visual"


@dataclass(frozen=True)
class MemoryItem:
    """Represents an atomic unit of knowledge."""
    id: str
    type: MemoryType
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[Any] = field(default=None, repr=False)
    timestamp: float = field(default_factory=time.time)


@dataclass(frozen=True)
class EventRecord:
    """Represents a discrete state change in the Immutable Ledger."""
    id: int
    entity_id: str
    event_type: str
    payload: Dict[str, Any]
    timestamp: float
