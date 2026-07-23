# DB de productoras RD -- estado de avance (v1)

Entregable en español real, UTF-8 (esta carpeta no es `context/` operativo,
así que no aplica la regla ASCII-only). Generado 2026-07-23 a partir de:
PR #210 (feat/candidatos-db-curatoria, docs/rd/candidatos_curatoria/candidatos_db.jsonl,
970 obras de 1731 fichas curadas) + 2 posts IG del día
(C:/rd/AUTOMATIZACION/input_ig_DbG7Z2qCPrl_2.jpg, input_ig_DbI68vBCSTc.jpg).

Fuente de verdad = data/productoras/*.json (editable a mano por el usuario).
Este doc es una lectura de esos archivos para que el usuario corrija fila por
fila. No hay dato inventado: lo no confirmado dice needs_confirmation o
PENDIENTE.

## Cómo se construye la DB (mecánica)

1. `data/productoras/<slug>.json` = un archivo por productora, campo
   `fuente_datos`/`fuente` por dato (nunca un campo global "confiar en todo").
2. `py -m flujo rd-db build` proyecta esos json + `knowledge/venues/*.yaml` a
   `data/rd.db` (sqlite regenerable, gitignored). Tablas: productoras,
   productora_tipos, productora_venues, productora_logos.
3. El campo `eventos` (nuevo en esta entrega) vive en el json pero aún no
   tiene tabla sqlite propia -- es metadata de registro, no queryable vía
   `rd-db` todavía. Extensión pendiente si se necesita consulta SQL.
4. Logos van en `knowledge/logos/<slug>.yaml` (workflow de vectorización,
   `logo_clean_lab`); el json de la productora solo referencia el id.

## Cobertura de esta entrega

4 productoras del PR #210 (match_ratio 1.0 contra vocabulario canónico) +
Dame (evento nuevo de hoy, ya existía el archivo). Piknic y Dame además
llevan el evento activo captado hoy.

| Productora | Confianza match | Logo | Venue | Eventos | Fuente principal |
|---|---|---|---|---|---|
| Sundeck | alta (1.0, 2 obras) | **FALTA** (no_encontrado) | Espacio Riesco -- candidato sin confirmar | 1 pasado (17-ene-2026, needs_confirmation) | PR #210 obra_45bae8c3f6 / obra_99ef9a1f8a |
| Piknic Electronik | alta (1.0, 1 obra) | 2 candidatos sin copiar (logo-piknic.png, piknic.png) -- **FALTA copiar+vectorizar** | Parque Padre Hurtado -- confirmado | 1 ACTIVO_VENTA (12-sep-2026) + 1 pasado sin fecha exacta | IG 2026-07-23 + PR #210 obra_25745a1c93 |
| Creamfields | alta (1.0, 1 obra) | yaml existente (source_needed) + 2 candidatos imagen sin copiar -- **FALTA vectorizar** | Club Hípico -- candidato sin confirmar; Espacio Riesco es ejemplo de escala, no dato | 1 pasado (11/12-oct-2025) | PR #210 obra_0304b8fe9a |
| OpenKlub | alta (1.0, 1 obra) | **FALTA** (no_encontrado) | Central Cultural -- candidato sin confirmar (nombre genérico, dudoso) | 1 pasado sin año confirmado (6-feb) | PR #210 obra_7879d3d141 |
| Dame | n/a (identidad ya en repo, no en match PR #210) | **FALTA** (no_encontrado) | Basel Venue Santiago -- confirmado | 1 ACTIVO_ANUNCIADO (Jeff Mills 30yr, 20-nov-2026) | IG 2026-07-23 |

## Huecos explícitos (cola de trabajo)

FALTA logo (sin ningún candidato en curatoría):
- Sundeck
- OpenKlub
- Dame

FALTA copiar/vectorizar (candidato existe pero no está en knowledge/logos/):
- Piknic Electronik: `FLYER/logo-piknic.png` (obra_bd9fc5daf8), `piknic.png` (obra_5add3c6113)
- Creamfields: `CREAMFIELDS/326185116_..._n.png` (obra_6d0ccb045c), `CREAMFIELDS/Comp 1 (0-00-30-04).png` (obra_defa9d8353)
  (yaml `knowledge/logos/creamfields.yaml` ya existe, status=needs_vectorization)

FALTA confirmar venue (venue_crudo de una sola obra, no verificado):
- Sundeck -> Espacio Riesco (obra_45bae8c3f6)
- Creamfields -> Club Hípico, Santiago (obra_0304b8fe9a)
- OpenKlub -> Central Cultural (obra_7879d3d141, nombre genérico, sospechoso)

FALTA confirmar fecha/año (fecha_cruda ambigua o sin año):
- Piknic -> "MAR 28" sin año (obra_25745a1c93)
- OpenKlub -> "VIERNES_06FEBR" sin año (obra_7879d3d141)

Identidad propia RD (EVENTOS@REDUCIENDODANO.CL / RD / REDUCIENDODANO.CL):
EXCLUIDA a propósito del match de productoras por el PR #210 (12 obras,
ver INFORME_CANDIDATOS.md sección "Identidad propia"). Es la ONG misma
organizando/co-organizando, no una productora tercera. No se creó archivo
en data/productoras/ para esto; si se necesita modelar como entidad
separada, es una decisión de producto a tomar por el usuario, no un dato
a inferir.

## Eventos Chile: núcleo de esta entrega

Solo 2 eventos entraron con evidencia primaria verificable HOY (imagen +
fecha + venue legibles en el post):

1. **Piknic Electronik Santiago** -- 12 sep 2026, Parque Padre Hurtado,
   lineup PARTIBOI69, co-org GLOVOX. Fuente: C:/rd/AUTOMATIZACION/input_ig_DbG7Z2qCPrl_2.jpg.
2. **Dame -- Jeff Mills 30 years** -- 20 nov 2026, Basel Venue Santiago.
   Fuente: C:/rd/AUTOMATIZACION/input_ig_DbI68vBCSTc.jpg.

Los demás eventos listados arriba vienen de fichas de curatoría (PR #210,
fechas crudas sin normalizar en varios casos) y están marcados pasado o
needs_confirmation -- NO se investigó activamente su estado actual.

## Backlog de research sembrado (MAK)

`docs/rd/backlog_semilla_rd.jsonl` (mismo patrón que
`cultura/mak_plataforma/backlog_semilla.jsonl`, pero fuera de `cultura/`
porque esa carpeta está bloqueada hasta merge de sus propios PRs). 1 tema
por productora: eventos activos + últimos 5 eventos en Chile, fuentes IG
oficial + ticketeras chilenas (puntoticket, passline, ticketmaster) + prensa.

## Verificación de esta entrega

- `py -m compileall src/flujo`: no se tocó código Python (solo data/*.json
  y docs/), aplica igual por regla del repo.
- `py -m pytest tests/ -q`: corre igual, valida que el nuevo campo `eventos`
  en los json no rompe `build_rd_db` (lee solo claves conocidas, ignora las
  demás). Verificado también con los acentos ya aplicados: `build_rd_db()`
  ejecutado directo contra los json en UTF-8 sin fallar.
- `py -m flujo verify`: idem.

## Nota de alcance

La regla ASCII-only del repo aplica solo a `context/` operativo
(CLAUDE.md, context/LAST_HANDOFF.md, context/SESSION_STATE.json). Los
entregables -- como este documento, los json de productoras y el backlog
de research -- van en español real, UTF-8 sin BOM.

## Presentación visual

`db_productoras.html` (scratchpad de sesión) -- tabla interactiva con la
misma información de este doc, huecos en rojo, para revisión fila por fila.
