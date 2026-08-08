#!/usr/bin/env python3
"""Adjudica candidatos legados sin promover ni borrar productos."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import providers

BASE = "/home/mak/plataforma/director_runs/faro-report-action-queue-20260808"
SOURCE = os.path.join(BASE, "RESCUE_REVIEW.json")
OUTPUT = os.path.join(BASE, "watsonx_adjudication_batches.jsonl")


def main():
    providers.load_env()
    data = json.load(open(SOURCE, encoding="utf-8"))
    items = data.get("items", [])
    with open(OUTPUT, "w", encoding="utf-8") as sink:
        for offset in range(0, len(items), 5):
            batch = items[offset:offset + 5]
            prompt = {
                "task": "Adjudica candidatos de informes legacy ya auditados.",
                "decision_vocabulary": ["rescue", "review", "retire_without_deleting"],
                "rules": [
                    "Usa solo los datos recibidos; no investigues ni inventes.",
                    "rescue exige proposito, lane, formato, claim y evidencia coherentes.",
                    "Si la evidencia no prueba el claim, usa review.",
                    "retire_without_deleting solo si es claramente duplicado, huerfano o contradictorio.",
                    "Devuelve JSON array con work_id, decision, reason, missing_evidence.",
                    "No promociones, borres ni escribas informes."
                ],
                "items": batch,
            }
            try:
                raw = providers.call("watsonx", json.dumps(prompt, ensure_ascii=False),
                                     max_tokens=2600, temperature=0.0)
                status = "ok"
            except Exception as exc:
                raw = ""
                status = "error:" + str(exc)[:180]
            sink.write(json.dumps({"batch": offset // 5 + 1, "status": status,
                                   "raw": raw,
                                   "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
                                  ensure_ascii=False) + "\n")
            sink.flush()
            print(json.dumps({"batch": offset // 5 + 1, "status": status}), flush=True)


if __name__ == "__main__":
    main()
