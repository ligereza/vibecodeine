#!/usr/bin/env python3
"""Safety contracts for `tools/mak_merge_roots.py`, 566 lines with no witness.

This tool copies real files between real roots on the operator's box. Its
docstring makes four promises that decide whether it is safe to run at all,
and nothing in the suite checked any of them:

* source roots are never removed by ``--apply``;
* identical content is kept once and logged, not copied twice;
* divergent content never overwrites the destination -- the incoming version is
  preserved under ``_archive/<run>/variants/<source-id>/``;
* every applied copy is verified by hash after writing.

To that this module adds one the docstring only implies: ``.env`` and its
siblings are in ``SKIP_FILES``, so a merge must never carry secrets into the
destination.

Every test drives explicit tmp roots. `archive_run` only reaches the real
`/home/mak/_archive` when the destination *is* `/home/mak`, which no test here
passes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.mak_merge_roots import (
    DEFAULT_DEST,
    RUN_ID,
    SKIP_FILES,
    apply_plan,
    archive_run,
    build_plan,
    sha256,
)


def _tree(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


@pytest.fixture
def roots(tmp_path: Path) -> tuple[Path, Path]:
    """A source with one shared, one unique, one divergent file and a secret."""
    source = tmp_path / "origen" / "flujo"
    destination = tmp_path / "destino"
    (source / "sub").mkdir(parents=True)
    destination.mkdir(parents=True)

    (source / "igual.txt").write_text("mismo contenido", encoding="utf-8")
    (source / "solo_origen.txt").write_text("solo aqui", encoding="utf-8")
    (source / "divergente.txt").write_text("version del origen", encoding="utf-8")
    (source / ".env").write_text("SECRETO=no_copiar", encoding="utf-8")
    (source / "sub" / "hondo.txt").write_text("anidado", encoding="utf-8")

    (destination / "igual.txt").write_text("mismo contenido", encoding="utf-8")
    (destination / "divergente.txt").write_text("version del destino", encoding="utf-8")
    return source, destination


@pytest.fixture
def merged(roots) -> tuple[Path, Path, dict, dict]:
    source, destination = roots
    plan = build_plan([source], destination)
    result = apply_plan(plan)
    return source, destination, plan, result


class TestTheSourceSurvives:
    def test_apply_leaves_every_source_file_byte_identical(self, roots) -> None:
        source, destination = roots
        before = _tree(source)
        apply_plan(build_plan([source], destination))
        assert _tree(source) == before

    def test_apply_removes_no_source_root(self, merged) -> None:
        source, _destination, _plan, _result = merged
        assert source.is_dir(), "--apply removed the source root"

    def test_apply_retires_nothing_unless_asked(self, merged) -> None:
        _source, _destination, _plan, result = merged
        assert result["retired"] == 0


class TestDivergentContentIsNeverOverwritten:
    def test_the_destination_keeps_its_own_version(self, merged) -> None:
        _source, destination, _plan, _result = merged
        assert (destination / "divergente.txt").read_text(encoding="utf-8") == (
            "version del destino"
        )

    def test_the_incoming_version_is_preserved_as_a_variant(self, merged) -> None:
        _source, destination, _plan, _result = merged
        variants = list((archive_run(destination) / "variants").rglob("divergente.txt"))
        assert variants, "the divergent incoming file was dropped instead of preserved"
        assert variants[0].read_text(encoding="utf-8") == "version del origen"

    def test_the_conflict_is_named_in_the_plan(self, merged) -> None:
        _source, _destination, plan, _result = merged
        operations = {action["operation"] for action in plan["actions"]}
        assert "conflict_existing_unhashed" in operations


class TestIdenticalContentIsKeptOnce:
    def test_an_identical_file_is_logged_as_a_duplicate(self, merged) -> None:
        _source, _destination, plan, _result = merged
        duplicates = [
            action for action in plan["actions"]
            if action["operation"] == "duplicate_exact_existing"
        ]
        assert duplicates, "the shared file was not recognised as already present"

    def test_a_duplicate_is_not_copied_again(self, merged) -> None:
        _source, _destination, plan, result = merged
        copies = [a for a in plan["actions"] if a["operation"] == "copy_unique"]
        assert result["applied"] == len(copies) + 1, (
            "applied count does not match the unique copies plus the preserved variant"
        )


class TestUniqueContentArrives:
    def test_a_file_only_in_the_source_reaches_the_destination(self, merged) -> None:
        _source, destination, _plan, _result = merged
        assert (destination / "solo_origen.txt").read_text(encoding="utf-8") == "solo aqui"

    def test_nested_paths_are_preserved(self, merged) -> None:
        _source, destination, _plan, _result = merged
        assert (destination / "sub" / "hondo.txt").read_text(encoding="utf-8") == "anidado"


class TestSecretsAreNeverMerged:
    def test_dotenv_does_not_reach_the_destination(self, merged) -> None:
        _source, destination, _plan, _result = merged
        assert not (destination / ".env").exists(), "the merge carried a secret across"

    def test_no_action_in_the_plan_names_a_skipped_secret(self, merged) -> None:
        _source, _destination, plan, _result = merged
        for action in plan["actions"]:
            name = Path(str(action.get("destination_rel") or "")).name
            assert name not in SKIP_FILES, f"{name} was planned for copy"

    @pytest.mark.parametrize("secret", sorted(SKIP_FILES))
    def test_every_declared_secret_name_is_skipped(
        self, tmp_path: Path, secret: str
    ) -> None:
        source = tmp_path / "origen" / "flujo"
        destination = tmp_path / "destino"
        source.mkdir(parents=True)
        destination.mkdir(parents=True)
        (source / secret).write_text("SECRETO=x", encoding="utf-8")
        (source / "normal.txt").write_text("ok", encoding="utf-8")

        apply_plan(build_plan([source], destination))

        assert (destination / "normal.txt").is_file(), "the merge did nothing at all"
        assert not (destination / secret).exists(), f"{secret} was merged"


class TestEveryCopyIsVerified:
    def test_each_applied_action_records_the_hash_it_verified(self, merged) -> None:
        _source, destination, _plan, result = merged
        log = destination / "context" / RUN_ID / "actions.jsonl"
        assert log.is_file(), "no action log was written"
        applied = [
            json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()
            if line.strip() and json.loads(line).get("status") == "applied"
        ]
        assert applied, "nothing was logged as applied"
        for entry in applied:
            assert entry.get("verified_sha256"), f"{entry['operation']} logged no hash"
        assert result["verified"] >= len(applied)

    def test_the_verified_hash_matches_the_file_on_disk(self, merged) -> None:
        _source, destination, _plan, _result = merged
        arrived = destination / "solo_origen.txt"
        log = destination / "context" / RUN_ID / "actions.jsonl"
        entries = [
            json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        match = [e for e in entries if str(e.get("destination", "")).endswith("solo_origen.txt")]
        assert match, "the copied file has no log entry"
        assert match[0]["verified_sha256"] == sha256(arrived, {})

    def test_a_missing_source_is_recorded_as_failed_not_raised(
        self, roots, tmp_path: Path
    ) -> None:
        source, destination = roots
        plan = build_plan([source], destination)
        for action in plan["actions"]:
            if action["operation"] == "copy_unique":
                action["source"] = str(tmp_path / "no_existe.txt")
                break
        result = apply_plan(plan)
        assert result["failed"] >= 1, "a vanished source was not reported"


class TestRetirementIsGatedOnSuccess:
    def test_a_failed_copy_blocks_retirement(self, roots, tmp_path: Path) -> None:
        # Moving the sources away after a partial copy is how an archive gets
        # lost. The gate is `result["failed"] == 0`.
        source, destination = roots
        plan = build_plan([source], destination)
        for action in plan["actions"]:
            if action["operation"] == "copy_unique":
                action["source"] = str(tmp_path / "no_existe.txt")
                break

        result = apply_plan(plan, retire_sources=True)

        assert result["failed"] >= 1
        assert result["retired"] == 0, "sources were retired after a failed copy"
        assert source.is_dir(), "the source root was moved despite a failure"

    def test_a_clean_run_retires_and_leaves_a_redirect(self, roots) -> None:
        source, destination = roots
        result = apply_plan(build_plan([source], destination), retire_sources=True)

        assert result["failed"] == 0
        assert result["retired"] == 1
        assert source.is_symlink(), "the retired source left no redirect behind"
        assert source.resolve().is_dir(), "the redirect points nowhere"
        assert (source / "solo_origen.txt").is_file(), (
            "the redirect does not resolve to the relocated content"
        )


class TestArchiveLocation:
    def test_a_test_destination_never_reaches_the_real_home_archive(
        self, tmp_path: Path
    ) -> None:
        # The guard that makes this whole module safe to run.
        assert archive_run(tmp_path).is_relative_to(tmp_path)

    def test_the_real_home_still_maps_to_the_durable_archive(self) -> None:
        assert not archive_run(DEFAULT_DEST).is_relative_to(DEFAULT_DEST / "context")
