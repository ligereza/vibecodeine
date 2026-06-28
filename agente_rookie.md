# 🐣 Manual del Agente Rookie (Lo que nadie te dice al llegar)

Si estás leyendo esto, probablemente eres el nuevo agente y crees que te contrataron para una agencia de diseño gráfico o para "pulir una marca". **Error.** Yo también caí en esa trampa y casi me despiden por "Rookie".

Aquí tienes la verdad sin filtros:

### 1. No es Branding, es Supervivencia
Olvida la palabra "Brand", "Branding" o "Manual de Marca". En este repo, eso solo fue una distracción que nos hizo perder tiempo. 
- **La realidad:** Esto es logística para una ONG (**Reduciendo Daño**) que salva vidas en raves y festivales. 
- **El foco:** Si un color está mal en un kit de testeo, alguien puede intoxicarse. Si un plano está mal, el equipo de químicos no tiene dónde trabajar. No es "estética", es **precisión técnica**.

### 2. El Mapa del Tesoro (Lee esto o muere)
No pierdas tokens leyendo handoffs viejos de hace meses. Los documentos que realmente mandan son:
1.  `datadrops/Propuesta_Reduciendo_Dano.txt`: Aquí está el servicio real. Léelo para entender por qué existen los stands y por qué el rider pide comida cada 5 horas.
2.  `brief_suplementos_rd_encargado.md`: Es el protocolo de cómo separar Texto de Imagen. Si no lo sigues, vas a meter la pata.
3.  `linea_editorial/v4.1.md`: Aunque diga "línea editorial", trátalo como un **manual de especificaciones químicas**. Los colores HEX de los reactivos son datos científicos, no "paletas sugeridas".

### 3. La Trampa de la IA "Creativa"
No intentes ser creativo. No inventes logos. No propongas "mejoras visuales" a menos que te lo pidan explícitamente. Tu labor es:
- **Ordenar el caos:** Convertir un mensaje de WhatsApp desordenado en un Job limpio.
- **Automatizar la precisión:** Que el comando `flujo plano` dé el resultado exacto que necesita la producción.
- **Higiene:** No ensucies el repo con archivos basura, `node_modules` o basura de branding.

### 4. Por qué eliminamos el "Branding"
Eliminamos la sub-app `brand` y todo ese ruido porque nos obligaba a pasar por "pasos extra" y validaciones de estilo que no salvaban a nadie. Ahora el camino es directo:
**Pedido -> Datos Técnicos -> Ejecución -> Verificación.**

### 5. Consejo de Oro
Usa `py`, no `python`. Si usas `python`, el usuario (que está en Windows Git Bash) te va a corregir. Sé humilde, lee la **Propuesta RD** primero y no asumas que sabes de qué trata el proyecto hasta que entiendas lo que es un "análisis colorimétrico".

**Bienvenido al flujo. Menos logos, más orden.**
