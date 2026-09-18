#!/usr/bin/env python3
"""promover_reglas.py -- integra project_ir.promote_rule() al ciclo real.

`promote_rule()` ya existe, completo y con criterios estrictos (soporte
minimo, holdout aprobado, cero contradicciones); antes de este script solo
lo invocaban los tests. Este script recorre todas las reglas candidatas y
llama a la funcion ya construida sobre cada una. Nunca decide con criterio
propio: solo asegura que el criterio que ya existe se aplique, en vez de
quedar sin usar.

Cada regla termina en uno de dos estados, nunca en silencio:
  - promovida: paso los criterios existentes.
  - rechazada, con la razon exacta que devuelve promote_rule().

Uso:
    python3 tools/promover_reglas.py [--db data/mak_knowledge.db]
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from flujo.knowledge.project_ir import LearningStore, ProjectIRError  # noqa: E402


def _candidate_rules(db_path: str) -> list[dict]:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT rule_id, evaluation_id, support_count, contradiction_count "
        "FROM semantic_rules WHERE status='candidate'"
    ).fetchall()
    con.close()
    return [dict(r) for r in rows]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default="data/mak_knowledge.db")
    ap.add_argument("--min-support", type=int, default=2)
    args = ap.parse_args(argv)

    store = LearningStore(args.db)
    candidates = _candidate_rules(args.db)
    if not candidates:
        print("no hay reglas candidatas.")
        return 0

    promoted, rejected = 0, 0
    for rule in candidates:
        rule_id = rule["rule_id"]
        evaluation_id = rule["evaluation_id"] or ""
        try:
            store.promote_rule(rule_id, min_support=args.min_support,
                               evaluation_id=evaluation_id)
            print(f"PROMOVIDA   {rule_id}")
            promoted += 1
        except ProjectIRError as exc:
            print(f"RECHAZADA   {rule_id}  razon={exc}")
            rejected += 1

    print()
    print(f"total candidatas: {len(candidates)}  promovidas: {promoted}  rechazadas: {rejected}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
