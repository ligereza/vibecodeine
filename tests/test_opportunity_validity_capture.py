from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import sqlite3
from pathlib import Path

import pytest

from flujo.knowledge.opportunity_validity_capture import (
    AUTHORITY_GROUP,
    EXPECTED_URLS,
    apply_opportunity_validity_capture,
    build_opportunity_validity_capture,
)
from cultura.mak_research.source_pipeline import SourceCorpusStore


NOW = "2026-08-26T12:00:00Z"
DEADLINE = "2026-09-15"


def _frontier() -> dict:
    opportunity_id = "fondart-investigacion-2027"
    return {
        "schema": "mak-research-frontier-jobs-v1",
        "opportunity_id": opportunity_id,
        "jobs": [{
            "job_id": "job:fondart-validity",
            "candidate_id": "program:arica",
            "opportunity_id": opportunity_id,
            "requirement_ids": [f"source-validity:{opportunity_id}"],
            "research_action_ids": [],
            "question": "Verify current validity from an official source",
            "domain": "general",
            "priority_rank": 1,
            "voi": {"value": None, "status": "unresolved", "numerator": None, "denominator": None},
            "source_policy": "official-source-only",
            "independent_source_groups_required": 1,
            "status": "planned_not_dispatched",
            "dispatch": False,
            "provenance": {"frontier_kind": "refresh_source_validity", "dispatch": False},
        }],
    }


def _receipts(*, captured_at: str = "2026-08-26T10:00:00Z", state: str = "open", deadline: str = DEADLINE) -> list[dict]:
    rows = []
    for role, url in EXPECTED_URLS.items():
        text = f"Fondart Investigacion 2027; state={state}; deadline={deadline}; role={role}"
        digest = hashlib.sha256(text.encode()).hexdigest()
        rows.append({
            "role": role,
            "requested_url": url,
            "final_url": url,
            "status": "captured",
            "http_status": 200,
            "raw_sha256": digest,
            "text_sha256": digest,
            "text": text,
            "retrieved_at": captured_at,
            "license_state": "official_public_source",
        })
    return rows


def test_declared_values_cannot_replace_or_override_captured_content() -> None:
    receipts = _receipts()
    receipts[0]["text"] = "Fondart Investigacion 2027; state=closed; deadline=2026-08-25"
    receipts[0]["text_sha256"] = hashlib.sha256(receipts[0]["text"].encode()).hexdigest()
    receipts[0]["raw_sha256"] = receipts[0]["text_sha256"]
    receipts[0]["opportunity_state"] = "open"
    receipts[0]["deadline"] = DEADLINE
    report = build_opportunity_validity_capture(
        _frontier(), receipts, opportunity_id="fondart-investigacion-2027", now=NOW,
    )
    assert report["valid"] is False
    assert "receipt[0]:declared_state_not_supported_by_content" in report["errors"]
    assert "receipt[0]:declared_deadline_not_supported_by_content" in report["errors"]
    assert report["validity"]["confirmed"] is False


def test_bases_pdf_does_not_need_to_claim_live_state() -> None:
    receipts = _receipts()
    pdf = next(row for row in receipts if row["role"] == "official_bases_pdf")
    pdf["text"] = "Bases de concurso Investigacion Fondart Nacional 2027"
    pdf["text_sha256"] = hashlib.sha256(pdf["text"].encode()).hexdigest()
    pdf["raw_sha256"] = pdf["text_sha256"]
    report = build_opportunity_validity_capture(
        _frontier(), receipts, opportunity_id="fondart-investigacion-2027", now=NOW,
    )
    assert report["valid"] is True
    assert report["validity"]["status"] == "current_verified"


def test_official_index_section_context_extracts_target_state_and_deadline() -> None:
    from flujo.knowledge.opportunity_validity_capture import extract_official_opportunity_observations

    text = (
        "Convocatorias abiertas Organización de muestras - Fondart Nacional 2027 "
        "Plazo de postulación: 16-09-2026 Investigación - Fondart Nacional 2027 "
        "Plazo de postulación: 10-09-2026 Convocatorias cerradas Ferias 2026"
    )
    assert extract_official_opportunity_observations("official_index", text) == {
        "opportunity_state": "open", "deadline": "2026-09-10",
    }


def test_current_official_receipts_close_validity_without_fit_or_promotion() -> None:
    report = build_opportunity_validity_capture(
        _frontier(), _receipts(), opportunity_id="fondart-investigacion-2027", now=NOW,
    )
    assert report["valid"] is True
    assert report["validity"] == {"status": "current_verified", "confirmed": True, "effective_to": DEADLINE}
    assert report["triangulation"]["results"][0]["status"] == "supported_candidate"
    assert report["triangulation"]["results"][0]["independent_source_groups"] == [AUTHORITY_GROUP]
    assert report["additive_evidence"]["opportunity_evidence_proposals"]
    assert report["additive_evidence"]["practice_evidence_proposals"] == []
    assert report["additive_evidence"]["promotion"] == "none"
    assert report["control"] == {
        "network_called": False, "dispatch": False, "publication": False,
        "submission": False, "training_permitted": False,
        "readiness_declared": False, "fit_declared": False,
    }


def test_same_domain_pages_and_pdf_are_one_authority_not_three_groups() -> None:
    report = build_opportunity_validity_capture(
        _frontier(), _receipts(), opportunity_id="fondart-investigacion-2027", now=NOW,
    )
    sources = report["research_result_batch"]["results"][0]["sources"]
    assert len(sources) == 3
    assert {source["source_group"] for source in sources} == {AUTHORITY_GROUP}
    assert report["authority"]["receipt_count"] == 3


def test_recovered_stale_local_capture_never_becomes_current() -> None:
    report = build_opportunity_validity_capture(
        _frontier(), _receipts(captured_at="2026-08-01T10:00:00Z"),
        opportunity_id="fondart-investigacion-2027", now=NOW,
    )
    assert report["valid"] is False
    assert report["validity"] == {"status": "observed_local", "confirmed": False, "effective_to": DEADLINE}
    assert any("capture_stale" in error for error in report["errors"])
    assert report["additive_evidence"]["opportunity_evidence_proposals"] == []


def test_hash_redirect_state_and_deadline_fail_closed() -> None:
    cases = []
    bad_hash = _receipts()
    bad_hash[0]["text_sha256"] = "0" * 64
    cases.append((bad_hash, "text_sha256_mismatch"))
    bad_redirect = _receipts()
    bad_redirect[0]["final_url"] = "https://example.org/fondart"
    cases.append((bad_redirect, "final_url_mismatch"))
    bad_state = _receipts()
    bad_state[1]["text"] = f"Fondart Investigacion 2027; state=closed; deadline={DEADLINE}; role=official_index"
    bad_state[1]["text_sha256"] = hashlib.sha256(bad_state[1]["text"].encode()).hexdigest()
    bad_state[1]["raw_sha256"] = bad_state[1]["text_sha256"]
    cases.append((bad_state, "opportunity_state_conflict"))
    bad_deadline = _receipts()
    bad_deadline[2]["deadline"] = "15-09-2026"
    cases.append((bad_deadline, "declared_deadline_invalid"))
    for receipts, expected in cases:
        report = build_opportunity_validity_capture(
            _frontier(), receipts, opportunity_id="fondart-investigacion-2027", now=NOW,
        )
        assert report["valid"] is False
        assert report["validity"]["confirmed"] is False
        assert any(expected in error for error in report["errors"])


def test_explicit_closed_or_past_deadline_is_expired_not_current() -> None:
    closed = build_opportunity_validity_capture(
        _frontier(), _receipts(state="closed"), opportunity_id="fondart-investigacion-2027", now=NOW,
    )
    past = build_opportunity_validity_capture(
        _frontier(), _receipts(deadline="2026-08-25"), opportunity_id="fondart-investigacion-2027", now=NOW,
    )
    assert closed["validity"]["status"] == "expired"
    assert past["validity"]["status"] == "expired"
    assert closed["control"]["submission"] is False
    assert past["control"]["publication"] is False


def test_cli_is_local_by_default_and_bounded(tmp_path: Path) -> None:
    frontier_path = tmp_path / "frontier.json"
    receipts_path = tmp_path / "receipts.json"
    frontier_path.write_text(json.dumps(_frontier()), encoding="utf-8")
    receipts_path.write_text(json.dumps(_receipts()), encoding="utf-8")
    completed = subprocess.run([
        sys.executable, "tools/capture_opportunity_validity.py",
        "--frontier", str(frontier_path),
        "--opportunity-id", "fondart-investigacion-2027",
        "--receipt", str(receipts_path),
        "--now", NOW,
    ], cwd=Path(__file__).parents[1], capture_output=True, text=True, check=False)
    assert completed.returncode == 0, completed.stderr
    report = json.loads(completed.stdout)
    assert report["valid"] is True
    assert report["control"]["network_called"] is False


def test_cli_hydrates_vigia_receipts_through_existing_capture_store(tmp_path: Path) -> None:
    frontier_path = tmp_path / "frontier.json"
    vigia_path = tmp_path / "vigia-receipts.json"
    capture_root = tmp_path / "capture-root"
    frontier_path.write_text(json.dumps(_frontier()), encoding="utf-8")
    store = SourceCorpusStore(capture_root)
    vigia_rows = []
    for role, url in EXPECTED_URLS.items():
        text = f"Fondart Investigacion 2027; state=open; deadline={DEADLINE}; role={role}"
        digest = hashlib.sha256(text.encode()).hexdigest()
        receipt = store.record_capture({
            "url": url, "text": text, "raw_sha256": digest,
            "backend": "fixture", "status": "captured", "http_status": 200,
            "content_type": "text/plain", "attempts": [], "metadata": {},
        }, requested_backend="fixture")
        vigia_rows.append({
            "plan_id": f"capture-plan:{role}", "url": url,
            "source_ids": [receipt["source_id"]], "item_hashes": [role],
            "titles": [role], "status": "captured",
            "capture_id": receipt["capture_id"], "source_id": receipt["source_id"],
            "text_path": receipt["text_path"], "error": "",
            "provenance": {"source_plan_id": f"capture-plan:{role}", "network_called": True, "promotion": "none"},
        })
    with sqlite3.connect(capture_root / "sources.sqlite") as conn:
        conn.execute("UPDATE source_captures SET retrieved_at=?", ("2026-08-26T10:00:00Z",))
    vigia_path.write_text(json.dumps({"schema": "mak-vigia-capture-receipts-v1", "receipts": vigia_rows}), encoding="utf-8")
    completed = subprocess.run([
        sys.executable, "tools/capture_opportunity_validity.py",
        "--frontier", str(frontier_path),
        "--opportunity-id", "fondart-investigacion-2027",
        "--receipt", str(vigia_path),
        "--capture-root", str(capture_root),
        "--now", NOW,
    ], cwd=Path(__file__).parents[1], capture_output=True, text=True, check=False)
    assert completed.returncode == 0, completed.stderr
    report = json.loads(completed.stdout)
    assert report["valid"] is True
    assert report["validity"]["status"] == "current_verified"
    assert report["control"]["network_called"] is False


def test_input_objects_are_not_mutated() -> None:
    frontier = _frontier()
    receipts = _receipts()
    original = copy.deepcopy((frontier, receipts))
    build_opportunity_validity_capture(
        frontier, receipts, opportunity_id="fondart-investigacion-2027", now=NOW,
    )
    assert (frontier, receipts) == original


def test_valid_capture_updates_only_matching_package_source_validity() -> None:
    report = build_opportunity_validity_capture(
        _frontier(), _receipts(), opportunity_id="fondart-investigacion-2027", now=NOW,
    )
    bases = next(row for row in report["receipts"] if row["role"] == "official_bases_pdf")
    package = {
        "schema": "mak-opportunity-document-package-v1",
        "opportunity_id": "fondart-investigacion-2027",
        "source": {
            "url": bases["final_url"], "sha256": bases["raw_sha256"],
            "validity": {"status": "observed_local", "confirmed": False},
        },
    }
    original = copy.deepcopy(package)
    applied = apply_opportunity_validity_capture(package, report)
    assert applied["source"]["validity"] == {
        "status": "current_verified", "confirmed": True, "effective_to": DEADLINE,
    }
    assert package == original
    bad = copy.deepcopy(package)
    bad["source"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="source_hash_mismatch"):
        apply_opportunity_validity_capture(bad, report)
