# Respuesta a la auditoría Luna y a las precisiones de Faro

Estado del material auditado: verifiqué los hashes relevantes de
`AUDITORIA_LUNA_20260906/research.md` contra los archivos de la v1 **antes** de
tocar nada. **Coinciden.** La v1 quedó congelada en
`../v1_ENTREGA_20260906_AUDITADA/` con sello en `../SELLO_v1.sha256`.

Reproduje además el cálculo del script PowerShell con un verificador propio que
lee los CSV en vez de cifras embebidas: los totales de la v1 eran correctos.
Eso valida la aritmética de Luna, no los CSV, que es la distinción que Faro hizo.

---

## Hallazgos de la auditoría

### A1 · "219 piezas descritas como 219 obras" — **ACEPTADO, y corregido más allá de lo pedido**

**Evidencia.** `campo.json` tipifica 219 piezas: `obra` 134, `foto_evento` 40,
`tatuaje` 28, `otro` 6, `logo` 4, `flyer_evento` 2, y cinco tipos con 1 cada uno.
Suma verificada = 219.

**Cambio aplicado.** Ninguna postulación dice "219 obras". Además **no adopté la
redacción propuesta por la auditoría**, que decía "134 tipificadas como obra y el
resto como contexto u otros tipos": el resto no es homogéneo y agruparlo pierde
información. Los expedientes citan la tipificación completa.

**Corrección adicional que la auditoría no hizo.** `tipo: "obra"` es una
tipificación del pipeline, **no una validación autoral**. Los textos dicen
"piezas tipificadas como obra en el campo activo", nunca "obras del artista".
Ver `evidencia/ESTADO_TECNICO_VERIFICADO.md` §2.

---

### A2 · "Decisiones, exportación y publicación presentadas cerca del presente" — **PARCIAL: aceptado en la forma, refutado en el fondo**

**Aceptado.** La v1 describía en presente un flujo de sesión que no existe. Los
resúmenes de Creación y Difusión se reescribieron separando lo que hay de lo que
se compromete construir.

**Refutado, y es la corrección más importante de todo el trabajo.** La auditoría
reprodujo de la v1 que el bucle de decisión humana "no se ha ejercido" y que hay
"0 decisiones". Faro advirtió que `curaduria.json` vacío no demuestra eso.
**Tenía razón, y al rastrear la función concreta apareció lo contrario.**

`_portfolio_select_unlocked` (`hub.py` líneas 2059-2160) escribe en un JSONL y
asienta en el ledger común con control de unicidad. Esos archivos tienen datos:

| Archivo | Contenido medido hoy |
|---|---|
| `selections.jsonl` | **87 decisiones**, 68 ítems, **14 sesiones**, 2026-08-07 → 2026-09-02 |
| | `descartar` 65 · `seleccionar` 13 · **`deseleccionar` 9** |
| | **65 de 65 descartes con `reason_code: "no_es_obra"`** |
| `classifications.jsonl` | **103 clasificaciones**; 100 `human_draft`, 3 `human_confirmed`; `promotion: none` |
| `common_ledger.jsonl` | **123 asientos en dominio `iskvw`**; 94 con `owner: human` |

Tres afirmaciones de la v1 caen:

1. "No hay persistencia" → **falso**: está implementada y en uso.
2. "La reversibilidad es un contrato sin ejercer" → **falso**: 9 reversiones reales.
3. "La distinción obra/no-obra es sólo de máquina" → **falso**: se ejerció
   autoralmente 65 veces, con motivo registrado.

Lo que **sí** se sostiene, y acota el hallazgo: el inventario está
`status: not_public`, las 103 clasificaciones están en `promotion: "none"` y sólo
3 llegaron a `human_confirmed`. **La curaduría ocurrió; la publicación no.**

**Sobre la exportación, también hubo que ser más preciso.** No es cierto que no
exista nada: `~/tools/compile_portfolio_dossier.py` existe, su motor carga y
**rechaza entradas vacías con 22 errores de validación**. Pero su propio contrato
lo excluye del uso que haría falta: consume un plan y un estado de evidencia, y
*"no lee un archivo, no abre una base de datos y no publica un asset"*.

La brecha, redefinida con precisión: **no existe la pieza que tome el inventario
más las decisiones ya registradas y produzca un artefacto publicable.** Eso es lo
que se financia, y sólo en un presupuesto de los cuatro.

---

### A3 · "Formulario vivo de Ama Amoedo no localizado" — **REFUTADO: resuelto**

**Evidencia.** El PDF oficial de bases contiene dos anotaciones de enlace que
`pdftotext` no extrae. Al leer los objetos `/URI` del archivo aparece el
formulario: **`https://opencallfundacionamaamoedo.vform.io/`**.

**Comprobación.** HTTP 200, título "Open Call Becas | Grants", "Portal de
postulaciones", plataforma Vinko/vform, `institution_id=671`.

**La barrera, con la precisión que Faro pidió.** No hace falta firma ni un dato
inexistente: hace falta **crear una cuenta** (correo y contraseña, o Google, o
Facebook). Cuatro rutas de listado público probadas devuelven 404, así que los
campos y límites **no son enumerables sin cuenta del titular**. Eso es lo que
queda tras la barrera, y nada más.

---

### A4 · "Identidad, CV, portfolio y cuenta bancaria" — **PARCIAL**

**Aceptado** para identidad, CV y portfolio: son del titular y no se inventan.
La ficha Markdown de corpus no es un portfolio; la v2 la presenta como **índice
de selección candidata**, con esa etiqueta, en `BORRADORES_SIN_FIRMA/`.

**Refutado** para la cuenta bancaria. Las bases dicen *"**Para la otorgación de
la Beca**, será requisito excluyente poseer cuenta bancaria a nombre del/la
titular"*. Es requisito **de pago, no de postulación**. Tratarlo como bloqueo de
envío es un error de momento de exigencia. Ver `MATRIZ_REQUISITOS.md` §2.

---

### F1 y F3 · "Cartas de equipo faltantes: bloqueante" — **PARCIAL: el bloqueo se disolvió rehaciendo el alcance**

**Aceptado** que, con equipo declarado, las cartas son taxativas y su ausencia
sería causal de exclusión.

**Refutado** que sea un bloqueo inevitable. El anexo dice **"(si corresponde)"**,
y equipo de trabajo es *"según lo defina el postulante en su formulación"*. Sin
equipo declarado, no hay cartas que faltar.

**Y no se hizo con una etiqueta.** La dirección advirtió contra reclasificar
personas como proveedores para eludir una carta, y no se hizo:

- En Creación **se eliminó** la mediación por tercera persona: el titular media.
- En Formativas **se eliminó** la co-facilitación: el titular imparte solo.
- Metas de público y de cohorte bajadas en proporción.
- Presupuestos rehechos: la asignación del responsable queda en 34,74% (Creación),
  38,64% (Difusión) y 36,69% (Formativas), y **los totales bajan** porque una sola
  persona no puede superar el 40% del solicitado.

Sólo permanecen servicios con entregable y periodo acotado —imprenta, flete,
auditoría de accesibilidad con informe, maquetación—, que no son equipo de trabajo.

---

### F2 · "Carta o cotización del espacio en Creación" — **ACEPTADO, y con salida**

Aceptado: la obra se exhibe en sala existente, así que el documento corresponde.
Es de evaluación, no taxativo: su ausencia baja Viabilidad (10%), no deja fuera
de bases. `MATRIZ_REQUISITOS.md` §1 hace esa distinción.

**Salida encontrada.** La línea **Difusión** exime expresamente el documento
cuando *"el soporte lo constituya un medio de difusión no existente (ejemplo: un
sitio web) y que será desarrollado por el proyecto en concurso"*. Por eso la v2
recomienda Difusión antes que Creación: **no depende de ningún tercero**.

---

### F4 · "Espacio y gratuidad en Formativas" — **ACEPTADO, y ampliado con dos requisitos que faltaban**

Gratuidad: obligatoria por bases; atraviesa convocatoria, metodología y
presupuesto —incluidos un fondo de traslado y equipos de préstamo arrendados,
para que la gratuidad sea efectiva y no sólo nominal.

**Ampliación que la auditoría no detectó.** El Anexo 2 de Formativas exige dos
documentos de evaluación más:

1. **"Antecedentes de respaldo de estudios formales y no formales"** de quien
   imparte la formación.
2. **"Carta compromiso de asistentes: documento que dé cuenta del compromiso de
   asistencia a la actividad formativa, de al menos 15 personas."**

Quince compromisos individuales firmados antes de enviar. No es taxativo, pero
es la dependencia humana más pesada del paquete y no la puede cerrar el titular
solo. **Es la razón principal por la que Formativas baja al tercer lugar en la v2.**

---

### N1 · "Acumulabilidad no verificada" — **REFUTADO: hay cláusula aplicable y nadie la había citado**

La auditoría concluyó "no prohibido expresamente, no confirmado; consultar SIAC".
Buscando en el Anexo 3 apareció la norma que gobierna el caso, presente en las
**tres** bases:

> **Anexo N°3, §II.4** — *"Si se constata la presentación de postulaciones que
> evidencien **el mismo contenido** (aún cuando existan diferencias formales en lo
> concerniente al **Fondo, Línea, Modalidad**…) sólo consideraremos la última
> postulación presentada… considerándose las demás fuera de convocatoria."*

Qué cambia:

1. Postular a líneas distintas **no está prohibido**: está condicionado.
2. La condición **no es el número de postulaciones sino la identidad de contenido**.
   Una FAQ sobre cantidad, como bien dijo Faro, no resolvía esto.
3. La separación de actividades deja de ser una salvaguarda voluntaria y pasa a
   ser **la forma de cumplir §II.4**.
4. **Consecuencia de diseño:** presentar el mismo instrumento en Creación *y* en
   Difusión es exactamente el caso de riesgo. Por eso la v2 recomienda postular
   **sólo una** de las dos.

Queda una pregunta genuina —qué ocurre al ser *seleccionado* en dos líneas con
contenidos distintos— redactada en `DEPENDENCIAS_HUMANAS.md` D-6. **No bloquea el
envío:** opera después de la selección.

---

### N2 · "Hosting y registro en varias líneas" — **ACEPTADO, resuelto eliminando en vez de separando**

La v1 argumentaba que eran dominios distintos. Argumento débil. La v2:

- **Hosting aparece una sola vez en todo el paquete**, en Difusión, cuyo objeto
  *es* la superficie pública. Los otros tres no lo llevan.
- **Desarrollo del motor se financia una sola vez**, en Ama Amoedo (`P-AMA-02`).
- **Registro documental** existe en tres proyectos con productos, periodos y
  objetos distintos, detallados en `presupuestos/TRAZABILIDAD_COSTES.md` §2.
- Cada línea lleva `id_coste` único y **el verificador falla si uno se repite**,
  con prueba negativa que lo comprueba.

---

### N3 · "Dedicación triple superpuesta" — **ACEPTADO, y ahora cuantificado**

La v1 lo mencionaba sin medirlo. `cronogramas/CARGA_Y_ESCENARIOS.md` calcula la
carga mensual del responsable en cada combinación, con horas por mes, y muestra
los meses en que se hace insostenible. La recomendación de postular una sola
línea Fondart para el instrumento reduce el problema de origen.

**No se suman pesos con dólares** en ningún escenario.

---

### N4 · "Mejoras de motores en curso: no usar como evidencia" — **ACEPTADO**

Corte declarado: **2026-09-06**. Tabla de situación en `MATRIZ_REQUISITOS.md` §10.
Ninguna capacidad no recibida se cita ni se presupone, y ninguna postulación
depende de completar esa integración. Tampoco se presupuesta desarrollar de nuevo
lo que sí está verificado y disponible: por eso la persistencia de decisiones
—que existe— **no** aparece como trabajo a financiar en ningún presupuesto.

---

## Precisiones de Faro

| # | Precisión | Estado | Dónde se aplicó |
|---|---|---|---|
| 1 | "Fuera de convocatoria" es equívoco para anexos faltantes | **Aplicada** | `MATRIZ_REQUISITOS.md` §1 separa los cuatro estados. Ninguna postulación se declara excluida: no hay acto administrativo ni envío |
| 2 | `curaduria.json` vacío no prueba ausencia de persistencia ni imposibilidad de exportar | **Aplicada, y cambió el dictamen** | Rastreé la función. Ver A2. Tres afirmaciones de la v1 refutadas con datos |
| 3 | Verificar tipologías restantes; tipificación ≠ validación autoral; conservar universo y fecha | **Aplicada** | `ESTADO_TECNICO_VERIFICADO.md` §1 separa dos universos que la v1 y la auditoría mezclaban; §2 da la tipificación completa |
| 4 | Ausencia de prueba de acumulabilidad no prueba incompatibilidad; una FAQ de cantidad no resuelve selección simultánea | **Aplicada** | Ver N1. Cláusula §II.4 localizada; pregunta SIAC reducida a lo que realmente queda abierto |
| 5 | Separar requisitos al postular y al adjudicarse | **Aplicada** | `MATRIZ_REQUISITOS.md` §2. Cuenta bancaria, cédula, domicilio y garantía movidos a su momento real |
| 6 | Que una página no exponga el formulario no lo convierte en pendiente humano | **Aplicada, y resuelta** | Ver A3. URL obtenida del propio PDF de bases; barrera identificada como registro de cuenta |
| 7 | No tratar cotizaciones como obligatorias en toda partida | **Aplicada** | `MATRIZ_REQUISITOS.md` §5. "Cotización" aparece 1 vez en Creación, 1 en Difusión y **0 en Formativas**, siempre como alternativa a la carta del espacio |

---

## Correcciones a la auditoría que no venían de ninguna de las dos listas

Hallazgos propios de esta revisión, con su fuente:

1. **Formativas exige carta de compromiso de al menos 15 asistentes.** Anexo 2.
   No estaba en la v1 ni en la auditoría. Cambia la prioridad de la línea.
2. **Formativas exige antecedentes de estudios formales y no formales** de quien
   imparte. Anexo 2, criterio Currículo.
3. **Anexo 3, §II.5:** la comisión puede rebajar hasta un 10% bajo lo solicitado,
   y **debe** rebajar cualquier ítem no financiable. Refuerza no agotar el tope y
   respetar la estructura de ítems por línea.
4. **La región nunca estuvo documentada.** Las nueve menciones a la Región
   Metropolitana en el material previo dicen "propuesta". Cambia la fecha de
   cierre aplicable. Escenarios en `MATRIZ_REQUISITOS.md` §4.
5. **Existen dos universos de datos distintos**, con identificadores que no se
   cruzan. La v1 y la auditoría hablaron de uno solo.
