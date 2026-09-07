# -*- coding: utf-8 -*-
DESTINO = "01_AMA_AMOEDO_ARTISTAS/TEXTO_POR_CAMPO.md"
TITULO = "Ama Amoedo 2026 - Artistas · texto por campo"
CABECERA = """
**Convocatoria:** Becas Fundación Ama Amoedo 2026, categoría **Artistas**.
**Cierre:** miércoles 9 de septiembre de 2026, 23:59 hora de Uruguay.
**Monto:** US$10.000. **Solicitado:** US$8.734. **Resultados:** 20 de noviembre.
**Formulario:** https://opencallfundacionamaamoedo.vform.io/ — portal Vinko,
"Open Call Becas | Grants", verificado HTTP 200 el 2026-09-06.

**Los límites de caracteres del formulario no son conocidos:** están detrás del
registro de cuenta y no hay listado público (cuatro rutas probadas, 404). Por eso
cada campo largo viene en **tres versiones de extensión declarada** — breve,
media y extendida — para recortar a lo que el formulario pida sin reescribir.

**Secciones según las bases §7:** a) información personal · b) información del
proyecto · c) presupuesto · d) adjuntos.
"""

CAMPOS = [
 {"campo":"Título del proyecto","version":"única","nota":"Sección b",
  "texto":"Dimensiones del Orden: ordenar el propio archivo"},

 {"campo":"Descripción del proyecto — versión breve","version":"breve (~70 palabras)","nota":"Sección b",
  "texto":"""Tengo un archivo que no puedo recorrer y un instrumento que lo mira, propone órdenes y declara cuánto pierde al proponerlos. Ya decidí sobre él: acepté, descarté con motivo y me desdije. Pero al intentar armar el portafolio de esta postulación apareció el problema entero: lo que decidí y lo que la máquina leyó son dos inventarios que no se tocan, y lo único con título mío no tiene archivo. Esta beca financia unirlos y producir la primera salida."""},

 {"campo":"Descripción del proyecto — versión media","version":"media (~200 palabras)","nota":"Sección b",
  "texto":"""Un archivo de artista crece sin forma. El mío tiene dos inventarios: un atlas de 2.034 piezas leído por visión computacional, y una bandeja de curaduría de 7.044 registros donde vengo decidiendo a mano.

Ahí ya hay trabajo hecho, y es verificable. Entre el 7 de agosto y el 2 de septiembre de 2026 registré 87 decisiones en 14 sesiones: 13 selecciones, 65 descartes —cada uno con el motivo "no es obra"— y 9 reversiones de decisiones que había tomado antes. El sistema guarda cada una con su fecha y su motivo, y permite deshacerla.

Y sin embargo no puedo armar un portafolio. Al cruzar los dos inventarios aparece el problema entero: de las 68 piezas que decidí, ninguna está en el campo visual que la máquina leyó. Cero coincidencias. Las que tienen mi decisión no tienen lectura; las que tienen lectura no tienen mi decisión; y las ocho que sí llevan título y texto míos no tienen archivo en disco.

No hay hoy en mi archivo una sola pieza que sea a la vez decidida por mí, legible y presente.

Este proyecto financia cerrar esa distancia: terminar la curaduría sobre el inventario completo, unir los dos inventarios en uno solo, normalizar el vocabulario con que se describe mi trabajo, y construir la exportación que convierte una selección decidida en un portafolio publicable y en un archivo preservado.

No prometo que la máquina encuentre el orden correcto. Su propia métrica dice que conserva menos de la mitad de la vecindad original. Prometo un archivo ordenado por una persona con ayuda de una máquina que muestra su trabajo."""},

 {"campo":"Descripción del proyecto — versión extendida","version":"extendida (~380 palabras)","nota":"Sección b",
  "texto":"""Un archivo de artista crece sin forma. El mío existe hoy en dos inventarios distintos, y conviene decirlo con precisión porque son cosas diferentes.

El primero es un atlas de lectura por máquina: 2.034 piezas y 5.812 relaciones. Sobre un campo activo de 219 piezas hay una lectura visual completa —color, estilo y una descripción automática de lo que se ve— y una proyección que dispone lo parecido cerca. Esa proyección publica su propio costo: conserva 0,4855 de la vecindad original. Menos de la mitad. El sistema lo declara en vez de esconderlo, y esa es la única razón por la que confío en él.

El segundo es una bandeja de curaduría con 7.044 registros, marcada como no pública. Ahí decido yo. Entre el 7 de agosto y el 2 de septiembre de 2026 registré 87 decisiones en 14 sesiones sobre 68 registros: 13 selecciones, 65 descartes y 9 reversiones. Los 65 descartes llevan el mismo motivo, "no es obra", que es el juicio más básico y más difícil sobre un archivo propio. De 103 clasificaciones, sólo 3 llegué a confirmarlas, y ninguna está promovida a público.

Ese trabajo existe y no se ve. El editor exporta un archivo de datos. Existe además un compilador de dossier que funciona y valida, pero su propio contrato lo excluye: no lee el archivo, no abre una base de datos y no publica nada.

Y hay algo peor, que descubrí al intentar armar el portafolio de esta misma postulación. Los dos inventarios no se tocan: de las 68 piezas que decidí, **ninguna** aparece entre las 219 que la máquina leyó. Las ocho piezas que sí llevan mi título, mi año y mi texto —las únicas con voz de autor en todo el archivo— no tienen archivo en disco: sus rutas no existen. De modo que hoy no hay una sola pieza que reúna las tres condiciones que un portafolio necesita: que yo la haya reconocido como obra, que exista una lectura de lo que se ve, y que el archivo esté ahí.

Esta beca financia cerrar esa distancia, y son cuatro cosas concretas. Unir los dos inventarios en uno solo, que es la condición para que una decisión y una lectura puedan caer sobre la misma pieza. Terminar la curaduría sobre el conjunto, en vez de las 68 piezas alcanzadas. Normalizar el vocabulario visual, que hoy está sucio —el mismo azul aparece con y sin mayúscula, algunas piezas traen los colores en inglés, y hay material tipificado como obra que la lectura describe como un tatuaje— porque decidir con qué palabras se describe mi trabajo es una decisión de autor y no de mantenimiento. Y construir la exportación que convierte una selección decidida en un portafolio publicable y en un archivo preservado con su procedencia.

No prometo que la máquina encuentre el orden correcto: su propia métrica dice que no puede. Prometo un archivo ordenado por una persona con ayuda de una máquina que muestra su trabajo, y un instrumento que después queda documentado para que otro artista haga lo mismo con el suyo, sujeto a la prueba de uso y a la licencia que yo defina."""},

 {"campo":"Objetivos","version":"única","nota":"Sección b",
  "texto":"""General: ordenar, decidir y publicar mi propio archivo artístico completando el eslabón que hoy le falta al instrumento con que lo trabajo.

Específicos:
1. Unificar los dos inventarios del archivo, hoy disjuntos, de modo que la decisión de autoría y la lectura visual puedan recaer sobre la misma pieza.
2. Extender la curaduría, hoy registrada sobre 68 registros, al inventario unificado, conservando el registro de cada decisión y su reverso.
3. Normalizar el vocabulario visual —color, estilo, tipo— de modo que las palabras con que se describe mi trabajo sean mías y consistentes, y corregir la tipificación donde no coincide con lo que la pieza es.
4. Construir la exportación que convierte una selección decidida en un portafolio publicable y en un archivo preservado con su procedencia.
5. Producir una primera edición del portafolio y dejar el instrumento documentado y utilizable por otros artistas, sujeto a prueba de uso y a la licencia que yo defina."""},

 {"campo":"Plan de implementación","version":"única","nota":"Sección b. Doce meses desde enero de 2027, trabajo individual",
  "texto":"""Meses 1-2 · Unificación de los dos inventarios y curaduría del conjunto. Reconciliar identificadores para que una decisión y una lectura puedan recaer sobre la misma pieza; localizar los archivos de las piezas que tienen título propio y no tienen imagen. Continuar el registro de decisiones ya iniciado, con su motivo y su reverso. Producto: inventario unificado y decidido.

Meses 3-4 · Normalización del vocabulario visual y de las relaciones. Reprocesamiento y comparación del orden antes y después. Producto: vocabulario consistente y comparación documentada.

Meses 5-7 · Construcción de la exportación: de selección decidida a artefacto de portafolio y a archivo preservado. Producto: exportador funcionando.

Meses 8-9 · Primera edición del portafolio y prueba de acceso. Producto: portafolio.

Meses 10-11 · Segunda vuelta de curaduría sobre lo publicado y documentación del método. Producto: método escrito.

Mes 12 · Cierre, respaldo e informe de uso a la Fundación."""},

 {"campo":"Justificación del interés en participar","version":"única","nota":"Sección b",
  "texto":"""Postulo a esta categoría porque sus bases nombran el proyecto antes de que yo lo describa: aceptan propuestas de archivo y preservación del propio trabajo. Es lo que vengo haciendo sin llamarlo así.

El momento importa. El instrumento está a un paso de servir y ese paso no se da solo: se da sentándose a decidir sobre miles de registros, que es trabajo lento y sin recompensa inmediata. Una beca es la forma de financiamiento que permite ese trabajo, porque no exige convertirlo antes en producto ni en exhibición.

La conexión con América Latina es de nacionalidad y de sitio: el archivo se produjo en Chile y el proyecto se realizará en Chile."""},

 {"campo":"Presupuesto: destino de los fondos","version":"única","nota":"Sección c. Desglose adjunto en Excel o PDF",
  "texto":"""Se solicitan US$8.734 de los US$10.000 disponibles. No se solicita el máximo: se solicita lo que cuesta el trabajo descrito.

Personal, US$7.500 (85,9%). Seis meses de dedicación a la curaduría del inventario y tres meses al desarrollo de la exportación. Es un proyecto de decisión y de tiempo, no de materiales.

Operación, US$1.234 (14,1%). Recaptura de material degradado antes de poder curarlo (US$400); almacenamiento y respaldo del archivo preservado durante doce meses (US$144); diseño gráfico y maquetación del portafolio como servicio puntual con entregable, sobre una selección ya decidida por mí (US$550); comisión bancaria y diferencia de cambio de la transferencia internacional (US$140).

El desglose por línea, con cantidad, unidad, precio unitario, actividad, periodo, producto y origen de cada valor, se adjunta como archivo. Ninguna cifra se presenta como cotización obtenida: son estimaciones y referencias de mercado, declaradas como tales."""},

 {"campo":"Adjuntos: estado","version":"única","nota":"Sección d",
  "texto":"""CV: lo aporta el titular.
Documento de identidad: lo aporta el titular.
Portfolio artístico: hay un índice de selección candidata preparado sobre material propio, con criterio explícito y reproducible. La selección final y los títulos los decide el titular; el PDF se arma con esa decisión.
Presupuesto: listo, en CSV convertible a Excel o PDF.
Anexo del proyecto (optativo): ficha técnica del instrumento y salida fechada de la prueba de estado."""},
]

NOTA_FINAL = """
## Verificación contra las bases

| Requisito | Momento | Estado |
|---|---|---|
| Prácticas abocadas a las artes visuales | postular | Cumple: archivo de obra visual propia |
| Investigación o creación, incluido archivo del propio trabajo | postular | Cumple literalmente |
| Mayor de 18 años | postular | Lo declara el titular |
| Conexión significativa con América Latina | postular | Cumple: sitio del proyecto en Chile |
| Una sola categoría | postular | Cumple: sólo Artistas |
| Titular único | postular | Cumple: persona natural |
| No fines comerciales | postular | Cumple: ninguna rama privada aparece como objetivo |
| No deudas, gastos legales ni recaudación | postular | Cumple |
| Sin apoyo de la Fundación en 12 meses previos | postular | Lo declara el titular |
| Sin vínculos ni parentesco hasta 2º grado con la Fundación | postular | Lo declara el titular |
| No es organismo ni institución estatal | postular | Cumple |
| **Cuenta bancaria a nombre del titular** | **adjudicación** | **No bloquea el envío** |
"""
