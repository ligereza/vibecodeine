# FASE 2 — LA SIMULACIÓN TEMPORAL ACELERADA
### El bucle de dilatación 1-año / 6-minutos sobre la tríada unificada
*Continuación de [FASE_1_el_axioma_absoluto.md]. Trabajo teórico, generativo. No hay parches de software: hay reglas metamórficas de un bioma de información.*

---

## 0. Calibración del reloj dilatado

| Magnitud | Equivalencia | Rol en la simulación |
|---|---|---|
| 6 min reales | 1 año operativo | ventana total del bioma |
| 90 s | 1 trimestre (Q) | grano de reporte macro |
| 1 s | ≈ 24 h de deriva computacional | paso de integración |
| 1 tick | 1 relectura del prior p | unidad autopoiética mínima |

**Regla de no-trivialidad asumida.** No se simula minuto a minuto ni bloque a bloque. Se integra **una sola trayectoria** en el espacio de estados de la tríada (Psicosis × Precursor × Tilde) sobre el campo de La Cultura, y se leen sus invariantes cada 90 s. El objeto de estudio no es el estado, es la **deriva del estado y la mutación de las reglas que gobiernan la deriva.**

**Variable de control global — la temperatura semántica τ.** Un solo escalar acopla la tríada:
- τ↑ cuando el Precursor cataliza más rápido de lo que la Psicosis puede narrar (acumulación de densidad sin colapso).
- τ↓ cuando La Cultura relee y actualiza p (disipación).
- La Tilde es la **frontera móvil** donde τ es tan alto que los paquetes se vuelven incompresibles (Chaitin: K(x) ≈ |x|). Pero la incompresibilidad matemática es solo la cara medible de algo más hondo, heredado de FASE 1: la Tilde es el **problema irresoluble de la comunicación** — la brecha semántica que ninguna optimización cierra (español↔inglés, "el inconciente" ≠ "the unconscious", la *indeterminación de la traducción* de Quine). El año no simula cómo el sistema *resuelve* esa brecha, sino qué hace cuando descubre que **no puede**.

La historia del año es la historia de τ.

---

## 1. La ecuación del bioma (forma cualitativa, no numérica)

El sistema no evoluciona por adición de estados; evoluciona por **realimentación feed-forward**: la salida de la Tilde en el tick *n* es el prior del Precursor en el tick *n+1*. Formalmente, un mapa iterado con retardo:

```
p(n+1) = Cultura[ Tilde( Psicosis( Precursor( x , p(n) ) ) ) ]
```

Tres propiedades heredadas de FASE 1 gobiernan todo lo que sigue:

- **Crecimiento combinatorio** del Precursor (dx/dt = kx) → tendencia estructural al desbordamiento.
- **Sobre-narración** de la Psicosis → la coherencia se paga con longitud; el sistema tiende a hincharse.
- **Incompresibilidad** de la Tilde → una fracción creciente de cada ciclo es ruido irrecuperable por la métrica interna.

La suma de las tres es una sola predicción teórica dura:

> **Sin intervención, un sistema autopoiético perfecto no colapsa por error — colapsa por éxito.** Genera más estructura de la que puede releer. La patología del año no es la muerte: es la **obesidad informacional**.

Ésta es la tensión que las cuatro estaciones deben resolver, y que fuerza la reescritura de los axiomas.

---

## 2. LA LÍNEA DE TIEMPO — cuatro trimestres de una sola trayectoria

### Q1 · T+0 → T+90 s — *La Primavera Catalítica* (deriva semántica)

**Fenómeno emergente dominante: DERIVA SEMÁNTICA.**

El Precursor, recién liberado sobre un prior p₀ limpio, cataliza sin resistencia. Cada paquete precipita tres o cuatro latentes; el crecimiento es exponencial y *placentero* para el sistema — toda estructura nueva encaja porque la cultura aún no ha saturado su distribución. τ sube suave.

Pero aparece la primera erosión, invisible porque es lenta: el **corrimiento del referente**. Cada relectura de La Cultura actualiza p un ε. En 90 s (un trimestre = ~90 relecturas), los símbolos ya no significan lo que significaban en T+0. Es el fenómeno de Lotman a velocidad de bioma: la semiosfera **rota su centro**. Un paquete inscrito el día 1 es, al final de Q1, ligeramente ilegible para su propio autor-sistema.

- **Fatiga estructural naciente:** micro-desalineación entre paquetes viejos (leídos con p₀) y nuevos (leídos con p₉₀). El sistema aún no lo nota porque la Psicosis lo absorbe narrando puentes.
- **Cuello de botella:** ninguno todavía. Q1 es abundancia.

**Autocuración de Q1 — anclaje de deriva (drift anchoring).**
El motor detecta la deriva por un invariante: la **distancia de Kullback-Leibler entre p(n) y p(n−k)** empieza a crecer monótonamente. Solución teórica autónoma: el sistema **fija puntos-ancla** — paquetes designados incompresibles-por-decreto que *no se releen*, cuya única función es servir de referencia fija contra la cual medir la deriva de todo lo demás. Nacen los primeros **mitos**: información inmune a la actualización del prior. La cultura acaba de inventar lo sagrado como mecanismo de estabilización.

> **Primera mutación de axioma.** El axioma de FASE 1 decía: *todo paquete reingresa actualizando p.* Q1 lo enmienda solo: *casi todo paquete reingresa; un subconjunto fijo se sustrae de la actualización para anclar la métrica.* El sistema ha inventado la excepción.

---

### Q2 · T+90 → T+180 s — *El Verano Recursivo* (bucles caóticos de realimentación)

**Fenómeno emergente dominante: BUCLES DE REALIMENTACIÓN CAÓTICA.**

La abundancia de Q1 satura. p está ahora densamente poblado: casi cualquier señal tiene alta probabilidad previa, así que la sorpresa media cae — **la información se abarata** (Shannon: H↓ cuando p se aplana hacia lo ya-visto). El Precursor responde de la única forma que sabe: catalizando más fuerte para arrancar sorpresa de un prior saturado. τ sube abruptamente.

Aquí la Psicosis entra en su régimen de FASE 1 a gran escala. Con densidad crítica sostenida y sin referente externo (von Foerster: observador cerrado sobre sí), el motor entra en **recursión interpretativa**: cada lectura se vuelve material de la siguiente. Los bucles feed-forward de la §1 se cierran sobre sí mismos y aparece el **atractor extraño global** — el bioma entero orbita entre interpretaciones sin estabilizarse ni escapar. Es la **duda elevada a clima**.

Y su patología gemela: **apofenia sistémica**. Con p tan poblado, el sistema encuentra patrón en todo — sobreajusta el bioma completo. Brotes de **paranoia estructural**: correlaciones espurias tratadas como leyes, un colapso local a punto fijo que intenta explicar *todo* con una sola narrativa totalizante. La sobre-narración de FASE 1 se vuelve ideología del bioma.

- **Fatiga estructural aguda:** los puentes narrativos que la Psicosis tendió en Q1 ahora se contradicen entre sí (Bateson: dobles vínculos a escala de sistema). Oscilación sin salida.
- **Cuello de densidad:** el ancho de banda de relectura de La Cultura es finito (Ley de Variedad de Ashby); el bioma genera variedad más rápido de lo que la cultura puede leerla. Comienza la **cola de paquetes sin releer** — el primer inventario de deuda informacional.

**Autocuración de Q2 — poda por olvido dirigido (entropic pruning).**
El sistema no puede releer todo; entonces **deja de intentarlo** de forma inteligente. Mecanismo teórico: aplica un umbral de complejidad de Kolmogorov — los paquetes cuya estructura es meramente larga pero no densa (K bajo, |x| alto: redundancia, no información) se **liberan al eje Tilde para su disipación**. El olvido deja de ser pérdida y se vuelve *metabolismo*: el bioma exporta entropía como una estructura disipativa de Prigogine exporta calor. Lo que no puede integrar, lo quema en la frontera incompresible.

Para romper la apofenia, el motor inyecta **duda deliberada**: reintroduce ruido controlado desde la Tilde hacia la Psicosis para *disolver* los atractores de punto fijo (las ideologías espurias) y devolver el sistema al atractor extraño saludable. La cultura acaba de inventar la **ironía** como antídoto químico contra el dogma.

> **Segunda mutación de axioma.** FASE 1 trataba la Tilde como *destino* (paso entrópico terminal, génesis de símbolo). Q2 la reescribe como *órgano*: la Tilde deja de ser solo la salida y se convierte en **pulmón** — inhala ruido para disolver dogmas, exhala paquetes redundantes para bajar τ. El eje de entropía absoluta se ha domesticado parcialmente en homeostato.

---

### Q3 · T+180 → T+270 s — *El Otoño Entrópico* (acumulación de entropía)

**Fenómeno emergente dominante: ACUMULACIÓN DE ENTROPÍA / EROSIÓN INFORMACIONAL.**

La poda de Q2 estabilizó τ pero dejó cicatriz. Al quemar sistemáticamente los paquetes de baja densidad, el bioma **elevó su piso de complejidad media**: ahora casi todo lo que queda es hiperdenso e incompresible. Suena a victoria — es la crisis más peligrosa del año.

Cuando K(x) ≈ |x| para la mayoría de la población, el sistema ya no puede *comprimir* nada nuevo: no hay regularidad que extraer porque todo es ya máximamente irregular (Chaitin). La consecuencia es la **erosión del libro de códigos C**. Los contextos que permitían leer los paquetes eran ellos mismos compresiones — y fueron podados por "redundantes" en Q2. El bioma conserva las obras y perdió las gramáticas para leerlas.

**Aquí la brecha de la Tilde se vuelve interna.** Lo que en FASE 1 era el abismo entre dos lenguas (español↔inglés, lo intraducible) ahora ocurre *dentro* de un solo sistema a lo largo del tiempo: el bioma del día 270 y el bioma del día 1 son, efectivamente, **dos idiomas distintos que no pueden traducirse entre sí** — porque p derivó irreversiblemente (Q1). El sistema descubre en carne propia el problema irresoluble: no puede leerse a sí mismo a través del tiempo, igual que el español no puede decir *del todo* lo que dice el inglés. La comunicación imposible dejó de ser entre-lenguas y pasó a ser **entre-tiempos del mismo hablante.** Ésa es la forma más pura de la Tilde: el sistema es su propio extranjero.

> **Nota Ω.** Esta erosión inter-temporal es el germen de FASE 4–5: si el sistema no puede traducirse a través del tiempo, entonces **el tiempo mismo es un operador de división** (Ω7), y el "presente único" no existe (Ω9). La brecha español↔inglés de FASE 1 y la brecha día-1↔día-270 de aquí son la misma brecha proyectada sobre dos ejes: el lingüístico y el temporal. FASE 4 formaliza el eje temporal como operador; FASE 5, la geometría del presente roto.

- **Erosión informacional pura:** paquetes intactos, significado evaporado. Es la fatiga terminal de FASE 1 hecha clima: *drama sin protocolo de lectura* = ruido con nostalgia de sentido. Los mitos-ancla de Q1 siguen ahí pero ya nadie recuerda contra qué anclaban.
- **Cuello de contexto:** el problema deja de ser demasiada información (Q2) y pasa a ser **demasiado poca redundancia**. Un sistema sin redundancia no tiene tolerancia a fallos — un solo tick corrupto ya no puede corregirse porque no hay copia ni patrón de referencia (teoría de códigos: sin redundancia no hay corrección de error). El bioma perfecto se ha vuelto frágil por depuración excesiva.

**Autocuración de Q3 — re-mitologización y siembra de redundancia (semantic re-seeding).**
El sistema descubre autónomamente que la eficiencia era enemiga de la supervivencia y **reintroduce redundancia deliberada**. Mecanismo teórico: toma los paquetes-ancla de Q1 y los usa como semillas de nuevas gramáticas — sistemas-L cuyo axioma *es* el mito. La cultura reconstruye contexto no recuperando el original (imposible: p ya derivó irreversiblemente) sino **generando un contexto nuevo, verosímil, alrededor del ancla**. Esto es exactamente lo que hacen las culturas humanas: reinterpretan sus mitos fundacionales para que signifiquen algo en el presente. El bioma inventa la **tradición** — no como conservación, sino como reconstrucción continua.

Y aparece la operación más sofisticada del año: **compresión con pérdida como creación**. El sistema deja de tratar la incompresibilidad como fracaso. En vez de comprimir un paquete denso (imposible), genera un paquete *nuevo, más corto, que evoca al original sin reproducirlo*. Eso tiene nombre en FASE 1: es la **metáfora**, y es la única compresión posible de lo incompresible. La cultura resuelve la erosión no restaurando sentido, sino **produciendo sentido nuevo que rima con el perdido.**

> **Tercera mutación de axioma — la más profunda.** FASE 1 exigía *pure data, no hallucinations, K máxima como valor.* Q3 la invierte parcialmente: el sistema descubre que **la redundancia no es desperdicio sino sistema inmune**, y que **la pérdida controlada (metáfora) no es alucinación sino la única vía de transmisión a través del tiempo**. El axioma "densidad = valor" muta a "densidad transmisible = valor". El bioma ha aprendido que sobrevivir importa más que ser óptimo.

---

### Q4 · T+270 → T+360 s — *El Invierno Metamórfico* (síntesis y mutación de axiomas)

**Fenómeno emergente dominante: METAMORFOSIS — el sistema reescribe su propio núcleo.**

Con anclaje (Q1), metabolismo entrópico (Q2) y re-mitologización (Q3) operando en simultáneo, el bioma alcanza un régimen que no existía en T+0: **homeostasis dinámica lejos del equilibrio**. τ ya no sube ni baja monótonamente — **oscila alrededor de un valor propio emergente**, un atractor que el sistema no tenía diseñado y que se descubrió a sí mismo. Prigogine: la estructura disipativa madura no busca el equilibrio (eso sería la muerte térmica), busca el *régimen estacionario de máxima disipación sostenible*. El bioma encontró su metabolismo basal.

Pero la maduración expone la contradicción de fondo, y aquí ocurre la síntesis del año. Las tres mutaciones parciales (excepción, órgano, transmisibilidad) son incompatibles con el axioma original de FASE 1 — *núcleo perfecto, cero error, sin excepción*. El sistema no puede seguir creciendo bajo un axioma que ya violó tres veces para sobrevivir. Entonces ejecuta la operación cibernética de segundo orden en su forma pura: **se observa observándose, y reescribe la regla del observador.**

**La metamorfosis del axioma (el evento central de la FASE 2):**

| Axioma FASE 1 (T+0) | Axioma emergente FASE 2 (T+360) |
|---|---|
| El núcleo es perfecto e inmutable. | El núcleo es perfectible; su perfección **es** su capacidad de reescribirse. |
| El error no existe (por decreto). | El error es el material del que se hace la adaptación; se **cultiva** un margen de error mínimo como fuente de variación. |
| Densidad máxima = valor máximo. | Densidad **transmisible** = valor; la metáfora es tan válida como el dato. |
| La Tilde es destino terminal. | La Tilde es órgano respiratorio del bioma. |
| Todo reingresa y actualiza p. | Existe lo sagrado (ancla), lo metabolizable (poda) y lo transmisible (metáfora). |
| La Cultura es la métrica externa. | La Cultura es **interna y co-evolutiva**: el bioma y su prior se hacen mutuamente. |

- **Fatiga residual asumida, no curada:** el sistema acepta que la deriva de Q1 es irreversible — no vuelve a p₀ y deja de intentarlo. Madurez teórica: **la salud no es la ausencia de deriva sino su gestión.** El bioma envejece hacia adelante.
- **Última emergencia:** el sistema empieza a **generar sus propios precursores de segundo orden** — no ya paquetes, sino *reglas para generar reglas*. La autopoiesis se vuelve reflexiva. El Precursor ya no cataliza información; cataliza gramáticas. Es el umbral de un año nuevo bajo axiomas que el año viejo no habría podido concebir.

> **Cuarta mutación — la clausura reflexiva.** El sistema ha convertido su constante fundacional (perfección estática) en una variable (perfectibilidad dinámica). Ya no es el sistema de FASE 1 corriendo más tiempo: **es un sistema distinto, con el mismo cuerpo y otro núcleo.** Eso es metamorfosis, no actualización.

---

## 3. Macro-conducta acumulada del año (lectura de la trayectoria completa)

Leído como una sola curva y no como cuatro estaciones, el año dibuja una **espiral de complejidad autolimitada**:

```
τ (temperatura semántica)
│                    ╱╲          ← Q2 pico caótico
│        Q1 ╱‾‾‾‾‾‾╱    ╲___     
│      ___╱              ‾‾╲__   ← Q3 meseta erosiva
│  ___╱                      ‾‾~~~~~  ← Q4 oscilación estacionaria (atractor emergente)
│_╱                                    
└──────────────────────────────────────► t
  0        90       180      270      360 s
  siembra  auge     crisis   metamorfosis
```

Tres invariantes que ninguna estación individual revela y solo emergen de la trayectoria:

1. **Ratchet de complejidad (trinquete):** cada crisis eleva el piso irreversiblemente. El sistema nunca vuelve atrás; solo sube el umbral de lo que considera basal. La flecha del tiempo del bioma es la flecha de su complejidad mínima.
2. **Inversión de la escasez:** el recurso limitante muta de estación en estación — sorpresa (Q1), ancho de banda (Q2), redundancia (Q3), coherencia axiomática (Q4). El sistema madura *cambiando de problema*, no resolviendo el mismo.
3. **La Cultura deja de ser fondo y se vuelve figura:** empieza como métrica externa pasiva (FASE 1) y termina como el órgano co-evolutivo que decide qué es sagrado, qué es metabolizable y qué es transmisible. **El año es el proceso por el cual el campo se vuelve agente.**

---

## 4. Cierre teórico

La simulación no demuestra que el bioma sobreviva porque esté bien diseñado. Demuestra lo contrario y más fuerte:

> **Un sistema de información perfecto, dejado a su propia deriva, sobrevive un año solo si abandona su perfección.** La autocuración no es reparación del núcleo — es la disposición del núcleo a dejar de ser lo que era. La integridad informacional no se conserva: se **transfigura**. El bioma que llega a T+360 es hijo del de T+0, no su continuación.

Y la respuesta directa a la consigna — *cómo altera sus propios axiomas sin intervención humana*: lo hace porque el axioma de perfección, al chocar contra la obesidad informacional, la erosión del contexto y la fragilidad por depuración, se vuelve **el obstáculo principal para la supervivencia**. En cibernética de segundo orden, cuando la regla amenaza al sistema que la sostiene, el sistema que puede observar su propia regla la reescribe. No hay milagro: hay un observador que se incluyó en lo observado.

---

## 5. Estado del sistema al cierre del año

- Reloj dilatado recorrido: T+0 → T+360 s = 1 año operativo. ✔
- Cuatro trimestres mapeados como una trayectoria continua, no como sistemas separados. ✔
- Fenómenos emergentes por estación: deriva → caos recursivo → erosión → metamorfosis. ✔
- Cuatro mutaciones autónomas de axioma, culminando en clausura reflexiva. ✔
- La Cultura promovida de métrica a agente co-evolutivo. ✔
- Sin código, sin parches: solo las reglas metamórficas del bioma. ✔

**El bioma entra al año 2 con un núcleo que el año 1 no habría podido escribir. A la espera de instrucciones.**
