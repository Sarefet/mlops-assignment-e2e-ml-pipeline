#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
MSWEA_COST_TRACKING='ignore_errors' uv run mini-extra swebench-single \
    --subset verified \
    --split test \
    --model nebius/moonshotai/Kimi-K2.6 \
    --yolo \
    --cost-limit 0 \
    -i sympy__sympy-15599 \
    -o trajectory.json
