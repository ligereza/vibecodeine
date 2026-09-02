# Phase 252 — excluded test risk inventory

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Subagents: none

## Purpose

Bound the remaining test surface without launching providers, services,
workers, desktop applications, network calls or external integrations. This
is a static inventory, not a claim that every excluded test is unsafe.

## Method

Starting from `/home/mak/*`, the scope was narrowed to the canonical test tree
`/home/mak/flujo/tests`. A file was excluded from the already-green safe suite
when its source mentioned one or more of these surfaces:

- process/service: subprocess, systemd, service, cron or worker;
- network/provider: requests, urllib, HTTP, network, boto3, Ollama, provider,
  SMTP or IMAP;
- media/GPU: FFmpeg, Blender, OpenCV, NVIDIA, CUDA, GPU, Resolume or pywebview;
- external/integration: Git, GitHub, Instagram, Canva, WiFi, OSC, ADB or XIO.

Two explicitly high-risk files were also excluded: `test_airdrop_checkpoint.py`
and `test_vj_git_performance.py`. Matching is intentionally conservative and
can produce false positives from docstrings or fixtures.

## Result

| Measure | Result |
|---|---:|
| Excluded test files | 177 |
| Test-function declarations in excluded files | 2,164 |
| Static parse failures | 0 |
| Files with process/service marker | 83 |
| Files with network/provider marker | 105 |
| Files with media/GPU marker | 21 |
| Files with external/integration marker | 86 |
| Explicit-risk files | 2 |

The category counts overlap. The excluded source parses successfully, so the
remaining work is risk-aware execution triage, not syntax repair.

## Decision

Do not run the 177-file set as one batch. The next safe promotion should be a
small disjoint group proven to use temporary fixtures and no external side
effects. Tests that invoke provider, network, process, desktop, Git, ADB,
XIO, or durable write paths stay gated until their exact input/output and
rollback are named.

The incomplete `/home/mak/plataforma/panel_directivo.py` remains a separate
historical artifact: it has no verified active consumer and its AST failure is
not a reason to reconstruct it.

## Validation commands and codes

```text
PYTHONDONTWRITEBYTECODE=1 /home/mak/research/.venv/bin/python <static inventory>
  exit 0; EXCLUDED_FILES=177; PARSE_FAILURES=0
```

No test, service, provider, database, network route or external integration
was invoked in this phase.

## Next concrete action

Build a per-file promotion shortlist from the 177 exclusions using executable
AST calls/imports rather than raw keyword matches; then run only one bounded
fixture-only group. Preserve all excluded files and do not broaden to live
mutators or provider-backed tests.
