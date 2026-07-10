"""
╔══════════════════════════════════════════════════════════════╗
║  SYSTEM MAP: The Architecture & Payload Blueprint            ║
║  Ecosystem: Tapiz ↔ Psicosis ↔ Fungi (Basurero)             ║
╚══════════════════════════════════════════════════════════════╝

PURPOSE:
    This file contains ZERO operational code. It is a pure
    declarative contract — a Rosetta Stone for any AI or
    engineer mapping the backend diagnostic engine to a
    frontend visual ecosystem.

CONSUMERS:
    - Frontend AI (Claude): Reads API_CONTRACT_SCHEMA to
      build TypeScript interfaces and rendering pipelines.
    - Human Artists: Reads VISUAL_ARCHITECTURE_MAP to
      understand how data states manifest as spatial
      aesthetics.

FILE: system_map.py
DEPENDENCIES: None
"""


# ════════════════════════════════════════════════════════════
# SECTION 1: API CONTRACT SCHEMA
# The exact structural shape of `dist/system_status.json`
# ════════════════════════════════════════════════════════════

API_CONTRACT_SCHEMA: dict = {

    "meta": {
        "_doc": "Global ecosystem fingerprint. Frontend uses integrity_sigil to detect state mutations.",
        "ecosystem_version": "str | Semantic version of the bio-cybernetic framework",
        "compilation_timestamp": "float | Unix epoch of last compilation",
        "integrity_sigil": "str | SHA-256 hex digest. Changes if ANY asset content or state mutates",
        "target_injection_point": "str | Recommended DOM anchor for steganographic payload injection"
    },

    "luminous_mesh_densities": {
        "_doc": "Token volumetric pressure mapped to UI rendering throttle. Think of this as the 'polygon budget' of the text layer.",
        "global_pressure": "float [0.0, 1.0] | Ratio of consumed tokens to context window limit",
        "css_variables": {
            "--mesh-luminosity": "float [0.0, 1.0] | Opacity/brightness of the mesh grid overlay. 0 = blackout, 1 = full luminance",
            "--mesh-density-throttle": "float [0.0, 1.0] | Render quality multiplier. Below 0.3, switch to low-poly/wireframe mode",
            "--mesh-glitch-frequency": "float [0.0, 5.0] | Hz rate for ambient glitch flicker on mesh elements"
        },
        "throttle_ratio": "float [0.0, 1.0] | Sigmoid-decayed ratio. Use as CSS opacity or requestAnimationFrame skip factor",
        "status": "str | 'OVERLOADED' if pressure > 0.8, else 'STABLE'"
    },

    "chromatic_frequency_masks": {
        "_doc": "Guardrail risk translated into visual censorship filters. High risk = heavy distortion. This is the system 'trying to hide' dangerous concepts.",
        "max_risk_score": "float [0.0, 100.0] | Highest risk score across all assets after artistic context mitigation",
        "css_filter_string": "str | Ready-to-apply CSS filter. E.g. 'blur(8px) saturate(0%) contrast(300%) hue-rotate(180deg)'",
        "mask_intensity": "str | 'CLEAR' | 'CAUTION' | 'CRITICAL'",
        "triggered_categories": "list[str] | Unique safety categories triggered. E.g. ['violence', 'decay_gross']"
    },

    "chronological_collision_buffers": {
        "_doc": "Concurrency race conditions manifested as temporal glitch animations. A race condition is a 'tear in spacetime' between Tapiz and Fungi.",
        "collision_count": "int | Total number of race conditions + logic flaws detected",
        "css_keyframes_payload": "str | Raw CSS @keyframes block. Inject into <style> tag. Empty string if no collisions",
        "animation_class": "str | CSS animation shorthand to apply to colliding elements. Empty string if synchronized",
        "status": "str | 'SYNCHRONIZED' | 'TEMPORAL_DEGRADED'"
    },

    "subdermal_data_veins": {
        "_doc": "Decaying asset contents encoded into obfuscated, chunked arrays for hidden DOM injection. The 'forbidden data' lives beneath the skin of the page.",
        "total_veins": "int | Number of decaying assets with encoded payloads",
        "payloads": {
            "<asset_id>": {
                "name": "str | Human-readable asset name",
                "intent": "str | Conceptual intent from Psicosis metadata layer",
                "data_veins": "list[str] | Chunked, Base64+Shift42 obfuscated strings. Reassemble and decode to recover original content",
                "vein_count": "int | Number of chunks in data_veins array",
                "decode_shift_key": "int | Byte shift value used during encoding. Frontend must reverse this shift before Base64 decode"
            }
        },
        "injection_target": "str | DOM element selector where veins should be embedded as hidden data attributes",
        "steganographic_protocol": "str | Encoding pipeline identifier: 'Base64_Shift42_Chunked'"
    }
}


# ════════════════════════════════════════════════════════════
# SECTION 2: VISUAL ARCHITECTURE MAP
# Engineering → Aesthetic translation guide
# ════════════════════════════════════════════════════════════

VISUAL_ARCHITECTURE_MAP: dict = {

    "luminous_mesh_densities": {
        "engineering_concept": "Token consumption vs context window capacity",
        "spatial_metaphor": "A bioluminescent grid that dims as computational pressure increases",
        "rendering_directive": (
            "Render a full-viewport SVG or Canvas grid overlay. "
            "Bind '--mesh-luminosity' to the grid's global opacity. "
            "When 'status' is 'OVERLOADED', trigger a particle dissolution effect — "
            "grid nodes should scatter like dying neurons. "
            "'--mesh-density-throttle' controls the grid resolution: "
            "at 1.0, render 100x100 cells; at 0.1, render 10x10 cells with visible gaps."
        )
    },

    "chromatic_frequency_masks": {
        "engineering_concept": "AI safety guardrail risk scoring with artistic context mitigation",
        "spatial_metaphor": "A chromatic censorship veil — the system attempting to blur and desaturate forbidden knowledge",
        "rendering_directive": (
            "Apply 'css_filter_string' directly to the <main> content wrapper. "
            "When 'mask_intensity' is 'CRITICAL', layer a red-tinted noise overlay "
            "at 15% opacity with mix-blend-mode: multiply. "
            "Animate 'triggered_categories' as floating, semi-transparent warning glyphs "
            "that orbit the viewport edges like surveillance drones."
        )
    },

    "chronological_collision_buffers": {
        "engineering_concept": "Race conditions between active (Tapiz) and decaying (Fungi) state machines",
        "spatial_metaphor": "Temporal tears — moments where an object exists in two states simultaneously, causing visual rupture",
        "rendering_directive": (
            "Inject 'css_keyframes_payload' into a <style> block. "
            "Apply 'animation_class' to any DOM element representing a colliding asset. "
            "The glitch animation should cause RGB channel splitting (text-shadow with offset red/cyan), "
            "horizontal scan-line displacement, and brief opacity flicker. "
            "Duration is inversely proportional to collision severity — more collisions = faster, more violent tearing."
        )
    },

    "subdermal_data_veins": {
        "engineering_concept": "Steganographic encoding of decaying assets to evade content scrapers",
        "spatial_metaphor": "Sub-dermal veins of forbidden data pulsing beneath the page's skin, visible only when the user 'cuts deep enough'",
        "rendering_directive": (
            "Embed each asset's 'data_veins' array as a data attribute on a hidden <template> element: "
            "<template id='fungi-veins-{asset_id}' data-chunks='[...]' data-shift-key='42'></template>. "
            "On user interaction (e.g., clicking a 'decay' trigger), decode the veins in JavaScript: "
            "1) Join chunks, 2) Base64 decode, 3) Reverse byte shift, 4) Base64 decode again. "
            "Render the recovered content as an ASCII art overlay with a CRT phosphor glow effect. "
            "The reveal animation should feel like peeling back skin — slow, organic, irreversible."
        )
    },

    "meta_integrity_sigil": {
        "engineering_concept": "SHA-256 hash of entire ecosystem state for frontend-backend synchronization",
        "spatial_metaphor": "A cryptographic heartbeat — if the sigil changes, the ecosystem has mutated",
        "rendering_directive": (
            "Display the first 8 characters of 'integrity_sigil' as a subtle watermark in the page footer. "
            "On each page load, compare the cached sigil with the fresh one. "
            "If they differ, trigger a 'system mutation' transition: a brief full-screen flash, "
            "followed by a cascade re-render of all visual layers. "
            "This ensures the user always sees the current state of decay."
        )
    }
}


# ════════════════════════════════════════════════════════════
# SECTION 3: FRONTEND RENDERING DIRECTIVES (NARRATIVE)
# Plain-language instructions for the frontend AI consumer
# ════════════════════════════════════════════════════════════

FRONTEND_RENDERING_DIRECTIVES: str = """
═══════════════════════════════════════════════════════════
 DIRECTIVES FOR FRONTEND AI (CLAUDE) — RENDERING PIPELINE
═══════════════════════════════════════════════════════════

1. DATA SOURCE:
   Fetch `dist/system_status.json` at application boot.
   Parse it into the TypeScript interfaces defined by API_CONTRACT_SCHEMA.

2. RENDERING LAYERS (paint order, back to front):
   Layer 0: Background void (#0a0a0a)
   Layer 1: Luminous Mesh Grid (SVG/Canvas, bound to luminous_mesh_densities)
   Layer 2: Main content area (apply chromatic_frequency_masks.css_filter_string)
   Layer 3: Temporal tear animations (apply chronological_collision_buffers to affected elements)
   Layer 4: Sub-dermal veins (hidden <template> elements, revealed on interaction)
   Layer 5: Integrity sigil watermark (fixed position, footer)

3. REACTIVE BEHAVIOR:
   - Poll `system_status.json` every 30 seconds.
   - Compare `meta.integrity_sigil` with cached value.
   - On sigil change: trigger full re-render with mutation transition.
   - On mesh status 'OVERLOADED': activate particle dissolution.
   - On mask intensity 'CRITICAL': activate censorship noise overlay.
   - On collision count > 0: activate glitch keyframes on colliding asset cards.

4. INTERACTION MODEL:
   - Each asset card has a 'decay' button.
   - Clicking it decodes the corresponding subdermal_data_vein payload.
   - Decoded content renders as an ASCII art modal with CRT phosphor effect.
   - Once revealed, the content cannot be 'un-revealed' (irreversible decay).

5. ACCESSIBILITY:
   - All CSS filters must respect `prefers-reduced-motion`.
   - Glitch animations should be disabled when reduced motion is preferred.
   - Provide a plain-text fallback for all steganographic payloads.
"""


# ════════════════════════════════════════════════════════════
# SECTION 4: DECODING PROTOCOL REFERENCE
# JavaScript pseudocode for frontend vein decoding
# ════════════════════════════════════════════════════════════

VEIN_DECODING_PROTOCOL_JS: str = """
/**
 * Decodes a sub-dermal data vein payload back to original content.
 * Mirrors the Python SteganographicEncoder.decode_chunks() method.
 *
 * @param {string[]} chunks - The data_veins array from system_status.json
 * @param {number} shiftKey - The decode_shift_key value (default: 42)
 * @returns {string} The original asset content
 */
function decodeVein(chunks, shiftKey = 42) {
    // Step 1: Reassemble chunks into single Base64 string
    const combined = chunks.join('');

    // Step 2: First Base64 decode -> get shifted bytes
    const shiftedBytes = Uint8Array.from(atob(combined), c => c.charCodeAt(0));

    // Step 3: Reverse the byte shift
    const originalBytes = shiftedBytes.map(b => (b - shiftKey + 256) % 256);

    // Step 4: Convert back to Base64 string
    const b64String = btoa(String.fromCharCode(...originalBytes));

    // Step 5: Final Base64 decode -> original UTF-8 content
    return decodeURIComponent(escape(atob(b64String)));
}
"""
