# Phase 52 — lenguaje consumer gate

## Result

`/home/mak/lenguaje` is not an orphan candidate. Its real consumer is the
MAK operational declaration `/home/mak/flujo/cultura/mak_plataforma/crontab.mak`:
the lexicon rebuild runs daily and `hook_barrido.py` is scheduled every ten
minutes. Existing `/home/mak/plataforma/logs/hook.log` contains successful
historical runs, so this is an active MAK utility, not a WIN migration slice.

The source boundary is complete and already mirrored in
`/home/mak/flujo/cultura/mak_lenguaje/`; all four Python modules have equal
normalized content between the physical runtime and the FLUJO department
source. No copy or source edit was needed.

## Foreground validation

```text
python3 AST parse of corregir.py, hook_barrido.py, lenguaje_lib.py, medir.py
exit=0; all four PASS in both MAK and FLUJO source roots

normalized parity check for all four modules
result: True for all four

PYTHONPATH=/home/mak/lenguaje python3 -c 'medir_archivo(/home/mak/flujo/README.md)'
exit=0; read-only result was a dict with language metrics

bash -n cron_lexicon.sh instalar_diccionarios.sh
exit=0; shell syntax valid; scripts were not executed

crontab consumer declaration check
result: both /home/mak/lenguaje/cron_lexicon.sh and hook_barrido.py present

pytest focused attempt
not run: pytest command absent on MAK; no package installed
```

## Decision

`lenguaje` is classified `LIVE_LOCAL_CONSUMER_VERIFIED`. It is not to be
copied into FLUJO or merged with the hub. Its dictionary installer and cron
writers remain operational boundaries; no dictionary download, cron mutation
or hook execution occurred in this phase.

Next bounded candidate: `/home/mak/vigia`, using static/AST/fixture checks
only. Keep `xio_puente` last and ADB deferred.
