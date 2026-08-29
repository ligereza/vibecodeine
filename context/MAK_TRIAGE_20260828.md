# MAK triage semantico -- 2026-08-28

Ejecuta el paso 2 de `context/GIT_HISTORY_STRATEGIC_REVIEW.md`, escrito el
2026-08-14 19:16, trece minutos despues de que el organismo se pausara, y
nunca ejecutado hasta hoy.

Tres fuentes cruzadas, ninguna inventada:

- **historia git**: `/home/mak/Descargas/historia git.odt`, sha256
  `510ca28c...e6a56` verificado contra el que registro LUNA. 450 key path
  journeys con dominio, primer y ultimo toque. Los 1347 omitidos citaban
  `git_history_context.full.json`, que **no existe en ningun arbol**.
- **nacimiento del inodo**: ext4 guarda birth time en esta caja (`stat -c %W`).
- **medicion de la sesion 2026-08-28**: que corre, que esta pausado, que consume.

Ordenado por primer toque en la historia de Git. Una celda sin medicion dice
`sin medir`; la diferencia entre "no lo se" y "no existe" fue el error mas
caro de esta sesion.

| ruta | estado | primer toque | ultimo toque | nacido | journeys | dominio | rol y verificacion |
|---|---|---|---|---|---:|---|---|
| `inbox/` | vivo/adoptable | - | - | 2026-07-20 | 0 | - | 2 txt de junio. consumido por cli.py e intake/reception.py |
| `jobs/` | solo-evidencia | - | - | 2026-07-20 | 0 | - | trabajos entregados. gitignored; zip de 65 MB redundante retirado |
| `knowledge/` | vivo/adoptable | - | - | 2026-07-20 | 0 | - | conocimiento declarado por ruta. 21 referencias en codigo |
| `linea_editorial/` | vivo/adoptable | - | - | 2026-07-20 | 0 | - | contrato editorial RD v4.1. inventario de logos corregido esta sesion |
| `proposals/` | solo-evidencia | - | - | 2026-07-20 | 0 | - | 2 ideas de negocio RD de Vibo, 2026-07-03. sin consumidor de codigo; citadas solo por corpus_olvido |
| `puente/` | solo-evidencia | - | - | 2026-07-20 | 0 | - | material conceptual. MD_CONTEXT_MASTER: sin consumidor de runtime |
| `schemas/` | vivo/adoptable | - | - | 2026-07-20 | 0 | - | 24 JSON Schema. sin puente medido con los 209 identificadores mak-*-v1 inline |
| `out/` | generado (regenerable) | - | - | 2026-08-03 | 0 | - | productos compilados. no es fuente; gitignored |
| `contracts/` | vivo/adoptable | - | - | 2026-08-15 | 0 | - | contratos por departamento. sin medir consumidor |
| `experiments/` | solo-evidencia | - | - | 2026-08-24 | 0 | - | corridas de piloto. 9 suites las leen como fixture; 187 MB deduplicados |
| `checkpoints/` | vivo/adoptable | 2026-06-28 | 2026-07-03 | 2026-07-20 | 13 | SHARED_OR_UNKNOWN | solo .gitkeep. consumido por airdrop.py, project_ir.py, director.py y 3 tests |
| `context/` | vivo/adoptable | 2026-06-28 | 2026-08-13 | 2026-07-20 | 5 | SHARED_OR_UNKNOWN | continuidad operativa. LAST_HANDOFF es autoridad de estado; 13 PHASE quedan de 749 |
| `docs/` | vivo/adoptable | 2026-06-28 | 2026-08-12 | 2026-07-20 | 142 | SHARED_OR_UNKNOWN | doctrina y evidencia fechada. AUTORIDAD.md y MAK_ORGANISMO.md escritos esta sesion |
| `projects/` | solo-evidencia | 2026-06-28 | 2026-07-26 | 2026-07-20 | 8 | SVG_ART | dossiers y proyectos fechados. sin consumidor de codigo medido |
| `scripts/` | vivo parcial | 2026-06-28 | 2026-07-03 | 2026-07-20 | 1 | SHARED_OR_UNKNOWN | 29 scripts. 15 con invocador, 14 sin ninguno |
| `src/` | vivo/adoptable | 2026-06-28 | 2026-08-13 | 2026-07-20 | 5 | RD | runtime y CLI. 196 modulos importan; 42 comandos CLI; 209 esquemas |
| `svg/` | vivo/adoptable | 2026-06-28 | 2026-07-27 | 2026-07-20 | 51 | SVG_ART | plantillas y piezas. consumido por export/illustrator.py y hub.py |
| `tests/` | vivo/adoptable | 2026-06-28 | 2026-08-13 | 2026-07-20 | 9 | MAK | 3799 ids en 357 suites. 3794 pasan, 5 skip, 0 fallan |
| `tools/` | vivo/adoptable | 2026-06-28 | 2026-08-10 | 2026-07-20 | 3 | SHARED_OR_UNKNOWN | 118 herramientas registradas. 92 en el registro seccion 5; 4 con disparador de workflow |
| `web/` | vivo/adoptable | 2026-06-30 | 2026-07-27 | 2026-07-20 | 3 | SVG_ART | bundle Vite/React. 36 modulos, 35 alcanzables, 0 muertos por repo_audit.py |
| `assets/` | vivo/adoptable | 2026-07-03 | 2026-07-03 | 2026-07-20 | 1 | SHARED_OR_UNKNOWN | logos RD. 2 SVG consumidos por 3 herramientas |
| `datadrops/` | solo-evidencia | 2026-07-03 | 2026-07-03 | 2026-07-20 | 1 | SVG_ART | entradas fechadas. sin medir |
| `xio/` | bloqueado | 2026-07-12 | 2026-08-07 | 2026-07-20 | 5 | SHARED_OR_UNKNOWN | Android/show. 4 runbooks restaurados desde WIN; servicio mak-xio inactivo y deshabilitado |
| `cultura/` | vivo/adoptable | 2026-07-15 | 2026-08-13 | 2026-07-20 | 67 | MAK | 9 subsistemas; hub.py es el unico proceso corriendo. 46 shims de plataforma/ delegan aca y los 46 resuelven |
| `iskvw/` | vivo/adoptable | 2026-07-27 | 2026-07-27 | 2026-07-27 | 40 | PORTFOLIO | editor y piel del portafolio. sin medir consumidor de piel/trazos |
| `data/` | vivo/adoptable | 2026-08-12 | 2026-08-12 | 2026-07-20 | 1 | SHARED_OR_UNKNOWN | 4 bases. mak_knowledge 48 tablas/387104 filas por repo_audit.py en CI |

Dominios en la historia: {"SHARED_OR_UNKNOWN": 2203, "SHARED_SYSTEM": 274, "RD": 49, "MAK": 299, "PORTFOLIO": 938, "SVG_ART": 255, "CODEX": 4}

## Lo que la historia dice y la fisica no confirma

- Git cannot prove which MAK/WIN file is physically current.
- Git commit subjects are not confirmed user decisions.
- A branch named mak is not the same thing as the MAK Linux box.
- Duplicate paths require physical hash comparison before consolidation.
- The full 22 MB evidence file is preserved separately for targeted queries.

