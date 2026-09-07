# Estado técnico verificado — corte 2026-09-06, 18:37 hora de Santiago

Reproducible con `evidencia/prueba_estado.sh`; salida en `evidencia/SALIDA_PRUEBA_ESTADO.txt`.
Solo lectura: la prueba hace GET y un POST de control cuyo 404 es la comprobación
de que la superficie servida no acepta escritura. No modifica nada de MAK.

Cada afirmación lleva una de estas tres etiquetas, y la distinción es el punto
de este documento:

- **OBSERVADO** — medido hoy, con archivo, ruta y cifra.
- **NO PROBADO** — no se midió; puede ser cierto o falso.
- **INEXISTENTE DEMOSTRADO** — se buscó la función concreta y no existe, o
  existe y su propio contrato excluye lo que se afirmaría.

---

## 1. Corrección mayor: hay dos universos distintos y no deben mezclarse

La v1 y la auditoría trataron el archivo de IRIS como un solo cuerpo. Son dos,
con fuentes, identificadores y fechas distintos.

| | **Universo A — `iskvw`** | **Universo B — `portfolio-editor`** |
|---|---|---|
| Ruta | `~/iskvw/datos/` | `~/plataforma/director_runs/portfolio-editor-20260808/` |
| Qué es | Atlas de lectura visual por máquina | Bandeja de curaduría con decisión humana |
| Inventario | `archivo.json`: 2.034 piezas, 5.812 vínculos, generado `2026-08-29T10:38:17` | `PORTFOLIO_INBOX.json`: **7.044 ítems**, 7.023 con asset, `status: not_public`, generado `2026-08-07T21:19:13` |
| Campo activo | `campo.json`: 219 piezas, mtime `2026-09-02T12:52:53` | 68 ítems con decisión, sobre 7.044 |
| Identificadores | `vola`, `campo-motor-diagnostico`, … | `18122826199703813.mp4`, `stories.json:1`, … |
| Qué aporta | color, estilo, descripción automática, coordenadas | selección, descarte, reversión, clasificación autoral |

**No comparten identificadores.** Sumar sus cifras, o describir las 219 piezas
del universo A con las decisiones del universo B, sería un error. Los expedientes
de la v2 citan cada universo por separado y con su fecha.

---

## 2. Universo A — lo que la máquina ve

**OBSERVADO.** `archivo.json`, `fuente: "todo"`, generado 2026-08-29T10:38:17:
2.034 piezas y 5.812 vínculos. Por clase: 1.826 `obra`, 208 `codigo`.

**OBSERVADO.** `campo.json`, mtime 2026-09-02: 219 piezas, **219 de 219 con
percepción de máquina**, 478 piezas filtradas por un filtro declarado en
`meta.filtro`, y `vecindad_conservada = 0.4855`.

**OBSERVADO — tipificación completa, que suma 219.** La v1 y la auditoría
dijeron "134 obras y el resto contexto u otros". El resto no es homogéneo y
aquí está entero:

| tipo | n | | tipo | n |
|---|---:|---|---|---:|
| `obra` | 134 | | `flyer_evento` | 2 |
| `foto_evento` | 40 | | `pantalla` | 1 |
| `tatuaje` | 28 | | `dibujo` | 1 |
| `otro` | 6 | | `meme` | 1 |
| `logo` | 4 | | `dibujo digital` | 1 |
| | | | `ficha_sustancia` | 1 |
| | | | **TOTAL** | **219** |

**Precisión que la auditoría pidió y que corresponde hacer:** `tipo: "obra"` es
una **tipificación de origen del pipeline, no una validación autoral**. Que 134
piezas estén marcadas `obra` no significa que el artista las haya reconocido como
obra suya. La validación autoral existe, pero está en el universo B y sobre otro
inventario. Ninguna postulación de la v2 dice "134 obras del artista": dice
"134 piezas tipificadas como obra en el campo activo".

**OBSERVADO.** `curaduria.json` registra **0 decisiones**, con mtime
`2026-08-01T09:34:34`. Es un archivo anterior al propio campo activo.

---

## 3. Universo B — la corrección más importante de toda la auditoría

La v1 afirmó, y la auditoría reprodujo, que "el bucle de decisión humana no se ha
ejercido" y que había "cero decisiones humanas registradas". **Esa afirmación es
falsa como enunciado general.** Era verdadera únicamente respecto de
`curaduria.json`.

Rastreando la función concreta —`_portfolio_select_unlocked` en
`~/cultura/mak_plataforma/hub.py`, líneas 2059-2160— aparece un subsistema de
persistencia completo, y sus archivos tienen datos.

**OBSERVADO — `selections.jsonl`, 87 filas:**

- **68 ítems distintos**, en **14 sesiones**,
  entre **2026-08-07T21:28** y **2026-09-02T02:53**.
- `descartar` **65** · `seleccionar` **13** · `deseleccionar` **9**.
- **65 de los 65 descartes** llevan `reason_code: "no_es_obra"` y
  `decision_scope: "record"`.
- 75 filas con `work.provider: "human"`.

Tres cosas se siguen de esto y las tres corrigen a la v1:

1. **La persistencia está implementada y en uso.** Hay escritura en JSONL más
   un asiento en el ledger común con control de unicidad
   (`_portfolio_ledger_append_unique`). No es un contrato sin ejercer.
2. **La reversibilidad está ejercida, no sólo declarada.** Nueve
   `deseleccionar` son nueve reversiones reales de una decisión previa.
3. **La validación autoral de obra / no-obra existe y se ejerció 65 veces.**
   `reason_code: "no_es_obra"` es exactamente el juicio "esto no es obra mía",
   hecho por una persona y registrado con su motivo.

**OBSERVADO — `classifications.jsonl`, 103 filas:** campos `triage` 91,
`context_kind` 18, `ownership` 16, `purpose` 16, `nature` 12, `lane` 11,
`format` 6. Estado: **100 `human_draft` y sólo 3 `human_confirmed`**.
`promotion: "none"` en las 103.

**OBSERVADO — `common_ledger.jsonl`:** 477 filas, **123 en dominio `iskvw`**.
Tipos: 100 `decision`, 21 `evidence`, 2 `reject`. Acciones: 67 `reject`,
47 `curate`, 7 `archive`, **2 `expose`**. Propietario: 94 `human`, 7 `MAK`.

**OBSERVADO también — y esto acota el entusiasmo:** el inventario está en
`status: not_public`, las clasificaciones están en `promotion: "none"`, y sólo 3
de 103 llegaron a `human_confirmed`. La compuerta de promoción a público existe,
funciona y **está deliberadamente sin cruzar**. El trabajo curatorial ocurrió;
la publicación no.

---

## 4. La exportación: qué existe y qué no, con el nombre de la función

La v1 dijo "no existe exportación". Hay que ser más preciso, porque existe una
pieza y no hace lo que se necesita.

**OBSERVADO — el editor.** `editor.html` línea 1092: *"its only output is a
download"*. Líneas 2784-2786: un `Blob` `application/json` entregado con
`a.download`. La superficie servida rechaza POST (404, comprobado). Es decir:
el editor exporta **datos**, no un portafolio.

**OBSERVADO — sí existe un compilador de dossier.** `~/tools/compile_portfolio_dossier.py`,
con motor en `~/flujo/src/flujo/knowledge/portfolio_dossier.py` (55.820 bytes,
mtime 2026-09-02). Se cargó y se ejercitó su contrato sin tocar datos reales:
produce `mak-portfolio-dossier-v1` y **rechaza entradas vacías con 22 errores de
validación**. Es código vivo y validante, no un esqueleto.

**INEXISTENTE DEMOSTRADO — pero no hace de archivo a portafolio.** Su propio
contrato lo excluye: consume `mak-product-plan-v1` + `mak-practice-evidence-state-v1`
y su docstring declara que *"no importa un productor de planes, no lee un
archivo, no abre una base de datos y no publica un asset"*.

**La brecha, entonces, queda definida con precisión quirúrgica y es esto:**

> No existe la pieza que tome el inventario más las decisiones humanas ya
> registradas y produzca un artefacto de portafolio publicable. El editor
> exporta datos. El compilador de dossier exporta un documento desde un plan.
> Entre el archivo decidido y la salida pública no hay nada.

Eso, y no "construir IRIS", es lo que las tres postulaciones piden financiar.

---

## 5. Lo que sigue sin probarse

**NO PROBADO** — que el instrumento sirva a alguien distinto de su autor; que
mejore la comprensión de un archivo; que sea accesible según norma; que soporte
más de un usuario. No hay medición con personas y ninguna postulación la afirma.

**INEXISTENTE DEMOSTRADO** — superficie pública: el servicio escucha en
`127.0.0.1:8900` y no está expuesto.

**NO AUDITABLE** — las mejoras de importación/reimportación/exportación de IRIS
y el ciclo de decisiones de PUPILA que se encargaron a otros agentes. No hay
prueba integrada, fechada y reproducible sobre MAK. **Corte de este documento:
2026-09-06.** Nada de eso se cuenta como capacidad y nada de eso se presupuesta
como ya hecho. Tabla de situación en `MATRIZ_REQUISITOS.md`, sección 6.
