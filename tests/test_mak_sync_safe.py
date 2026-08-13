"""Fixture-only contract tests for the MAK transport guard."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load():
    path = ROOT / "tools" / "mak_ops" / "sync_mak_safe.py"
    spec = importlib.util.spec_from_file_location("mak_sync_safe_fixture", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _git(repo: Path, *args: str) -> None:
    result = subprocess.run(["git", "-C", str(repo), *args], text=True,
                            capture_output=True, check=False)
    assert result.returncode == 0, result.stderr


def _fixture(tmp_path: Path):
    module = _load()
    deploy = tmp_path / "deploy"
    source_root = deploy / "src"
    target_root = tmp_path / "runtime"
    user = tmp_path / "human"
    source_root.mkdir(parents=True)
    target_root.mkdir()
    user.mkdir()
    _git(deploy, "init", "-q")
    _git(deploy, "config", "user.email", "test@example.invalid")
    _git(deploy, "config", "user.name", "fixture")
    source_file = source_root / "worker.py"
    target_file = target_root / "worker.py"
    target_file.write_text("old\n", encoding="utf-8")
    source_file.write_text("new\n", encoding="utf-8")
    _git(deploy, "add", "src/worker.py")
    _git(deploy, "commit", "-qm", "fixture")
    old_hash = module.sha256(target_file)
    source_stat = source_file.stat()
    os.utime(target_file, ns=(source_stat.st_atime_ns, source_stat.st_mtime_ns - 10))
    settings = module.Settings(
        deploy_repo=deploy,
        user_repo=user,
        lock_path=tmp_path / "lock",
        manifest_path=tmp_path / "manifest.json",
        backup_root=tmp_path / "backups",
        recovery_root=tmp_path / "recovery",
        staging_root=tmp_path / "staging",
    )
    module.SOURCES = {"test_component": ("src", str(target_root))}
    return module, settings, source_file, target_file, old_hash


def _seed_completed(settings, module, old_hash):
    settings.manifest_path.write_text(json.dumps({
        "schema": module.SCHEMA,
        "status": "completed",
        "managed_files": [{
            "component": "test_component",
            "path": "worker.py",
            "source_hash": old_hash,
            "deployed_source_hash": old_hash,
        }],
    }), encoding="utf-8")


def test_source_newer_is_plannable_and_dry_run_is_idempotent(tmp_path):
    module, settings, _, _, old_hash = _fixture(tmp_path)
    _seed_completed(settings, module, old_hash)
    first = module.build_plan(settings)
    assert first["promotion_result"]["status"] == "ready"
    assert {item["state"] for item in first["managed_files"]} == {"source_newer"}
    module.write_plan(settings, first)
    first_bytes = settings.manifest_path.read_bytes()
    second = module.build_plan(settings)
    module.write_plan(settings, second)
    assert settings.manifest_path.read_bytes() == first_bytes


def test_target_newer_dirty_and_untracked_are_blocked(tmp_path):
    module, settings, source, target, old_hash = _fixture(tmp_path)
    _seed_completed(settings, module, old_hash)
    os.utime(target, ns=(source.stat().st_atime_ns, source.stat().st_mtime_ns + 1_000_000_000))
    plan = module.build_plan(settings)
    assert "test_component:worker.py:target_newer" in plan["promotion_result"]["reasons"]

    target.write_text("dirty\n", encoding="utf-8")
    os.utime(target, ns=(source.stat().st_atime_ns, source.stat().st_mtime_ns - 1_000_000_000))
    plan = module.build_plan(settings)
    assert "test_component:worker.py:dirty_target" in plan["promotion_result"]["reasons"]

    (target.parent / "untracked.txt").write_text("local\n", encoding="utf-8")
    plan = module.build_plan(settings)
    assert any("untracked:untracked.txt" in reason
               for reason in plan["promotion_result"]["reasons"])


def test_private_and_runtime_material_is_excluded_from_transport(tmp_path):
    module, settings, _, target, old_hash = _fixture(tmp_path)
    (settings.deploy_repo / "src" / ".env").write_text("TOKEN=private\n", encoding="utf-8")
    (settings.deploy_repo / "src" / "cache.db").write_text("runtime\n", encoding="utf-8")
    (settings.deploy_repo / "src" / "generated").mkdir()
    (settings.deploy_repo / "src" / "generated" / "out.txt").write_text("derived\n", encoding="utf-8")
    _seed_completed(settings, module, old_hash)
    plan = module.build_plan(settings)
    paths = {item["path"] for item in plan["managed_files"]}
    assert paths == {"worker.py"}
    component = plan["components"]["test_component"]
    assert ".env" in component["source_excluded"]
    assert "cache.db" in component["source_excluded"]
    assert "generated/" in component["source_excluded"]

    (target.parent / ".env").write_text("LOCAL=secret\n", encoding="utf-8")
    plan = module.build_plan(settings)
    assert ".env" in plan["components"]["test_component"]["target_excluded"]


def test_interrupted_apply_leaves_resumable_journal_and_can_resume(tmp_path, monkeypatch):
    module, settings, _, target, old_hash = _fixture(tmp_path)
    _seed_completed(settings, module, old_hash)
    plan = module.build_plan(settings)
    module.write_plan(settings, plan)
    real_replace = module.os.replace

    def fail_target(source, destination):
        if Path(destination) == target:
            raise OSError("fixture interruption")
        return real_replace(source, destination)

    monkeypatch.setattr(module.os, "replace", fail_target)
    assert module.apply_manifest(settings, settings.manifest_path) == 20
    interrupted = json.loads(settings.manifest_path.read_text(encoding="utf-8"))
    journal = settings.recovery_root / plan["operation_id"] / "journal.json"
    assert interrupted["status"] == "interrupted"
    assert json.loads(journal.read_text(encoding="utf-8"))["phase"] == "interrupted"
    assert (settings.staging_root / plan["operation_id"] / "test_component" / "worker.py").exists()

    monkeypatch.setattr(module.os, "replace", real_replace)
    assert module.apply_manifest(settings, settings.manifest_path) == 0
    assert target.read_text(encoding="utf-8") == "new\n"


def test_manifest_path_traversal_and_operation_tampering_are_blocked(tmp_path):
    module, settings, _, _, old_hash = _fixture(tmp_path)
    _seed_completed(settings, module, old_hash)
    plan = module.build_plan(settings)
    module.write_plan(settings, plan)
    tampered = json.loads(settings.manifest_path.read_text(encoding="utf-8"))
    tampered["managed_files"][0]["path"] = "../outside.py"
    settings.manifest_path.write_text(json.dumps(tampered), encoding="utf-8")
    assert module.apply_manifest(settings, settings.manifest_path) == 20


def test_manifest_target_root_tampering_and_same_path_are_blocked(tmp_path):
    module, settings, _, target, old_hash = _fixture(tmp_path)
    _seed_completed(settings, module, old_hash)
    plan = module.build_plan(settings)
    module.write_plan(settings, plan)
    tampered = json.loads(settings.manifest_path.read_text(encoding="utf-8"))
    tampered["target_roots"]["test_component"] = str(tmp_path / "outside")
    settings.manifest_path.write_text(json.dumps(tampered), encoding="utf-8")
    assert module.apply_manifest(settings, settings.manifest_path) == 20
    assert target.read_text(encoding="utf-8") == "old\n"

    module.SOURCES = {
        "test_component": ("src", str(settings.deploy_repo / "src")),
    }
    errors = module.settings_path_errors(settings)
    assert any("overlaps a protected checkout" in error for error in errors)


def test_manifest_hash_tampering_is_blocked_even_with_recomputed_operation_id(tmp_path):
    module, settings, _, target, old_hash = _fixture(tmp_path)
    _seed_completed(settings, module, old_hash)
    plan = module.build_plan(settings)
    plan["managed_files"][0]["source_hash"] = "0" * 64
    plan["operation_id"] = module.operation_id(
        plan["source_checkpoint"]["commit"],
        plan["source_checkpoint"]["tree"],
        plan["target_roots"].values(),
        plan["managed_files"],
    )
    plan["backup_path"] = str(settings.backup_root / plan["operation_id"])
    plan["recovery_path"] = str(settings.recovery_root / plan["operation_id"])
    module.write_plan(settings, plan)
    assert module.apply_manifest(settings, settings.manifest_path) == 20
    assert target.read_text(encoding="utf-8") == "old\n"


def test_state_same_cannot_skip_a_real_source_change(tmp_path):
    module, settings, _, target, old_hash = _fixture(tmp_path)
    _seed_completed(settings, module, old_hash)
    plan = module.build_plan(settings)
    plan["managed_files"][0]["state"] = "same"
    plan["operation_id"] = module.operation_id(
        plan["source_checkpoint"]["commit"],
        plan["source_checkpoint"]["tree"],
        plan["target_roots"].values(),
        plan["managed_files"],
    )
    module.write_plan(settings, plan)
    assert module.apply_manifest(settings, settings.manifest_path) == 20
    assert target.read_text(encoding="utf-8") == "old\n"


def test_corrupt_or_external_journal_is_blocked_without_target_write(tmp_path):
    module, settings, _, target, old_hash = _fixture(tmp_path)
    _seed_completed(settings, module, old_hash)
    plan = module.build_plan(settings)
    module.write_plan(settings, plan)
    recovery = settings.recovery_root / plan["operation_id"]
    recovery.mkdir(parents=True)
    journal = recovery / "journal.json"
    journal.write_text("{not-json", encoding="utf-8")
    assert module.apply_manifest(settings, settings.manifest_path) == 20
    assert target.read_text(encoding="utf-8") == "old\n"

    journal.write_text(json.dumps({
        "schema": module.JOURNAL_SCHEMA,
        "operation_id": plan["operation_id"],
        "phase": "staging",
        "status": "applying",
        "completed_files": [],
        "staging_path": str(tmp_path / "outside-staging"),
    }), encoding="utf-8")
    assert module.apply_manifest(settings, settings.manifest_path) == 20
    assert not (tmp_path / "outside-staging").exists()


def test_missing_target_after_plan_is_not_treated_as_safe_replace(tmp_path):
    module, settings, _, target, old_hash = _fixture(tmp_path)
    _seed_completed(settings, module, old_hash)
    plan = module.build_plan(settings)
    module.write_plan(settings, plan)
    target.unlink()
    assert module.apply_manifest(settings, settings.manifest_path) == 20
    assert not target.exists()


def test_source_toctou_after_staging_is_blocked(tmp_path, monkeypatch):
    module, settings, source, target, old_hash = _fixture(tmp_path)
    _seed_completed(settings, module, old_hash)
    plan = module.build_plan(settings)
    module.write_plan(settings, plan)
    real_copy = module.copy_to_stage

    def copy_then_mutate(*args, **kwargs):
        real_copy(*args, **kwargs)
        source.write_text("changed after staging\n", encoding="utf-8")

    monkeypatch.setattr(module, "copy_to_stage", copy_then_mutate)
    assert module.apply_manifest(settings, settings.manifest_path) == 20
    assert target.read_text(encoding="utf-8") == "old\n"


def test_target_toctou_after_backup_is_blocked(tmp_path, monkeypatch):
    module, settings, _, target, old_hash = _fixture(tmp_path)
    _seed_completed(settings, module, old_hash)
    plan = module.build_plan(settings)
    module.write_plan(settings, plan)
    real_backup = module.backup_targets

    def backup_then_mutate(*args, **kwargs):
        real_backup(*args, **kwargs)
        target.write_text("changed during promotion\n", encoding="utf-8")

    monkeypatch.setattr(module, "backup_targets", backup_then_mutate)
    assert module.apply_manifest(settings, settings.manifest_path) == 20
    assert target.read_text(encoding="utf-8") == "changed during promotion\n"


def test_case_insensitive_private_runtime_material_never_enters_plan(tmp_path):
    module, settings, _, _, old_hash = _fixture(tmp_path)
    source_root = settings.deploy_repo / "src"
    (source_root / ".ENV").write_text("TOKEN=private\n", encoding="utf-8")
    (source_root / "Cache.DB").write_text("runtime\n", encoding="utf-8")
    (source_root / "MOUNTS").mkdir()
    (source_root / "MOUNTS" / "secret.txt").write_text("private\n", encoding="utf-8")
    _seed_completed(settings, module, old_hash)
    plan = module.build_plan(settings)
    assert {item["path"] for item in plan["managed_files"]} == {"worker.py"}
    excluded = plan["components"]["test_component"]["source_excluded"]
    assert ".ENV" in excluded
    assert "Cache.DB" in excluded
    assert "MOUNTS/" in excluded


def test_build_plan_and_inventory_do_not_write_dry_run_artifacts(tmp_path):
    module, settings, _, _, old_hash = _fixture(tmp_path)
    _seed_completed(settings, module, old_hash)
    before = {path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*")}
    module.inventory(settings)
    module.build_plan(settings)
    after = {path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*")}
    assert after == before


def test_git_status_failure_is_blocked_not_interpreted_as_clean(tmp_path, monkeypatch):
    module, settings, _, target, old_hash = _fixture(tmp_path)
    _seed_completed(settings, module, old_hash)
    plan = module.build_plan(settings)
    module.write_plan(settings, plan)
    real_git = module.git

    def failing_status(repo, *args):
        if args and args[0] == "status":
            return subprocess.CompletedProcess(args, 124, "", "timeout")
        return real_git(repo, *args)

    monkeypatch.setattr(module, "git", failing_status)
    assert module.apply_manifest(settings, settings.manifest_path) == 20
    assert target.read_text(encoding="utf-8") == "old\n"


def test_lock_is_exclusive_on_available_platform_backend(tmp_path):
    module = _load()
    if module.fcntl is None and module.msvcrt is None:
        pytest.skip("no platform lock backend")
    first = module.acquire_lock(tmp_path / "sync.lock")
    try:
        with pytest.raises(RuntimeError, match="already running"):
            module.acquire_lock(tmp_path / "sync.lock")
    finally:
        first.close()


def test_target_newer_with_same_hash_is_same_and_target_newer_different_hash_blocks(tmp_path):
    module, settings, source, target, old_hash = _fixture(tmp_path)
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    os.utime(target, ns=(source.stat().st_atime_ns, source.stat().st_mtime_ns + 1_000_000_000))
    _seed_completed(settings, module, old_hash)
    plan = module.build_plan(settings)
    assert plan["promotion_result"]["status"] == "ready"
    assert plan["managed_files"][0]["state"] == "same"

    target.write_text("different\n", encoding="utf-8")
    os.utime(target, ns=(source.stat().st_atime_ns, source.stat().st_mtime_ns + 2_000_000_000))
    plan = module.build_plan(settings)
    assert plan["promotion_result"]["status"] == "blocked"
    assert "target_newer" in plan["promotion_result"]["reasons"][0]


def test_resume_tracks_component_and_path_not_path_alone(tmp_path, monkeypatch):
    module, settings, _, target_a, old_hash = _fixture(tmp_path)
    deploy = settings.deploy_repo
    target_b = tmp_path / "runtime-b"
    target_b.mkdir()
    source_b = deploy / "src-b"
    source_b.mkdir()
    source_b_file = source_b / "worker.py"
    source_b_file.write_text("second\n", encoding="utf-8")
    target_b_file = target_b / "worker.py"
    target_b_file.write_text("old-second\n", encoding="utf-8")
    source_b_stat = source_b_file.stat()
    os.utime(target_b_file, ns=(source_b_stat.st_atime_ns, source_b_stat.st_mtime_ns - 10))
    _git(deploy, "add", "src-b/worker.py")
    _git(deploy, "commit", "-qm", "second component")
    module.SOURCES = {
        "test_component": ("src", str(target_a.parent)),
        "second": ("src-b", str(target_b)),
    }
    # Keep the first component's target at runtime-a while retaining the
    # fixture's source/target relationship.
    settings.manifest_path.write_text(json.dumps({
        "status": "completed",
        "managed_files": [
            {
                "component": "test_component",
                "path": "worker.py",
                "source_hash": old_hash,
                "deployed_source_hash": old_hash,
            },
            {
                "component": "second",
                "path": "worker.py",
                "source_hash": module.sha256(target_b_file),
                "deployed_source_hash": module.sha256(target_b_file),
            },
        ],
    }), encoding="utf-8")
    plan = module.build_plan(settings)
    module.write_plan(settings, plan)
    real_replace = module.os.replace

    def fail_second(source, destination):
        if Path(destination) == target_b_file:
            raise OSError("second component interruption")
        return real_replace(source, destination)

    monkeypatch.setattr(module.os, "replace", fail_second)
    assert module.apply_manifest(settings, settings.manifest_path) == 20
    journal = json.loads(
        (settings.recovery_root / plan["operation_id"] / "journal.json").read_text(
            encoding="utf-8"
        )
    )
    assert "test_component:worker.py" in journal["completed_files"]
    assert "second:worker.py" not in journal["completed_files"]
    assert target_a.read_text(encoding="utf-8") == "new\n"
    assert target_b_file.read_text(encoding="utf-8") == "old-second\n"

    monkeypatch.setattr(module.os, "replace", real_replace)
    assert module.apply_manifest(settings, settings.manifest_path) == 0
    assert target_a.read_text(encoding="utf-8") == "new\n"
    assert target_b_file.read_text(encoding="utf-8") == "second\n"


def test_symlink_source_and_target_are_excluded_or_blocked(tmp_path):
    module, settings, _, target, old_hash = _fixture(tmp_path)
    outside = tmp_path / "outside-secret.py"
    outside.write_text("secret\n", encoding="utf-8")
    source_link = settings.deploy_repo / "src" / "secret.py"
    try:
        source_link.symlink_to(outside)
        target.unlink()
        target.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation is unavailable on this Windows fixture")
    _seed_completed(settings, module, old_hash)
    plan = module.build_plan(settings)
    assert "secret.py [link]" in plan["components"]["test_component"]["source_excluded"]
    assert module.apply_manifest(settings, settings.manifest_path) == 20
    assert outside.read_text(encoding="utf-8") == "secret\n"
