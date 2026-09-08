#!/usr/bin/env python3
"""The repeatability contract of `tools/substrate_scan.py`, 374 lines untested.

The module exists because a previous measurement of the corpus could not be
repeated, and its docstring names why: five of the nine things a repeat needs
were never written down, and the table that got reported spliced two runs made
with two different extractor versions, so the totals corresponded to no
execution that had ever happened.

So it refuses to produce a result without a run record. The parts of that
record this module checks are the ones a walk can be held to without an XMP
extractor present:

* every error carries its path *and* the stage that produced it -- an error
  without a path is the failure mode the docstring calls out by name;
* a file that could not be hashed is still listed, because dropping it would
  shrink the denominator and make the run look cleaner than it was;
* the manifest digest is a function of what was found, not of the order the
  filesystem happened to return it in.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from tools.substrate_scan import build_manifest, output_digest

EXTENSIONS = (".jpg", ".png", ".tif")


@pytest.fixture
def corpus(tmp_path: Path) -> Path:
    root = tmp_path / "corpus"
    (root / "a" / "hondo").mkdir(parents=True)
    (root / "b").mkdir()
    (root / "uno.jpg").write_bytes(b"imagen uno")
    (root / "a" / "dos.PNG").write_bytes(b"imagen dos")
    (root / "a" / "hondo" / "tres.tif").write_bytes(b"imagen tres")
    (root / "b" / "cuatro.jpg").write_bytes(b"imagen cuatro")
    (root / "notas.txt").write_text("no es candidata", encoding="utf-8")
    (root / "sin_extension").write_bytes(b"tampoco")
    return root


def _manifest(root: Path, **overrides):
    options = {"limit": None, "hash_files": True}
    options.update(overrides)
    return build_manifest(root, EXTENSIONS, **options)


class TestWhatCountsAsACandidate:
    def test_only_the_declared_extensions_are_listed(self, corpus: Path) -> None:
        manifest = _manifest(corpus)
        listed = {row["path"] for row in manifest["entries"]}
        assert listed == {
            "uno.jpg",
            os.path.join("a", "dos.PNG"),
            os.path.join("a", "hondo", "tres.tif"),
            os.path.join("b", "cuatro.jpg"),
        }

    def test_the_extension_match_ignores_case(self, corpus: Path) -> None:
        # `dos.PNG` is a candidate; a case-sensitive match would silently
        # shrink the corpus on a disk that shouts.
        listed = {row["path"] for row in _manifest(corpus)["entries"]}
        assert os.path.join("a", "dos.PNG") in listed

    def test_the_count_matches_the_entries(self, corpus: Path) -> None:
        manifest = _manifest(corpus)
        assert manifest["files"] == len(manifest["entries"])

    def test_a_limit_is_respected(self, corpus: Path) -> None:
        assert _manifest(corpus, limit=2)["files"] == 2

    def test_an_empty_corpus_reports_zero_rather_than_failing(
        self, tmp_path: Path
    ) -> None:
        empty = tmp_path / "vacio"
        empty.mkdir()
        manifest = _manifest(empty)
        assert manifest["files"] == 0
        assert manifest["entries"] == []
        assert manifest["manifest_sha256"]


class TestEveryEntryDescribesItself:
    def test_each_entry_carries_size_and_mtime(self, corpus: Path) -> None:
        for row in _manifest(corpus)["entries"]:
            assert row["size"] > 0
            assert row["mtime_ns"] > 0

    def test_hashing_records_a_digest_per_file(self, corpus: Path) -> None:
        for row in _manifest(corpus, hash_files=True)["entries"]:
            assert len(row["sha256"]) == 64

    def test_without_hashing_no_digest_is_claimed(self, corpus: Path) -> None:
        # A run that did not hash must not leave a field that looks like it did.
        for row in _manifest(corpus, hash_files=False)["entries"]:
            assert "sha256" not in row


class TestErrorsKeepTheirPath:
    """An error without a path is the failure the module was written against."""

    def test_an_unreadable_file_is_reported_with_its_path_and_stage(
        self, corpus: Path
    ) -> None:
        blocked = corpus / "b" / "cuatro.jpg"
        blocked.chmod(0o000)
        try:
            manifest = _manifest(corpus, hash_files=True)
        finally:
            blocked.chmod(0o644)

        failures = [e for e in manifest["errors"] if e["stage"] == "hash"]
        if not failures:
            pytest.skip("this filesystem let the read through despite the mode")
        assert failures[0]["path"] == os.path.join("b", "cuatro.jpg")
        assert failures[0]["error"]

    def test_a_file_that_could_not_be_hashed_is_still_listed(
        self, corpus: Path
    ) -> None:
        # Dropping it would shrink the denominator and make the run look
        # cleaner than it was.
        blocked = corpus / "b" / "cuatro.jpg"
        blocked.chmod(0o000)
        try:
            manifest = _manifest(corpus, hash_files=True)
        finally:
            blocked.chmod(0o644)

        listed = {row["path"] for row in manifest["entries"]}
        assert os.path.join("b", "cuatro.jpg") in listed

    def test_an_unreadable_directory_is_reported_with_its_path(
        self, corpus: Path
    ) -> None:
        blocked = corpus / "a" / "hondo"
        blocked.chmod(0o000)
        try:
            manifest = _manifest(corpus, hash_files=False)
        finally:
            blocked.chmod(0o755)

        walk_errors = [e for e in manifest["errors"] if e["stage"] == "walk"]
        if not walk_errors:
            pytest.skip("this filesystem let the walk through despite the mode")
        assert any("hondo" in str(e["path"]) for e in walk_errors)

    def test_every_error_names_a_stage(self, corpus: Path) -> None:
        blocked = corpus / "b" / "cuatro.jpg"
        blocked.chmod(0o000)
        try:
            manifest = _manifest(corpus, hash_files=True)
        finally:
            blocked.chmod(0o644)
        for error in manifest["errors"]:
            assert error["stage"] in {"walk", "stat", "hash"}
            assert error["path"]


class TestTheDigestMakesRunsComparable:
    def test_the_same_corpus_yields_the_same_manifest_digest(
        self, corpus: Path
    ) -> None:
        assert _manifest(corpus)["manifest_sha256"] == _manifest(corpus)["manifest_sha256"]

    def test_a_new_candidate_changes_the_digest(self, corpus: Path) -> None:
        before = _manifest(corpus)["manifest_sha256"]
        (corpus / "cinco.jpg").write_bytes(b"imagen cinco")
        assert _manifest(corpus)["manifest_sha256"] != before

    def test_a_non_candidate_does_not_change_the_digest(self, corpus: Path) -> None:
        before = _manifest(corpus)["manifest_sha256"]
        (corpus / "otra_nota.txt").write_text("nada", encoding="utf-8")
        assert _manifest(corpus)["manifest_sha256"] == before

    def test_the_entries_come_back_in_path_order(self, corpus: Path) -> None:
        # The digest is taken over the sorted entries, so it describes what was
        # found rather than the order the filesystem happened to return.
        paths = [row["path"] for row in _manifest(corpus)["entries"]]
        assert paths == sorted(paths)

    def test_hashing_and_not_hashing_are_different_runs(self, corpus: Path) -> None:
        # Two runs whose digests match must have measured the same thing; a
        # hashed and an unhashed pass did not.
        assert (
            _manifest(corpus, hash_files=True)["manifest_sha256"]
            != _manifest(corpus, hash_files=False)["manifest_sha256"]
        )


class TestOutputDigest:
    def test_the_same_result_yields_the_same_digest(self) -> None:
        result = {"schema": "x", "rows": [1, 2, 3], "count": 3}
        assert output_digest(result) == output_digest(dict(result))

    def test_key_order_does_not_change_the_digest(self) -> None:
        assert output_digest({"a": 1, "b": 2}) == output_digest({"b": 2, "a": 1})

    def test_a_changed_value_changes_the_digest(self) -> None:
        assert output_digest({"a": 1}) != output_digest({"a": 2})
