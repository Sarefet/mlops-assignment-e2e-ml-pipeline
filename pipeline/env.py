from __future__ import annotations

import os
from pathlib import Path


def load_project_dotenv(project_root: Path) -> dict[str, str]:
    """Load .env so Airflow tasks get NEBIUS_API_KEY even if the parent shell didn't."""
    env_file = project_root / ".env"
    if not env_file.exists():
        return {}
    from dotenv import dotenv_values

    return {k: v for k, v in dotenv_values(env_file).items() if v is not None}


def project_env(project_root: Path, base: dict[str, str]) -> dict[str, str]:
    """Merge .env, process env, and task-specific variables; prepend project venv to PATH."""
    env = {**load_project_dotenv(project_root), **base}
    venv_bin = project_root / ".venv" / "bin"
    if venv_bin.is_dir():
        env["PATH"] = f"{venv_bin}:{env.get('PATH', '')}"
    return env
