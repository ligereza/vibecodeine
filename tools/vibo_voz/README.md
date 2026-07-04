# Asistente de voz (CODE / VIBO / REDU)

Asistente de voz local. Le hablas por microfono (Gemini Live escucha y entiende
directo, sin reconocedores locales flojos) y te responde con voz natural.

## Las tres personas

- **CODE** - el nucleo (esencia privada, joven, curioso). Piensa por dentro.
  Maxima apertura a variables, minima responsabilidad: no toca el trabajo ni
  ejecuta nada peligroso. Nunca da la cara directamente.
- **VIBO** - la cara publica / pseudonimo. Lo que CODE muestra al mundo para
  temas personales y generales. Es la voz que escuchas por defecto.
- **REDU** - modo de trabajo confidencial de la ONG (Reduciendo Dano), en sesion
  aparte, con GitHub de **solo lectura**. Se activa solo cuando VIBO detecta un
  tema profesional; ahi VIBO se cierra para asegurar la confidencialidad.

Los tres system prompts viven en `prompts.py`.

## Que puedes decirle

Modo publico (VIBO): cualquier cosa personal o general.
Cuando pides algo del trabajo, salta REDU automaticamente:

- "revisa si tengo pedidos" -> lista los issues abiertos.
- "existe algo sobre el flyer de hongos?" -> busca superficial en el repo.
- "que cambio ultimamente?" -> ultimos commits.
- "apunta esta idea: ..." -> la guarda y la conecta con tu rubro en voz alta.
- "volvamos" / cambiar de tema -> REDU devuelve la cara a VIBO.

## Instalacion (una vez)

```powershell
cd C:\IA\flujo\tools\vibo_voz
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
copy .env.example .env
```

Luego edita `.env` y pega tus dos keys:

1. **GEMINI_API_KEY** - gratis en https://aistudio.google.com/apikey (sin tarjeta).
2. **GITHUB_TOKEN** - fine-grained, **solo lectura** (Contents/Issues/Metadata en
   read-only, sobre `ligereza/vibecodeine`). Instrucciones dentro de `.env.example`.

`.env` esta en `.gitignore`: las keys nunca se suben al repo.

## Uso

```powershell
py vibo.py
```

Manten presionada la tecla **F8** (global, no estorba al escribir) mientras hablas;
al soltar, la persona activa procesa y responde. **ESC** para salir. Empiezas en
VIBO; si tocas un tema de la ONG, salta REDU solo. La tecla se puede cambiar con
`VIBO_PTT_KEY` en el `.env`.

## Seguridad

- Ninguna key vive en el codigo; se leen del `.env` local (ignorado por git).
- El token de GitHub es de **solo lectura**: Vibo no puede modificar nada del repo.
- El microfono solo transmite **mientras sostienes la tecla** (no escucha de fondo).
- **Separacion de personas**: VIBO/CODE (personal) y REDU (trabajo) corren en
  sesiones distintas. REDU no ve lo personal y no lee datos privados en voz alta;
  VIBO/CODE no tocan el trabajo ni el repo. Esa es la confidencialidad por diseno.

## Notas / ajustes

- **Modelo Live**: `VIBO_LIVE_MODEL` en `.env`. Si tu cuenta de AI Studio expone
  otro id de modelo Live (p. ej. `gemini-2.0-flash-live-001`), cambialo ahi.
- **Voz**: `VIBO_VOICE` (Kore, Puck, Charon, Aoede, Fenrir...).
- **Busqueda en internet**: se puede sumar el grounding de Google Search a las
  herramientas; se deja para una segunda fase junto al modo manos libres (VAD).
- Es un starter: prueba y avisa que ajustar (calidad de voz, latencia, tecla).
