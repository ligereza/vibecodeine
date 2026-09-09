from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

import tools.mak_ops.migrate_unified_knowledge as controller
import flujo.knowledge.postgres_runtime as runtime
from flujo.knowledge.postgres_migration import ImportReport
from flujo.knowledge.postgres_runtime import CommandResult, PostgresConfig


def _source(path: Path) -> None:
    db = sqlite3.connect(path)
    db.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, label TEXT)")
    db.execute("INSERT INTO items VALUES (1, 'one')")
    db.commit()
    db.close()


class FakeCursor:
    def __init__(self) -> None:
        self.statements: list[tuple[str, object]] = []
        self.result = (False,)

    def execute(self, sql: str, params=None) -> None:
        self.statements.append((sql, params))
        if sql.startswith("SELECT EXISTS"):
            self.result = (False,)

    def fetchone(self):
        return self.result

    def close(self) -> None:
        pass


class FakeConnection:
    def __init__(self) -> None:
        self.cursors: list[FakeCursor] = []
        self.commits = 0
        self.rollbacks = 0

    def cursor(self) -> FakeCursor:
        cursor = FakeCursor()
        self.cursors.append(cursor)
        return cursor

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1

    def close(self) -> None:
        pass


def _healthy_runner(command, environment):
    sql = command[-1]
    if sql == "SELECT 1;":
        return CommandResult(0, "1\n", "")
    if "current_database()" in sql:
        return CommandResult(0, "mak_knowledge\tmak\n", "")
    if "pg_namespace" in sql:
        return CommandResult(0, "pg_catalog\n", "")
    if "pg_is_in_recovery" in sql:
        return CommandResult(0, "false" + chr(9) + "off\n", "")
    raise AssertionError(sql)


def test_plan_is_read_only_and_serializable(tmp_path: Path) -> None:
    source = tmp_path / "rd.db"
    _source(source)
    before = source.read_bytes()
    result = controller.plan_phase(str(source), "windows_rd")
    assert result.ok is True
    assert result.details["target_schema"] == "staging_rd"
    assert source.read_bytes() == before


def test_architecture_creates_only_non_rd_architecture_schemas() -> None:
    sql = controller._architecture_sql().upper()
    assert "DROP" not in sql
    assert "ALTER SCHEMA" not in sql
    for schema in ("CORE", "MAK", "PORTFOLIO", "RELATIONS", "PRODUCTS", "AUDIT"):
        assert f'"{schema}"' in sql
    assert '"RD"' not in sql


def test_connect_fails_closed_without_psycopg(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "psycopg", None)
    with pytest.raises(controller.OrchestrationError, match="psycopg 3 is required"):
        controller._connect(PostgresConfig())


def test_connect_rejects_password_without_exposing_it() -> None:
    secret = "not-for-output"
    config = PostgresConfig(password=secret)
    with pytest.raises(controller.OrchestrationError) as error:
        controller._connect(config)
    assert secret not in str(error.value)


def test_stage_requires_source_verification_before_and_after_and_target_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "rd.db"
    _source(source)
    connection = FakeConnection()
    source_labels: list[str] = []
    monkeypatch.setattr(
        controller,
        "_source_gate",
        lambda _source, _plan, label: source_labels.append(label) or {"ok": True},
    )
    monkeypatch.setattr(
        controller,
        "apply_plan",
        lambda _connection, plan: ImportReport("windows_rd", plan.target_schema, 1, 1, True, False),
    )
    monkeypatch.setattr(controller, "_ensure_relational_schema", lambda *_args: None)
    monkeypatch.setattr(controller, "_target_gate", lambda *_args: {"target": {"ok": True}, "relational": {"ok": True}})
    monkeypatch.setattr(runtime, "_is_installed", lambda _config: True)

    result = controller.stage_phase(
        str(source),
        "windows_rd",
        PostgresConfig(),
        connection_factory=lambda _config: connection,
        health_runner=_healthy_runner,
    )
    assert result.ok is True
    assert source_labels == ["before stage", "after stage"]
    assert connection.commits == 0


def test_verify_is_non_mutating_and_requires_both_evidence_gates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "rd.db"
    _source(source)
    connection = FakeConnection()
    calls: list[str] = []
    monkeypatch.setattr(controller, "_source_gate", lambda *_args: calls.append("source") or {"ok": True})
    monkeypatch.setattr(controller, "_target_gate", lambda *_args: calls.append("target") or {"ok": True, "relational": {"ok": True}})

    result = controller.verify_phase(
        str(source),
        "windows_rd",
        PostgresConfig(),
        connection_factory=lambda _config: connection,
    )
    assert result.ok is True
    assert calls == ["source", "target"]
    assert connection.commits == 0


def test_promotion_requires_confirmation(tmp_path: Path) -> None:
    source = tmp_path / "rd.db"
    _source(source)
    with pytest.raises(controller.OrchestrationError, match="confirm-promote"):
        controller.promote_phase(str(source), "windows_rd", "m1", connection_factory=lambda _: None)


def test_promotion_renames_once_and_records_parameterized_provenance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "rd.db"
    _source(source)
    connection = FakeConnection()
    monkeypatch.setattr(controller, "_source_gate", lambda *_args: {"ok": True})
    monkeypatch.setattr(controller, "_target_gate", lambda *_args: {"target": {"ok": True}, "relational": {"ok": True}})

    result = controller.promote_phase(
        str(source),
        "windows_rd",
        "migration-1",
        PostgresConfig(),
        connection_factory=lambda _config: connection,
        confirm=True,
    )
    assert result.ok is True
    assert connection.commits == 1
    assert sum('ALTER SCHEMA "staging_rd" RENAME TO "rd"' in sql for cursor in connection.cursors for sql, _ in cursor.statements) == 1
    statements = [item for cursor in connection.cursors for item in cursor.statements]
    assert all("DROP" not in sql.upper() for sql, _ in statements)
    provenance = [params for sql, params in statements if sql.startswith("INSERT INTO")]
    assert provenance and all(params for params in provenance)
    assert all("not-for-output" not in sql for sql, _ in statements)
