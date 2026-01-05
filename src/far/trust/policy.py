from far.core.types import MemoryItem, TrustTier
from typing import List

class PolicyEnforcer:
    """
    Enforces RBAC, Trust Tiers, and Redaction.
    """
    
    def filter_by_trust(self, items: List[MemoryItem], min_tier: TrustTier) -> List[MemoryItem]:
        """
        Returns only items meeting the minimum trust tier.
        """
        # Define hierarchy
        tiers = {
            TrustTier.UNTRUSTED: 0,
            TrustTier.USER: 1,
            TrustTier.TOOL: 2,
            TrustTier.SIGNED_DOC: 3,
            TrustTier.SYSTEM: 4
        }
        min_val = tiers.get(min_tier, 0)
        
        return [i for i in items if tiers.get(i.trust_tier, 0) >= min_val]

    def redact_pii(self, text: str) -> str:
        """
        Simple PII redaction stub.
        """
        # Stub: replace common PII patterns
        return text.replace("sk-", "sk-***")
