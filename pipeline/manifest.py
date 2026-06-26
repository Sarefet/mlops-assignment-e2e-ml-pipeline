from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def write_manifest(
    run_dir: Path,
    *,
    metrics: dict[str, Any],
    artifact_uri: str | None = None,
) -> Path:
    """Write manifest.json pointing at the important run artifacts."""
    config_path = run_dir / "config.json"
    run_config = json.loads(config_path.read_text(encoding="utf-8"))

    manifest = {
        "run_id": run_config["run_id"],
        "created_at": run_config.get("created_at"),
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "config": str(config_path.relative_to(run_dir)),
        "paths": {
            "run_agent": "run-agent/",
            "preds_json": "run-agent/preds.json",
            "trajectories": "run-agent/trajectories/",
            "run_eval": "run-eval/",
            "eval_logs": "run-eval/logs/",
            "eval_reports": "run-eval/reports/",
            "metrics_json": "metrics.json",
        },
        "parameters": {
            k: run_config[k]
            for k in (
                "subset",
                "split",
                "model",
                "workers",
                "task_slice",
                "cost_limit",
                "dataset_name",
            )
            if k in run_config
        },
        "metrics_summary": metrics,
        "artifact_uri": artifact_uri,
    }

    manifest_path = run_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest_path
