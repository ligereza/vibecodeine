"""Contract tests for one explicit, idempotent research-job continuation."""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
from flujo.knowledge.research_job_continuation import confirm_research_extraction, license_compatibility_plan, license_review, license_source_review, normalize_dry_run, normalize_plan, normalize_readiness, resume_research_job  # noqa: E402


def _seed_captured_job(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE domain_adapters (
                id INTEGER PRIMARY KEY, slug TEXT, label TEXT,
                description TEXT, input_examples TEXT, source_policy TEXT,
                constraint_policy TEXT
            );
            CREATE TABLE research_jobs (
                id INTEGER PRIMARY KEY, question TEXT, domain TEXT,
                adapter_id INTEGER, status TEXT, next_process TEXT,
                created_at TEXT
            );
            CREATE TABLE job_steps (
                id INTEGER PRIMARY KEY, job_id INTEGER, step_order INTEGER,
                process_key TEXT, input_semantics TEXT, output_semantics TEXT,
                status TEXT, provider_policy TEXT
            );
            CREATE TABLE job_sources (
                id INTEGER PRIMARY KEY, job_id INTEGER, stage TEXT,
                query TEXT, discovery_provider TEXT, rank INTEGER,
                url TEXT, title TEXT, snippet TEXT, capture_provider TEXT,
                capture_status TEXT, http_status INTEGER, content_type TEXT,
                raw_sha256 TEXT, text_sha256 TEXT, text_path TEXT,
                captured_at TEXT, license_state TEXT, license_evidence TEXT,
                credits_estimate REAL, notes TEXT
            );
            CREATE TABLE audit_events (
                id INTEGER PRIMARY KEY, event_type TEXT, object_type TEXT,
                object_id INTEGER, detail TEXT, created_at TEXT
            );
            """
        )
        conn.execute("INSERT INTO domain_adapters VALUES (1,'curatoria','Curatoria','d','e','s','c')")
        conn.execute(
            "INSERT INTO research_jobs VALUES (3,'¿Qué demuestra este job?','cultura',1,'captured','extract','2026-09-13T00:00:00+00:00')"
        )
        for step_id, (process, status) in enumerate((
            ("discover", "done"), ("capture", "done"), ("extract", "pending"),
        ), start=1):
            conn.execute(
                "INSERT INTO job_steps VALUES (?,?,?,?,?,?,?,?)",
                (step_id, 3, step_id, process, "input", "output", status, "local"),
            )
        conn.execute(
            "INSERT INTO job_sources VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (1, 3, "capture", "q", "local", 1, "https://example.test/source",
             "Fuente de prueba", "snippet", "local", "captured", 200,
             "text/html", "raw-hash", "text-hash", "logical/source.txt",
             "2026-09-13T00:00:00+00:00", "reviewed", "fixture", 0.0, ""),
        )
        conn.commit()


@pytest.mark.flujo
def test_extract_continuation_writes_checkpoint_and_replays_idempotently(tmp_path: Path):
    db_path = tmp_path / "research.sqlite"
    output_root = tmp_path / "outputs"
    _seed_captured_job(db_path)

    first, code = resume_research_job(
        db_path, output_root, job_id=3, expected_process="extract",
        request_id="test-q790",
    )
    assert code == 200
    assert first["schema"] == "mak-research-job-continuation-v1"
    assert first["status"] == "COMPLETED"
    assert first["idempotent_replay"] is False
    assert first["control"] == {
        "database_write": True, "decision_write": False,
        "promotion": "none", "publication": False,
    }
    output_path = output_root / "3" / "continuations" / "test-q790.json"
    assert output_path.is_file()
    assert json.loads(output_path.read_text(encoding="utf-8"))["model_calls"] == 0

    with sqlite3.connect(db_path) as conn:
        before_readiness = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
        before_job = conn.execute("SELECT status,next_process FROM research_jobs WHERE id=3").fetchone()
    readiness, readiness_code = normalize_readiness(db_path, job_id=3)
    with sqlite3.connect(db_path) as conn:
        after_readiness = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
        after_job = conn.execute("SELECT status,next_process FROM research_jobs WHERE id=3").fetchone()
    assert readiness_code == 200
    assert readiness["read_only"] is True
    assert readiness["human_attestation"]["present"] is False
    assert readiness["human_attestation"]["actor_kind"] is None
    assert readiness["input_sha256"] == first["input_sha256"]
    assert readiness["execution"]["normalize_execution"] is False
    assert after_readiness == before_readiness
    assert after_job == before_job

    plan, plan_code = normalize_plan(db_path, job_id=3)
    assert plan_code == 200
    assert plan["read_only"] is True
    assert plan["plan"]["record_count"] == 1
    assert plan["plan"]["preview"][0]["candidate_kind"] == "unmapped_source_record"
    assert plan["plan"]["semantic_claims_created"] is False
    assert plan["execution_allowed"] is False
    assert plan["control"]["state_advance"] is False
    assert readiness["normalization_allowed"] is False
    assert readiness["control"]["state_advance"] is False

    dry_run, dry_run_code = normalize_dry_run(db_path, job_id=3)
    assert dry_run_code == 200
    assert dry_run["read_only"] is True
    assert dry_run["dry_run"]["records"] == 1
    assert dry_run["dry_run"]["semantic_transform_performed"] is False
    assert dry_run["dry_run"]["database_rows_created"] == 0
    assert dry_run["execution"]["attempted"] is False
    assert dry_run["control"]["state_advance"] is False

    licenses, licenses_code = license_review(db_path, job_id=3)
    assert licenses_code == 200
    assert licenses["read_only"] is True
    assert licenses["sources"][0]["verification"] == "pending_review"
    assert licenses["ready_for_attestation"] is False
    assert licenses["control"]["database_write"] is False

    source_review, source_review_code = license_source_review(db_path, job_id=3)
    assert source_review_code == 409
    assert source_review["error"] == "license_source_review_invalid"

    compatibility, compatibility_code = license_compatibility_plan(db_path, job_id=3)
    assert compatibility_code == 409
    assert compatibility["error"] == "license_source_review_invalid"

    second, replay_code = resume_research_job(
        db_path, output_root, job_id=3, expected_process="extract",
        request_id="test-q790",
    )
    assert replay_code == 200
    assert second["idempotent_replay"] is True
    assert second["input_sha256"] == first["input_sha256"]

    confirmation, confirmation_code = confirm_research_extraction(
        db_path, output_root, job_id=3, actor="mak-operator",
        input_sha256=first["input_sha256"], request_id="confirm-q800",
    )
    assert confirmation_code == 200
    assert confirmation["schema"] == "mak-research-human-confirmation-v1"
    assert confirmation["status"] == "CONFIRMED"
    assert confirmation["actor_kind"] == "human"
    assert confirmation["execution"]["process_advanced"] is False
    assert confirmation["execution"]["normalize_execution"] is False
    assert confirmation["control"]["decision_write"] is False
    assert confirmation["control"]["state_advance"] is False

    confirmed_readiness, confirmed_readiness_code = normalize_readiness(db_path, job_id=3)
    assert confirmed_readiness_code == 200
    assert confirmed_readiness["human_attestation"]["matches_input_sha256"] is True
    assert confirmed_readiness["human_attestation"]["actor_kind"] == "human"
    assert confirmed_readiness["normalization_allowed"] is False

    confirmed_plan, confirmed_plan_code = normalize_plan(db_path, job_id=3)
    assert confirmed_plan_code == 200
    assert confirmed_plan["human_attestation"]["present"] is True
    assert confirmed_plan["execution_allowed"] is False

    confirmation_replay, replay_confirmation_code = confirm_research_extraction(
        db_path, output_root, job_id=3, actor="mak-operator",
        input_sha256=first["input_sha256"], request_id="confirm-q800",
    )
    assert replay_confirmation_code == 200
    assert confirmation_replay["idempotent_replay"] is True

    with sqlite3.connect(db_path) as conn:
        job = conn.execute("SELECT status,next_process FROM research_jobs WHERE id=3").fetchone()
        receipt_count = conn.execute("SELECT COUNT(*) FROM research_continuation_receipts").fetchone()[0]
        confirmation_count = conn.execute("SELECT COUNT(*) FROM research_extraction_confirmations").fetchone()[0]
        step = conn.execute("SELECT status FROM job_steps WHERE job_id=3 AND process_key='extract'").fetchone()[0]
    assert job == ("extracted", "normalize")
    assert step == "done"
    assert receipt_count == 1
    assert confirmation_count == 1


@pytest.mark.flujo
def test_continuation_refuses_wrong_next_process_without_checkpoint(tmp_path: Path):
    db_path = tmp_path / "research.sqlite"
    _seed_captured_job(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute("UPDATE research_jobs SET next_process='normalize' WHERE id=3")
        conn.commit()

    result, code = resume_research_job(
        db_path, tmp_path / "outputs", job_id=3, expected_process="extract",
        request_id="test-mismatch",
    )
    assert code == 409
    assert result["error"] == "next_process_mismatch"
    assert not (tmp_path / "outputs").exists()
