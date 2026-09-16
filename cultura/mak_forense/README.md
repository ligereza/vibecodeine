# mak_forense — procedencia de un registro

Dado un conjunto de anotaciones agrupadas por jornada, decide cuáles son un
hecho nuevo y cuáles son el rastro de otra anotación. Marca; nunca borra.

Nace del análisis de `Testeo 2025` (16-sep-2026). El hallazgo no fue un error
de un voluntario: fue la forma de la herramienta. **Cada jornada se armaba
copiando la hoja del evento anterior y sobrescribiendo filas.** Lo que no
alcanzaba a sobrescribirse quedaba como muestra que nadie testeó.

La prueba está en las fechas: cada bloque ajeno viene de la hoja
inmediatamente anterior del calendario. `Psiquiátrico 1603` copió de
`DAME 1503`, **un día antes**, 73 anotaciones. `Mamisonga 8225` copió de
`Cachorros 18125`, que es literalmente el evento previo, y después alguien
arrastró el bloque hasta la fila 989: de 639 filas, 9 son muestras reales.

## Por qué es un módulo y no un script

Porque la forma del problema se repite donde sea que una persona registre
hechos bajo urgencia:

```
anotación + otra anotación de otra fecha → ¿son la misma?
                                          → y si lo son, ¿cuál es la copia?
```

Lo que cambia por área es qué campos definen "la misma anotación". Eso se pide
explícito; el resto es el mismo.

## Los detectores

| patrón | qué mide | certeza |
|---|---|---|
| `bloque_periodico` | contenidos que vuelven cada P posiciones | confirmado |
| `lote_contiguo` | anotaciones idénticas una debajo de otra | probable — **no se descuenta** |
| `repeticion_dispersa` | repite sin geometría que lo explique | pendiente |
| `tramo_ajeno` | tramo contiguo que ya estaba en otra jornada | según corrobore la fecha |
| `encabezado_intercalado` | encabezado en medio del grupo: costura de un pegado | confirmado |
| `registro_en_evento_futuro` | se guardó antes de que el evento ocurriera | confirmado |
| `registro_en_evento_pasado` | se guardó mucho después | confirmado |
| `fuera_de_jornada` | captura lejos del cúmulo horario de su grupo (MAD) | probable |
| `rafaga_no_humana` | cargas demasiado seguidas para tipearse | confirmado |

### La distinción que costó cara

Contar filas idénticas y llamarlas duplicadas infla el daño. De las 904
repeticiones del corpus, 645 eran un pegado real (periodo 22) y **139 eran
filas contiguas**: `DAME 1503` tiene 37 de sus 39 pegadas una debajo de otra,
que es exactamente como se ve una mesa donde llegaron cinco ketaminas seguidas
con el mismo reactivo y el mismo color.

**La geometría distingue lo que el contenido no puede.** Por eso
`lote_contiguo` existe como patrón propio y se marca `probable`, no se resta.

### La dirección de una copia

En el original el tramo *es* prácticamente todo su contenido propio; en la
copia queda diluido entre las anotaciones nuevas que sí se hicieron. El tramo
de 71 filas pesa 0,96 del contenido distinto de `DAME 1503` y 0,62 del de
`Psiquiátrico 1603` — la copia es Psiquiátrico, que además es la hoja del día
siguiente.

El peso decide y **la fecha corrobora**. Si coinciden, `confirmado`. Si solo
hay una señal, `probable`. Si se contradicen, `pendiente` con las dos
hipótesis escritas: copiar del futuro no existe, y las fechas del corpus salen
del nombre de la hoja.

## Lo que XIO-RD puede detectar y una planilla no

Una hoja de cálculo no sabe cuándo se escribió una celda. Una app sabe
exactamente cuándo se guardó una muestra. Con eso, los dos errores que se
anticipan dejan de ser invisibles:

- el voluntario elige una jornada que **todavía no pasa** → `registro_en_evento_futuro`
- el voluntario elige una jornada **anterior** de la lista → `registro_en_evento_pasado`
- la jornada se llenó, nadie alcanzó a cargar, y al final alguien volcó todo
  de una → `rafaga_no_humana`

`fuera_de_jornada` cubre el caso sin fecha declarada: el grupo igual tiene su
horario implícito, y la captura que no cae ahí se separa sola. Usa mediana y
MAD, no promedio: si el grupo ya trae varias cargas erradas, el promedio se
corre hacia ellas y deja de verlas.

## El contrato

1. **Nada se descarta.** Un hallazgo marca registros que siguen en la fuente.
   La exclusión es una decisión humana posterior — mismo contrato que
   `triangular.py` con `revision_humana: pendiente`.
2. **La certeza se declara.** `confirmado` / `probable` / `pendiente` separan
   lo que la matemática probó de lo que sugiere.
3. **El análisis declara lo que no pudo ver.** `Cobertura.limites` existe
   porque el detector original solo comparaba hojas de una misma corrida —
   una hoja de 2025 copiada de una de 2024 le era invisible, y el informe no
   lo decía. Un número sin su cobertura se lee como un total.

## Uso

```bash
python3 cultura/mak_forense/forense.py testeos                  # la planilla heredada
python3 cultura/mak_forense/forense.py muestras                 # lo que carga XIO-RD
python3 cultura/mak_forense/forense.py jsonl ARCHIVO \
    --grupo CAMPO --contenido C1,C2,C3 [--instante CAMPO] [--fecha CAMPO]
```

Todo en solo lectura (`sqlite3 ... mode=ro`). `--json SALIDA` deja el informe
completo con la evidencia de cada hallazgo.

### Integracion con triangular

cultura/mak_curatoria/triangular.py usa este mismo motor cuando arma su cola
de investigacion. Si una ficha fue percibida mas de una vez, la cola usa la
version mas reciente pero conserva junto a ella los ids y fechas observados,
los hallazgos de procedencia y el estado revision_humana: pendiente.

Asi una re-percepcion no reemplaza silenciosamente la historia ni se confunde
con una confirmacion. La cola sigue siendo una pregunta de investigacion; el
analisis solo aporta evidencia y nunca escribe en la base RD.

## Archivos

- `registro.py` — `Registro`, `Hallazgo`, `Cobertura`, `Analisis`
- `patrones.py` — los detectores: funciones puras, sin red ni base de datos
- `fuentes.py` — adaptadores de solo lectura, cada uno declara sus límites
- `forense.py` — CLI
- `tests/test_forense.py` (en la raíz del repo) — 16 tests

Las constantes de `patrones.py` no son preferencias: cada una tiene su
medición citada en el docstring. `MINIMO_TRAMO = 6` porque con 4 aparecía un
falso positivo real — tres filas de MDMA «tesla rosada» cuyo supuesto origen
era 28 días posterior y cuyos resultados eran distintos entre sí.
