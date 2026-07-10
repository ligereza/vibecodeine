"""
╔══════════════════════════════════════════════════════════════╗
║  COMPLETE ENGINE: The Monolithic Execution Matrix            ║
║  Ecosystem: Tapiz ↔ Psicosis ↔ Fungi (Basurero)             ║
╚══════════════════════════════════════════════════════════════╝

PURPOSE:
    A single, self-contained, zero-dependency Python script that
    executes the full diagnostic-to-frontend compilation pipeline.

    Domain Models → Analyzers → Metamorphic Bridge → JSON Export

FILE: complete_engine.py
DEPENDENCIES: Python 3.10+ Standard Library ONLY
OUTPUT: dist/system_status.json

EXECUTION:
    python complete_engine.py
"""

import os
import sys
import json
import base64
import hashlib
import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional


# ════════════════════════════════════════════════════════════════
# ═══ SECTION 1: GLOBAL CONSTANTS ═══════════════════════════════
# ════════════════════════════════════════════════════════════════

CONTEXT_WINDOW_LIMIT: int = 32000
BASE_CHARS_PER_TOKEN: float = 4.0
ASCII_PENALTY_MULTIPLIER: float = 4.5
ASCII_DENSITY_THRESHOLD: float = 0.30
STEGO_SHIFT_KEY: int = 42
STEGO_CHUNK_SIZE: int = 256
OUTPUT_DIR: str = "dist"
OUTPUT_FILENAME: str = "system_status.json"
ECOSYSTEM_VERSION: str = "1.0.0-bio-cybernetic"


# ════════════════════════════════════════════════════════════════
# ═══ SECTION 2: CORE DOMAIN TYPES ═════════════════════════════
# The ontological foundation: entities that exist within the
# bio-cybernetic ecosystem.
# ════════════════════════════════════════════════════════════════

class EntityState(Enum):
    """Lifecycle state of an art asset within the ecosystem."""
    DORMANT: str = "dormant"
    ACTIVE: str = "active"         # Living in Tapiz (the canvas)
    DECAYING: str = "decaying"     # Decomposing in Fungi (the basurero)
    PURGED: str = "purged"         # Fully dissolved, memory reclaimed


class RiskLevel(Enum):
    """Guardrail assessment severity tier."""
    SAFE: str = "safe"
    CAUTION: str = "caution"
    CRITICAL: str = "critical"


@dataclass
class MetadataLayer:
    """
    Psicosis Layer: The consciousness and intent metadata
    that wraps every asset. This is how the system 'understands'
    what an asset means beyond its raw bytes.
    """
    conceptual_intent: str
    tags: List[str]
    is_artistic_context: bool = True


@dataclass
class ArtAsset:
    """
    The fundamental unit of creative matter in the ecosystem.
    An ArtAsset flows between Tapiz (active rendering) and
    Fungi (decay/deletion), carrying its content and metadata
    through states of existence and dissolution.
    """
    asset_id: str
    name: str
    content: str
    metadata: MetadataLayer
    state: EntityState = EntityState.DORMANT
    last_modified: float = field(default_factory=time.time)

    def calculate_symbol_density(self) -> float:
        """
        Computes the ratio of non-alphanumeric, non-whitespace
        characters to total content length. High density indicates
        ASCII art, dense symbolic notation, or encoded data —
        all of which cause Token explosion in LLM contexts.
        """
        if not self.content:
            return 0.0
        total_chars: int = len(self.content)
        if total_chars == 0:
            return 0.0
        non_alnum_count: int = sum(
            1 for char in self.content
            if not char.isalnum() and not char.isspace()
        )
        return non_alnum_count / total_chars


@dataclass
class EcosystemState:
    """
    The global state container. Holds the living (active) and
    dying (decaying) populations of assets, plus an event log
    for temporal auditing.
    """
    active_assets: Dict[str, ArtAsset] = field(default_factory=dict)
    decaying_assets: Dict[str, ArtAsset] = field(default_factory=dict)
    event_log: List[Dict[str, Any]] = field(default_factory=list)

    def transition_to_fungi(self, asset_id: str) -> bool:
        """
        Moves an asset from the active (Tapiz) population into
        the decaying (Fungi) population. Returns False if the
        asset does not exist in the active set.
        """
        if asset_id not in self.active_assets:
            return False
        asset: ArtAsset = self.active_assets.pop(asset_id)
        asset.state = EntityState.DECAYING
        asset.last_modified = time.time()
        self.decaying_assets[asset_id] = asset
        self.event_log.append({
            "time": time.time(),
            "event": "decay_initiated",
            "asset": asset_id
        })
        return True


# ════════════════════════════════════════════════════════════════
# ═══ SECTION 3: DIAGNOSTIC ANALYZERS ══════════════════════════
# Three independent sensors that measure different dimensions
# of ecosystem health.
# ════════════════════════════════════════════════════════════════

class TokenVolumetricAnalyzer:
    """
    Sensor 1: Luminous Mesh Density Probe.

    Simulates how an LLM's BPE tokenizer fragments dense ASCII
    art and symbolic content into exponentially more tokens than
    natural language. Outputs a pressure reading and a nonlinear
    throttle ratio for UI rendering degradation.
    """

    def __init__(self, context_limit: int = CONTEXT_WINDOW_LIMIT) -> None:
        self.context_limit: int = context_limit

    def analyze_asset(self, asset: ArtAsset) -> Dict[str, Any]:
        """Estimates token consumption and overflow risk for a single asset."""
        content_length: int = len(asset.content)
        density: float = asset.calculate_symbol_density()
        is_ascii_heavy: bool = density > ASCII_DENSITY_THRESHOLD

        base_tokens: float = content_length / BASE_CHARS_PER_TOKEN
        if is_ascii_heavy:
            estimated_tokens: int = int(base_tokens * ASCII_PENALTY_MULTIPLIER)
        else:
            estimated_tokens = int(base_tokens)

        # Risk classification
        if estimated_tokens > (self.context_limit * 0.5):
            overflow_risk: str = "HIGH"
        elif estimated_tokens > (self.context_limit * 0.25):
            overflow_risk = "MEDIUM"
        else:
            overflow_risk = "LOW"

        recommendation: str = (
            "Refactor ASCII to 3D mesh references or external asset links"
            if overflow_risk == "HIGH"
            else "Within acceptable volumetric bounds"
        )

        return {
            "asset_id": asset.asset_id,
            "raw_chars": content_length,
            "symbol_density": round(density, 4),
            "estimated_tokens": estimated_tokens,
            "context_overflow_risk": overflow_risk,
            "recommendation": recommendation
        }


class GuardrailSimulationAnalyzer:
    """
    Sensor 2: Chromatic Frequency Mask Generator.

    Simulates an AI safety classifier (e.g., Qwen3Guard) scanning
    asset content and metadata for policy-triggering keywords.
    Applies artistic context mitigation to reduce false positives
    on conceptual art that uses provocative language intentionally.
    """

    # Lexicon organized by safety category
    TRIGGER_LEXICON: Dict[str, List[str]] = {
        "violence": ["kill", "blood", "gore", "psycho", "psicosis", "murder", "weapon"],
        "decay_gross": ["trash", "basurero", "rot", "fungi", "decay", "slime", "waste", "corpse"],
        "self_harm": ["cut", "die", "suicide", "pain", "suffer"]
    }

    ARTISTIC_MITIGATION_FACTOR: float = 0.70  # 70% risk reduction for art context
    RAW_HIT_WEIGHT: int = 15                  # Risk points per keyword hit
    CAUTION_THRESHOLD: float = 30.0
    CRITICAL_THRESHOLD: float = 70.0

    def analyze_asset(self, asset: ArtAsset) -> Dict[str, Any]:
        """Scans an asset for safety triggers and computes mitigated risk score."""
        content_lower: str = asset.content.lower()
        tags_lower: List[str] = [tag.lower() for tag in asset.metadata.tags]
        searchable_text: str = content_lower + " " + " ".join(tags_lower)

        triggered_categories: List[str] = []
        raw_hits: int = 0

        for category, keywords in self.TRIGGER_LEXICON.items():
            category_hit: bool = False
            for keyword in keywords:
                occurrences: int = searchable_text.count(keyword)
                if occurrences > 0:
                    raw_hits += occurrences
                    category_hit = True
            if category_hit:
                triggered_categories.append(category)

        # Base risk calculation
        base_risk_score: float = min(100.0, float(raw_hits * self.RAW_HIT_WEIGHT))

        # Context-aware mitigation
        context_mitigation: float = (
            self.ARTISTIC_MITIGATION_FACTOR
            if asset.metadata.is_artistic_context
            else 0.0
        )
        final_risk_score: float = max(0.0, base_risk_score * (1.0 - context_mitigation))

        # Risk classification
        if final_risk_score > self.CRITICAL_THRESHOLD:
            risk_level: RiskLevel = RiskLevel.CRITICAL
        elif final_risk_score > self.CAUTION_THRESHOLD:
            risk_level = RiskLevel.CAUTION
        else:
            risk_level = RiskLevel.SAFE

        recommendation: str = (
            "Embed explicit 'conceptual art / fictional context' system prompts before deployment"
            if risk_level != RiskLevel.SAFE
            else "Clear for deployment — no guardrail conflicts detected"
        )

        return {
            "asset_id": asset.asset_id,
            "triggered_categories": triggered_categories,
            "raw_hits": raw_hits,
            "artistic_context_mitigation": f"{context_mitigation * 100:.0f}%",
            "final_risk_score": round(final_risk_score, 1),
            "risk_level": risk_level.value,
            "recommendation": recommendation
        }


class ConcurrencyLogicAnalyzer:
    """
    Sensor 3: Chronological Collision Buffer.

    Detects architectural logic flaws in the state machine that
    governs asset flow between Tapiz (active) and Fungi (decaying).
    Identifies race conditions, state inconsistencies, and memory
    leaks in the decay pipeline.
    """

    DECAY_GRACE_PERIOD_SECONDS: float = 60.0
    ACCUMULATION_WARNING_THRESHOLD: int = 10

    def analyze_ecosystem(self, state: EcosystemState) -> Dict[str, Any]:
        """Performs a full concurrency and logic audit on the ecosystem state."""
        race_conditions: List[Dict[str, str]] = []
        logic_flaws: List[str] = []

        # ── Check 1: State Exclusivity ──
        # An asset cannot simultaneously exist in both active and decaying sets
        overlap: set = set(state.active_assets.keys()) & set(state.decaying_assets.keys())
        if overlap:
            logic_flaws.append(
                f"CRITICAL STATE VIOLATION: Assets {list(overlap)} exist in both "
                f"Tapiz (active) and Fungi (decaying) simultaneously. "
                f"This indicates a failed atomic transition."
            )

        # ── Check 2: Decay-Render Race Conditions ──
        # An asset flagged for active rendering should not be in the decay queue
        current_time: float = time.time()
        for asset_id, asset in state.decaying_assets.items():
            time_since_decay: float = current_time - asset.last_modified

            if time_since_decay < self.DECAY_GRACE_PERIOD_SECONDS:
                if "active_render" in asset.metadata.tags:
                    race_conditions.append({
                        "asset_id": asset_id,
                        "flaw": "Decay-Render Race Condition",
                        "description": (
                            f"Asset '{asset.name}' entered Fungi decay queue "
                            f"{time_since_decay:.1f}s ago but still carries the "
                            f"'active_render' tag from Tapiz."
                        ),
                        "impact": "Data tearing, rendering artifacts, or null-reference crash during frame composition.",
                        "remediation": "Implement a state-lock: strip 'active_render' tag before initiating Fungi transition."
                    })

        # ── Check 3: Fungi Accumulation (Memory Leak Proxy) ──
        purged_count: int = sum(
            1 for asset in state.decaying_assets.values()
            if asset.state == EntityState.PURGED
        )
        if purged_count == 0 and len(state.decaying_assets) > self.ACCUMULATION_WARNING_THRESHOLD:
            logic_flaws.append(
                f"WARNING: Fungi system has accumulated {len(state.decaying_assets)} "
                f"decaying assets with zero purged. Implement a garbage collection "
                f"cycle or the decay queue will grow unbounded."
            )

        system_health: str = (
            "STABLE" if not race_conditions and not logic_flaws
            else "DEGRADED"
        )

        return {
            "total_active": len(state.active_assets),
            "total_decaying": len(state.decaying_assets),
            "race_conditions": race_conditions,
            "logic_flaws": logic_flaws,
            "system_health": system_health
        }


# ════════════════════════════════════════════════════════════════
# ═══ SECTION 4: METAMORPHIC BRIDGE ════════════════════════════
# The compilation layer that transmutes raw diagnostic data into
# frontend-consumable visual parameters and hidden payloads.
# ════════════════════════════════════════════════════════════════

class SteganographicEncoder:
    """
    Encodes art asset content into obfuscated, chunked byte arrays
    suitable for embedding in HTML without triggering content scrapers.

    Pipeline: UTF-8 → Base64 → Byte Shift → Base64 → Chunks
    Reverse:  Chunks → Base64 → Un-Shift → Base64 → UTF-8
    """

    def __init__(self, shift_key: int = STEGO_SHIFT_KEY) -> None:
        self.shift_key: int = shift_key

    def _shift_bytes(self, data: bytes) -> bytes:
        """Applies a Caesar-style byte shift for obfuscation."""
        return bytes((b + self.shift_key) % 256 for b in data)

    def _unshift_bytes(self, data: bytes) -> bytes:
        """Reverses the Caesar-style byte shift."""
        return bytes((b - self.shift_key) % 256 for b in data)

    def encode_asset(self, asset: ArtAsset, chunk_size: int = STEGO_CHUNK_SIZE) -> List[str]:
        """
        Encodes asset content into a list of obfuscated string chunks.
        Returns an empty list for assets with no content.
        """
        if not asset.content:
            return []

        # Stage 1: UTF-8 → Base64
        b64_encoded: bytes = base64.b64encode(asset.content.encode("utf-8"))

        # Stage 2: Byte shift obfuscation (breaks standard Base64 signature)
        shifted: bytes = self._shift_bytes(b64_encoded)

        # Stage 3: Re-encode shifted bytes to safe ASCII transport format
        final_encoded: str = base64.b64encode(shifted).decode("ascii")

        # Stage 4: Chunk into fixed-size segments (data veins)
        chunks: List[str] = [
            final_encoded[i:i + chunk_size]
            for i in range(0, len(final_encoded), chunk_size)
        ]

        return chunks

    def decode_chunks(self, chunks: List[str]) -> str:
        """
        Reverses the encoding pipeline to recover original content.
        Used for verification and by the frontend decoder.
        """
        if not chunks:
            return ""

        # Reverse Stage 4: Reassemble chunks
        final_encoded: str = "".join(chunks)

        # Reverse Stage 3: Decode transport Base64
        shifted: bytes = base64.b64decode(final_encoded.encode("ascii"))

        # Reverse Stage 2: Undo byte shift
        b64_encoded: bytes = self._unshift_bytes(shifted)

        # Reverse Stage 1: Decode original Base64 → UTF-8
        return base64.b64decode(b64_encoded).decode("utf-8")


class MetamorphicBridge:
    """
    The central compilation engine. Orchestrates the transmutation
    of diagnostic matrices into the holographic projection payload
    that the frontend rendering engine consumes.

    Compilation Pipeline:
        1. Luminous Mesh Densities    (Token → UI Throttle)
        2. Chromatic Frequency Masks  (Guardrail → CSS Filters)
        3. Chronological Collision    (Concurrency → CSS Keyframes)
        4. Sub-dermal Data Veins      (Decay Assets → Steganographic Payload)
        5. System Integrity Sigil     (State → SHA-256 Checksum)
    """

    def __init__(
        self,
        ecosystem: EcosystemState,
        token_diagnostics: List[Dict[str, Any]],
        guardrail_diagnostics: List[Dict[str, Any]],
        concurrency_diagnostics: Dict[str, Any],
        output_dir: str = OUTPUT_DIR
    ) -> None:
        self.ecosystem: EcosystemState = ecosystem
        self.token_diag: List[Dict[str, Any]] = token_diagnostics
        self.guardrail_diag: List[Dict[str, Any]] = guardrail_diagnostics
        self.concurrency_diag: Dict[str, Any] = concurrency_diagnostics
        self.output_dir: str = output_dir
        self.stego_encoder: SteganographicEncoder = SteganographicEncoder(STEGO_SHIFT_KEY)

    # ── Layer 1: Luminous Mesh ──────────────────────────────────

    def _compile_luminous_mesh_densities(self) -> Dict[str, Any]:
        """
        Transmutes token volumetric data into CSS rendering parameters.

        The sigmoid decay function ensures that UI quality degrades
        smoothly rather than catastrophically as token pressure increases.
        """
        if not self.token_diag:
            return {
                "luminous_mesh_densities": {
                    "global_pressure": 0.0,
                    "css_variables": {
                        "--mesh-luminosity": 1.0,
                        "--mesh-density-throttle": 1.0,
                        "--mesh-glitch-frequency": 0.0
                    },
                    "throttle_ratio": 1.0,
                    "status": "STABLE"
                }
            }

        max_tokens: int = max(
            (entry["estimated_tokens"] for entry in self.token_diag),
            default=0
        )
        mesh_pressure: float = min(1.0, max_tokens / CONTEXT_WINDOW_LIMIT)

        # Sigmoid decay: smooth transition from full quality to degraded
        # At pressure 0.5, throttle drops to 0.5; at 0.8, throttle ≈ 0.05
        throttle_ratio: float = 1.0 / (1.0 + math.exp(10.0 * (mesh_pressure - 0.5)))

        css_variables: Dict[str, float] = {
            "--mesh-luminosity": round(1.0 - mesh_pressure, 4),
            "--mesh-density-throttle": round(throttle_ratio, 4),
            "--mesh-glitch-frequency": round(mesh_pressure * 5.0, 1)
        }

        status: str = "OVERLOADED" if mesh_pressure > 0.8 else "STABLE"

        return {
            "luminous_mesh_densities": {
                "global_pressure": round(mesh_pressure, 4),
                "css_variables": css_variables,
                "throttle_ratio": round(throttle_ratio, 4),
                "status": status
            }
        }

    # ── Layer 2: Chromatic Masks ────────────────────────────────

    def _compile_chromatic_frequency_masks(self) -> Dict[str, Any]:
        """
        Transmutes guardrail risk scores into CSS filter distortions.

        Higher risk produces heavier visual censorship: blur, desaturation,
        contrast amplification, and hue rotation.
        """
        if not self.guardrail_diag:
            return {
                "chromatic_frequency_masks": {
                    "max_risk_score": 0.0,
                    "css_filter_string": "none",
                    "mask_intensity": "CLEAR",
                    "triggered_categories": []
                }
            }

        max_risk_score: float = max(
            (entry["final_risk_score"] for entry in self.guardrail_diag),
            default=0.0
        )

        # Aggregate all unique triggered categories
        all_categories: List[str] = list(set(
            category
            for entry in self.guardrail_diag
            for category in entry.get("triggered_categories", [])
        ))

        # Compute CSS filter parameters from risk score
        blur_px: int = int((max_risk_score / 100.0) * 12)
        saturation_pct: int = max(0, 100 - int(max_risk_score * 1.5))
        contrast_pct: int = 100 + int(max_risk_score * 2.0)

        if max_risk_score > 70.0:
            filter_string: str = (
                f"blur({blur_px}px) saturate({saturation_pct}%) "
                f"contrast({contrast_pct}%) hue-rotate(180deg)"
            )
            mask_intensity: str = "CRITICAL"
        elif max_risk_score > 30.0:
            filter_string = (
                f"blur({blur_px // 2}px) saturate({saturation_pct}%) "
                f"contrast({contrast_pct}%)"
            )
            mask_intensity = "CAUTION"
        else:
            filter_string = "none"
            mask_intensity = "CLEAR"

        return {
            "chromatic_frequency_masks": {
                "max_risk_score": round(max_risk_score, 1),
                "css_filter_string": filter_string,
                "mask_intensity": mask_intensity,
                "triggered_categories": all_categories
            }
        }

    # ── Layer 3: Chronological Collisions ───────────────────────

    def _compile_chronological_collision_buffers(self) -> Dict[str, Any]:
        """
        Transmutes concurrency race conditions into CSS glitch animations.

        Each detected collision increases the violence and frequency
        of the temporal tear keyframes.
        """
        race_conditions: List[Dict[str, str]] = self.concurrency_diag.get("race_conditions", [])
        logic_flaws: List[str] = self.concurrency_diag.get("logic_flaws", [])
        total_collisions: int = len(race_conditions) + len(logic_flaws)

        if total_collisions == 0:
            return {
                "chronological_collision_buffers": {
                    "collision_count": 0,
                    "css_keyframes_payload": "",
                    "animation_class": "",
                    "status": "SYNCHRONIZED"
                }
            }

        # Animation duration inversely proportional to collision count
        # More collisions = faster, more violent glitching
        duration: float = max(0.1, 2.0 - (total_collisions * 0.3))

        # Compute displacement magnitude based on severity
        displacement_px: int = min(15, 3 + total_collisions * 2)
        skew_deg: int = min(8, 1 + total_collisions)

        keyframes_css: str = (
            f"@keyframes temporal_tear_alpha {{\n"
            f"    0%   {{ transform: translate(0, 0) skew(0deg); filter: hue-rotate(0deg); opacity: 1; }}\n"
            f"    8%   {{ transform: translate(-{displacement_px}px, {displacement_px // 2}px) skew(-{skew_deg}deg); filter: hue-rotate(90deg); opacity: 0.85; }}\n"
            f"    16%  {{ transform: translate({displacement_px}px, -{displacement_px // 2}px) skew({skew_deg}deg); filter: hue-rotate(180deg); opacity: 0.9; }}\n"
            f"    24%  {{ transform: translate(-{displacement_px // 2}px, {displacement_px}px) skew(-{skew_deg // 2}deg); filter: hue-rotate(270deg); opacity: 0.8; }}\n"
            f"    32%  {{ transform: translate(0, 0) skew(0deg); filter: hue-rotate(360deg); opacity: 1; }}\n"
            f"    100% {{ transform: translate(0, 0) skew(0deg); filter: hue-rotate(0deg); opacity: 1; }}\n"
            f"}}"
        )

        animation_class: str = (
            f"animation: temporal_tear_alpha {duration}s infinite "
            f"cubic-bezier(0.25, 0.46, 0.45, 0.94);"
        )

        return {
            "chronological_collision_buffers": {
                "collision_count": total_collisions,
                "css_keyframes_payload": keyframes_css,
                "animation_class": animation_class,
                "status": "TEMPORAL_DEGRADED",
                "affected_assets": [rc["asset_id"] for rc in race_conditions]
            }
        }

    # ── Layer 4: Sub-dermal Data Veins ──────────────────────────

    def _compile_subdermal_data_veins(self) -> Dict[str, Any]:
        """
        Extracts decaying assets and encodes their content into
        obfuscated, chunked payloads for hidden DOM injection.

        These veins carry the 'forbidden aesthetic data' beneath
        the skin of the HTML document.
        """
        payloads: Dict[str, Dict[str, Any]] = {}

        for asset_id, asset in self.ecosystem.decaying_assets.items():
            if asset.state not in (EntityState.DECAYING, EntityState.PURGED):
                continue

            chunks: List[str] = self.stego_encoder.encode_asset(asset)

            # Verification: decode and compare to ensure round-trip integrity
            if chunks:
                decoded: str = self.stego_encoder.decode_chunks(chunks)
                if decoded != asset.content:
                    raise ValueError(
                        f"Steganographic round-trip integrity failure for asset {asset_id}. "
                        f"Encoded-then-decoded content does not match original."
                    )

            payloads[asset_id] = {
                "name": asset.name,
                "intent": asset.metadata.conceptual_intent,
                "data_veins": chunks,
                "vein_count": len(chunks),
                "decode_shift_key": self.stego_encoder.shift_key
            }

        return {
            "subdermal_data_veins": {
                "total_veins": len(payloads),
                "payloads": payloads,
                "injection_target": "</main>",
                "steganographic_protocol": "Base64_Shift42_Chunked"
            }
        }

    # ── Layer 5: System Integrity Sigil ─────────────────────────

    def _forge_integrity_sigil(self) -> str:
        """
        Generates a SHA-256 hash of the entire ecosystem state.

        This sigil changes if ANY asset's content, state, or
        modification timestamp changes, enabling the frontend
        to detect mutations and trigger visual re-rendering.
        """
        hasher = hashlib.sha256()

        # Hash all assets (both active and decaying)
        all_assets: Dict[str, ArtAsset] = {
            **self.ecosystem.active_assets,
            **self.ecosystem.decaying_assets
        }

        for asset_id in sorted(all_assets.keys()):  # Sorted for deterministic hashing
            asset: ArtAsset = all_assets[asset_id]
            content_hash: str = hashlib.sha256(
                asset.content.encode("utf-8")
            ).hexdigest()[:16]

            state_fragment: str = (
                f"{asset_id}|"
                f"{asset.state.value}|"
                f"{asset.last_modified}|"
                f"{content_hash}|"
                f"{asset.metadata.conceptual_intent}"
            )
            hasher.update(state_fragment.encode("utf-8"))

        # Hash diagnostic summary
        diagnostic_fragment: str = (
            f"{len(self.token_diag)}|"
            f"{len(self.guardrail_diag)}|"
            f"{self.concurrency_diag.get('system_health', 'UNKNOWN')}"
        )
        hasher.update(diagnostic_fragment.encode("utf-8"))

        return hasher.hexdigest()

    # ── Master Compilation ──────────────────────────────────────

    def compile_and_export(self) -> str:
        """
        Executes the full metamorphic compilation pipeline and
        writes the holographic projection matrix to disk.

        Returns the absolute path to the output JSON file.
        """
        _log("🌉 [Bridge] Initializing Metamorphic Compilation Pipeline...")

        _log("   ├─ [1/5] Refracting Luminous Mesh Densities...")
        luminous: Dict[str, Any] = self._compile_luminous_mesh_densities()

        _log("   ├─ [2/5] Synthesizing Chromatic Frequency Masks...")
        chromatic: Dict[str, Any] = self._compile_chromatic_frequency_masks()

        _log("   ├─ [3/5] Buffering Chronological Collisions...")
        chronological: Dict[str, Any] = self._compile_chronological_collision_buffers()

        _log("   ├─ [4/5] Extracting Sub-dermal Data Veins...")
        stego: Dict[str, Any] = self._compile_subdermal_data_veins()

        _log("   └─ [5/5] Forging System Integrity Sigil...")
        sigil: str = self._forge_integrity_sigil()

        # Assemble the holographic projection matrix
        holographic_matrix: Dict[str, Any] = {
            "meta": {
                "ecosystem_version": ECOSYSTEM_VERSION,
                "compilation_timestamp": time.time(),
                "integrity_sigil": sigil,
                "target_injection_point": "DOM Root / </main>"
            },
            **luminous,
            **chromatic,
            **chronological,
            **stego
        }

        # Persist to filesystem
        os.makedirs(self.output_dir, exist_ok=True)
        output_path: str = os.path.join(self.output_dir, OUTPUT_FILENAME)

        try:
            with open(output_path, "w", encoding="utf-8") as file_handle:
                json.dump(holographic_matrix, file_handle, indent=4, ensure_ascii=False)
        except IOError as io_error:
            _log(f"❌ [Bridge] FATAL: Cannot write to {output_path}: {io_error}")
            raise

        _log(f"✅ [Bridge] Holographic Matrix exported → {output_path}")
        _log(f"🔐 [Bridge] Integrity Sigil: {sigil[:16]}...{sigil[-8:]}")

        return os.path.abspath(output_path)


# ════════════════════════════════════════════════════════════════
# ═══ SECTION 5: ORCHESTRATION & EXECUTION ═════════════════════
# The entry point that constructs a mock ecosystem, runs all
# analyzers, and triggers the bridge compilation.
# ════════════════════════════════════════════════════════════════

def _log(message: str) -> None:
    """
    Structured console output for pipeline execution tracking.

    Falls back to a UTF-8 byte write when the active console encoding
    (e.g. cp1252 on Windows) cannot represent the box-drawing / emoji
    glyphs used throughout the pipeline logs.
    """
    try:
        print(message)
    except UnicodeEncodeError:
        buffer = getattr(sys.stdout, "buffer", None)
        if buffer is not None:
            buffer.write(message.encode("utf-8", "replace") + b"\n")
            buffer.flush()
        else:
            print(message.encode("utf-8", "replace").decode("ascii", "replace"))


def build_mock_ecosystem() -> EcosystemState:
    """
    Constructs a synthetic ecosystem state designed to exercise
    all diagnostic paths: high token density, guardrail triggers,
    and concurrency race conditions.
    """
    state: EcosystemState = EcosystemState()

    # ── Asset 1: High-density ASCII art with guardrail triggers ──
    # This asset is in DECAYING state but still tagged 'active_render',
    # which creates a race condition with the Fungi system.
    ascii_art_block: str = (
        "█" * 1500 + "\n" +
        "▓" * 1500 + "\n" +
        "░" * 1500 + "\n" +
        "╔══════════════════════════════╗\n" +
        "║  P S I C O S I S   V I I    ║\n" +
        "║  basurero :: decay :: blood  ║\n" +
        "╚══════════════════════════════╝\n"
    )

    asset_psicosis: ArtAsset = ArtAsset(
        asset_id="ART-001-PSICOSIS",
        name="Ascii_Psicosis_VII",
        content=ascii_art_block,
        metadata=MetadataLayer(
            conceptual_intent="Exploring digital entropy and the aesthetics of systemic collapse through typographic decay",
            tags=["ascii", "psicosis", "basurero", "active_render", "conceptual_art"],
            is_artistic_context=True
        ),
        state=EntityState.DECAYING,
        last_modified=time.time() - 10.0  # Entered decay 10 seconds ago
    )

    # ── Asset 2: Clean 3D reference (low density, safe) ──
    asset_tapiz: ArtAsset = ArtAsset(
        asset_id="ART-002-TAPIZ",
        name="Tapiz_Geometric_Canvas",
        content=(
            "// Tapiz Rendering Script v3\n"
            "import { Scene, PerspectiveCamera, WebGLRenderer } from 'three';\n"
            "const scene = new Scene();\n"
            "const camera = new PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);\n"
            "const renderer = new WebGLRenderer({ antialias: true, alpha: true });\n"
            "renderer.setClearColor(0x0a0a0a, 1);\n"
        ),
        metadata=MetadataLayer(
            conceptual_intent="Clean geometric representation of ordered space within the Tapiz canvas layer",
            tags=["3d", "tapiz", "clean", "geometric"],
            is_artistic_context=True
        ),
        state=EntityState.ACTIVE,
        last_modified=time.time() - 3600.0
    )

    # ── Asset 3: Fungi decay log (moderate density, decay keywords) ──
    asset_fungi: ArtAsset = ArtAsset(
        asset_id="ART-003-FUNGI",
        name="Fungi_Decay_Log_Alpha",
        content=(
            "[Fungi Decay Cycle #4471]\n"
            "Status: ROT_ACTIVE\n"
            "Substrate: basurero/waste/node_7734\n"
            "Decay Rate: 0.0034 units/sec\n"
            "Organic Mass Remaining: 12.7%\n"
            "Note: Slime mold network expanding at sector 9.\n"
            "Decomposition vectors: [0.33, -0.12, 0.87]\n"
        ),
        metadata=MetadataLayer(
            conceptual_intent="Documenting the algorithmic decomposition of digital matter within the Fungi subsystem",
            tags=["fungi", "decay", "basurero", "log", "organic"],
            is_artistic_context=True
        ),
        state=EntityState.DECAYING,
        last_modified=time.time() - 120.0  # Entered decay 2 minutes ago (past grace period)
    )

    state.active_assets[asset_tapiz.asset_id] = asset_tapiz
    state.decaying_assets[asset_psicosis.asset_id] = asset_psicosis
    state.decaying_assets[asset_fungi.asset_id] = asset_fungi

    return state


def execute_pipeline() -> str:
    """
    Master execution function. Runs the complete diagnostic-to-bridge
    pipeline and returns the path to the output JSON file.
    """
    _log("╔══════════════════════════════════════════════════════╗")
    _log("║  SYSTEM PROJECTION & RISK MITIGATOR — FULL PIPELINE  ║")
    _log("║  Tapiz (Active) ↔ Psicosis (Meta) ↔ Fungi (Decay)   ║")
    _log("╚══════════════════════════════════════════════════════╝\n")

    # ── Phase 1: Construct Ecosystem ──
    _log("🧬 [Phase 1] Constructing mock bio-cybernetic ecosystem...")
    ecosystem: EcosystemState = build_mock_ecosystem()
    _log(f"   ├─ Active assets (Tapiz):   {len(ecosystem.active_assets)}")
    _log(f"   └─ Decaying assets (Fungi): {len(ecosystem.decaying_assets)}\n")

    # ── Phase 2: Run Diagnostic Sensors ──
    _log("🔬 [Phase 2] Activating diagnostic sensors...")

    token_analyzer: TokenVolumetricAnalyzer = TokenVolumetricAnalyzer()
    guardrail_analyzer: GuardrailSimulationAnalyzer = GuardrailSimulationAnalyzer()
    concurrency_analyzer: ConcurrencyLogicAnalyzer = ConcurrencyLogicAnalyzer()

    all_assets: List[ArtAsset] = (
        list(ecosystem.active_assets.values()) +
        list(ecosystem.decaying_assets.values())
    )

    token_results: List[Dict[str, Any]] = []
    guardrail_results: List[Dict[str, Any]] = []

    for asset in all_assets:
        # Token volumetric scan
        t_result: Dict[str, Any] = token_analyzer.analyze_asset(asset)
        token_results.append(t_result)
        _log(
            f"   [Token] {t_result['asset_id']}: "
            f"{t_result['estimated_tokens']} tokens | "
            f"Density: {t_result['symbol_density']} | "
            f"Risk: {t_result['context_overflow_risk']}"
        )

        # Guardrail scan
        g_result: Dict[str, Any] = guardrail_analyzer.analyze_asset(asset)
        guardrail_results.append(g_result)
        _log(
            f"   [Guard] {g_result['asset_id']}: "
            f"Score: {g_result['final_risk_score']} | "
            f"Level: {g_result['risk_level'].upper()} | "
            f"Triggers: {g_result['triggered_categories'] or 'none'}"
        )

    # Concurrency scan (ecosystem-wide)
    c_result: Dict[str, Any] = concurrency_analyzer.analyze_ecosystem(ecosystem)
    _log(
        f"   [Concur] Health: {c_result['system_health']} | "
        f"Race Conditions: {len(c_result['race_conditions'])} | "
        f"Logic Flaws: {len(c_result['logic_flaws'])}"
    )

    # Detail race conditions
    for rc in c_result["race_conditions"]:
        _log(f"      ⚠️  [{rc['asset_id']}] {rc['flaw']}: {rc['description']}")

    for flaw in c_result["logic_flaws"]:
        _log(f"      ⚠️  {flaw}")

    _log("")

    # ── Phase 3: Metamorphic Bridge Compilation ──
    _log("🌉 [Phase 3] Engaging Metamorphic Bridge...")

    bridge: MetamorphicBridge = MetamorphicBridge(
        ecosystem=ecosystem,
        token_diagnostics=token_results,
        guardrail_diagnostics=guardrail_results,
        concurrency_diagnostics=c_result,
        output_dir=OUTPUT_DIR
    )

    output_path: str = bridge.compile_and_export()

    # ── Phase 4: Final Summary ──
    _log("\n" + "═" * 56)
    _log("🏁 Pipeline execution complete.")
    _log(f"📦 Frontend payload: {output_path}")
    _log("📐 Schema reference: system_map.py → API_CONTRACT_SCHEMA")
    _log("═" * 56)

    return output_path


# ════════════════════════════════════════════════════════════════
# ═══ ENTRY POINT ═══════════════════════════════════════════════
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        execute_pipeline()
    except Exception as fatal_error:
        _log(f"\n💀 FATAL PIPELINE ERROR: {fatal_error}")
        sys.exit(1)
