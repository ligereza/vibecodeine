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

    assert first == {"queued": 1, "duplicates": 0, "deferred": 0, "errors": []}
    assert second == {"queued": 0, "duplicates": 1, "deferred": 0, "errors": []}
    assert rows[0]["type"] == "task"
    assert rows[0]["metadata"]["queue_status"] == "pending_human"
    assert rows[0]["metadata"]["safety"] == "no contact or submission"


def test_vigia_caps_new_queue_per_source_without_deleting_listings(tmp_path):
    path = tmp_path / "common_ledger.jsonl"
    results = [{"id": "fondos", "nuevos": [
        {"h": str(index), "fuente": "fondos", "titulo": "Open call %d" % index,
         "url": "https://official.example/%d" % index}
        for index in range(3)
    ]}]

    result = vigia.encolar_oportunidades(results, str(path), max_per_source=2)

    assert result == {"queued": 2, "duplicates": 0, "deferred": 1, "errors": []}
    assert len(ledger.read_items(str(path))) == 2


def test_summary_surfaces_pending_human(tmp_path):
    path = tmp_path / "common_ledger.jsonl"
    ledger.opportunity_from_vigia({
        "h": "xyz", "fuente": "resartis", "titulo": "Open call",
        "url": "https://official.example/open-call",
    }, path=str(path))
    assert ledger.summarize(str(path))["pending_human"] == 1


def test_vigia_prioritizes_artist_lanes_before_generic_jobs():
    items = [
        {"h": "nursing", "fuente": "empleos", "titulo": "Enfermero hospital",
         "url": "https://jobs.example/1"},
        {"h": "residency", "fuente": "resartis", "titulo": "Artist residency open call",
         "url": "https://art.example/2"},
    ]

    ranked = vigia.priorizar_oportunidades(items, {
        "direction": {"opportunities": ["artist residencies"]}
    })

    assert ranked[0]["h"] == "residency"
    assert "practice_or_funding" in ranked[0]["priority_reasons"]


def test_vigia_persists_priority_metadata(tmp_path):
    path = tmp_path / "common_ledger.jsonl"
    results = [{"id": "resartis", "nuevos": [
        {"h": "abc", "fuente": "resartis", "titulo": "Artist residency",
         "url": "https://official.example/call"}
    ]}]

    result = vigia.encolar_oportunidades(results, str(path), contexto={
        "direction": {"opportunities": ["artist residencies"]}
    })
    row = ledger.read_items(str(path))[0]

    assert result["queued"] == 1
    assert int(row["metadata"]["priority_score"]) > 0
    assert row["metadata"]["priority_reasons"]
