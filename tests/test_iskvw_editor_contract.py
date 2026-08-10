from pathlib import Path


EDITOR = Path(__file__).parents[1] / "iskvw" / "editor.html"
MESA = Path(__file__).parents[1] / "iskvw" / "mesa_montaje.js"


def test_editor_surfaces_mak_contract_without_making_hub_required():
    source = EDITOR.read_text(encoding="utf-8")
    mesa = MESA.read_text(encoding="utf-8")

    assert "id=\"inbox-contrato\"" in source
    assert "fetch('/api/portfolio/contract'" in source
    assert 'id="inbox-copiloto-externos-lista"' in source
    assert "/api/portfolio/external-candidates" in source
    assert "fetch('/api/portfolio/review-queue'" in source
    assert "fetch('/api/portfolio/triangulation'" in source
    assert "/api/portfolio/triangulation/context-link" in source
    assert "function enlazarContexto" in source
    assert "enlazar a grupo..." in source
    assert 'id="inbox-revision"' in source
    assert "function cargarRevision" in source
    assert "evidencia humana" in source
    assert "Contexto humano aceptado" in source
    assert "sin grupo de triangulacion enlazado" in source
    assert 'id="inbox-indice-lista"' in source
    assert "/api/portfolio/index" in source
    assert "Usuarios mencionados, no entidades resueltas" in source
    assert 'id="inbox-foco"' in source
    assert "Estudio de obra" in source
    assert "abrir en estudio" in source
    assert "function mostrarAccionPieza" in source
    assert "function cargarTriangulacionPieza" in source
    assert "foco-visual-field" in source
    assert "foco-orbit-item" in source
    assert "foco-dock" in source
    assert "/api/portfolio/copilot/vision" in source
    assert "visión AWS" in source
    assert "previsualizar orden" in source
    assert 'id="inbox-herramientas"' in source
    assert "no se ha movido ningun archivo" in source
    assert "function pintarFoco" in source
    assert "ID exacto para enfocar" in source
    assert "resolverCandidatoExterno" in source
    assert "copiloto-candidato-media" in source
    assert "mediaInbox(item)" in source
    assert "candidato pendiente" in source
    assert "contexto visual" in source
    assert "medios visibles" in source
    assert "foco-visual-legend" in source
    assert "estudio-review-queue" in source
    assert "estudioPendingItems" in source
    assert "estudioOpenReview" in source
    assert "estudioResolveCandidate" in source
    assert "estudio-learning-summary" in source
    assert "estudioLoadLearning" in source
    assert "/api/portfolio/copilot/learning" in source
    assert "source_id:sourceId" in source
    assert "Decisión guardada" in source
    assert "source_id_requerido" not in source
    assert "await cargarPendientesRevision()" in source
    assert "data-role=\"candidate\"" in source
    assert "data-role=\"context\"" in source
    assert "no publica automaticamente" in source
    assert "consentimiento registrado antes de publicar" in source
    assert "archivo visual · obras editoriales" in source
    assert "estudioArchiveUnits" in source
    assert "fecha antigua → nueva" in source
    assert "20 unidades" in source
    assert "function estudioLiveSelect" in source
    assert "ESTUDIO_SESSION_ID" in source
    assert "medios dentro de esta pasada" in source
    assert "estudio-live-suggestion-grid" in source
    assert "estudioSuggestionOpen" in source
    assert "estudioEnableSuggestionDrag" in source
    assert "data-item-id=\"${esc(neighbor.id)}\"" in source
    assert "estudio-live-suggestion-layer" in source
    assert "estudio-suggestion-popover" in source
    assert "estudioSuggestionDecision" in source
    assert "descartar · no es obra" in source
    assert "ESTUDIO_FEEDBACK_BUSY" in source
    assert "seleccionada'" in source
    assert "mesa_montaje.js?v=20260809-review-packet4" in source
    assert "<title>MAK · Estudio de obra</title>" in source
    assert "Estudio de obra · archivo vivo" in source
    assert "campo de orden" in mesa
    assert "La geometría permanece" in mesa
    assert 'data-field-mode="uncertainty"' in mesa
    assert 'data-field-mode="coverage"' in mesa
    assert 'data-field-mode="evidence"' in mesa
    assert 'data-field-mode="resonance"' in mesa
    assert "mesa-field-layer" in mesa
    assert "renderField" in mesa
    assert "relaxVisiblePositions" in mesa
    assert "selectOrderRegion" in mesa
    assert "mesa-order-compass" in mesa
    assert "mesa-map-legend" in mesa
    assert "centerNodeInView" in mesa
    assert "processedHumanSeed" in mesa
    assert "fetchSceneCached" in mesa
    assert "ficha activa · la decisión no crea vínculos" in mesa
    assert "advanceSeedFromPopover" in mesa
    assert "prefetchNextHumanSeed" in mesa
    assert "no creó relación. Completa la ficha y pulsa siguiente." in mesa
    assert "nextAvailableRecord" in mesa
    assert 'data-editor-mode="order"' in mesa
    assert 'data-editor-mode="relate"' in mesa
    assert 'data-learning-action="next-seed"' in mesa
    assert "async function loadHumanSeed" in mesa
    assert "humanSeedItemId" in mesa
    assert "state.humanSeedActive && id === state.humanSeedItemId" in mesa
    assert "centerNodeInView(candidateId)" in mesa
    assert "seedCandidateAllowed" in mesa
    assert "if (!response.ok) throw new Error(`HTTP ${response.status}`);" in mesa
    assert 'fetchSceneCached(candidateId, "copilot", "order")' in mesa
    assert 'query.set("surface", surface)' in mesa
    assert 'fetchScene(first.id, "copilot", "order")' in mesa
    assert 'const surface = state.editorMode === "order" ? "order" : "";' in mesa
    assert "ficha activa · la decisión no crea vínculos" in mesa
    assert "const advanceSeed = state.humanSeedActive" in mesa
    assert 'state.feedbackBusy.has("advance-seed")' in mesa
    assert 'state.feedbackBusy.add("advance-seed")' in mesa
    assert 'const busyKey = `discard:${record.source_id}`' in mesa
    assert 'state.feedbackBusy.has(busyKey)' in mesa
    assert 'await loadHumanSeed({ refresh: false, excludeId:' in mesa
    assert "/api/portfolio/copilot/learning" in mesa
    assert "classify-batch" in mesa
    assert "toggleOrderSelection" in mesa
    assert "el aprendizaje queda registrado sin crear relaciones" in mesa
    assert "una pieza, sus relaciones, ninguna copia" not in mesa
    assert "arrastra el vacío: recorrer el atlas" in mesa
    assert 'actionButton("relate"' in mesa
    assert 'actionButton("accept"' in mesa
    assert 'actionButton("reject"' in mesa
    assert 'actionButton("open"' in mesa
    assert 'actionButton("center"' in mesa
    assert "selectedId" in mesa
    assert "selectRelation" in mesa
    assert "window.open" in mesa
    assert "requestAnimationFrame" in mesa
    assert "work_group" in mesa
    assert "shuffle" in mesa
    assert "reloadSuggestions" in mesa
    assert 'item.selection !== "descartar"' in mesa
    assert "classificationMarkup" in mesa
    assert "classify-toggle" in mesa
    assert '[data-class-field="context_kind"].is-active' in mesa
    assert 'clearFields.push("context_value")' in mesa
    assert 'const pieceContext = `${groupNote}${workGroupNote}`' in mesa
    assert "viewRequestId" in mesa
    assert "if (requestId !== state.viewRequestId) return;" in mesa
    assert "sceneCacheRevision" in mesa
    assert "invalidateSceneCache" in mesa
    assert "state.sceneCachePromises.clear()" in mesa
    assert "classificationPending" in mesa
    assert "const normalizedMode = mode === \"all\" ? \"copilot\" : mode" in mesa
    assert "const excluded = new Set(state.processedHumanSeed)" in mesa
    assert "return candidates.find((record) => !isDecidedRecord(record)) || null" in mesa
    assert "state.editorMode === \"order\" && record.source_id !== state.activeId" in mesa
    assert "acquireRecordActions" in mesa
    assert 'field === "context_kind" && fields.context_kind !== value' in mesa
    assert "relationCounterpartId" in mesa
    assert "linkedIds.add(relation.source_id)" in mesa
    assert "/api/portfolio/classify" in mesa
    assert "replaceChildren" in mesa
    assert "data-pop-note" in mesa
    assert "mesa-suggestion-card" in mesa
    assert "relationHasUsefulEvidence" in mesa
    assert "mesa-decision-note" in mesa
    assert "mesa-popover-flow" in mesa
    assert "mesa-popover-grid" not in mesa
    assert "sugerencias · ${usefulSuggestions.length}" in mesa
    assert "mesa-popover-media-note" not in mesa
    assert "ver descripción original" not in mesa
    assert "const description =" in mesa
    assert "note" in mesa
    assert "distancia adaptada" in mesa


def test_editor_keeps_search_board_filter_and_association_tray_separate():
    source = EDITOR.read_text(encoding="utf-8")

    assert 'id="inbox-buscar"' in source
    assert 'id="inbox-tablero"' in source
    assert 'id="inbox-asociacion"' in source
    assert 'id="inbox-resumen"' in source
    assert 'data-inbox-view="pendientes"' in source
    assert 'data-inbox-view="archivo"' in source
    assert 'data-inbox-view="mesa"' in source
    assert 'let INBOX_VIEW = "pendientes"' in source
    assert 'class="inbox-tools"' in source
    assert "inbox-pin-media" in source
    assert "inbox-action-primary" in source
    assert "const INBOX_SELECTED = new Set()" in source
    assert "anadirSeleccionAlTablero" in source
