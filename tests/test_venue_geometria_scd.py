#!/usr/bin/env python3
"""The confidence contract of `tools/venue_geometria_scd.py`, 314 lines untested.

The module builds a demo geometry of the SCD Plaza Egaña radial hall and says
plainly what it is not: "NO es una visita con instrumento: nadie firma este
archivo y ninguna cota se levantó en sala."

What makes it worth testing is the rule it states for its own confidence tiers:

    todo lo que tiene altura -- muros, balcón -- es una suposición
    (`no_verificado`), porque el plano es una planta y una planta no sabe
    cuánto mide el techo.

That is not a comment, it is a checkable invariant over the whole geometry: a
polyline with any point above the floor cannot claim to be measured. It would
break the day someone adds a wall with a height they made up, and nothing else
in the file would look wrong.
"""
from __future__ import annotations

import math

import pytest

from tools.venue_geometria_scd import (
    ANCHO_ESC,
    DERIVADO,
    MEDIDO,
    RADIO,
    SAGITA,
    SUPUESTO,
    arco,
    banda,
    geometria,
    punto,
    vertical,
)

TIERS = {"medido", "ajustado", "no_verificado"}
METHODS = {MEDIDO, DERIVADO, SUPUESTO}


@pytest.fixture(scope="module")
def polylines() -> list[dict]:
    lines, _count = geometria()
    assert lines, "the geometry came back empty; nothing below would be measured"
    return lines


class TestHeightIsNeverClaimedAsMeasured:
    """A floor plan does not know how tall the ceiling is."""

    def test_every_polyline_with_height_is_unverified(self, polylines) -> None:
        overclaimed = [
            line["etiqueta"]
            for line in polylines
            if any(point[2] > 0 for point in line["puntos"])
            and line["confianza"] != "no_verificado"
        ]
        assert not overclaimed, (
            "these carry a height and do not admit it is assumed:\n  "
            + "\n  ".join(overclaimed)
        )

    def test_there_is_height_to_check(self, polylines) -> None:
        # Without this the invariant above passes on a flat drawing while
        # measuring nothing.
        with_height = [
            line for line in polylines
            if any(point[2] > 0 for point in line["puntos"])
        ]
        assert len(with_height) >= 10, (
            f"only {len(with_height)} polylines have height; the rule about "
            "heights would be vacuous"
        )

    def test_an_unverified_line_declares_the_assumption_as_its_method(
        self, polylines
    ) -> None:
        for line in polylines:
            if line["confianza"] == "no_verificado":
                assert line["metodo"] == SUPUESTO, (
                    f"{line['etiqueta']} is unverified but its method reads "
                    f"{line['metodo']!r}"
                )

    def test_the_floor_is_where_the_measured_lines_are(self, polylines) -> None:
        for line in polylines:
            if line["confianza"] == "medido":
                assert all(point[2] == 0 for point in line["puntos"]), (
                    f"{line['etiqueta']} is claimed measured and leaves the floor"
                )


class TestEveryLineDeclaresItself:
    def test_each_polyline_carries_the_five_fields(self, polylines) -> None:
        for line in polylines:
            assert set(line) == {
                "puntos", "confianza", "etiqueta", "capa", "metodo"
            }, line.get("etiqueta")

    def test_each_confidence_is_one_of_the_three_declared_tiers(
        self, polylines
    ) -> None:
        for line in polylines:
            assert line["confianza"] in TIERS, line["etiqueta"]

    def test_each_method_is_one_of_the_declared_reasons(self, polylines) -> None:
        for line in polylines:
            assert line["metodo"] in METHODS, line["etiqueta"]

    def test_all_three_tiers_are_actually_used(self, polylines) -> None:
        # A tier system with one tier in it is a label, not a system.
        used = {line["confianza"] for line in polylines}
        assert used == TIERS, f"only {sorted(used)} appear"

    def test_no_polyline_is_unlabelled(self, polylines) -> None:
        for line in polylines:
            assert line["etiqueta"].strip()
            assert line["capa"].strip()

    def test_every_point_is_three_dimensional(self, polylines) -> None:
        for line in polylines:
            for point in line["puntos"]:
                assert len(point) == 3, line["etiqueta"]


class TestTheRadialModelMatchesItsOwnDocumentation:
    def test_the_radius_follows_from_the_chord_and_the_sagitta(self) -> None:
        # The docstring states chord 10 m, sagitta 0,9 m, radius 14,34 m. That
        # is arithmetic, so it can be checked rather than trusted.
        expected = (SAGITA ** 2 + (ANCHO_ESC / 2) ** 2) / (2 * SAGITA)
        assert RADIO == pytest.approx(expected)
        assert RADIO == pytest.approx(14.34, abs=0.01)

    def test_a_point_sits_on_the_circle_it_was_built_from(self) -> None:
        from tools.venue_geometria_scd import Y_CENTRO

        p = punto(RADIO, math.radians(12.0))
        distance = math.hypot(p[0], p[1] - Y_CENTRO)
        assert distance == pytest.approx(RADIO, abs=0.01)

    def test_an_arc_keeps_every_point_at_its_radius(self) -> None:
        from tools.venue_geometria_scd import Y_CENTRO

        for p in arco(8.0, math.radians(-20), math.radians(20), 12):
            assert math.hypot(p[0], p[1] - Y_CENTRO) == pytest.approx(8.0, abs=0.01)

    def test_an_arc_honours_a_requested_height(self) -> None:
        assert all(p[2] == pytest.approx(3.2) for p in
                   arco(8.0, 0.0, math.radians(10), 4, z=3.2))

    def test_a_seating_band_closes_on_itself(self) -> None:
        # A row has depth, so it is drawn as a closed band; an open one would
        # render as a stray line.
        strip = banda(8.0, math.radians(-10), math.radians(10), 6)
        assert strip[0] == strip[-1]

    def test_a_vertical_rises_from_the_point_it_is_given(self) -> None:
        base = [1.0, 2.0, 0.0]
        line = vertical(base, 6.0)
        assert line[0][:2] == base[:2]
        assert max(p[2] for p in line) == pytest.approx(6.0)


class TestDeterminism:
    def test_two_runs_produce_the_same_geometry(self) -> None:
        # The file is regenerated and compared with --check, so a run that
        # differs from itself would report a drift that never happened.
        first, first_count = geometria()
        second, second_count = geometria()
        assert first == second
        assert first_count == second_count

    def test_the_second_value_is_a_seat_count_not_a_point_count(
        self, polylines
    ) -> None:
        # It is `butacas + butacas_bal`. I first read it as the number of
        # points drawn, which is 559 against a reported 293 -- the kind of
        # mistake that turns a stall count into geometry trivia in a report.
        _lines, seats = geometria()
        points = sum(len(line["puntos"]) for line in polylines)
        assert seats != points
        assert 0 < seats < points

    def test_the_seat_count_has_seating_to_come_from(self, polylines) -> None:
        seating = [line for line in polylines if line["capa"].startswith("butacas")]
        assert seating, "a seat count with no seating polyline is unattached"
        _lines, seats = geometria()
        assert seats >= len(seating), (
            "fewer seats than seating blocks: the count is not counting stalls"
        )
