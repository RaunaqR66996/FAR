import logging
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from far.core.cues import Cue, CueModerator
from far.core.types import MemoryItem, MemoryType
from far.retrieval.hybrid_search import HybridSearch
from far.retrieval.reranker import Reranker
from far.context.builder import ContextBuilder

from far.verify.coverage_gate import CoverageGate
from far.core.llm_interface import LLMProvider, MockLLM

logger = logging.getLogger(__name__)

class FissionOrchestrator:
    """
    Orchestrates the Multi-Hop Cue Chain Reaction (MHCCR).
    Manages the Fission Generation Loop (Requirement C).
    """

    def __init__(
        self,
        moderator: CueModerator,
        searcher: HybridSearch = None,
        reranker: Reranker = None,
        builder: ContextBuilder = None,
        llm: LLMProvider = None,
        max_hops: int = 3,
        target_k: float = 1.0,
        drift_threshold: float = 1.5
    ):
        self.moderator = moderator
        self.searcher = searcher
        self.reranker = reranker or Reranker()
        self.builder = builder or ContextBuilder()
        self.llm = llm or MockLLM()
        self.coverage_gate = CoverageGate() # Initialize Gate
        self.max_hops = max_hops
        self.target_k = target_k  # Criticality target (k_hat)
        self.drift_threshold = drift_threshold

    async def run_mhccr(self, initial_query: str, intent: str) -> Dict[str, Any]:
        """
        Executes the fission chain reaction.
        """
        trace_id = str(uuid.uuid4())
        logger.info(f"Starting MHCCR trace={trace_id} query='{initial_query}'")

        # 0. Initial Cue Extraction (Neutron Source)
        # Use LLM to extract initial cues from query
        raw_cues = await self.llm.extract_cues(initial_query)
        # Fallback if LLM extraction fails/returns empty on short query
        if not raw_cues:
            raw_cues = [Cue(content=initial_query, type="intent", source_hop=0)]
            
        current_cues = self.moderator.normalize(raw_cues)

        all_evidence: Dict[str, MemoryItem] = {}
        generation_stats = []

        for g in range(1, self.max_hops + 1):
            logger.info(f"--- Generation G={g} | Input Cues: {len(current_cues)} ---")
            
            # C.1 Route & Retrieve
            if self.searcher:
                candidates = self.searcher.search(current_cues)
            else:
                candidates = self._mock_retrieve(current_cues, intent)

            # C.2 Rerank
            # Prioritize evidence based on relevance to the original query/intent
            top_evidence = self.reranker.rank(candidates, initial_query)[:5]

            # Store evidence
            new_evidence_count = 0
            for item in top_evidence:
                if item.id not in all_evidence:
                    all_evidence[item.id] = item
                    new_evidence_count += 1
            
            # C.3 Fission: Derive new cues C_{g+1} from E_g
            # Use LLM to extract cues from the retrieved evidence content
            next_cues = []
            for item in top_evidence:
                extracted = await self.llm.extract_cues(item.content)
                for c in extracted:
                    c.source_hop = g
                    next_cues.append(c)
            
            next_cues = self.moderator.normalize(next_cues)
            
            # C.4 Control & k_hat calculation
            num_input = max(len(current_cues), 1)
            num_output = len(next_cues)
            k_hat = num_output / num_input
            
            drift_score = self._calculate_drift(next_cues, initial_query)

            stats = {
                "hop": g,
                "input_cues": len(current_cues),
                "retrieved": len(candidates),
                "kept_evidence": len(top_evidence),
                "new_cues": num_output,
                "k_hat": k_hat,
                "drift_score": drift_score
            }
            generation_stats.append(stats)
            logger.info(f"Stats: {stats}")

            # Control Rods
            if drift_score > self.drift_threshold:
                logger.warning(f"Drift detected ({drift_score}), pruning cues.")
                pass

            if k_hat > 2.0:
                 logger.warning(f"k_hat high ({k_hat:.2f}), suppressing branching.")
                 next_cues = next_cues[:num_input + 2]

            # C.5 Stop Conditions
            if new_evidence_count == 0:
                logger.info("No new evidence found. Stopping fission.")
                break
            
            if not next_cues:
                logger.info("No further cues generated. Stopping.")
                break

            current_cues = next_cues

        # D. Verification (Coverage Gate)
        evidence_list = list(all_evidence.values())
        gate_result = self.coverage_gate.check(intent, evidence_list)
        
        context_result = self.builder.build_context(evidence_list)
        
        if not gate_result["passed"]:
            missing = ", ".join(gate_result["missing"])
            summary = f"INSUFFICIENT EVIDENCE. Missing required memory types for '{intent}': {missing}. System cannot proceed safely."
            logger.warning(summary)
        else:
            # E. Energy Extraction (Consolidation/Summary)
            summary = await self.llm.summarize(context_result["context_text"], initial_query)

        return {
            "trace_id": trace_id,
            "summary": summary,
            "gate_result": gate_result,
            "context": context_result["context_text"],
            "evidence": [item.dict() for item in evidence_list],
            "stats": generation_stats,
            "final_k_hat": generation_stats[-1]["k_hat"] if generation_stats else 0.0
        }

    def _mock_retrieve(self, cues: List[Cue], intent: str) -> List[MemoryItem]:
        """Stub for retrieval logic"""
        return []

    def _calculate_drift(self, cues: List[Cue], original_query: str) -> float:
        """
        Calculates 'Drift Score' (inverse relevance).
        Uses Jaccard similarity between cue content and original query.
        """
        if not cues:
            return 0.0 # No output, no drift (but also no energy)
            
        # Normalize query terms
        query_terms = set(original_query.lower().split())
        
        # Aggregate cue terms
        cue_text = " ".join([c.content for c in cues]).lower()
        cue_terms = set(cue_text.split())
        
        # Calculate Jaccard Similarity
        intersection = query_terms.intersection(cue_terms)
        union = query_terms.union(cue_terms)
        
        if not union:
            return 1.0 # Should not happen defined above
            
        similarity = len(intersection) / len(union)
        
        # Drift is inverse of similarity. 
        # High Similarity (1.0) -> Low Drift (0.0)
        # Low Similarity (0.0) -> High Drift (1.0+)
        # We scale it up to make thresholding easier (e.g. > 1.5 is bad)
        
        # Avoid div by zero
        drift = 1.0 / max(similarity, 0.01)
        
        # Normalize: if drift > threshold, it's "critical"
        return drift
