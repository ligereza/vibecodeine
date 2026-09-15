import copy

from flujo.knowledge.operations_read_only_map import (
    ENDPOINTS,
    build_operations_read_only_map,
    validate_operations_read_only_map,
)


def _snapshots():
    payloads = {
        endpoint: {"schema": f"schema-{index}"}
        for index, endpoint in enumerate(ENDPOINTS)
    }
    payloads["/api/rd/topics"].update({"topics": [{"id": "one"}], "database": {"canonical_rows": 2, "runtime_rows": 0}})
    payloads["/api/rd/crosswalk"].update({"status": "review_only", "entities": [{"id": "one"}]})
    payloads["/api/rd/cultura-relations"].update({"status": "read_only_candidate_graph", "producers": [], "venues": [], "relations": []})
    payloads["/api/cultura/sources"].update({"roots": [], "entries": []})
    payloads["/api/cultura/capabilities"].update({"policy": {"offline_first": True}, "output_formats": []})
    payloads["/api/cultura/opportunity-gate"].update({"mode": "contract_check_only", "required_fields": []})
    payloads["/api/research/catalog"].update({"adapters": [], "jobs": 0})
    payloads["/api/research/jobs"].update({"jobs": []})
    payloads["/api/portfolio/archive-view"].update({"status": "draft_only", "selection": {}, "reconciliation": {}, "source": {}})
    payloads["/api/portfolio/vizz-measurement-status"].update({"status": "unknown_measurement_refused", "measurement": {"triangulation_attempted": False, "depth_result_present": False}, "provenance": {"ref": "fixture"}})
    return {endpoint: {"http_status": 200, "payload": payloads[endpoint]} for endpoint in ENDPOINTS}


def test_operations_map_is_ordered_and_fail_closed():
    payload = build_operations_read_only_map(_snapshots(), generated_at="fixture-1")
    assert validate_operations_read_only_map(payload)
    assert [item["endpoint"] for item in payload["entries"]] == ENDPOINTS
    assert all(item["claims"]["semantic_claim"] is False for item in payload["entries"])
    assert payload["control"]["external_calls"] is False


def test_operations_map_normalized_content_is_deterministic():
    first = build_operations_read_only_map(_snapshots(), generated_at="fixture-1")
    second = build_operations_read_only_map(_snapshots(), generated_at="fixture-2")
    first.pop("generated_at")
    second.pop("generated_at")
    assert first == second


def test_operations_map_rejects_claim_drift():
    payload = build_operations_read_only_map(_snapshots())
    tampered = copy.deepcopy(payload)
    tampered["entries"][0]["claims"]["learning_demonstrated"] = True
    try:
        validate_operations_read_only_map(tampered)
    except ValueError as exc:
        assert str(exc) == "operations_map_entry_control_invalid"
    else:
        raise AssertionError("unsafe operations map was accepted")


def test_operations_map_rejects_unsafe_child_control():
    snapshots = _snapshots()
    snapshots[ENDPOINTS[0]]["payload"]["control"] = {"database_write": True}
    try:
        build_operations_read_only_map(snapshots)
    except ValueError as exc:
        assert str(exc) == "operations_map_source_control_invalid"
    else:
        raise AssertionError("unsafe child payload was projected")


def test_operations_map_projects_explicit_child_learning_boundary():
    snapshots = _snapshots()
    snapshots["/api/project/learning-read-only-context"]["payload"]["boundary"] = {"learning_demonstrated": False}
    payload = build_operations_read_only_map(snapshots)
    entry = next(item for item in payload["entries"] if item["endpoint"] == "/api/project/learning-read-only-context")
    assert entry["claims"]["learning_demonstrated"] is False


def test_operations_map_rejects_nested_learning_claim():
    snapshots = _snapshots()
    snapshots["/api/project/learning-read-only-context"]["payload"]["boundary"] = {"learning_demonstrated": True}
    try:
        build_operations_read_only_map(snapshots)
    except ValueError as exc:
        assert str(exc) == "operations_map_source_claim_invalid"
    else:
        raise AssertionError("nested unsafe claim was accepted")


def test_operations_map_normalizes_unavailable_status_fail_closed():
    snapshots = _snapshots()
    snapshots[ENDPOINTS[0]] = {"http_status": None, "payload": {}}
    payload = build_operations_read_only_map(snapshots)
    assert payload["entries"][0]["observed_status"] == "unavailable_http_unknown"
    try:
        build_operations_read_only_map(None)
    except ValueError as exc:
        assert str(exc) == "operations_map_snapshots_invalid"
    else:
        raise AssertionError("invalid snapshots were accepted")
