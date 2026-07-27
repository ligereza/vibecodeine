# MAPA de iskvw — por dónde se entra

La línea `iskvw` es **la curatoría y la obra**: el archivo del artista y su cara
visible. Esto dice qué es cada archivo y en qué orden se leen. Si llegaste acá
sin contexto, leé de arriba hacia abajo y no hace falta nada más.

RD tiene su equivalente en `docs/rd/MAPA_RD.md`. Las reglas de conducta de
cualquier agente están en `CLAUDE.md`, en la raíz.

---

## Los cuatro documentos, en orden de lectura

| archivo | qué responde | cuándo se lee |
|---|---|---|
| `README.md` | qué es esta carpeta, en veinte líneas | siempre, primero |
| `CONTRATO.md` | **qué no se puede romper**: las cinco reglas que cumple cualquier piel | antes de escribir una piel |
| `DIRECCION.md` | **hacia dónde va**: las once decisiones de diseño, con el motivo de cada una | antes de proponer nada |
| `PROMPT_ESTETICA.md` | lo que se le pega a un agente externo para pedir una estética nueva | al pedir una piel |

La diferencia entre los dos del medio: el contrato es un límite, la dirección es
un rumbo. Una piel puede cumplir el contrato y estar en contra de la dirección.

Las once decisiones de `DIRECCION.md` **ya se discutieron con dos agentes y
sobrevivieron**. No se re-derivan ni se re-abren: se leen y se cumplen.

## Las tres capas

```
  datos/obras.json     CONTENIDO   no cambia cuando cambia el estilo
  CONTRATO.md          CONTRATO    qué mostrar y qué no se puede afirmar
  piel/<la-que-sea>/   PIEL        se despega entera y se reemplaza
```

La piel **consume** los datos y **cumple** el contrato. No los edita, no agrega
campos, no inventa. Si una piel necesita un dato que no está, ese dato se agrega
primero al contenido — nunca se cablea en la piel, porque entonces la piel deja
de ser reemplazable, que es todo el punto de esta carpeta.

`datos/ESQUEMA.md` dice exactamente qué hay en `obras.json` y qué campo puede
faltar. Un campo que no conocés es un campo que ignorás: por eso una piel vieja
sigue funcionando cuando la curatoría agrega conceptos o técnica.

## Las pieles

| carpeta | qué puerta es | estado |
|---|---|---|
| `piel/terminal/` | la puerta **CV**: legible, mapeada, con filtros, treinta segundos | funciona, verificada en navegador con cero errores de consola |
| — | la puerta **obra**: operativa, sin mapa, se habita | por construir, según `DIRECCION.md` |

No hay que elegir entre CV y obra: las dos leen los mismos datos. Lo único que
se elige es **cuál abre por defecto**, y eso es decisión del autor.

## La condición que manda sobre todo

`DIRECCION.md` punto 11: nada puede quedar cableado. El autor cambia de lenguaje
visual seguido, y una pieza que sólo sirve para la estética de hoy es una pieza
que hay que tirar mañana.

En concreto: los valores que dan carácter —la constante del resorte al bajar y
al subir, los ciclos por minuto del pulso, los umbrales de las tres velocidades,
los modos del drop— viven en **configuración editable**, como `data/rd_packs.json`
del lado de RD. No adentro del bundle.

La prueba de que se cumple, y es la única que vale: **un agente externo tiene que
poder producir una piel nueva leyendo sólo estos documentos, sin ver el código de
la anterior.**

## Cómo se cambia el estilo

1. Se le pasan a un agente externo `PROMPT_ESTETICA.md` + `CONTRATO.md` +
   `DIRECCION.md` + `datos/ESQUEMA.md`.
2. Lo que devuelva va a `piel/<nombre-nuevo>/`.
3. Se abre en un navegador. **El veredicto es abrirla, no leerla**: una piel que
   compila limpio puede tirar ocho errores de consola, ya pasó.
4. La piel anterior queda donde está. Cambiar de estilo no borra el anterior.

## Lo que está abierto

- **El sustrato** (PR #338): un contrato de PIEZAS y VÍNCULOS que no sabe si las
  obras son del artista o informes de MAK, para que una piel sirva a las dos
  fuentes. Es una propuesta y **espera decisión del autor**: fusionar su obra con
  los ensayos de MAK en un solo archivo puede estar mal para un portafolio.
- **Qué piel abre por defecto.** Decisión del autor, no técnica.
