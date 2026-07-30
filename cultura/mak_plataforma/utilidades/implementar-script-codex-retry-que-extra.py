import argparse, sys
import sqlite3
from typing import Any
import json
import random
import time

def main() -> None:
    parser = argparse.ArgumentParser(prog="codex_worker")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_retry = sub.add_parser("codex_retry", help="Re‑intenta tareas fallidas/pending")
    p_retry.add_argument("--max", type=int, default=10, help="Número máximo de tareas a procesar (default: 10)")
    p_retry.set_defaults(func=_cmd_retry)

    p_auto = sub.add_parser("codex_autoreview", help="Revisión automática de baja complejidad")
    p_auto.add_argument("--max", type=int, default=10, help="Número máximo de revisiones a procesar (default: 10)")
    p_auto.set_defaults(func=_cmd_autoreview)

    args = parser.parse_args()
    args.func(args)

def _init_db(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS backlog_codex  (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       payload TEXT,
                       status TEXT,
                       retries INTEGER DEFAULT 0,
                       last_error TEXT,
                       confidence REAL,
                       complexity TEXT
                    )""")
    conn.commit()

def _insert_task(conn, payload: dict[str, Any], *, status="pending", retries=0, confidence=None, complexity="low"):
    cur = conn.execute("INSERT INTO backlog_codex  (payload, status, retries, confidence, complexity) VALUES  (?,?,?,?,?)",
                       (json.dumps(payload), status, retries, confidence, complexity))
    conn.commit()
    return cur.lastrowid

def _cmd_retry(args):
    conn = sqlite3.connect(":memory:")
    _init_db(conn)

    task_id = _insert_task(conn, payload={"action": "gen", "text": "hola"}, status="failed", retries=0, complexity="high")
    
    row = conn.execute("SELECT status, retries FROM backlog_codex WHERE id=?", (task_id,)).fetchone()
    assert row == ("completed", 1), "Tarea fallida debe quedar completada tras primer retry"

def _cmd_autoreview(args):
    conn = sqlite3.connect(":memory:")
    _init_db(conn)
    
    def mejora_libre(payload):
        return 0.90

    globals()["mejora_libre"] = mejora_libre

    task_id = _insert_task(conn, payload={"action": "rev", "code": "print('x')"}, status="processing", retries=0, confidence=0.70, complexity="low")
    
    row = conn.execute("SELECT status, confidence FROM backlog_codex WHERE id=?", (task_id,)).fetchone()
    assert row == ("completed", 0.90), "Con confidence ≥0.85 la tarea debe marcarse como completed"

if __name__ == "__main__" and sys.argv[1:] == ["test"]:
    import sqlite3, json, random
    
    conn = sqlite3.connect(":memory:")
    _init_db(conn)

    task_id = _insert_task(conn, payload={"action": "gen", "text": "hola"}, status="failed", retries=0, complexity="high")
    
    row = conn.execute("SELECT status, retries FROM backlog_codex WHERE id=?", (task_id,)).fetchone()
    assert row == ("completed", 1), "Tarea fallida debe quedar completada tras primer retry"

    print("✅ Todos los test internos pasaron.")
    sys.exit(0)
