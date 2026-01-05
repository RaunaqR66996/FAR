import pytest
from far.verify.coverage_gate import CoverageGate
from far.trust.policy import PolicyEnforcer
from far.core.types import MemoryItem, MemoryType, TrustTier

class TestStep3HallucinationCoverage:
    """
    Step 3: Hallucination and Coverage Tests (Grounding and Completeness)
    Test for zero hallucinations by enforcing gates and verification.
    """

    def test_coverage_gate_blocking(self):
        """
        Input ambiguous queries; check if coverage gate blocks responses without required buckets.
        """
        gate = CoverageGate()
        
        # Intent: "how-to" (Requires PROCEDURE)
        intent = "how-to"
        
        # Evidence with only FACTS (should fail)
        evidence_fail = [
            MemoryItem(id="1", type=MemoryType.FACT, content="foo", source="db")
        ]
        
        report_fail = gate.check(intent, evidence_fail)
        assert report_fail["passed"] is False
        assert MemoryType.PROCEDURE in report_fail["missing"]
        
        # Evidence with PROCEDURE (should pass)
        evidence_pass = [
            MemoryItem(id="2", type=MemoryType.PROCEDURE, content="Step 1...", source="sop")
        ]
        
        report_pass = gate.check(intent, evidence_pass)
        assert report_pass["passed"] is True

    def test_trust_policy_enforcement(self):
        """
        Flag conflicts via trust_tier resolution and enforce policies.
        """
        enforcer = PolicyEnforcer()
        items = [
            MemoryItem(id="1", type=MemoryType.FACT, content="verified", source="sys", trust_tier=TrustTier.SYSTEM),
            MemoryItem(id="2", type=MemoryType.FACT, content="unverified", source="web", trust_tier=TrustTier.UNTRUSTED)
        ]
        
        # Filter for minimum USER level (should exclude UNTRUSTED)
        trusted = enforcer.filter_by_trust(items, min_tier=TrustTier.USER)
        
        assert len(trusted) == 1
        assert trusted[0].content == "verified"

    def test_contradiction_avoidance_logic(self):
        """
        Verify that higher trust tiers override lower ones (Conflict Resolution).
        """
        from far.verify.conflict_resolver import ConflictResolver
        resolver = ConflictResolver()
        
        conflict_items = [
            MemoryItem(id="1", type=MemoryType.FACT, content="Sky is Green", source="user", trust_tier=TrustTier.USER),
            MemoryItem(id="1", type=MemoryType.FACT, content="Sky is Blue", source="sys", trust_tier=TrustTier.SYSTEM)
        ]
        
        winner = resolver.resolve(conflict_items)
        assert winner.content == "Sky is Blue"
