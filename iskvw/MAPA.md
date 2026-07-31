# iskvw · qué hay acá

Mapa **factual**: qué archivo es qué, qué comando genera qué, y los números
medidos el 2026-07-27. La dirección artística NO está acá y no la escribe un
agente — eso ya se intentó y el usuario lo rechazó con razón (ver la decisión
"un loop no escribe documentos" en `context/LAST_HANDOFF.md`).

Si algo de este archivo no calza con lo que ves, confiá en el repo y corregilo
en el mismo PR que lo detecte.

## El sitio en vivo

`iskvw.cl` → GitHub Pages de este repo, publicado por
`.github/workflows/publicar_iskvw.yml` en cada push a `main` que toque `iskvw/`.
Sube **sólo `iskvw/`**: nada de RD, MAK ni xio. La raíz del sitio es la piel
`campo`.

## Los archivos

```
iskvw/
  CONTRATO.md          qué debe cumplir cualquier piel para no mentir
  ESQUEMA_ARCHIVO.md   la forma piezas+vínculos que sirve a las dos fuentes
  PROMPT_ESTETICA.md   lo que se le pasa a un agente externo para pedir una piel
  README.md            índice de esta carpeta
  MAPA.md              este archivo
  editor.html          el panel de curaduría: se abre, se edita, se descarga
  datos/
    ESQUEMA.md         qué campos tiene obras.json
    obras.json         8 piezas generativas del repo (VOLÁ, Campo, Cenefa…)
    campo.json         219 obras del archivo, con posición medida y capas
    curaduria.json     la mano del artista sobre lo percibido
    tablero.json       qué mejoras están encendidas
  piel/
    campo/             la piel viva: el organismo. Es la raíz del sitio
    terminal/          piel anterior. Lee sólo obras.json (8 piezas)
    trazos/            208 SVG + _indice.json. La obra que puede viajar
    lib/               librerías vendorizadas: tsne, trazo, gestos, distancia
```

## Los números, medidos

| | |
|---|---|
| obras en el campo | **219**, todas de `posts/` |
| con trazo publicado | **208** (las 11 restantes son video o sin contraste) |
| capas | `tilde` en 219, `trazo` en 208 |
| vecindad conservada | **48,6 %** — lo que la proyección puede afirmar |
| piezas de `obras.json` | 8 |

`vecindad_conservada` es el número que sostiene el campo: de los vecinos reales
de cada obra en 768 dimensiones, qué fracción sigue siendo vecina en el plano.
Si baja, lo que el campo afirma se debilita y hay que decirlo.

## Los comandos

```bash
# el campo: posiciones medidas desde los embeddings del micelio (necesita MAK)
py tools/gen_campo_iskvw.py --vectores <v.json> --meta <m.json>

# el índice de trazos, para que la piel no pida lo que no existe
py tools/gen_campo_iskvw.py --indice-trazos iskvw/piel/trazos

# las capas: cada una mide algo y lo deja en el campo
py tools/gen_capas_iskvw.py            # correr las activas
py tools/gen_capas_iskvw.py --listar   # qué hay y qué corre

# el contrato unificado: obras del repo + micelio de MAK, una sola forma
py tools/gen_archivo_iskvw.py --fuente todo

# las librerías de la piel, como módulos ESM sin CDN ni build
py tools/vendorizar_iskvw.py

# la curaduría, validada antes de entrar al portón: ids desconocidos o
# duplicados, campos inválidos, svg firmado ausente, diacríticos mutilados
py tools/validar_curaduria.py
py tools/validar_curaduria.py --curaduria <descarga>/curaduria.json
```

## Qué se edita a mano y qué se genera

**Se edita** (y por eso viaja en el repo):
`data/iskvw_campo_filtro.json` — qué obras entran, hoy `posts` y `reels`.
`data/iskvw_capas.json` — qué capas corren.
`data/iskvw_librerias.json` — qué librerías se vendorizan.

**Se edita a mano o con el panel**: `datos/curaduria.json` — la mano del
artista (título, mostrar, abstracción, svg firmado, régimen, y desde
2026-07-31 tres campos opcionales que no cambian nada hasta que se escriben:
**peso** — número > 0, cuánta materia tiene la pieza, desplaza al peso medido
del contrato—, **serie** —etiqueta de agrupación, viaja en `extra.serie`— y
**nota** —la nota del artista, en `extra.nota`, español correcto con tildes).
El panel es `iskvw/editor.html`: una página estática, sin build y sin servidor
propio. Se abre con el repo servido desde la raíz (`py -m http.server`, después
`/iskvw/editor.html`), lee `datos/archivo.json` y si no está `datos/campo.json`,
y su única salida es un **`curaduria.json` que se descarga**: no escribe en
disco, el archivo entra por el mismo portón que todo lo demás. Una pieza que no
se toca **no aparece** en ese archivo — cada id que sale es una decisión.

Tres protecciones del panel (2026-07-31): **importar** un `curaduria.json`
descargado y todavía no commiteado para seguir editándolo (botón en la
cabecera; sin eso, reabrir la página retomaba en silencio la copia vieja del
repo); el navegador **pregunta antes de cerrar** si hay ediciones que no se
descargaron (descargar es lo que marca el estado como a salvo); y un campo por
pieza que el panel **no entiende viaja intacto** en la salida — la misma regla
que el tablero declara para sus valores no booleanos. El circuito completo
—panel → validador → consumidor— está fijado por
`tests/test_curaduria_roundtrip.py`: lo que el panel exporta valida sin
errores y es exactamente lo que `aplicar_curaduria()` obedece.

La misma página tiene el **tablero de mejoras**: `datos/tablero.json`
(`{"version": 1, "mejoras": {…}}`), un interruptor por clave. Las claves las
agrega el agente que trae cada mejora; el editor **no conoce ninguna** y dibuja
las que encuentre, así que una mejora nueva aparece sola sin tocar la página. El
ciclo es **prender → descargar → subir**: hasta que el archivo no entra al repo,
no cambió nada. Cada archivo tiene su propio botón, porque son dos archivos
distintos y un botón único haría que apagar una mejora pareciera guardado
cuando lo que bajó fue la curaduría. Un valor que no es `true`/`false` se
muestra de sólo lectura y viaja de vuelta intacto: el editor no destruye un dato
que no entiende.

**Se genera** y no se toca a mano: `datos/campo.json`,
`piel/trazos/_indice.json`, `piel/lib/*.js`. `datos/archivo.json` se genera y
**no se versiona**.

**La piel pide el sustrato** (2026-07-30): `piel/campo` intenta
`datos/archivo.json` primero —piezas **y** vínculos, así que por ahí entran los
ensayos de MAK con sus conceptos e íconos— y si no está sigue exactamente como
antes con `campo.json` y `obras.json`. Como `archivo.json` no se versiona, hoy
el camino vivo es el respaldo: la degradación es lo normal, no la excepción.

**Los vínculos se dibujan siempre, tenues y por peso** (decisión del usuario,
2026-07-30): la opacidad sale del peso del vínculo, con techo bajo, y van
**debajo** de las obras — la relación es el sustrato, la obra es lo que se mira.
Se descarta todo vínculo que no tenga sus **dos** puntas en cuadro, y los vecinos
se indexan una vez al sembrar: el defecto de recorrer todos los pares en cada
frame está fijado por `tests/test_iskvw_vinculos.py`. Medido sobre las 219
piezas del campo: entre 207 y 615 segmentos por frame según dónde se lea, contra
23.871 pares que costaría el todos-contra-todos. Lo que NO se midió, y por eso
no se afirma: cuadros por segundo en un teléfono.

**Una sesión es una semilla** (2026-07-30, PROYECCION 6.2): el hash dejó de ser
sólo un ancla y ahora codifica la lectura completa,
`#semilla=<pieza>&centro=<y>&escala=<lateral>`, escrita con `replaceState` al
terminar un gesto. Misma semilla + mismo archivo = misma constelación, fijado
por `tests/test_iskvw_semilla.py` contra este mismo archivo. Un enlace viejo de
sólo id sigue funcionando.

## Lo que falta, y de quién es

- **La dirección**: qué es este archivo como obra. **Del usuario.**
- **Si los ensayos se publican en iskvw.cl.** Hoy `archivo.json` no se versiona,
  así que el sitio no los ve. Que la investigación de MAK aparezca junto a la
  obra del artista es una decisión de autoría, y el usuario la dejó **para
  debatir**: el puente está construido y sin usar.
- **Qué son las 8 piezas de `obras.json`** frente a las 219 del archivo. **Del usuario.**
- La piel `terminal` sigue leyendo sólo `obras.json`: no ve el archivo.
- 34 reels sin percibir en MAK. Ya están declarados en el filtro: entran solos.
