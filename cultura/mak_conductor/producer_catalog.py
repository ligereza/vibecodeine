"""Canonical inventory of MAK producer boundaries.

This is an audit manifest, not a second queue or policy engine. Every entry is
either routed through the durable conductor, observed at a covered child
boundary, or explicitly classified as control/maintenance. Tests compare this
manifest with the versioned MAK crontab so a new producer cannot appear
silently outside the convergence plan.
"""

from __future__ import annotations

from typing import Final


PRODUCER_CATALOG: Final[tuple[dict[str, object], ...]] = (
    {"producer": "research.worker.run_tema", "stage": "investigacion",
     "kind": "work", "coverage": "active_and_shadow"},
    {"producer": "research.enqueue_annex_icons", "stage": "anexo_svg",
     "kind": "work", "coverage": "shadow_child"},
    {"producer": "post.pipeline.build_post_package", "stage": "post_package",
     "kind": "public_output", "coverage": "active_and_shadow"},
    {"producer": "research.LLM.call", "stage": "llm_call",
     "kind": "provider", "coverage": "active_and_shadow"},
    {"producer": "codex.worker_codex.run_pedido", "stage": "codex",
     "kind": "work", "coverage": "active_and_shadow"},
    {"producer": "codex.CoderLLM.call", "stage": "codex_llm_call",
     "kind": "provider", "coverage": "active_and_shadow"},
    {"producer": "platform.providers.call", "stage": "external_call",
     "kind": "provider", "coverage": "active_and_shadow"},
    {"producer": "platform.discernment.call_ollama", "stage": "ollama_judge",
     "kind": "provider", "coverage": "active_and_shadow"},
    {"producer": "curatoria.percepcion.vision_imagen", "stage": "curatoria_vision",
     "kind": "gpu_work", "coverage": "active_and_shadow"},
    {"producer": "curatoria.diagnostico_proyectos.organism_plan", "stage": "organism_family_plan",
     "kind": "routing", "coverage": "shadow_child"},
    {"producer": "curatoria.diagnostico_proyectos.organism_execute", "stage": "organism_family_execute",
     "kind": "gpu_work", "coverage": "shadow_child"},
    {"producer": "platform.mineria_rd.vision_flyer", "stage": "mineria_vision",
     "kind": "gpu_work", "coverage": "active_and_shadow"},
    {"producer": "research.memoria.indexar", "stage": "memoria_embedding",
     "kind": "gpu_work", "coverage": "active_and_shadow"},
    {"producer": "platform.visual_index.build_index", "stage": "visual_index",
     "kind": "gpu_work", "coverage": "active_and_shadow"},
    {"producer": "platform.puente_issues.una_pasada", "stage": "issue_render",
     "kind": "gpu_work", "coverage": "active_and_shadow"},
    {"producer": "platform.trabajo.main", "stage": "cron_tick",
     "kind": "orchestration", "coverage": "active_and_shadow"},
    {"producer": "platform.tandas.run_external_batch", "stage": "external_batch",
     "kind": "provider_batch", "coverage": "active_and_shadow"},
    {"producer": "platform.entregar.main", "stage": "repo_delivery",
     "kind": "publication", "coverage": "human_gate_pending"},
    {"producer": "platform.revisor.enforce_pr", "stage": "pr_merge",
     "kind": "branch_mutation", "coverage": "human_gate_pending"},
    {"producer": "codex.agente_libre.correr", "stage": "codex_free",
     "kind": "work", "coverage": "child_coder"},
    {"producer": "platform.backlog_codex.main", "stage": "codex_backlog",
     "kind": "task_source", "coverage": "legacy_store_pending"},
    {"producer": "platform.capataz.main", "stage": "capataz_cycle",
     "kind": "orchestration", "coverage": "human_gate_pending"},
    {"producer": "platform.junta.main", "stage": "junta_cycle",
     "kind": "advisory", "coverage": "child_llm"},
    {"producer": "platform.latido.main", "stage": "heartbeat",
     "kind": "orchestration", "coverage": "active_and_shadow"},
    {"producer": "platform.material.main", "stage": "material_rebuild",
     "kind": "task_source", "coverage": "legacy_store_pending"},
    {"producer": "conductor.source_bridge.material", "stage": "legacy_material_task",
     "kind": "task_source", "coverage": "shadow_import"},
    {"producer": "conductor.source_bridge.codex", "stage": "legacy_codex_task",
     "kind": "task_source", "coverage": "shadow_import"},
    {"producer": "conductor.source_bridge.research", "stage": "legacy_research_task",
     "kind": "task_source", "coverage": "shadow_import"},
    {"producer": "research.corpus_a_micelio.main", "stage": "corpus_projection",
     "kind": "maintenance", "coverage": "active_and_shadow"},
    {"producer": "research.retencion.main", "stage": "retention",
     "kind": "maintenance", "coverage": "human_gate_pending"},
    {"producer": "platform.backup", "stage": "backup",
     "kind": "maintenance", "coverage": "control_boundary"},
    {"producer": "platform.watchdogs", "stage": "watchdog",
     "kind": "control", "coverage": "excluded_control"},
    {"producer": "platform.red_watch", "stage": "network_watch",
     "kind": "control", "coverage": "excluded_control"},
    {"producer": "platform.vigia", "stage": "external_watch",
     "kind": "control", "coverage": "excluded_control"},
    {"producer": "language.hooks", "stage": "language_scan",
     "kind": "control", "coverage": "excluded_control"},
)


CRONTAB_PRODUCER_HINTS: Final[dict[str, str]] = {
    "trabajo.py": "platform.trabajo.main",
    "entregar.py": "platform.entregar.main",
    "backlog_codex.py": "platform.backlog_codex.main",
    "junta.py": "platform.junta.main",
    "agente_libre.py": "codex.agente_libre.correr",
    "revisor.py": "platform.revisor.enforce_pr",
    "capataz.py": "platform.capataz.main",
    "latido.py": "platform.latido.main",
    "material.py": "platform.material.main",
    "corpus_a_micelio.py": "research.corpus_a_micelio.main",
    "puente_issues.py": "platform.puente_issues.una_pasada",
    "retencion.py": "research.retencion.main",
}


def catalog_by_producer() -> dict[str, dict[str, object]]:
    return {str(row["producer"]): dict(row) for row in PRODUCER_CATALOG}


def uncovered_entries() -> list[dict[str, object]]:
    return [dict(row) for row in PRODUCER_CATALOG
            if str(row.get("coverage")) in {
                "unadapted_audit", "legacy_store_pending", "human_gate_pending",
            }]
