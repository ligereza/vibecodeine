# Phase 445 — RD Vite bundle: current source/projection parity gate

## Alcance

Se reanudó el auditoría de consumidores HTML desde `/home/mak/*`, acotando al
bundle standalone de herramientas RD. El objetivo fue confirmar el dueño de
build, la frontera con `App.tsx`, la copia de distribución y si el artefacto
generado refleja el catálogo RD vigente después de la corrección de FRVR,
OpenKlub y Paralelo 89.

No se ejecutó `npm run build:rd`: el build usa `emptyOutDir: true` y podría
sobrescribir el artefacto protegido mientras el entorno Node/Vite sigue
bloqueado. No se instaló nada ni se editó el bundle manualmente.

## Dueño físico

La cadena activa es:

```text
web/rd.html
  -> web/vite.rd.config.ts
  -> web/src/mainRd.tsx
  -> web/src/components/{RdDbPanel,QuotePanel,EventsPanel,IntakePanel}.tsx
  -> web/src/data/rdDbEmbebida.json
  -> web/dist-rd/rd.html
  -> scripts/copy-rd-share.mjs
  -> dist_compartir/herramientas_rd.html
```

`vite.rd.config.ts` mantiene un `outDir` separado (`dist-rd`) y una entrada
separada (`rd.html`), por lo que no se mezcla con el hub ni con el bundle del
Plano. `mainRd.tsx` importa explícitamente las cuatro vistas RD y no importa
`App.tsx`; la mención textual de `App.tsx` es solo documentación de esa
frontera.

## Validación foreground

Comandos ejecutados desde `/home/mak/flujo`:

```text
PYTHONDONTWRITEBYTECODE=1 python3 [static import check]       -> exit 0
node --check web/scripts/copy-rd-share.mjs                      -> exit 0
cmp -s web/dist-rd/rd.html dist_compartir/herramientas_rd.html -> exit 0
node -v                                                        -> v18.20.4
```

La comprobación estática encontró 9 imports y 0 rutas relativas faltantes.
La expresión de imports confirmó `import_App_tsx=False`. Las dos salidas
HTML tienen 467466 bytes, dos etiquetas `script` inline y cero `src` externos.

El dueño fuente ya refleja el estado corregido: `web/src/data/rdDbEmbebida.json`
contiene `Sala Metronomo`, no contiene `paralelo_89`, y contiene las filas
actuales de OpenKlub como productora. El bundle protegido, en cambio, conserva
los marcadores históricos `paralelo_89` (1) y `OpenKlub` (4), no contiene
`Sala Metronomo`, y ambas proyecciones siguen siendo byte-identical con SHA-256
`11eb4eab551129f779caba4734d66736312c270cb700b96e803ad9f5c72fa175`.

## Dictamen

```text
RD_SOURCE_OWNER_GREEN
RD_ENTRY_IMPORT_BOUNDARY_GREEN
RD_SHARE_COPY_EXACT_GREEN
RD_GENERATED_BUNDLE_STALE_RED
```

El problema restante no es una herramienta RD ausente ni una segunda base de
datos que fusionar: es la regeneración del bundle standalone. Como el bundle
actual es una salida generada y el build requiere reparar/usar un runtime Node
compatible, se conserva intacto hasta que exista una validación de build que
no destruya evidencia. El catálogo fuente y el bundle no deben considerarse
paritarios todavía.

## Riesgos y rollback

- Riesgo: `vite.rd.config.ts` tiene `emptyOutDir: true`; un build fallido puede
  tocar `web/dist-rd/` antes de terminar.
- Riesgo conocido de Phase 432: Node 18.20.4 no satisface el requisito de Vite
  7 y falta el binario Rollup Linux; no se repitió una acción destructiva ni se
  instaló dependencia.
- Rollback: no hubo cambios en archivos. Si una futura regeneración produce
  salida incorrecta, restaurar únicamente los dos artefactos generados desde
  su copia preservada y volver a validar `cmp`; mantener el fuente y la base
  de datos sin revertir.

## Siguiente acción

Dejar este gate explícito y continuar el auditoría con el siguiente consumidor
HTML independiente. La regeneración RD queda pendiente de una reparación
autorizada del runtime Node/Vite o de un entorno compatible; no se debe editar
`dist-rd/rd.html` ni `dist_compartir/herramientas_rd.html` a mano.
