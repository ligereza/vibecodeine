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
