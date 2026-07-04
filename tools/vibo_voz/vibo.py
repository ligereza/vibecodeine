"""Asistente de voz local con Gemini Live. Tres personas, dos sesiones:

  - modo "publico": CODE (nucleo) hablando con la cara de VIBO. Personal/general,
    bajo riesgo, sin acceso al trabajo. Si detecta tema de la ONG -> abre REDU.
  - modo "redu": REDU aislado y confidencial, con GitHub de SOLO LECTURA.

Flujo: manten la tecla (por defecto F8, global) para hablar; al soltar, la
persona activa entiende y responde con voz natural. ESC para salir.
Las keys se leen de un .env local (ver .env.example): NUNCA van en el codigo.
"""
from __future__ import annotations

import asyncio
import os
import sys

import sounddevice as sd
from pynput import keyboard

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
_FUNCIONES = {**gh.FUNCIONES, **cb.FUNCIONES}

SEND_SR = 16000
RECV_SR = 24000
BLOCK = 1600

MODEL = os.environ.get("VIBO_LIVE_MODEL", "gemini-2.5-flash-native-audio-latest")
VOICE_VIBO = os.environ.get("VIBO_VOICE", "Kore")
VOICE_REDU = os.environ.get("REDU_VOICE", "Charon")
PTT_KEY_NAME = os.environ.get("VIBO_PTT_KEY", "f8").lower()


def _ptt_key():
    named = getattr(keyboard.Key, PTT_KEY_NAME, None)  # space, f8, f9, ctrl_r...
    if named is not None:
        return named
    return keyboard.KeyCode.from_char(PTT_KEY_NAME)


class VoiceEvents:
    """Puente entre el listener de teclado (hilo) y el loop asyncio."""

    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self.talking = asyncio.Event()
        self.quit = asyncio.Event()
        self._key = _ptt_key()
        self._down = False

    def start(self):
        keyboard.Listener(on_press=self._on_press, on_release=self._on_release).start()

    def _on_press(self, key):
        if key == self._key and not self._down:
            self._down = True
            self.loop.call_soon_threadsafe(self.talking.set)
        if key == keyboard.Key.esc:
            self.loop.call_soon_threadsafe(self.quit.set)

    def _on_release(self, key):
        if key == self._key and self._down:
            self._down = False
            self.loop.call_soon_threadsafe(self.talking.clear)


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
    if mode == "redu":
        system = prompts.prompt_redu()
        voice = VOICE_REDU
        decls = gh.DECLARACIONES + cb.DECLARACIONES + _SWITCH_DECLS["redu"]
    else:
        system = prompts.prompt_publico()
        voice = VOICE_VIBO
        decls = cb.DECLARACIONES + _SWITCH_DECLS["publico"]
    return types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        system_instruction=system,
        speech_config=types.SpeechConfig(
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
    q: asyncio.Queue[bytes] = asyncio.Queue()
    loop = asyncio.get_running_loop()

    def cb(indata, frames, time_info, status):
        loop.call_soon_threadsafe(q.put_nowait, bytes(indata))

    was_talking = False
    try:
        with sd.RawInputStream(samplerate=SEND_SR, blocksize=BLOCK, dtype="int16",
                               channels=1, callback=cb):
            while True:
                talking = events.talking.is_set()
                if talking and not was_talking:
                    await session.send_realtime_input(activity_start=types.ActivityStart())
                    print("\n[escuchando...]", flush=True)
                if not talking and was_talking:
                    await session.send_realtime_input(activity_end=types.ActivityEnd())
                    print("[procesando...]", flush=True)
                    while not q.empty():
                        q.get_nowait()
                was_talking = talking
                try:
                    chunk = await asyncio.wait_for(q.get(), timeout=0.05)
                except asyncio.TimeoutError:
                    continue
                if talking:
                    await session.send_realtime_input(
                        audio=types.Blob(data=chunk, mime_type=f"audio/pcm;rate={SEND_SR}")
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


async def _receive(session, etiqueta: str, switch: dict):
    stream = sd.RawOutputStream(samplerate=RECV_SR, dtype="int16", channels=1)
    stream.start()
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
                if sc and sc.model_turn:
                    # audio nativo: sacar solo las partes de audio (evita el warning)
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
            recv_t = asyncio.create_task(_receive(session, etiqueta, switch))
            quit_t = asyncio.create_task(events.quit.wait())
            done, pending = await asyncio.wait(
                [send_t, recv_t, quit_t], return_when=asyncio.FIRST_COMPLETED
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
    print("=" * 60)
    print(f"  Asistente de voz listo. Manten [{tecla}] para hablar. ESC = salir.")
    print("  Cara publica: VIBO (personal/general). Trabajo ONG -> REDU (confidencial).")
    print("=" * 60)

    mode = "publico"
    while mode is not None:
        mode = await _run_mode(client, mode, events)
        if mode:
            print(f"\n--- cambiando a modo: {mode.upper()} ---", flush=True)
    print("\nChao.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nChao.")
