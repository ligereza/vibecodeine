# Plan Mesa de Montaje

## Decision de arquitectura

No se continua parchando el Estudio actual. Se reconstruye su superficie de
navegacion dentro del mismo Hub y en el mismo puerto. Se conservan el archivo
original, los contratos, el ledger y las APIs utiles; se reemplaza el modelo de
interaccion que hoy mezcla archivo, mesa, orbita y sugerencias.

El objetivo no es mostrar mas tarjetas. Es que el artista pueda recorrer el
archivo, entender por que el copiloto propone una relacion y decidir sin salir
de una mesa visual estable.

## 1. Modelo de datos

La interfaz no tratara cada media como una obra. Mantendra cuatro niveles:

- `registro`: post, reel, historia, carrusel o archivo audiovisual original.
- `obra`: entidad curatorial que puede nacer de uno o varios registros.
- `contexto`: evento, venue, artista, cliente, productora, ciudad o fecha.
- `relacion`: hipotesis que conecta registros, obras o contextos.

Cada objeto conserva un `source_id` estable. La misma pieza puede proyectarse en
varias lecturas sin duplicar el registro ni copiar el archivo. Una historia
puede ser evidencia de una obra, pero no se convierte en obra por aparecer en
la misma fecha.

## 2. Estado unico de la mesa

Se reemplazan los estados dispersos por un solo estado de escena:

```text
scene
  active_record_id
  visible_record_ids
  selected_pass_ids
  lens
  relation_hypotheses
  accepted_relations
  rejected_relations
  discarded_record_ids
  positions_by_source
  inspector
```

Reglas:

- Un `source_id` produce un solo nodo visible.
- Una sugerencia nunca crea otro nodo: solo agrega halo, borde o conexion al
  nodo existente.
- La posicion es estado de navegacion; la decision y la relacion son memoria
  persistente.
- La mesa no debe depender de scroll vertical para mostrar la accion vigente.

## 3. Superficie topologica unica

La escena ocupa el Estudio completo y el mapa es el editor; el portafolio queda
como una proyeccion posterior:

- **Barra de lentes:** `fecha`, `carrusel`, `evento`, `venue`, `artista`,
  `cliente`, `semantica`.
- **Campo GTM central:** cada nodo conserva su posicion relativa del mapa real;
  el registro activo no se fuerza al centro ni se convierte en una portada.
- **Capas visibles:** obra, registro, entidad/contexto y candidato usan forma y
  borde distintos. La jerarquia aparece en las conexiones, no en una grilla de
  formularios.
- **Conexiones fantasma:** lineas o halos de color para las hipotesis del
  copiloto. El color indica canal, no certeza absoluta.
- **HUD de nodo:** aparece junto al nodo enfocado y contiene la evidencia y la
  decision; es una herramienta contextual, no la estructura del editor.
- **Ventana de escena:** el navegador recibe 10 o 20 nodos y sus coordenadas
  GTM, mientras MAK conserva el archivo completo de 7044 registros.

La vista no sera una grilla Excel ni un grafo saturado. Sera una composicion de
foco y contexto: un centro claro, pocas relaciones legibles y una lente activa.
GTM calcula la proyeccion inicial. La retroalimentacion humana modifica el
espacio de caracteristicas y la proxima proyeccion; el mapa nunca se convierte
en una nueva fuente de verdad.

## 4. Gestos y navegacion

Todos los nodos comparten el mismo comportamiento; no habra una regla distinta
para orbita, sugerencia y galeria:

- `pointerdown` guarda la posicion inicial.
- Si el movimiento supera un umbral, entra en modo arrastre.
- Arrastrar mueve el nodo y nunca registra una decision.
- Soltar sin movimiento enfoca el nodo y abre el inspector fijo.
- Doble clic en escritorio convierte el nodo en registro activo.
- En celular, tocar enfoca y el inspector ofrece `abrir registro`; no se
  dependera del doble clic tactil.
- La rueda o gesto de zoom cambia la escala del canvas, no la pagina completa.
- `Esc` cierra el inspector y conserva la pieza activa.
- Las sugerencias aceptadas quedan verdes; las rechazadas quedan marcadas pero
  no desaparecen; un registro descartado queda gris y sale de la capa obra.

## 5. Inspector contextual

El inspector no mostrara siempre las mismas acciones. Su contenido depende de
lo que esta enfocado:

### Si se enfoca una relacion

- canal: fecha, carrusel, evento, venue, artista, cliente o semantica;
- fuente y evidencia concreta;
- fuerza y limite de la inferencia;
- `aceptar vinculo`;
- `rechazar vinculo`;
- `abrir registro`.

### Si se enfoca un registro

- media real, fecha, descripcion original y origen;
- `seleccionar para pasada`;
- `obra`;
- `registro`;
- `no es obra`;
- `revisar luego`.

`rechazar vinculo` no elimina ni desacredita el registro. `no es obra` es una
clasificacion del registro y se guarda como decision de registro con razon
`no_es_obra`; conserva el archivo original y lo excluye de futuras sugerencias
curatoriales.

## 6. Copiloto

El copiloto recibira solo el registro activo, la lente y la ventana de 10/20.
No calculara un mapa GTM de 7044 items en cada clic.

Su salida sera una lista de hipotesis estructuradas:

```text
target_id
channel
relation_type
evidence
confidence
scope: declared | exploratory
next_action
```

La interfaz traducira esa salida a conexiones visuales. El texto sera evidencia
del inspector, no el producto principal. Si no hay evidencia, el borde se marca
como exploratorio y no se presenta como hecho.

## 6.1. Orden rapido antes de relacionar

Relacionar no es el primer gesto. El editor tiene dos modos dentro de la misma
escena:

- `ordenar`: un click selecciona varios nodos y una barra contextual los marca
  como `obra`, `registro`, `revisar` o `descartar`; no crea relaciones.
- `relacionar`: doble click o cambio explicito de modo abre la evidencia y las
  hipotesis del copiloto para una pregunta concreta.

La clasificacion rapida se persiste por lote mediante el endpoint existente de
Hub extendido como `classify-batch`, usando el contrato de clasificaciones y
sin crear otra base. El descarte conserva el registro en el ledger y lo retira
solo de la escena activa.

La probabilidad se actualiza por dimensiones independientes: `obra/registro`,
`personal/cliente`, `visual/promocional`, contexto y grupo. No se usa un titulo
aislado como evidencia. Las relaciones son una consecuencia posterior de los
grupos y correcciones humanas.

## 7. Memoria y aprendizaje

Cada gesto persistente registra:

- `source_id` y `target_id`;
- `decision_scope`: `relation`, `record` o `pass`;
- `decision`: aceptar, rechazar, descartar o revisar;
- `reason_code`;
- lente activa;
- sesion y tamano de pasada;
- evidencia mostrada al artista.

Aceptar una relacion aumenta el peso de ese canal. Rechazarla reduce esa
hipotesis. Marcar `no_es_obra` no borra el registro ni contamina la verdad del
archivo: solo lo excluye de la capa curatorial. El ledger sigue siendo
append-only y los resultados no se publican automaticamente.

## 8. Backend y rendimiento

Se reutilizan `hub.py`, `copilot.py`, `ledger.py` y los contratos existentes.
Solo se agregan superficies concretas si una pieza existente no alcanza:

- escena paginada por lente, fecha y pasada;
- relaciones para el registro activo;
- decision unificada con alcance explicito;
- estado de sesion de posiciones, separado del ledger curatorial.

La pagina no creara thumbnails nuevos por defecto. Usara los `asset_path`
existentes, carga diferida, ventana virtual de 10/20 y videos bajo demanda.
La fuente completa seguira en MAK; el navegador recibe solo lo necesario para
la escena actual.

## 9. Orden de implementacion

1. Congelar el Estudio experimental actual; no sumar otro parche de eventos.
2. Definir y probar el estado unico de escena y el identificador unico por
   registro.
3. Implementar un renderer limpio de canvas, linea temporal e inspector dentro
   de `#estudio-app`.
4. Separar el modo `ordenar` del modo `relacionar` sin duplicar la escena.
5. Migrar las hipotesis actuales a conexiones sobre nodos existentes y eliminar
   la duplicacion orbita/sugerencia.
6. Implementar gestos con umbral de arrastre, foco, doble clic y alternativa
   tactil.
7. Conectar las decisiones contextualizadas al ledger sin borrar medios.
8. Entregar la proyeccion GTM solo para la ventana activa y conservar el ajuste
   completo en MAK; no serializar 7044 coordenadas al navegador.
9. Agregar aprendizaje incremental tipo GNG sobre decisiones aceptadas y
   rechazadas; no llamarlo deep learning hasta que exista entrenamiento real.
10. Verificar la misma escena en escritorio y celular antes de volver a cargar
   material externo.
11. Ejecutar una pasada real de 10 registros. No pasar a 20 hasta comprobar que
   el sistema distingue navegar, seleccionar, relacionar y descartar.
12. Solo despues promover el bloque mecanico estable; no hacer commit o push de
   cada ajuste visual.

## Fase 1 ejecutada: atlas y campo rapido 2026-08-09

El motor ya separa dos escalas de tiempo dentro de las piezas existentes:

- `atlas`: topologia GTM versionada y estable durante una pasada humana;
- `field`: aprendizaje rapido que cambia probabilidades, incertidumbre y
  cobertura sin mover la geometria;
- `active seed`: seleccion de casos por ganancia de informacion, diversidad y
  zonas sin cobertura, agrupando carruseles como una unidad;
- `evidence/resonance`: hechos declarados y lecturas conceptuales viajan por
  espacios distintos y resonancia nunca modifica identidad ni publica;
- `evaluation`: validacion leave-one-out y gate explicito antes de cualquier
  automatizacion.

La metrica predictiva usa el vector estructural de 32 dimensiones conservado
en memoria. La cobertura espacial usa las coordenadas GTM 2D. Esta separacion
evita usar una compresion visual como unica verdad estadistica y mantiene la
camara estable mientras el campo aprende.

Estado MAK medido: 7,044 registros, topologia
`16f75b4075c1d263`, 21 etiquetas, `active_learning_ready=true`,
`automation_ready=false`. Solo existen ejemplos humanos de `work` y `discard`;
faltan `record` y `review`. La precision leave-one-out actual no habilita
automatizacion porque el soporte de clases es incompleto. El gate exige 100
etiquetas, 1% de cobertura, cinco ejemplos por clase y macro-recall 0.75.

Coste medido despues del despliegue: ajuste frio 9.258 s; aprendizaje caliente
menor a 0.8 s; escena order cercana a 0.75 s. El coste frio se paga una vez por
topologia o cambio estructural, no en cada decision.

La fase siguiente no debe cambiar el motor. Debe reemplazar la traduccion
visual del campo: mostrar incertidumbre, cobertura, evidencia y resonancia como
propiedades espaciales; permitir decisiones comparativas y por regiones; y
eliminar la dependencia de formularios y popups extensos.

## 10. Prueba de aceptacion

La reconstruccion solo se considera util si una persona puede:

1. elegir fecha y pasada de 10;
2. enfocar un registro sin que se abra otra pagina;
3. ver media y evidencia en el mismo encuadre;
4. mover un nodo sin disparar una decision;
5. aceptar una relacion y verla verde;
6. rechazar una relacion sin perder registros;
7. marcar un registro como `no es obra` y encontrarlo luego en archivo;
8. abrir otro registro con doble clic o control tactil;
9. recargar y conservar las decisiones, no necesariamente las posiciones;
10. continuar con la siguiente pasada sin que aparezcan duplicados ni una lista
    infinita de paneles.

## 11. Criterio de cierre

No se declara terminado porque la pantalla se vea sofisticada. Se cierra cuando
la mesa permite navegar el archivo como artista, el copiloto explica sus
relaciones, las acciones no se confunden entre si y cada decision queda
trazable sin convertir una historia en obra por accidente.

## 12. Fase 2 ejecutada: campo cartografico 2026-08-09

La mesa ya no traduce el atlas a otra tabla. El atlas permanece fijo y la
interfaz dibuja encima cuatro campos intercambiables: incertidumbre, cobertura,
evidencia y resonancia. La vecindad del mapa tiene un tercer espacio tecnico,
`topology`, que organiza sin fingir una relacion semantica.

La zona visible se magnifica y relaja colisiones localmente; esta operacion es
solo de camara y no altera coordenadas canonicas. La decision aparece como un
compas radial alrededor de la pieza. El usuario puede decidir una pieza o
previsualizar una region corta antes de aplicar un destino comun. El modo
relacionar agrega aristas sobre la misma topologia en vez de reconstruir otra
escena.

Criterio alcanzado: el mapa informa donde el sistema sabe menos, diferencia
hecho de lectura poetica y permite una decision espacial sin mover archivos,
crear relaciones falsas ni promover contenido.

## 13. Fase unica siguiente: calibracion activa de la distancia

### Objetivo

Convertir una pasada humana corta en una mejora demostrable y reutilizable del
campo. La meta no es etiquetar 7.044 registros ni alcanzar una taxonomia final:
es aprender que dimensiones acercan o separan piezas para este artista, medir
si el aprendizaje generaliza y conservar la anomalia cuando no cabe.

### Ejecucion

1. Congelar una linea base real desde MAK: `topology_id`, revision, labels,
   matriz de confusion, macro-recall, calibracion, latencia y rendimiento de
   seleccion activa. No copiar los numeros de este documento sin medirlos.
2. Preparar una pasada de 20 unidades editoriales, no 20 archivos sueltos. La
   muestra mezcla fronteras ambiguas, zonas sin cobertura, stories, published
   media y carruseles; no fuerza una cantidad artificial por clase.
3. Instrumentar la pasada en la mesa existente: decision, tiempo, cambio de
   opinion, alcance individual/regional y contexto opcional. No agregar otro
   formulario, puerto, store ni interfaz.
4. Extender el campo rapido, no crear otro motor. Aprender pesos sobre el
   vector estructural existente usando dos tipos de senal: clase humana
   (`work/record/review/discard`) y restricciones de pares ya registradas
   (`misma obra`, relacion aceptada o rechazada). El atlas sigue inmovil.
5. Separar salida probabilistica de decision: calibrar probabilidades, mostrar
   incertidumbre y abstenerse cuando la distancia no discrimina. Ninguna
   prediccion se vuelve verdad, identidad ni promocion.
6. Reproducir las decisiones anteriores como benchmark. Comparar politica
   activa, seleccion aleatoria y campo previo con el mismo conjunto retenido.
   Medir macro-recall, Brier score, cobertura, rendimiento por decision y
   errores por clase; no declarar mejora desde una captura bonita.
7. Solo despues del benchmark, pedir a Watsonx y AWS una clasificacion ciega
   del mismo subconjunto. Sus respuestas son challengers: medir acuerdo,
   errores y costo frente al humano; nunca usarlas como gold label.
8. Si la distancia aprendida no supera la linea base dentro de la incertidumbre
   del test, descartarla como modelo y conservar sus resultados como evidencia
   negativa. No parchar el umbral para fabricar exito.
9. Dibujar el resultado en el mismo campo: regiones que ganaron cobertura,
   fronteras que siguen ambiguas y casos donde el sistema se abstiene. No
   convertirlo en dashboard ni mover coordenadas canonicas.
10. Cerrar con un protocolo repetible para futuros archivos/clientes: importar,
    tomar 20 decisiones, medir transferencia, ajustar solo si mejora y operar
    aun cuando Watsonx/AWS ya no existan.

### Criterio de salida

- una pasada humana trazable de 20 unidades;
- baseline y resultado evaluados sobre el mismo replay;
- probabilidades calibradas o abstencion explicita;
- ninguna clase ausente rellenada por ficcion;
- cero promociones automaticas y cero movimientos de archivos;
- latencia caliente de orden menor a 1.5 s en MAK;
- un informe corto que diga que mejoro, que empeoro y que no se sabe;
- continuidad demostrada con el motor local/determinista.

### Orientacion de pensamiento

No mapear un territorio como si tuviera una unica division correcta. Pensar el
archivo como espacio de fases: las categorias son atractores temporales y las
decisiones humanas son fuerzas que curvan una metrica, no cajones que capturan
objetos. `topology` significa vecindad, `evidence` significa relacion factual
respaldada y `resonance` significa lectura posible; nunca intercambiarlas.

La interfaz es un instrumento epistemico: debe mostrar donde el sistema duda,
que dato produjo una cercania y que parte proviene del artista. La anomalia no
se elimina para mejorar una metrica. Se conserva como posible semilla capaz de
cambiar el mapa. La autonomia buscada es saber preguntar, abstenerse y dejar
una accion concreta; no producir mas texto ni adivinar con seguridad estetica.

## 14. Fase 3 ejecutada: metrica activa con abstencion

La fase implemento la calibracion propuesta sin crear un motor paralelo. El
vector `declared-hashed32` mantiene su identidad y la nueva capa calcula una
distancia ponderada desde pares humanos. Pares de una misma etiqueta atraen;
pares de etiquetas distintas y relaciones rechazadas separan. Conflictos se
conservan pero se excluyen del ajuste.

El campo calcula el candidato, lo reejecuta sobre el replay existente y solo
lo activa si supera la distancia identidad en accuracy o macro-recall. En la
medicion viva de MAK hubo 21 labels, 111 pares positivos y 110 negativos, pero
el candidato empato exactamente la linea base (`0.857143` accuracy,
`0.859091` macro-recall). Por eso el sistema lo retiene como
`held_out_no_replay_gain` y sigue usando identidad. Esta es una mejora de
criterio, no una simulacion de aprendizaje.

Watsonx y AWS desafiaron ciegamente el mismo subconjunto de 21 registros una
vez medido el replay: Watsonx acerto `1/21` y AWS `9/21`. Las salidas quedan
aisladas como evidencia y no alteran el ledger ni el campo.

La proxima ejecucion valida necesita 20 decisiones humanas nuevas y una mejor
mezcla de `work`, `record`, `review` y `discard`. La mesa debe seguir siendo
la misma superficie; la metrica solo gana el derecho a activarse si el replay
lo demuestra.
