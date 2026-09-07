# Reporte de ejecución — 6 de septiembre de 2026

Ficha del titular al ejecutar: **0 de 28 campos, 0 de 5 filas de portfolio**.
No se incorporó ningún dato porque no hay ninguno, y no se inventó ninguno.

---

## Decisiones de proyecto que tomé, con su criterio

**1. Difusión: elimino la mediación presencial.** Tres razones. La exención del
compromiso de espacio —única razón para preferir esta línea— se apoya en que el
soporte es un medio no existente que el proyecto desarrolla; sostener actividades
en espacios de acceso público reintroduce la dependencia de terceros por la puerta
de atrás. Las bases advierten que *"no financiaremos proyectos de circulación de
obra y/o contenido"*. Y con Impacto Potencial al 50%, una superficie con
accesibilidad auditada y registro de circulación acredita acceso y públicos con
datos, no con actas. Se conserva el acceso sin conectividad con una **edición
imprimible de la guía**, que es un producto y no un evento. Corregido en los 13
campos, en el anexo de exhibición y en el presupuesto.

**2. Formativas: modalidad mixta y espacio por cotización.** Cuatro sesiones
presenciales —las que exigen mesa y mirarse entre pares: 1, 2, 6 y 8— y cuatro en
línea, con las 48 horas de tutoría remotas. Baja el arriendo de ocho sesiones a
cuatro, elimina las doce jornadas de sala para tutorías y reduce la barrera de
traslado. El espacio se resuelve con **cotización**, que las bases aceptan igual
que la carta y que no depende de que un tercero adhiera al proyecto. El total baja
de **$9.266.000 a $8.608.000 por la modalidad, no por recorte**; se añaden fondo
de conectividad y equipos de préstamo para que la modalidad no seleccione por
recursos.

**3. Creación: llevada a nivel técnico completo, de 6 a 13 campos.** Añadidos
Fundamentación, Producción y pruebas —con **criterio de aceptación declarado**:
la obra no abre si no completa 20 recorridos sin fallo y quedan hallazgos críticos
de accesibilidad—, Espacio y montaje, Accesibilidad, Indicadores, Currículo y
Sostenibilidad. El espacio se resuelve también por cotización de arriendo de sala.

**4. Ama: la selección de portfolio está hecha y fundamentada**, no devuelta como
pregunta. 4 piezas con decisión de autoría registrada más 12 propuestas con
criterio explícito y epígrafes redactados. Total 16, dentro del máximo de 20.

**5. Descarté las 8 obras con título propio, y el motivo cambió el concepto.**
Eran el mejor material textual del archivo. Verifiqué su procedencia: **0 en el
inventario de curaduría, 0 selecciones, 0 clasificaciones, 0 en el registro de
decisiones, 0 en `curaduria.json`**, su `estado: publicada` es un valor por
defecto de las 1.826 piezas de esa clase, `obras.json` es del 2026-07-27 —anterior
a las dos instancias posteriores— y **sus ocho archivos no existen en disco**.

Y al cruzar los dos inventarios apareció el hallazgo que reformula Ama Amoedo:
**de las 68 piezas decididas, ninguna está entre las 219 que la máquina leyó.
Intersección cero.** Hoy no hay en el archivo una sola pieza que sea a la vez
decidida por el autor, legible y presente. Eso no es un obstáculo del expediente:
es su argumento, y ahora es lo que la beca financia.

## Archivos creados

| Archivo | Contenido |
|---|---|
| `MATRIZ_COHERENCIA_20260906.md` | Título → idea → concepto → área → metodología → resultados → presupuesto → anexos de los cuatro, con prueba de coherencia interna y verificación cruzada |
| `postulaciones/ANEXOS/SELECCION_PORTFOLIO_AMA.md` | 16 piezas por nivel de procedencia (N1 4, N2 12, N3 8 descartadas), epígrafes propuestos y **2 alertas de dato automáticas** |
| `postulaciones/BORRADORES_SIN_FIRMA/MODELO_AUTORIZACION_USO_DE_IMAGEN.md` | Modelo sin firmar, con la distinción entre uso de imagen y derechos de autor |
| `postulaciones/BORRADORES_SIN_FIRMA/MODELO_CARTA_COMPROMISO_EQUIPO.md` | Modelo sin firmar, con la tabla de qué es y qué no es equipo de trabajo |
| `verificador/generar_seleccion_portfolio.py` | Genera la selección y marca alertas de dato |

## Archivos corregidos

`campos_difusion.py` (16 reemplazos) · `campos_formativas.py` (14) ·
`campos_creacion.py` (+7 campos) · `campos_ama.py` (8) · los cuatro
`TEXTO_POR_CAMPO.md` · `presupuestos/03_fondart_difusion.csv` ·
`presupuestos/04_fondart_formativas.csv` (rehecho) · `DRY_RUN_ENVIO_20260906.md` ·
`LEEME_CIERRE.md` · `generar_para_copiar.py` (+7 documentos) ·
`generar_indice_anexos.py` (+4 anexos) · `comprobacion_cruzada.py` (cita
actualizada) · `BORRADOR_INDICE_PORTFOLIO.md` (marcado como superado).

## Errores que los verificadores detectaron y corregí

1. `generar_seleccion_portfolio.py`: dos candidatas con defecto real de dato —una
   tipificada `obra` cuya lectura describe un tatuaje, y otra con los colores en
   inglés. **No se ocultaron:** se marcan en el anexo, porque son la evidencia del
   trabajo que Ama Amoedo financia.
2. `comprobacion_cruzada.py`: la cita del total de Formativas quedó desfasada tras
   el cambio de modalidad. Corregida a $8.608.000.

## Resultado de cada comando

```
generar_texto_por_campo.py       Ama 9/1.504 · Difusión 13/2.326 · Formativas 11/2.642 · Creación 13/2.495
generar_matriz_campos.py         46 campos, 8.967 palabras
generar_para_copiar.py           35 archivos + LEEME.md
generar_seleccion_portfolio.py   N1=4 · N2=12 de 134 · N3=8 descartadas · 2 alertas
generar_indice_anexos.py         exit=0  41 anexos, 0 rutas rotas
verificar_presupuestos.py        exit=0  USD 8.734 · 12.090.000 · 8.800.000 · 8.608.000
pruebas_negativas.sh             exit=0  control positivo 1 · 14 defectos · 0 no detectados
comprobacion_cruzada.py          exit=0
revision_ids_y_gastos.py         exit=0  40 ids únicos · 6 conceptos comunes sin duplicación
leer_ficha_titular.py            exit=0  0 completados, 28 pendientes
```

## Pendientes personales, y sólo esos

Región y comuna · identidad, RUT, edad, domicilio, contacto · Perfil Cultura ·
cuenta del portal Ama · CV y cédula · **aprobación** de la selección de 16 piezas
y sus epígrafes · antecedentes de estudios · 15 compromisos de asistencia ·
cotización de espacio.

**Ninguna es una pregunta de proyecto.** No queda ninguna decisión de concepto,
línea, modalidad, espacio, metodología ni estrategia sin tomar.

Un pendiente que vale la pena señalar sin que bloquee nada: si el titular localiza
los ocho archivos de las obras con título propio, pasan a ser el mejor material
del portfolio, porque aportan lo único que a N1 y N2 les falta —título y texto de
autor.

## Constancia

No se envió ninguna postulación, no se firmó nada, no se registró ninguna cuenta,
no se contactó a ningún tercero, no se inventaron datos personales, obras, CV,
estudios, firmas, nombres, RUT ni regiones, y no se modificó la v1 congelada,
ningún repositorio ni ningún servicio.
