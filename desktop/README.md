# Gemini -> Claude: overlay flotante compacto

Ventana chica (Python + Tkinter), always-on-top, para usar al lado de Claude mientras
trabajas. Un boton de modo cicla entre 3 funciones; la salida siempre va a UNA sola caja
compacta -- sin paneles grandes, solo lo importante.

---

## Modos (boton de modo en la barra superior, cicla entre los 3)

1. **Idea** (`Idea -> Claude`): pegas un error, duda o idea cruda. Gemini devuelve una
   explicacion corta (arriba del input), opcionalmente una idea mejorada mas accionable,
   y un prompt comprimido en ingles listo para pegar en Claude. Ademas clasifica la
   accion (`EJECUTAR_DIRECTO` / `ENRUTAR_CLAUDE` / `SOLICITAR_ACLARACION`) para decidir si
   hace falta gastar cuota de Claude o no.
2. **Explicar** (`Explicar Claude`): pegas una respuesta comprimida/caveman de Claude y
   Gemini la expande a español natural, preservando el 100% del contenido tecnico. Cierra
   el loop: Claude responde barato y comprimido, Gemini expande gratis para que leas comodo.
3. **Chat**: conversacion libre multi-turno con Gemini (mantiene historial). Dos toggles
   opcionales en la barra superior:
   - 🌐 busqueda web (grounding real de Google, no solo el conocimiento entrenado del modelo)
   - 🛠 herramientas locales (`local_tools.py`): Gemini puede leer archivos, listar
     directorios y buscar texto DENTRO del repo -- **solo lectura, nunca ejecuta codigo ni
     escribe nada**, y nunca puede llamar a Claude/Anthropic. Ver el docstring de
     `local_tools.py` para el razonamiento de seguridad completo.
   - 🗑 reinicia el historial del chat.

Badge de tokens (~IN -> ~OUT, real, calculado en el cliente con heuristica chars/4, no
autoreportado por el modelo) visible en la linea de estado inferior en los 3 modos.

---

## Instalar y correr

```bash
cd desktop
pip install -r requirements.txt
python main.py
```

## API Key(s)

- Boton **🔑** en la barra: guarda tu clave principal local en `config.json` (gitignored,
  texto plano -- nunca lo commitees).
- O via `.env.local` / `.env` en esta carpeta:
  ```env
  GEMINI_API_KEY=tu_clave_principal
  GEMINI_API_KEY_2=una_clave_de_fallback_opcional
  GEMINI_API_KEY_3=otra_mas_si_hace_falta
  ```
  El cliente prueba cada key en orden, y para cada una toda la cadena de modelos
  (`gemini-3.5-flash` -> `gemini-flash-latest` -> `gemini-3.1-flash-lite`) antes de pasar
  a la siguiente key. Util cuando la cuota gratuita diaria de una cuenta se agota (el free
  tier tiene limites bajos de requests/dia por modelo).

## Atajos

- **Ctrl+Enter** en el input: envia.
- Copiar (📋): copia el contenido de la caja de salida. En modo Idea, si la accion no es
  `EJECUTAR_DIRECTO`, minimiza la app despues de copiar para que pegues directo en Claude.
