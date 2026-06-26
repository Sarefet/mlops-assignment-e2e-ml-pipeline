# Local dev (Mac) — no Nebius API required for smoke tests

Repo fork hand-in: **https://github.com/Sarefet/mlops-assignment-e2e-ml-pipeline** (create this fork before the slot).

## What works on Mac

| Task | Command | Needs API? |
|------|---------|------------|
| Parse sample metrics/manifest | `./scripts/smoke_local.sh` | No |
| Lint / read DAG | open `dags/evaluate_agent.py` | No |
| Airflow UI wiring | `uv sync --group airflow` + `bash run-airflow-standalone.sh` | No (DAG loads; run tasks need VM) |
| Full agent batch | `./scripts/nebius_setup.sh` then single/batch scripts | Yes (`NEBIUS_API_KEY`) |

Python **3.12+** required (course starter uses `>=3.12`).

```bash
cd /Users/idan.shafat/my-repos/ml_ops_hw/e2e-ml-pipeline
chmod +x scripts/*.sh run-airflow-standalone.sh
uv sync
./scripts/smoke_local.sh   # should print resolve_rate from sample/
```

## Push to your fork (once, before slot)

```bash
# GitHub UI: fork https://github.com/minotru/mlops-assignment-e2e-ml-pipeline
cd /Users/idan.shafat/my-repos/ml_ops_hw/e2e-ml-pipeline
git remote add mine https://github.com/Sarefet/mlops-assignment-e2e-ml-pipeline.git 2>/dev/null || true
git add -A && git commit -m "Prep: evaluate_agent DAG + pipeline helpers"
git push -u mine main
```

On the VM you can `git clone` your fork instead of uploading a tarball.

## Port forwards (slot session)

| Port | Service |
|------|---------|
| 8080 | Airflow |
| 5000 | MLflow |

Cursor: Remote-SSH → Ports → forward both.
