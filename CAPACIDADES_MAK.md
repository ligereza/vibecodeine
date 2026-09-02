# MAK branch capabilities

This branch owns the Linux MAK box surface and its department projections.

Physical layout (2026-09-02): `/home/mak` is this checkout. The portable motor
is the sibling checkout `/home/mak/flujo` (branch `FLUJO`); MAK consumes it
from `/home/mak/flujo/src` and carries no copy of `src/flujo`. `main` and
`historia` are historical and are never runtime.

Lanes and their real commands:

- `mak`: `PYTHONPATH=/home/mak:/home/mak/flujo/src python -m pytest -o addopts=''
  -q -m mak` with `requirements-mak.txt`.
- `integration`: the composition of both checkouts, declared by
  `requirements-integration.txt`, run with
  `PYTHONPATH=/home/mak:/home/mak/flujo:/home/mak/flujo/src python -m pytest
  -o addopts='' -q -m integration`.
- Structural gate: `python tools/release_gate.py --check`. Runtime evidence:
  `python tools/runtime_preflight.py --check --strict`.

## Owned surfaces

- `cultura/mak_plataforma/hub.py`: human-facing MAK Hub on port `8900`.
- `plataforma/hub.py`: compatibility entrypoint for the MAK Hub.
- `cultura/mak_*/`: department, research and machine-bound projections.
- `tools/` and `data/`: box-side operators and read-only ledgers required by
  the `mak` lane.

## Runtime surfaces and boundaries (checked 2026-09-02)

| Surface | Canonical source / unit | Port or invocation | Boundary |
|---|---|---|---|
| MAK Hub | `cultura/mak_plataforma/hub.py` / `/home/mak/.config/systemd/user/mak-hub.service` | `127.0.0.1:8900` | The MAK user-facing hub; portfolio, departments and Copilot routes |
| MAK Copilot | `cultura/mak_plataforma/copilot.py`; imported by `hub.py` | `/api/portfolio/copilot/*` through port `8900` | Library for candidate ranking, atlas and suggestions; no independent daemon |
| Research | `cultura/mak_research/interfaz.py` / `/home/mak/.config/systemd/user/mak-research.service` | `127.0.0.1:8890` | Internal Research service consumed by the Hub |
| Codex bridge | `cultura/mak_codex/interfaz_codex.py` / `/home/mak/.config/systemd/user/mak-codex.service` | `127.0.0.1:8891` | Internal Codex bridge; separate from the FLUJO App |
| Ollama local inference | `/etc/systemd/system/ollama.service` + `cultura/mak_research/research_lib.py` | `127.0.0.1:11434` (`gemma3:4b`, `deepseek-coder:6.7b`, `nomic-embed-text:latest`) | Local completion/embedding provider consumed by Research, MAK Codex, Conductor, RD mining, batches and local chat; `nomic-embed-text` has no confirmed in-repo caller |
| SearXNG dependency | `searxng/settings.yml` | `127.0.0.1:8888` | Search backend, not a MAK Hub |
| Optional ntfy queue | `/home/mak/.config/systemd/user/mak-research-queue.service` | No port; disabled until a topic exists | Notification transport only; not Research itself |

The FLUJO surfaces are not owned by this MAK branch: `python -m flujo app`
uses `flujo/src/flujo/web/hub.py` in the FLUJO checkout (contract port `8765`;
auto-detection is opt-in, so an explicit `--port` binds or fails, and the
port is occupied), while `python -m flujo serve` uses the lightweight
`flujo/src/flujo/serve/server.py` (default `8777`). Neither is the MAK Hub on `8900`.
Live state belongs in `docs/MAK_CURRENT_STATE.md`; this file records ownership
and transfer boundaries.

## Validation

```text
python -m pytest -m mak -q
python cultura/mak_plataforma/hub.py --help
```

## Transferable consumers

The MAK Hub and the FLUJO Hub remain separate implementations. They share
`project_api.py`, `system_status.py`, `departments.py` and the
`data/mak_knowledge.db` schema through typed JSON payloads and explicit
`source_ref` values. A future transfer changes an adapter, not the other Hub.
