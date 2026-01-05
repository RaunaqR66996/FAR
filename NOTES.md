# Environment & Setup Notes

## Prerequisites

The system requires **Python 3.9+** and `pip` to be installed and available in your system PATH.

During the setup process, we detected that `python` might not be immediately available in the current shell. Please ensure you have Python installed.


## Deployment (Docker)

To run the full system (API + UI) using Docker:

```bash
docker-compose up --build
```

Access the **UI** at: `http://localhost:7860`
Access the **API** at: `http://localhost:8000/docs`

## Local Development Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Fission Simulation

To visualize the stability control ($k_{hat}$) and see how the "Control Rods" work:

```bash
python src/far/eval/fission_sim.py
```

This will run scenarios for $k=0.8$, $1.0$, and $1.2$ and print the neutron population sequences.

## Running Tests

To verify the core logic and memory layers (Unit):

```bash
pytest tests/
```

### MVP Testing Pipeline
We have implemented the full testing suite as requested:

1.  **Unit Tests Instructions**: `pytest tests/step1_unit.py` (Verify Initiation, Cascade, Fusion)
2.  **Integration Tests**: `pytest tests/step2_integration.py` (End-to-End Flow)
3.  **Hallucination & Coverage**: `pytest tests/step3_coverage.py` (Gates & Trust)
4.  **Performance**: `pytest tests/step4_performance.py` (Latency & Token usage)
5.  **Load/Stress**: `pytest tests/step5_stress.py` (Concurrency & Drift)
6.  **User Validation**: `python tests/step6_validation.py` (Simulation of A/B testing)

## Running the API Server

To start the FAR system API:

```bash
uvicorn far.api.server:app --reload
```
