# Phase 308 — language consumer and projection gate

Date: 2026-08-15 America/Santiago  
Owner: LUNA principal  
Status: `PROJECTION_PARITY_VERIFIED_DATA_OWNER_PROTECTED`

## Scope

The physical search began at `/home/mak/*` and narrowed to the language
department and its FLUJO canonical owner. `/home/mak/WIN` was not modified or
used as a runtime path. The scan covered Spanish and English identifiers,
Python entrypoints, shell launchers, dictionaries, lexicon output, cron
declarations and active department references.

## Owner and physical disposition

| Surface | Finding | Decision |
|---|---|---|
| `/home/mak/flujo/cultura/mak_lenguaje/*.py` | canonical implementation; four Python modules parse | retain as semantic owner |
| `/home/mak/lenguaje/*.py` | four exact byte-identical runtime projections | retain while root data/runtime paths are consumed |
| `/home/mak/lenguaje/diccionarios` | Spanish dictionary data used by `cargar_diccionario()` | protect as live data; do not move or regenerate |
| `/home/mak/lenguaje/lexico` | generated lexicon and cron log consumed by the language workflow | protect as output/state; do not merge with source |
| `/home/mak/lenguaje/cron_lexicon.sh` | dormant scheduler entrypoint, syntax-valid | retain as paused operational evidence |
| `/home/mak/lenguaje/hook_barrido.py` | appends signal annotations to research/codex Markdown | classify as mutator; no live run |
| `/home/mak/lenguaje/corregir.py` | calls LLM/provider path and writes `.corregido.md` | provider/output gate; no live run |
| `/home/mak/lenguaje/instalar_diccionarios.sh` | downloads external dictionary and writes local data | external/network/install gate; no run |

The hard-coded `/home/mak/lenguaje` data contract is intentional evidence that
the root department is not a disposable duplicate. The safe merge boundary is
therefore: canonical code in `cultura/mak_lenguaje`, protected root
projection/data in `lenguaje`, and no whole-tree synchronization.

## Consumers and dependencies

Static references were found in:

- `cultura/mak_plataforma/roles.py` and the paused `crontab.mak` template;
- `cultura/mak_vigia/vigia.py`, which documents the language pattern;
- the language scripts themselves and root department launch paths.

The pure measurement/lexicon path is standard-library-only. `corregir.py`
depends on the Research LLM/provider layer; dictionary installation depends on
the downloader and an external GitHub source. Neither dependency was promoted
or contacted.

## Foreground validation

Commands and observed results:

```text
AST parse of canonical and root Python modules: exit 0; 8/8 AST_OK
cmp/hash of four source/projection pairs: exit 0 for each; byte-identical
bash -n cron_lexicon.sh: exit 0
bash -n instalar_diccionarios.sh: exit 0
pure medir_senal parity: PASS; canonical/root results equal
temporary construir_lexicon fixture: PASS; 1 input, 2 unique terms,
  outputs confined to /tmp/mak-lenguaje-gate.KC4LsA/out
medir.py temporary-file CLI: exit 0; valid JSON with Spanish characters
active reference scan: only language family, roles, vigia and historical
  paused/rollback references; no competing active owner found
```

No file under `/home/mak` changed in this phase. No cron entry, service,
provider, downloader, dictionary, research/codex Markdown or lexicon output
was touched. The temporary fixture is outside MAK and contains no production
data.

## Risk and rollback

Moving the root code or data would break the hard-coded dictionary/lexicon
contract and the paused launchers. The rollback is therefore the unchanged
state: keep the exact projection and root data at their current paths. Any
future refactor must first introduce a configurable data root, validate all
Spanish/English launchers, and prove the hook/output rollback.

## Decision and next action

`lenguaje` is `CONSUMER_BACKED_PROTECTED_PROJECTION`; no merge or quarantine is
justified. Continue with the next low-mutation review surface from the
architecture queue: `/home/mak/trazos`, beginning at `/home/mak/*`, mapping
active consumers and provenance before any move. Keep language cron, provider
correction, dictionary download, live mutators and services inactive.
