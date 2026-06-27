#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
MSWEA_COST_TRACKING='ignore_errors' uv run mini-extra swebench \
    --subset verified \
    --split test \
    --model nebius/moonshotai/Kimi-K2.6 \
    --slice '0:3' \
    --config mini-swe-agent/src/minisweagent/config/benchmarks/swebench.yaml \
    --workers 5 \
    -o trajectories
