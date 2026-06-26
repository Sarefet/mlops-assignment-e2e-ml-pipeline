from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def runs_root() -> Path:
    return project_root() / "runs"


def run_dir_for(run_id: str) -> Path:
    return runs_root() / run_id


def prepare_run_dir(run_config: dict[str, Any]) -> Path:
    """Create runs/<run-id>/ and write config.json."""
    run_dir = run_dir_for(run_config["run_id"])
    agent_dir = run_dir / "run-agent"
    eval_dir = run_dir / "run-eval"
    agent_dir.mkdir(parents=True, exist_ok=True)
    eval_dir.mkdir(parents=True, exist_ok=True)
    (eval_dir / "logs").mkdir(parents=True, exist_ok=True)
    (eval_dir / "reports").mkdir(parents=True, exist_ok=True)

    config_path = run_dir / "config.json"
    config_path.write_text(json.dumps(run_config, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return run_dir
