"""IRIS invariants: one address for the four properties the surface promises.

The properties were already covered, but scattered across eight files, so no
single failure told an operator that IRIS had stopped being honest.  This gate
names them:

1. replay never promotes its own output,
2. a learned metric activates only on measured gain,
3. the ordering field does not move the atlas geometry,
4. every machine output arrives as a human candidate, not a decision.

Cause (2026-09-02): the surface is being presented as an epistemic instrument
whose credibility rests on what it refuses to do; a refusal with no test is a
claim.  Retirement: when a contract check enforces the four properties at the
route boundary instead of at the function boundary.
"""
from __future__ import annotations

import copy

from cultura.mak_plataforma import ledger
from cultura.mak_plataforma.copilot import (active_ordering_seed,
                                            build_gtm_map,
                                            replay_ordering_evaluation)


def _item(item_id, *, date="2026-08-08", description="", kind="story",
          publication="", triage=""):
    item = {
        "id": item_id,
        "fecha": date,
        "descripcion_original": description,
        "tipo_contenido": kind,
        "publicacion_id": publication,
        "asset_path": "/portfolio-media/stories/%s.mp4" % item_id,
        "asset_available": True,
    }
    if triage:
        item["classification"] = {"triage": triage}
    return item


def _labeled_corpus():
    """A corpus whose labels are real but whose terms carry no signal.

    The pair metric cannot beat identity here, which is the case measured on
    2026-08-09 (accuracy 0.857143 against macro-recall 0.859091, tie retained
    and not activated).
    """
    labels = ("work", "record", "review", "discard")
    items = []
    for index in range(24):
        label = labels[index % len(labels)]
        items.append(_item(
            "labeled-%02d" % index,
            date="2026-08-%02d" % (index % 28 + 1),
            description="registro de sesion %d" % index,
            triage=label))
    for index in range(8):
        items.append(_item(
            "open-%02d" % index,
            date="2026-07-%02d" % (index + 1),
            description="pieza sin decidir %d" % index))
    return items


def test_replay_never_promotes_and_hands_back_to_a_human():
    items = _labeled_corpus()
    before = copy.deepcopy(items)

    result = replay_ordering_evaluation(items)

    assert result["promotion"] == "none"
    assert result["next_action"] == "human_review"
    assert items == before, "replay mutated the corpus it was measuring"


def test_replay_reports_abstention_apart_from_error():
    result = replay_ordering_evaluation(_labeled_corpus())

    assert result["evaluated"] == result["committed"] + result["abstained"]
    assert result["accuracy"] <= result["selective_accuracy"] or not result["committed"]
    for actual, row in result["confusion"].items():
        assert "abstain" in row, "%s has no abstention column" % actual


def test_learned_metric_stays_inactive_without_measured_gain():
    surface = build_gtm_map(_labeled_corpus(), stable_topology=True)
    profile = surface["ordering"]["field"]["distance_profile"]

    if profile["active"]:
        comparison = surface["ordering"]["evaluation"]["distance_comparison"]
        assert (comparison["accuracy_delta"] > 0
                or comparison["macro_recall_delta"] > 0), (
            "metric activated without beating the baseline")
        assert profile["activation"] == "replay_gain"
    else:
        assert profile["activation"] == "held_out_no_replay_gain"
        assert profile["rejection_reason"] == "no_replay_gain"
        assert profile["method"] == "identity"
        assert set(profile["weights"]) == {1.0}


def test_activation_gate_never_promotes_the_candidate_metric():
    surface = build_gtm_map(_labeled_corpus(), stable_topology=True)

    comparison = surface["ordering"]["evaluation"]["distance_comparison"]
    assert comparison["promotion"] == "none"


def test_ordering_field_does_not_move_the_atlas_geometry():
    items = _labeled_corpus()
    surface = build_gtm_map(items, stable_topology=True)

    field = surface["ordering"]["field"]
    assert field["moves_geometry"] is False
    assert surface["atlas"]["stable_during_pass"] is True
    assert {row["item_id"] for row in surface["items"]} == {
        str(item["id"]) for item in items}


def test_every_seeded_case_arrives_as_a_human_candidate():
    items = _labeled_corpus()
    surface = build_gtm_map(items, stable_topology=True)

    seed = active_ordering_seed(items, surface, limit=6)

    assert seed, "the active seed produced no cases to review"
    for row in seed:
        assert row["status"] == "human_candidate"
        assert row["review_scope"] == "record_or_review"
        assert "reason" in row and row["reason"]


def test_seeded_cases_are_never_already_decided():
    items = _labeled_corpus()
    surface = build_gtm_map(items, stable_topology=True)

    seeded = {row["item_id"] for row in active_ordering_seed(items, surface,
                                                             limit=12)}
    decided = {str(item["id"]) for item in items
               if (item.get("classification") or {}).get("triage")}

    assert not seeded & decided, "the seed asked again for a settled decision"


def _raw_record():
    return {
        "domain": "portfolio",
        "type": "evidence",
        "action": "review",
        "claim": "aparece un montaje de video en vivo",
        "identity": {"kind": "record", "source_id": "instagram:sample-1"},
    }


def test_ledger_item_keeps_its_source_id_and_declared_claim():
    item = ledger.normalize_item(_raw_record(), source="manual",
                                 ts="2026-09-02T00:00:00Z")

    ok, errors, _normalized = ledger.validate_item(item, source="manual")
    assert (ok, errors) == (True, [])
    assert item["work"]["identity"]["source_id"] == "instagram:sample-1"
    assert item["work"]["identity"]["kind"] == "record"
    assert item["claim"] == "aparece un montaje de video en vivo"


def test_a_record_cannot_enter_the_ledger_without_a_declared_action():
    raw = _raw_record()
    del raw["action"]

    item = ledger.normalize_item(raw, source="manual",
                                 ts="2026-09-02T00:00:00Z")
    ok, errors, _normalized = ledger.validate_item(item, source="manual")

    assert ok is False
    assert "bad_action_for_domain" in errors


def test_normalizing_the_same_record_twice_is_idempotent():
    raw = _raw_record()

    first = ledger.normalize_item(copy.deepcopy(raw), source="manual",
                                  ts="2026-09-02T00:00:00Z")
    second = ledger.normalize_item(copy.deepcopy(raw), source="manual",
                                   ts="2026-09-02T00:00:00Z")

    assert first == second
