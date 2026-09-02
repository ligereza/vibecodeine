# Cierre MAK / FLUJO — 2026-09-02

`status: IMPLEMENTATION_COMPLETE_TESTS_DEFERRED`. Resumen del JSON homónimo;
el JSONL lleva el detalle por accion.

## Metricas

| Metrica | Antes | Despues |
|---|---|---|
| rutas comunes | 3617 | **2840** |
| rutas comunes injustificadas | -- | **0** |
| solo MAK | 6 | 376 |
| solo FLUJO | 3 | 392 |
| archivos de test MAK | 388 | 199 |
| archivos de test FLUJO | 388 | 183 |
| tests compartidos | 387 | 10 |
| tests ajenos en MAK / FLUJO | 175 / 174 | **0 / 0** |
| Hub ajeno en MAK / FLUJO | 1 / 1 | **0 / 0** |
| imports cruzados no declarados | 4 | **0** |
| archivos src/flujo en MAK | 226 | 32 |
| archivos cultura/ en FLUJO | 190 | 10 |
| commits locales | -- | MAK 11, FLUJO 8 |

SHA final: MAK `c1f71668`, FLUJO `8b9830bd`. main `3d83ed60` e historia
`09f7e7d9` intactos.

## Como se justifico cada ruta comun

Cada `.py` comun se parseo con AST contra el arbol de la otra rama. Un archivo
que importa un modulo que la rama ya no lleva se elimino: asi el contador llego
a cero, no por declaracion. Reparto: 27 contratos declarados, 10 tests de doble
carril, 236 herramientas neutrales sin import de Hub, 735 material no
ejecutable, 1029 material artistico/dataset, 805 evidencia historica.

## Lo que cambio de raiz

El `.pth` no era la causa de la falta de portabilidad. La causa eran dos
imports de `cultura.mak_*` a nivel de modulo en `autonomia.py` y
`knowledge/opportunity_validity_capture.py`: hacian fallar `import
flujo.autonomia` en cualquier maquina sin el arbol MAK. Ahora son pares
opcionales con bandera declarada, y los tres sitios lazy sin proteger degradan
con error nombrado.

Los markers nunca separaron nada: pytest importa el modulo antes de
deseleccionarlo. La presencia se decide por `context/test_lane_map.json` mas el
arbol que cada test toca.

Requirements repartidos por uso medido: MAK no importa pydantic, typer, rich ni
requests, y le faltaba cairosvg. La base comun quedo byte-identica.

## Runtime

FLUJO vivo en el **puerto contractual 8765**, pid 897766, HTTP 200, corriendo
el codigo de la rama corregida. 8766 libre. Los tres servicios MAK siguen con
los mismos PID 854934 / 854932 / 854933 y 200 en 8900, 8890 y 8891; ninguno se
reinicio. El proceso redespleado sirve el contexto del worktree, no el de
`/home/mak`: los flags son identicos y volver al contexto de la caja es un solo
flag cuando la rama se publique.

## Pruebas

Ejecutadas: 6 focalizadas FLUJO, 14 focalizadas MAK, compileall en ambos
worktrees, sonda de import del contrato MAK aislado, `python -m flujo --help`
desde la rama, gate (exit 5), HTTP en cuatro puertos.

Diferidas y obligatorias para push: `pytest -m mak` y `pytest -m flujo`. Por eso
el estado no es `READY_TO_PUSH`.

## Sin resolver

17 tests que necesitan ambos arboles y `tools/capture_opportunity_validity.py`
quedan solo en main e historia. Los tres archivos modificados en el checkout de
`main` antes de esta sesion siguen sin atribuir.

## Rollback

```bash
git -C /home/mak update-ref refs/heads/MAK   a62f9019585f9c80a749dae7383f3a519f2efdf5
git -C /home/mak update-ref refs/heads/FLUJO ad9ee8811325ee8661023312cd1d4a419407f547
```

Sin push. `writes_outside_scope`: vacio.
