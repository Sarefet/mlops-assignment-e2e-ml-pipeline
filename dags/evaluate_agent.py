import json
import os
import sys
from datetime import datetime
from pathlib import Path

from airflow.decorators import dag, task
from airflow.models.param import Param

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pipeline import (  # noqa: E402
    build_run_config,
    collect_metrics,
    log_mlflow_run,
    prepare_run_dir,
    run_agent_batch,
    run_swebench_eval,
    write_manifest,
)


@dag(
    dag_id="evaluate_agent",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    params={
        "split": Param(default="test", type="string", description="SWE-bench split"),
        "subset": Param(default="verified", type="string", description="SWE-bench subset"),
        "workers": Param(default=3, type="integer", description="Parallel workers"),
        "model": Param(
            default="nebius/moonshotai/Kimi-K2.6",
            type="string",
            description="Nebius Token Factory model id",
        ),
        "task_slice": Param(
            default="0:3",
            type="string",
            description="Instance slice, e.g. 0:3 for first three tasks",
        ),
        "run_id": Param(default="", type="string", description="Optional stable run id"),
        "cost_limit": Param(default="0", type="string", description="mini-swe-agent cost limit"),
    },
    tags=["swe-bench", "mini-swe-agent"],
)
def evaluate_agent():
    @task
    def prepare_run(**context) -> str:
        run_config = build_run_config(context["params"])
        run_dir = prepare_run_dir(run_config)
        return str(run_dir)

    @task
    def run_agent(run_dir_str: str, **context) -> str:
        run_dir = Path(run_dir_str)
        run_config = json.loads((run_dir / "config.json").read_text(encoding="utf-8"))
        preds_path = run_agent_batch(run_config, run_dir)
        return str(preds_path)

    @task
    def run_eval(run_dir_str: str, preds_path_str: str, **context) -> str:
        run_dir = Path(run_dir_str)
        run_config = json.loads((run_dir / "config.json").read_text(encoding="utf-8"))
        eval_dir = run_swebench_eval(run_config, Path(preds_path_str), run_dir)
        return str(eval_dir)

    @task
    def summarize_and_log(run_dir_str: str, eval_dir_str: str, **context) -> dict:
        run_dir = Path(run_dir_str)
        run_config = json.loads((run_dir / "config.json").read_text(encoding="utf-8"))
        metrics = collect_metrics(Path(eval_dir_str))
        metrics_path = run_dir / "metrics.json"
        metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        artifact_uri = os.environ.get("RUN_ARTIFACT_URI")
        write_manifest(run_dir, metrics=metrics, artifact_uri=artifact_uri)
        mlflow_run_id = log_mlflow_run(
            run_config,
            metrics,
            artifact_uri,
            run_dir=run_dir,
        )
        return {
            "run_id": run_config["run_id"],
            "run_dir": str(run_dir),
            "metrics": metrics,
            "mlflow_run_id": mlflow_run_id,
        }

    run_dir = prepare_run()
    preds = run_agent(run_dir)
    eval_dir = run_eval(run_dir, preds)
    summarize_and_log(run_dir, eval_dir)


evaluate_agent()
