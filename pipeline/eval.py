from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


def _run(cmd: list[str], *, cwd: Path, env: dict[str, str]) -> None:
    subprocess.run(cmd, cwd=cwd, env=env, check=True)


from pipeline.env import project_env as _project_env


def run_swebench_eval(run_config: dict[str, Any], preds_path: Path, run_dir: Path) -> Path:
    """Run SWE-bench evaluation and collect logs/reports under run-eval/."""
    project_root = run_dir.parents[1]
    eval_dir = run_dir / "run-eval"
    logs_dir = eval_dir / "logs"
    reports_dir = eval_dir / "reports"
    logs_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    env = _project_env(
        project_root,
        {
            **os.environ,
            "PREDS_PATH": str(preds_path),
            "DATASET_NAME": run_config["dataset_name"],
            "DATASET_SPLIT": run_config["split"],
            "EVAL_WORKERS": str(run_config["workers"]),
            "EVAL_RUN_ID": run_config["eval_run_id"],
        },
    )

    script = project_root / "scripts" / "run_eval.sh"
    _run(["bash", str(script)], cwd=project_root, env=env)

    # Harness writes under <project_root>/logs/ (no --log_dir in this swebench version)
    source_logs = project_root / "logs"
    if source_logs.exists():
        for item in source_logs.iterdir():
            dest = logs_dir / item.name
            if item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

    harness_logs = logs_dir / "run_evaluation"
    _copy_aggregate_reports(harness_logs, reports_dir)
    _copy_run_aggregate_report(project_root, run_config, reports_dir)
    return eval_dir


def _copy_run_aggregate_report(
    project_root: Path, run_config: dict[str, Any], reports_dir: Path
) -> None:
    """SWE-bench writes the summary JSON to project cwd, e.g. nebius__moonshotai__Kimi-K2.6.submit-v2.json."""
    run_id = str(run_config["eval_run_id"])
    model_tag = str(run_config["model"]).replace("/", "__")
    patterns = [f"{model_tag}.{run_id}.json", f"*.{run_id}.json"]
    for pattern in patterns:
        for report in project_root.glob(pattern):
            shutil.copy2(report, reports_dir / report.name)


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
    search_roots: list[Path] = [logs_dir, reports_dir, logs_dir.parent]
    for ancestor in logs_dir.parents:
        if ancestor.name == "runs" and ancestor.parent.exists():
            search_roots.append(ancestor.parent)
        project_logs = ancestor / "logs"
        if project_logs.exists() and project_logs != logs_dir:
            search_roots.append(project_logs)
    candidates: list[Path] = []
    seen_roots: set[Path] = set()
    for root in search_roots:
        if not root.exists() or root in seen_roots:
            continue
        seen_roots.add(root)
        candidates.extend(root.glob("*.json"))
        candidates.extend(root.rglob("*.json"))

    for path in sorted(candidates, key=lambda p: p.stat().st_size, reverse=True):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if "resolved_instances" in data and "submitted_instances" in data:
            return path
    return None
