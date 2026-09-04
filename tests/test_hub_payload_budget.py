#!/usr/bin/env python3
"""No hub collection route may grow past its declared cost per item.

The repository ratchets its tool registry, its language and its consumer
inventory. Nothing watched response size, which is how
`/api/portfolio/copilot/map` came to answer 4,367,883 bytes so its only
consumer could read three fields per row.

The pin is bytes **per item**, not total bytes. A total depends on how many
pieces the archive holds that day: it would fail on the operator's machine and
pass vacuously on a fresh clone. Per-item cost is a property of the route's
shape and survives both.

Which is also why a small archive is reported as "not measured" rather than
"clean": a ratchet that measures nothing and says nothing is wrong is the
silent zero this repository already names elsewhere.
"""
from __future__ import annotations

import json

import pytest

from tools.hub_payload_budget import (
    BUDGET_FILE,
    MIN_ITEMS_TO_JUDGE,
    SCHEMA,
    capture,
    findings,
    load_budget,
    measure,
)


@pytest.fixture(scope="module")
def measured() -> dict:
    return measure()


@pytest.fixture(scope="module")
def budget() -> dict:
    return load_budget()


@pytest.fixture(scope="module")
def measurable(measured: dict) -> bool:
    return any(row.get("items", 0) >= MIN_ITEMS_TO_JUDGE for row in measured["routes"])


class TestBudgetFile:
    def test_the_budget_is_declared_and_travels_with_the_repo(self) -> None:
        assert BUDGET_FILE.is_file(), (
            f"{BUDGET_FILE} is missing: without it this ratchet measures nothing"
        )
        data = json.loads(BUDGET_FILE.read_text(encoding="utf-8"))
        assert data["schema"] == SCHEMA
        assert data["routes"], "an empty budget would pass forever"

    def test_every_declared_route_has_a_ceiling(self, budget: dict) -> None:
        for route, rule in budget["routes"].items():
            cap = rule.get("max_bytes_per_item")
            assert isinstance(cap, int) and cap > 0, f"{route} has no usable ceiling"

    def test_the_expensive_routes_at_scale_say_why(self, budget: dict) -> None:
        # An expensive row on twelve rows costs nothing. The same row on seven
        # thousand is the defect this file exists to catch, and a high ceiling
        # there with no reason is indistinguishable from an oversight.
        for route, rule in budget["routes"].items():
            costly = rule["max_bytes_per_item"] > 600
            at_scale = rule.get("items_at_capture", 0) >= 500
            if costly and at_scale:
                assert rule.get("note"), (
                    f"{route} is allowed {rule['max_bytes_per_item']} bytes per item "
                    f"across {rule['items_at_capture']} entries and does not say why"
                )


class TestMeasurement:
    def test_the_archive_is_large_enough_to_measure(self, measurable: bool) -> None:
        if not measurable:
            pytest.skip(
                f"no route reached {MIN_ITEMS_TO_JUDGE} items in this checkout; "
                "the per-item figure would be noise"
            )

    def test_no_route_is_over_its_declared_budget(
        self, measured: dict, budget: dict, measurable: bool
    ) -> None:
        if not measurable:
            pytest.skip("archive too small to judge")
        over = [f for f in findings(measured, budget) if f["kind"] == "sobre_presupuesto"]
        assert not over, "\n".join(f"{f['route']}: {f['detail']}" for f in over)

    def test_every_collection_route_is_declared(
        self, measured: dict, budget: dict, measurable: bool
    ) -> None:
        if not measurable:
            pytest.skip("archive too small to judge")
        undeclared = [f for f in findings(measured, budget) if f["kind"] == "sin_declarar"]
        assert not undeclared, (
            "a new collection route has no budget entry. Measure it and add one:\n"
            "  python -m tools.hub_payload_budget --capture > data/hub_payload_budget.json\n"
            + "\n".join(f"{f['route']}: {f['detail']}" for f in undeclared)
        )

    def test_no_route_raised_while_being_measured(self, measured: dict) -> None:
        broken = [row for row in measured["routes"] if "error" in row]
        assert not broken, "\n".join(f"{r['route']}: {r['error']}" for r in broken)


class TestTheRatchetActuallyCatches:
    """A ratchet nobody has seen fire is a ratchet nobody knows works."""

    def test_a_route_that_grows_is_reported(self, measured: dict, budget: dict,
                                            measurable: bool) -> None:
        if not measurable:
            pytest.skip("archive too small to judge")
        fat = [row for row in measured["routes"] if "bytes_per_item" in row]
        assert fat, "nothing was measured"
        route = fat[0]["route"]

        tightened = {
            "schema": SCHEMA,
            "routes": {
                **budget["routes"],
                route: {**budget["routes"].get(route, {}), "max_bytes_per_item": 1},
            },
        }
        reported = [f for f in findings(measured, tightened) if f["route"] == route]
        assert reported, f"{route} exceeded a 1-byte ceiling and was not reported"
        assert reported[0]["kind"] == "sobre_presupuesto"

    def test_a_new_undeclared_route_is_reported(self, measured: dict,
                                                measurable: bool) -> None:
        if not measurable:
            pytest.skip("archive too small to judge")
        empty = {"schema": SCHEMA, "routes": {}}
        assert findings(measured, empty), (
            "with an empty budget every collection route should be undeclared"
        )

    def test_capture_produces_a_budget_that_passes(self, measured: dict,
                                                   budget: dict, measurable: bool) -> None:
        if not measurable:
            pytest.skip("archive too small to judge")
        fresh = capture(measured, budget)
        assert not [
            f for f in findings(measured, fresh) if f["kind"] == "sobre_presupuesto"
        ], "--capture wrote a budget its own measurement fails"

    def test_capture_keeps_the_notes(self, measured: dict, budget: dict) -> None:
        # Regenerating the pin must not silently drop the reasons.
        annotated = [r for r, rule in budget["routes"].items() if rule.get("note")]
        if not annotated:
            pytest.skip("no notes to keep")
        fresh = capture(measured, budget)
        for route in annotated:
            assert fresh["routes"][route].get("note"), f"--capture dropped {route}'s note"
