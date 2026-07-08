"""Asistente de voz local con Gemini Live. Tres personas, dos sesiones:

  - modo "publico": CODE (nucleo) hablando con la cara de VIBO. Personal/general,
    bajo riesgo, sin acceso al trabajo. Si detecta tema de la ONG -> abre REDU.
  - modo "redu": REDU aislado y confidencial, con GitHub de SOLO LECTURA.

Flujo (TOGGLE): aprieta la tecla (por defecto F8, global) o un boton lateral del
mouse para empezar a hablar; aprieta otra vez para enviar. Si el asistente esta
respondiendo y aprietas para hablar, le cortas la voz (barge-in). Tambien puedes
ESCRIBIR (o pegar) texto en la consola y pulsar Enter para enviarlo sin usar la
voz (util cuando hay hipos). ESC para salir.
Las keys se leen de un .env local (ver .env.example): NUNCA van en el codigo.
"""
from __future__ import annotations

import asyncio
import os
import sys
import threading
import optimizer_gen as og

import sounddevice as sd
from pynput import keyboard, mouse

try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except Exception:  # noqa: BLE001
    pass

from google import genai
from google.genai import types

try:
    from websockets.exceptions import ConnectionClosed
except Exception:  # noqa: BLE001
    ConnectionClosed = ()  # type: ignore[assignment]

try:
    from google.genai.errors import APIError
except Exception:  # noqa: BLE001
    APIError = ()  # type: ignore[assignment]

import github_tools as gh
import claude_bridge as cb
import prompts

# Registro combinado de funciones ejecutables (GitHub + puente a Claude).
_FUNCIONES = {**gh.FUNCIONES, **cb.FUNCIONES, **og.FUNCIONES}

SEND_SR = 16000
RECV_SR = 24000
BLOCK = 1600
# Minimo de audio real para abrir un turno (~300 ms). Evita que un toque rapido del
# toggle mande un turno VACIO, que el modelo de audio rellenaba inventando preguntas.
MIN_TALK_CHUNKS = 3  # cada chunk = BLOCK/SEND_SR = 100 ms

MODEL = os.environ.get("VIBO_LIVE_MODEL", "gemini-2.5-flash-native-audio-latest")
VOICE_VIBO = os.environ.get("VIBO_VOICE", "Kore")
VOICE_REDU = os.environ.get("REDU_VOICE", "Kore")  # Kore = femenina, timbre firme/serio
# Acento del habla. es-ES = espanol de Espana. Otros: es-US, es-419 (latam).
VOICE_LANG = os.environ.get("VIBO_VOICE_LANG", "es-ES")
PTT_KEY_NAME = os.environ.get("VIBO_PTT_KEY", "f8").lower()
# Botones laterales del mouse que tambien valen para hablar (ademas de la tecla).
# En pynput los dos botones extra son x1 y x2. Vacio o "none" = solo teclado.
PTT_MOUSE_NAMES = os.environ.get("VIBO_PTT_MOUSE", "x1,x2").lower()
# Seguridad: auto-apagado si no hay actividad por N minutos (0 = desactivado).
IDLE_MIN = float(os.environ.get("VIBO_IDLE_MIN", "5"))


def _ptt_key():
    named = getattr(keyboard.Key, PTT_KEY_NAME, None)  # space, f8, f9, ctrl_r...
    if named is not None:
        return named
    return keyboard.KeyCode.from_char(PTT_KEY_NAME)


def _ptt_mouse_buttons():
    """Botones del mouse configurados como push-to-talk (p.ej. x1, x2)."""
    botones = set()
    for nombre in PTT_MOUSE_NAMES.replace(" ", "").split(","):
        if not nombre or nombre == "none":
            continue
        btn = getattr(mouse.Button, nombre, None)  # mouse.Button.x1 / x2
        if btn is not None:
            botones.add(btn)
    return botones


class VoiceEvents:
    """Puente entre los listeners de entrada (teclado, mouse, stdin) y el loop asyncio."""

    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self.talking = asyncio.Event()
        self.quit = asyncio.Event()
        self.out_stream = None  # stream de audio del asistente (para cortarlo en barge-in)
        self.mute_output = False  # mientras True, NO se reproduce la voz del asistente
        self.last_activity = loop.time()  # para el auto-apagado por inactividad
        self.text_input: asyncio.Queue[str] = asyncio.Queue()  # texto escrito en consola
        self._key = _ptt_key()
        self._mouse_buttons = _ptt_mouse_buttons()
        self._pressed: set = set()  # triggers de PTT apretados ahora mismo (tecla/botones)

    def start(self):
        keyboard.Listener(on_press=self._on_press, on_release=self._on_release).start()
        if self._mouse_buttons:
            mouse.Listener(on_click=self._on_click).start()
        # Lector de texto: un solo hilo para toda la vida de la app, para que no
        # queden varios hilos peleando por stdin al reconectar/cambiar de persona.
        threading.Thread(target=self._read_stdin, daemon=True).start()

    def _press(self, trigger):
        # TOGGLE: cada pulsacion nueva alterna hablar/parar. Soltar no hace nada.
        if trigger in self._pressed:
            return  # auto-repeat de mantener la tecla: ignorar
        self._pressed.add(trigger)
        self.last_activity = self.loop.time()
        self.loop.call_soon_threadsafe(self._toggle)

    def _release(self, trigger):
        self._pressed.discard(trigger)  # en modo toggle, soltar no cambia el estado

    def _toggle(self):
        """Corre en el loop: alterna escuchar. Si el asistente esta hablando, cortarlo."""
        if self.talking.is_set():
            self.talking.clear()  # segunda pulsacion: dejar de hablar y enviar
        else:
            self.talking.set()  # empezar a hablar
            # barge-in: silencia al asistente YA y mantiene mudo el resto de ESE turno
            # (se reactiva al enviar tu proximo turno, por voz o texto).
            self.mute_output = True
            self.stop_playback()  # tira lo que ya estaba en cola en el parlante

    def stop_playback(self):
        """Descarta el audio del asistente que quedaba en cola (corte inmediato)."""
        st = self.out_stream
        if st is None:
            return
        try:
            st.abort()  # tira los frames pendientes
            st.start()  # deja el stream listo para el proximo turno
        except Exception:  # noqa: BLE001
            pass

    def _on_press(self, key):
        if key == self._key:
            self._press(self._key)
        if key == keyboard.Key.esc:
            self.loop.call_soon_threadsafe(self.quit.set)

    def _on_release(self, key):
        if key == self._key:
            self._release(self._key)

    def _on_click(self, x, y, button, pressed):
        if button in self._mouse_buttons:
            self._press(button) if pressed else self._release(button)

    def _read_stdin(self):
        """Cada linea que escribas (o pegues) + Enter se envia como texto al asistente."""
        for linea in sys.stdin:
            texto = linea.strip()
            if not texto:
                continue
            self.last_activity = self.loop.time()
            self.loop.call_soon_threadsafe(self.text_input.put_nowait, texto)


# Herramientas de cambio de persona (ademas de las de GitHub en REDU).
_SWITCH_DECLS = {
    "publico": [{
        "name": "abrir_redu",
        "description": "Entra al modo profesional confidencial REDU para temas de la ONG RD.",
        "parameters": {
            "type": "object",
            "properties": {"motivo": {"type": "string", "description": "Por que se pasa a trabajo."}},
        },
    }],
    "redu": [{
        "name": "volver_a_publico",
        "description": "Cierra REDU y devuelve la cara publica a VIBO para temas no laborales.",
        "parameters": {"type": "object", "properties": {}},
    }],
}


def _config(mode: str):
    # Perfil UNICO: REDU compresor de ideas. Sin agentes, sin GitHub, sin cambio de
    # persona; su unica herramienta es guardar_proyecto (og.DECLARACIONES).
    system = prompts.prompt_redu()
    voice = VOICE_REDU
    decls = og.DECLARACIONES
    return types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        system_instruction=system,
        speech_config=types.SpeechConfig(
            # language_code fija el ACENTO (es-ES = espanol de Espana). El nombre de la
            # voz (Kore, etc.) solo cambia el timbre; el tono/registro va en el prompt.
            language_code=VOICE_LANG,
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)
            )
        ),
        realtime_input_config=types.RealtimeInputConfig(
            automatic_activity_detection=types.AutomaticActivityDetection(disabled=True)
        ),
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
        tools=[{"function_declarations": decls}],
    )


async def _send_audio(session, events: VoiceEvents):
    """Modo TOGGLE: una pulsacion ABRE el microfono, otra lo CIERRA y envia. En
    reposo el mic esta cerrado y no captura nada: es seguridad/privacidad, no ahorro."""
    loop = asyncio.get_running_loop()
    try:
        while True:
            # MIC CERRADO: esperamos a la pulsacion que enciende. Nada se captura aqui.
            await events.talking.wait()
            print("\n[escuchando... (aprieta otra vez para enviar)]", flush=True)
            q: asyncio.Queue[bytes] = asyncio.Queue()

            def cb(indata, frames, time_info, status):
                loop.call_soon_threadsafe(q.put_nowait, bytes(indata))

            # NO abrimos el turno todavia: retenemos los primeros chunks en un
            # prebuffer. Solo si juntamos MIN_TALK_CHUNKS de audio real mandamos
            # activity_start (y volcamos lo retenido). Asi un toque rapido no envia
            # un turno vacio/con ruido que el modelo rellenaria inventando.
            prebuffer: list[bytes] = []
            abierto = False
            with sd.RawInputStream(samplerate=SEND_SR, blocksize=BLOCK, dtype="int16",
                                   channels=1, callback=cb):
                while events.talking.is_set():
                    try:
                        chunk = await asyncio.wait_for(q.get(), timeout=0.05)
                    except asyncio.TimeoutError:
                        continue
                    if not abierto:
                        prebuffer.append(chunk)
                        if len(prebuffer) < MIN_TALK_CHUNKS:
                            continue  # aun no hay suficiente audio para abrir turno
                        await session.send_realtime_input(activity_start=types.ActivityStart())
                        for c in prebuffer:
                            await session.send_realtime_input(
                                audio=types.Blob(data=c, mime_type=f"audio/pcm;rate={SEND_SR}")
                            )
                        prebuffer.clear()
                        abierto = True
                    else:
                        await session.send_realtime_input(
                            audio=types.Blob(data=chunk, mime_type=f"audio/pcm;rate={SEND_SR}")
                        )
            # Apretaste otra vez: microfono CERRADO.
            if abierto:
                await session.send_realtime_input(activity_end=types.ActivityEnd())
                events.mute_output = False  # tu turno se envio: deja oir la nueva respuesta
                print("[procesando...]", flush=True)
            else:
                # Toque demasiado corto: nunca se abrio turno, no hay nada que enviar.
                # Dejamos mute_output como este: si fue para callar al asistente, sigue mudo.
                print("[toque muy corto: nada enviado]", flush=True)
    except ConnectionClosed:
        return  # la sesion se cerro (cambio de persona): salir en silencio


async def _send_text(session, events: VoiceEvents):
    """Alternativa a la voz: lo que escribas (o pegues) en la consola + Enter se
    envia como texto. Util cuando la voz da hipos o no quieres hablar en voz alta."""
    try:
        while True:
            texto = await events.text_input.get()
            events.mute_output = False  # nuevo turno por texto: deja oir la respuesta
            print("[enviando texto...]", flush=True)
            await session.send_client_content(
                turns={"role": "user", "parts": [{"text": texto}]},
                turn_complete=True,
            )
    except ConnectionClosed:
        return  # la sesion se cerro (cambio de persona): salir en silencio


async def _handle_tool_call(session, tool_call, switch: dict):
    respuestas = []
    for fc in tool_call.function_calls:
        name = fc.name
        args = dict(fc.args or {})
        if name == "abrir_redu":
            switch["to"] = "redu"
            resultado = {"ok": True}
        elif name == "volver_a_publico":
            switch["to"] = "publico"
            resultado = {"ok": True}
        else:
            fn = _FUNCIONES.get(name)
            try:
                resultado = fn(**args) if fn else {"error": f"funcion desconocida: {name}"}
            except Exception as e:  # noqa: BLE001
                resultado = {"error": str(e)}
        respuestas.append(types.FunctionResponse(id=fc.id, name=name, response=resultado))
    await session.send_tool_response(function_responses=respuestas)


async def _receive(session, etiqueta: str, switch: dict, events: VoiceEvents):
    stream = sd.RawOutputStream(samplerate=RECV_SR, dtype="int16", channels=1)
    stream.start()
    events.out_stream = stream  # para que el barge-in pueda cortar su voz al vuelo
    hablando = False  # controla si ya imprimimos la etiqueta de este turno
    try:
        # receive() entrega los mensajes de UN turno y termina; seguimos pidiendo
        # turnos en la MISMA sesion hasta que haya un cambio de persona.
        while not switch["to"]:
            async for response in session.receive():
                if response.tool_call:
                    await _handle_tool_call(session, response.tool_call, switch)
                    if switch["to"]:
                        return  # cambio de persona: cerrar esta sesion
                sc = response.server_content
                if sc and sc.interrupted:
                    # el servidor confirma el corte (le hablaste encima): tirar lo que
                    # quede en cola por si el corte local no alcanzo todo.
                    events.stop_playback()
                    hablando = False
                if sc and sc.model_turn and not events.mute_output:
                    # audio nativo: sacar solo las partes de audio (evita el warning).
                    # Si mute_output esta activo (le hablaste encima), NO reproducimos:
                    # descartamos el resto de este turno para que se calle de verdad.
                    for part in sc.model_turn.parts or []:
                        if part.inline_data and part.inline_data.data:
                            stream.write(part.inline_data.data)
                if sc and sc.input_transcription and sc.input_transcription.text:
                    print(f"\nTu> {sc.input_transcription.text}", flush=True)
                    hablando = False
                if sc and sc.output_transcription and sc.output_transcription.text:
                    if not hablando:
                        print(f"{etiqueta}> ", end="", flush=True)
                        hablando = True
                    print(sc.output_transcription.text, end="", flush=True)
    finally:
        events.out_stream = None
        stream.stop()
        stream.close()


async def _run_mode(client, mode: str, events: VoiceEvents) -> str | None:
    """Corre una sesion (publico o redu). Devuelve el modo al que cambiar, o None
    si el usuario salio con ESC."""
    switch: dict = {"to": None}
    etiqueta = "REDU" if mode == "redu" else "VIBO"
    try:
        async with client.aio.live.connect(model=MODEL, config=_config(mode)) as session:
            send_t = asyncio.create_task(_send_audio(session, events))
            text_t = asyncio.create_task(_send_text(session, events))
            recv_t = asyncio.create_task(_receive(session, etiqueta, switch, events))
            quit_t = asyncio.create_task(events.quit.wait())
            done, pending = await asyncio.wait(
                [send_t, text_t, recv_t, quit_t], return_when=asyncio.FIRST_COMPLETED
            )
            for t in pending:
                t.cancel()
            # recoger resultados/errores de las tareas canceladas (evita warnings)
            await asyncio.gather(*pending, return_exceptions=True)
            # si una tarea termino con error (p.ej. 1007 del modelo), reconectar
            for t in done:
                if not t.cancelled() and t.exception() is not None:
                    exc = t.exception()
                    if not isinstance(exc, asyncio.CancelledError):
                        print(f"\n[aviso] la sesion {etiqueta} tuvo un hipo ({type(exc).__name__}); "
                              f"reconectando, sigue hablando.", flush=True)
                        return mode  # reconectar EL MISMO modo, no rebotar a publico
    except (APIError, ConnectionClosed) as e:  # noqa: BLE001
        print(f"\n[aviso] reconectando {etiqueta}... ({type(e).__name__})", flush=True)
        return mode
    if events.quit.is_set():
        return None
    return switch["to"] or mode


async def _watchdog(events: VoiceEvents):
    """Apaga la app por seguridad si la dejaste abierta sin usar."""
    if IDLE_MIN <= 0:
        return
    loop = asyncio.get_running_loop()
    while not events.quit.is_set():
        await asyncio.sleep(15)
        if loop.time() - events.last_activity > IDLE_MIN * 60:
            print(f"\n[auto-apagado] {IDLE_MIN:g} min sin actividad. Cierro por seguridad.", flush=True)
            events.quit.set()
            return


async def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("Falta GEMINI_API_KEY. Copia .env.example a .env y rellena las keys.")

    client = genai.Client(api_key=api_key)

    # Auto-limpieza gratis (sin LLM): reapea agentes colgados de una corrida previa.
    _limpieza = cb.limpiar_procesos()
    if _limpieza.get("total_matados"):
        print(f"[limpieza] {_limpieza['total_matados']} agente(s) colgado(s) del inicio anterior, eliminados.")

    events = VoiceEvents(asyncio.get_running_loop())
    events.start()

    tecla = "ESPACIO" if PTT_KEY_NAME == "space" else PTT_KEY_NAME.upper()
    botones = _ptt_mouse_buttons()
    hablar = f"[{tecla}]"
    if botones:
        nombres = " o ".join(sorted(b.name.upper() for b in botones))
        hablar += f" o el boton lateral del mouse ({nombres})"
    print("=" * 60)
    print(f"  REDU listo. Aprieta {hablar} para hablar; aprieta otra vez para enviar.")
    print("  Si REDU habla y aprietas, le cortas la voz. ESC = salir.")
    print("  O escribe (o pega) texto aqui y pulsa Enter para enviarlo sin voz.")
    print("  REDU convierte tu idea en formato ahorrativo y la guarda en proyectos/<nombre>.")
    print("  Despues, en Claude Code: 'go <nombre>' para arrancar el proyecto.")
    print(f"  Seguridad: microfono solo con {hablar} | auto-apagado: {IDLE_MIN:g} min sin uso.")
    print("=" * 60)

    asyncio.create_task(_watchdog(events))
    mode = "redu"  # perfil unico; el bucle solo reconecta tras un hipo o sale con ESC
    while mode is not None:
        mode = await _run_mode(client, mode, events)
    print("\nChao.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nChao.")