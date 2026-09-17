import json

from cultura.mak_plataforma import discernment, ledger, xio_evidence


def _write_show_kit(root):
    """The authoritative files `load_show_evidence` reads, and nothing else.

    Factored out on 2026-09-02 so the end-to-end circuit below feeds on the
    SAME input as the unit test above. A second hand-written copy of a fixture
    is how two tests start measuring different things without anyone noticing.
    """
    root.mkdir(parents=True, exist_ok=True)
    (root / "setlist_festival_sentir.txt").write_text(
        "00:00:00:00 intro show\n01:00:00:00 Último Día\n", encoding="utf-8")
    (root / "setlist_durations_dref.json").write_text(
        json.dumps({"durations": [71.2, None]}), encoding="utf-8")
    (root / "cue_map_dref.json").write_text(
        json.dumps({"fps": 30, "cues": [
            {"n": "1", "tema": "intro show", "timecode": "00:00:00:00", "layer": 1, "clip": 1},
            {"n": "2", "tema": "Último Día", "timecode": "01:00:00:00", "layer": None, "clip": None},
        ]}), encoding="utf-8")
    (root / "DIA_DEL_SHOW.md").write_text(
        "Kit de DREF CHOCOLATE. El artista y venue no están declarados aquí.",
        encoding="utf-8")
    (root / "ANOTACIONES_SHOW_20260724.md").write_text(
        "Show 2026-07-24. TC observado 07:33:56:29.", encoding="utf-8")
    return root


def test_xio_show_kit_keeps_evidence_atoms_separate_and_validates_work(tmp_path):
    _write_show_kit(tmp_path)

    result = xio_evidence.load_show_evidence(tmp_path)

    assert result["available"] is True
    assert result["work"]["schema"] == "mak-work-v1"
    assert result["work_valid"] is True
    assert result["linked_to_source_id"] is False
    fields = {row["field"]: row for row in result["evidence"]}
    assert fields["event"]["value"] == "DREF CHOCOLATE"
    assert fields["date"]["value"] == "2026-07-24"
    assert fields["timecode"]["status"] == "observed"
    assert fields["artist"]["status"] == "unknown"
    assert result["segments"][1]["duration_s"] is None


def test_xio_missing_show_kit_is_safe_fallback(tmp_path):
    result = xio_evidence.load_show_evidence(tmp_path)
    assert result["available"] is False
    assert result["segments"] == []


# ---------------------------------------------------------------------------
# The vertical circuit: evidence -> work -> candidate -> review -> decision ->
# auditable record
# ---------------------------------------------------------------------------
#
# Added 2026-09-02. Every node above already existed and was unit-tested; the
# CHAIN was not, so nothing failed when a hop lost a property. These two tests
# demonstrate the chain and pin the eight ways it degrades: a lost source_ref,
# producer read as owner, a hypothesis printed as fact, a candidate promoted
# without a human gate, an absence turned into `false`, a projection presented
# as knowledge, a possible operation reported as executed, and a result that
# drops its next action.
#
# The ledger is written to `tmp_path`, never to the append-only file the box
# keeps under the operator's home. Nothing here reaches a productive store.

_STATUS_CONFIDENCE = {"observed": "high", "declared": "medium", "unknown": "unknown"}


def _review_payload(evidence):
    """One review item per evidence atom, keeping each atom's own status.

    An atom whose status is `unknown` carries NO evidence reference, because it
    has none. That is what makes the local reviewer ask for it instead of
    letting the absence pass as a settled value.
    """
    return {"items": [{
        "claim": "%s=%s" % (row["field"], row["value"] or "(sin declarar)"),
        "evidence": [row["source"]] if row["status"] != "unknown" else [],
        "files": [],
        "action": "review",
        "confidence": _STATUS_CONFIDENCE[row["status"]],
    } for row in evidence]}


def test_show_evidence_reaches_an_auditable_decision_without_promoting_it(tmp_path):
    kit = _write_show_kit(tmp_path / "show_kit")
    ledger_path = tmp_path / "common_ledger.jsonl"

    # Node 1: evidence. Three fields have no source, and they stay unknown.
    result = xio_evidence.load_show_evidence(kit)
    atoms = {row["field"]: row for row in result["evidence"]}
    assert result["available"] is True
    assert result["unknowns"] == ["artist", "venue", "producer"]
    for field in ("artist", "venue", "producer"):
        assert atoms[field]["status"] == "unknown"
        # An absence is an empty declared value, never False and never None:
        # `false` would assert that nobody performed, which nothing measured.
        assert atoms[field]["value"] == ""
        assert atoms[field]["value"] is not False
    assert atoms["timecode"]["status"] == "observed"
    assert atoms["event"]["status"] == "declared"
    assert all(row["source"] for row in result["evidence"])

    # Node 2: the shared envelope, valid and still a candidate.
    work = result["work"]
    assert (work["schema"], work["status"]) == ("mak-work-v1", "candidate")
    assert ledger.validate_work_envelope(work) == (True, [])
    assert work["sources"] == result["source_files"] != []
    assert work["evidence_required"] == ["xio_show_kit", "human_portfolio_link"]
    # Producer and owner are different questions: xio_local made it, MAK owns
    # it. Collapsing them is how a provider's output becomes its own authority.
    assert work["provider"] == "xio_local"
    assert work["owner"] == "MAK"
    # The event name is an event. It is not an artist, a venue or a producer,
    # and no path, filename or directory name may become authorship.
    entities = work["identity"]["entities"]
    assert entities["event"] == ["DREF CHOCOLATE"]
    assert entities["source"] == result["source_files"]
    for field in ("artist", "username", "client", "collab", "venue", "location"):
        assert entities[field] == [], field

    # Node 3: evidence review. The three unresolved fields are what it asks
    # for; the verdict is `revise`, not a verdict about the show's truth.
    review = discernment.deterministic_review("mak_quality", _review_payload(result["evidence"]))
    assert review["verdict"] == "revise"
    assert review["domain"] == "mak"
    assert review["risks"] == []
    assert [line.split(": ", 1)[1].split("=", 1)[0] for line in review["missing_evidence"]] == [
        "artist", "venue", "producer"]

    # Node 4: the decision, in the shared five-value vocabulary.
    decision = discernment.decision_record(
        "mak_quality", _review_payload(result["evidence"]), work=work)
    assert decision["decision"] == "revisar"
    assert decision["decision"] in work["allowed_decisions"]
    # No hop promotes anything, and the human is the one who has to act.
    assert decision["promotion"] == "none"
    assert decision["owner"] == "human"
    assert decision["provider"] == "local_deterministic" != work["provider"]
    assert decision["work"]["status"] == "candidate"

    # Node 5: the auditable record, written to a throwaway ledger.
    ok, errors, row = ledger.append_review(
        review, "mak_quality", path=str(ledger_path), source="xio_local",
        metadata={"work": work, "decision": decision})
    assert (ok, errors) == (True, [])
    assert row["decision"] == "revisar"
    assert row["owner"] == "human"
    # A review that asked for evidence is low confidence. Recording it as
    # anything else would present a projection as knowledge.
    assert row["confidence"] == "low"
    # The work keeps its own lane; the decision about it is a system act. Two
    # objects, two lanes, and merging them loses which one was judged.
    assert (work["lane"], row["lane"]) == ("trabajo", "sistema")

    # The chain is auditable end to end: the source refs survive the round trip
    # and every hop still names its next action.
    stored = ledger.read_items(path=str(ledger_path))
    assert len(stored) == 1
    assert stored[0]["work"]["work_id"] == work["work_id"] == "xio:show:show_kit"
    assert stored[0]["work"]["sources"] == result["source_files"]
    assert stored[0]["work"]["status"] == "candidate"
    for hop in (result, work, review, decision, row, stored[0]):
        assert str(hop.get("next_action") or "").strip(), hop.get("schema")

    # The link this circuit exists to prepare was NOT performed. A possible
    # operation reported as executed is the failure this flag prevents.
    assert result["linked_to_source_id"] is False
    assert result["next_action"] == "link manually to portfolio source"


def test_an_accepted_review_still_does_not_link_or_promote(tmp_path):
    """The gate, stated as the case that would be easiest to get wrong.

    Even when every field carries a source and the verdict is `accept`, the
    decision does not promote the candidate and does not create the portfolio
    link. Promotion stays a human act; `accept` only means the batch is
    reviewable, never that the relation is true.
    """
    kit = _write_show_kit(tmp_path / "show_kit")
    result = xio_evidence.load_show_evidence(kit)
    sourced = {"items": [{
        "claim": "%s=declarado" % row["field"],
        "evidence": [row["source"]],
        "files": [], "action": "review", "confidence": "high",
    } for row in result["evidence"]]}

    review = discernment.deterministic_review("mak_quality", sourced)
    decision = discernment.decision_record("mak_quality", sourced, work=result["work"])

    assert review["verdict"] == "accept"
    assert review["missing_evidence"] == []
    assert decision["decision"] == "hacer"
    assert decision["owner"] == "MAK"
    assert decision["promotion"] == "none"
    assert decision["work"]["status"] == "candidate"
    assert result["linked_to_source_id"] is False


# ── el puente con el conocimiento que XIO acumula ────────────────────────


def _publish(tmp_path, subject, keys):
    directory = tmp_path / "foh_knowledge"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{subject}.json").write_text(json.dumps({
        "schema": "faro-xio-evidence-v1",
        "domain": "vj_foh",
        "subject": subject,
        "generated": "2026-09-17T00:00:00+00:00",
        "keys": keys,
    }), encoding="utf-8")
    return directory


def test_knowledge_absent_is_reported_and_not_read_as_nothing_known(tmp_path):
    result = xio_evidence.load_foh_knowledge("work", "Enrolar",
                                             root=tmp_path / "no-publicado")
    assert result["ok"] is True
    assert result["available"] is False
    assert "no ha publicado" in result["reason"]


def test_knowledge_keeps_the_declared_and_observed_labels(tmp_path):
    directory = _publish(tmp_path, "venue", {
        "Club Freedom": {
            "ok": True, "available": True, "schema": "faro-xio-evidence-v1",
            "subject": "venue", "key": "Club Freedom",
            "evidence": [
                {"field": "flicker_hz", "value": 240, "status": "declared",
                 "source": "raider"},
                {"field": "flicker_hz", "value": 100, "status": "observed",
                 "source": "flicker_reading:foto.jpg"},
            ],
            "unknowns": [],
        },
    })
    result = xio_evidence.load_foh_knowledge("venue", "Club Freedom", root=directory)
    assert result["available"] is True
    statuses = sorted(item["status"] for item in result["evidence"])
    assert statuses == ["declared", "observed"]
    # El dato medido no reemplaza al declarado: llegan los dos, etiquetados.
    values = {item["status"]: item["value"] for item in result["evidence"]}
    assert values == {"declared": 240, "observed": 100}


def test_a_subject_without_published_evidence_says_so(tmp_path):
    directory = _publish(tmp_path, "work", {})
    result = xio_evidence.load_foh_knowledge("work", "Enrolar", root=directory)
    assert result["available"] is False
    assert "no tiene evidencia publicada" in result["reason"]


def test_an_unreadable_envelope_fails_visibly(tmp_path):
    directory = tmp_path / "foh_knowledge"
    directory.mkdir(parents=True)
    (directory / "work.json").write_text("{ esto no es json", encoding="utf-8")
    result = xio_evidence.load_foh_knowledge("work", "Enrolar", root=directory)
    assert result["ok"] is False
    assert "ilegible" in result["reason"]


def test_an_unknown_subject_is_refused():
    result = xio_evidence.load_foh_knowledge("planeta")
    assert result["ok"] is False
    assert "subject desconocido" in result["reason"]
