import json

from cultura.mak_plataforma import xio_evidence


def test_xio_show_kit_keeps_evidence_atoms_separate_and_validates_work(tmp_path):
    (tmp_path / "setlist_festival_sentir.txt").write_text(
        "00:00:00:00 intro show\n01:00:00:00 Último Día\n", encoding="utf-8")
    (tmp_path / "setlist_durations_dref.json").write_text(
        json.dumps({"durations": [71.2, None]}), encoding="utf-8")
    (tmp_path / "cue_map_dref.json").write_text(
        json.dumps({"fps": 30, "cues": [
            {"n": "1", "tema": "intro show", "timecode": "00:00:00:00", "layer": 1, "clip": 1},
            {"n": "2", "tema": "Último Día", "timecode": "01:00:00:00", "layer": None, "clip": None},
        ]}), encoding="utf-8")
    (tmp_path / "DIA_DEL_SHOW.md").write_text(
        "Kit de DREF CHOCOLATE. El artista y venue no están declarados aquí.",
        encoding="utf-8")
    (tmp_path / "ANOTACIONES_SHOW_20260724.md").write_text(
        "Show 2026-07-24. TC observado 07:33:56:29.", encoding="utf-8")

    result = xio_evidence.load_show_evidence(tmp_path)

    assert result["available"] is True
    assert result["work"]["schema"] == "mak-work-v1"
    assert result["work_valid"] is True
    assert result["linked_to_source_id"] is False
    fields = {row["field"]: row for row in result["evidence"]}
    assert fields["event"]["value"] == "DREF CHOCOLATE"
    assert fields["date"]["value"] == "2026-07-24"
    assert fields["timecode"]["status"] == "observed"
    assert fields["artist"]["status"] == "unknown"
    assert result["segments"][1]["duration_s"] is None


def test_xio_missing_show_kit_is_safe_fallback(tmp_path):
    result = xio_evidence.load_show_evidence(tmp_path)
    assert result["available"] is False
    assert result["segments"] == []
