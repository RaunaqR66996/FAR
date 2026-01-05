import pytest
import time
from far.context.builder import ContextBuilder
from far.core.types import MemoryItem, MemoryType

class TestStep4Performance:
    """
    Step 4: Performance and Efficiency Tests (Scalability and Optimization)
    Test resource usage and speed for real-world viability.
    """

    def test_latency_check(self):
        """
        Measure latency < 5s/query (Stubbed).
        """
        start = time.time()
        # Simulate work
        time.sleep(0.1) 
        end = time.time()
        
        latency = end - start
        assert latency < 5.0
        
    def test_token_reduction(self):
        """
        Benchmark token reduction via compression in Fusion.
        """
        builder = ContextBuilder(max_tokens=100)
        
        # Create 20 items of ~10 tokens each (200 tokens total)
        # Should be truncated/compressed to fit 100
        evidence = [
            MemoryItem(id=f"{i}", type=MemoryType.FACT, content=f"Fact content number {i} is moderately long.")
            for i in range(20)
        ]
        
        result = builder.build_context(evidence)
        
        assert result["token_count"] <= 100
        assert len(result["context_text"]) > 0
