# Entrega — tres postulaciones y un motor común

**6 de septiembre de 2026.** Todo lo que sigue está en esta carpeta y es revisable.

---

## La decisión

**Los tres concursos originales sí existían y están identificados.** La carpeta
"bases" que se daba por no localizada es **`/home/mak/BASES/postulaciones/`**, y
su README declara la terna que la dirección seguía: **Ama Amoedo**, **Fondart
Regional Creación (IRIS)** y **Fondart Nacional Investigación (JARDINES)**. La
terna Creación / Difusión / Formativas era una propuesta del asistente anterior,
no lo que el usuario tenía en mente.

**Recomendación: conservar dos y sustituir uno.**

| | Concurso | Proyecto | Cierre | Monto |
|---|---|---|---|---|
| **1** | Becas Fundación Ama Amoedo 2026 — Artistas | *Dimensiones del Orden: ordenar el propio archivo* | **mié 9 sep, 23:59** | US$10.000 |
| **2** | Fondart Regional — Creación Artística, disciplina **Diseño** | *IRIS: Mesa de Montaje* | **vie 11 sep, 15:00** | $18.000.000 |
| **3** | Fondart Regional — Actividades Formativas | *Laboratorio Dimensiones del Orden* | **vie 11 sep, 15:00** | $14.900.000 |

Se desplaza Investigación Nacional (JARDINES), que **queda vivo** con cierre el
14 de septiembre y su material intacto. La razón está en
`analisis/RECOMENDACION_TRES_OPCIONES.md` §3.

**Las tres son compatibles:** las bases sólo prohíben más de una postulación *por
línea*. Y este paquete se autolimita: **ninguna actividad ni gasto se repite
entre expedientes**.

---

## El hallazgo que ordena todo lo demás

IRIS funciona. Lo comprobé hoy y la prueba es reproducible: 2.034 piezas, 5.812
vínculos, 219 obras leídas por visión de máquina, y una métrica que el propio
sistema publica sobre cuánto pierde al ordenar — `vecindad_conservada = 0.4855`.

**Y le falta exactamente una cosa: la salida.** Su única salida hoy es la
descarga de un archivo JSON. No hay portafolio, no hay publicación, el servicio
escucha sólo en `127.0.0.1`, y el registro de decisiones humanas tiene **cero
entradas**.

Ese hueco es el proyecto. Los tres expedientes piden financiar el eslabón que
falta, no declaran capacidades que no existen.

---

## Acceso directo

### Para decidir
- **`analisis/RECOMENDACION_TRES_OPCIONES.md`** — qué postular y qué cuesta adaptarse
- `analisis/A_PROYECTO_MAS_SIMPLE_Y_ROBUSTO.md` — por qué IRIS y no otra cosa
- `analisis/B_MOTOR_Y_RAMAS.md` — el motor explicado con una pieza real, y las ramas posteriores

### Para revisar las postulaciones
- `postulaciones/01_AMA_AMOEDO_ARTISTAS/EXPEDIENTE.md`
- `postulaciones/02_FONDART_CREACION_IRIS/EXPEDIENTE.md`
- `postulaciones/03_FONDART_FORMATIVAS_LABORATORIO/EXPEDIENTE.md`
- `postulaciones/ANEXOS/` — 8 anexos y 2 modelos de carta

### Para verificar las cifras
- `presupuestos/*.csv` — tres presupuestos con cantidad, unidad, precio, subtotal, fundamento y origen del valor
- `presupuestos/VERIFICACION_TOPES.md` — recálculo de cada subtotal y control de topes
- `presupuestos/ESCENARIOS_DE_ADJUDICACION.md` — gana una, dos o tres

### Para auditar la evidencia
- `evidencia/CIRCUITO_IRIS_COMPROBADO.md` — qué funciona, qué no, con archivo y línea
- `evidencia/prueba_circuito.sh` — ejecutable, no modifica nada
- `evidencia/MAPA_DE_FUNCIONES.md` — IRIS, JARDINES/WACHUMA y FARMAKSIA/PUPILA comparados

### Para las fuentes
- `fuentes/pdf/` — 9 PDF oficiales sin editar · `fuentes/txt/` — extracción legible
- `fuentes/REGISTRO_DE_CITAS.md` — URL, fecha, qué resuelve cada uno, y **qué no resuelven**
- `fuentes/MATRIZ_COMPARATIVA.csv` — 26 dimensiones × 5 convocatorias

### Para actuar
- **`RESOLUCIONES_EXTERNAS.md`** — las 9 cosas que sólo puede hacer una persona
- `cronogramas/PREPARACION_HASTA_EL_ENVIO.md` — día por día del 6 al 11
- `INFORME_FINAL.md` — qué cambió, qué se corrigió y el estado real

---

## Lo primero que hay que hacer, mañana lunes

1. **Confirmar la región de domicilio.** Todo asume Región Metropolitana. Si es
   otra, puede cambiar la fecha de cierre. *Es lo primero.*
2. **Pedir las cartas del equipo.** Son taxativas: sin ellas, los dos Fondart
   quedan fuera de bases.
3. **Contactar el espacio anfitrión.** Es lo que más tarda en responder.
4. **Buscar el formulario vivo de Ama Amoedo.** Cierra el miércoles.

---

## Qué no se hizo, por no haber sido encargado

No se envió ninguna postulación. No se contactó a nadie. No se publicó nada. No
se tocó ningún repositorio ni se hizo ninguna operación de Git. No se modificó
ningún dato de IRIS: la prueba técnica sólo lee, y su único POST es un control
que debe fallar. Nada salió de esta máquina.
