# MEMORIAS.md

Memoria consolidada de MAK, auditada el 2026-09-03. Este archivo conserva
continuidad útil para el operador; no es contrato, no reemplaza una medición y
no convierte una hipótesis histórica en un hecho actual.

## Cómo leerla

Cada entrada queda en una de estas clases:

- `OPERADOR`: contexto o decisión expresada por el operador.
- `MEDIDO`: resultado observado con comando, código, consumidor o estado
  físico indicado.
- `HISTÓRICO`: ocurrió en una fecha anterior; puede orientar, pero no describe
  necesariamente el presente.
- `POR_REVISAR`: hay una afirmación o una diferencia que todavía necesita
  fuente, medición o decisión. Cada pendiente de abajo explicita motivo,
  evidencia faltante y siguiente acción.

La fecha de una medición es parte del dato. Una memoria puede conservar una
lección aunque el hecho que la originó haya envejecido.

## Contexto del operador

- `MAK` es el computador Linux completo.
- La rama MAK está montada en `/home/mak`; la rama FLUJO está montada en
  `/home/mak/flujo`. Son dos checkouts del mismo proyecto, con responsabilidades
  distintas.
- `vibecodeine` es el repositorio y `ISKVW`/`iskvw.cl` es la superficie pública
  del trabajo artístico. `IRIS` es el sistema interno de orden y relación.
- Reduciendo Daño (RD), Cultura, el trabajo VJ y el archivo ISKVW comparten
  intereses en eventos, productoras y venues, pero no se deben confundir sus
  autoridades ni sus datos.
- FLUJO APP es un conjunto de herramientas de autoría/integración. El flujo
  operativo que el operador reconoce como real es la señal de correo con tema
  `EVENTO`, que llega a Git y crea un issue. La lectura de esos issues debe ser
  de solo lectura para no generar un bucle de respuesta.
- La descarga del flyer, OCR/visión, render Blender, Drive y las bases de
  eventos/productoras/venues son partes relacionadas del trabajo, pero cada
  relación debe demostrarse por consumidor y fuente, no por proximidad de
  carpetas.

## Aprendizajes consolidados

### Buscar bien es parte de medir

Una búsqueda por idioma, basename o una sola carpeta no demuestra ausencia.
Antes de crear una base, herramienta o documento hay que buscar en español e
inglés, revisar nombres alternativos, recorrer las raíces físicas pertinentes
y comprobar el consumidor. La búsqueda amplia también sobre-incluye cachés,
vendor, worktrees, informes y archivos históricos; el nombre solo no prueba
autoridad.

### Una declaración no es una capacidad ejecutándose

Un archivo, import, puerto, test verde o nombre de proceso demuestra solo una
parte. Para declarar una superficie como disponible se deben distinguir fuente,
consumidor, proveedor, proceso, listener y resultado de la prueba. Los estados
`posible`, `presente`, `implementado`, `activo` y `verificado` no son sinónimos.

### La máquina tiene prioridad sobre la prosa envejecida

Las capacidades actuales se comprobaron el 2026-09-03 con:

```text
/home/mak/.venv/bin/python /home/mak/tools/capabilities.py --check
mak-capabilities-runtime-v1 | 9/9 declared | 9/9 sources | issues=0

/home/mak/.venv/bin/python /home/mak/tools/repo_audit.py
repo-audit: OK
```

Eso confirma la medición de esas superficies y bases en ese momento; no
confirma automáticamente cada frase de los documentos antiguos.

### Las dudas deben ser accionables

`dudoso` no es una categoría final. Toda duda útil debe decir el motivo, qué
evidencia falta y cuál es la siguiente acción que puede resolverla. Si solo
existe una fecha de medición antigua, se conserva como histórico y se pide una
nueva medición cuando el dato importe.

### Las bases y los archivos tienen autoridades distintas

RD, MAK, FLUJO, ISKVW, XIO, Windows, montajes y archivos históricos pueden
compartir material sin compartir autoridad. Una coincidencia de nombre, hash o
ruta no autoriza fusionar identidad, datos ni significado. Las relaciones
deben conservar fuente, propietario, estado y visibilidad.

### Los agentes no deben inventar continuidad

Las memorias de Claude y Codex son almacenes internos de sus respectivos
runtimes. Este archivo resume lo que es útil para el proyecto, pero no las
reemplaza ni debe leerse como instrucciones automáticas para ellos. Las
decisiones del operador y las mediciones actuales tienen prioridad sobre una
recomendación antigua de cualquier agente.

## Medición vigente junto a esta consolidación — 2026-09-03

Se repitieron las mediciones, no se heredó el resultado desde una memoria:

```text
/home/mak/.venv/bin/python /home/mak/tools/capabilities.py --check --check-branch
MAK: 9/9 superficies declaradas, 9/9 fuentes, issues=0

/home/mak/.venv/bin/python /home/mak/flujo/tools/capabilities.py --check --check-branch
FLUJO: 2/2 superficies declaradas, 2/2 fuentes, issues=0
```

- `capabilities.py` confirma fuentes, unidades, listeners y consumidores
  declarados; no confirma la calidad semántica de cada herramienta.
- `tools/repo_audit.py`: `mak_knowledge.db` 48 tablas/387104 filas,
  `rd.db` 20/7585, `rd_datos.db` 3/0 y `flujo.db` 1/6; integridad `ok` en los
  cuatro archivos medidos.
- `tools/mak_status.py`: estado `attention`, 2 atenciones, 0 bloqueos y
  política de aprendizaje `candidate`; esto no equivale a una falla total ni
  a un cierre definitivo.
- El `repo_audit.py` ejecutado desde FLUJO devuelve `ATTENTION` porque ese
  auditor también busca bases y consumidores propios de MAK; no se usa como
  veredicto de salud de la CLI FLUJO.
- La consolidación de capacidades deja dos documentos de proyecto: uno para
  MAK y otro para FLUJO. XIO queda descrito dentro de MAK como capacidad
  dependiente, con la operación en el Xiaomi separada de la presencia del
  código local.

## Historia que se conserva sin elevarla a presente

- Las memorias de continuidad de Codex registran trabajos sobre IRIS/Atlas,
  Hub, archivo ISKVW, bases, conciliaciones, pruebas, XIO y exportaciones.
- Las memorias de Claude registran lecciones de búsqueda, autoridad local,
  issues, entregas RD, operación VJ, XIO y límites de los agentes.
- `MEMORIA_DIRECCION.md`, los handoffs, informes y documentos de sesiones
  contienen ideas y decisiones valiosas, pero sus cifras y rutas se consideran
  históricas hasta volver a medirlas.
- Los documentos `CAPACIDADES_MAK.md` y `CAPACIDADES_FLUJO.md` anteriores se usaron como fuentes de
  contraste. Sus duplicados, worktrees y copias de `_archive` no son nuevas
  autoridades: son historia o material de otra ejecución.

## Fuentes absorbidas

- `/home/mak/.codex/memories/MEMORY.md`, `memory_summary.md` y
  `raw_memories.md`.
- `/home/mak/.claude/projects/-home-mak/memory/MEMORY.md` y la memoria del
  proyecto de Escritorio.
- `/home/mak/state/windows-director-20260813/claude-memory/MEMORY.md` y
  `claude-recovered-artifacts/MEMORIA_DIRECCION.md`.
- Las matrices de capacidades MAK, FLUJO y XIO existentes en los dos
  checkouts, contrastadas con sus consumidores y los verificadores actuales.

## Pendientes explícitos

| Pendiente | Motivo | Evidencia faltante | Siguiente acción |
|---|---|---|---|
| Pipeline flyer/OCR/visión/render/Drive | Las matrices mezclaban herramientas, workflows y restos históricos | traza actual del issue `EVENTO`, consumidor de cada etapa y artefacto de salida | leer `issue_descarga_ig.yml` y sus callers; repetir una corrida read-only o registrar que no existe |
| Autoridad de bases RD/eventos/productoras/venues/logos | Hay varias SQLite y proyecciones con dominios distintos | mapa actual de escritores, lectores y autoridad por dominio | medir writers/consumers; pedir al operador la decisión final antes de fusionar |
| Cifras operativas antiguas | Una fecha vieja describe una medición pasada, no el presente | nueva salida del comando que originó la cifra | repetir solo la medición necesaria y reemplazar el dato, manteniendo la fecha anterior como historia |
