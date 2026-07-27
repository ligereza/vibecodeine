# El archivo, en una sola forma

> **PROPUESTA, no contrato cerrado (2026-07-27).** Está probada contra las dos
> fuentes reales —993 piezas y 3157 vínculos salieron bien— pero **no se congeló
> el archivo generado a propósito**. MAK está percibiendo el archivo del artista
> ahora mismo, y cuando termine cada obra va a traer conceptos, técnica y
> vínculos medidos. Fijar la forma antes de ver eso sería delimitar con lo que
> hay hoy, que es lo más pobre que va a haber.
>
> Se genera cuando se necesita. `iskvw/datos/archivo.json` NO se versiona.

Este documento es **el conector**. Define qué recibe una piel, sea lo que sea que
haya detrás.

Hoy detrás hay dos cosas que no se parecen en nada:

- **Las obras del artista**: pocas, con datos ricos —título, año, técnica,
  descripción— y **ninguna relación explícita**. Sólo etiquetas.
- **El micelio de MAK**: casi mil nodos con **3141 relaciones medidas** entre sí,
  pero apenas un título por nodo.

Una tenía que ver la otra y no podía. Cada piel terminaba escribiendo su propio
lector, y una piel nueva servía para una sola fuente. Con esta forma, una piel
pide *"dame las piezas y sus vínculos"* y siempre recibe lo mismo.

**Quien dibuja no necesita saber de dónde salió.** Ese es todo el punto.

---

## La forma

```json
{
  "version": 1,
  "fuente": "obras",
  "generado": "2026-07-27T05:00:00",
  "piezas": [ ... ],
  "vinculos": [ ... ],
  "meta": { }
}
```

### Una pieza

```json
{
  "id": "tatuaje-romero",
  "titulo": "Tatuaje de ramas de romero",
  "clase": "obra",
  "fecha": "2020-11",
  "resumen": "Una o dos frases.",
  "etiquetas": ["botánico", "línea"],
  "peso": 3,
  "medio": { "tipo": "imagen", "src": "obras/romero.jpg" },
  "estado": "publicada",
  "extra": { }
}
```

| campo | obligatorio | qué es |
|---|---|---|
| `id` | **sí** | Identificador estable. Es lo que usan los vínculos |
| `titulo` | **sí** | Lo que se muestra. Con tildes y eñes |
| `clase` | **sí** | De qué familia es: `obra`, `informe`, `codigo`, `evento`… |
| `fecha` | no | `AAAA`, `AAAA-MM` o `AAAA-MM-DD`. **Ausente = no se sabe**, no es cero |
| `resumen` | no | Una o dos frases |
| `etiquetas` | no | Lista de textos. Puede venir vacía |
| `peso` | no | Cuánta materia tiene la pieza. Sirve para el tamaño. Por defecto 1 |
| `medio` | no | `{tipo, src, poster}`. `tipo`: `imagen`, `video`, `texto`, `ninguno` |
| `estado` | no | `publicada`, `anunciada`, `borrador`. **`anunciada` = todavía no existe** |
| `extra` | no | Cualquier cosa propia de la fuente. **Una piel que no lo entiende lo ignora** |

### Un vínculo

```json
{ "de": "tatuaje-romero", "a": "hoja-seca", "peso": 0.78, "clase": "semantico" }
```

| campo | obligatorio | qué es |
|---|---|---|
| `de`, `a` | **sí** | `id` de dos piezas |
| `peso` | **sí** | Entre 0 y 1. Cuán fuerte es el vínculo |
| `clase` | no | `semantico` (medido), `etiqueta` (comparten una), `manual` |

Los vínculos **no tienen dirección**: `de` y `a` son intercambiables.

---

## Las cinco reglas

Son las mismas del contrato y no se negocian. Repetidas acá porque quien escribe
una piel lee este archivo:

1. **Ninguna pieza afirma un dato que no tiene.** Sin fecha, no se inventa una.
   Un contador que dice doce muestra doce. Una barra que no mide nada no va.
2. **Todo lo visible en castellano correcto**, con tildes y eñes.
3. **Abre sin internet.** Sin CDN, sin fuentes remotas, sin analítica.
4. **Se ve en un teléfono.** No igual: visible.
5. **La piel se borra y se pone otra sin tocar los datos.**

Y una que sale de esta forma:

6. **Campo que no conocés, campo que ignorás.** Cuando la curatoría agregue
   conceptos y técnica por obra, van a llegar dentro de `extra`. Una piel vieja
   tiene que seguir funcionando el día que eso pase.

---

## Cómo se genera

```bash
py tools/gen_archivo_iskvw.py --fuente obras    # las obras del artista
py tools/gen_archivo_iskvw.py --fuente micelio  # lo que MAK relacionó
py tools/gen_archivo_iskvw.py --fuente todo     # las dos, en un solo archivo
```

Sale a `iskvw/datos/archivo.json`. Una piel lee ESE archivo y nada más.

**La fuente `obras`** deriva los vínculos de las etiquetas compartidas: dos obras
con etiquetas en común quedan unidas, con peso según cuántas comparten. Es lo
único que hay hoy, y se dice: esos vínculos son `clase: "etiqueta"`, no
`semantico`, porque nadie midió que se parezcan — comparten una palabra.

**La fuente `micelio`** trae los vínculos que MAK midió de verdad, por cercanía
entre los textos. Ahí `clase` sí es `semantico`.

Cuando la percepción del archivo termine, las obras van a tener las dos cosas: sus
datos y sus vínculos medidos.
