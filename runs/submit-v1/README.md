# submit-v1 — infrastructure proof run

Completed on Nebius VM (`evaluate_agent` DAG, all four tasks green).

- **Agent:** 3 instances submitted; all `model_patch` fields empty (API key not visible to Airflow on first agent attempt).
- **Eval:** SWE-bench harness ran; 0 instances completed (empty patches).
- **MLflow:** run `ef4cf61973e748dabc23165c22434a40` in experiment `swe-bench-agent-eval`.

Full trajectories and eval logs remain on the VM under `runs/submit-v1/`. This folder in git contains only small reproducibility files (`metrics.json`, `manifest.json`, `config.json`).
