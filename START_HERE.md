# START HERE — E2E ML Pipeline homework

Course: Nebius Academy MLOps, **Lesson 6** — End-to-end ML pipeline  
Starter: [minotru/mlops-assignment-e2e-ml-pipeline](https://github.com/minotru/mlops-assignment-e2e-ml-pipeline)  
Your fork (hand-in): **https://github.com/Sarefet/mlops-assignment-e2e-ml-pipeline** ← create before the slot  
Local prep (already started): `/Users/idan.shafat/my-repos/ml_ops_hw/e2e-ml-pipeline`

**Workplace repos (`airflow-prod-etl`, `de_etl`) are off limits** — this is course homework only.

---

## The one idea

| | Your Mac | Nebius CPU VM (8 CPU, 32 GB) |
|---|---|---|
| GPU? | No | No (inference is Nebius API) |
| What to do here | Write code, smoke-test parsing, push to fork | Run agent, eval, Airflow, MLflow, screenshots |
| API key | Optional | **Required** (`NEBIUS_API_KEY`) |

**Goal:** Turn ad-hoc `mini-swe-agent` + SWE-bench scripts into a **configurable Airflow DAG** with durable `runs/<run-id>/` artifacts and **MLflow** tracking.

```text
prepare_run → run_agent → run_eval → summarize_and_log
```

---

## Should you fork?

**Yes.** Same pattern as assignment #4 (`Sarefet/mlops-assignment`).

1. GitHub → open [minotru/mlops-assignment-e2e-ml-pipeline](https://github.com/minotru/mlops-assignment-e2e-ml-pipeline) → **Fork**
2. Name it e.g. `Sarefet/mlops-assignment-e2e-ml-pipeline`
3. Push your local prep to `mine` remote (see [README_LOCAL.md](README_LOCAL.md))
4. **Hand-in link** = your fork URL + `REPORT.md` + screenshots

You can either **git clone your fork** on the VM or **upload a tarball** (see Phase B).

---

## What we already prepared locally

| Item | Status |
|------|--------|
| `dags/evaluate_agent.py` | 4-task DAG with Airflow params |
| `pipeline/` | config, paths, agent/eval runners, MLflow, manifest |
| `scripts/run_agent.sh`, `run_eval.sh` | Parametric (env-driven) |
| `scripts/smoke_local.sh` | Tests metrics/manifest using `sample/` — **no API** |
| `scripts/nebius_setup.sh` | VM one-shot setup |
| `scripts/start_mlflow.sh` | MLflow server on :5000 |
| `scripts/upload_from_mac.sh` | Tarball upload helper |
| `REPORT.md` | Template to fill on slot |

---

## Grading cheat sheet (what matters)

| Area | Weight | Minimum to score well |
|------|--------|------------------------|
| Configurable Airflow DAG | 35% | `evaluate_agent` runs from UI with params |
| Artifact structure | 20% | Full `runs/<run-id>/` tree + `manifest.json` |
| MLflow | 15% | Params + metrics + artifact path logged |
| Execution isolation | 10% | Documented env; bonus: DockerOperator |
| Docker Compose | 10% | Airflow + MLflow via compose (optional v1) |
| REPORT.md | 10% | Architecture, trigger steps, one real run |

**Provenance > lucky metric.** A 1/3 resolve rate with a perfect run folder beats a pasted number.

---

# PHASE A — On your Mac (before the slot)

Do this **now**, no Nebius machine needed.

### A1. Fork + push (5 min)

```bash
cd /Users/idan.shafat/my-repos/ml_ops_hw/e2e-ml-pipeline
chmod +x scripts/*.sh run-airflow-standalone.sh
uv sync
./scripts/smoke_local.sh
```

Expected: prints `Smoke run OK: .../runs/sample-smoke` and `resolve_rate: 0.333...`

If smoke fails, fix before the slot — saves an hour on the VM.

### A2. Create GitHub fork and push

See [README_LOCAL.md](README_LOCAL.md).

### A3. Get `NEBIUS_API_KEY` ready

- Nebius Token Factory / Academy portal
- Paste into a password manager — you'll copy to VM `.env` on slot day
- **Do not commit** `.env`

### A4. (Optional) Skim starter + sample

```bash
ls sample/trajectories/          # preds.json + per-instance trajectories
cat sample/nebius__moonshotai__Kimi-K2.6.test.json | head   # aggregate metrics
open dags/evaluate_agent.py
```

### A5. Build upload bundle (if not using git on VM)

```bash
./scripts/make_transfer_bundle.sh
# → /Users/idan.shafat/my-repos/ml_ops_hw/e2e-ml-pipeline.tar.gz
```

---

# PHASE B — Nebius slot (step by step)

**Hardware:** 8 CPU, 32 GB RAM, public IP — **not** H100.  
**Connect:** Cursor Remote-SSH (same as inference-o11y homework).

### B0. Port forwards

| Local port | Service |
|------------|---------|
| **8080** | Airflow UI |
| **5000** | MLflow UI |

---

### B1. Get code on the VM

**Option 1 — git (preferred)**

```bash
git clone https://github.com/Sarefet/mlops-assignment-e2e-ml-pipeline.git
cd mlops-assignment-e2e-ml-pipeline   # or e2e-ml-pipeline if you renamed locally
```

**Option 2 — tarball from Mac**

On Mac Terminal:

```bash
/Users/idan.shafat/my-repos/ml_ops_hw/e2e-ml-pipeline/scripts/upload_from_mac.sh
```

Then on VM:

```bash
cd ~ && tar xzf e2e-ml-pipeline.tar.gz && cd e2e-ml-pipeline
```

---

### B2. VM prerequisites (first time only)

If Docker/uv not installed, follow the **Prerequisites** section in the course README:

```bash
# uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Docker (for SWE-bench eval sandboxes + optional Phase 3)
# ... see README Prerequisites block ...
sudo usermod -aG docker "$USER"
newgrp docker
```

---

### B3. One-shot setup

```bash
chmod +x scripts/*.sh run-airflow-standalone.sh
./scripts/nebius_setup.sh
```

This runs `uv sync`, clones `mini-swe-agent` + `SWE-bench` siblings, and **smoke_local**.

```bash
cp .env.example .env
nano .env   # set NEBIUS_API_KEY=...
```

---

### B4. Sanity check — single instance (API smoke)

~5–15 min, confirms API + Docker eval path:

```bash
source .env
bash scripts/mini-swe-bench-single.sh
```

If this fails, fix API key / Docker before Airflow.

---

### B5. Start MLflow

```bash
./scripts/start_mlflow.sh
export MLFLOW_TRACKING_URI=http://127.0.0.1:5000
export MLFLOW_EXPERIMENT_NAME=swe-bench-agent-eval
```

Open http://localhost:5000 on laptop (port forward).

---

### B6. Start Airflow

```bash
bash run-airflow-standalone.sh
```

- UI: http://localhost:8080
- Login: `admin` / `admin` (standalone default)
- Confirm DAG **`evaluate_agent`** appears (green, no import errors)

---

### B7. Run the pipeline (submission run)

1. Airflow → **evaluate_agent** → **Trigger DAG w/ config**
2. Use defaults or explicit JSON:

```json
{
  "split": "test",
  "subset": "verified",
  "workers": 3,
  "model": "nebius/moonshotai/Kimi-K2.6",
  "task_slice": "0:3",
  "run_id": "submit-v1",
  "cost_limit": "0"
}
```

3. Watch tasks: `prepare_run` → `run_agent` → `run_eval` → `summarize_and_log`
4. **run_agent** is the long step (3 SWE-bench instances × API calls)

---

### B8. Verify artifacts

```bash
ls -R runs/submit-v1/
cat runs/submit-v1/metrics.json
cat runs/submit-v1/manifest.json
```

Checklist:

- [ ] `config.json`
- [ ] `run-agent/preds.json`
- [ ] `run-agent/trajectories/`
- [ ] `run-eval/logs/` and `run-eval/reports/`
- [ ] `metrics.json` with `resolved_instances`, `resolve_rate`
- [ ] `manifest.json`

---

### B9. Verify MLflow

- Open MLflow UI → experiment `swe-bench-agent-eval`
- Run named `submit-v1` with params + metrics
- Screenshot → `screenshots/mlflow_runs.png`

---

### B10. Screenshots

```bash
mkdir -p screenshots
```

- `screenshots/airflow_dag.png` — DAG graph, all tasks green
- `screenshots/mlflow_runs.png` — logged run with metrics

---

### B11. Fill REPORT.md

Edit `REPORT.md` with:

- Architecture (short)
- Exact trigger params you used
- run_id, resolve_rate, what happened
- How to rerun by run_id
- Screenshot paths

---

### B12. Push and submit

```bash
git add dags/ pipeline/ scripts/ REPORT.md screenshots/ runs/submit-v1/manifest.json
# Commit small manifest or metrics only — NOT multi-GB trajectories
git commit -m "Complete evaluate_agent pipeline run submit-v1"
git push mine main
```

Hand in: **fork URL** + ensure grader can follow README/REPORT.

---

# PHASE C — Production extras (if time left)

Do after B12 minimum works.

| Step | What |
|------|------|
| C1 | Second DAG run with different `task_slice` or `model` — compare in MLflow |
| C2 | `docker-compose.yaml` for Airflow + MLflow (course README link) |
| C3 | `DockerOperator` instead of subprocess in DAG |
| C4 | Upload `runs/<run-id>/` to Nebius Object Storage; set `RUN_ARTIFACT_URI` in `.env` |
| C5 | Screenshot `object_storage_artifacts.png` |

---

# Troubleshooting

| Symptom | Fix |
|---------|-----|
| DAG import error | `export PYTHONPATH=$(pwd):$PYTHONPATH` before Airflow |
| `mini-swe-agent config not found` | `export MINI_SWE_CONFIG=../mini-swe-agent/src/.../swebench.yaml` |
| Eval Docker errors | `docker ps`, user in `docker` group, `newgrp docker` |
| MLflow connection refused | `./scripts/start_mlflow.sh`, check port 5000 forward |
| `preds.json` missing | Check `run-agent/trajectories/preds.json` — pipeline copies to `run-agent/preds.json` |
| Slot running out | Use `task_slice: "0:1"` for a faster proof run first |

---

# Time budget (8 CPU slot)

| Step | ~Time |
|------|-------|
| B1–B3 setup | 15–25 min |
| B4 single sanity | 10–20 min |
| B5–B6 Airflow + MLflow | 10 min |
| B7 full DAG `0:3` | 30–90 min (API + eval) |
| B8–B12 docs + push | 20 min |

**Tip:** Run B7 early. Do REPORT/screenshots while waiting or after.

---

# Quick reference

```bash
# Mac smoke (no API)
./scripts/smoke_local.sh

# VM setup
./scripts/nebius_setup.sh && cp .env.example .env

# Services
./scripts/start_mlflow.sh
bash run-airflow-standalone.sh

# After successful run
ls runs/<run-id>/
```

When you're ready for the slot, say the word and we'll debug live step by step.
