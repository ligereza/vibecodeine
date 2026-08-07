from __future__ import annotations

import json

from flujo.web.hub import HubRequestHandler


def _write_jsonl(path, rows):
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def test_hub_exposes_mak_batch_ledger_surface(tmp_path, monkeypatch):
    common = tmp_path / "common_ledger.jsonl"
    batch = tmp_path / "external_batches.jsonl"
    _write_jsonl(common, [
        {
            "schema": "mak-ledger-v1",
            "source": "watsonx:rd_evidence",
            "domain": "rd",
            "type": "decision",
            "claim": "accept review",
            "action": "verify_source",
        },
        {
            "schema": "mak-ledger-v1",
            "source": "watsonx:rd_evidence",
            "domain": "rd",
            "type": "evidence",
            "claim": "official source field exists",
            "action": "verify_source",
        },
        {
            "schema": "mak-ledger-v1",
            "source": "local_review:aws",
            "domain": "svg",
            "type": "reject",
            "claim": "revise review for svg",
            "action": "reject",
            "reject_reason": "missing measurement",
        },
        {
            "schema": "mak-ledger-v1",
            "source": "vigia:fondos",
            "domain": "opportunities",
            "type": "task",
            "claim": "New watched opportunity",
            "action": "review",
            "metadata": {"queue_status": "pending_human", "next_action": "verify"},
        },
    ])
    _write_jsonl(batch, [
        {"area": "rd_evidence", "provider": "watsonx", "status": "accepted", "items": 1},
        {"area": "svg_pipeline", "provider": "aws", "status": "revise", "items": 0},
    ])
    monkeypatch.setenv("FLUJO_MAK_COMMON_LEDGER", str(common))
    monkeypatch.setenv("FLUJO_MAK_BATCH_LEDGER", str(batch))

    fake = HubRequestHandler.__new__(HubRequestHandler)
    surface = HubRequestHandler._get_mak_tandas(fake)

    assert surface["common_rows"] == 4
    assert surface["batch_rows"] == 2
    assert surface["accepted"] == 1
    assert surface["rejected_or_revise"] == 1
    assert surface["decisions"] == 1
    assert surface["by_domain"] == {"rd": 2, "svg": 1, "opportunities": 1}
    assert surface["by_provider"]["watsonx"] == 2
    assert surface["pending"][0]["reason"] == "missing measurement"
    assert surface["pending_human"] == 1


def test_mak_panel_contains_external_batch_surface():
    src = open("web/src/components/MakPanel.tsx", encoding="utf-8").read()

    assert "Tandas externas y juicio local" in src
    assert "Pendiente de revisión" in src
    assert "by_provider" in src
    assert "Memoria operativa MAK" in src
    assert "Slugs repetidos" in src
