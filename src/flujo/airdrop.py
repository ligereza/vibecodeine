import shutil
import os
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional, Dict

from .paths import repo_root

def get_airdrop_dir() -> Path:
    return repo_root() / "_airdrop"

def get_backup_base_dir() -> Path:
    return repo_root() / "_airdrop_backups"

def list_versions() -> List[str]:
    """Lists available airdrop versions in _airdrop/."""
    airdrop_dir = get_airdrop_dir()
    if not airdrop_dir.exists():
        return []
    return sorted([d.name for d in airdrop_dir.iterdir() if d.is_dir()], reverse=True)

def scan_airdrop(version: str) -> List[Dict]:
    """Scans an airdrop version and identifies what will be changed."""
    airdrop_dir = get_airdrop_dir() / version
    if not airdrop_dir.exists():
        raise FileNotFoundError(f"Airdrop version {version} not found in {get_airdrop_dir()}")

    changes = []
    for src in airdrop_dir.rglob("*"):
        if src.is_dir() or src.name == ".gitkeep":
            continue

        # Calculate relative path to repo root
        rel_path = src.relative_to(airdrop_dir)
        dest = repo_root() / rel_path

        status = "REPLACE" if dest.exists() else "NEW"
        changes.append({
            "src": src,
            "dest": dest,
            "rel": str(rel_path),
            "status": status
        })

    return sorted(changes, key=lambda x: x["rel"])

def apply_airdrop(version: str, dry_run: bool = False) -> List[Dict]:
    """Applies an airdrop version to the repository."""
    changes = scan_airdrop(version)
    if not changes:
        return []

    if dry_run:
        return changes

    # Create backup
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_dir = get_backup_base_dir() / f"{timestamp}_{version}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    applied = []
    for change in changes:
        src = change["src"]
        dest = change["dest"]
        rel = change["rel"]

        # Backup if exists
        if change["status"] == "REPLACE":
            backup_path = backup_dir / rel
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dest, backup_path)

        # Copy new file
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)

        # Set executable for scripts
        if dest.suffix == ".sh":
            dest.chmod(dest.stat().st_mode | 0o111)

        applied.append(change)

    return applied

def rollback_last() -> Optional[Path]:
    """Rolls back to the most recent backup."""
    backup_base = get_backup_base_dir()
    if not backup_base.exists():
        return None

    backups = sorted([d for d in backup_base.iterdir() if d.is_dir()], reverse=True)
    if not backups:
        return None

    last_backup = backups[0]
    for src in last_backup.rglob("*"):
        if src.is_dir():
            continue

        rel_path = src.relative_to(last_backup)
        dest = repo_root() / rel_path

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        if dest.suffix == ".sh":
            dest.chmod(dest.stat().st_mode | 0o111)

    return last_backup
