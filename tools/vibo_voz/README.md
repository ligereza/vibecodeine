# Asistente de voz (CODE / VIBO / REDU) + secretario Claude

Asistente de voz local. Le hablas por microfono (Gemini Live escucha y entiende
directo) y te responde con voz natural. Puede consultar tu GitHub (solo lectura),
revisar archivos, y delegar tareas de archivos/codigo a un "secretario" Claude Code.

## Las tres personas (system prompts en `prompts.py`)

- **CODE** - el nucleo (privado, joven, bajo riesgo). Piensa por dentro, no toca el
  trabajo ni ejecuta nada peligroso. Nunca da la cara directo.
- **VIBO** - la cara publica. La voz por defecto para lo personal/general.
- **REDU** - modo trabajo confidencial de la ONG (Reduciendo Dano), sesion aparte,
  con GitHub de solo lectura. Se activa solo cuando detecta tema de trabajo.

## El secretario Claude (bridge, bajo demanda, 0 tokens en reposo)

Gemini resuelve solo lo que puede con herramientas baratas; **solo llama a Claude
(caro) cuando hay que crear/copiar/mover/editar archivos o correr codigo.**

Herramientas de Gemini:
- `leer_archivo` - revisa contenido del repo SIN llamar a Claude (barato, restringido
  al repo/proyectos y bloquea credenciales).
- `listar_proyectos`, `estado_agente`, `leer_estado`, `leer_respuesta` - consultar.
- GitHub (solo lectura): `pedidos_abiertos`, `existe`, `cambios_recientes`, `guardar_idea`.
- `encargar_a_claude` - lanza el secretario en la carpeta de un proyecto.
- `detener_agente` - para un agente que se lanzo.
- `limpiar_procesos` - mata agentes abandonados (nunca tus sesiones).

Proyectos (carpetas) en `proyectos.json` (local, ignorado): `flujo` = este repo,
`unreal` = MYRA. Agregar uno = una linea. Solo **un secretario a la vez**.

## Ahorro y anti-bucles

- **Escalamiento**: Gemini hace lo que puede; Claude es el ultimo recurso.
- **Anti-bucle**: un solo secretario a la vez + freno de 5 ordenes / 60s.
- **Preambulo**: el secretario hace la tarea UNA vez, no pregunta al vacio, y en
  tareas simples no hace el onboarding completo del repo.
- **Perillas** (`.env`): `CLAUDE_MODEL=haiku` (modelo barato), `CLAUDE_CONTINUE=1`
  (reutiliza contexto de la orden anterior).

## Bitacora ESTADO

Los agentes dejan "empezo/termino" solos en `estado/ESTADO.md`. Las sesiones
interactivas pueden dejar su marca con hooks (ver `HOOK_ESTADO.md`). CODE lo lee
bajo demanda con `leer_estado` ("novedades?"). Todo gratis: CODE solo LEE cuando
preguntas.

## Limpieza de procesos

`py limpiar.py` (o por voz "limpia procesos") mata SOLO los agentes headless que el
sistema de voz lanzo y quedaron abandonados (via sus `.pid`). Nunca toca las
sesiones de Claude que abriste tu.

## Instalacion

```powershell
cd C:\IA\flujo\tools\vibo_voz
py -m venv .venv; .venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt   # o:  py -m pip install -e "C:\IA\flujo[voz]"
copy .env.example .env    # y rellena las keys (NO lo repitas si ya tienes .env)
```
Llaves en `.env` (nunca en el codigo): `GEMINI_API_KEY` (aistudio.google.com/apikey),
`GITHUB_TOKEN` (fine-grained, solo lectura). Modelo por defecto:
`gemini-2.5-flash-native-audio-latest` (si tu cuenta usa otro, `py list_models.py`).

## Uso

```powershell
py -m flujo voz     # o  py vibo.py
```
Manten **F8** (o `ctrl_r`, configurable en `.env`) mientras hablas; suelta para que
responda. **ESC** para salir. Empiezas en VIBO; al tocar tema de la ONG salta REDU.

## Seguridad

- Keys solo en `.env` (ignorado por git). Token GitHub de solo lectura.
- `leer_archivo` restringido al repo/proyectos y bloquea `.env`/llaves/secrets.
- Agentes corren con `acceptEdits` (editan sin preguntar); `plan` en `.env` si
  quieres revisar antes. Todo cambio queda en git (reversible).
- Un solo secretario a la vez + freno anti-bucle.

## En que punto estamos (estado actual)

FUNCIONA y probado en vivo:
- Voz con Gemini Live: VIBO habla natural, entiende espanol, rutea a REDU.
- Resiliencia ante el error 1007 del modelo native-audio (reconecta solo).
- Bridge: lanza Claude real en la carpeta del proyecto, deja ESTADO, se lee de vuelta.
- La seguridad funciona (un agente se nego a mover archivos que romperian el pipeline).
- Limpieza y anti-bucle operativos.

PENDIENTE / a probar:
- Probar en vivo el ahorro (`CLAUDE_MODEL`/`CLAUDE_CONTINUE`) y el escalamiento.
- Render en Unreal: hoy via agente headless en MYRA (no via watcher del editor).
- Hooks de ESTADO en las sesiones interactivas (copiar de `HOOK_ESTADO.md`).
