#!/usr/bin/env bash
# Parametric agent batch — reads config from environment (set by Airflow / pipeline).
set -euo pipefail

: "${RUN_DIR:?RUN_DIR is required}"
: "${SUBSET:=verified}"
: "${SPLIT:=test}"
: "${MODEL:=nebius/moonshotai/Kimi-K2.6}"
: "${TASK_SLICE:=0:3}"
: "${WORKERS:=3}"
: "${COST_LIMIT:=0}"
: "${MINI_SWE_CONFIG:=../mini-swe-agent/src/minisweagent/config/benchmarks/swebench.yaml}"

mkdir -p "${RUN_DIR}/trajectories"

MSWEA_COST_TRACKING='ignore_errors' mini-extra swebench \
  --subset "${SUBSET}" \
  --split "${SPLIT}" \
  --model "${MODEL}" \
  --slice "${TASK_SLICE}" \
  --config "${MINI_SWE_CONFIG}" \
  --workers "${WORKERS}" \
  --cost-limit "${COST_LIMIT}" \
  -o "${RUN_DIR}/trajectories"
