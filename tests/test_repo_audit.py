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
        # A consumer that cannot be checked here is only ever a motor file in
        # the FLUJO checkout, never a MAK path. Measured 2026-09-02: this test
        # passed in /home/mak and failed in every agent worktree, because four
        # `flujo/src/flujo/*` consumers are absent wherever that sibling
        # checkout is not on disk -- which includes a fresh clone. An absence
        # that is the topology must not read as a broken inventory.
        for consumer in item.get("unverifiable_consumers", []):
            assert consumer.startswith("flujo/"), consumer
            assert consumer in item["peer_consumers"], consumer


def test_a_consumer_outside_the_peer_checkout_is_still_a_finding():
    """The exemption is for the sibling checkout only, not for absence at large.

    Softening the check into "absent is fine" would have hidden the very thing
    it exists to catch: a database whose declared reader no longer exists in
    this branch.
    """
    from pathlib import Path

    from tools import repo_audit

    original = repo_audit.DB_CONSUMERS
    patched = dict(original)
    first = sorted(patched)[0]
    patched[first] = (*patched[first], "cultura/no_existe_este_consumidor.py")
    repo_audit.DB_CONSUMERS = patched
    try:
        result = repo_audit.audit()
    finally:
        repo_audit.DB_CONSUMERS = original

    item = next(row for row in result["databases"] if row["path"] == first)
    assert "cultura/no_existe_este_consumidor.py" in item["missing_consumers"]
    assert result["ok"] is False
    assert not Path("cultura/no_existe_este_consumidor.py").exists()


def test_tool_consumer_inventory_is_explicit_and_bounded():
    result = audit()["tools"]

    assert result["schema"] == "mak-tool-consumer-inventory-v1"
    assert result["historical_win_excluded"] is True
    # 106, not 137: the MAK/FLUJO separation removed the tools that drive the
    # motor from this branch. The number is pinned on purpose -- an unnoticed
    # drift in the tool inventory is what this ratchet exists to catch.
    #
    # 105 -> 106 on 2026-09-02: `gen_campo_iskvw.py` came back to MAK by
    # consumer (commit ea847e0b), after this pin was written (4bba4e98). The
    # ratchet did its job -- it caught a real inventory move.
    #
    # 106 -> 104 on 2026-09-03: `agent_bootstrap.py` and `handoff.py` were
    # deleted by the operator's order. Both existed to manufacture "current
    # state" out of documents -- the first emitted a hash-pinned packet from
    # `agents.md` plus the handoff, the second printed a template to paste into
    # the handoff. The active document is now `DECISIONES.md`, which holds
    # decisions and no facts, and the facts come from `tools/mak_status.py`.
    # Neither tool had a consumer other than its own test.
    assert result["count"] == 104
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
