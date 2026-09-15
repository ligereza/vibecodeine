import importlib.util


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MAK_OPS = _load("mak_operations", "/home/mak/src/flujo/knowledge/operations_read_only_map.py")
FLUJO_OPS = _load("flujo_operations", "/home/mak/flujo/src/flujo/knowledge/operations_read_only_map.py")
MAK_AREA = _load("mak_area", "/home/mak/src/flujo/knowledge/area_orientation.py")
FLUJO_AREA = _load("flujo_area", "/home/mak/flujo/src/flujo/knowledge/area_orientation.py")


def _operations_fixture(module, http_status=200):
    return {
        endpoint: {"http_status": http_status, "payload": {"schema": f"fixture-{index}"}}
        for index, endpoint in enumerate(module.ENDPOINTS)
    }


def _area_fixture():
    return {
        "status": "attention",
        "generated_at": "fixture",
        "ledger": {"counts": {"attention": 1}, "next_actions": ["review"]},
        "components": {"hub": {"status": "ready"}, "portfolio": {"status": "ready"}, "research": {"status": "ready"}},
    }, {
        "domains": {area_id: {"contract": f"contract/{area_id}.md", "checks": [f"check-{area_id}"]} for area_id in ("core", "rd", "portfolio", "cultura", "research")}
    }, {
        "areas": {department_id: {"label": department_id, "surface": f"/departments/{department_id}", "runtime_mode": "offline_first", "contract_dir": f"contracts/{department_id}", "handoff_exists": True, "ready": True, "root_checks": {"root": True}, "tool_links": [{"path": f"/api/{department_id}"}] } for department_id in ("rd", "cultura", "iskvw")}
    }


def test_operations_mirror_matches_canonical_on_valid_and_unavailable_inputs():
    first = MAK_OPS.build_operations_read_only_map(_operations_fixture(MAK_OPS), generated_at="same")
    second = FLUJO_OPS.build_operations_read_only_map(_operations_fixture(FLUJO_OPS), generated_at="same")
    assert first == second
    first_unavailable = MAK_OPS.build_operations_read_only_map(_operations_fixture(MAK_OPS, http_status=None))
    second_unavailable = FLUJO_OPS.build_operations_read_only_map(_operations_fixture(FLUJO_OPS, http_status=None))
    assert first_unavailable == second_unavailable


def test_operations_mirror_matches_canonical_rejection():
    for module in (MAK_OPS, FLUJO_OPS):
        try:
            module.build_operations_read_only_map(None)
        except ValueError as exc:
            assert str(exc) == "operations_map_snapshots_invalid"
        else:
            raise AssertionError("invalid snapshots were accepted")


def test_area_mirror_matches_canonical():
    status, domains, departments = _area_fixture()
    first = MAK_AREA.build_area_orientation(status, domains, departments=departments, generated_at="same")
    second = FLUJO_AREA.build_area_orientation(status, domains, departments=departments, generated_at="same")
    assert first == second
    assert MAK_AREA.validate_area_orientation(first)
    assert FLUJO_AREA.validate_area_orientation(second)
