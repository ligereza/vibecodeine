#!/usr/bin/env python3
"""The RD service tariff must say the same price everywhere it is written.

`data/rd_packs.json` opens by declaring itself the single source, and it says
why: the tariff used to live hardcoded in two copies -- `src/flujo/plano/packs.py`
and `web/src/rdBrand.ts` -- that could drift apart. Consolidating them into one
editable file was the fix.

The consolidation missed a third copy. `data/rd.db` carries its own `packs`
table with `precio`, and it is read by a different path: `flujo.rd.database`
serves the RD panel and the crosswalk from the database, while
`flujo.plano.packs` quotes from the JSON. So the same pack can be quoted at one
price by `flujo plano --costs` and displayed at another by the panel, and
nothing would say so.

Measured 2026-09-05, the three agree: INFO 250.000, TESTEO 300.000, COMPLETO
500.000. This keeps them agreeing. It is not a claim that the prices are
correct -- only the operator decides that -- but that there is one answer.

If this fails, `data/rd_packs.json` is the one to edit: it is the file the
comment inside it says a human maintains by hand. The database is loaded from
elsewhere and should follow.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TARIFF = REPO / "data" / "rd_packs.json"
DATABASE = REPO / "data" / "rd.db"


def _tariff() -> dict[str, dict]:
    return json.loads(TARIFF.read_text(encoding="utf-8"))["packs"]


def _database_packs() -> dict[str, tuple[str, int]]:
    connection = sqlite3.connect(f"file:{DATABASE}?mode=ro", uri=True)
    try:
        return {
            str(row[0]): (str(row[1]), int(row[2]))
            for row in connection.execute("SELECT id, nombre, precio FROM packs")
        }
    finally:
        connection.close()


class TestBothSourcesArePresent:
    def test_the_tariff_travels_with_the_repository(self) -> None:
        # It is inside `data/`, which `.gitignore` excludes with an allowlist
        # below it. The allowlist exists because `rd_packs.json` was declared
        # the single source and then did not enter the repo, so every other
        # checkout quoted from the fallback copy.
        assert TARIFF.is_file(), f"{TARIFF} is missing: the tariff is the source"

    def test_the_database_travels_with_the_repository(self) -> None:
        assert DATABASE.is_file(), f"{DATABASE} is missing"

    def test_neither_is_empty(self) -> None:
        assert _tariff(), "the tariff declares no pack"
        assert _database_packs(), "the database carries no pack"


class TestTheTariffSaysOnePrice:
    def test_the_two_sources_declare_the_same_packs(self) -> None:
        tariff = set(_tariff())
        database = set(_database_packs())
        assert tariff == database, (
            f"only in the tariff: {sorted(tariff - database)}; "
            f"only in the database: {sorted(database - tariff)}"
        )

    def test_every_pack_costs_the_same_in_both(self) -> None:
        tariff = _tariff()
        database = _database_packs()
        disagreements = [
            f"{pack}: rd_packs.json says {tariff[pack]['precio']}, "
            f"rd.db says {price}"
            for pack, (_, price) in sorted(database.items())
            if pack in tariff and tariff[pack]["precio"] != price
        ]
        assert not disagreements, (
            "the same pack is quoted at two prices. `flujo plano --costs` reads "
            "the tariff and the RD panel reads the database, so a customer can "
            "be quoted one figure and shown another:\n  "
            + "\n  ".join(disagreements)
            + "\nEdit `data/rd_packs.json`: it is the source a human maintains."
        )

    def test_no_price_is_zero_or_negative(self) -> None:
        # A pack that costs nothing is a data error that reads as a decision.
        for pack, body in sorted(_tariff().items()):
            assert body["precio"] > 0, f"{pack} is quoted at {body['precio']}"


class TestTheGateIsArmed:
    """A comparison nobody has seen fail is a comparison nobody knows works."""

    @pytest.mark.parametrize("delta", [1, -1, 50_000])
    def test_a_single_changed_price_is_caught(self, delta: int) -> None:
        tariff = _tariff()
        database = _database_packs()
        pack = sorted(database)[0]
        tampered = dict(database)
        tampered[pack] = (database[pack][0], database[pack][1] + delta)

        disagreements = [
            key for key, (_, price) in tampered.items()
            if key in tariff and tariff[key]["precio"] != price
        ]
        assert disagreements == [pack], (
            f"moving {pack} by {delta} went unnoticed by the comparison"
        )

    def test_a_pack_missing_from_one_side_is_caught(self) -> None:
        tariff = set(_tariff())
        database = set(_database_packs())
        assert tariff - (database - {sorted(database)[0]}), (
            "dropping a pack from the database left the sets equal"
        )
