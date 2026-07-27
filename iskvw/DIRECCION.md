# Dirección de la cara visible — lo que se decidió

Conversación del 2026-07-27, entre el usuario y dos agentes. Esto NO es una
propuesta: son las decisiones que sobrevivieron a la discusión, con el motivo
por el que se tomaron. Quien vaya a construir la piel lee esto antes que nada.

`CONTRATO.md` dice qué no se puede romper. Esto dice **hacia dónde va**.

---

## 1. El sitio no escucha. Es el metrónomo.

Se descartó la idea de simular audio-reactividad. El visitante puede estar con
audífonos, con parlantes, en el subte con ruido, o en silencio: no hay forma de
saberlo y fingir que se sabe se nota en segundos.

La inversión: **el sitio tiene pulso propio y el visitante se alinea a él.**
Funciona igual en los cuatro casos porque no depende de ninguno.

## 2. El scroll es el instrumento

Es el único mecanismo que **no puede desincronizarse**, porque el gesto y el
evento visual son la misma cosa. Latencia cero por construcción.

```
scroll lento     → profundizar → una obra, nítida        (breakdown)
scroll rápido    → divergir    → varias, difusas         (build)
frenar de golpe  → resolver                              (drop)
```

La velocidad del dedo es a la vez el tempo y el diafragma. **Frenar es enfocar,
y enfocar es el acento.** No son dos controles: es uno.

## 3. Operativa, no legible

El visitante NO debe entender que existe esa correlación. Debe descubrirla por
accidente, como quien ajusta el foco de una cámara y de pronto ve la cara. Si
la entiende, el sitio se vuelve un catálogo con efectos.

## 4. La gramática es invariante. El contenido, variable.

**La decisión más importante de la conversación.** El archivo se reordena con el
paso de la gente, pero el reordenamiento no puede tocar cómo responde el gesto.

```
algoritmo cambia QUÉ obra aparece   → sí
algoritmo cambia CÓMO responde      → nunca
```

Si al frenar no resuelve porque el algoritmo interfirió, el visitante no se
desincroniza con su música: **se desincroniza consigo mismo**, que es peor. Un
instrumento que responde distinto cada vez es una máquina tragamonedas.

## 5. Nada de parpadeo rápido

Se propuso parpadeo a 10-14 Hz y **se retiró entero**. Es el rango documentado
de disparo de epilepsia fotosensible; las pautas de accesibilidad fijan el
límite en tres destellos por segundo.

No es prudencia de manual: el público de este trabajo está en fiestas, y parte
de esa gente está bajo efectos que bajan el umbral convulsivo. Quien firma esto
trabaja en reducción de daños.

El ancla es fisiológica y lenta: **pulso respiratorio, 12 a 20 ciclos por
minuto** — menos de 0,3 Hz, cuarenta veces más lento que la zona de riesgo.
Invisible hasta que se nota, y ancla al cuerpo igual.

## 6. Dos pieles, misma data

```
terminal    → puerta CV: legible, mapeada, filtros, treinta segundos
experiencia → puerta obra: operativa, sin mapa, se habita
```

Ya existe la primera (`piel/terminal/`, verificada con cero errores de consola).
No hay que elegir entre CV y obra: hay que elegir **cuál abre por defecto**, y
eso es decisión del autor.

## 7. La URL es el mapa que no se muestra

Sin migas de pan, sin barra de progreso, sin coordenadas. Pero **una obra
resuelta tiene dirección propia**.

Motivo concreto: alguien que podría contratarlo ve algo, le interesa, quiere
mostrárselo a un socio. Sin dirección, no puede. Para una obra la desorientación
es coherente; para un CV es una pérdida funcional.

Y cierra el círculo: el recorrido viaja en la URL, así que **el objeto que el
visitante se lleva es el mapa que no se le dio**.

## 8. Inercia asimétrica

```
bajar (profundizar) → pesada, como entrar al agua
subir (divergir)    → liviana, como flotar
```

Es el mismo resorte con distinta constante. Una línea de diferencia, y refuerza
la metáfora sin que nadie la piense. Subir no es "volver": es **perder el foco**.

## 9. El drop varía

Si frenar produce siempre lo mismo, se agota en tres visitas. Alterna:

- la imagen se cristaliza desde el ruido
- capas que se alinean en un patrón que no estaba
- el ruido se condensa en texto legible

Y **a veces no resuelve en información**, sino en textura o color. Con un límite:
"a veces no legible" sí, "nunca legible" no — un cliente potencial tiene que
poder llegar a leer algo alguna vez.

## 10. La zona intermedia es incómoda a propósito

Entre rápido y lento hay una velocidad donde nada está del todo enfocado. No es
un error de diseño: obliga a elegir entre detenerse o acelerar. Nadie se queda
en el limbo.

---

## Lo que se descartó, y por qué

| descartado | motivo |
|---|---|
| Barras de espectro tipo VU | Se ve falso al instante |
| Un solo BPM fijo | Imposible que coincida; cuando falla, es error obvio |
| Pedir micrófono | Rompe la entrada y genera desconfianza |
| Botón de música de fondo | El visitante ya está escuchando algo |
| LLM en el navegador | 300 MB antes de ver nada; choca con la fluidez |
| Scroll infinito con muchos nodos animados en el DOM | Medido: 9.600 elementos animados cuelgan un navegador de escritorio |

## Referencias que sí valen

Ikeda (*datamatics*), Reich (obras de fase), *Rez*, *Thumper*,
Lozano-Hemmer (*Pulse Room*), y la señalética de andenes japonesa —
patrones que se animan por el movimiento del tren, no por sí mismos.

De la lista de portafolios revisada: **Eliasson** (*Your uncertain archive*) es
la competencia conceptual más cercana, pero corre contra APIs propias — es un
servicio, no un archivo que viaje. **Rozendaal** es el modelo del objeto
autónomo que se comparte solo. **Samuel Day** demuestra que el aspecto "hecho a
medida" se consigue con un constructor comercial más animación vectorial
(Lottie), no con ingeniería propia.

Ninguno de los catorce revisados deja que el visitante modifique el archivo.
