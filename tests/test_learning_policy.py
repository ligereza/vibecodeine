import json

from flujo.knowledge.learning_policy import compile_dataset, fit_learning_policy, record_verified_result
from flujo.knowledge.project_ir import LearningStore, build_project_ir


def _project(project_id: str, domain: str, format_family: str = "text"):
    suffix = "blend" if format_family == "3d" else "md"
    return build_project_ir(
        project_id=project_id,
        title=project_id,
        source_root="/tmp/learning-source",
        domains=[domain],
        artifacts=[{"relative_path": project_id + "/asset." + suffix, "format_family": format_family}],
        state="active",
        evidence=[{"kind": "fixture", "status": "verified"}],
    )


def _record(store: LearningStore, project_id: str, label: str) -> None:
    store.record_episode(
        project_id=project_id,
        objective="validated route",
        phase="consumer_probe",
        action={"decision": {"selected": {"tool_id": label}}},
        observation={"source": "fixture"},
        outcome={"status": "succeeded"},
        validation={"status": "passed", "check": "fixture"},
        status="succeeded",
        episode_id="episode-" + project_id,
    )


def test_unverified_episodes_do_not_become_labels(tmp_path):
    database = tmp_path / "learning.sqlite"
    store = LearningStore(database)
    project = _project("unknown-project", "research")
    store.save_project(project)
    store.record_episode(
        project_id=project["project_id"], objective="probe", phase="consumer_probe",
        action={"decision": {"selected": {"tool_id": "research_job_router"}}},
        observation={}, outcome={"status": "needs_evidence"},
        validation={"status": "needs_evidence"}, status="needs_evidence",
        episode_id="episode-unknown",
    )
    dataset = compile_dataset(database)
    result = fit_learning_policy(database)
    assert not dataset.examples
    assert result["status"] == "abstain"
    assert result["reason"] == "insufficient_verified_examples"
    assert result["excluded"] == {"episode_not_verified": 1}


def test_verified_examples_split_by_project_and_can_pass_gate(tmp_path):
    database = tmp_path / "learning.sqlite"
    store = LearningStore(database)
    for index in range(30):
        domain = "research" if index % 2 else "rd"
        label = "research_job_router" if domain == "research" else "blend_scene_audit"
        project = _project("project-" + str(index), domain, "text" if domain == "research" else "3d")
        store.save_project(project)
        _record(store, project["project_id"], label)
    result = fit_learning_policy(database)
    assert result["eligible_examples"] == 30
    assert result["evaluation"]["holdout_count"] >= 2
    assert result["status"] == "candidate"
    assert result["recordable"] is True
    assert result["evaluation"]["holdout_accuracy"] >= 0.60


def test_verified_result_adapter_requires_validator_and_is_idempotent(tmp_path):
    database = tmp_path / "learning.sqlite"
    store = LearningStore(database)
    project = _project("verified-project", "rd", "3d")
    store.save_project(project)
    packet = tmp_path / "verified-result.json"
    packet.write_text(json.dumps({
        "schema": "mak-verified-result-v1",
        "project_id": project["project_id"],
        "tool_id": "blend_scene_audit",
        "episode_id": "episode-verified-result",
        "result": {"status": "verified", "artifact": "render_manifest.json"},
        "validation": {"status": "passed", "validator": "fixture-validator", "checks": ["manifest", "artifact"]},
        "evidence": [{"kind": "manifest", "ref": "render_manifest.json"}],
    }), encoding="utf-8")
    first = record_verified_result(database, packet)
    second = record_verified_result(database, packet)
    assert first == second == "episode-verified-result"
    assert len(compile_dataset(database).examples) == 1

    bad = tmp_path / "bad-result.json"
    bad.write_text(json.dumps({
        "schema": "mak-verified-result-v1", "project_id": project["project_id"],
        "tool_id": "blend_scene_audit", "result": {"status": "success"},
        "validation": {"status": "passed"}, "evidence": [{"ref": "x"}],
    }), encoding="utf-8")
    try:
        record_verified_result(database, bad)
    except ValueError as exc:
        assert str(exc) == "verified_result_validator_checks_required"
    else:
        raise AssertionError("invalid verification packet was accepted")
