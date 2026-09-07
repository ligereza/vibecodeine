# Carga del responsable y escenarios de adjudicación

Calculado por `carga.py`, no estimado a ojo. Reejecutar si cambian los perfiles.

**Supuesto declarado:** jornada de referencia de 160 h/mes. Los perfiles de horas
por fase provienen de las actividades de cada expediente y de sus presupuestos.
Son estimaciones del responsable, no mediciones.

**No se suman pesos con dólares en ninguna tabla.** Las horas sí se suman: son
la misma persona.

## 1. Carga mensual por escenario, en horas

| Escenario | pico h/mes | mes del pico | meses sobre 100h | meses sobre 140h | total h |
|---|---:|---|---:|---:|---:|
| A · solo Ama Amoedo | 75 | 2027-05 | 0 | 0 | 695 |
| B · solo Difusion | 60 | 2027-07 | 0 | 0 | 540 |
| C · solo Formativas | 70 | 2027-07 | 0 | 0 | 550 |
| D · Ama + Difusion | 135 | 2027-07 | 6 | 0 | 1235 |
| E · Ama + Formativas | 145 | 2027-07 | 6 | 1 | 1245 |
| F · Difusion + Formativas | 130 | 2027-07 | 5 | 0 | 1090 |
| G · las tres recomendadas | 205 | 2027-07 | 8 | 6 | 1785 |

## 2. Detalle mes a mes de los escenarios con más de una adjudicación

### D · Ama + Difusion

| mes | Ama Amoedo | Difusion | total | jornada |
|---|---:|---:|---:|---|
| 2027-01 | 70 | - | **70** | OK |
| 2027-02 | 70 | - | **70** | OK |
| 2027-03 | 60 | - | **60** | OK |
| 2027-04 | 60 | 50 | **110** | ALTA |
| 2027-05 | 75 | 50 | **125** | ALTA |
| 2027-06 | 75 | 55 | **130** | ALTA |
| 2027-07 | 75 | 60 | **135** | ALTA |
| 2027-08 | 55 | 60 | **115** | ALTA |
| 2027-09 | 55 | 55 | **110** | ALTA |
| 2027-10 | 40 | 45 | **85** | OK |
| 2027-11 | 40 | 40 | **80** | OK |
| 2027-12 | 20 | 40 | **60** | OK |
| 2028-01 | - | 35 | **35** | OK |
| 2028-02 | - | 30 | **30** | OK |
| 2028-03 | - | 20 | **20** | OK |

### E · Ama + Formativas

| mes | Ama Amoedo | Formativas | total | jornada |
|---|---:|---:|---:|---|
| 2027-01 | 70 | - | **70** | OK |
| 2027-02 | 70 | - | **70** | OK |
| 2027-03 | 60 | - | **60** | OK |
| 2027-04 | 60 | - | **60** | OK |
| 2027-05 | 75 | 45 | **120** | ALTA |
| 2027-06 | 75 | 55 | **130** | ALTA |
| 2027-07 | 75 | 70 | **145** | **INSOSTENIBLE** |
| 2027-08 | 55 | 70 | **125** | ALTA |
| 2027-09 | 55 | 70 | **125** | ALTA |
| 2027-10 | 40 | 70 | **110** | ALTA |
| 2027-11 | 40 | 45 | **85** | OK |
| 2027-12 | 20 | 35 | **55** | OK |
| 2028-01 | - | 30 | **30** | OK |
| 2028-02 | - | 25 | **25** | OK |
| 2028-03 | - | 20 | **20** | OK |
| 2028-04 | - | 15 | **15** | OK |

### F · Difusion + Formativas

| mes | Difusion | Formativas | total | jornada |
|---|---:|---:|---:|---|
| 2027-04 | 50 | - | **50** | OK |
| 2027-05 | 50 | 45 | **95** | OK |
| 2027-06 | 55 | 55 | **110** | ALTA |
| 2027-07 | 60 | 70 | **130** | ALTA |
| 2027-08 | 60 | 70 | **130** | ALTA |
| 2027-09 | 55 | 70 | **125** | ALTA |
| 2027-10 | 45 | 70 | **115** | ALTA |
| 2027-11 | 40 | 45 | **85** | OK |
| 2027-12 | 40 | 35 | **75** | OK |
| 2028-01 | 35 | 30 | **65** | OK |
| 2028-02 | 30 | 25 | **55** | OK |
| 2028-03 | 20 | 20 | **40** | OK |
| 2028-04 | - | 15 | **15** | OK |

### G · las tres recomendadas

| mes | Ama Amoedo | Difusion | Formativas | total | jornada |
|---|---:|---:|---:|---:|---|
| 2027-01 | 70 | - | - | **70** | OK |
| 2027-02 | 70 | - | - | **70** | OK |
| 2027-03 | 60 | - | - | **60** | OK |
| 2027-04 | 60 | 50 | - | **110** | ALTA |
| 2027-05 | 75 | 50 | 45 | **170** | **INSOSTENIBLE** |
| 2027-06 | 75 | 55 | 55 | **185** | **INSOSTENIBLE** |
| 2027-07 | 75 | 60 | 70 | **205** | **INSOSTENIBLE** |
| 2027-08 | 55 | 60 | 70 | **185** | **INSOSTENIBLE** |
| 2027-09 | 55 | 55 | 70 | **180** | **INSOSTENIBLE** |
| 2027-10 | 40 | 45 | 70 | **155** | **INSOSTENIBLE** |
| 2027-11 | 40 | 40 | 45 | **125** | ALTA |
| 2027-12 | 20 | 40 | 35 | **95** | OK |
| 2028-01 | - | 35 | 30 | **65** | OK |
| 2028-02 | - | 30 | 25 | **55** | OK |
| 2028-03 | - | 20 | 20 | **40** | OK |
| 2028-04 | - | - | 15 | **15** | OK |

---

## 3. Lectura de los números

**Cualquier proyecto solo es holgado.** A, B y C no superan las 75 h/mes en su
peor mes. Una sola adjudicación es cómodamente ejecutable por una persona.

**Dos adjudicaciones son exigentes pero sostenibles.** D, E y F llegan a picos de
130-145 h/mes durante julio de 2027, con cinco o seis meses sobre 100 h. Es
trabajo intenso y no imposible: la jornada de referencia es 160 h/mes.

**Las tres a la vez no son sostenibles como están declaradas.** El escenario G
llega a **205 h/mes en julio de 2027**, con **seis meses por sobre 140 h**. Eso
excede la jornada de referencia y no es una molestia de agenda: sería declarar en
tres formularios una dedicación que una persona no puede entregar.

**El escenario H, con la alternativa Creación en lugar de Difusión, es peor
todavía**, porque el montaje y la exhibición se concentran en los mismos meses
que las sesiones formativas.

## 4. Qué hacer en cada caso, decidido de antemano

| Si se adjudica | Decisión |
|---|---|
| Una sola | Ejecutar según cronograma. Ningún ajuste |
| Ama + Difusión | Ejecutar. Es la mejor combinación: la curaduría de Ama alimenta la selección que Difusión publica, sin que ningún gasto se repita |
| Ama + Formativas | Ejecutar, desplazando el inicio de Formativas al 31 de mayo, que ya está previsto |
| Difusión + Formativas | Ejecutar. Ambas empiezan con dos meses de diferencia dentro de la ventana permitida |
| **Las tres** | **Rehacer la dedicación declarada antes de firmar convenios.** Tres caminos, en orden de preferencia: (1) escalonar al máximo dentro de la ventana del 1 de abril al 31 de mayo; (2) redistribuir dentro del ítem Personal para incorporar apoyo, lo que las bases permiten sin autorización previa salvo alojamiento, alimentación y traslado; (3) renunciar a una selección, que es preferible a incumplir un convenio |

**Lo que no se debe hacer:** aceptar las tres y sostener la dedicación declarada
en cada una. Está anotado como dependencia D-7, con fecha de activación en los
resultados.

## 5. Por qué esto reduce el problema de origen

La v1 recomendaba postular a dos líneas Fondart para el mismo instrumento
—Creación y Formativas— más Ama Amoedo. La v2 recomienda **una sola línea Fondart
para el instrumento**, por la razón normativa del Anexo 3 §II.4 sobre identidad
de contenido. Ese cambio, tomado por otro motivo, tiene un efecto lateral útil:
elimina el escenario de carga más pesado antes de que pueda ocurrir.

## 6. Costes incrementales reales de cada combinación

Sin sumar monedas distintas.

| Combinación | Costo en CLP | Costo en USD | Qué se reutiliza sin volver a cobrarse |
|---|---:|---:|---|
| Ama sola | — | 8.734 | — |
| Difusión sola | 8.800.000 | — | Usa el instrumento existente tal como esté |
| Formativas sola | 9.266.000 | — | Usa el instrumento existente tal como esté |
| Ama + Difusión | 8.800.000 | 8.734 | Difusión publica la selección que Ama curó. **Ningún desarrollo se paga dos veces:** el exportador lo financia sólo Ama |
| Ama + Formativas | 9.266.000 | 8.734 | Formativas enseña el método que Ama ejerció |
| Difusión + Formativas | 18.066.000 | — | Formativas usa como ejemplo la superficie que Difusión publica |
| Las tres | 18.066.000 | 8.734 | Hosting se paga una vez (Difusión). Desarrollo se paga una vez (Ama) |

**Lo que cuesta de más al sumar proyectos es tiempo del responsable, no dinero
duplicado.** Los presupuestos están construidos para que eso sea verificable:
`verificador/verificar_presupuestos.py` falla si un `id_coste` se repite.
