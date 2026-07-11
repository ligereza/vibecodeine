"""Tests for tools/compete_engine.py (Tapiz/Psicosis/Fungi diagnostics pipeline)."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import compete_engine as ce


def make_asset(content, tags=None, artistic=True, state=ce.EntityState.ACTIVE):
    return ce.ArtAsset(
        asset_id="TEST-001",
        name="TestAsset",
        content=content,
        metadata=ce.MetadataLayer("test intent", tags or [], artistic),
        state=state,
        last_modified=time.time(),
    )


class TestChunkedEncoder:
    def test_round_trip_ascii(self):
        enc = ce.ChunkedEncoder()
        asset = make_asset("plain ascii payload 123")
        chunks = enc.encode_asset(asset)
        assert chunks
        assert enc.decode_chunks(chunks) == asset.content

    def test_round_trip_non_ascii_multichunk(self):
        enc = ce.ChunkedEncoder()
        content = ("█" * 50 + "▓" * 50 + "\n╔═╗ psicosis\n") * 5
        asset = make_asset(content)
        chunks = enc.encode_asset(asset, chunk_size=32)
        assert len(chunks) > 1
        assert all(len(c) <= 32 for c in chunks)
        assert enc.decode_chunks(chunks) == content

    def test_empty_content(self):
        enc = ce.ChunkedEncoder()
        assert enc.encode_asset(make_asset("")) == []
        assert enc.decode_chunks([]) == ""


class TestTokenVolumetricAnalyzer:
    def test_light_density_no_penalty(self):
        analyzer = ce.TokenVolumetricAnalyzer()
        content = "plain readable prose " * 20
        result = analyzer.analyze_asset(make_asset(content))
        assert result["symbol_density"] <= ce.ASCII_DENSITY_THRESHOLD
        assert result["estimated_tokens"] == int(len(content) / ce.BASE_CHARS_PER_TOKEN)

    def test_heavy_density_penalized(self):
        analyzer = ce.TokenVolumetricAnalyzer()
        content = "#@$%" * 100  # pure symbols, density 1.0
        result = analyzer.analyze_asset(make_asset(content))
        assert result["symbol_density"] > ce.ASCII_DENSITY_THRESHOLD
        base = len(content) / ce.BASE_CHARS_PER_TOKEN
        assert result["estimated_tokens"] == int(base * ce.ASCII_PENALTY_MULTIPLIER)

    def test_heavy_costs_more_than_light_of_same_length(self):
        analyzer = ce.TokenVolumetricAnalyzer()
        heavy = analyzer.analyze_asset(make_asset("=" * 400))
        light = analyzer.analyze_asset(make_asset("word" * 100))
        assert heavy["estimated_tokens"] > light["estimated_tokens"]


class TestEcosystemStateTransition:
    def test_transition_to_fungi_moves_and_strips_render_tag(self):
        state = ce.EcosystemState()
        asset = make_asset("mass", tags=["active_render", "tapiz"],
                           state=ce.EntityState.ACTIVE)
        state.active_assets[asset.asset_id] = asset

        assert state.transition_to_fungi(asset.asset_id) is True
        assert asset.asset_id not in state.active_assets
        moved = state.decaying_assets[asset.asset_id]
        assert moved.state == ce.EntityState.DECAYING
        assert "active_render" not in moved.metadata.tags
        assert "tapiz" in moved.metadata.tags
        assert any(e["event"] == "decay_initiated" and e["asset"] == asset.asset_id
                   for e in state.event_log)

    def test_transition_to_fungi_missing_asset_returns_false(self):
        state = ce.EcosystemState()
        assert state.transition_to_fungi("NOPE") is False
        assert state.event_log == []

    def test_transitioned_asset_never_races_the_renderer(self):
        # The state-lock (tag strip) means a proper transition cannot be
        # flagged as a Decay-Render race by the concurrency analyzer.
        state = ce.EcosystemState()
        asset = make_asset("mass", tags=["active_render"],
                           state=ce.EntityState.ACTIVE)
        state.active_assets[asset.asset_id] = asset
        state.transition_to_fungi(asset.asset_id)
        result = ce.ConcurrencyLogicAnalyzer().analyze_ecosystem(state)
        assert result["race_conditions"] == []


class TestGuardrailSimulationAnalyzer:
    def test_artistic_mitigation_lowers_score(self):
        analyzer = ce.GuardrailSimulationAnalyzer()
        content = "psicosis decay fungi rot"
        artistic = analyzer.analyze_asset(make_asset(content, artistic=True))
        raw = analyzer.analyze_asset(make_asset(content, artistic=False))
        assert artistic["triggered_categories"]
        assert artistic["artistic_context_mitigation"] == "70%"
        assert raw["artistic_context_mitigation"] == "0%"
        assert artistic["final_risk_score"] < raw["final_risk_score"]

    def test_clean_content_is_safe(self):
        analyzer = ce.GuardrailSimulationAnalyzer()
        result = analyzer.analyze_asset(make_asset("geometric mesh of light"))
        assert result["triggered_categories"] == []
        assert result["risk_level"] == ce.RiskLevel.SAFE.value

    def test_extended_lexicon_keywords_trigger(self):
        # keywords ported from the ecosystem_engine draft
        analyzer = ce.GuardrailSimulationAnalyzer()
        result = analyzer.analyze_asset(
            make_asset("a weapon over corpse waste, they suffer"))
        assert "violence" in result["triggered_categories"]
        assert "decay_gross" in result["triggered_categories"]
        assert "self_harm" in result["triggered_categories"]


class TestConcurrencyLogicAnalyzer:
    def test_overlap_detected_as_flaw(self):
        analyzer = ce.ConcurrencyLogicAnalyzer()
        state = ce.EcosystemState()
        asset = make_asset("shared", state=ce.EntityState.DECAYING)
        state.active_assets[asset.asset_id] = asset
        state.decaying_assets[asset.asset_id] = asset
        result = analyzer.analyze_ecosystem(state)
        assert any("State violation" in f for f in result["logic_flaws"])
        assert result["system_health"] == "DEGRADED"

    def test_disjoint_sets_stable(self):
        analyzer = ce.ConcurrencyLogicAnalyzer()
        state = ce.EcosystemState()
        active = make_asset("a", state=ce.EntityState.ACTIVE)
        state.active_assets[active.asset_id] = active
        result = analyzer.analyze_ecosystem(state)
        assert result["logic_flaws"] == []
        assert result["race_conditions"] == []
        assert result["system_health"] == "STABLE"

    def test_decay_render_conflict(self):
        analyzer = ce.ConcurrencyLogicAnalyzer()
        state = ce.EcosystemState()
        asset = make_asset("x", tags=["active_render"], state=ce.EntityState.DECAYING)
        asset.last_modified = time.time()  # inside grace period
        state.decaying_assets["RACE-1"] = asset
        result = analyzer.analyze_ecosystem(state)
        assert result["race_conditions"]
        assert result["race_conditions"][0]["flaw"] == "Decay-Render conflict"


class TestPipelineOutput:
    def test_demo_pipeline_writes_to_given_out_dir(self, tmp_path, capsys):
        out = tmp_path / "dist"
        path = ce.execute_pipeline(output_dir=out)
        assert Path(path).exists()
        assert Path(path).parent == out.resolve()

    def test_stress_pipeline_triggers_every_degraded_state(self, tmp_path, capsys):
        import json
        path = ce.execute_pipeline(output_dir=tmp_path / "dist", stress=True)
        matrix = json.loads(Path(path).read_text(encoding="utf-8"))

        mesh = matrix["luminous_mesh_densities"]
        assert mesh["status"] == "OVERLOADED"
        assert mesh["global_pressure"] > 0.8

        mask = matrix["chromatic_frequency_masks"]
        assert mask["mask_intensity"] == "CRITICAL"
        assert "hue-rotate" in mask["css_filter_string"]

        chrono = matrix["chronological_collision_buffers"]
        assert chrono["status"] == "TEMPORAL_DEGRADED"
        assert chrono["collision_count"] >= 5  # violation + accumulation + races
        # public keyframe name stays stable for TAPIZ.md / tapiz_renderer.html
        assert "@keyframes temporal_tear {" in chrono["css_keyframes_payload"]
        # richer glitch grammar ported from the ecosystem_engine draft
        assert "hue-rotate" in chrono["css_keyframes_payload"]
        assert "opacity" in chrono["css_keyframes_payload"]
        assert "cubic-bezier" in chrono["animation_class"]

        payloads = matrix["encoded_asset_payloads"]
        assert payloads["total_payloads"] > 10  # colony accumulation visible as spores


class TestLiveTelemetry:
    """LIVE mode: the repo paints a self-portrait from real state."""

    def test_build_outside_git_repo_does_not_crash(self, tmp_path):
        import tapiz_telemetry as tt
        state = tt.build_live_ecosystem(tmp_path)
        assert isinstance(state, ce.EcosystemState)
        # graceful degradation: at worst the fallback void asset exists
        assert state.active_assets or state.decaying_assets

    def test_build_on_real_repo_has_assets_and_vitals(self):
        import tapiz_telemetry as tt
        state = tt.build_live_ecosystem()
        assert state.active_assets
        assert any(e.get("event") == "repo_vitals" for e in state.event_log)

    def test_exclude_patterns_match_canaries(self):
        import tapiz_telemetry as tt
        blocked = [
            ".env", ".env.local", "gemini_api_key.txt", "secrets.json",
            "hf_token.txt", "notas.local.md", "credentials.yaml",
            "tilde_log.jsonl", "passwords.txt", "azure_export.csv",
            "id_rsa.pem", "id_rsa", "id_ed25519.pub", "cert.p12",
            "putty.ppk", "data.db", "cache.sqlite3", ".npmrc", ".netrc",
            "cookies.txt", "mi_clave_gemini.txt", "contrasena.txt",
            "credencial_banco.txt", "config.json",
        ]
        for name in blocked:
            assert tt._is_excluded(name), "should be excluded: %s" % name
        allowed = ["compete_engine.py", "FLYERS8.ai", "idea.md", "flujo_hub.html"]
        for name in allowed:
            assert not tt._is_excluded(name), "should be allowed: %s" % name

    def test_path_excluded_checks_every_component_and_git_quoting(self):
        import tapiz_telemetry as tt
        # directory components must not smuggle excluded names through
        assert tt._path_excluded("secrets/config.json")
        assert tt._path_excluded("desktop\\config.json")
        assert tt._path_excluded("a/b/.env")
        assert tt._path_excluded('"clave-priv.pem"')  # git C-quoted form
        assert not tt._path_excluded("tools/tapiz_telemetry.py")
        assert not tt._path_excluded('"cafe con acento.md"')

    def test_generated_content_never_leaks_excluded_names(self, tmp_path):
        import tapiz_telemetry as tt
        # canary repo: excluded files planted exactly where scanners look
        (tmp_path / "datadrops").mkdir()
        (tmp_path / "datadrops" / ".env").write_text("SECRET=1")
        (tmp_path / "datadrops" / "api_key.txt").write_text("k")
        (tmp_path / "datadrops" / "drop_notes.txt").write_text("ok")
        archive = tmp_path / "docs" / "handoffs" / "archive"
        archive.mkdir(parents=True)
        (archive / "credentials_backup.md").write_text("x")
        (archive / "handoff_01.md").write_text("x")

        state = tt.build_live_ecosystem(tmp_path)
        assets = list(state.active_assets.values()) + list(state.decaying_assets.values())
        blob = " ".join(a.asset_id + " " + a.name + " " + a.content
                        for a in assets).lower()
        for needle in (".env", "api_key", "credentials_backup", "secret="):
            assert needle not in blob, "leaked: %s" % needle
        # sanity: allowed names DO surface, so exclusion is not vacuous
        assert "drop_notes" in blob or "handoff_01" in blob

    def test_real_repo_content_has_no_private_markers(self):
        import tapiz_telemetry as tt
        state = tt.build_live_ecosystem()
        assets = list(state.active_assets.values()) + list(state.decaying_assets.values())
        blob = " ".join(a.content.lower() for a in assets)
        for needle in (".env", "secret", "api_key", "apikey", "password",
                       "credential", ".local.md", "tilde_log", ".pem"):
            assert needle not in blob, "private marker in live content: %s" % needle

    def test_pipeline_live_end_to_end_validates(self, tmp_path, capsys):
        import json
        import system_map
        path = ce.execute_pipeline(output_dir=tmp_path / "dist", mode="live")
        matrix = json.loads(Path(path).read_text(encoding="utf-8"))
        results = system_map.validate(matrix)
        assert all(not errs for errs in results.values()), results
        # mesh must react to real magnitude (compiled bundles / session logs)
        assert matrix["luminous_mesh_densities"]["global_pressure"] >= 0.0

    def test_cli_live_flag(self, tmp_path, capsys):
        assert ce.main(["--live", "--out", str(tmp_path / "dist")]) == 0
        assert (tmp_path / "dist" / "system_status.json").exists()

    def test_live_mutually_exclusive_with_demo(self, capsys):
        import pytest
        with pytest.raises(SystemExit):
            ce.main(["--live", "--demo"])

    def test_contradictory_stress_and_mode_kwargs_raise(self):
        import pytest
        with pytest.raises(ValueError):
            ce.execute_pipeline(stress=True, mode="demo")

    def test_session_stats_slug_handles_worktree_dots(self, monkeypatch, tmp_path):
        import tapiz_telemetry as tt
        # fake sessions root with the slug a worktree path must resolve to
        proj = tmp_path / "C--IA-flujo--claude-worktrees-tapiz-ecosystem"
        proj.mkdir()
        (proj / "s1.jsonl").write_text("x" * 10)
        monkeypatch.setattr(tt, "SESSIONS_ROOT", tmp_path)
        count, total, newest = tt._session_stats(
            Path(r"C:\IA\flujo\.claude\worktrees\tapiz-ecosystem"))
        assert count == 1 and total == 10 and newest > 0

    def test_cli_subprocess_live_keeps_enum_identity(self, tmp_path):
        # Regression: run as a real script (__main__), telemetry must share
        # the engine's EntityState classes or decaying payloads vanish.
        import json
        import subprocess
        engine = Path(__file__).resolve().parents[1] / "tools" / "compete_engine.py"
        out = tmp_path / "dist"
        proc = subprocess.run(
            [sys.executable, str(engine), "--live", "--out", str(out)],
            capture_output=True, text=True, timeout=60,
        )
        assert proc.returncode == 0, proc.stderr
        matrix = json.loads((out / "system_status.json").read_text(encoding="utf-8"))
        # the live repo always has decaying mass (fat zones, spores, psicosis)
        assert matrix["encoded_asset_payloads"]["total_payloads"] > 0

    def test_demo_behavior_unchanged(self, tmp_path, capsys):
        # stress=/mode= keyword back-compat: both spellings, same result shape
        p1 = ce.execute_pipeline(output_dir=tmp_path / "a", stress=False)
        p2 = ce.execute_pipeline(output_dir=tmp_path / "b", mode="demo")
        assert Path(p1).exists() and Path(p2).exists()
