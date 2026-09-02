"""Fail-closed orchestration for the SQLite to PostgreSQL RD migration."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
import json
from pathlib import Path
import re
import sys
from typing import Any, Callable, Sequence

ROOT = Path(__file__).resolve().parents[2]
MOTOR_SRC = ROOT / "flujo" / "src"
if MOTOR_SRC.is_dir() and str(MOTOR_SRC) not in sys.path:
    sys.path.insert(0, str(MOTOR_SRC))

from flujo.knowledge.postgres_migration import (
    MigrationPlan,
    apply_plan,
    build_migration_plan,
    quote_identifier,
    verify_source,
    verify_target,
)
from flujo.knowledge.postgres_runtime import (
    CommandResult,
    PostgresConfig,
    TARGET_SCHEMAS,
    _subprocess_runner,
    health_report,
    resolve_config,
)


DEFAULT_STAGE_SCHEMA = "staging_rd"
AUDIT_SCHEMA = "audit"
NON_RD_SCHEMAS = tuple(name for name in TARGET_SCHEMAS if name != "rd")


class OrchestrationError(RuntimeError):
    """Raised when a phase cannot prove its safety preconditions."""


@dataclass(frozen=True)
class PhaseResult:
    phase: str
    ok: bool
    details: dict[str, Any]


def _require_unix_socket(config: PostgresConfig) -> None:
    if config.transport != "unix" or config.password is not None:
        raise OrchestrationError("migration requires passwordless Unix-socket PostgreSQL")


def _connect(config: PostgresConfig) -> Any:
    """Open psycopg 3 on the MAK Unix socket, never with a password."""

    _require_unix_socket(config)
    try:
        import psycopg
    except ImportError as exc:
        raise OrchestrationError(
            "psycopg 3 is required for migration stage, verify, and promote"
        ) from exc
    try:
        return psycopg.connect(
            dbname=config.database,
            user=config.user,
            host=config.socket_dir,
        )
    except Exception as exc:
        raise OrchestrationError("PostgreSQL Unix-socket connection failed") from exc


def _resolved_config(config: PostgresConfig | None) -> PostgresConfig:
    return config if config is not None else resolve_config()


def _plan(source: str, source_id: str) -> MigrationPlan:
    return build_migration_plan(source, DEFAULT_STAGE_SCHEMA, source_id=source_id)


def _source_summary(plan: MigrationPlan) -> dict[str, Any]:
    primary = plan.source_files[0]
    return {
        "source_id": plan.source_id,
        "source_path": plan.source_path,
        "source_sha256": primary.sha256,
        "source_bytes": primary.size,
        "table_count": len(plan.tables),
        "tables": [
            {"name": table.name, "row_count": table.row_count, "row_hash": table.row_hash}
            for table in plan.tables
        ],
    }


def _architecture_sql() -> str:
    """Create only the six non-RD architecture schemas before the rename."""

    return "\n".join(
        f"CREATE SCHEMA IF NOT EXISTS {quote_identifier(name)};"
        for name in NON_RD_SCHEMAS
    )


def _architecture_statements() -> tuple[str, ...]:
    return tuple(
        f"CREATE SCHEMA IF NOT EXISTS {quote_identifier(name)}"
        for name in NON_RD_SCHEMAS
    )


def _audit_sql(plan: MigrationPlan, migration_id: str) -> str:
    """Return audit DDL only; values are always bound separately."""

    del plan, migration_id
    return "\n".join(
        (
            'CREATE TABLE IF NOT EXISTS "audit"."source_artifacts" ('
            "source_id TEXT PRIMARY KEY, source_path TEXT NOT NULL, "
            "source_sha256 TEXT NOT NULL, source_bytes BIGINT NOT NULL, "
            "source_files_json TEXT NOT NULL, status TEXT NOT NULL, "
            "recorded_at TIMESTAMPTZ NOT NULL DEFAULT now());",
            'CREATE TABLE IF NOT EXISTS "audit"."migrations" ('
            "migration_id TEXT PRIMARY KEY, source_id TEXT NOT NULL, "
            "source_sha256 TEXT NOT NULL, staging_schema TEXT NOT NULL, "
            "target_schema TEXT NOT NULL, plan_json TEXT NOT NULL, "
            "status TEXT NOT NULL, recorded_at TIMESTAMPTZ NOT NULL DEFAULT now());",
        )
    )


def _audit_statements(plan: MigrationPlan, migration_id: str) -> tuple[tuple[str, tuple[Any, ...]], ...]:
    source = plan.source_files[0]
    source_files = json.dumps([item.__dict__ for item in plan.source_files], ensure_ascii=True, sort_keys=True)
    return (
        (
            'CREATE TABLE IF NOT EXISTS "audit"."source_artifacts" ('
            "source_id TEXT PRIMARY KEY, source_path TEXT NOT NULL, "
            "source_sha256 TEXT NOT NULL, source_bytes BIGINT NOT NULL, "
            "source_files_json TEXT NOT NULL, status TEXT NOT NULL, "
            "recorded_at TIMESTAMPTZ NOT NULL DEFAULT now())",
            (),
        ),
        (
            'CREATE TABLE IF NOT EXISTS "audit"."migrations" ('
            "migration_id TEXT PRIMARY KEY, source_id TEXT NOT NULL, "
            "source_sha256 TEXT NOT NULL, staging_schema TEXT NOT NULL, "
            "target_schema TEXT NOT NULL, plan_json TEXT NOT NULL, "
            "status TEXT NOT NULL, recorded_at TIMESTAMPTZ NOT NULL DEFAULT now())",
            (),
        ),
        (
            'INSERT INTO "audit"."source_artifacts" '
            "(source_id, source_path, source_sha256, source_bytes, source_files_json, status) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (plan.source_id, plan.source_path, source.sha256, source.size, source_files, "promoted"),
        ),
        (
            'INSERT INTO "audit"."migrations" '
            "(migration_id, source_id, source_sha256, staging_schema, target_schema, plan_json, status) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (migration_id, plan.source_id, source.sha256, DEFAULT_STAGE_SCHEMA, "rd", plan.to_json(), "promoted"),
        ),
    )


def _source_gate(source: str, plan: MigrationPlan, label: str) -> dict[str, Any]:
    report = verify_source(source, plan)
    if not report.ok or not report.source_unchanged:
        raise OrchestrationError(f"source verification failed {label}: " + "; ".join(report.errors))
    return report.as_dict()


def _safe_default(value: str) -> str:
    candidate = value.strip()
    if not re.fullmatch(
        r"(?:-?\d+(?:\.\d+)?|NULL|CURRENT_(?:DATE|TIME|TIMESTAMP)|'(?:''|[^'])*')",
        candidate,
        flags=re.IGNORECASE,
    ):
        raise OrchestrationError(f"unsupported SQLite default expression: {value}")
    return candidate


def _fk_name(table: str, key_id: int) -> str:
    return f"fk_{table}_{key_id}"


def _ensure_relational_schema(connection: Any, plan: MigrationPlan) -> None:
    """Complete the relational elements captured by the migration plan."""

    cursor = connection.cursor()
    try:
        cursor.execute("BEGIN")
        for table in plan.tables:
            for foreign_key in table.foreign_keys:
                source_columns = ", ".join(quote_identifier(item) for item in foreign_key.source_columns)
                target_columns = ", ".join(quote_identifier(item) for item in foreign_key.target_columns)
                actions = []
                for keyword, action in (("ON UPDATE", foreign_key.on_update), ("ON DELETE", foreign_key.on_delete)):
                    if action not in {"NO ACTION", "RESTRICT", "CASCADE", "SET NULL", "SET DEFAULT"}:
                        raise OrchestrationError(f"unsupported foreign-key action: {action}")
                    if action != "NO ACTION":
                        actions.append(f"{keyword} {action}")
                cursor.execute(
                    f"ALTER TABLE {quote_identifier(DEFAULT_STAGE_SCHEMA)}.{quote_identifier(table.name)} "
                    f"ADD CONSTRAINT {quote_identifier(_fk_name(table.name, foreign_key.id))} "
                    f"FOREIGN KEY ({source_columns}) REFERENCES "
                    f"{quote_identifier(DEFAULT_STAGE_SCHEMA)}.{quote_identifier(foreign_key.target_table)} "
                    f"({target_columns}) {' '.join(actions)}"
                )
            for index in table.indexes:
                if index.name.startswith("sqlite_autoindex_") or index.origin in {"pk", "u"}:
                    continue
                if not index.columns:
                    raise OrchestrationError(f"index has no columns: {index.name}")
                columns = ", ".join(quote_identifier(item) for item in index.columns)
                unique = "UNIQUE " if index.unique else ""
                cursor.execute(
                    f"CREATE {unique}INDEX {quote_identifier(index.name)} ON "
                    f"{quote_identifier(DEFAULT_STAGE_SCHEMA)}.{quote_identifier(table.name)} ({columns})"
                )
            for column in table.columns:
                if column.default_sql is not None:
                    cursor.execute(
                        f"ALTER TABLE {quote_identifier(DEFAULT_STAGE_SCHEMA)}.{quote_identifier(table.name)} "
                        f"ALTER COLUMN {quote_identifier(column.name)} SET DEFAULT {_safe_default(column.default_sql)}"
                    )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()


def _relational_schema_evidence(connection: Any, plan: MigrationPlan) -> dict[str, Any]:
    """Compare columns, nullability, defaults, primary keys, foreign keys, and indexes."""

    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT c.relname, a.attname, format_type(a.atttypid, a.atttypmod), "
            "a.attnotnull, COALESCE(pg_get_expr(ad.adbin, ad.adrelid), '') "
            "FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
            "JOIN pg_attribute a ON a.attrelid = c.oid "
            "LEFT JOIN pg_attrdef ad ON ad.adrelid = c.oid AND ad.adnum = a.attnum "
            "WHERE n.nspname = %s AND c.relkind = 'r' AND a.attnum > 0 "
            "AND NOT a.attisdropped ORDER BY c.relname, a.attnum",
            (plan.target_schema,),
        )
        actual_columns = tuple(cursor.fetchall())
        cursor.execute(
            "SELECT tc.table_name, kcu.column_name, kcu.ordinal_position "
            "FROM information_schema.table_constraints tc "
            "JOIN information_schema.key_column_usage kcu "
            "ON kcu.constraint_schema = tc.constraint_schema "
            "AND kcu.constraint_name = tc.constraint_name "
            "AND kcu.table_name = tc.table_name "
            "WHERE tc.table_schema = %s AND tc.constraint_type = 'PRIMARY KEY' "
            "ORDER BY tc.table_name, kcu.ordinal_position",
            (plan.target_schema,),
        )
        actual_primary_keys = tuple(cursor.fetchall())
        cursor.execute(
            "SELECT tc.table_name, kcu.column_name, ccu.table_name, ccu.column_name, kcu.ordinal_position "
            "FROM information_schema.table_constraints tc "
            "JOIN information_schema.key_column_usage kcu ON kcu.constraint_schema = tc.constraint_schema "
            "AND kcu.constraint_name = tc.constraint_name AND kcu.table_name = tc.table_name "
            "JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_schema = tc.constraint_schema "
            "AND ccu.constraint_name = tc.constraint_name "
            "WHERE tc.table_schema = %s AND tc.constraint_type = 'FOREIGN KEY' "
            "ORDER BY tc.table_name, kcu.ordinal_position",
            (plan.target_schema,),
        )
        actual_foreign_keys = tuple(cursor.fetchall())
        cursor.execute(
            "SELECT tablename, indexname, indexdef FROM pg_indexes "
            "WHERE schemaname = %s ORDER BY tablename, indexname",
            (plan.target_schema,),
        )
        actual_indexes = tuple(cursor.fetchall())
    except Exception as exc:
        return {"ok": False, "errors": (f"relational schema evidence failed: {exc}",)}
    finally:
        cursor.close()

    expected_columns = tuple(
        (
            table.name,
            column.name,
            column.postgres_type.lower(),
            column.not_null or column.name in table.primary_key,
            (column.default_sql or "").strip(),
        )
        for table in plan.tables
        for column in table.columns
    )
    normalized_actual_columns = tuple(
        (str(table), str(column), str(kind).lower(), bool(not_null), str(default or "").strip(" ()"))
        for table, column, kind, not_null, default in actual_columns
    )
    expected_primary_keys = tuple(
        (table.name, column, position)
        for table in plan.tables
        for position, column in enumerate(table.primary_key, start=1)
    )
    expected_foreign_keys = tuple(
        (table.name, source, foreign_key.target_table, target, position)
        for table in plan.tables
        for foreign_key in table.foreign_keys
        for position, (source, target) in enumerate(
            zip(foreign_key.source_columns, foreign_key.target_columns), start=1
        )
    )
    expected_index_names = tuple(
        sorted(
            index.name
            for table in plan.tables
            for index in table.indexes
            if not index.name.startswith("sqlite_autoindex_") and index.origin not in {"pk", "u"}
        )
    )
    actual_index_names = tuple(sorted(str(row[1]) for row in actual_indexes if not str(row[1]).endswith("_pkey")))
    errors = []
    if normalized_actual_columns != expected_columns:
        errors.append("target relational columns differ from migration plan")
    if tuple(actual_primary_keys) != expected_primary_keys:
        errors.append("target primary-key evidence differs from migration plan")
    if tuple(actual_foreign_keys) != expected_foreign_keys:
        errors.append("target foreign-key evidence differs from migration plan")
    if actual_index_names != expected_index_names:
        errors.append("target index evidence differs from migration plan")
    return {
        "ok": not errors,
        "errors": tuple(errors),
        "expected_columns": len(expected_columns),
        "actual_columns": len(normalized_actual_columns),
        "expected_primary_keys": len(expected_primary_keys),
        "expected_foreign_keys": len(expected_foreign_keys),
        "expected_indexes": len(expected_index_names),
    }


def _target_gate(connection: Any, plan: MigrationPlan, label: str) -> dict[str, Any]:
    target = verify_target(connection, plan)
    if not target.ok:
        raise OrchestrationError(f"target verification failed {label}: " + "; ".join(target.errors))
    relational = _relational_schema_evidence(connection, plan)
    if not relational["ok"]:
        raise OrchestrationError(
            f"relational schema verification failed {label}: " + "; ".join(relational["errors"])
        )
    return {"target": target.as_dict(), "relational": relational}


def plan_phase(source: str, source_id: str, output: str | None = None) -> PhaseResult:
    plan = _plan(source, source_id)
    payload = plan.as_dict()
    if output:
        Path(output).write_text(
            json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n",
            encoding="ascii",
        )
    return PhaseResult("plan", True, payload)


def stage_phase(
    source: str,
    source_id: str,
    config: PostgresConfig | None = None,
    *,
    connection_factory: Callable[[PostgresConfig], Any] = _connect,
    health_runner: Callable[[Sequence[str], dict[str, str]], CommandResult] = _subprocess_runner,
) -> PhaseResult:
    plan = _plan(source, source_id)
    before = _source_gate(source, plan, "before stage")
    resolved = _resolved_config(config)
    _require_unix_socket(resolved)
    # The target architecture is intentionally absent before promotion. Probe
    # connectivity/primary state against pg_catalog, not against future schemas.
    health = health_report(
        replace(resolved, schemas=("pg_catalog",)),
        runner=health_runner,
    )
    if not health.connectable or not health.primary_writer:
        raise OrchestrationError("PostgreSQL is not a writable primary")
    connection = connection_factory(resolved)
    try:
        imported = apply_plan(connection, plan)
        _ensure_relational_schema(connection, plan)
        after = _source_gate(source, plan, "after stage")
        target = _target_gate(connection, plan, "after stage")
    finally:
        connection.close()
    return PhaseResult(
        "stage",
        imported.committed,
        {"source_before": before, "source_after": after, "import": imported.as_dict(), **target},
    )


def verify_phase(
    source: str,
    source_id: str,
    config: PostgresConfig | None = None,
    *,
    connection_factory: Callable[[PostgresConfig], Any] = _connect,
) -> PhaseResult:
    plan = _plan(source, source_id)
    source_report = _source_gate(source, plan, "during verify")
    resolved = _resolved_config(config)
    _require_unix_socket(resolved)
    connection = connection_factory(resolved)
    try:
        target = _target_gate(connection, plan, "during verify")
    finally:
        connection.close()
    return PhaseResult("verify", True, {"source": source_report, **target})


def promote_phase(
    source: str,
    source_id: str,
    migration_id: str,
    config: PostgresConfig | None = None,
    *,
    connection_factory: Callable[[PostgresConfig], Any] = _connect,
    confirm: bool = False,
) -> PhaseResult:
    if not confirm:
        raise OrchestrationError("promotion requires --confirm-promote")
    plan = _plan(source, source_id)
    source_report = _source_gate(source, plan, "before promote")
    resolved = _resolved_config(config)
    _require_unix_socket(resolved)
    connection = connection_factory(resolved)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = %s)", ("rd",))
        if cursor.fetchone()[0]:
            raise OrchestrationError("promotion refused: rd schema already exists")
        target = _target_gate(connection, plan, "before promote")
        cursor.close()
        connection.rollback()
        cursor = connection.cursor()
        cursor.execute("BEGIN")
        for statement in _architecture_statements():
            cursor.execute(statement)
        cursor.execute('ALTER SCHEMA "staging_rd" RENAME TO "rd"')
        for statement, params in _audit_statements(plan, migration_id):
            cursor.execute(statement, params)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()
    return PhaseResult(
        "promote",
        True,
        {"source": source_report, "migration_id": migration_id, "target_schema": "rd", **target},
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("plan", "stage", "verify", "promote"))
    parser.add_argument("source")
    parser.add_argument("--source-id", default="windows_rd")
    parser.add_argument("--output")
    parser.add_argument("--migration-id", default="rd-windows-promote-v1")
    parser.add_argument("--confirm-promote", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.phase == "plan":
            result = plan_phase(args.source, args.source_id, args.output)
        elif args.phase == "stage":
            result = stage_phase(args.source, args.source_id)
        elif args.phase == "verify":
            result = verify_phase(args.source, args.source_id)
        else:
            result = promote_phase(args.source, args.source_id, args.migration_id, confirm=args.confirm_promote)
        print(json.dumps({"phase": result.phase, "ok": result.ok, "details": result.details}, ensure_ascii=True, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
