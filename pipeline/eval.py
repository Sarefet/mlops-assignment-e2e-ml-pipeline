from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


def _run(cmd: list[str], *, cwd: Path, env: dict[str, str]) -> None:
    subprocess.run(cmd, cwd=cwd, env=env, check=True)


def run_swebench_eval(run_config: dict[str, Any], preds_path: Path, run_dir: Path) -> Path:
    """Run SWE-bench evaluation and collect logs/reports under run-eval/."""
    project_root = run_dir.parents[1]
    eval_dir = run_dir / "run-eval"
    logs_dir = eval_dir / "logs"
    reports_dir = eval_dir / "reports"
    logs_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    env = {
        **os.environ,
        "PREDS_PATH": str(preds_path),
        "DATASET_NAME": run_config["dataset_name"],
        "EVAL_WORKERS": str(run_config["workers"]),
        "EVAL_RUN_ID": run_config["eval_run_id"],
        "EVAL_LOG_DIR": str(logs_dir),
    }

    script = project_root / "scripts" / "run_eval.sh"
    _run(["bash", str(script)], cwd=project_root, env=env)

    # SWE-bench writes under logs/run_evaluation/<run_id>/...
    harness_logs = logs_dir / "run_evaluation"
    if not harness_logs.exists():
        # Fallback: harness may write to project logs/
        fallback = project_root / "logs" / "run_evaluation"
        if fallback.exists():
            if harness_logs.exists():
                shutil.rmtree(harness_logs)
            shutil.copytree(fallback, harness_logs)

    _copy_aggregate_reports(harness_logs, reports_dir)
    return eval_dir


def _copy_aggregate_reports(harness_logs: Path, reports_dir: Path) -> None:
    if not harness_logs.exists():
        return
    for path in harness_logs.rglob("report.json"):
        rel = path.relative_to(harness_logs)
        target = reports_dir / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def collect_metrics(eval_dir: Path) -> dict[str, Any]:
    """Parse SWE-bench aggregate report JSON into flat metrics."""
    reports_dir = eval_dir / "reports"
    logs_dir = eval_dir / "logs"

    aggregate = _find_aggregate_report(logs_dir, reports_dir)
    if aggregate is None:
        return {"metrics_found": False}

    data = json.loads(aggregate.read_text(encoding="utf-8"))
    submitted = int(data.get("submitted_instances", 0))
    resolved = int(data.get("resolved_instances", 0))
    completed = int(data.get("completed_instances", 0))
    resolve_rate = (resolved / submitted) if submitted else 0.0

    return {
        "metrics_found": True,
        "aggregate_report": str(aggregate.relative_to(eval_dir.parent)),
        "submitted_instances": submitted,
        "completed_instances": completed,
        "resolved_instances": resolved,
        "unresolved_instances": int(data.get("unresolved_instances", 0)),
        "error_instances": int(data.get("error_instances", 0)),
        "resolve_rate": resolve_rate,
    }


def _find_aggregate_report(logs_dir: Path, reports_dir: Path) -> Path | None:
    search_roots = [logs_dir, reports_dir, logs_dir.parent]
    candidates: list[Path] = []
    for root in search_roots:
        if not root.exists():
            continue
        candidates.extend(root.glob("*.json"))
        candidates.extend(root.rglob("*.test.json"))

    for path in sorted(candidates, key=lambda p: p.stat().st_size, reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if "resolved_instances" in data and "submitted_instances" in data:
            return path
    return None
