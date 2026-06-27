# MLOps Assignment: End-to-end ML Pipeline (coding-agent evaluation)

## Architecture

- **Orchestrator:** Apache Airflow (`dags/evaluate_agent.py`) — four TaskFlow tasks
- **Agent:** [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) batch via Nebius Token Factory (`scripts/run_agent.sh`)
- **Evaluation:** [SWE-bench](https://github.com/swe-bench/SWE-bench) harness (`scripts/run_eval.sh`)
- **Tracking:** MLflow — params, metrics, artifacts under `runs/<run-id>/`
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
  "run_id": "submit-v2",
  "cost_limit": "0"
}
```

**DAG parameters:** `split`, `subset`, `workers`, `model`, `task_slice`, `run_id`, `cost_limit`.

### Docker Compose (production-style)

Alternative to `run-airflow-standalone.sh` + `start_mlflow.sh`:

```bash
cp .env.example .env          # set NEBIUS_API_KEY
chmod +x scripts/start_compose.sh
./scripts/start_compose.sh    # or: docker compose up -d --build
```

- **Airflow:** http://localhost:8080 (`admin` / `admin`)
- **MLflow:** http://localhost:5000
- Airflow container mounts the repo, `runs/`, host Docker socket (for SWE-bench), and `../mini-swe-agent` for agent config.
- Stop: `docker compose down`

See `docker-compose.yaml`, `Dockerfile.airflow`, `Dockerfile.mlflow`.

## Completed run — submit-v2 (primary)

| Field | Value |
|-------|-------|
| run_id | `submit-v2` |
| model | `nebius/moonshotai/Kimi-K2.6` |
| task_slice | `0:3` (astropy-12907, astropy-13033, astropy-13236) |
| submitted / resolved | 3 / 2 |
| resolve_rate | 0.667 (66.7%) |
| MLflow run id | `f962323f32974cbba1dfd8fdc9886408` |
| MLflow experiment | `swe-bench-agent-eval` |
| Airflow duration | ~7 min (run_agent ~6 min, run_eval ~2 min) |

### What happened

All four Airflow tasks completed successfully. The agent produced real patches; SWE-bench Docker eval ran on all three instances. Two instances resolved, one unresolved, zero errors. Metrics and artifacts were logged to MLflow.

Fixes applied for reproducibility: `pipeline/env.py` loads `NEBIUS_API_KEY` from `.env` into Airflow tasks; `pipeline/mlflow_logging.py` uses the project venv's MLflow; eval aggregate report is collected from the project root.

## Earlier run — submit-v1 (infrastructure proof)

| Field | Value |
|-------|-------|
| run_id | `submit-v1` |
| submitted / resolved | 3 / 0 |
| resolve_rate | 0.0 |
| MLflow run id | `ef4cf61973e748dabc23165c22434a40` |

First DAG run before API key was consistently available to Airflow — empty patches, `metrics_found: false`. Kept as evidence of pipeline wiring and retry/debug workflow.

## Artifact layout

```text
runs/<run-id>/
  config.json
  run-agent/preds.json
  run-agent/trajectories/
  run-eval/logs/
  run-eval/reports/
  metrics.json
  manifest.json
```

**Git policy:** small JSON files per run in git; full trajectories on VM only.

## Rerun by run_id

1. Trigger `evaluate_agent` with a new or existing `run_id` param.
2. Outputs land in `runs/<run-id>/` without overwriting other runs.
3. Compare runs in MLflow experiment `swe-bench-agent-eval`.

## Screenshots

| File | Description |
|------|-------------|
| `screenshots/airflow_dag_v2.png` | Airflow — submit-v2, all tasks success |
| `screenshots/mlflow_runs_v2.png` | MLflow — submit-v2 overview (params + metrics) |
| `screenshots/mlflow_metrics_v2.png` | MLflow — submit-v2 metric charts |
| `screenshots/mlflow_artifacts_v2.png` | MLflow — submit-v2 artifacts tree |
| `screenshots/airflow_dag.png` | Airflow — submit-v1 run |
| `screenshots/mlflow_runs.png` | MLflow — submit-v1 (params only) |

## What I'd do with more time

- **DockerOperator** tasks using the project `Dockerfile` instead of subprocess calls
- Upload full `runs/<run-id>/` to Nebius Object Storage; set `RUN_ARTIFACT_URI`
- Additional runs with different `task_slice` or `model` for MLflow comparison
