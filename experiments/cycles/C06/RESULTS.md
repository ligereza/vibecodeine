# C06 — resultado del puente de exportación

**Estado:** PASS — 2026-08-25

## Gate

```text
PYTHONPATH=. .venv/bin/python experiments/cycles/C06/verify_cycle.py
EXIT 0
tests_exit_code=0
claim_status=supported
edge_count=1
adversarial_cases=3
```

C06 consumió únicamente
`experiments/cycles/C05/real_export_witness.json` y materializó una arista:

```text
authoring:blend:ARICA/RAYU.blend
  --EXPORTS_TO--> artifact:glb:rayu_resources.glb
```

La arista conserva los `evidence_refs` del witness y su límite de afirmación:
exportación apoyada, no entrega final, publicación, intención artística ni
autoría.

## Adversarial

Los tres casos negativos pasaron: refs ausentes, check contradictorio y
estado `unknown` produjeron `claim=unknown` y cero aristas. El puente no lee
filesystem, no ejecuta scripts, no abre Blender y no usa verdad oculta.

Conclusión: el witness puede entrar al grafo como una relación tipada sin
convertirse en una label de proyecto ni en una decisión de router.
