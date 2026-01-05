from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime

class MemoryType(str, Enum):
    FACT = "FACT"
    EVENT = "EVENT"
    PROCEDURE = "PROCEDURE"
    STATE = "STATE"

class TrustTier(str, Enum):
    SYSTEM = "SYSTEM"       # Hard-coded rules, axiomatic truths
    SIGNED_DOC = "SIGNED_DOC" # e.g., verified contracts, specs
    TOOL = "TOOL"           # Output from reliable tools
    USER = "USER"           # Direct user input
    UNTRUSTED = "UNTRUSTED" # Unverified external web content

class MemoryItem(BaseModel):
    """
    Hard Requirement A: Memory Item Schema.
    Universal unit of memory in FAR.
    """
    id: str = Field(..., description="Unique identifier")
    type: MemoryType = Field(..., description="Bucket: FACT, EVENT, PROCEDURE, STATE")
    tenant_id: str = Field(default="default", description="Multi-tenancy isolation key")
    entity_ids: List[str] = Field(default_factory=list, description="Linked entities")
    
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Creation time")
    as_of: Optional[datetime] = Field(None, description="Valid as-of time (for state/facts)")
    valid_from: Optional[datetime] = Field(None, description="Validity start")
    valid_to: Optional[datetime] = Field(None, description="Validity end")
    version: int = Field(default=1, description="Versioning for conflict resolution")
    
    source: str = Field(..., description="Origin of the information")
    trust_tier: TrustTier = Field(default=TrustTier.USER, description="Confidence level")
    
    content: str = Field(..., description="The actual memory content")
    citations: List[str] = Field(default_factory=list, description="IDs of backing evidence")
    
    hash: Optional[str] = Field(None, description="Content hash for integrity")
    embedding: Optional[List[float]] = Field(None, description="Vector representation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary extra data")
