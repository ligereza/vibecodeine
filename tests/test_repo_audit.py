"""Compact regression gate for the active web surface and local DB map."""

from tools.repo_audit import _searchable_text, _tools_markdown, audit


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


def test_tool_consumer_inventory_is_explicit_and_bounded():
    result = audit()["tools"]

    assert result["schema"] == "mak-tool-consumer-inventory-v1"
    assert result["historical_win_excluded"] is True
    # 105, not 137: the MAK/FLUJO separation removed the tools that drive the
    # motor from this branch. The number is pinned on purpose -- an unnoticed
    # drift in the tool inventory is what this ratchet exists to catch.
    assert result["count"] == 105
    assert len(result["files"]) == result["count"]
    summary = result["summary"]
    assert summary["with_production_reference"] + summary["tests_only"] \
        + summary["without_any_reference"] == result["count"]
    assert summary["without_any_reference"] > 0
    for row in result["files"]:
        assert row["path"].startswith("tools/")
        assert row["exists"] is True
        assert set(row) >= {
            "refs_production", "refs_test", "workflows", "consumer_evidence",
        }
        assert all("WIN" not in path and "curatoria_inbox" not in path
                   for paths in (row["refs_production"], row["refs_test"], row["workflows"])
                   for path in paths)


def test_tool_search_ignores_python_comments_and_docstrings():
    source = (
        '"""Mention tools/not_a_consumer.py in documentation."""\n'
        '# tools/not_a_consumer.py is only a comment\n'
        'COMMAND = "tools/not_a_consumer.py"\n'
    )

    searchable = _searchable_text(__import__("pathlib").Path("probe.py"), source)

    assert searchable.count("tools/not_a_consumer.py") == 1


def test_tool_inventory_markdown_is_generated_from_inventory():
    rendered = _tools_markdown({
        "schema": "mak-tool-consumer-inventory-v1",
        "count": 1,
        "summary": {
            "with_production_reference": 1,
            "tests_only": 0,
            "without_any_reference": 0,
            "with_workflow_trigger": 0,
        },
        "files": [{
            "path": "tools/example.py",
            "refs_production": ["src/example.py"],
            "refs_test": [],
            "workflows": [],
            "consumer_evidence": True,
        }],
    })
    assert "count: **1**" in rendered
    assert "`tools/example.py`" in rendered
    assert "`src/example.py`" in rendered
