"""The evidence gate of `cultura/mak_curatoria/ingesta_archivo.py`.

That module is 882 statements at about 9% coverage and it is live:
`cultura/mak_conductor/handler_registry.py` calls into it at nine separate
points. This file covers the part with the most consequence -- the gate that
decides whether the organism may route an asset to a judge -- and it asserts on
the RESULT of each call, never merely that the call did not raise.

The doctrine being pinned, in the module's own words: `ROUTE_TO_JUDGE` "is not
approval", and a candidate produced by one pipeline "is not a second
independent source". Both were unpinned until now, which meant either could
have been loosened by accident and no test would have said so.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cultura.mak_curatoria import ingesta_archivo  # noqa: E402

ASSET = "asset-under-test"


@pytest.fixture()
def conn(tmp_path: Path):
    """A real schema on a throwaway path -- never MAK's production database.

    `observations` has a foreign key onto `assets`, so the row has to exist
    first or every write fails with IntegrityError. Discovered by writing this
    fixture the lazy way and watching six tests fail at once.
    """
    connection = ingesta_archivo.connect(tmp_path)
    connection.execute(
        "INSERT OR IGNORE INTO assets(asset_id, source_key, relative_path, extension,"
        " media_kind, bytes, mtime_ns, hash_state, indexed_at)"
        " VALUES (?, 'rd', 'poster.png', '.png', 'image', 1024, 0, 'done', '2026-08-31')",
        (ASSET,))
    connection.commit()
    yield connection
    connection.close()


def _relation(connection, relation: str, status: str, right: str = "other") -> None:
    connection.execute(
        "INSERT OR REPLACE INTO relations(left_id, relation, right_id, status, evidence_json) "
        "VALUES (?, ?, ?, ?, ?)", (ASSET, relation, right, status, "{}"))
    connection.commit()


# ---------------------------------------------------------------------------
# The gate's four routes, each reached on purpose
# ---------------------------------------------------------------------------

def test_gate_without_an_asset_defers_and_names_the_reason(conn):
    result = ingesta_archivo.build_evidence_gate(conn, "   ")
    assert result["route"] == "DEFERRED"
    assert result["reason"] == "asset_missing"
    assert result["promotion"] == "none"


def test_gate_with_no_evidence_defers_instead_of_guessing(conn):
    result = ingesta_archivo.build_evidence_gate(conn, ASSET)
    assert result["route"] == "DEFERRED"
    assert result["reason"] == "insufficient_independent_evidence_branches"
    assert result["active_branches"] == []
    assert result["minimum_independent_branches"] == 2


def test_gate_routes_to_judge_only_with_two_independent_branches(conn):
    ingesta_archivo.store_observation(conn, ASSET, "structure", "layers", {"n": 3})
    conn.commit()
    one = ingesta_archivo.build_evidence_gate(conn, ASSET)
    assert one["route"] == "DEFERRED", "una sola rama no alcanza"
    assert one["branches"]["structure"] is True

    _relation(conn, "visual_similarity_candidate", "candidate")
    two = ingesta_archivo.build_evidence_gate(conn, ASSET)
    assert two["route"] == "ROUTE_TO_JUDGE"
    assert two["reason"] == "independent_evidence_branches_available"
    assert set(two["active_branches"]) >= {"structure", "visual"}
    assert two["promotion"] == "none", "enrutar no es aprobar"


def test_a_candidate_from_one_pipeline_is_not_a_second_source(conn):
    """The doctrine most at risk of being loosened by accident."""
    ingesta_archivo.store_observation(conn, ASSET, "structure", "layers", {"n": 3})
    _relation(conn, "visual_similarity_candidate", "candidate")
    assert ingesta_archivo.build_evidence_gate(conn, ASSET)["route"] == "ROUTE_TO_JUDGE"

    conn.execute("INSERT OR REPLACE INTO candidates(asset_id, kind, value, status, "
                 "evidence_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                 (ASSET, "producer", "Some Producer", "candidate", "{}", "2026-08-31"))
    conn.commit()
    result = ingesta_archivo.build_evidence_gate(conn, ASSET)
    assert result["route"] == "ABSTAIN"
    assert result["reason"] == "identity_quorum_not_proven"
    assert result["identity_candidate_count"] == 1
    assert result["identity_candidate_kinds"] == ["producer"]


def test_a_divergence_relation_abstains_and_keeps_the_conflict(conn):
    ingesta_archivo.store_observation(conn, ASSET, "structure", "layers", {"n": 3})
    _relation(conn, "visual_similarity_candidate", "candidate")
    _relation(conn, "lineage_context_divergence_candidate", "candidate", right="rival")
    result = ingesta_archivo.build_evidence_gate(conn, ASSET)
    assert result["route"] == "ABSTAIN"
    assert result["reason"] == "evidence_conflict_requires_judge"
    assert any(c["relation"] == "lineage_context_divergence_candidate"
               for c in result["conflicts"]), "el conflicto se conserva, no se resume"


def test_gate_survives_a_database_without_the_evidence_tables(tmp_path: Path):
    """Absence must be named, not raised, and not read as health."""
    bare = sqlite3.connect(tmp_path / "bare.sqlite")
    bare.execute("CREATE TABLE observations (asset_id TEXT, observer TEXT, field TEXT,"
                 " value_json TEXT, status TEXT, observed_at TEXT,"
                 " UNIQUE(asset_id, observer, field))")
    bare.commit()
    result = ingesta_archivo.build_evidence_gate(bare, ASSET)
    assert result["route"] == "DEFERRED"
    assert result["branches"]["visual"] is False
    assert result["coverage"] == {"status": "unmeasured", "match_type": ""}
    bare.close()


def test_strong_coverage_counts_as_a_branch_and_weak_does_not(conn):
    # `asset_coverage` is NOT created by `connect()`: the gate reads it inside a
    # try/except and degrades to "unmeasured" when it is absent. So the branch
    # can only be exercised by bringing the table, which is itself worth
    # knowing -- on a fresh database this branch is permanently False.
    conn.execute("CREATE TABLE IF NOT EXISTS asset_coverage (asset_id TEXT,"
                 " status TEXT, match_type TEXT)")
    for status, expected in (("weak", False), ("strong", True)):
        conn.execute("DELETE FROM asset_coverage WHERE asset_id=?", (ASSET,))
        conn.execute("INSERT INTO asset_coverage(asset_id, status, match_type) "
                     "VALUES (?, ?, ?)", (ASSET, status, "phash"))
        conn.commit()
        result = ingesta_archivo.build_evidence_gate(conn, ASSET)
        assert result["branches"]["coverage"] is expected
        assert result["coverage"]["status"] == status


def test_the_gate_records_its_own_routing_as_an_observation(conn):
    ingesta_archivo.build_evidence_gate(conn, ASSET)
    row = conn.execute("SELECT value_json, status FROM observations WHERE asset_id=? "
                       "AND observer='organism_gate'", (ASSET,)).fetchone()
    assert row is not None, "la decision del gate queda registrada"
    assert json.loads(row[0])["schema"] == "mak-organism-evidence-gate-v1"


# ---------------------------------------------------------------------------
# canonical_producer: an exact identity or nothing
# ---------------------------------------------------------------------------

def test_canonical_producer_needs_an_exact_normalized_identity():
    catalog = sorted((ROOT / "data" / "productoras").glob("*.json"))
    if not catalog:
        pytest.skip("no hay catalogo de productoras en data/productoras/")
    record = json.loads(catalog[0].read_text(encoding="utf-8"))
    name = str(record.get("name") or "")
    if not name:
        pytest.skip("la primera ficha del catalogo no declara nombre")

    hit = ingesta_archivo.canonical_producer(name)
    assert hit is not None and hit["record"].get("name") == name

    noisy = ingesta_archivo.canonical_producer(f"  {name.upper()}!!  ")
    assert noisy is not None, "normaliza mayusculas, espacios y puntuacion"

    assert ingesta_archivo.canonical_producer(name + "zzq") is None, \
        "no hace coincidencia parcial: un nombre parecido no es el mismo"
    assert ingesta_archivo.canonical_producer("") is None
