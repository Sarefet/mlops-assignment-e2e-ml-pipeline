from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


def _run(cmd: list[str], *, cwd: Path, env: dict[str, str]) -> None:
    subprocess.run(cmd, cwd=cwd, env=env, check=True)


from pipeline.env import project_env as _project_env


def run_agent_batch(run_config: dict[str, Any], run_dir: Path) -> Path:
    """Run mini-swe-agent batch and place outputs under run-agent/."""
    project_root = run_dir.parents[1]
    agent_dir = run_dir / "run-agent"
    trajectories_dir = agent_dir / "trajectories"
    trajectories_dir.mkdir(parents=True, exist_ok=True)

    env = _project_env(
        project_root,
        {
            **os.environ,
            "MSWEA_COST_TRACKING": "ignore_errors",
            "RUN_DIR": str(agent_dir),
            "SUBSET": run_config["subset"],
            "SPLIT": run_config["split"],
            "MODEL": run_config["model"],
            "TASK_SLICE": run_config["task_slice"],
            "WORKERS": str(run_config["workers"]),
            "MINI_SWE_CONFIG": run_config["mini_swe_config"],
        },
    )

    script = project_root / "scripts" / "run_agent.sh"
    _run(["bash", str(script)], cwd=project_root, env=env)

    # Normalize output layout: preds.json at run-agent/preds.json
    preds_candidates = [
        agent_dir / "preds.json",
        trajectories_dir / "preds.json",
        agent_dir / "trajectories" / "preds.json",
    ]
    preds_path = next((p for p in preds_candidates if p.exists()), None)
    if preds_path is None:
        raise FileNotFoundError(f"No preds.json found under {agent_dir}")

    final_preds = agent_dir / "preds.json"
    if preds_path != final_preds:
        shutil.copy2(preds_path, final_preds)

    return final_preds
