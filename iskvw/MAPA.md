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
  datos/
    ESQUEMA.md         qué campos tiene obras.json
    obras.json         8 piezas generativas del repo (VOLÁ, Campo, Cenefa…)
    campo.json         219 obras del archivo, con posición medida y capas
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
```

## Qué se edita a mano y qué se genera

**Se edita** (y por eso viaja en el repo):
`data/iskvw_campo_filtro.json` — qué obras entran, hoy `posts` y `reels`.
`data/iskvw_capas.json` — qué capas corren.
`data/iskvw_librerias.json` — qué librerías se vendorizan.

**Se genera** y no se toca a mano: `datos/campo.json`,
`piel/trazos/_indice.json`, `piel/lib/*.js`. `datos/archivo.json` se genera y
**no se versiona**.

## Lo que falta, y de quién es

- **La dirección**: qué es este archivo como obra. **Del usuario.**
- **Qué son las 8 piezas de `obras.json`** frente a las 219 del archivo. **Del usuario.**
- La piel `terminal` sigue leyendo sólo `obras.json`: no ve el archivo.
- 34 reels sin percibir en MAK. Ya están declarados en el filtro: entran solos.
