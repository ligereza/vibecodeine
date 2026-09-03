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
    assert "MAK · campo de orden" in source
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
    assert "mesa_montaje.js?v=20260811-atlas-context-map" in source
    assert "/api/portfolio/inbox?surface=mesa" in mesa
    assert "<title>MAK · Campo de orden · archivo vivo</title>" in source
    assert "MAK · campo de orden" in source
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
    assert "visual_similarity" in mesa
    assert "MobileCLIP-S0" in mesa
    assert "centerNodeInView" in mesa
    assert "processedHumanSeed" in mesa
    assert "fetchSceneCached" in mesa
    assert "ficha activa · la decisión no crea vínculos" in mesa
    assert "advanceSeedFromPopover" in mesa
    assert "prefetchNextHumanSeed" in mesa
    assert "await loadHumanSeed({ refresh: false, excludeId: record.source_id });" in mesa
    assert "advanceAfterOrderDecision" not in mesa
    assert "nextAvailableRecord" not in mesa
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
    assert 'state.feedbackBusy.has("advance-seed")' in mesa
    assert 'state.feedbackBusy.add("advance-seed")' in mesa
    assert 'await loadHumanSeed({ refresh: false, excludeId:' in mesa
    assert "state.orderSelectedIds = new Set(" in mesa
    assert "/api/portfolio/copilot/learning" in mesa
    assert "toggleOrderSelection" in mesa
    assert "draftFor" in mesa
    assert "draftHasContent" in mesa
    assert "saveDraft" in mesa
    assert "commitDraft" in mesa
    assert "cancelDraft" in mesa
    assert "undoLastAction" in mesa
    assert "undoRelationDecision" in mesa
    assert "syncRecordFromItem(anchor, data.item)" in mesa
    assert "clearDraftState(anchor, data.item?.decision_draft" in mesa
    assert 'portfolioPost("/api/portfolio/draft"' in mesa
    assert 'portfolioPost("/api/portfolio/commit"' in mesa
    assert 'portfolioPost("/api/portfolio/undo"' in mesa
    assert "window.confirm" in mesa
    assert "advanceAfterOrderDecision" not in mesa
    assert "una pieza, sus relaciones, ninguna copia" not in mesa
    assert "arrastra el vacío: recorrer el atlas" in mesa
    assert 'actionButton("relate"' in mesa
    assert 'actionButton("accept"' in mesa
    assert 'actionButton("reject"' in mesa
    assert 'actionButton("open"' in mesa
    assert 'actionButton("center"' in mesa
    assert "selectedId" in mesa
    assert "selectRelation" in mesa
    assert "const suggestionsDrawerMarkup = active && usefulSuggestions.length" in mesa
    assert "return relation?.relation_id ? selectRelation(relation.relation_id)" in mesa
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
    assert "context_fields: contextFields" in mesa
    assert "const contextFields = {" in mesa
    assert 'const pieceContext = `${groupNote}${workGroupNote}`' in mesa
    assert "viewRequestId" in mesa
    assert "if (requestId !== state.viewRequestId) return;" in mesa
    assert "sceneCacheRevision" in mesa
    assert "invalidateSceneCache" in mesa
    assert "state.sceneCachePromises.clear()" in mesa
    assert "classificationPending" in mesa
    assert "const normalizedMode = mode === \"all\" ? \"copilot\" : mode" in mesa
    assert "const excluded = new Set(state.processedHumanSeed)" in mesa
    assert "return candidates.find((record) => !isDecidedRecord(record)) || null" not in mesa
    assert "state.editorMode === \"order\" && record.source_id !== state.activeId" in mesa
    assert "acquireRecordActions" in mesa
    assert 'field === "context_kind" && fields.context_kind !== value' in mesa
    assert "relationCounterpartId" in mesa
    assert "linkedIds.add(relation.source_id)" in mesa
    assert 'fetch("/api/portfolio/select"' not in mesa
    assert 'fetch("/api/portfolio/classify"' not in mesa
    assert 'fetch("/api/portfolio/feedback"' not in mesa
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
    assert 'id="mesa-external-queue"' in mesa
    assert "loadExternalQueue" in mesa
    assert "externalReviewMarkup" in mesa
    assert "/api/portfolio/external-candidates/review" in mesa
    assert 'data-pop-action="external-review"' in mesa
    assert 'id="mesa-audit"' in mesa
    assert "/api/portfolio/audit" in mesa
    assert "Atlas de decisiones verificable" in mesa
    assert "Estado actual de selección" in mesa
    assert "Etiquetas de aprendizaje · no son piezas activas" in mesa
    assert "Línea temporal" in mesa
    assert "current_selection" in mesa
    assert "triage_labels" in mesa
    assert 'contentType.includes("application/json")' in mesa
    assert "la auditoría aún no está desplegada" in mesa

    order_decision = mesa[mesa.index("function applyOrderDecision") : mesa.index("function rebuildScene")]
    assert "updateDraft(record" in order_decision
    assert "revisa y efectúa la acción explícitamente" in order_decision

    assert "if(!r.ok)throw new Error(`HTTP ${r.status}`);" in source
    assert "Selección parcial del carrusel" in source
    assert "la selección visible fue restaurada" in source
    assert "tableros no disponibles temporalmente" in source
    assert "No se pudieron cargar las sugerencias; la pieza sigue disponible." in source


def test_mesa_uses_explicit_draft_gate_and_keeps_targets_visible():
    mesa = MESA.read_text(encoding="utf-8")

    assert 'data-order-action="save-draft-all"' in mesa
    assert 'data-order-action="commit-draft-all"' in mesa
    assert 'data-order-action="cancel-draft-all"' in mesa
    assert 'actionButton("save-draft"' in mesa
    assert 'actionButton("commit-draft"' in mesa
    assert 'actionButton("cancel-draft"' in mesa
    assert 'actionButton("undo"' in mesa
    assert 'actionButton("undo-relation"' in mesa
    assert "mesa-relation-pending" in mesa
    assert "mesa-order-targets" in mesa
    assert "state.selectedId = itemIds.length === 1 ? itemIds[0] : state.activeId" in mesa
    assert "window.confirm" in mesa
    assert "advanceAfterOrderDecision" not in mesa


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


# ---------------------------------------------------------------------------
# The portfolio surface is a PAIR of files, and which copy is served is a
# contract
# ---------------------------------------------------------------------------
#
# Added 2026-09-02 after the same confusion cost two agents in a row. The Hub's
# portfolio tab is the application that orders records, relates them and
# carries a copilot that learns. The artist's portfolio is the PRODUCT that
# comes out of it, and `iskvw.cl` is a third thing: the dormant published site.
# They share the `iskvw/` prefix through a historical join and are not one
# surface. (`IRIS` is the name of the grant application this system is
# presented under; it renames nothing in the tree.)
#
# The trap these guards close: the interface a person sees is drawn by
# `mesa_montaje.js`, not by `editor.html`. Searching the HTML alone for the
# visible chrome returns ZERO and reads exactly like a stale deployment, which
# is how "Codex left the old version" became a plausible-looking conclusion
# about a tree that was current.
#
# Retirement: when one authoritative copy of the pair exists and the Hub
# resolves it by contract instead of by a default path.

# Strings a person reads on screen, in the case the SOURCE uses. The screen
# shows them uppercase because the shell carries the `text-transform` rules, so
# searching for what the screenshot shows is a second way to measure nothing.
_VISIBLE_CHROME = (
    "atlas vivo", "incertidumbre", "siguiente frontera", "evidencia externa",
)


def test_the_surface_is_a_pair_and_the_chrome_lives_in_the_javascript():
    """Measuring `editor.html` alone cannot tell you what version is running."""
    source = EDITOR.read_text(encoding="utf-8")
    mesa = MESA.read_text(encoding="utf-8")

    assert 'src="mesa_montaje.js' in source, (
        "the shell must load the interface; without this the pair is not a pair")
    for token in _VISIBLE_CHROME:
        assert token in mesa, token
        # Pin the trap itself: the chrome is NOT in the shell, so a search that
        # stops at the HTML measures the wrong file and reports a false stale.
        assert token not in source, token


def test_the_hub_serves_the_editor_from_this_checkout_not_the_sibling():
    """`PORTFOLIO_ROOT` decides which copy a person actually edits."""
    hub = (Path(__file__).parents[1] / "cultura" / "mak_plataforma"
           / "hub.py").read_text(encoding="utf-8")
    assert 'os.path.join(HOME, "iskvw")' in hub
    assert 'os.path.join(HOME, "flujo/iskvw")' not in hub
    assert 'HOME, "flujo", "iskvw"' not in hub


def test_the_mak_tree_never_reads_the_sibling_copy_of_the_surface():
    """MAK owns this surface; FLUJO's copy of it cannot run.

    First written on 2026-09-02 as "the two copies must stay byte-identical",
    and refuted the same day by the first real improvement to the interface:
    that rule would force every MAK-side UI change to also touch the FLUJO
    branch, coupling the two checkouts the separation existed to decouple.

    Measured instead: the FLUJO Hub serves no `/api/portfolio/*` route, and the
    interface makes five or more fetches to exactly those routes, so the
    sibling copy is inert there -- it would load and fail every call. What
    still needs guarding is the real risk: someone editing the sibling copy
    believing they are editing the served one. So the rule is direction, not
    equality: nothing in the MAK tree may read the sibling's copy.
    Measured over string LITERALS, not file text: `hub.py` carries a comment
    explaining why the `HOME/flujo/iskvw` spelling was retired, and a plain
    substring search calls that comment a read. Naming a path is not using it.
    """
    import ast

    sibling = "flujo/iskvw"
    offenders = []
    for folder in ("cultura", "tools", "iskvw"):
        root = Path(__file__).parents[1] / folder
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            source = path.read_text(encoding="utf-8", errors="replace")
            if sibling not in source:
                continue
            try:
                tree = ast.parse(source, filename=str(path))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    if sibling in node.value:
                        offenders.append("%s:%d" % (path, node.lineno))
    assert not offenders, (
        "these read the sibling checkout's copy of the surface; the Hub serves "
        "the MAK one:\n  " + "\n  ".join(offenders))
    assert 'os.path.join(HOME, "iskvw")' in (
        Path(__file__).parents[1] / "cultura" / "mak_plataforma" / "hub.py"
    ).read_text(encoding="utf-8")


def test_the_interface_shows_what_the_record_has_and_lacks():
    """Data reaching the browser is not the same as a person being able to
    read it. The frontier rows carried has_description / has_vision /
    review_scope for months and the interface referenced none of them.
    """
    mesa = MESA.read_text(encoding="utf-8")
    shell = EDITOR.read_text(encoding="utf-8")

    assert "evidence_readiness" in mesa, "the interface must consume the report"
    assert "readinessStrip" in mesa
    # Every channel is named for a person, not left as a raw key.
    for channel in ("asset", "description", "date", "perception",
                    "classification", "relations", "work_group"):
        assert f"{channel}:" in mesa, channel
    # The three statuses must be visually distinct, or `unknown` reads as
    # `absent` and a gap becomes a finding.
    for status in ("is-present", "is-absent", "is-unknown"):
        assert f".mesa-readiness-chips .{status}" in shell, status
    # Abstention has to look different from a reservation.
    assert '.mesa-readiness[data-decision="abstain"]' in shell
    # And the label that means "not decidable yet" stays one click away.
    assert 'data-order-action="review"' in mesa


def test_the_declared_purposes_are_readable_from_the_interface():
    """The production chain rendered four documents that a person could only
    reach by curling a JSON route.

    A purpose is a declared format (`data/portfolio_formats/*.json`), and the
    whole point of `O_G` is that one corpus yields several defensible orders.
    Leaving them invisible made the system look like it produced nothing.
    """
    mesa = MESA.read_text(encoding="utf-8")
    shell = EDITOR.read_text(encoding="utf-8")

    assert 'id="mesa-purposes"' in mesa, "the toolbar must offer the panel"
    assert "loadPurposes" in mesa
    assert "/api/portfolio/production" in mesa
    # A blocked purpose has to look different from a producing one, or "no
    # factible" reads as "empty" and the reason disappears.
    assert ".mesa-purpose.is-rendered" in shell
    assert ".mesa-purpose.is-blocked" in shell
    # The document itself is readable, not just its status.
    assert "purposeDocumentMarkup" in mesa
    assert ".mesa-purpose-doc" in shell
    # It reads; it does not decide. No write action is wired into this panel.
    start = mesa.index("async function loadPurposes(")
    body = mesa[start:mesa.index("\n  async function ", start + 10)]
    assert "method:" not in body, "the purposes panel must not POST"
    assert "promotion" in mesa[mesa.index("function purposesMarkup("):
                                mesa.index("function purposeDocumentMarkup(")]
