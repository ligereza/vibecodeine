# MAK Codex Fallback Analysis

## Executive Summary

The CoderLLM fallback mechanism (cultura/mak_codex/codex_lib.py, lines 110-129) iterates through a chain of coder providers but surfaces only the LAST error when all fail. This obscures which providers were attempted, what specific errors each had, and whether timeouts are transient vs. systemic.

## Current Fallback Implementation

**File:** cultura/mak_codex/codex_lib.py
**Loop:** lines 110-129 in CoderLLM.call()

```python
def call(self, system, user, max_tok=1200):
    cadena = list(self.chain)
    # Network reordering logic (lines 114-116)
    if not red_ok():
        frente = [c for c in cadena if c[0] in ("win", "ollama")]
        cadena = frente + [c for c in cadena if c not in frente]
    
    fns = {"nim": self._nim, "win": self._win, "ollama": self._ollama}
    last = None
    for prov, model in cadena:
        try:
            text = fns[prov](system, user, max_tok, model)
            if text and text.strip():
                self.stats[model] = self.stats.get(model, 0) + 1
                return text, model
            last = model + " devolvio vacio"
        except Exception as e:  # noqa: BLE001 - fallback multi-coder
            last = model + ": " + str(e)[:140]
            self.errors.append(last)
    raise RuntimeError("Todos los coders fallaron. Ultimo: %s" % last)
```

**Key observations:**

1. **Chain Definition** (lines 39-44):
   ```
   ("nim", "deepseek-ai/deepseek-v4-pro")      # NIM hosted, timeout=120s
   ("nim", "deepseek-ai/deepseek-v4-flash")    # NIM hosted, timeout=120s
   ("win", deepseek-v2:16b-lite-instruct...)   # Local RTX 4070, timeout=300s
   ("ollama", "deepseek-coder:6.7b")           # Local Ollama, timeout=300s
   ```

2. **Network Reordering** (lines 114-116):
   - If network is down (`not red_ok()`), local providers (win/ollama) move to front
   - Respects offline-first fallback, but no per-provider health tracking

3. **Error Capture** (line 127-128):
   - Broad `except Exception` catches all errors uniformly
   - Truncates error message to 140 chars (line 127)
   - Only LAST error is re-raised; accumulated errors in `self.errors` are never surfaced
   - Stats track successes, not failures

4. **Timeout Behavior**:
   - NIM calls have `timeout=120` (line 91)
   - Ollama/Win calls have `timeout=300` (line 100)
   - Timeout exceptions are indistinguishable from API errors in the catch block
   - Worker-level timeout is 900s (worker_codex.py line 41); misalignment with provider timeouts

5. **Empty Response Handling** (lines 122-125):
   - If provider returns empty string, loop continues
   - Marked as `model + " devolvio vacio"` but continues fallback
   - Non-fatal; correct behavior, but not logged per-provider

## Failure Modes

**Observed in audit (today):**
```
RuntimeError: Todos los coders fallaron. Ultimo: deepseek-coder:6.7b: timed out
RuntimeError: Todos los coders fallaron. Ultimo: timeout 900s
```

**Issues:**
- Only the last error visible; if NIM timed out, we don't know that
- "timed out" is truncated; full context lost (which provider, how long it waited)
- No way to distinguish:
  - (a) one provider flaky, others working
  - (b) all providers consistently failing
  - (c) system under load (universal timeout across all)
  - (d) specific provider down (only one type fails)
- No backoff or selective retry of transient errors

## Proposed Improvements

### 1. **Aggregate Error Listing (High Priority)**
Display all providers attempted and their specific failure reasons, not just the last:
```
Todos los coders fallaron:
  - nim/deepseek-v4-pro: timeout (waited 120s)
  - nim/deepseek-v4-flash: HTTP 429 (rate limited)
  - win/deepseek-v2:16b-lite: connection refused
  - ollama/deepseek-coder:6.7b: timeout (waited 300s)
```
**Benefit:** Operators can diagnose if one provider is broken vs. systemic load.

### 2. **Per-Provider Timeout Tracking (Medium Priority)**
Mark which errors are timeouts so retry/backoff logic can treat them specially:
```python
errors = [
    {"provider": "nim", "model": "deepseek-v4-pro", "reason": "timeout", "waited": 120},
    {"provider": "nim", "model": "deepseek-v4-flash", "reason": "HTTP 429", "waited": 120},
    {"provider": "ollama", "model": "deepseek-coder:6.7b", "reason": "timeout", "waited": 300},
]
```
**Benefit:** Enables smart retry logic: timeout = transient, HTTP 429 = backoff, connection refused = skip provider.

### 3. **Provider Health Stats (Medium Priority)**
Extend `self.stats` to track not just successes but failures per provider type (nim/win/ollama):
```python
self.stats = {
    "nim": {"successes": 5, "timeouts": 2, "api_errors": 1},
    "win": {"successes": 8, "timeouts": 0, "errors": 0},
    "ollama": {"successes": 3, "timeouts": 1, "errors": 0},
}
```
**Benefit:** Subsequent calls can reorder chain: try healthy providers first, skip known-flaky ones.

### 4. **Backoff for Transient Errors (Low Priority, Optional)**
For timeouts and temporary 5xx errors, retry with exponential backoff within the CoderLLM chain:
```python
if error_type == "timeout" and attempt < max_retries:
    time.sleep(2 ** attempt)
    retry this provider once
```
**Benefit:** Survive brief network hiccups; reduces false negatives on load spikes.

### 5. **Clearer Aggregate Error Message (High Priority)**
Stop truncating error strings and aggregate all attempts in the RuntimeError:
- Current: `"Todos los coders fallaron. Ultimo: deepseek-coder:6.7b: timed out"`
- Proposed: Include all providers and their timeouts in the message, or log separately to a structured field
- **Benefit:** No information loss; operators can act on complete context.

## Optional Clean Extraction: fallback_util.py

A pure helper module (no network/ollama deps) can be extracted:

### `fallback_util.parse_provider_error(exception, provider_type, model, timeout_sec)`
Classify error into (timeout, api_error, connection_error, other) and format consistently.
**Dependencies:** None (pure string/exception inspection).

### `fallback_util.aggregate_failures(attempts_list)`
Takes list of (provider, model, error_type, reason) and formats a readable aggregated message.
**Dependencies:** None.

### `fallback_util.score_provider_health(stats_dict)`
Rank providers by success ratio; returns reordered chain suggestion.
**Dependencies:** None.

**Tests:** Mock provider attempts, verify error classification and aggregation.

## Implementation Status

This document serves as a specification for improvements. The live CoderLLM fallback loop (lines 110-129) should be enhanced with:
1. Structured error collection (not just `last`)
2. Per-provider timeout/error-type tracking
3. Aggregate error surfacing (all providers, all reasons)

A clean extraction of error parsing and aggregation logic into `fallback_util.py` is feasible and testable without touching network code.


## ADVERTENCIA -- verificado en runtime (ts: 2026-07-20 21:00 UTC)

CoderLLM.call() en codex_lib.py revirtio silenciosamente a la implementacion
naive de este documento (linea 110-129 original) en un hotfix no documentado.
fallback_util.parse_provider_error / aggregate_failures dejaron de invocarse
en produccion. La mejora de este documento NO esta activa. Re-verificar antes
de asumir que el fallback esta resuelto.
