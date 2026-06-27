from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any


def _import_project_mlflow():
    """Airflow runs tasks with its own Python; use the project venv's mlflow."""
    project_root = Path(__file__).resolve().parents[1]
    for site_packages in (project_root / ".venv" / "lib").glob("python*/site-packages"):
        site = str(site_packages)
        if site not in sys.path:
            sys.path.insert(0, site)
    import mlflow

    return mlflow


def log_mlflow_run(
    run_config: dict[str, Any],
    metrics: dict[str, Any],
    artifact_uri: str | None,
    *,
    run_dir: Path | None = None,
) -> str | None:
    """Log params, metrics, and artifact references to MLflow. Returns MLflow run id."""
    mlflow = _import_project_mlflow()

    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
    experiment = os.environ.get("MLFLOW_EXPERIMENT_NAME", "swe-bench-agent-eval")

    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment)

    params = {
        "run_id": run_config["run_id"],
        "subset": run_config["subset"],
        "split": run_config["split"],
        "model": run_config["model"],
        "workers": str(run_config["workers"]),
        "task_slice": run_config["task_slice"],
        "cost_limit": str(run_config["cost_limit"]),
        "dataset_name": run_config["dataset_name"],
    }

    with mlflow.start_run(run_name=run_config["run_id"]) as active_run:
        mlflow.log_params(params)

        for key, value in metrics.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                mlflow.log_metric(key, float(value))

        if artifact_uri:
            mlflow.log_param("artifact_uri", artifact_uri)
        elif run_dir is not None:
            mlflow.log_artifacts(str(run_dir), artifact_path=run_config["run_id"])

        return active_run.info.run_id
