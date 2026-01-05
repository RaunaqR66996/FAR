# Fission-Augmented Reasoning (FAR)

FAR is a production-grade memory architecture that models reasoning as a controlled chain-reaction (fission) process. It replaces flat RAG with a Multi-Hop Cue Chain Reaction (MHCCR) mechanism governed by a stability factor ($k_{hat}$) to ensure human-like recall without hallucinations.

## Core Concept: Fission Infusion

We analogize information propagation to nuclear fission to strictly control context expansion:

*   **Neutron**: A memory **Cue** (entity, constraint, temporal, intent).
*   **Fission Event**: One **MHCCR Hop** (Retrieve $\rightarrow$ Rerank $\rightarrow$ Verify).
*   **Neutrons Emitted**: Derived sub-cues for the next hop.
*   **Radiation**: Irrelevant or noisy cues (filtered out).
*   **Energy**: Compressed insight summary produced from evidence.
*   **$k_{hat}$ (Control Factor)**: The cue multiplication factor.
    *   $k \approx 1$: Stable, human-like recall.
    *   $k < 1$: Fading signal, insufficient grounding.
    *   $k > 1$: Runaway drift, hallucination risk.
*   **Control Rods**: Mechanisms to suppress $k$ (strict budgets, branching caps, drift guards).
*   **Moderator**: Cue normalization service (canonicalization, synonym mapping).

## Architecture

FAR utilizes a 4-Layer Memory System to guarantee coverage of human cognition aspects:

1.  **FACTS (Semantic Layer)**: Immutable truths, entities, and relationships.
2.  **EVENTS (Episodic Layer)**: Time-ordered history of what happened.
3.  **PROCEDURES (Procedural Layer)**: How-to knowledge, workflows, and SOPs.
4.  **CURRENT STATE (State Layer)**: Live operational status and working memory.

## MHCCR Algorithm (Fission Generation Loop)

For a maximum of $G$ generations (hops):

1.  **Extract & Moderate**: Generate cues $C_g$ from the query or previous results.
2.  **Route**: Send cues to appropriate memory layers based on intent.
3.  **Retrieve**: Fetch candidates with strict metadata filters.
4.  **Rerank**: Select top evidence $E_g$.
5.  **Fission**: Derive new cues $C_{g+1}$ from $E_g$.
6.  **Control**: Calculate $k_{hat}$ and apply control rods (cap branching, prune drift).
7.  **Terminate**: Stop if coverage is satisfied, budget is hit, or drift is detected.

## Trust & Safety

*   **Coverage Gates**: Enforce required memory types before generation (e.g., "How-to" query *must* have PROCEDURAL evidence).
*   **Conflict Resolution**: Resolves data conflicts via `Trust Tier > Version > Recency`.
*   **Citations**: All assertions must be backed by retrieved evidence IDs.
*   **LLM Interface**: The system uses an abstract `LLMProvider`. By default, it runs with `MockLLM` (rule-based) for testing. You can implement `OpenAILLM` or `LocalLLM` in `src/far/core/llm_interface.py` to connect real models.

## Quick Start

### Using Docker (Recommended)

The easiest way to run the full FAR system (API + UI) is via Docker Compose:

```bash
docker-compose up --build
```

-   **Web UI**: Open [http://localhost:7860](http://localhost:7860) to visualize fission traces and ingest memory.
-   **API Docs**: Open [http://localhost:8000/docs](http://localhost:8000/docs) to explore the Swagger documentation.

### Manual Installation

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run API Server**:
    ```bash
    uvicorn far.api.server:app --reload
    ```
3.  **Run UI**:
    ```bash
    python src/far/ui/app.py
    ```

### Running Tests

We have a comprehensive testing pipeline (Unit, Integration, Performance, Stress):

```bash
pytest tests/
```
