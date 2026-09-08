#!/usr/bin/env python3
"""The epistemic contract of `tools/resolve_identity_ties.py`, 396 lines untested.

The tool exists because a sample hash is not an identity: two files can agree
on a sample and differ in full content. Its whole value is that it refuses to
turn a cheap agreement into a decision. That refusal is a property of the code,
and nothing checked it.

The contract, in the order the tool applies it:

    stage 0   a size disagreement certifies difference, for free
    stage 1   a whole-file digest is the only thing that certifies sameness

and the failure modes must degrade to `UNRESOLVED`, never to a verdict: an
unreadable file, or a budget that ran out, cannot be allowed to read as
"these are the same file".

The strongest assertion here is the cross-cutting one: no member is ever
`CERTIFIED_SAME` without a recorded whole-file digest, whatever path through
the code produced it.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tools.resolve_identity_ties import (
    CERTIFIED_DISTINCT,
    CERTIFIED_SAME,
    UNRESOLVED,
    build_classes,
    container_root,
    digest_whole,
    is_appledouble,
    resolve,
)


def _member(relative: str, size: int, sample: str = "sample-a") -> dict:
    return {
        "asset_id": relative,
        "relative_path": relative,
        "extension": Path(relative).suffix,
        "bytes": size,
        "sample_sha256": sample,
        "container_root": container_root(relative),
        "is_appledouble": is_appledouble(relative),
    }


@pytest.fixture
def disk(tmp_path: Path):
    """Write a file under the scan root and return its tie member."""
    def write(relative: str, content: bytes, sample: str = "sample-a") -> dict:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return _member(relative, len(content), sample)

    write.root = tmp_path  # type: ignore[attr-defined]
    return write


class TestNothingIsEverCertifiedSameWithoutReadingIt:
    """The one assertion that has to hold on every path through the tool."""

    def _assert_invariant(self, outcome: dict) -> None:
        for member in outcome["assets"]:
            if member["verdict"] == CERTIFIED_SAME:
                assert member.get("full_sha256"), (
                    f"{member['relative_path']} was certified identical with no "
                    "whole-file digest recorded"
                )
                assert member.get("content_id", "").startswith("sha256:")

    def test_on_identical_files(self, disk) -> None:
        members = [disk("a/uno.bin", b"mismo"), disk("b/dos.bin", b"mismo")]
        self._assert_invariant(resolve({"sample-a": members}, disk.root, full_budget=None))

    def test_on_files_that_only_share_a_size(self, disk) -> None:
        members = [disk("a/uno.bin", b"aaaaa"), disk("b/dos.bin", b"bbbbb")]
        self._assert_invariant(resolve({"sample-a": members}, disk.root, full_budget=None))

    def test_when_the_budget_runs_out(self, disk) -> None:
        members = [disk("a/uno.bin", b"mismo"), disk("b/dos.bin", b"mismo")]
        self._assert_invariant(resolve({"sample-a": members}, disk.root, full_budget=1))

    def test_when_a_file_cannot_be_read(self, disk) -> None:
        members = [disk("a/uno.bin", b"mismo"), _member("b/ausente.bin", 5)]
        self._assert_invariant(resolve({"sample-a": members}, disk.root, full_budget=None))


class TestStageZeroIsFree:
    def test_a_lone_size_is_certified_distinct_without_reading(self, disk) -> None:
        members = [disk("a/corto.bin", b"ab"), disk("b/largo.bin", b"abcdef")]
        outcome = resolve({"sample-a": members}, disk.root, full_budget=None)

        assert outcome["stats"]["stage0_resolved"] == 2
        assert outcome["stats"]["bytes_read_stage1"] == 0, (
            "a size disagreement was paid for with a read"
        )
        assert {m["verdict"] for m in outcome["assets"]} == {CERTIFIED_DISTINCT}

    def test_a_size_difference_never_yields_a_content_id(self, disk) -> None:
        members = [disk("a/corto.bin", b"ab"), disk("b/largo.bin", b"abcdef")]
        outcome = resolve({"sample-a": members}, disk.root, full_budget=None)
        assert all(m["content_id"] is None for m in outcome["assets"])


class TestStageOneDecides:
    def test_same_size_same_bytes_is_certified_same(self, disk) -> None:
        members = [disk("a/uno.bin", b"identico"), disk("b/dos.bin", b"identico")]
        outcome = resolve({"sample-a": members}, disk.root, full_budget=None)

        assert {m["verdict"] for m in outcome["assets"]} == {CERTIFIED_SAME}
        assert len({m["content_id"] for m in outcome["assets"]}) == 1
        assert outcome["stats"]["bytes_read_stage1"] == len(b"identico") * 2

    def test_same_size_different_bytes_is_certified_distinct(self, disk) -> None:
        # The case the whole tool exists for: a shared sample that is not a
        # shared identity.
        members = [disk("a/uno.bin", b"aaaaa"), disk("b/dos.bin", b"bbbbb")]
        outcome = resolve({"sample-a": members}, disk.root, full_budget=None)

        assert {m["verdict"] for m in outcome["assets"]} == {CERTIFIED_DISTINCT}
        assert all(m["content_id"] is None for m in outcome["assets"])
        assert outcome["stats"]["stage1_resolved"] == 2

    def test_three_files_split_into_the_right_classes(self, disk) -> None:
        members = [
            disk("a/uno.bin", b"grupo"),
            disk("b/dos.bin", b"grupo"),
            disk("c/tres.bin", b"solos"),
        ]
        outcome = resolve({"sample-a": members}, disk.root, full_budget=None)
        by_path = {m["relative_path"]: m for m in outcome["assets"]}

        assert by_path["a/uno.bin"]["verdict"] == CERTIFIED_SAME
        assert by_path["b/dos.bin"]["verdict"] == CERTIFIED_SAME
        assert by_path["c/tres.bin"]["verdict"] == CERTIFIED_DISTINCT
        assert by_path["a/uno.bin"]["content_id"] == by_path["b/dos.bin"]["content_id"]


class TestFailureDegradesToUnresolved:
    def test_an_unreadable_file_is_unresolved_not_decided(self, disk) -> None:
        members = [disk("a/uno.bin", b"mismo"), _member("b/ausente.bin", 5)]
        outcome = resolve({"sample-a": members}, disk.root, full_budget=None)
        missing = [m for m in outcome["assets"] if m["relative_path"] == "b/ausente.bin"]

        assert missing and missing[0]["verdict"] == UNRESOLVED
        assert missing[0]["content_id"] is None
        assert missing[0]["unknown_cause"]
        assert outcome["stats"]["unreadable"] == 1

    def test_an_exhausted_budget_is_unresolved_not_certified(self, disk) -> None:
        # Running out of money must not read as "these are the same file".
        members = [disk("a/uno.bin", b"identico"), disk("b/dos.bin", b"identico")]
        outcome = resolve({"sample-a": members}, disk.root, full_budget=1)

        assert {m["verdict"] for m in outcome["assets"]} == {UNRESOLVED}
        assert outcome["stats"]["unresolved_over_budget"] == 2
        assert outcome["stats"]["bytes_read_stage1"] == 0
        assert all(m["note"] == "full_hash_budget_exhausted" for m in outcome["assets"])

    def test_a_generous_budget_decides_the_same_input(self, disk) -> None:
        # Guards the budget test above from passing because of something else.
        members = [disk("a/uno.bin", b"identico"), disk("b/dos.bin", b"identico")]
        outcome = resolve({"sample-a": members}, disk.root, full_budget=10_000)
        assert {m["verdict"] for m in outcome["assets"]} == {CERTIFIED_SAME}


class TestAccounting:
    def test_every_input_asset_appears_in_the_output(self, disk) -> None:
        # A tool that silently drops an input cannot be checked against the
        # index it read from -- the module says so about AppleDouble stubs.
        members = [
            disk("a/uno.bin", b"aaa"),
            disk("b/dos.bin", b"aaa"),
            disk("c/tres.bin", b"bbbb"),
            _member("d/ausente.bin", 3),
        ]
        outcome = resolve({"sample-a": members}, disk.root, full_budget=None)
        assert len(outcome["assets"]) == len(members)
        assert {m["relative_path"] for m in outcome["assets"]} == {
            m["relative_path"] for m in members
        }

    def test_the_naive_cost_is_the_sum_of_every_input(self, disk) -> None:
        members = [disk("a/uno.bin", b"aaa"), disk("b/dos.bin", b"aaa")]
        outcome = resolve({"sample-a": members}, disk.root, full_budget=None)
        assert outcome["stats"]["bytes_if_naive"] == 6

    def test_group_and_asset_counts_are_reported(self, disk) -> None:
        groups = {
            "sample-a": [disk("a/uno.bin", b"aaa"), disk("b/dos.bin", b"aaa")],
            "sample-b": [disk("c/tres.bin", b"bb", "sample-b")],
        }
        outcome = resolve(groups, disk.root, full_budget=None)
        assert outcome["stats"]["groups"] == 2
        assert outcome["stats"]["assets"] == 3


class TestPureHelpers:
    @pytest.mark.parametrize(
        "relative,expected",
        [
            ("obra/uno.bin", "obra"),
            ("./obra/uno.bin", "obra"),
            ("uno.bin", "uno.bin"),
            ("a/b/c.bin", "a"),
        ],
    )
    def test_container_root(self, relative: str, expected: str) -> None:
        assert container_root(relative) == expected

    @pytest.mark.parametrize(
        "relative,expected",
        [
            ("a/._obra.psd", True),
            ("._obra.psd", True),
            ("a/obra.psd", False),
            ("a/_obra.psd", False),
            ("a/b._c.psd", False),
        ],
    )
    def test_appledouble_is_recognised_by_the_filename_only(
        self, relative: str, expected: bool
    ) -> None:
        assert is_appledouble(relative) is expected

    def test_digest_whole_reports_what_it_read(self, tmp_path: Path) -> None:
        target = tmp_path / "x.bin"
        target.write_bytes(b"contenido")
        digest, read = digest_whole(target)
        assert read == len(b"contenido")
        assert len(digest) == 64


class TestBuildClasses:
    def test_only_certified_sameness_forms_a_class(self, disk) -> None:
        members = [
            disk("a/uno.bin", b"grupo"),
            disk("b/dos.bin", b"grupo"),
            disk("c/tres.bin", b"otros"),
        ]
        outcome = resolve({"sample-a": members}, disk.root, full_budget=None)
        classes = build_classes(outcome["assets"])

        assert len(classes) == 1, "a distinct file was folded into a class"
        assert classes[0]["member_count"] == 2
        assert classes[0]["bytes_each"] == len(b"grupo")
        assert classes[0]["total_bytes"] == len(b"grupo") * 2

    def test_reclaimable_bytes_keeps_one_copy(self, disk) -> None:
        # The figure is what a deduplication would free, and this tool never
        # deletes: keeping one copy is the whole difference.
        members = [disk(f"r{i}/x.bin", b"ocho__by") for i in range(3)]
        outcome = resolve({"sample-a": members}, disk.root, full_budget=None)
        klass = build_classes(outcome["assets"])[0]

        assert klass["member_count"] == 3
        assert klass["reclaimable_bytes"] == klass["bytes_each"] * 2
        assert klass["reclaimable_bytes"] < klass["total_bytes"]

    def test_a_class_reports_whether_it_crosses_roots(self, disk) -> None:
        crossing = [disk("a/uno.bin", b"cruza"), disk("b/dos.bin", b"cruza")]
        klass = build_classes(
            resolve({"sample-a": crossing}, disk.root, full_budget=None)["assets"]
        )[0]
        assert klass["crosses_roots"] is True
        assert klass["distinct_roots"] == 2
        assert klass["roots"] == ["a", "b"]

    def test_a_class_inside_one_root_says_so(self, disk) -> None:
        same_root = [disk("a/uno.bin", b"mismo"), disk("a/dos.bin", b"mismo")]
        klass = build_classes(
            resolve({"sample-a": same_root}, disk.root, full_budget=None)["assets"]
        )[0]
        assert klass["crosses_roots"] is False
        assert klass["distinct_roots"] == 1

    def test_an_all_appledouble_class_is_labelled(self, disk) -> None:
        stubs = [disk("a/._obra.psd", b"stub"), disk("b/._obra.psd", b"stub")]
        klass = build_classes(
            resolve({"sample-a": stubs}, disk.root, full_budget=None)["assets"]
        )[0]
        assert klass["all_appledouble"] is True

    def test_no_class_is_built_from_unresolved_members(self, disk) -> None:
        members = [disk("a/uno.bin", b"identico"), disk("b/dos.bin", b"identico")]
        outcome = resolve({"sample-a": members}, disk.root, full_budget=1)
        assert build_classes(outcome["assets"]) == []
