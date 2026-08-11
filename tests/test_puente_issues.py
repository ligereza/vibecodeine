from cultura.mak_plataforma import puente_issues


def test_path_sanitization_handles_windows_and_linux_without_breaking_urls():
    text = (
        r"fallo C:\Users\mak\RD\AUTOMATIZACION\render.png "
        "/home/mak/RD/AUTOMATIZACION/render.png "
        "https://example.org/open-call"
    )

    result = puente_issues._sin_rutas(text)

    assert "C:\\Users\\mak" not in result
    assert "/home/mak/RD" not in result
    assert ".../render.png" in result
    assert "https://example.org/open-call" in result


def test_replace_failure_preserves_previous_state_and_cleans_temp(
        monkeypatch, tmp_path):
    path = tmp_path / "estado.json"
    path.write_text('{"old": true}', encoding="utf-8")
    monkeypatch.setattr(puente_issues, "ESTADO", path)
    original_replace = puente_issues.os.replace

    def fail_install(source, destination):
        if destination == str(path):
            raise OSError("simulated replace failure")
        return original_replace(source, destination)

    monkeypatch.setattr(puente_issues.os, "replace", fail_install)
    puente_issues._guardar_estado({"new": True})

    assert path.read_text(encoding="utf-8") == '{"old": true}'
    assert not list(tmp_path.glob(".*.tmp"))
