from pathlib import Path

from tools.recovered.import_claude_sessions import public_bytes, sanitize_text


def test_sanitize_text_removes_windows_user_root():
    text = r"C:\Users\private\AppData\Local\session.txt"

    sanitized = sanitize_text(text)

    assert "C:\\Users\\private" not in sanitized
    assert "<local-user-home>" in sanitized


def test_public_bytes_preserves_source_hash_boundary_for_text(tmp_path: Path):
    source = tmp_path / "session.md"
    source.write_text(r"C:\Users\private\session", encoding="utf-8")

    content, changed = public_bytes(source)

    assert changed is True
    assert b"C:\\Users\\private" not in content
    assert b"<local-user-home>" in content
