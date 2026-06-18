import shutil
import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional, Dict
from .paths import repo_root
def get_airdrop_dir() -> Path: return repo_root() / "_airdrop"
def get_backup_base_dir() -> Path: return repo_root() / "_airdrop_backups"
def list_versions() -> List[str]:
    airdrop_dir = get_airdrop_dir()
    if not airdrop_dir.exists(): return []
    return sorted([d.name for d in airdrop_dir.iterdir() if d.is_dir()], reverse=True)
def scan_airdrop(version: str) -> List[Dict]:
    airdrop_dir = get_airdrop_dir() / version
    if not airdrop_dir.exists(): raise FileNotFoundError(f"Airdrop version {version} not found")
    changes = []
    for src in airdrop_dir.rglob("*"):
        if src.is_dir() or src.name == ".gitkeep": continue
        rel_path = src.relative_to(airdrop_dir)
        dest = repo_root() / rel_path
        status = "REPLACE" if dest.exists() else "NEW"
        changes.append({"src": src, "dest": dest, "rel": str(rel_path), "status": status})
    return sorted(changes, key=lambda x: x["rel"])
def apply_airdrop(version: str, dry_run: bool = False) -> List[Dict]:
    changes = scan_airdrop(version)
    if not changes: return []
    if dry_run: return changes
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_dir = get_backup_base_dir() / f"{timestamp}_{version}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    applied = []
    for change in changes:
        src, dest, rel = change["src"], change["dest"], change["rel"]
        if change["status"] == "REPLACE":
            backup_path = backup_dir / rel
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dest, backup_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        if dest.suffix == ".sh": dest.chmod(dest.stat().st_mode | 0o111)
        applied.append(change)
    return applied
def run_auto_checkpoint(version: str) -> bool:
    script_path = repo_root() / "scripts" / "checkpoint.sh"
    if not script_path.exists(): return False
    message = f"airdrop v{version} aplicado automáticamente"
    try:
        subprocess.run(["bash", str(script_path), message], cwd=repo_root(), check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError: return False
def rollback_last() -> Optional[Path]:
    backup_base = get_backup_base_dir()
    if not backup_base.exists(): return None
    backups = sorted([d for d in backup_base.iterdir() if d.is_dir()], reverse=True)
    if not backups: return None
    last_backup = backups[0]
    for src in last_backup.rglob("*"):
        if src.is_dir(): continue
        rel_path = src.relative_to(last_backup)
        dest = repo_root() / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        if dest.suffix == ".sh": dest.chmod(dest.stat().st_mode | 0o111)
    return last_backup
