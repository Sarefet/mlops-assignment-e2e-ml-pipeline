#!/usr/bin/env bash
# Start MLflow tracking server (background) for the slot session.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export MLFLOW_BACKEND_STORE_URI="${MLFLOW_BACKEND_STORE_URI:-sqlite:///${ROOT}/mlflow/mlflow.db}"
export MLFLOW_DEFAULT_ARTIFACT_ROOT="${MLFLOW_DEFAULT_ARTIFACT_ROOT:-${ROOT}/mlflow/artifacts}"
mkdir -p mlflow/artifacts

if pgrep -f "mlflow server" >/dev/null 2>&1; then
  echo "MLflow already running"
else
  nohup uv run mlflow server \
    --host 127.0.0.1 \
    --port 5000 \
    --backend-store-uri "${MLFLOW_BACKEND_STORE_URI}" \
    --default-artifact-root "${MLFLOW_DEFAULT_ARTIFACT_ROOT}" \
    > mlflow/server.log 2>&1 &
  echo "MLflow started on http://127.0.0.1:5000 (log: mlflow/server.log)"
fi

echo "Export for Airflow tasks:"
echo "  export MLFLOW_TRACKING_URI=http://127.0.0.1:5000"
echo "  export MLFLOW_EXPERIMENT_NAME=swe-bench-agent-eval"
