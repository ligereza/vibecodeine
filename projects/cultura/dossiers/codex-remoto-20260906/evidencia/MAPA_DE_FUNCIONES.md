# Mapa de funciones: IRIS · JARDINES/WACHUMA · FARMAKSIA/PUPILA

Fecha de verificación local: 2026-09-06. Todo lo que sigue distingue tres cosas
que los briefs recibidos mezclaban: lo que está **implementado en MAK**, lo que
está **documentado**, y lo que es **deseo de arquitectura**.

## 1. Qué existe realmente en MAK

| Proyecto | ¿Está en MAK? | Ruta verificada | Estado observado |
|---|---|---|---|
| IRIS / Atlas Campo del Orden | **Sí, corriendo** | `~/cultura/mak_plataforma/hub.py` (:8900) + `~/iskvw/` | Servicio activo, corpus real, sólo lectura, sin exportación |
| JARDINES interpretativos | **Sí, como base de investigación** | `~/research/jardines_interpretativos/jardines_interpretativos.sqlite` | 22 tablas pobladas |
| WACHUMA | **Sí, monorepo completo** | `~/WACHUMA/` | Vertical web/API/worker/db; contenido en su mayoría sintético o restringido, por declaración propia |
| FARMAKSIA / FARMAXIA | **No** | — | No existe bajo `~` hasta profundidad 4. La evidencia es de Windows y no fue trasladada. |
| PUPILA / XANAX / X-ANA-X | **No** | — | Ídem. Sólo referencias en documentos de traspaso. |

**Corrección importante al informe de traspaso.** El traspaso suponía que
WACHUMA vivía sólo en Windows. Está en MAK, completo. Y su propio README lo
acota: *"los ejemplares, la escena 3D, el linaje y la relación cultural del
jardín siguen siendo sintéticos o restringidos hasta incorporar registros reales
revisados"*. Es decir: existe como software, no como contenido biocultural
publicable. Eso confirma —por evidencia y no por prudencia— que no debe ser el
centro de una postulación con cierre en días.

**Limitación declarada.** FARMAKSIA y PUPILA no pueden auditarse desde MAK. Todo
lo que se diga de ellos en este paquete es cita del traspaso, no observación.
Por eso ninguna de las tres postulaciones depende de ellos.

## 2. El motor comparado: las ocho operaciones

Las columnas son las operaciones que el encargo pide comparar. `IMPL` =
implementado y verificado hoy; `DOC` = documentado sin ejecución observada;
`—` = ausente.

| Operación | IRIS (verificado) | JARDINES (sqlite verificado) | WACHUMA (repo) | PUPILA (no auditable) |
|---|---|---|---|---|
| **Fuente** | `archivo.json.fuente = "todo"`, generación fechada | tabla `sources`, 44 filas | IMPL: procedencia explícita, IDs GBIF/IPNI | DOC en traspaso |
| **Entidad** | 2.034 piezas tipadas (`obra`/`codigo`) | `entities` 13, `claims` 26 | IMPL: organismo, ejemplar, linaje | DOC |
| **Relación** | 5.812 vínculos con peso y clase | `relations` 4, `claim_entities` 12 | IMPL: relaciones documentadas, no supuestas | DOC |
| **Intención / pregunta** | `tablero.json` (qué capas se encienden) | `topics` 12, `research_jobs` 4 | DOC: contrato editorial | DOC |
| **Transformación** | visión: color, estilo, `percibido` (219/219) | `domain_adapters` 6, `process_semantics` 12 | IMPL: importers, worker | DOC |
| **Representación** | proyección x,y + `vecindad_conservada = 0.4855` | `correlations` 10, `interpretations` 2 | IMPL: web, escena 3D (sintética) | DOC |
| **Decisión humana** | `curaduria.json`: contrato completo, **0 decisiones** | `audit_events` 11, `states` 1 | DOC: revisión comunitaria y takedown | DOC |
| **Salida** | **sólo descarga JSON** | `results` 2, CSV exportados | DOC: release checklist | DOC |

## 3. Lectura de la comparación

**Lo que comparten de verdad.** Los tres proyectos que existen en MAK
implementan la misma cadena: una fuente con procedencia, entidades tipadas,
relaciones con peso, una transformación que produce una representación, y una
instancia donde una persona decide. No es una analogía retórica: es el mismo
patrón instanciado tres veces, y `jardines_interpretativos.sqlite` lo hace
explícito con tablas que se llaman exactamente así (`sources`, `entities`,
`relations`, `contexts`, `interpretations`, `states`, `results`).

**Dónde se rompe la analogía, en los tres por igual.** La última columna. Los
tres tienen salida débil: IRIS descarga un JSON, JARDINES exporta dos CSV,
WACHUMA tiene checklist de release pero contenido restringido. **La salida
cultural pública es el eslabón que ninguno cerró.** Ese es el hallazgo más útil
de esta comparación y es, exactamente, lo que un fondo puede financiar.

**Qué exige cada dominio, y por qué no son intercambiables.**

- **IRIS** exige derechos sobre el archivo propio y una política de qué se
  publica. Es el dominio con menos dependencias externas: el archivo es del
  artista. Por eso es el circuito más corto entre archivo y salida.
- **JARDINES** exige rigor metodológico y fuentes citables. Es investigación,
  no producción de obra. Su naturaleza encaja con una línea de Investigación y
  desencaja con una de Creación.
- **WACHUMA** exige consentimiento biocultural, revisión comunitaria y una
  posición sobre conocimiento tradicional. Su propio repositorio lo reconoce.
  Ese costo no se resuelve en una semana ni debe intentarse.
- **PUPILA/XANAX** exigirían consentimiento de terceros y coordinación
  multiusuario. No hay implementación auditable en MAK. Nombrarlo en una
  postulación sería prometer sin respaldo.

## 4. Veredicto sobre la hipótesis inicial

> *Hipótesis recibida: "IRIS ofrece el circuito más corto entre archivo, criterio
> visual, selección humana y formato de portafolio reutilizable."*

**Se sostiene en sus tres primeros términos y falla en el cuarto.**

- *Archivo*: sí. 2.034 piezas propias, verificadas.
- *Criterio visual*: sí. Color, estilo y percepción sobre 219 obras, con métrica
  de pérdida publicada.
- *Selección humana*: el contrato existe y es de calidad inusual (reversible,
  campo a campo, sin publicación automática), pero **no se ha ejercido**.
- *Formato de portafolio reutilizable*: **no existe**. Es la brecha.

La hipótesis no debe descartarse: debe convertirse en el objeto del proyecto.
IRIS es el circuito más corto precisamente porque le falta un solo eslabón, ese
eslabón es visible, acotado y verificable, y el archivo sobre el que operaría ya
está en la máquina.
