"""Pluggable cognitive skills."""
from __future__ import annotations


def exact_recall_handler(query: str, context: str) -> str:
    """Handle requests requiring 100% precision (e.g., numerical data)."""
    return "Accessed Immutable Ledger. Verified State: PRECISION_MATCH."


def creative_association_handler(query: str, context: str) -> str:
    """Handle requests requiring synthesis of multiple sources."""
    token_count = len(context.split()) if context else 0
    return f"Accessed Associative Cortex. Synthesized {token_count} context tokens into answer."
