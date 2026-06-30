# HANDOFF 2026-06-30 - Agente 3 Resolume base y docs duales

## Resumen

Este airdrop armoniza README.md y AGENTS.md, oficializa Modo RD vs Modo Studio, documenta el ruteo Gmail por asunto y agrega la base tecnica para automatizacion Resolume/Chataigne desde jobs de EVENTOS.

## Archivos incluidos

- README.md
- AGENTS.md
- context/LAST_HANDOFF.md
- tools/resolume_chataigne_automator/SPEC.md
- src/flujo/resolume/__init__.py
- src/flujo/resolume/automator.py
- src/flujo/cli.py
- projects/agente1_flyers_web/README.md
- projects/agente1_flyers_web/PROMPT_AGENTE_1.md
- projects/agente2_resolume_chataigne/README.md
- projects/agente2_resolume_chataigne/PROMPT_AGENTE_2.md

## Comando nuevo

```bash
py -m flujo resolume automatizar jobs/<job_id>
```

Opciones:

```bash
py -m flujo resolume automatizar jobs/<job_id> --fps 25
py -m flujo resolume automatizar jobs/<job_id> --host 127.0.0.1 --port 7000
py -m flujo resolume automatizar jobs/<job_id> --output salida.xml
```

## Verificacion ejecutada por Agente 3

En sandbox Linux se ejecuto el equivalente interno con el launcher disponible:

```bash
python -m compileall src/flujo/resolume src/flujo/cli.py
PYTHONPATH=src python -m flujo resolume automatizar jobs/_resolume_demo
```

Ademas se valido el XML generado con `xml.etree.ElementTree`.

Resultado: OK.

## Aplicacion recomendada en Windows/Git Bash

```bash
py scripts/validate_airdrop.py
py scripts/run_airdrop_checks.py "agente3 resolume base y docs duales"
```

Si ya se aplico y fallo solo despues de apply:

```bash
py scripts/run_airdrop_checks.py --resume "agente3 resolume base y docs duales"
```

## Siguientes agentes

Agente 1 debe trabajar desde:

```txt
projects/agente1_flyers_web/PROMPT_AGENTE_1.md
```

Agente 2 debe trabajar desde:

```txt
projects/agente2_resolume_chataigne/PROMPT_AGENTE_2.md
```
