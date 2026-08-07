import json
import subprocess
import sys

from cultura.mak_plataforma import ledger
from cultura.mak_plataforma import tandas


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
                  "fallback": True, "profile_verdict": "revise"})
    assert ok is True
    assert errors == []
    assert row["metadata"]["provider"] == "watsonx"
    assert row["metadata"]["fallback"] == "True"


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
