from flujo.diagnostics import domain_catalog
from flujo.departments import catalog as department_catalog
from flujo.knowledge.area_orientation import (
    AREA_IDS,
    build_area_orientation,
    validate_area_orientation,
)


def _status():
    return {
        "status": "attention",
        "generated_at": "2026-09-13T00:00:00+00:00",
        "ledger": {"counts": {"attention": 2}, "next_actions": ["review evidence"]},
        "components": {
            "hub": {"status": "ready"},
            "portfolio": {"status": "ready"},
            "research": {"status": "ready"},
        },
    }


def test_area_orientation_covers_mak_areas_without_execution():
    payload = build_area_orientation(
        _status(),
        domain_catalog("/home/mak"),
        vizz_status={"status": "unknown_measurement_refused"},
        learning={"policy": {"status": "candidate"}},
        departments=department_catalog("/home/mak"),
        generated_at="2026-09-13T00:00:00+00:00",
    )
    assert validate_area_orientation(payload)
    assert [area["id"] for area in payload["areas"]] == AREA_IDS
    assert all(area["execution_allowed"] is False for area in payload["areas"])
    assert payload["boundary"]["semantic_claim"] is False
    assert payload["control"]["execution"] is False


def test_area_orientation_preserves_operational_bases():
    payload = build_area_orientation(_status(), domain_catalog("/home/mak"), departments=department_catalog("/home/mak"))
    by_id = {area["id"]: area for area in payload["areas"]}
    assert by_id["core"]["status_basis"] == ["diagnostics_domain", "hub_component"]
    assert by_id["rd"]["observed_status"] == "catalogued"
    assert by_id["vizz"]["observed_status"] == "unknown_measurement_refused"


def test_area_orientation_rejects_semantic_or_execution_drift():
    payload = build_area_orientation(_status(), domain_catalog("/home/mak"), departments=department_catalog("/home/mak"))
    payload["areas"][0]["execution_allowed"] = True
    try:
        validate_area_orientation(payload)
    except ValueError as exc:
        assert str(exc) == "area_orientation_area_control_invalid"
    else:
        raise AssertionError("unsafe area orientation was accepted")
