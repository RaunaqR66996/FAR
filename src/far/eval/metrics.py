from typing import Dict, Any

class MetricsCollector:
    """
    Observability & Evaluation.
    """
    
    def calculate_stats(self, trace_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Computes summary metrics for a trace.
        """
        stats = trace_data.get("stats", [])
        if not stats:
            return {}
            
        k_values = [s["k_hat"] for s in stats]
        avg_k = sum(k_values) / len(k_values)
        max_k = max(k_values)
        
        return {
            "avg_k_hat": avg_k,
            "max_k_hat": max_k,
            "total_hops": len(stats),
            "total_evidence": len(trace_data.get("evidence", [])),
            "final_drift": stats[-1]["drift_score"] if stats else 0.0
        }
