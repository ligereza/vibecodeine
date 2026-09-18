#!/usr/bin/env python3
"""guarda_subida_externa.py -- thin wrapper over flujo.privacy.scan_text,
meant to run before uploading any document to an external service (Azure
Search, a model, etc.).

History: on 2026-09-18 the auto-mode classifier blocked an attempt to
upload RD reports to Azure Search as "Data Exfiltration". The first
response was to write a new guard with 4 hardcoded keywords -- but
flujo.privacy.scan_text already existed and is far more complete (RUT,
phone number, Luhn-validated card, address, and high-risk keywords that
already cover "substances"/"drugs"), and is used in production by
rd-datos ingest. This version reinvents nothing, it just wires that
existing module into the external-upload case.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path("/home/mak/flujo/src")))
from flujo.privacy.scan import scan_text  # noqa: E402


def subir_documento_seguro(client, documento: dict) -> None:
    texto = " ".join(str(v) for v in documento.values())
    resultado = scan_text(texto, source=documento.get("ruta", ""))
    if not resultado.aprobado_para_ia_externa:
        raise ValueError(
            f"Documento bloqueado por flujo.privacy.scan_text: "
            f"riesgo={resultado.risk} keywords={resultado.sensitive_keywords} "
            f"pii={list(resultado.matches.keys())}"
        )
    client.upload_documents([documento])


if __name__ == "__main__":
    casos_reales = [
        {"ruta": "docs/rd/SINTESIS_DIRECTIVA.md", "proposito": "Sintesis para la directiva: informes de sustancias y consumo."},
        {"ruta": "docs/rd/TRIANGULACION_TESTEOS_EVENTOS_2025.md", "proposito": "Triangulacion de testeo de drogas en eventos."},
        {"ruta": "src/flujo/rd/database.py", "proposito": "Constructor y consultas de la base de datos RD (SQLite)."},
    ]
    for doc in casos_reales:
        texto = " ".join(str(v) for v in doc.values())
        r = scan_text(texto, source=doc["ruta"])
        estado = "PERMITIDO" if r.aprobado_para_ia_externa else "BLOQUEADO"
        print(f"{estado}  {doc['ruta']}  riesgo={r.risk}  keywords={r.sensitive_keywords}")
