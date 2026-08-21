"""Compact regression gate for the active web surface and local DB map."""

from tools.repo_audit import audit


def test_web_graph_has_no_dead_active_modules():
    result = audit()
    assert result["web"]["dead_modules"] == []
    assert result["stale_active_references"] == []


def test_database_inventory_is_read_only_and_declares_consumers():
    result = audit()
    assert result["policy"] == {
        "read_only": True,
        "historical_win_excluded": True,
        "missing_databases_allowed": True,
        "automatic_delete": False,
    }
    for item in result["databases"]:
        assert item["consumers"]
        assert item["missing_consumers"] == []
        if item["exists"]:
            assert item.get("integrity") == "ok"
