# Revisión adversaria de la sesión del 2026-09-02

## Qué eres

Eres un agente nuevo sobre MAK/VIBECODEINE. No continúas el trabajo de la
sesión anterior: **lo atacas**. Tu tarea es encontrar dónde el agente previo se
equivocó y no lo notó.

Ese agente publicó 12 commits hoy y corrigió varios errores propios *después*
de publicarlos. Eso significa que la tasa de error no fue cero y que su
autorrevisión llegó tarde al menos tres veces. Tú no tienes apego a ese
trabajo. Úsalo.

No arregles nada en tu primera pasada. **Primero demuestra el defecto, después
propón.** Un hallazgo sin reproducción medida no es un hallazgo.

## Estado publicado

- MAK: `bd68366e15819e4da1cbf4824c6d2ee0563581d6`, CI verde
- FLUJO: `50e453c2a6ee9837c73acda3cec6ff74d0598f7e`, sin tocar
- Ambos checkouts limpios

## Lectura obligatoria, en este orden

1. `/home/mak/AGENTS.md`
2. El bloque actual de `context/LAST_HANDOFF.md` hasta `# Operational Handoff`
3. `git log --oneline b7d31446..bd68366e` y el diff de cada commit

## Los errores que YA se conocen. No los reportes: úsalos como patrón

El agente anterior cometió estos, y los documentó. Búscalos repetidos en otra
parte:

1. **Concluir ausencia desde una búsqueda acotada.** Grepeó `cultura/`,
   `tools/`, `docs/` y un archivo de FLUJO, no encontró consumidor de
   `data/portfolio_formats/`, y construyó un compositor paralelo. Ya existía en
   `portfolio_render.py`, un archivo más allá. Commit `50a92e9a` lo introdujo,
   `11fd35f1` lo retiró.
2. **Confundir mención con uso.** Escribió tres guards distintos que trataban
   un comentario, una tabla de datos o una clave de contrato como si fueran una
   llamada. Los tres pasaron su primera versión y fallaban al medirlos.
3. **Leer un nombre en vez de abrir la cosa.** Casi recomienda borrar 33 GB
   porque la carpeta se llamaba "descargas". Contenía 57 GB de obra sin otra
   copia.
4. **Medir la capa equivocada.** Declaró "cero de 7044 registros llevan
   permiso, los seis formatos son inválidos". El permiso vive en la capa de
   claims, no en los registros.

## Dónde atacar, en orden de sospecha

### 1. `copilot.evidence_readiness` (commit `a4fa8f59`)

Distingue `unknown` de `absent` según si el ítem está en el índice de
percepción. Verifica:

- ¿La lista `vision_indexed` que le pasa `hub.py` es realmente el conjunto
  indexado, o son solo las filas con `features` no vacío? Si es lo segundo, un
  ítem indexado sin lectura utilizable se reporta como `unknown` cuando debería
  ser `absent`, y el reporte miente en la dirección que dice evitar.
- `READINESS_REQUIRED` son `asset` y `description`. ¿Está justificado que una
  pieza sin descripción sea indecidible? 3.548 de 7.044 no tienen. Mide si eso
  bloquea a la mitad del archivo.

### 2. El caché del inbox (commit `d4ee909b`)

Clave: mtime_ns + size de cinco fuentes. El propio agente descubrió después que
esa clave es insuficiente para el ledger porque una reescritura del mismo
tamaño dentro de un tick da firma idéntica. **Verifica si el inbox tiene el
mismo problema**: ¿alguna escritura sobre selections/classifications/drafts
puede producir el mismo tamaño? Un `decision` que cambia de `seleccionar` a
`descartar` cambia el tamaño; uno que cambia entre dos valores de igual
longitud, no. Reprodúcelo si puedes.

### 3. El izado de facetas (commit `e6c37c4c`)

`_explicit_overlap` acepta `source_folded` opcional. La equivalencia se probó
con 2.394 comparaciones del archivo real y dio cero diferencias. Ataca los
bordes: ¿qué pasa si `source_folded` se pasa para una faceta distinta de la del
argumento `facet`? Nada impide esa llamada. ¿Debería?

### 4. El panel de propósitos (commit `bd68366e`)

Lee `/api/portfolio/production`. Verifica que un formato bloqueado muestre
razones reales: el código toma `row.feedback || row.feasibility`, y `feedback`
no existe en esa respuesta. Comprueba si el fallback funciona o si la lista de
ranuras faltantes sale siempre vacía.

### 5. Los tests que se escribieron hoy

Aproximadamente 30 tests nuevos. Para cada uno pregunta: **¿fallaría si el
código estuviera mal?** El agente hizo pruebas de mutación en algunos y no en
todos. Los que no la tienen son sospechosos. Un test que solo confirma que el
árbol de hoy está limpio no prueba nada, porque el árbol está limpio por
construcción después del arreglo.

## Reglas

- Mide antes de afirmar. Un `grep` que devuelve cero no prueba ausencia:
  acótalo a las zonas que mandan (`cultura/`, `tools/`, `tests/`, `iskvw/`,
  `docs/`) y **nunca** sobre `/home/mak` entero ni con `-L`: hay un montaje
  FUSE de OneDrive y un SSD, y un `find` así estuvo tres horas al 36% de CPU.
- Si lanzas algo en background, revisa `ps` antes de cerrar el tema. Matar la
  tarea no mata al hijo.
- No borres nada. No hay una sola ganancia de disco segura: eso ya se midió y
  está en el handoff.
- No toques IRIS data, `iskvw/datos/*`, bases ni servicios.
- No commitees ni pushees sin autorización explícita del operador.
- Usa `PYTHONDONTWRITEBYTECODE=1` y `-o addopts=` para pruebas focales.
- Corre el carril completo solo antes de publicar, no en cada iteración.

## Salida

Empieza con una etiqueta exacta: `DEFECTS_FOUND` o `NO_DEFECTS_FOUND`.

Por cada defecto: qué es, la reproducción medida, qué commit lo introdujo, y la
corrección mínima. Ordenados por gravedad.

Si no encuentras ninguno, dilo. Un "todo bien" honesto vale más que un hallazgo
inflado — pero antes de decirlo, muestra qué atacaste y con qué medición, para
que se pueda juzgar si buscaste de verdad.
