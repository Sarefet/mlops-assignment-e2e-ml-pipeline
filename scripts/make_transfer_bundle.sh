#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="/Users/idan.shafat/my-repos/ml_ops_hw/e2e-ml-pipeline.tar.gz"

tar czf "$OUT" \
  --exclude='.venv' \
  --exclude='.git' \
  --exclude='runs' \
  --exclude='mlflow' \
  --exclude='logs' \
  --exclude='__pycache__' \
  --exclude='.ruff_cache' \
  --exclude='trajectories' \
  -C "$(dirname "$ROOT")" "$(basename "$ROOT")"

echo "Created $OUT ($(du -h "$OUT" | awk '{print $1}'))"
