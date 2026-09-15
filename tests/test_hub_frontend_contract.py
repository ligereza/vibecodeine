from pathlib import Path


def test_portfolio_card_keeps_epistemic_and_operational_boundaries_visible() -> None:
    source = (
        Path(__file__).resolve().parents[1]
        / "web"
        / "src"
        / "components"
        / "HubDashboard.tsx"
    ).read_text(encoding="utf-8")

    for marker in (
        "Portafolio / archivo",
        "Contexto de práctica",
        "Resultado interno (no aprobación)",
        "Promoción:",
        "no automatizada · requiere actor humano",
        "piezas quedan fuera",
        "Límites conservados:",
        "Visión interna · no aprobación",
        "Hipótesis seleccionada para lectura:",
        "hipótesis que sobrevive al test interno",
        "Contraevidencia conservada",
        "Razón:",
        "Referencias de evidencia:",
        "selectedReviewProjectId",
        "setSelectedReviewProjectId(item.project_id)",
        "portfolioReviewContext(selectedReviewProjectId || undefined)",
        "Faltantes concretos",
        "Evidencias observadas",
        "referencia local",
        "provide_typed_archive_project_relation_with_source_refs",
        "operationReceipt()",
        "Recibo de operación · MAK",
        "expand_library_program",
        "semantic_equivalence_authorized",
        "executed_structural_only",
        "vizzMeasurementStatus()",
        "VIZZ · estado de medición",
        "unknown_measurement_refused",
        "no emitida",
        "provide_physical_calibration_evidence_before_metric_measurement",
        "calibration_audit_sha256",
        "calibration_provenance_ref",
        "confirm-extraction",
        "confirmar extract",
        "actor_kind",
        "process_advanced",
        "decision_write",
        "Fuente oficial de licencias",
        "source_review_sha256",
        "licencia no concluyente",
        "revisión humana",
        "vizzLineageStatus()",
        "Lineage VIZZ · contexto",
        "revision_context_only",
        "current_state_replaced",
        "structuralDeltaStatus()",
        "Delta estructural · revisión-only",
        "revision_only_delta",
        "Residuos nuevos:",
        "learning_demonstrated",
        "portfolioDirectionContext()",
        "Marco de trabajo · visión / orden / cultura-computación",
        "vision_order_culture_computation_read_only_frame",
        "measurement_claim_allowed",
        "selección=none · promoción=none · publicación=false",
        "portfolioWorkPacket()",
        "Paquete de trabajo · Portafolio",
        "execution_allowed",
        "human_review_portfolio_work_packet_and_choose_one_task",
        "portfolioWorkPreview()",
        "previsualizar",
        "Preview:",
        "human_review_selected_work_preview_before_execution",
        "archiveOrientation()",
        "Orientación del archivo · 4 capas",
        "declared-works",
        "observed-field",
        "practice-context",
        "source_piece_count",
        "portfolioRelationEvidencePlan()",
        "Relación · plan de evidencia",
        "Unknowns:",
        "typed_relation_present",
        "Evidencia observada",
        "reference_present",
        "reference_class",
    ):
        assert marker in source
    assert "archiveView.control?.publication ? 'habilitada' : 'cerrada'" in source
    assert "archiveView.reconciliation?.truth_promotions" in source
    assert "(reviewQueue.items || []).slice(0, 4)" not in source
