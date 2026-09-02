# Sonda: lo que CAPACIDADES.md, los tests y las funciones dicen de MAK

2026-08-29. Lo medido sobre el repositorio `flujo` durante la sesión de orden.
Complementa `APRENDIZAJE.CLAUDE.MD` (la máquina) y `ERRORES.CLAUDE.MD` (cómo me
equivoqué). Esto es el aparato: qué reglas gobiernan el código y qué demuestran
realmente.

---

## 1. La regla que gobierna `tools/`

`CAPACIDADES.md` es un registro. La regla, fechada **2026-07-25** y obligada por
`tests/test_higiene_repo.py`:

> **Toda herramienta en `tools/` declara su consumidor en `CAPACIDADES.md`, o no
> entra.**

El test enumera `tools/*.py` y falla si alguno no tiene fila. La comprobó
conmigo: rechazó `medir_tests.py` hasta que lo registré.

**Es una buena regla.** Este es un repo donde los agentes crean herramientas
todo el tiempo; sin ella, `tools/` se llena de scripts que nadie llama y nadie
distingue. La regla es la pregunta *¿qué está obsoleto?* contestada por
adelantado.

**Y tiene un agujero.** La forma más barata de declarar un consumidor es
escribir un test. Entonces el test deja de ser prueba de que la herramienta
sirve y pasa a ser la **coartada** para que entre. La regla caza "herramienta
sin consumidor"; no caza "herramienta que existe sólo porque alguien le escribió
un test".

Consecuencia operativa: cuando se retira una herramienta y se verifica con la
suite, la suite sólo confirma que **salieron las dos mitades del mismo par**. No
dice que sacarlo estuviera bien. Es un chequeo de consistencia disfrazado de
chequeo de utilidad. La verificación real es buscar, aparte, si algo todavía la
consume.

## 2. El estado de `CAPACIDADES.md`

- **119 archivos `.py`** en `tools/` contra **87 filas VIVO**, más 6 REVISAR y
  2 LEGACY. `MUERTO`: cero. — **Vieja 2026-08-31**: medido de nuevo,
  `tools/*.py` da 116 y la sección 5 de `CAPACIDADES.md` da 117 filas `VIVO`
  (más 1 `LEGACY`). Creció, como es de esperar en dos días de sesión activa;
  no se cuadraron las dos tablas porque el punto siguiente ya explica por qué
  no conviene confiar en el conteo a mano. No recites esta cifra: contarla es
  `grep -c '| VIVO |' /home/mak/flujo/CAPACIDADES.md` y `ls flujo/tools/*.py |
  wc -l`.
- Hay **dos tablas distintas**: el registro VIVO/MUERTO de la sección 5, y una
  segunda tabla con columnas de conteo. Un agente borró la fila de la primera
  al retirar una herramienta y dejó la de la segunda afirmando que el archivo
  existe. **Ninguna de las dos la genera `tools/repo_audit.py`**: se mantienen a
  mano, así que divergen en silencio.
- Retiradas en esta sesión por no tener consumidor medido: `context_pack.py`,
  `render_archaeology_deliverables.py`, `tapiz_live_loop.py`, `token_budget.py`,
  `verify_all.py`. Corroborado de forma independiente por un inventario
  anterior, `docs/session_learning/auditar_capacidades_mak/inventory.json`, que
  ya decía *"none proven for context_pack, token_budget, verify_all,
  tapiz_live_loop, tapiz_telemetry, render_archaeology_deliverables"*.
- **Conflicto sin resolver**: el `action_plan.md` de ese mismo inventario
  recomienda *conservar* `render_archaeology_deliverables.py` como histórico. Se
  retiró igual. Los dos criterios son defendibles; es reversible con un `mv`.

## 3. Los tests: qué son y qué no

**350 archivos, 3634 funciones, introducidos por 164 commits.** Ninguna función
tiene el cuerpo idéntico a otra (comparado por AST normalizado). Ninguna apunta
a un módulo inexistente. Crecieron parejo entre junio y agosto de 2026, no en
una volcada.

**No son acumulación. Son el subproducto de la regla del punto 1**: cada test
aterriza en el mismo commit que la función que prueba, porque la herramienta no
podía entrar sin él. La palanca para reducir superficie está en `tools/`, no en
`tests/`.

### El propósito ya está escrito

No hace falta abrir un test para saber para qué es: está en el mensaje del
commit que lo introdujo. Un solo `git log --diff-filter=A` sobre `tests/` ubica
los 350 archivos en sus 164 commits, con fecha y motivo.

    python3 ~/flujo/tools/medir_tests.py              # áreas que crecieron en commits sueltos
    python3 ~/flujo/tools/medir_tests.py --cronologia # los 164 commits, del más viejo al más nuevo

Lo que ese agrupamiento separa:

- **Áreas que llegaron enteras en un commit** = un diseño tomado una vez. Son
  11. `archive` parece la peor con 12 archivos, pero 10 son del mismo día en
  cuatro commits: entrega por etapas, no acreción.
- **Áreas que crecieron en commits sueltos** = donde puede haber repetición.
  `research` es la única con sujetos anchos —consolidate, publish, establish—
  repartidos en 5 fechas a lo largo de un mes.

Y descarta sospechas sin abrir nada: `ig` creció en cinco fechas y **no**
repite, porque cada sujeto nombra un bug distinto (URL canónica, parth-dl,
fallback curl_cffi). Cinco regresiones, no cinco veces lo mismo. Igual `rd` y
`tilde`.

**Advertencia sobre este método**: agrupar por la palabra del nombre de archivo
produce clusters falsos. Los 11 archivos de `research` cargan once módulos
distintos. El nombre no es el tema.

### Lo que la suite NO demuestra

`experiments/pilots/` está en `.gitignore` línea 104 a propósito: guarda
evidencia real de pilotos (ARICA-FONDART-2027, DREFQUILA, HARRY-NACH-2026).
Cuatro suites lo leían con `read_text()` sin comprobar que existiera. En MAK
está; en un checkout limpio no.

Resultado: **CI llevaba seis corridas rojas en `main` mientras la suite local
daba 3741 verde.** La suite certificaba esta máquina, no el repositorio.
Corregido con guardas de skip, el patrón que el repo ya usaba en
`tests/test_open_episode_state.py:91` —saltar **nombrando lo que falta**, para
que la ausencia se vea con `-rs` en vez de pasar por salud.

Segundo defecto de la misma familia: dos tests lanzaban `ROOT/.venv/bin/python`,
un archivo que en CI no existe. 48 archivos ya usaban `sys.executable`.

### Las compuertas, que son la parte que sí atrapa

De 3634 funciones, **533 (15%) leen el repo como texto** en vez de ejercitar
comportamiento. Y son las más caras: de los 25 tests más lentos, los primeros
cuatro son `test_higiene_repo` (14,8 s), `test_idioma_ratchet` (7,0 + 6,7 + 6,7)
y `test_comandos_manifiesto` (6,7).

Parecen mal repartidas, y son las únicas que encontraron algo en toda la sesión.
Lo que encontraron fueron **mis propios errores**:

| compuerta | qué vigila | me atrapó en |
|---|---|---|
| `test_idioma_ratchet` | idioma de comentarios e identificadores | docstring en español, luego identificadores en español |
| `test_higiene_repo` | que las herramientas corran y estén registradas | una herramienta sin fila en CAPACIDADES |
| `test_higiene_docs` | qué tienen permitido decir los docs | `AUTORIDAD.md` escribiendo el patrón que él mismo prohíbe |
| `test_agent_bootstrap` | que el paquete de arranque no pierda el contrato | cuatro afirmaciones permanentes caídas |
| `test_comandos_manifiesto` | que el manifiesto no mienta sobre el CLI real | un comando documentado y retirado |

Son una barrera contra agentes que degradan el repo. No son evidencia de que
MAK funcione. Para eso están `medir_organismo.py` y `medir_procesos.py`.

### Deuda medida, no resuelta

- **24 módulos grandes bajo 40% de cobertura**, 6722 sentencias sin cubrir. El
  peor es `cultura/mak_curatoria/ingesta_archivo.py`: 882 sentencias al 9% — **CORREGIDO 2026-08-31**: la cifra de 9% era falsa. Medido con la suite completa, la linea base era **72%** y hoy queda en **73%**. El 9% salia de una seleccion parcial de tests o de una forma equivocada de `--cov`. La deuda real de ese archivo son 234 sentencias sin cubrir, no 800., y
  está **vivo** — `cultura/mak_conductor/handler_registry.py` lo llama en nueve
  puntos.
- **Solapamiento por propiedad verificada: sin medir.** Cero cuerpos idénticos
  descarta el copy-paste, no la redundancia. El instrumento que lo contestaría
  es cobertura por test (`pytest --cov-context=test`) y quedó sin correr.
- El baseline `tests/fixtures/idioma_baseline.txt` exoneraba a **12 archivos
  inexistentes**. Corregido: una exención a nombre de un muerto se convierte en
  permiso automático si mañana nace un archivo con esa ruta.

## 4. Las funciones y los puentes

- **122 de 122 shims resuelven**: su destino existe en el repo. Verificado por
  dos métodos independientes (evaluador AST y `test -f` a mano). Las 23 líneas
  del cron pausado arrancarían sin error de archivo ausente. — **Vieja
  2026-08-31**: el conteo de 122 ya no es el actual. Hoy existe un instrumento
  que no existía cuando se escribió esto,
  `indexes/mak-bridges-20260829/medir_bridges.py`, y da **130** puentes (52
  plataforma, 36 research, 18 codex, 12 curatoria, 6 lenguaje, 3 vigia, 3
  xio_puente), con **0 destinos ausentes y 0 defectos de entrypoint**: la
  conclusión ("todos resuelven") sigue siendo cierta, la cifra de 122 no. No
  la repitas: corre el instrumento.
- **Un defecto real, más sutil que "destino ausente"**: `plataforma/copilot.py`
  llamaba a `_MODULE.main()` en su bloque `__main__`, y el destino canónico
  —1820 líneas— no define `main`. La copia pre-proyección del 2026-08-21 tampoco:
  **el CLI no se perdió en la divergencia, nunca existió.** De los 30 shims que
  prometen `main`, era el único cuyo destino no lo tenía. Corregido quitando la
  promesa, no inventando la función.
- `cultura/mak_plataforma/hub.py` **no** reimplementa `route_payload` ni
  `probe_payload`: los importa de `flujo.knowledge.project_api` con un `except`
  que degrada a `None`, porque `plataforma/.venv` no tiene `flujo` instalado. Lo
  contrario se afirmó durante media sesión antes de abrir el archivo.
- `cultura/mak_plataforma/tandas.py` mantiene, por área, una **lista blanca** de
  rutas que un tanda puede citar como evidencia. No exige que existan, así que
  retirar una herramienta no rompe nada — pero deja autorizada una ruta que
  jamás resolverá. Mismo defecto que el baseline de idioma.

## Cobertura, medida de verdad el 2026-08-31

Lo de arriba citaba "24 módulos bajo 40%, 6722 sentencias sin cubrir" y que
`ingesta_archivo.py` era la mayor deuda al 9%. Medido con la suite completa
(`pytest tests --cov=src/flujo --cov=cultura --cov-report=term`):

    249 módulos, 59 359 sentencias, 71% cubierto
    32 módulos bajo 40%, de ellos 21 con 100 sentencias o más
    6124 sentencias sin cubrir en los que están bajo 40%
    17 327 sentencias sin cubrir en total

La cifra de los 24 módulos estaba **vieja** (son 32), no inventada. La del 9%
de `ingesta_archivo.py` estaba **falsa**: su línea base era 72% y hoy es 73%,
con 234 sentencias sin cubrir. Salía de una selección parcial de tests, y el
primer intento honesto de medirla devolvió "No data to report" — ésa era la
señal de que el instrumento estaba mal apuntado, y se ignoró.

**La deuda real, por sentencias sin cubrir:**

| sin cubrir | % | sentencias | módulo |
|---:|---:|---:|---|
| 1197 | 29% | 1675 | `src/flujo/web/hub.py` |
| 1148 | 29% | 1611 | `src/flujo/cli.py` |
| 1062 | 62% | 2770 | `cultura/mak_plataforma/hub.py` |
| 420 | 45% | 762 | `cultura/mak_research/interfaz.py` |
| 388 | 27% | 531 | `cultura/mak_curatoria/diagnostico_proyectos.py` |
| 360 | 27% | 494 | `cultura/mak_research/memoria.py` |
| 309 | 35% | 475 | `cultura/mak_plataforma/visual_index.py` |

**Los dos hubs y el CLI son la deuda**, no curatoría. Y el tercero de esa lista
—`cultura/mak_plataforma/hub.py`, 2770 sentencias— es el órgano que está
corriendo ahora mismo en `:8900`: la superficie más expuesta de MAK es también
de las menos probadas.

`ingesta_archivo.py` sí ganó algo esta jornada: nueve tests que fijan la
doctrina de su gate de evidencia, que estaba sin fijar. Ver
`tests/test_ingesta_evidence_gate.py`. Pero el trabajo grande está en otra
parte, y dirigir agentes al 9% fue dirigirlos a un fantasma.

## Solape entre tests: contestado el 2026-08-31

La pregunta "de los ~3800 tests, cuántos verifican lo mismo" quedó medida y la
respuesta está en `~/indexes/mak-solape-tests-20260829/RESPUESTA.md`, con el
analizador al lado para repetirla.

En una línea: **245 grupos comparten cobertura idéntica (636 tests) y ninguno es
redundante** — son tests que comparten un constructor y afirman propiedades
distintas de su salida. Verificado abriéndolos.

Y el hallazgo inverso, que es el que vale: **11 310 de 52 228 líneas cubiertas
las toca un solo test**, y 773 de ellas están en `cultura/mak_plataforma/hub.py`,
el órgano que corre en `:8900`. La pregunta útil no era qué sobra, era qué
cuelga de un hilo.
