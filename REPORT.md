# MLOps Assignment: End-to-end ML Pipeline (coding-agent evaluation)

## Architecture

- **Orchestrator:** Apache Airflow (`dags/evaluate_agent.py`) — four TaskFlow tasks
- **Agent:** [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) batch via Nebius Token Factory (`scripts/run_agent.sh`)
- **Evaluation:** [SWE-bench](https://github.com/swe-bench/SWE-bench) harness (`scripts/run_eval.sh`)
- **Tracking:** MLflow — params, metrics, artifact path under `runs/<run-id>/`
- **Shared helpers:** `pipeline/` (`config`, `runner`, `eval`, `manifest`, `mlflow_logging`, `env`)

```text
prepare_run → run_agent → run_eval → summarize_and_log
```

| Task | What it does |
|------|----------------|
| `prepare_run` | Builds `run_config`, creates `runs/<run-id>/config.json` |
| `run_agent` | Runs mini-swe-agent; writes `run-agent/preds.json` + trajectories |
| `run_eval` | Runs SWE-bench Docker eval on `preds.json` |
| `summarize_and_log` | Writes `metrics.json`, `manifest.json`, logs to MLflow |

## How to trigger a run

**On the Nebius VM** (API key + Docker required):

```bash
cd ~/mlops-assignment-e2e-ml-pipeline
source .venv/bin/activate
set -a && source .env && set +a
export PATH="$(pwd)/.venv/bin:$PATH"
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Terminal 1
./scripts/start_mlflow.sh

# Terminal 2
bash run-airflow-standalone.sh
```

1. Port-forward **8080** (Airflow) and **5000** (MLflow) from the VM.
2. Open http://localhost:8080 → DAG **`evaluate_agent`** → **Trigger DAG w/ config**.
3. Example config:

```json
{
  "split": "test",
  "subset": "verified",
  "workers": 3,
  "model": "nebius/moonshotai/Kimi-K2.6",
  "task_slice": "0:3",
  "run_id": "submit-v1",
  "cost_limit": "0"
}
```

**DAG parameters:** `split`, `subset`, `workers`, `model`, `task_slice`, `run_id`, `cost_limit`.

## Completed run — submit-v1

| Field | Value |
|-------|-------|
| run_id | `submit-v1` |
| model | `nebius/moonshotai/Kimi-K2.6` |
| task_slice | `0:3` (3 SWE-bench Verified instances) |
| submitted / resolved | 3 / 0 |
| resolve_rate | 0.0 |
| MLflow run id | `ef4cf61973e748dabc23165c22434a40` |
| MLflow experiment | `swe-bench-agent-eval` |
| MLflow UI | http://127.0.0.1:5000 (on VM; port-forward to view) |

### What happened

All four Airflow tasks completed successfully. The pipeline wrote a full `runs/submit-v1/` tree and logged the run to MLflow.

The agent step finished quickly and produced `preds.json` with the correct instance IDs but **empty `model_patch` fields** for all three instances. SWE-bench eval therefore reported `Instances with empty patches: 3` and `metrics_found: false`. This is an agent/API-configuration issue on the first run (Nebius API key not consistently available to the Airflow worker), not a pipeline-structure failure.

The run still demonstrates: configurable DAG, isolated run directory, eval harness integration, manifest generation, and MLflow tracking — which is what the assignment prioritizes over resolve rate.

### Optional follow-up — submit-v2

Re-trigger with `"run_id": "submit-v2"` after:

1. Confirming `NEBIUS_API_KEY` in `.env`
2. Passing `bash scripts/mini-swe-bench-single.sh` on the VM (non-empty patch)
3. Restarting Airflow from a shell where `docker ps` works without sudo

See `runs/submit-v2/README.md`.

## Artifact layout

```text
runs/<run-id>/
  config.json              # frozen run parameters
  run-agent/
    preds.json             # SWE-bench predictions
    trajectories/          # mini-swe-agent logs + per-instance output
  run-eval/
    logs/                  # SWE-bench harness logs (when instances run)
    reports/               # per-instance report.json copies
  metrics.json             # parsed resolve metrics
  manifest.json            # provenance index (paths, params, timestamps)
```

**Git policy:** commit small files (`config.json`, `metrics.json`, `manifest.json`) per run. Full trajectories stay on the VM (too large for git).

## Rerun by run_id

1. Trigger `evaluate_agent` with a new or existing `run_id` param.
2. Outputs land in `runs/<run-id>/` without overwriting other runs.
3. `config.json` and `manifest.json` in that folder record exact parameters and timestamps.
4. Compare runs in MLflow experiment `swe-bench-agent-eval`.

## Screenshots

- `screenshots/airflow_dag.png` — `evaluate_agent` graph, submit-v1, all tasks green
- `screenshots/mlflow_runs.png` — MLflow experiment with submit-v1 logged

## What I'd do with more time

- **submit-v2** with `.env` loaded into agent tasks (`pipeline/env.py`) for real patches and non-zero metrics
- **DockerOperator** + project `Dockerfile` for stronger execution isolation
- **docker-compose.yaml** for Airflow + MLflow on the VM
- Upload full `runs/<run-id>/` to Nebius Object Storage; set `RUN_ARTIFACT_URI` for MLflow
- Second DAG run with different `task_slice` or `model` to compare in MLflow
