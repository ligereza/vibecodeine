from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from cultura.mak_conductor.handler_registry import build_handler_registry
from cultura.mak_conductor.queue_store import QueueStore
from cultura.mak_conductor.queue_worker import QueueWorker
from cultura.mak_conductor.source_bridge import (compare_imported_jobs,
                                                  import_legacy_sources)


def test_canonical_registry_contains_every_operational_stage():
    handlers = build_handler_registry()
    for stage in (
        "investigacion", "codex", "codex_free", "llm_call", "codex_llm_call",
        "external_call", "ollama_judge", "curatoria_vision",
        "mineria_vision", "memoria_embedding", "visual_index",
        "issue_render", "cron_tick", "external_batch", "repo_delivery",
        "pr_merge", "capataz_cycle", "junta_cycle", "heartbeat",
        "material_rebuild", "codex_backlog", "corpus_projection", "retention",
        "anexo_svg", "legacy_material_task", "legacy_codex_task",
        "legacy_research_task",
        "organism_family_plan",
        "organism_family_execute",
    ):
        assert callable(handlers[stage])


def test_organism_ingest_contract_uses_ascii_keyword():
    import inspect

    from cultura.mak_curatoria import ingesta_archivo

    for name in ("run_perception", "project_candidates"):
        parameters = inspect.signature(getattr(ingesta_archivo, name)).parameters
        assert "source_name" in parameters


def test_organism_execute_is_plan_only_without_explicit_isolated_mode():
    from cultura.mak_conductor.handler_registry import _organism_family_execute
    from cultura.mak_curatoria.diagnostico_proyectos import organism_plan

    plan = organism_plan({
        "family_id": "family-test", "project_id": "project-test",
        "family_kind": "asset_family", "strategy": "sample_visuals",
        "representative_asset_id": "asset-test",
        "representative_reason": "representative_visual",
    }, "render.png")
    result = _organism_family_execute({
        "payload_json": json.dumps({"plan": plan}),
    })
    assert result["validated"] is True
    assert result["status"] == "PLAN_ONLY"
    assert result["provider_calls"] == 0
    assert result["promotion"] == "none"


def test_organism_triangular_branch_emits_candidates_without_identity_promotion(
        tmp_path):
    from cultura.mak_conductor.handler_registry import _organism_triangular_branch

    records_path = tmp_path / "fichas.jsonl"
    records_path.write_text(json.dumps({
        "id": "ficha-1", "ruta_rel": "flyers/evento.png",
        "categoria": "flyer_evento", "mtime": "2026-08-13",
        "ocr_texto": "HEADLINER\n12/08/2026\nESPACIO RIESGO",
        "vision": {"descripcion": "evento"},
        "datos_evento": {"fecha": "12/08/2026", "venue": "Espacio Riesco",
                          "productora": "Productora Demo"},
    }, ensure_ascii=False) + "\n", encoding="utf-8")
    result = _organism_triangular_branch(records_path, tmp_path / "derived")

    assert result["status"] == "CANDIDATES"
    assert result["signals"] == 1
    assert result["event_candidates"]
    assert result["producer_candidates"]
    assert result["promotion"] == "none"


def test_organism_structure_branch_is_deterministic_and_degrades_explicitly(
        tmp_path):
    from cultura.mak_conductor.handler_registry import _organism_structure_branch

    image = tmp_path / "sample.png"
    image.write_bytes(bytes.fromhex(
        "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
        "1f15c4890000000d49444154789c6360f8cf00000004000101"
        "000018dd8db40000000049454e44ae426082"))
    observed = _organism_structure_branch(
        image, "sample.png", ".png", "image", tmp_path / "out")
    assert observed["status"] == "OBSERVED"
    assert observed["metadata"]["width"] == 1
    assert observed["promotion"] == "none"

    blend = tmp_path / "scene.blend"
    blend.write_bytes(b"BLENDER")
    deferred = _organism_structure_branch(
        blend, "scene.blend", ".blend", "other", tmp_path / "out-blend")
    assert deferred["status"] == "DEFERRED_TOOL"
    assert deferred["reason"] == "blender_unavailable"
    assert deferred["promotion"] == "none"


def test_organism_structure_branch_exposes_deeper_metadata_without_identity(
        tmp_path):
    from cultura.mak_conductor.handler_registry import _organism_structure_branch

    adobe = tmp_path / "autosave.psd"
    adobe.write_bytes(
        b"<xmp:CreatorTool>Adobe After Effects 2024</xmp:CreatorTool>"
        b"<xmp:CreateDate>2025-01-02T03:04:05-03:00</xmp:CreateDate>"
        b"<xmpMM:DocumentID>xmp.did:test</xmpMM:DocumentID>"
        b"<stEvt:action>saved</stEvt:action>"
    )
    xmp = _organism_structure_branch(
        adobe, "autosave.psd", ".psd", "structural", tmp_path / "xmp")
    assert xmp["status"] == "OBSERVED"
    assert xmp["metadata"]["document_id"] == ["xmp.did:test"]
    assert xmp["policy"] == "metadata_candidate_not_identity"

    import zipfile
    archive = tmp_path / "bundle.zip"
    with zipfile.ZipFile(archive, "w") as handle:
        handle.writestr("scene/0001.png", b"frame")
    manifest = _organism_structure_branch(
        archive, "bundle.zip", ".zip", "other", tmp_path / "archive")
    assert manifest["status"] == "OBSERVED"
    assert manifest["metadata"]["entry_count"] == 1
    assert manifest["metadata"]["policy"].endswith("current_mtime")

    show = tmp_path / "show.xml"
    show.write_text(
        '<MidiShortcutPreset><Shortcut uniqueId="1729388476817">'
        '<Value name="InputPath" path="/composition/layers/1"/>'
        "</Shortcut></MidiShortcutPreset>", encoding="utf-8")
    resolume = _organism_structure_branch(
        show, "show.xml", ".xml", "other", tmp_path / "xml")
    assert resolume["status"] == "OBSERVED"
    assert resolume["metadata"]["recognized_resolume_shape"] is True
    assert resolume["metadata"]["epoch_id_candidates"]
    assert resolume["metadata"]["policy"].endswith("venue_identity")


def test_canonical_worker_can_resume_durable_job_after_new_instance(tmp_path,
                                                                     monkeypatch):
    store = QueueStore(tmp_path / "mak.db")
    job = store.enqueue("legacy_codex_task", {
        "source_record_id": "one", "text": "bounded task", "mode": "generar",
        "density": "medio",
    })
    worker = QueueWorker.canonical(store, gpu_lock=tmp_path / "gpu.lock")
    assert "legacy_codex_task" in worker.handlers
    # Replace only this real handler in the canonical registry to avoid any
    # provider/process call; the durable claim still goes through Conductor.
    monkeypatch.setitem(worker.handlers, "legacy_codex_task",
                        lambda _job: {"validated": True,
                                      "artifacts": [{"kind": "task", "content": "ok"}]})
    restarted_worker = QueueWorker.canonical(store, gpu_lock=tmp_path / "gpu.lock")
    monkeypatch.setitem(restarted_worker.handlers, "legacy_codex_task",
                        worker.handlers["legacy_codex_task"])
    result = restarted_worker.run_once()
    assert result["job_id"] == job["job_id"]
    assert result["status"] == "COMPLETED"


def test_legacy_source_import_is_read_only_and_idempotent(tmp_path):
    material = tmp_path / "material.jsonl"
    material.write_text(json.dumps({
        "id": "m-1", "estado": "pendiente", "depto": "research",
        "modo": "research", "texto": "tema acotado",
    }) + "\n", encoding="utf-8")
    backlog = tmp_path / "backlog_codex.txt"
    backlog.write_text("# comment\nwrite a bounded utility\n", encoding="utf-8")
    material_before = material.read_bytes()
    backlog_before = backlog.read_bytes()
    store = QueueStore(tmp_path / "mak.db")

    first = import_legacy_sources(store, material_path=material,
                                  backlog_path=backlog, limit=10)
    second = import_legacy_sources(store, material_path=material,
                                   backlog_path=backlog, limit=10)

    assert first["material"]["created"] == 1
    assert first["codex"]["created"] == 1
    assert first["research"]["created"] == 0
    assert second["material"]["deduplicated"] == 1
    assert second["codex"]["deduplicated"] == 1
    assert second["research"]["created"] == 0
    assert material.read_bytes() == material_before
    assert backlog.read_bytes() == backlog_before
    assert len(store.list_jobs()) == 2


def test_source_comparison_matches_legacy_contract_and_records_evidence(tmp_path):
    material = tmp_path / "material.jsonl"
    material.write_text(json.dumps({
        "id": "m-1", "estado": "pendiente", "depto": "research",
        "modo": "research", "texto": "same research task",
    }) + "\n", encoding="utf-8")
    backlog = tmp_path / "backlog_codex.txt"
    backlog.write_text("# comment\nwrite bounded code\n", encoding="utf-8")
    research = tmp_path / "backlog.jsonl"
    research.write_text(json.dumps({
        "id": "r-1", "estado": "pendiente", "pregunta": "same question",
    }) + "\n", encoding="utf-8")
    store = QueueStore(tmp_path / "mak.db")
    imported = import_legacy_sources(store, material_path=material,
                                     backlog_path=backlog,
                                     research_path=research, limit=10)

    comparison = compare_imported_jobs(store, imported)

    assert comparison["ok"] is True
    assert comparison["checked"] == 3
    assert comparison["matched"] == 3
    assert comparison["mismatched"] == 0
    assert len(comparison["artifact_ids"]) == 3
    assert len(store.list_artifacts()) == 3
    events = store.list_events(event_type="shadow_input_comparison")
    assert len(events) == 3
    assert {event["status"] for event in events} == {"MATCH"}


def test_source_comparison_detects_external_legacy_mutation(tmp_path):
    material = tmp_path / "material.jsonl"
    material.write_text(json.dumps({
        "id": "m-1", "estado": "pendiente", "depto": "codex",
        "modo": "generar", "texto": "original task",
    }) + "\n", encoding="utf-8")
    empty = tmp_path / "empty.txt"
    empty.write_text("", encoding="utf-8")
    store = QueueStore(tmp_path / "mak.db")
    imported = import_legacy_sources(store, material_path=material,
                                     backlog_path=empty, research_path=empty,
                                     limit=10)
    material.write_text(json.dumps({
        "id": "m-1", "estado": "pendiente", "depto": "codex",
        "modo": "generar", "texto": "changed after import",
    }) + "\n", encoding="utf-8")

    comparison = compare_imported_jobs(store, imported)

    assert comparison["ok"] is False
    assert comparison["mismatched"] == 1
    assert comparison["mismatches"][0]["source"] == "material"


def test_cron_handler_imports_and_claims_one_legacy_task(tmp_path, monkeypatch):
    from cultura.mak_conductor import handler_registry

    material = tmp_path / "material.jsonl"
    material.write_text(json.dumps({
        "id": "m-1", "estado": "pendiente", "depto": "codex",
        "modo": "generar", "texto": "bounded task",
    }) + "\n", encoding="utf-8")
    backlog = tmp_path / "backlog.txt"
    backlog.write_text("", encoding="utf-8")
    research = tmp_path / "research.jsonl"
    research.write_text("", encoding="utf-8")
    monkeypatch.setenv("MAK_DB_PATH", str(tmp_path / "mak.db"))
    monkeypatch.setenv("MAK_GPU_LOCK_PATH", str(tmp_path / "gpu.lock"))
    monkeypatch.setenv("MAK_MATERIAL_PATH", str(material))
    monkeypatch.setenv("MAK_CODEX_BACKLOG_PATH", str(backlog))
    monkeypatch.setenv("MAK_RESEARCH_BACKLOG_PATH", str(research))
    original = handler_registry.HANDLERS["legacy_material_task"]
    handler_registry.HANDLERS["legacy_material_task"] = (
        lambda _job: {"validated": True,
                      "artifacts": [{"kind": "task-output", "content": "ok"}]})
    try:
        result = handler_registry._cron_tick({})
    finally:
        handler_registry.HANDLERS["legacy_material_task"] = original
    assert result["validated"] is True
    assert result["result"]["child"]["status"] == "COMPLETED"
    store = QueueStore(tmp_path / "mak.db")
    assert store.list_jobs(status="COMPLETED")


def test_cron_handler_preserves_legacy_fallback_when_sources_are_empty(
        tmp_path, monkeypatch):
    from cultura.mak_conductor import handler_registry

    for name in ("MAK_DB_PATH", "MAK_GPU_LOCK_PATH", "MAK_MATERIAL_PATH",
                 "MAK_CODEX_BACKLOG_PATH", "MAK_RESEARCH_BACKLOG_PATH"):
        monkeypatch.setenv(name, str(tmp_path / name))
    monkeypatch.setattr(handler_registry, "_legacy_tick_fallback",
                        lambda: {"legacy": True})
    result = handler_registry._cron_tick({})
    assert result["result"]["child"] == {
        "status": "LEGACY_FALLBACK", "result": {"legacy": True}}


def test_completed_legacy_source_never_falls_back_to_jsonl_execution(
        tmp_path, monkeypatch):
    from cultura.mak_conductor import handler_registry

    material = tmp_path / "material.jsonl"
    material.write_text(json.dumps({
        "id": "m-1", "estado": "pendiente", "depto": "codex",
        "modo": "generar", "texto": "bounded task",
    }) + "\n", encoding="utf-8")
    backlog = tmp_path / "backlog.txt"
    research = tmp_path / "research.jsonl"
    backlog.write_text("", encoding="utf-8")
    research.write_text("", encoding="utf-8")
    monkeypatch.setenv("MAK_DB_PATH", str(tmp_path / "mak.db"))
    monkeypatch.setenv("MAK_GPU_LOCK_PATH", str(tmp_path / "gpu.lock"))
    monkeypatch.setenv("MAK_MATERIAL_PATH", str(material))
    monkeypatch.setenv("MAK_CODEX_BACKLOG_PATH", str(backlog))
    monkeypatch.setenv("MAK_RESEARCH_BACKLOG_PATH", str(research))
    original = handler_registry.HANDLERS["legacy_material_task"]
    handler_registry.HANDLERS["legacy_material_task"] = (
        lambda _job: {"validated": True,
                      "artifacts": [{"kind": "task-output", "content": "ok"}]})
    fallback_calls = []
    monkeypatch.setattr(handler_registry, "_legacy_tick_fallback",
                        lambda: fallback_calls.append(True))
    try:
        first = handler_registry._cron_tick({})
        second = handler_registry._cron_tick({})
    finally:
        handler_registry.HANDLERS["legacy_material_task"] = original
    assert first["result"]["child"]["status"] == "COMPLETED"
    assert second["result"]["child"]["status"] == "SOURCE_QUEUE_DRAINED"
    assert fallback_calls == []


def test_terminal_source_rows_do_not_starve_later_pending_rows(tmp_path):
    from cultura.mak_conductor.source_bridge import import_material
    material = tmp_path / "material.jsonl"
    rows = [
        {"id": "done", "estado": "pendiente", "depto": "research",
         "modo": "research", "texto": "already done"},
        {"id": "next", "estado": "pendiente", "depto": "research",
         "modo": "research", "texto": "next task"},
    ]
    material.write_text("\n".join(json.dumps(row) for row in rows) + "\n",
                        encoding="utf-8")
    store = QueueStore(tmp_path / "mak.db")
    first = import_material(material, store, limit=10)
    done_job = store.get_job(first["jobs"][0])["job_id"]
    worker = QueueWorker(store, {
        "legacy_material_task": lambda _job: {
            "validated": True,
            "artifacts": [{"kind": "task-output", "content": "done"}],
        },
    }, gpu_lock=tmp_path / "gpu.lock")
    assert worker.run_once()["status"] == "COMPLETED"
    second = import_material(material, store, limit=1)
    assert second["seen"] == 2
    assert len(second["jobs"]) == 1
    assert second["jobs"][0] != done_job


def test_observe_only_worker_requires_sentinel(tmp_path):
    repo_root = Path(__file__).resolve().parents[1]
    tool = (repo_root / "tools" / "mak_ops" /
            "run_conductor_worker.py")
    result = subprocess.run(
        [sys.executable, str(tool), "--observe-only", "--db",
         str(tmp_path / "observe.db")],
        cwd=str(repo_root), capture_output=True, text=True,
        check=False,
    )
    assert result.returncode == 3
    assert "sentinel_required" in result.stdout


def test_observe_only_worker_requires_isolated_db(tmp_path):
    repo_root = Path(__file__).resolve().parents[1]
    tool = (repo_root / "tools" / "mak_ops" /
            "run_conductor_worker.py")
    sentinel = tmp_path / "ALLOW"
    sentinel.write_text("human gate\n", encoding="utf-8")
    env = dict(os.environ)
    env.pop("MAK_DB_PATH", None)
    result = subprocess.run(
        [sys.executable, str(tool), "--observe-only", "--sentinel",
         str(sentinel)],
        cwd=str(repo_root), capture_output=True, text=True, env=env,
        check=False,
    )
    assert result.returncode == 3
    assert "shadow_db_required" in result.stdout


def test_observe_only_worker_imports_without_claiming(tmp_path):
    repo_root = Path(__file__).resolve().parents[1]
    tool = (repo_root / "tools" / "mak_ops" /
            "run_conductor_worker.py")
    source = tmp_path / "backlog.txt"
    source.write_text("one bounded task\n", encoding="utf-8")
    sentinel = tmp_path / "ALLOW"
    sentinel.write_text("human gate\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(tool), "--observe-only", "--sentinel",
         str(sentinel), "--import-legacy", "--source-limit", "1", "--db",
         str(tmp_path / "observe.db"), "--material", str(source),
         "--backlog", str(source), "--research", str(source)],
        cwd=str(repo_root), capture_output=True, text=True,
        check=False,
    )
    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["mode"] == "observe-only"
    assert report["summary"]["jobs"] == {"ENQUEUED": 1}
    assert report["summary"]["observations"] == 0
