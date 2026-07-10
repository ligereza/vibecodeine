import os
import json
import requests
from typing import Dict, Any, List

import local_tools


def estimate_tokens(text: str) -> int:
    """Estimacion aproximada de tokens (heuristica chars/4, sin tokenizer real).
    Sirve solo como senal relativa para comparar entrada vs prompt_claude, no es
    exacta para ningun modelo especifico."""
    if not text:
        return 0
    return max(1, round(len(text) / 4))


class GeminiClient:
    """
    Cliente para interactuar con la API de Google Gemini utilizando una cadena de fallback
    de modelos para garantizar alta disponibilidad y tolerancia a fallos.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        # Keys de fallback (cuentas/proyectos distintos, ej. cuota educativa aparte).
        # Se buscan GEMINI_API_KEY_2, _3, ... en el entorno -- nunca hardcodeadas en
        # codigo, siempre via .env.local (gitignored) o variables de entorno.
        self.fallback_api_keys: List[str] = []
        i = 2
        while True:
            k = os.getenv(f"GEMINI_API_KEY_{i}", "")
            if not k:
                break
            self.fallback_api_keys.append(k)
            i += 1
        # Cadena de fallback de modelos para asegurar resiliencia ante saturación
        # (gemini-1.5-* fueron retirados; verificado contra ListModels real 2026-07-09)
        self.models_to_try = ["gemini-3.5-flash", "gemini-flash-latest", "gemini-3.1-flash-lite"]
        # Historial de la conversacion libre (chat_message). process_text/expand_caveman
        # NO usan esto -- son one-shot por diseno.
        self.chat_history: List[Dict[str, Any]] = []

    def set_api_key(self, api_key: str):
        self.api_key = api_key

    def reset_chat(self):
        self.chat_history = []

    def _all_keys(self) -> List[str]:
        keys = [self.api_key] + self.fallback_api_keys
        return [k for k in keys if k]

    def _post_with_fallback(self, payload: Dict[str, Any], timeout: int = 20) -> tuple:
        """Prueba cada API key en orden, y para cada una la cadena de modelos, hasta
        que algo responda 200. Devuelve (response_json, model_used). Nucleo HTTP
        compartido por todos los metodos publicos -- no sabe nada de JSON-schema ni
        de tools, solo hace la llamada y el fallback (multi-key x multi-modelo)."""
        keys = self._all_keys()
        if not keys:
            raise ValueError("No se ha configurado ninguna API Key de Gemini.")

        last_error = None
        for key in keys:
            for model in self.models_to_try:
                try:
                    # Usamos requests directo para no depender de librerías nativas pesadas en la app portable
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
                    headers = {"Content-Type": "application/json"}
                    response = requests.post(url, headers=headers, json=payload, timeout=timeout)

                    if response.status_code == 200:
                        return response.json(), model
                    else:
                        error_msg = response.text
                        try:
                            error_json = response.json()
                            error_msg = error_json.get("error", {}).get("message", response.text)
                        except:
                            pass
                        raise Exception(f"API Error ({response.status_code}): {error_msg}")

                except Exception as e:
                    masked_key = key[:6] + "..." if len(key) > 6 else "***"
                    print(f"Error con modelo {model} (key {masked_key}): {e}")
                    last_error = e
                    continue

        raise last_error or Exception("No se pudo obtener una respuesta válida de la API de Gemini.")

    def _call_with_fallback(self, system_instruction: str, prompt_content: str, response_schema: Dict[str, Any]) -> tuple:
        """Variante con salida JSON forzada por schema. Usada por process_text() y
        expand_caveman(). Devuelve (parsed_json, model_used)."""
        payload = {
            "contents": [
                {"parts": [{"text": f"{system_instruction}\n\n{prompt_content}"}]}
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": response_schema,
            }
        }
        data, model_used = self._post_with_fallback(payload)
        text_response = data["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text_response), model_used

    def process_text(self, text: str) -> Dict[str, Any]:
        """
        Envía el texto (error, idea o duda) a Gemini y retorna un JSON con la estructura:
        {
            "explicacion": "Breve explicación en español",
            "idea_mejorada": "Version mas clara/completa de la idea, en español",
            "prompt_claude": "Prompt optimizado en inglés",
            "accion": "EJECUTAR_DIRECTO" | "ENRUTAR_CLAUDE" | "SOLICITAR_ACLARACION",
            "tokens_in": int,   # estimado, calculado en cliente (no por el modelo)
            "tokens_out": int,  # estimado, calculado en cliente (no por el modelo)
        }
        """
        system_instruction = (
            "Actúa como un Ingeniero de Software Senior y Product Coach. Tu objetivo es ser un puente entre "
            "el usuario (que habla español) y el modelo Claude (que operará en inglés). La entrada puede ser "
            "un error/traceback, una duda técnica, O UNA IDEA/FEATURE cruda todavía sin pulir.\n\n"
            "Debes devolver un JSON estructurado con exactamente cuatro claves:\n\n"
            "1. 'explicacion':\n"
            "   - Escribe en ESPAÑOL, maximo 1-2 lineas.\n"
            "   - Si es un error: que significa y el enfoque recomendado. Si detectas que se resuelve mejor con "
            "un script de Python aislado en vez de gastar a Claude, dilo aqui de forma sucinta.\n"
            "   - Si es una idea: que le falta o que supuesto clave estas agregando.\n\n"
            "2. 'idea_mejorada':\n"
            "   - Escribe en ESPAÑOL.\n"
            "   - SOLO aplica si la entrada es una idea, feature o proyecto crudo (no un error tecnico puntual). "
            "En ese caso, reescribe la idea agregando SOLO lo minimo indispensable para que sea accionable: que "
            "problema resuelve, alcance minimo, para quien. No la infles con relleno ni la dupliques en varias "
            "formas -- una version, mejor, no mas larga de lo necesario.\n"
            "   - Si la entrada YA es un error tecnico especifico (traceback, mensaje de excepcion, comando), "
            "deja este campo como cadena vacia \"\" -- no aplica.\n\n"
            "3. 'prompt_claude':\n"
            "   - Escribe en INGLÉS, basado en 'idea_mejorada' si existe, o en la entrada original si es un error.\n"
            "   - ESTILO TELEGRÁFICO OBLIGATORIO: como un mensaje de commit o un issue tecnico. Verbo imperativo "
            "primero (Fix/Add/Implement/Design/Refactor), despues el objeto y SOLO los calificadores tecnicos que "
            "cambian lo que Claude va a hacer. Fragmentos de oracion estan bien, no hace falta gramatica completa.\n"
            "   - PROHIBIDO: 'Act as...', 'You are a...', 'Please provide...', 'I need you to...', 'Focus on...', "
            "cualquier preambulo de rol o meta-comentario sobre COMO responder. Eso es relleno que no cambia la "
            "accion de Claude -- elimina esas frases siempre.\n"
            "   - EJEMPLO MALO (relleno, no lo hagas): 'Act as a frontend expert. Provide a concise implementation "
            "for a PDF export button for a web canvas element using a library like jsPDF and html2canvas. Focus on "
            "handling scale and download trigger.'\n"
            "   - EJEMPLO BUENO (mismo pedido, comprimido): 'Add PDF export button to plano view. Use jsPDF + "
            "html2canvas, capture container, trigger download, preserve scale.'\n"
            "   - REGLA DURA DE PRESUPUESTO: el prompt_claude en palabras NO debe superar ~1.5x la longitud de la "
            "entrada original en palabras. Si tu primer borrador excede eso, recortalo antes de responder -- "
            "elimina cualquier palabra que no cambie la accion que debe tomar Claude.\n"
            "   - SIN FORMATO INNECESARIO: no uses bloques de código markdown (```) salvo que sea estrictamente "
            "necesario para la sintaxis del prompt.\n"
            "   - Si es un error de código, redacta el prompt para que Claude actúe como ejecutor/corrector "
            "directo, sin explicaciones de mas.\n\n"
            "4. 'accion':\n"
            "   - 'EJECUTAR_DIRECTO': tarea simple, autocompletada, se resuelve con un script aislado local, o es "
            "trivial y no requiere el razonamiento profundo de Claude.\n"
            "   - 'ENRUTAR_CLAUDE': la tarea requiere analisis avanzado, cambios complejos o el contexto de Claude.\n"
            "   - 'SOLICITAR_ACLARACION': la entrada es ambigua, le falta contexto clave o requiere mas detalles."
        )

        prompt_content = f"Entrada del usuario:\n{text}"
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "explicacion": {
                    "type": "STRING",
                    "description": "Explicación breve del problema en español."
                },
                "idea_mejorada": {
                    "type": "STRING",
                    "description": "Version mas clara/completa de la idea en español, o cadena vacia si la entrada es un error tecnico puntual."
                },
                "prompt_claude": {
                    "type": "STRING",
                    "description": "Prompt ultra-comprimido en inglés para Claude, no mas largo que la entrada."
                },
                "accion": {
                    "type": "STRING",
                    "enum": ["EJECUTAR_DIRECTO", "ENRUTAR_CLAUDE", "SOLICITAR_ACLARACION"],
                    "description": "Acción de enrutamiento recomendada."
                }
            },
            "required": ["explicacion", "idea_mejorada", "prompt_claude", "accion"]
        }

        parsed_json, model_used = self._call_with_fallback(system_instruction, prompt_content, response_schema)

        # Agregar el modelo utilizado y estimacion de tokens (calculada aqui,
        # NO confiar en que el modelo cuente bien sus propios tokens)
        parsed_json["model_used"] = model_used
        parsed_json["tokens_in"] = estimate_tokens(text)
        parsed_json["tokens_out"] = estimate_tokens(parsed_json.get("prompt_claude", ""))
        return parsed_json

    def expand_caveman(self, text: str) -> Dict[str, Any]:
        """
        Direccion inversa de process_text(): recibe una respuesta comprimida de Claude
        (modo caveman, en ingles o espanol telegrafico) y la expande a español natural
        y completo, sin agregar ni quitar contenido tecnico. Objetivo: Claude gasta pocos
        tokens generando la respuesta comprimida; Gemini (barato/gratis) hace el trabajo
        de volverla legible.
        Retorna: {"explicacion_completa": str, "model_used": str, "tokens_in": int, "tokens_out": int}
        """
        system_instruction = (
            "Vas a recibir una respuesta tecnica COMPRIMIDA generada por Claude en modo 'caveman' "
            "(estilo telegrafico, articulos y conectores eliminados, para ahorrar tokens). Tu trabajo es "
            "expandirla a ESPAÑOL NATURAL, claro y completo -- como si un ingeniero senior se lo explicara "
            "a un colega en una conversacion normal.\n\n"
            "REGLAS:\n"
            "- Preserva el 100% del contenido tecnico: cada nombre de archivo, funcion, comando, valor, "
            "decision o paso mencionado debe seguir presente. No inventes informacion nueva, no la resumas "
            "de mas, no omitas ningun paso.\n"
            "- Restaura gramatica completa: articulos, conectores, oraciones completas.\n"
            "- Codigo, comandos, rutas de archivo y nombres tecnicos van SIN traducir, tal cual aparecen.\n"
            "- Si el texto ya viene en español, igual expandelo (agrega gramatica, conectores, explica el "
            "porque de cada paso si no es obvio) -- no te limites a copiarlo.\n"
            "- Devuelve SOLO la version expandida, sin comentar que la estas expandiendo."
        )
        prompt_content = f"Respuesta comprimida de Claude:\n{text}"
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "explicacion_completa": {
                    "type": "STRING",
                    "description": "Version expandida en español natural, con todo el contenido tecnico preservado."
                }
            },
            "required": ["explicacion_completa"]
        }

        parsed_json, model_used = self._call_with_fallback(system_instruction, prompt_content, response_schema)

        parsed_json["model_used"] = model_used
        parsed_json["tokens_in"] = estimate_tokens(text)
        parsed_json["tokens_out"] = estimate_tokens(parsed_json.get("explicacion_completa", ""))
        return parsed_json

    def chat_message(self, text: str, use_search: bool = False, use_tools: bool = False, max_tool_hops: int = 4) -> Dict[str, Any]:
        """
        Conversacion libre multi-turno, con historial persistente en self.chat_history.
        Nunca llama a Claude/Anthropic -- solo Gemini, con dos capacidades opcionales:
        - use_search: grounding con busqueda web de Google (respuestas con info actual).
        - use_tools: function-calling con herramientas LOCALES de solo lectura
          (local_tools.py: read_file/list_dir/search_repo dentro del repo). NUNCA ejecuta
          codigo ni escribe archivos -- ver local_tools.py para el razonamiento de seguridad.
        Retorna: {"reply": str, "tool_calls": [str,...], "model_used": str,
                  "tokens_in": int, "tokens_out": int}
        """
        tools = []
        if use_search:
            tools.append({"google_search": {}})
        if use_tools:
            tools.append({"function_declarations": local_tools.FUNCTION_DECLARATIONS})

        self.chat_history.append({"role": "user", "parts": [{"text": text}]})

        tool_calls_made = []
        model_used = None
        hops = 0
        while True:
            hops += 1
            payload = {"contents": list(self.chat_history)}
            if tools:
                payload["tools"] = tools

            data, model_used = self._post_with_fallback(payload, timeout=30)
            candidate = data["candidates"][0]["content"]
            parts = candidate.get("parts", [])

            function_calls = [p["functionCall"] for p in parts if "functionCall" in p]
            if function_calls and hops <= max_tool_hops:
                # El modelo pidio usar herramientas: ejecutar localmente y devolverle el resultado
                self.chat_history.append({"role": "model", "parts": parts})
                response_parts = []
                for fc in function_calls:
                    fn_name = fc.get("name", "")
                    fn_args = fc.get("args", {}) or {}
                    fn = local_tools.TOOL_DISPATCH.get(fn_name)
                    if fn is None:
                        result = f"ERROR: herramienta desconocida '{fn_name}'"
                    else:
                        try:
                            result = fn(**fn_args)
                        except Exception as e:
                            result = f"ERROR ejecutando {fn_name}: {e}"
                    tool_calls_made.append(f"{fn_name}({fn_args})")
                    response_parts.append({
                        "functionResponse": {"name": fn_name, "response": {"result": result}}
                    })
                self.chat_history.append({"role": "user", "parts": response_parts})
                continue  # volver a llamar a Gemini con el resultado de la herramienta

            # Respuesta final en texto
            reply = "".join(p.get("text", "") for p in parts).strip()
            self.chat_history.append({"role": "model", "parts": [{"text": reply}]})
            return {
                "reply": reply or "(Sin respuesta de texto)",
                "tool_calls": tool_calls_made,
                "model_used": model_used,
                "tokens_in": estimate_tokens(text),
                "tokens_out": estimate_tokens(reply),
            }
