#!/usr/bin/env python3
"""reportar_calibracion_deepseek.py -- lee el evaluador real (learning_evaluations
en data/mak_knowledge.db) para el patron azure_delegation_pattern, calcula la
tasa de acierto real de DeepSeek con hechos completos, y la registra en MLflow
(workspace makmak-ml-workspace) como una corrida repetible, no un numero
mencionado en un chat.

Uso:
    python3 tools/reportar_calibracion_deepseek.py
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def main() -> int:
    con = sqlite3.connect("data/mak_knowledge.db")
    cur = con.cursor()
    cur.execute(
        "SELECT status, COUNT(*) FROM learning_evaluations "
        "WHERE target_kind='azure_delegation_pattern' GROUP BY status"
    )
    rows = dict(cur.fetchall())
    passed = rows.get("passed", 0)
    failed = rows.get("failed", 0)
    total = passed + failed
    accuracy = passed / total if total else 0.0

    print(f"aciertos={passed} fallos={failed} total={total} accuracy={accuracy:.3f}")

    try:
        import mlflow
        mlflow.set_tracking_uri(
            "azureml://brazilsouth.api.azureml.ms/mlflow/v1.0/subscriptions/"
            "6519fcfc-3807-407e-bae5-5f1f7f64e337/resourceGroups/makmak/"
            "providers/Microsoft.MachineLearningServices/workspaces/makmak-ml-workspace"
        )
        mlflow.set_experiment("mak-azure-integration")
        with mlflow.start_run(run_name="calibracion-deepseek-real"):
            mlflow.log_metric("deepseek_aciertos", passed)
            mlflow.log_metric("deepseek_fallos", failed)
            mlflow.log_metric("deepseek_accuracy", accuracy)
        print("registrado en MLflow.")
    except Exception as exc:  # noqa: BLE001
        print(f"MLflow no disponible o fallo la conexion, numeros arriba son reales igual: {exc}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
