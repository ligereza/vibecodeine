#!/usr/bin/env python3
"""tests/test_mak_fallback.py -- Tests for MAK codex fallback utilities.

No network, ollama, or system deps. Pure logic tests.
"""
import sys
import os

# Add cultura to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "cultura", "mak_codex"))

import pytest
from fallback_util import (
    parse_provider_error,
    aggregate_failures,
    score_provider_health,
    format_chain_suggestion,
)


class TestParseProviderError:
    """Tests for parse_provider_error() error classification."""

    def test_timeout_error_detection(self):
        """Should classify timeout errors correctly."""
        result = parse_provider_error("timed out after 120s", "nim", "deepseek-v4-pro", timeout_sec=120)
        assert result["error_type"] == "timeout"
        assert result["timeout"] == 120
        assert result["provider"] == "nim"
        assert result["model"] == "deepseek-v4-pro"

    def test_connection_error_detection(self):
        """Should classify connection errors correctly."""
        result = parse_provider_error("Connection refused to 192.168.50.1", "win", "deepseek-coder:16b", timeout_sec=None)
        assert result["error_type"] == "connection"
        assert result["timeout"] is None

    def test_api_rate_limit_detection(self):
        """Should classify rate limit (429) errors correctly."""
        result = parse_provider_error("HTTP 429: rate limited", "nim", "deepseek-v4-flash")
        assert result["error_type"] == "api_error"
        assert "rate" in result["reason"].lower() or "429" in result["reason"]

    def test_empty_response_detection(self):
        """Should classify empty response errors correctly."""
        result = parse_provider_error("devolvio vacio", "ollama", "deepseek-coder:6.7b")
        assert result["error_type"] == "empty"

    def test_other_error_fallthrough(self):
        """Should classify unknown errors as 'other'."""
        result = parse_provider_error("some random error occurred", "nim", "model-xyz")
        assert result["error_type"] == "other"
        assert "random" in result["reason"].lower()

    def test_reason_truncation(self):
        """Should truncate reason to max 100 chars."""
        long_error = "x" * 150
        result = parse_provider_error(long_error, "ollama", "model")
        assert len(result["reason"]) == 100

    def test_http_5xx_error_detection(self):
        """Should classify HTTP 5xx as api_error."""
        result = parse_provider_error("HTTP 503 Service Unavailable", "nim", "model")
        assert result["error_type"] == "api_error"

    def test_http_4xx_error_detection(self):
        """Should classify HTTP 4xx as api_error."""
        result = parse_provider_error("HTTP 401 Unauthorized", "nim", "model")
        assert result["error_type"] == "api_error"


class TestAggregateFailures:
    """Tests for aggregate_failures() error message formatting."""

    def test_empty_attempts_list(self):
        """Should return empty string for no attempts."""
        result = aggregate_failures([])
        assert result == ""

    def test_single_timeout_failure(self):
        """Should format a single timeout error."""
        attempts = [
            {
                "provider": "nim",
                "model": "deepseek-v4-pro",
                "error_type": "timeout",
                "reason": "timed out",
                "timeout": 120,
            }
        ]
        result = aggregate_failures(attempts)
        assert "Todos los coders fallaron:" in result
        assert "nim/deepseek-v4-pro" in result
        assert "timeout" in result
        assert "120s" in result

    def test_multiple_failures_aggregated(self):
        """Should format multiple provider failures."""
        attempts = [
            {
                "provider": "nim",
                "model": "deepseek-v4-pro",
                "error_type": "timeout",
                "reason": "timed out",
                "timeout": 120,
            },
            {
                "provider": "nim",
                "model": "deepseek-v4-flash",
                "error_type": "api_error",
                "reason": "HTTP 429: rate limited",
                "timeout": None,
            },
            {
                "provider": "ollama",
                "model": "deepseek-coder:6.7b",
                "error_type": "connection",
                "reason": "Connection refused",
                "timeout": None,
            },
        ]
        result = aggregate_failures(attempts)
        assert result.count("\n") >= 3  # header + 3 entries
        assert "nim/deepseek-v4-pro" in result
        assert "nim/deepseek-v4-flash" in result
        assert "ollama/deepseek-coder:6.7b" in result
        assert "120s" in result
        assert "rate limited" in result or "429" in result
        assert "connection refused" in result

    def test_empty_response_formatting(self):
        """Should format empty response errors."""
        attempts = [
            {
                "provider": "win",
                "model": "deepseek-v2:16b",
                "error_type": "empty",
                "reason": "no response",
                "timeout": None,
            }
        ]
        result = aggregate_failures(attempts)
        assert "no response" in result
        assert "win/deepseek-v2:16b" in result

    def test_other_error_formatting(self):
        """Should format generic errors."""
        attempts = [
            {
                "provider": "ollama",
                "model": "model-x",
                "error_type": "other",
                "reason": "random failure",
                "timeout": None,
            }
        ]
        result = aggregate_failures(attempts)
        assert "random failure" in result


class TestScoreProviderHealth:
    """Tests for score_provider_health() provider ranking."""

    def test_single_provider_all_success(self):
        """Should give perfect score to provider with all successes."""
        stats = {"nim": {"successes": 10, "timeouts": 0, "api_errors": 0, "errors": 0}}
        scores = score_provider_health(stats)
        assert len(scores) == 1
        assert scores[0] == ("nim", 1.0)

    def test_single_provider_all_failures(self):
        """Should give zero score to provider with no successes."""
        stats = {"nim": {"successes": 0, "timeouts": 5, "api_errors": 3, "errors": 2}}
        scores = score_provider_health(stats)
        assert len(scores) == 1
        assert scores[0] == ("nim", 0.0)

    def test_multiple_providers_ranked_by_health(self):
        """Should rank providers by success ratio."""
        stats = {
            "nim": {"successes": 5, "timeouts": 2, "api_errors": 1, "errors": 0},
            "win": {"successes": 8, "timeouts": 0, "api_errors": 0, "errors": 0},
            "ollama": {"successes": 1, "timeouts": 5, "api_errors": 2, "errors": 0},
        }
        scores = score_provider_health(stats)
        # win should be first (8/8 = 1.0), nim second (5/8 = 0.625), ollama last (1/8 = 0.125)
        assert scores[0][0] == "win"
        assert scores[0][1] == 1.0
        assert scores[1][0] == "nim"
        assert abs(scores[1][1] - 0.625) < 0.01
        assert scores[2][0] == "ollama"
        assert abs(scores[2][1] - 0.125) < 0.01

    def test_provider_with_no_attempts(self):
        """Should give zero score to provider with no attempts."""
        stats = {"nim": {"successes": 0, "timeouts": 0, "api_errors": 0, "errors": 0}}
        scores = score_provider_health(stats)
        assert scores[0][1] == 0.0

    def test_partial_stats_dict(self):
        """Should handle stats dicts with missing fields gracefully."""
        stats = {"nim": {"successes": 5}}  # missing error fields
        scores = score_provider_health(stats)
        assert len(scores) == 1
        assert scores[0][0] == "nim"
        assert scores[0][1] == 1.0  # 5 / (5+0+0+0)


class TestFormatChainSuggestion:
    """Tests for format_chain_suggestion() reordering."""

    def test_reorder_by_health(self):
        """Should reorder chain to prioritize healthy providers."""
        scores = [("win", 1.0), ("nim", 0.5), ("ollama", 0.2)]
        original_chain = [
            ("nim", "deepseek-v4-pro"),
            ("nim", "deepseek-v4-flash"),
            ("ollama", "deepseek-coder:6.7b"),
            ("win", "deepseek-v2:16b"),
        ]
        reordered, explanation = format_chain_suggestion(scores, original_chain)

        # win should come first
        assert reordered[0][0] == "win"
        # ollama should come last
        assert reordered[-1][0] == "ollama"
        # All models preserved
        assert len(reordered) == 4

    def test_empty_chain(self):
        """Should handle empty chain gracefully."""
        scores = [("nim", 1.0)]
        reordered, explanation = format_chain_suggestion(scores, [])
        assert reordered == []

    def test_explanation_text(self):
        """Should generate readable explanation."""
        scores = [("win", 0.8), ("nim", 0.5)]
        original_chain = [
            ("nim", "model-a"),
            ("win", "model-b"),
        ]
        reordered, explanation = format_chain_suggestion(scores, original_chain)
        assert "win (80%)" in explanation
        assert "nim (50%)" in explanation
        assert "->" in explanation

    def test_unscored_providers_appended(self):
        """Should append providers that weren't scored."""
        scores = [("win", 1.0)]  # ollama not scored
        original_chain = [
            ("nim", "model-a"),
            ("win", "model-b"),
            ("ollama", "model-c"),
        ]
        reordered, explanation = format_chain_suggestion(scores, original_chain)
        assert len(reordered) == 3  # all preserved
        # win first (scored), then others
        assert reordered[0][0] == "win"


class TestIntegrationWorkflow:
    """Integration tests simulating real fallback scenario."""

    def test_full_fallback_workflow(self):
        """Should handle a complete fallback scenario: attempt multiple providers, aggregate errors."""
        # Simulate provider attempts with errors
        provider_attempts = [
            ("nim", "deepseek-v4-pro", "timed out after 120s", 120),
            ("nim", "deepseek-v4-flash", "HTTP 429: rate limited", None),
            ("win", "deepseek-v2:16b", "Connection refused", None),
            ("ollama", "deepseek-coder:6.7b", "timed out after 300s", 300),
        ]

        # Parse each error
        parsed = []
        for prov, model, error_msg, timeout_sec in provider_attempts:
            parsed.append(parse_provider_error(error_msg, prov, model, timeout_sec))

        # Aggregate into user-facing message
        aggregated = aggregate_failures(parsed)

        # Verify message contains key info
        assert "Todos los coders fallaron:" in aggregated
        assert "120s" in aggregated
        assert "300s" in aggregated
        assert "rate limited" in aggregated or "429" in aggregated

    def test_health_tracking_and_reordering(self):
        """Should track health and suggest better ordering."""
        # Simulate history
        stats = {
            "nim": {"successes": 2, "timeouts": 5, "api_errors": 2, "errors": 0},
            "win": {"successes": 8, "timeouts": 1, "api_errors": 0, "errors": 0},
            "ollama": {"successes": 3, "timeouts": 3, "api_errors": 0, "errors": 0},
        }

        scores = score_provider_health(stats)

        # win should rank best
        assert scores[0][0] == "win"
        assert scores[0][1] > 0.8

        # Original chain starts with nim (historically flaky)
        original_chain = [
            ("nim", "deepseek-v4-pro"),
            ("nim", "deepseek-v4-flash"),
            ("win", "deepseek-v2:16b"),
            ("ollama", "deepseek-coder:6.7b"),
        ]

        reordered, explanation = format_chain_suggestion(scores, original_chain)

        # Reordered chain should try win first
        assert reordered[0][0] == "win"
        assert "win" in explanation and ("88%" in explanation or "89%" in explanation or "80%" in explanation)


class TestCoderLLMErrorAggregation:
    """Integration: CoderLLM.call aggregates ALL failed attempts via fallback_util."""

    @staticmethod
    def _import_codex_lib():
        """Import codex_lib with its Linux-only deps stubbed (research_lib, resource)."""
        import types
        import importlib

        if "research_lib" not in sys.modules:
            fake = types.ModuleType("research_lib")
            fake.LLM = object
            fake.MODELO_CAPAZ = "fake-model"
            fake._http_json = lambda *a, **k: {}
            fake.escala_tok = lambda *a, **k: 1000
            fake.load_env = lambda: None
            fake.red_ok = lambda: True
            fake.slug = lambda s: s
            fake.stamp = lambda: "stamp"
            sys.modules["research_lib"] = fake
        try:
            import resource  # noqa: F401  # exists on Linux
        except ImportError:
            sys.modules["resource"] = types.ModuleType("resource")
        sys.modules.pop("codex_lib", None)
        return importlib.import_module("codex_lib")

    def test_call_raises_with_all_attempts(self):
        """When every provider fails, the raised message lists ALL attempts, not just the last."""
        codex_lib = self._import_codex_lib()
        coder = codex_lib.CoderLLM(chain=[
            ("nim", "deepseek-v4-pro"),
            ("win", "deepseek-v2:16b"),
            ("ollama", "deepseek-coder:6.7b"),
        ])
        fallos = {
            "deepseek-v4-pro": TimeoutError("timed out after 120s"),
            "deepseek-v2:16b": ConnectionError("Connection refused to 192.168.50.1"),
            "deepseek-coder:6.7b": RuntimeError("HTTP 429: rate limited"),
        }

        def _boom(system, user, max_tok, model):
            raise fallos[model]

        coder._nim = _boom
        coder._win = _boom
        coder._ollama = _boom
        with pytest.raises(RuntimeError) as exc_info:
            coder.call("sys", "user")
        msg = str(exc_info.value)
        assert "Todos los coders fallaron:" in msg
        assert "nim/deepseek-v4-pro" in msg and "timeout" in msg
        assert "win/deepseek-v2:16b" in msg
        assert "ollama/deepseek-coder:6.7b" in msg
        assert "rate limited" in msg or "429" in msg
        # old behavior showed only the LAST error; earlier attempts must survive
        assert "120s" in msg  # nim timeout mapped from _PROV_TIMEOUT

    def test_call_empty_response_appears_in_aggregate(self):
        """Providers returning empty text are reported as failed attempts too."""
        codex_lib = self._import_codex_lib()
        coder = codex_lib.CoderLLM(chain=[
            ("win", "deepseek-v2:16b"),
            ("ollama", "deepseek-coder:6.7b"),
        ])
        coder._win = lambda system, user, max_tok, model: ""
        coder._ollama = lambda system, user, max_tok, model: (
            (_ for _ in ()).throw(ConnectionError("connection refused")))
        with pytest.raises(RuntimeError) as exc_info:
            coder.call("sys", "user")
        msg = str(exc_info.value)
        assert "win/deepseek-v2:16b" in msg  # the empty one, lost before the fix
        assert "ollama/deepseek-coder:6.7b" in msg

    def test_call_success_path_unchanged(self):
        """A successful provider returns (text, model) with no exception and stats updated."""
        codex_lib = self._import_codex_lib()
        coder = codex_lib.CoderLLM(chain=[("nim", "deepseek-v4-pro")])
        coder._nim = lambda system, user, max_tok, model: "print('hola')"
        text, model = coder.call("sys", "user")
        assert text == "print('hola')"
        assert model == "deepseek-v4-pro"
        assert coder.stats["deepseek-v4-pro"] == 1
        assert coder.errors == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
