<p align="center">
  <img src="arte-ascii-readme.svg" alt="VIBE-CODEINE animated ASCII vessel" width="936">
</p>

# flujo -- Dimensiones del Orden

MAK: an archive, production and automation system for artistic and cultural
practice. Python 3.11, Typer CLI.

No measured figure is written in this file. A figure in prose rots and nobody
updates it, so the commands below are the measurement.

```bash
python -m pytest tests/ -q      # suite size and state
python -m flujo --help          # CLI commands
ls tools/*.py | wc -l           # tools
```

## If you are an agent, read this order and nothing else

```
agents.md -> docs/MAK_CURRENT_STATE.md -> context/LAST_HANDOFF.md
```

That is the order `tools/agent_bootstrap.py` emits, and it is the only one.
Other documents in this repo have declared themselves canonical at some point;
**`docs/AUTORIDAD.md` says which is which and why.** Read it before trusting a
header.

## If you are a person

```bash
make install        # dependencies
make test           # suite
make audit          # read-only audit: web, references, local databases
python -m flujo --help
```

## Minimal map

| Path | What it is |
|---|---|
| `src/flujo/` | runtime and CLI. Implementation authority |
| `src/flujo/knowledge/` | archive, portfolio, evidence, `mak-*-v1` schemas |
| `cultura/mak_*/` | in-house subsystems, including the human Hub (`mak_plataforma/hub.py`) |
| `tools/` | tools, each registered in `CAPACIDADES.md` with its consumer |
| `tests/` | suites by domain |
| `docs/` | doctrine and dated evidence. Start at `docs/AUTORIDAD.md` |
| `context/` | operational continuity. `LAST_HANDOFF.md` is the state authority |
| `data/`, `knowledge/` | databases and knowledge declared by path |
| `experiments/pilots/` | pilot runs. Live fixtures: 9 suites read them |
| `out/` | generated products. Not source |
| `.archive/` | retirement. `tests/test_higiene_docs.py` excludes it on purpose |

## Writing rules the repo enforces

Four tests hold these up, not goodwill:

- `tests/test_higiene_docs.py` -- a document may not claim a suite total, an
  invariant range or a version that contradicts what is measured.
- `tests/test_higiene_repo.py` -- every tool in `tools/` is in the registry,
  compiles, and does not crash when asked what it does.
- `tests/test_idioma_ratchet.py` -- no new Python file starts carrying Spanish
  comments or docstrings. Measured by `tools/idioma.py`, pinned in
  `tests/fixtures/idioma_baseline.txt`. Shrinking the set is always welcome.
- `tests/test_privacidad_repo.py` -- no credentials, no sensitive data.

Two more are applied by hand and stated in `docs/AUTORIDAD.md`: every file
reference carries its path from the repo root, and every state says how it was
checked.

## Language

Per `agents.md`: machine-facing code, identifiers, filenames, configuration
keys, tests, technical logs and operational metadata are **English ASCII**.
Human-facing RD and Portfolio material uses **correct Spanish with diacritics**.
This file is operational metadata, so it is English.

## License

See `LICENSE`.
