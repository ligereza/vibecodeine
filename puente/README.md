# puente/ -- corpus TEORICO (Omega). NO es codigo operativo.

Esta carpeta es la capa conceptual heredada del corpus Omega de
`Desktop/idea_generativa`. Es TEORIA: ensayo, diagnostico, protocolo y registro
de semillas. **No se ejecuta, no se importa, no es parte del pipeline de flujo.**
Un agente que busque codigo que corre NO lo encuentra aca -- lo encuentra en
`src/flujo/`, `projects/` y `tools/`.

## Que hay aca (todo es texto teorico)

- `SEMILLAS.md` -- registro fechado de semillas (simbolo suma "(+)"). Fuente de
  verdad de que semilla esta viva. Todo proyecto nuevo del corpus arranca de aca.
- `MANIFIESTO.md` -- workflows concretos propuestos (arrancables), fechado.
- `OMEGA_MAP.md` -- mapa conceptual Omega <-> flujo.
- `MOTOR.md`, `SPEC.md`, `v2/`, `v1/` -- el ensayo/diagnostico Omega versionado.
- `BIFURCACION_REGISTRO.md` -- instrumento append-only de lecturas del test.
- `HANDOFF_*.md`, `ULTIMO_*.md`, `TILDE_NOTA.md` -- textos TEORICOS del corpus.
  NO confundir con los handoffs OPERATIVOS de `context/` y `docs/handoffs/`.

## Como cruza a la practica

El unico puente teoria -> practica es el protocolo **motor-omega** (skill en
`.claude/skills/motor-omega/`): arranca SOLO desde una semilla viva de
`SEMILLAS.md` o un pedido real, declara su condicion de fracaso Omega11 ANTES de
producir, y deja el resultado como una PIEZA en el repo real. Ejemplo real:
`projects/cultura/tilde_residuo.py` (primera pieza corrida asi, desde la semilla
"tilde" (+)3). Las piezas viven en `projects/`; su registro fechado vive aca.

## Reglas al tocar esta carpeta

- No se ejecuta ni se cablea a la GUI/CLI. Es descriptivo.
- Lo fechado (semillas, fracasos, lecturas) NO se reinterpreta ni se borra.
- Limites de cultura: capa descriptiva si; nada generativo de sintesis; psicosis
  nunca perfila personas reales; precursor solo cultura/ley/estetica, nada
  operativo.
- **Si venis a "limpiar el repo": esta carpeta se preserva entera.** No es codigo
  desactualizado; es teoria fechada.
