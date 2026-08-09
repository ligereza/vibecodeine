import json
import subprocess
import sys

from cultura.mak_plataforma import ledger
from cultura.mak_plataforma import tandas


def test_work_envelope_is_shared_and_validated():
    work = ledger.build_work_envelope(
        "portfolio_record:sample", "portfolio:sample", "obra",
        "triangular registro audiovisual", "registro", "aws",
        sources=["instagram:sample"], status="awaiting_review",
        identity={"kind": "record", "source_id": "instagram:sample",
                  "entities": {"artist": ["DrefQuila"]}},
        fallback_chain=["ollama", "local_deterministic"])

    assert ledger.validate_work_envelope(work) == (True, [])
    assert work["identity"]["kind"] == "record"
    assert work["fallback_chain"] == ["ollama", "local_deterministic"]


def test_append_item_accepts_typed_domain_record(tmp_path):
    path = tmp_path / "common_ledger.jsonl"
    ok, errors, row = ledger.append_item({
        "domain": "rd",
        "type": "evidence",
        "claim": "BCN page names the Chilean legal requirement",
        "evidence": ["https://www.bcn.cl/example"],
        "files": ["docs/rd/example.md"],
        "confidence": "high",
        "action": "verify_source",
    }, path=str(path), source="watsonx")
    assert ok is True
    assert errors == []
    assert json.loads(path.read_text(encoding="utf-8")) == row
    assert row["lane"] == "trabajo"
    assert row["decision"] == "revisar"
    assert row["work"]["status"] == "legacy_unknown"


def test_external_batch_preserves_work_identity(tmp_path):
    path = tmp_path / "common_ledger.jsonl"
    payload = {"work": {
        "schema": "mak-work-v1", "work_id": "rd_evidence:round-1",
        "parent_task": "brief:round-1", "lane": "trabajo",
        "purpose": "verificar una fuente oficial", "format": "research",
        "created_at": "2026-08-08T00:00:00Z", "provider": "watsonx",
        "sources": ["docs/brief.md"], "status": "awaiting_review",
    }, "items": [{
        "claim": "source exists", "evidence": ["https://official.example"],
        "files": [], "confidence": "high", "action": "verify_source",
        "reject_reason": "",
    }]}
    rows, errors = tandas.append_common_ledger(
        payload, "rd_evidence", path=str(path), source="watsonx")
    assert errors == []
    assert rows[0]["work"]["work_id"] == "rd_evidence:round-1"
    assert rows[0]["work"]["parent_task"] == "brief:round-1"


def test_portfolio_candidate_from_review_stays_human_review(tmp_path):
    path = tmp_path / "common_ledger.jsonl"
    candidate = {
        "entity_id": "post-a",
        "format": "media",
        "triage": {
            "provider": "aws",
            "verdict": "accept",
            "candidate_relations": {"artist": ["ober.byg"]},
        },
    }

    ok, errors, row = ledger.portfolio_candidate_from_review(
        candidate, path=str(path))

    assert ok is True
    assert errors == []
    assert row["domain"] == "portfolio"
    assert row["decision"] == "revisar"
    assert row["owner"] == "human"
    assert row["work"]["status"] == "candidate_external"
    assert row["work"]["identity"]["entities"]["artist"] == ["ober.byg"]


def test_external_portfolio_record_surfaces_as_pending_candidate():
    row = ledger.external_item_to_ledger({
        "claim": "registro audiovisual candidato",
        "evidence": ["manifest.json"],
        "files": ["/portfolio-media/stories/2026/record.jpg"],
        "confidence": "high",
        "action": "triangulate",
        "format": "registro",
        "product": {
            "record_kind": "story_record",
            "relations": "sin_relaciones_observables",
            "unknowns": "evento_no_confirmado",
        },
    }, "portfolio_record", {"provider": "aws"})

    candidate = row["metadata"]["portfolio_candidate"]
    assert candidate["entity_id"] == "record.jpg"
    assert candidate["triage"]["verdict"] == "accept"
    assert row["decision"] == "revisar"
    assert row["next_action"] == "triangulate"


def test_portfolio_candidate_from_review_rejects_nonaccepted_verdict(tmp_path):
    path = tmp_path / "common_ledger.jsonl"
    ok, errors, row = ledger.portfolio_candidate_from_review({
        "entity_id": "post-a",
        "triage": {"verdict": "revise", "candidate_relations": {"artist": ["x"]}},
    }, path=str(path))

    assert ok is False
    assert errors == ["candidate_not_traceable"]
    assert row is None


def test_typed_work_preserves_identity_entities_and_trace_status(tmp_path):
    path = tmp_path / "common_ledger.jsonl"
    ok, errors, row = ledger.append_item({
        "domain": "iskvw",
        "type": "evidence",
        "claim": "registro asociado al evento",
        "evidence": ["iskvw/datos/campo.json"],
        "files": ["iskvw/datos/campo.json"],
        "confidence": "medium",
        "action": "curate",
        "work": {
            "work_id": "portfolio:post-1",
            "parent_task": "portfolio:import-1",
            "lane": "obra",
            "purpose": "agrupar un registro visual",
            "format": "curatoria",
            "created_at": "2026-08-08T23:00:00Z",
            "provider": "watsonx",
            "sources": ["instagram:post-1"],
            "status": "awaiting_review",
            "identity": {
                "kind": "record",
                "source_id": "instagram:post-1",
                "parent_id": "portfolio:import-1",
                "entities": {"artist": ["drefquila"], "event": ["Lolla"]},
                "event_date": "2025-03-15",
            },
        },
    }, path=str(path), source="watsonx")
    assert ok is True
    assert errors == []
    assert row["trace_status"] == "declared"
    assert row["work"]["identity"]["kind"] == "record"
    assert row["work"]["identity"]["entities"]["artist"] == ["drefquila"]


def test_legacy_work_is_marked_without_inventing_identity(tmp_path):
    path = tmp_path / "common_ledger.jsonl"
    ok, errors, row = ledger.append_item({
        "domain": "mak", "type": "evidence", "claim": "old report",
        "evidence": [], "files": [], "confidence": "unknown",
        "action": "archive",
    }, path=str(path))
    assert ok is True
    assert errors == []
    assert row["trace_status"] == "legacy_unknown"
    assert row["work"]["identity"]["kind"] == "legacy_unknown"


def test_decision_queue_rejects_unknown_lane_or_decision():
    ok, errors, _row = ledger.validate_item({
        "domain": "rd", "type": "task", "claim": "x",
        "evidence": [], "files": [], "confidence": "unknown",
        "action": "verify_source", "lane": "publico", "decision": "inventar",
    })

    assert ok is False
    assert "bad_lane" in errors
    assert "bad_decision" in errors


def test_reject_requires_reason_and_valid_domain_action():
    ok, errors, _row = ledger.validate_item({
        "domain": "iskvw",
        "type": "reject",
        "claim": "",
        "evidence": [],
        "files": [],
        "confidence": "low",
        "action": "verify_source",
        "reject_reason": "",
    })
    assert ok is False
    assert "bad_action_for_domain" in errors
    assert "reject_without_reason" in errors


def test_secret_markers_are_redacted(tmp_path):
    path = tmp_path / "common_ledger.jsonl"
    ok, _errors, row = ledger.append_item({
        "domain": "repo",
        "type": "artifact",
        "claim": "api_key should never be persisted",
        "evidence": ["token bearer abc"],
        "files": [],
        "confidence": "medium",
        "action": "test",
    }, path=str(path))
    assert ok is True
    assert row["claim"] == "[redacted]"
    assert row["evidence"] == ["[redacted]"]


def test_external_batch_items_enter_common_ledger(tmp_path):
    path = tmp_path / "common_ledger.jsonl"
    payload = {"items": [{
        "claim": "old MAK reports need quarantine",
        "evidence": ["~/research/informes/x.md"],
        "files": ["cultura/mak_plataforma/trabajo.py"],
        "confidence": "high",
        "action": "archive",
        "reject_reason": "",
    }]}
    rows, errors = tandas.append_common_ledger(
        payload, "mak_quality", path=str(path), source="aws")
    assert errors == []
    assert rows[0]["domain"] == "mak"
    assert rows[0]["type"] == "evidence"
    assert rows[0]["action"] == "archive"


def test_portfolio_record_keeps_record_domain_and_triangulation_action(tmp_path):
    path = tmp_path / "common_ledger.jsonl"
    payload = {"work": {
        "schema": "mak-work-v1", "work_id": "portfolio_record:story01",
        "parent_task": "batch:story01", "lane": "obra",
        "purpose": "triage story record", "format": "external_batch",
        "created_at": "2026-08-09T00:00:00Z", "provider": "aws",
        "sources": ["story-queue.json"], "status": "awaiting_review",
        "identity": {"schema": "mak-identity-v1", "kind": "record",
                     "source_id": "portfolio_record:story01",
                     "parent_id": "batch:story01", "entities": {},
                     "event_date": ""}}, "items": [{
        "claim": "registro audiovisual candidato",
        "evidence": ["story-contact-sheet.jpg"],
        "files": ["story-contact-sheet.jpg"], "confidence": "medium",
        "action": "triangulate", "reject_reason": "",
    }]}
    rows, errors = tandas.append_common_ledger(
        payload, "portfolio_record", path=str(path), source="aws")
    assert errors == []
    assert rows[0]["domain"] == "portfolio"
    assert rows[0]["lane"] == "obra"
    assert rows[0]["action"] == "triangulate"
    assert rows[0]["work"]["identity"]["kind"] == "record"


def test_external_product_metadata_survives_in_common_ledger(tmp_path):
    path = tmp_path / "common_ledger.jsonl"
    payload = {"items": [{
        "claim": "registro audiovisual candidato",
        "evidence": ["story-contact-sheet.jpg"],
        "files": ["story-contact-sheet.jpg"], "confidence": "medium",
        "action": "triangulate", "reject_reason": "",
        "format": "registro", "evidence_kind": "media_metadata",
        "product": {"record_kind": "story_record",
                     "relations": {"artist": "ober"},
                     "unknowns": ["venue por confirmar"]},
    }]}
    rows, errors = tandas.append_common_ledger(
        payload, "portfolio_record", path=str(path), source="aws")
    assert errors == []
    assert rows[0]["metadata"]["product"]["record_kind"] == "story_record"
    assert rows[0]["metadata"]["product"]["relations"]["artist"] == "ober"


def test_review_ledger_preserves_judge_trace_metadata(tmp_path):
    path = tmp_path / "common_ledger.jsonl"
    review = {
        "schema": "mak-local-review-v1",
        "verdict": "revise",
        "domain": "rd",
        "reason": "missing primary source",
        "risks": [],
        "missing_evidence": ["official source"],
        "next_action": "verify source",
    }
    ok, errors, row = ledger.append_review(
        review, "rd_evidence", path=str(path), source="local_review:watsonx",
        metadata={"provider": "watsonx", "reviewer": "deterministic",
                  "fallback": True, "profile_verdict": "revise",
                  "work": {"work_id": "rd_evidence:review-1",
                           "identity": {"kind": "report",
                                        "source_id": "rd_evidence:review-1",
                                        "entities": {}}}})
    assert ok is True
    assert errors == []
    assert row["metadata"]["provider"] == "watsonx"
    assert row["metadata"]["fallback"] == "True"
    assert row["work"]["work_id"] == "rd_evidence:review-1"
    assert row["work"]["identity"]["kind"] == "report"


def test_review_ledger_keeps_official_evidence_on_accept(tmp_path):
    path = tmp_path / "common_ledger.jsonl"
    ok, errors, row = ledger.append_review(
        {"verdict": "accept", "domain": "opportunities",
         "reason": "official page and date verified", "evidence": [
             "https://official.example/call"], "risks": []},
        "opportunity", path=str(path))

    assert ok is True
    assert errors == []
    assert row["evidence"] == ["https://official.example/call"]


def test_opportunity_seed_enters_ledger_as_unverified_human_review(tmp_path):
    path = tmp_path / "common_ledger.jsonl"
    card = {
        "schema": "faro-opportunity-card-v1",
        "opportunity_id": "opportunity:fondart-regional",
        "title": "Fondart regional",
        "source_url": "https://fondosdecultura.cl/bases.pdf",
        "captured_at": "2026-08-06",
        "status": "unverified",
        "next_action": "verify official bases, eligibility and exact deadline",
        "deadline_raw": "segunda quincena de agosto",
    }

    ok, errors, row = ledger.opportunity_from_seed(card, path=str(path))

    assert ok is True
    assert errors == []
    assert row["id"] == "opportunity:fondart-regional"
    assert row["decision"] == "revisar"
    assert row["owner"] == "human"
    assert row["work"]["identity"]["kind"] == "opportunity"
    assert row["metadata"]["opportunity_card"]["status"] == "unverified"


def test_opportunity_seed_does_not_accept_untyped_candidate(tmp_path):
    ok, errors, row = ledger.opportunity_from_seed(
        {"title": "legacy"}, path=str(tmp_path / "common.jsonl"))

    assert ok is False
    assert errors == ["bad_opportunity_card_schema"]
    assert row is None


def test_summary_counts_by_domain_type_and_action(tmp_path):
    path = tmp_path / "common_ledger.jsonl"
    ledger.append_item({
        "domain": "svg", "type": "idea", "claim": "animate icon",
        "evidence": [], "files": [], "confidence": "medium",
        "action": "prototype",
    }, path=str(path))
    ledger.append_item({
        "domain": "svg", "type": "reject", "claim": "",
        "evidence": [], "files": [], "confidence": "low",
        "action": "reject", "reject_reason": "duplicate tool exists",
    }, path=str(path))
    summary = ledger.summarize(str(path))
    assert summary["by_domain"] == {"svg": 2}
    assert summary["by_type"] == {"idea": 1, "reject": 1}
    assert summary["by_action"] == {"prototype": 1, "reject": 1}


def test_summary_counts_by_lane_and_decision(tmp_path):
    path = tmp_path / "common_ledger.jsonl"
    ledger.append_item({
        "domain": "svg", "type": "artifact", "claim": "icon",
        "evidence": ["icon.svg"], "confidence": "high", "action": "prototype",
        "decision": "hacer",
    }, path=str(path))
    ledger.append_item({
        "domain": "rd", "type": "task", "claim": "source",
        "evidence": ["https://example.org"], "confidence": "medium",
        "action": "verify_source", "decision": "revisar",
    }, path=str(path))
    summary = ledger.summarize(str(path))
    assert summary["by_lane"] == {"obra": 1, "trabajo": 1}
    assert summary["by_decision"] == {"hacer": 1, "revisar": 1}


def test_summary_projects_legacy_rows_without_mutating_storage(tmp_path):
    path = tmp_path / "common_ledger.jsonl"
    path.write_text(json.dumps({
        "schema": ledger.SCHEMA_VERSION, "id": "legacy", "domain": "rd",
        "type": "task", "claim": "old source", "evidence": [], "files": [],
        "confidence": "unknown", "action": "verify_source",
        "metadata": {"queue_status": "pending_human"},
    }) + "\n", encoding="utf-8")
    summary = ledger.summarize(str(path))
    assert summary["by_lane"] == {"trabajo": 1}
    assert summary["by_decision"] == {"hacer": 1}
    assert summary["last"][0]["lane"] == "trabajo"
    assert summary["last"][0]["next_action"] == "verify source and date"


def test_tandas_cli_validate_can_write_common_ledger(tmp_path):
    common = tmp_path / "common_ledger.jsonl"
    payload = {"items": [{
        "claim": "existing tool should be reused",
        "evidence": ["tools/x.py"],
        "files": ["tools/x.py"],
        "confidence": "medium",
        "action": "reuse",
        "reject_reason": "",
    }]}
    result = subprocess.run(
        [sys.executable, "-m", "cultura.mak_plataforma.tandas", "validate",
         "--ledger-area", "tool_archaeology", "--ledger-provider", "watsonx",
         "--common-ledger", str(common)],
        input=json.dumps(payload), capture_output=True, text=True, timeout=20)
    assert result.returncode == 0
    row = json.loads(common.read_text(encoding="utf-8"))
    assert row["domain"] == "repo"
    assert row["source"] == "watsonx:tool_archaeology"


def test_audit_missing_paths_quarantines_without_mutating_ledger(tmp_path):
    ledger_path = tmp_path / "common.jsonl"
    quarantine_path = tmp_path / "quarantine.jsonl"
    ledger.append_item({
        "domain": "repo", "type": "evidence", "claim": "invented file",
        "evidence": [], "files": ["not-real/tool.py"], "confidence": "high",
        "action": "test",
    }, path=str(ledger_path))

    found = ledger.audit_missing_paths(str(ledger_path))
    added = ledger.write_quarantine(found, str(quarantine_path))

    assert len(found) == 1
    assert len(added) == 1
    assert added[0]["status"] == "quarantined"
    assert len(ledger.read_items(str(ledger_path))) == 1
    assert len(ledger.read_items_quarantine(str(quarantine_path))) == 1


def test_audit_deduplicates_quarantine(tmp_path):
    quarantine_path = tmp_path / "quarantine.jsonl"
    row = {"original_id": "abc", "missing_files": ["x.py"]}
    assert len(ledger.write_quarantine([row], str(quarantine_path))) == 1
    assert ledger.write_quarantine([row], str(quarantine_path)) == []


def test_classify_quarantine_never_restores_and_finds_unique_candidate(tmp_path):
    candidate = tmp_path / "candidate.py"
    candidate.write_text("pass\n", encoding="utf-8")
    rows = [
        {"original_id": "one", "missing_files": ["old/candidate.py"]},
        {"original_id": "two", "missing_files": ["gone.py"]},
        {"original_id": "three", "missing_files": ["[redacted]"]},
    ]

    classified = ledger.classify_quarantine(rows, roots=[str(tmp_path)])

    assert [item["disposition"] for item in classified] == [
        "review_only_unique", "stale_reject", "reject_secret"]
    assert classified[0]["candidate_paths"] == [str(candidate)]
    assert all("status" not in item or item["status"] == "quarantined"
               for item in classified)
