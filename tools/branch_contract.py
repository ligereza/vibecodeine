"""Shared interpretation of Git refs and branch profiles.

``branch_profile.json`` was originally written for canonical checkouts and its
``branch`` field therefore means the lane that owns the work.  A topic or
worktree checkout can inherit that profile without becoming the canonical ref.
This module keeps that distinction in one small compatibility layer used by
the existing capability, release and runtime checks.
"""

from __future__ import annotations

from typing import Any, Mapping


CANONICAL_REFS = frozenset({"main", "MAK", "FLUJO", "historia"})
LANES = frozenset({"main", "MAK", "FLUJO", "integrated"})


def ref_name(value: str | None) -> str:
    """Normalize a local or ``refs/remotes/...`` name to its branch name."""
    text = str(value or "").strip()
    if text.startswith("refs/remotes/"):
        text = text.removeprefix("refs/remotes/")
        if "/" in text:
            text = text.split("/", 1)[1]
    elif text.startswith("refs/heads/"):
        text = text.removeprefix("refs/heads/")
    return text


def _pattern_kind(current_ref: str) -> str:
    if current_ref in CANONICAL_REFS:
        return {
            "main": "integrated",
            "MAK": "operational",
            "FLUJO": "operational",
            "historia": "historical",
        }[current_ref]
    if current_ref.startswith("dependabot/"):
        return "automated"
    if current_ref == "DIRECTOR" or current_ref.startswith("archive/"):
        return "historical"
    if current_ref.startswith("integration/") or "main-union" in current_ref:
        return "integration-alias"
    if current_ref.startswith("worktree-"):
        return "worktree"
    if current_ref.split("/", 1)[0] in {"docs", "feat", "fix", "test", "chore", "perf", "refactor"}:
        return "topic"
    return "auxiliary"


def interpret_ref(current_ref: str | None, profile: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Return one semantic view without claiming a topic is its parent ref."""
    current = ref_name(current_ref)
    profile = profile if isinstance(profile, Mapping) else {}
    declared = str(
        profile.get("canonical_ref")
        or profile.get("lane")
        or profile.get("branch")
        or ""
    ).strip()
    pattern_kind = _pattern_kind(current)
    kind = str(profile.get("kind") or "").strip() or pattern_kind
    if current not in CANONICAL_REFS:
        # A copied canonical profile is inherited metadata, not a claim about
        # the current ref.  Names with their own topology signal take priority.
        kind = pattern_kind
    if "main-union" in current:
        canonical = "main"
        lane = "integrated"
    elif current in CANONICAL_REFS:
        canonical = declared if declared in CANONICAL_REFS else current
        lane = (
            str(profile.get("lane"))
            if profile.get("lane") in LANES
            else "integrated" if canonical == "main" else canonical
        )
    else:
        canonical = declared if declared in {"MAK", "FLUJO", "main", "historia"} else None
        if pattern_kind == "historical" and not canonical:
            canonical = current or None
            lane = "historical"
        else:
            lane = "integrated" if canonical == "main" else canonical

    if kind == "historical":
        target = None
    elif kind == "integrated" or lane == "integrated":
        target = "main"
    else:
        target = lane if lane in {"MAK", "FLUJO"} else None

    explicit_current = profile.get("current_ref")
    issues: list[str] = []
    if current in CANONICAL_REFS and canonical != current:
        issues.append(f"profile_branch_mismatch:{canonical or declared or None}->{current}")
    if explicit_current and str(explicit_current) != current:
        issues.append(f"profile_current_ref_mismatch:{explicit_current}->{current}")
    if current not in CANONICAL_REFS and not canonical:
        issues.append("profile_canonical_ref_missing")
    if current not in CANONICAL_REFS and declared and declared != canonical:
        issues.append(f"profile_lane_mismatch:{declared}->{canonical}")

    return {
        "current_ref": current or None,
        "canonical_ref": canonical,
        "lane": lane,
        "kind": kind,
        "integration_target": target,
        "profile_declared_ref": declared or None,
        "profile_scope": "canonical" if current in CANONICAL_REFS else "inherited",
        "issues": issues,
    }


def disposition(current_ref: str | None, semantics: Mapping[str, Any]) -> str:
    """Name the bounded disposition used by the ref inventory."""
    current = ref_name(current_ref)
    kind = str(semantics.get("kind") or "auxiliary")
    if current in CANONICAL_REFS:
        return "canonical"
    if kind == "historical":
        return "historical_preserve"
    if kind == "automated":
        return "automated_reevaluate"
    if kind == "integration-alias":
        return "alias_or_checkpoint"
    if kind == "worktree":
        return "worktree_checkpoint"
    if kind == "topic":
        return "topic_active_or_recover_selectively"
    return "auxiliary_review"
