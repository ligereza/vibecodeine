import importlib.util
from pathlib import Path

from cultura.mak_plataforma import ledger


_SPEC = importlib.util.spec_from_file_location(
    "vigia_queue_test_module", Path(__file__).with_name("test_vigia.py"))
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
vigia = _MODULE.vigia


def test_vigia_queues_new_listings_once(tmp_path):
    path = tmp_path / "common_ledger.jsonl"
    results = [{"id": "fondos", "nuevos": [{
        "h": "abc123", "fuente": "fondos", "titulo": "Residencia para artistas",
        "url": "https://official.example/call",
    }]}]

    first = vigia.encolar_oportunidades(results, str(path))
    second = vigia.encolar_oportunidades(results, str(path))
    rows = ledger.read_items(str(path))

    assert first == {"queued": 1, "duplicates": 0, "errors": []}
    assert second == {"queued": 0, "duplicates": 1, "errors": []}
    assert rows[0]["type"] == "task"
    assert rows[0]["metadata"]["queue_status"] == "pending_human"
    assert rows[0]["metadata"]["safety"] == "no contact or submission"


def test_summary_surfaces_pending_human(tmp_path):
    path = tmp_path / "common_ledger.jsonl"
    ledger.opportunity_from_vigia({
        "h": "xyz", "fuente": "resartis", "titulo": "Open call",
        "url": "https://official.example/open-call",
    }, path=str(path))
    assert ledger.summarize(str(path))["pending_human"] == 1
