#!/usr/bin/env bash
# Smoke-test metrics/manifest parsing using the starter sample/ folder (no API calls).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

uv run python - <<'PY'
import json
import shutil
from pathlib import Path

from pipeline.config import build_run_config
from pipeline.eval import collect_metrics
from pipeline.manifest import write_manifest
from pipeline.paths import prepare_run_dir

run_config = build_run_config({"run_id": "sample-smoke", "task_slice": "0:3"})
run_dir = prepare_run_dir(run_config)

agent_dir = run_dir / "run-agent"
shutil.copytree("sample/trajectories", agent_dir / "trajectories", dirs_exist_ok=True)
shutil.copy2("sample/trajectories/preds.json", agent_dir / "preds.json")

eval_dir = run_dir / "run-eval"
shutil.copytree("sample/logs", eval_dir / "logs", dirs_exist_ok=True)
shutil.copytree("sample/logs/run_evaluation", eval_dir / "reports", dirs_exist_ok=True)
shutil.copy2("sample/nebius__moonshotai__Kimi-K2.6.test.json", eval_dir / "reports" / "aggregate.json")

metrics = collect_metrics(eval_dir)
(run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
write_manifest(run_dir, metrics=metrics, artifact_uri=None)

print("Smoke run OK:", run_dir)
print(json.dumps(metrics, indent=2))
PY
