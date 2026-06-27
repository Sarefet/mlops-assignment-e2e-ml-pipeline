#!/usr/bin/env bash
# Start Airflow + MLflow via Docker Compose (production-style deployment).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  echo "Copy .env.example to .env and set NEBIUS_API_KEY first."
  exit 1
fi

PARENT="$(dirname "$ROOT")"
if [[ ! -d "${PARENT}/mini-swe-agent" ]]; then
  echo "WARNING: ../mini-swe-agent not found. Clone it or set MINI_SWE_AGENT_PATH."
fi

export MINI_SWE_AGENT_PATH="${MINI_SWE_AGENT_PATH:-${PARENT}/mini-swe-agent}"

echo "==> Building and starting mlflow + airflow"
docker compose up -d --build

echo ""
echo "Airflow UI:  http://localhost:8080  (admin / admin)"
echo "MLflow UI:   http://localhost:5000"
echo "Logs:        docker compose logs -f airflow"
echo "Stop:        docker compose down"
