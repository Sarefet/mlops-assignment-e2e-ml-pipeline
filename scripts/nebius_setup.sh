#!/usr/bin/env bash
# One-shot setup + sanity checks for the Nebius CPU slot.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> Installing uv deps"
uv sync

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env — add NEBIUS_API_KEY before running the agent."
fi

# shellcheck disable=SC1091
set -a
source .env
set +a

if [[ -z "${NEBIUS_API_KEY:-}" || "${NEBIUS_API_KEY}" == "XXX" ]]; then
  echo "WARNING: NEBIUS_API_KEY is not set in .env"
fi

PARENT="$(dirname "$ROOT")"
if [[ ! -d "${PARENT}/mini-swe-agent" ]]; then
  echo "==> Cloning mini-swe-agent (reference + config path)"
  git clone --depth 1 https://github.com/SWE-agent/mini-swe-agent.git "${PARENT}/mini-swe-agent"
fi

if [[ ! -d "${PARENT}/SWE-bench" ]]; then
  echo "==> Cloning SWE-bench (reference)"
  git clone --depth 1 https://github.com/swe-bench/SWE-bench.git "${PARENT}/SWE-bench"
fi

export MINI_SWE_CONFIG="${PARENT}/mini-swe-agent/src/minisweagent/config/benchmarks/swebench.yaml"
echo "MINI_SWE_CONFIG=${MINI_SWE_CONFIG}"

chmod +x scripts/*.sh run-airflow-standalone.sh

echo "==> Pre-caching SWE-bench Verified dataset (Hugging Face)"
"${ROOT}/.venv/bin/python" - <<'PY'
from datasets import load_dataset

ds = load_dataset("princeton-nlp/SWE-bench_Verified", split="test")
print(f"Cached {len(ds)} instances")
PY

echo "==> Local pipeline smoke (sample data, no API)"
./scripts/smoke_local.sh

echo ""
echo "==> Next manual checks on the slot:"
echo "  1. bash scripts/mini-swe-bench-single.sh     # one instance, needs API key"
echo "  2. bash run-airflow-standalone.sh           # Airflow UI on :8080"
echo "  3. Trigger DAG evaluate_agent with default params"
