#!/usr/bin/env python3
"""fallback_util.py -- Pure helpers for CoderLLM fallback error parsing and aggregation.

No network, ollama, or system deps. Testable with mocks.
- parse_provider_error(): classify exception into error type
- aggregate_failures(): format all attempts into readable message
- score_provider_health(): rank providers by success ratio
"""


def parse_provider_error(exception, provider_type, model, timeout_sec=None):
    """Classify a provider error and return structured dict.

    Args:
        exception: The exception or error message (str or Exception)
        provider_type: "nim", "win", "ollama"
        model: model name (str)
        timeout_sec: timeout value if known (int or None)

    Returns:
        {
            "provider": provider_type,
            "model": model,
            "error_type": "timeout" | "connection" | "api_error" | "empty" | "other",
            "reason": short string (max 100 chars),
            "timeout": timeout_sec if timeout error else None
        }
    """
    err_str = str(exception).lower()

    # Classify error type
    if "timeout" in err_str or "timed out" in err_str:
        error_type = "timeout"
    elif "connection" in err_str or "refused" in err_str:
        error_type = "connection"
    elif "429" in err_str or "rate" in err_str or "limited" in err_str:
        error_type = "api_error"
    elif "http" in err_str and ("5" in err_str[0:10] or "4" in err_str[0:10]):
        error_type = "api_error"
    elif "devolvio vacio" in err_str or "empty" in err_str:
        error_type = "empty"
    else:
        error_type = "other"

    # Truncate reason to 100 chars
    full_reason = str(exception)
    reason = full_reason[:100] if len(full_reason) > 100 else full_reason

    return {
        "provider": provider_type,
        "model": model,
        "error_type": error_type,
        "reason": reason,
        "timeout": timeout_sec if error_type == "timeout" else None,
    }


def aggregate_failures(attempts_list):
    """Format a list of provider attempts into a readable error message.

    Args:
        attempts_list: list of dicts with keys:
            - provider: str ("nim", "win", "ollama")
            - model: str (model name)
            - error_type: str (from parse_provider_error)
            - reason: str (error description)
            - timeout: int or None (timeout seconds if applicable)

    Returns:
        Formatted multi-line string suitable for error messages.
        If no attempts, returns empty string.
    """
    if not attempts_list:
        return ""

    lines = ["Todos los coders fallaron:"]

    for attempt in attempts_list:
        provider = attempt.get("provider", "?")
        model = attempt.get("model", "?")
        error_type = attempt.get("error_type", "other")
        reason = attempt.get("reason", "unknown")
        timeout = attempt.get("timeout")

        # Format by error type
        if error_type == "timeout":
            msg = f"{provider}/{model}: timeout"
            if timeout:
                msg += f" (waited {timeout}s)"
        elif error_type == "connection":
            msg = f"{provider}/{model}: connection refused"
        elif error_type == "api_error":
            msg = f"{provider}/{model}: API error ({reason})"
        elif error_type == "empty":
            msg = f"{provider}/{model}: no response"
        else:
            msg = f"{provider}/{model}: {reason}"

        lines.append(f"  - {msg}")

    return "\n".join(lines)


def score_provider_health(stats_dict):
    """Rank providers by success ratio.

    Args:
        stats_dict: dict mapping provider_type -> counts dict
            Example:
            {
                "nim": {"successes": 5, "timeouts": 2, "api_errors": 1},
                "win": {"successes": 8, "timeouts": 0, "errors": 0},
                "ollama": {"successes": 3, "timeouts": 1, "errors": 0},
            }

    Returns:
        Sorted list of (provider_type, health_score) tuples, highest score first.
        health_score = successes / (successes + failures).
        Providers with no attempts get score 0.0.
    """
    scores = []

    for provider, counts in stats_dict.items():
        successes = counts.get("successes", 0)
        timeouts = counts.get("timeouts", 0)
        api_errors = counts.get("api_errors", 0)
        errors = counts.get("errors", 0)

        total_attempts = successes + timeouts + api_errors + errors
        if total_attempts == 0:
            score = 0.0
        else:
            score = successes / total_attempts

        scores.append((provider, score))

    # Sort by score descending
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


def format_chain_suggestion(scores_list, original_chain):
    """Format a reordered provider chain based on health scores.

    Args:
        scores_list: output of score_provider_health()
        original_chain: original chain list of (provider_type, model) tuples

    Returns:
        Tuple of:
        - reordered_chain: new chain prioritizing healthy providers
        - explanation: str describing reordering

    Note: This is a simple heuristic. Does not handle multiple models per provider.
    """
    if not original_chain:
        return original_chain, ""

    # Group original chain by provider type
    by_provider = {}
    for prov, model in original_chain:
        if prov not in by_provider:
            by_provider[prov] = []
        by_provider[prov].append((prov, model))

    # Reorder by health score
    reordered = []
    explanation_parts = []

    for provider, score in scores_list:
        if provider in by_provider:
            reordered.extend(by_provider[provider])
            health_pct = int(score * 100)
            explanation_parts.append(f"{provider} ({health_pct}%)")

    # Add any remaining providers not scored
    for prov, entries in by_provider.items():
        if prov not in [p for p, _ in scores_list]:
            reordered.extend(entries)
            explanation_parts.append(f"{prov} (unscored)")

    explanation = "Suggested provider order by health: " + " -> ".join(explanation_parts)

    return reordered, explanation
