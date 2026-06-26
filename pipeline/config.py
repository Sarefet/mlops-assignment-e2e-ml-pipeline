from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any


DEFAULT_MODEL = "nebius/moonshotai/Kimi-K2.6"
DEFAULT_SUBSET = "verified"
DEFAULT_SPLIT = "test"
DEFAULT_WORKERS = 3
DEFAULT_TASK_SLICE = "0:3"
DEFAULT_COST_LIMIT = "0"


def _dataset_name(subset: str) -> str:
    if subset == "verified":
        return "princeton-nlp/SWE-bench_Verified"
    if subset == "lite":
        return "princeton-nlp/SWE-bench_Lite"
    return f"princeton-nlp/SWE-bench_{subset}"


def build_run_config(params: dict[str, Any]) -> dict[str, Any]:
    """Normalize Airflow params into a durable run configuration."""
    run_id = params.get("run_id") or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    subset = str(params.get("subset", DEFAULT_SUBSET))
    split = str(params.get("split", DEFAULT_SPLIT))
    model = str(params.get("model", DEFAULT_MODEL))
    workers = int(params.get("workers", DEFAULT_WORKERS))
    task_slice = str(params.get("task_slice", DEFAULT_TASK_SLICE))
    cost_limit = str(params.get("cost_limit", DEFAULT_COST_LIMIT))

    mini_swe_config = os.environ.get(
        "MINI_SWE_CONFIG",
        str(params.get("mini_swe_config", "../mini-swe-agent/src/minisweagent/config/benchmarks/swebench.yaml")),
    )

    return {
        "run_id": run_id,
        "subset": subset,
        "split": split,
        "model": model,
        "workers": workers,
        "task_slice": task_slice,
        "cost_limit": cost_limit,
        "dataset_name": _dataset_name(subset),
        "mini_swe_config": mini_swe_config,
        "eval_run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
