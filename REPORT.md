# MLOps Assignment: End-to-end ML Pipeline (coding-agent evaluation)

> Fill in after your Nebius slot run. Keep provenance honest — weak resolve rate + clear artifacts beats a mystery number.

## Architecture

- **Orchestrator:** Apache Airflow (`dags/evaluate_agent.py`)
- **Agent:** mini-swe-agent via Nebius Token Factory API
- **Eval:** SWE-bench harness
- **Tracking:** MLflow (params, metrics, artifact path)
- **Artifacts:** `runs/<run-id>/` (config, trajectories, preds, eval logs, metrics, manifest)

```text
prepare_run → run_agent → run_eval → summarize_and_log
```

## How to trigger a run

1. Start MLflow: `./scripts/start_mlflow.sh`
2. Start Airflow: `bash run-airflow-standalone.sh`
3. Open http://localhost:8080 → DAG `evaluate_agent` → Trigger
4. Default params: `split=test`, `subset=verified`, `workers=3`, `task_slice=0:3`

## Completed run

| Field | Value |
|-------|-------|
| run_id | _TBD_ |
| model | _TBD_ |
| task_slice | _TBD_ |
| submitted / resolved | _TBD_ |
| resolve_rate | _TBD_ |
| MLflow run id | _TBD_ |

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

## Rerun by run_id

_TBD — e.g. trigger DAG with same `run_id` param or inspect `runs/<run-id>/config.json`._

## Screenshots

- `screenshots/airflow_dag.png`
- `screenshots/mlflow_runs.png`
- _(optional)_ `screenshots/object_storage_artifacts.png`

## What I'd do with more time

_TBD — be specific (retries, DockerOperator, S3 lifecycle, parallel slices, etc.)._
