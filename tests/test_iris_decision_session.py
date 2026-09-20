import json
from pathlib import Path

from tools.iris_decision_session import compile_session, write_session


def test_compile_session_produces_final_sanitized_grouped_labels(tmp_path):
    queue = {
        "items": [{
            "project_id": 7,
            "scan_id": 1,
            "project_rel_root": "svg/example",
            "source_path": "C:\\IA\\svg\\example",
            "project_kind": "framework_project",
            "origin_class": "known_template_or_scaffold",
            "structure_class": "probable_derivative_family",
            "total_bytes": 12,
            "predicted_decision": "REVIEW_EXCEPTION",
            "confidence": 0.4,
            "reason_json": "[]",
            "evidence_json": "{}",
        }]
    }
    decisions = {
        "status": "final",
        "requires_approval": False,
        "decision_authority": "operator_delegated",
        "decision_maker": "codex",
        "session_id": "session-test",
        "purpose": "test",
        "source": {"scan_id": 1},
        "decisions": [{
            "project_id": 7,
            "decision": "PRESERVE_ECOSYSTEM",
            "confidence": 0.9,
            "group_key": "family-a",
            "reason": "fixture",
        }],
    }
    resources = {"policy": {"local_authority": True}}
    queue_path = tmp_path / "queue.json"
    decisions_path = tmp_path / "decisions.json"
    resources_path = tmp_path / "resources.json"
    queue_path.write_text(json.dumps(queue), encoding="utf-8")
    decisions_path.write_text(json.dumps(decisions), encoding="utf-8")
    resources_path.write_text(json.dumps(resources), encoding="utf-8")

    records, receipt = compile_session(queue_path, decisions_path, resources_path)
    assert records[0]["status"] == "final"
    assert records[0]["requires_approval"] is False
    assert records[0]["decision_authority"] == "operator_delegated"
    assert records[0]["independent_gold_label"] is False
    assert "source_path" not in records[0]
    assert receipt["row_count"] == 1
    assert receipt["evaluation_policy"]["split_by"] == "group_key"

    dataset_path, receipt_path = write_session(records, receipt, tmp_path)
    assert dataset_path.exists()
    assert receipt_path.exists()
    assert len(dataset_path.read_text(encoding="utf-8").splitlines()) == 1


def test_compile_session_rejects_pending_or_duplicate_decisions(tmp_path):
    queue = {"items": [{
        "project_id": 1,
        "scan_id": 1,
        "reason_json": "[]",
        "evidence_json": "{}",
    }]}
    decisions = {
        "status": "pending",
        "requires_approval": True,
        "decision_authority": "operator_delegated",
        "session_id": "bad",
        "purpose": "test",
        "source": {"scan_id": 1},
        "decisions": [],
    }
    resources = {"policy": {"local_authority": True}}
    paths = []
    for name, value in (("q", queue), ("d", decisions), ("r", resources)):
        path = tmp_path / f"{name}.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        paths.append(path)

    try:
        compile_session(*paths)
    except ValueError as exc:
        assert "final" in str(exc)
    else:
        raise AssertionError("pending decisions must be rejected")
