"""Attack the identity escalation: cheap evidence may reject, never accept.

The whole tool rests on one asymmetry, and each test below fails if it is
inverted or shortcut:

- two files whose tails differ ARE different, and no further reading can change
  it. Cheap rejection is final.
- two files whose tails AGREE are not yet the same file. Cheap agreement must
  escalate to a full read. Skipping that is exactly the error the index already
  documents about sample hashes, reintroduced one window size larger.
- a file no larger than the tail window is read whole, so its tail digest IS its
  full digest and may certify. This shortcut must never leak to a bigger file.
- a run that hits its byte budget must say so per asset. A tool that quietly
  drops work reads as "covered everything" to whoever consumes its output.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parents[1] / "tools" / "resolve_identity_ties.py"


def load_tool():
    spec = importlib.util.spec_from_file_location("identity_ties_mod", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ties = load_tool()


def member(name: str, size: int, *, root: str = "R", sample: str = "S"):
    return {
        "asset_id": hashlib.sha256(name.encode()).hexdigest(),
        "relative_path": name, "extension": Path(name).suffix,
        "bytes": size, "sample_sha256": sample,
        "container_root": root, "is_appledouble": False,
    }


def write(root: Path, name: str, body: bytes) -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)


BIG = ties.TAIL_BYTES * 3


def test_size_difference_certifies_distinct_for_free(tmp_path: Path) -> None:
    write(tmp_path, "A/a.bin", b"x" * 10)
    write(tmp_path, "B/b.bin", b"x" * 20)
    out = ties.resolve({"S": [member("A/a.bin", 10, root="A"),
                             member("B/b.bin", 20, root="B")]},
                       tmp_path, full_budget=None)
    assert out["stats"]["stage0_resolved"] == 2
    assert out["stats"]["bytes_read_stage1"] == 0
    assert {m["verdict"] for m in out["assets"]} == {ties.CERTIFIED_DISTINCT}


def test_tail_disagreement_certifies_distinct_without_full_read(tmp_path: Path) -> None:
    head = b"same" * (BIG // 4)
    write(tmp_path, "A/a.bin", head[:-8] + b"ENDING01")
    write(tmp_path, "B/b.bin", head[:-8] + b"ENDING02")
    size = len(head)
    out = ties.resolve({"S": [member("A/a.bin", size, root="A"),
                             member("B/b.bin", size, root="B")]},
                       tmp_path, full_budget=None)
    stats = out["stats"]
    assert stats["stage1_resolved"] == 2
    # The point: it never paid for the whole file.
    assert stats["bytes_read_stage2"] == 0
    assert {m["verdict"] for m in out["assets"]} == {ties.CERTIFIED_DISTINCT}


def test_tail_agreement_on_a_big_file_must_escalate(tmp_path: Path) -> None:
    """Cheap agreement certifies nothing. This is the load-bearing test."""
    tail = b"identical-ending" * (ties.TAIL_BYTES // 16)
    write(tmp_path, "A/a.bin", b"P" * ties.TAIL_BYTES * 2 + tail)
    write(tmp_path, "B/b.bin", b"Q" * ties.TAIL_BYTES * 2 + tail)
    size = ties.TAIL_BYTES * 2 + len(tail)
    out = ties.resolve({"S": [member("A/a.bin", size, root="A"),
                             member("B/b.bin", size, root="B")]},
                       tmp_path, full_budget=None)
    stats = out["stats"]
    assert stats["bytes_read_stage2"] > 0, "identical tails were trusted"
    # And the full read finds them different, which the tail could not.
    assert {m["verdict"] for m in out["assets"]} == {ties.CERTIFIED_DISTINCT}
    assert all(m["content_id"] is None for m in out["assets"])


def test_real_duplicate_is_certified_same_with_a_content_id(tmp_path: Path) -> None:
    body = bytes(range(256)) * (BIG // 256)
    write(tmp_path, "A/a.bin", body)
    write(tmp_path, "B/b.bin", body)
    out = ties.resolve({"S": [member("A/a.bin", len(body), root="A"),
                             member("B/b.bin", len(body), root="B")]},
                       tmp_path, full_budget=None)
    assert {m["verdict"] for m in out["assets"]} == {ties.CERTIFIED_SAME}
    ids = {m["content_id"] for m in out["assets"]}
    assert len(ids) == 1 and next(iter(ids)).startswith("sha256:")
    klasses = ties.build_classes(out["assets"])
    assert len(klasses) == 1
    klass = klasses[0]
    assert klass["member_count"] == 2
    assert klass["reclaimable_bytes"] == len(body)      # one of the two
    assert klass["crosses_roots"] is True
    assert klass["distinct_roots"] == 2


def test_small_file_is_certified_at_stage_one(tmp_path: Path) -> None:
    """The tail window covers the whole file, so the shortcut is sound here."""
    body = b"tiny-and-identical"
    write(tmp_path, "A/a.txt", body)
    write(tmp_path, "B/b.txt", body)
    out = ties.resolve({"S": [member("A/a.txt", len(body), root="A"),
                             member("B/b.txt", len(body), root="B")]},
                       tmp_path, full_budget=None)
    assert out["stats"]["bytes_read_stage2"] == 0
    assert {m["verdict"] for m in out["assets"]} == {ties.CERTIFIED_SAME}
    assert all(m["resolved_at_stage"] == 1 for m in out["assets"])
    # A full digest was still recorded, because the bytes really were all read.
    expect = "sha256:" + hashlib.sha256(body).hexdigest()
    assert {m["content_id"] for m in out["assets"]} == {expect}


def test_budget_exhaustion_is_recorded_per_asset(tmp_path: Path) -> None:
    tail = b"z" * ties.TAIL_BYTES
    write(tmp_path, "A/a.bin", b"1" * BIG + tail)
    write(tmp_path, "B/b.bin", b"2" * BIG + tail)
    size = BIG + len(tail)
    out = ties.resolve({"S": [member("A/a.bin", size, root="A"),
                             member("B/b.bin", size, root="B")]},
                       tmp_path, full_budget=1)
    assert out["stats"]["unresolved_over_budget"] == 2
    for asset in out["assets"]:
        assert asset["verdict"] == ties.UNRESOLVED
        # A cause, not a bare unknown, because the remedy differs per cause.
        assert asset["unknown_cause"]
        assert asset["note"] == "full_hash_budget_exhausted"


def test_missing_file_is_unresolved_not_distinct(tmp_path: Path) -> None:
    write(tmp_path, "A/a.bin", b"x" * BIG)
    out = ties.resolve({"S": [member("A/a.bin", BIG, root="A"),
                             member("B/gone.bin", BIG, root="B")]},
                       tmp_path, full_budget=None)
    verdicts = {m["relative_path"]: m["verdict"] for m in out["assets"]}
    assert verdicts["B/gone.bin"] == ties.UNRESOLVED
    assert out["stats"]["unreadable"] == 1


def test_duplicate_inside_one_root_is_not_a_cross_root_claim(tmp_path: Path) -> None:
    """Only a cross-root duplicate is evidence about two commissions."""
    body = b"same" * (BIG // 4)
    write(tmp_path, "A/one/x.bin", body)
    write(tmp_path, "A/two/y.bin", body)
    out = ties.resolve({"S": [member("A/one/x.bin", len(body), root="A"),
                             member("A/two/y.bin", len(body), root="A")]},
                       tmp_path, full_budget=None)
    klass = ties.build_classes(out["assets"])[0]
    assert klass["crosses_roots"] is False
    assert klass["distinct_roots"] == 1


def test_appledouble_stubs_are_labelled_not_dropped(tmp_path: Path) -> None:
    assert ties.is_appledouble("dir/._IMG_0551.JPG") is True
    assert ties.is_appledouble("dir/IMG_0551.JPG") is False
    assert ties.container_root("LYON/COMANDO/x.jpg") == "LYON"
    assert ties.container_root("./LYON/x.jpg") == "LYON"


def test_result_digest_ignores_wall_time() -> None:
    """Two identical runs must produce one digest, or reproducibility is unfalsifiable."""
    a = {"files": 10, "elapsed_seconds": 1.5, "nested": {"elapsed_seconds": 9}}
    b = {"files": 10, "elapsed_seconds": 99.9, "nested": {"elapsed_seconds": 1}}
    from flujo.runrecord import result_digest
    assert (result_digest(a, ignore=("elapsed_seconds",))
            == result_digest(b, ignore=("elapsed_seconds",)))
    assert result_digest(a) != result_digest(b)
