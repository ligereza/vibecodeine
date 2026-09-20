# SYSTEM

Contexto operacional durable de VIBECODEINE.

Este archivo explica identidades, fronteras e invariantes. No es un snapshot:
HEAD, archivos presentes, servicios, consumidores y tests deben medirse.

## Identidades

- **MAK** es el computador Linux físico del usuario, con raíz operativa
  `/home/mak`. No es una rama, un repo ni un módulo.
- **Windows** es la estación física actual de control, desarrollo y render.
  Está conectada a MAK por la red privada del estudio y un enlace Ethernet
  directo. El antiguo runtime/copia Windows retirado NO es este PC actual.
- **FLUJO** es software: el motor portátil que vive principalmente en
  `src/flujo/`. MAK puede ejecutarlo/consumirlo; MAK != FLUJO.
- **XIO** es un sistema/repositorio separado. VIBECODEINE consume contratos y
  evidencia publicados por XIO; no mantiene una copia completa de `xio/`.
- **IRIS/Atlas** organiza archivo, evidencia, relaciones y orden.
- **ISKVW** es una superficie de portfolio/publicación. Una vista o editor no
  se convierte por eso en segunda autoridad.

## Topología operativa

MAK y Windows son máquinas distintas.

```
Windows
control / desarrollo / GPU / Blender
        |
        | LAN privada + Ethernet directo
        | SSH / SCP / HTTP
        v
MAK Linux
/home/mak
```

GitHub transporta código y estado versionado; no es la conexión física entre
ambas máquinas.

El antiguo árbol/runtime Windows conservado históricamente bajo rutas como
`/home/mak/WIN` no representa a la estación Windows actual.

## README

`arte-ascii-readme.svg` ES el README raíz y además una obra SVG animada
construida con el texto/ASCII del README.

La ausencia de `README.md` es intencional. No recrearlo para satisfacer una
convención o un validador genérico.

## Cómo conocer el presente

1. Leer este archivo para identidades e invariantes.
2. Medir Git: branch, HEAD, diff, dirty state y procedencia.
3. Ejecutar `python tools/contexto_repo.py --json`.
4. Cuando corresponda a MAK físico, ejecutar
   `python tools/mak_status.py --json`.
5. Consultar `python -m flujo --help` para la CLI real.
6. Revisar consumidores, tests y workflows del área.
7. Usar historia Git sólo cuando el presente sea contradictorio.

**Git explica por qué; árbol + código + consumidores + tests explican qué.**

## Autoridad y consumidores

- Presencia en el árbol no demuestra vigencia.
- Ausencia en este repo no demuestra inexistencia física.
- Una mención documental no es un consumidor real.
- Un wrapper legacy llamando wrappers legacy no demuestra vida.
- Una herramienta manual puede ser válida aunque no tenga invocador automático.
- Owner y consumer pesan más que el nombre del archivo.
- Una proyección puede adaptar presentación, pero no convertirse silenciosamente
  en segunda autoridad.
- Estado medible no se copia a prosa.

## Regla anti-resurrección

El 2026-09-08 una unión mecánica MAK + FLUJO restauró cientos de archivos.
Recuperó trabajo válido, pero también resucitó piezas retiradas.

Ante un componente dudoso:

1. medir consumidor actual;
2. buscar si fue retirado explícitamente;
3. distinguir reactivación deliberada de restauración mecánica.

Una retirada explícita prevalece sobre una reaparición mecánica si no existe
una decisión posterior explícita de reactivación.

## Retiros que no deben revertirse accidentalmente

- **Airdrop**: subsistema retirado deliberadamente. No revivir módulo, CLI,
  scripts, workflow o tests sólo porque aparezcan en historia/merge.
- **Copia XIO en VIBECODEINE**: retirada. La autoridad vive en XIO; aquí se
  conserva sólo integración por contratos/evidencia.
- **AGENTS.md / handoff persistente**: retirados como contrato de entrada.
  No recrearlos como autoridad.
- **Watsonx runtime**: retirado. Benchmarks históricos no son provider activo.
- **tapiz_live_loop**: retirado como daemon sin consumidor medido.

## Archivo, obra y evidencia

- Archivo != obra.
- Registro != obra != contexto != relación != presentación.
- El nombre o la ruta son señales, no identidad suficiente.
- Evidencia, conocimiento y política son capas distintas.
- Observación e interpretación son capas distintas.
- Un candidato no es un hecho.
- `unknown`, abstención y ausencia medida son resultados válidos.
- Una señal puede servir para refutar sin bastar para confirmar.
- Una decisión humana debe conservarse como evidencia humana, no reescribirse
  como inferencia automática.
- Antes de declarar que algo falta, buscar en las rutas, idiomas y sistemas
  relevantes.

## Decisiones humanas durables

- El portfolio no intenta descubrir un orden verdadero único: primero define el
  formato/propósito de presentación y luego ordena los materiales para ese fin.
- No se exige una descripción escrita por pieza para poder clasificarla,
  relacionarla o decidir sobre ella.
- Código, comentarios, contratos de máquina y commits se escriben en inglés
  cuando corresponda; los productos que lee una persona se entregan en español
  correcto, con tildes y ñ.
- Un objetivo importante debe declarar cómo puede fallar. El fracaso medido se
  conserva como evidencia; no se reinterpreta para hacerlo parecer éxito.

## Principios de trabajo

- Leer y medir antes de editar.
- No reconstruir la historia completa salvo contradicción.
- Cambios con write-set acotado y rollback claro.
- Preferir la CLI/módulo actual sobre wrappers pre-Typer.
- No mantener dos motores para la misma capacidad.
- Todo cambio relevante debe identificar owner, consumer y prueba.
- Si una regla puede medirse, automatizarla en vez de narrarla.
- Cada entrega útil debería dejar un activo reutilizable, no otra capa de
  documentación de sesión.

## Documentación vs contenido

"Un solo contexto" no significa borrar Markdown que sea contenido real.

Se conservan cuando corresponda:
- dossiers y postulaciones;
- investigación;
- bases y evidencia recuperada;
- contratos técnicos ligados a código/tests;
- documentación de producto que contiene conocimiento humano no expresable
  completamente en schemas/código.

Se retiran del árbol activo:
- handoffs;
- NEXT;
- cierres de sesión;
- snapshots de estado;
- reportes de fase;
- roadmaps cumplidos;
- inventarios regenerables;
- manuales supersedidos;
- narrativas históricas cuyo único propósito es explicar qué ocurrió.

Git conserva esa historia.

## Qué no debe agregarse aquí

No copiar:
- SHA/HEAD actual;
- cantidad de tests;
- número de archivos;
- listas exhaustivas de scripts;
- estados de servicios;
- ramas/worktrees temporales;
- tareas de una sesión;
- métricas que puedan medirse.

Este archivo debe permanecer pequeño y durable.
