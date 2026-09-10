from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKUP = ROOT / "cultura" / "mak_plataforma" / "backup.sh"


def test_azure_backup_is_explicit_and_uses_login_authentication():
    text = BACKUP.read_text(encoding="utf-8")

    assert 'MAK_AZURE_BACKUP_UPLOAD:-0' in text
    assert "--auth-mode login" in text
    assert "--public-access off" in text
    assert "--overwrite true" in text
    assert "AZURE_STORAGE_CONNECTION_STRING" not in text
    assert "AZURE_STORAGE_KEY" not in text
