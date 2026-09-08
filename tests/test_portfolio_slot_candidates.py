"""`slot_candidates` must agree with the motor's own eligibility rule.

The explanation of why a slot is blocked has to come from the same rule that
decided it was blocked, or the two drift and the panel starts arguing with the
verdict beside it. So `slot_candidates` takes `_eligible` as an argument and
this test calls it with the real one, over the real declared formats in
`data/portfolio_formats`, which are tracked and available everywhere.

The claim base itself is not used here: compiling it needs the SSD index and
the IRIS archive, neither of which exists in CI. The claims below are written
by hand for that reason, and every verdict about them still comes from the
motor.

Lane: `integration`. It imports FLUJO, and that is where a FLUJO import is
declared.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from cultura.mak_plataforma.copilot import slot_candidates

_eligible = pytest.importorskip(
    "flujo.knowledge.portfolio_render")._eligible

FORMATS = Path(__file__).parents[1] / "data" / "portfolio_formats"


def _slot_of(format_id, slot_id):
    spec = json.loads((FORMATS / (format_id + ".json")).read_text(encoding="utf-8"))
    return next(slot for slot in spec["slots"] if slot["slot_id"] == slot_id)


def _claim(subject, **overrides):
    """A `puedo`/`process` claim that satisfies the barberia caption grammar."""
    row = {
        "claim_id": "claim:" + subject,
        "verb": "puedo",
        "layer": "process",
        "subject": subject,
        "scope": "archive",
        "state": "candidate",
        "permission": "unnamed",
        "caption_fields": {"technique": subject, "value": "sostenido",
                           "span": "2024-2025"},
    }
    row.update(overrides)
    return row


def test_the_report_agrees_with_the_motor_on_the_real_barberia_slot():
    slot = _slot_of("F2-capacidad-barberia", "consistencia")
    passes = _claim("degrade")
    low_state = _claim("fade", state="observed")
    no_caption = _claim("corte", caption_fields={"technique": "corte"})
    off_slot = _claim("un contexto", verb="ocurrio", layer="context")
    claims = [passes, low_state, no_caption, off_slot]

    # The motor's own verdict on each claim, taken one at a time.
    accepted, _ = _eligible(slot, [passes])
    assert accepted, "the fixture must contain one claim the motor accepts"
    for rejected_claim in (low_state, no_caption, off_slot):
        rows, _ = _eligible(slot, [rejected_claim])
        assert not rows

    report = slot_candidates(slot, claims, _eligible)

    assert report["eligible_now"] == 1
    assert report["kind"] == "satisfied", "this slot asks for one and has one"
    # The one the motor accepts is never offered as a candidate to fix.
    assert "degrade" not in [row["subject"] for row in report["candidates"]]
    # And the ones it rejects are named with the motor's own reason.
    subjects = {row["subject"]: row["condition"] for row in report["candidates"]}
    assert subjects.get("fade") == "state_too_low"
    assert subjects.get("corte") == "caption_incomplete"
    assert "un contexto" not in subjects, "another layer is not this slot"


def test_the_blocked_case_is_one_condition_short_and_says_which():
    slot = _slot_of("F2-capacidad-barberia", "consistencia")
    claims = [_claim("fade", state="observed"), _claim("degrade", state="observed")]

    report = slot_candidates(slot, claims, _eligible)

    assert report["eligible_now"] == 0
    assert report["kind"] == "one_condition_short"
    assert report["needs"] == slot["count"]["min"]
    assert report["by_condition"] == {"state_too_low": 2}
    assert all(row["condition"] == "state_too_low"
               for row in report["candidates"])
    assert "state_too_low" in report["next_action"]


def test_the_real_curatorial_slot_reports_a_missing_kind_of_statement():
    """`F7-lectura-curatorial` asks for `significa` in the `curatorial` layer.

    Measured against the live chain on 2026-09-02, the archive produced 278
    claims and none of that verb or layer, so the honest answer is that the
    format asks for a kind of statement nothing produces yet -- not that
    evidence is thin.
    """
    slot = _slot_of("F7-lectura-curatorial", "lecturas")
    claims = [_claim("fade"), _claim("degrade", state="observed")]

    report = slot_candidates(slot, claims, _eligible)

    assert report["kind"] == "no_claim_of_this_kind"
    assert report["on_slot_total"] == 0
    assert report["candidates"] == []
    assert slot["claim"] in report["next_action"]
    assert slot["layer"] in report["next_action"]


def test_every_declared_format_can_be_explained_without_raising():
    """Whatever the library holds, the explanation must not be the thing that
    breaks the read-only surface showing it."""
    for path in sorted(FORMATS.glob("*.json")):
        spec = json.loads(path.read_text(encoding="utf-8"))
        for slot in spec["slots"]:
            report = slot_candidates(slot, [_claim("fade", state="observed")],
                                     _eligible)
            assert report["slot_id"] == slot["slot_id"]
            assert report["promotion"] == "none"
            assert report["owner"] == "human"
            assert report["kind"] in ("satisfied", "one_condition_short",
                                      "no_claim_of_this_kind")
