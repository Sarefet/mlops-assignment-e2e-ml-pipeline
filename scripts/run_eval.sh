#!/usr/bin/env bash
# Parametric SWE-bench evaluation — reads config from environment.
set -euo pipefail

: "${PREDS_PATH:?PREDS_PATH is required}"
: "${DATASET_NAME:=princeton-nlp/SWE-bench_Verified}"
: "${EVAL_WORKERS:=3}"
: "${EVAL_RUN_ID:?EVAL_RUN_ID is required}"
: "${EVAL_LOG_DIR:=logs}"

mkdir -p "${EVAL_LOG_DIR}"

python -m swebench.harness.run_evaluation \
  --dataset_name "${DATASET_NAME}" \
  --predictions_path "${PREDS_PATH}" \
  --max_workers "${EVAL_WORKERS}" \
  --run_id "${EVAL_RUN_ID}" \
  --log_dir "${EVAL_LOG_DIR}"
