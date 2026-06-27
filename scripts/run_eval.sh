#!/usr/bin/env bash
# Parametric SWE-bench evaluation — reads config from environment.
set -euo pipefail

: "${PREDS_PATH:?PREDS_PATH is required}"
: "${DATASET_NAME:=princeton-nlp/SWE-bench_Verified}"
: "${DATASET_SPLIT:=test}"
: "${EVAL_WORKERS:=3}"
: "${EVAL_RUN_ID:?EVAL_RUN_ID is required}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="${ROOT}/.venv/bin/python"

"${PYTHON}" -m swebench.harness.run_evaluation \
  --dataset_name "${DATASET_NAME}" \
  --split "${DATASET_SPLIT}" \
  --predictions_path "${PREDS_PATH}" \
  --max_workers "${EVAL_WORKERS}" \
  --run_id "${EVAL_RUN_ID}"
