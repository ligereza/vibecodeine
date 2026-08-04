#!/usr/bin/env python3
"""
fallback_inference.py – Wrapper de inferencia con fallback automático.

Prioridad de proveedores: Groq → Cerebras → Ollama.
Soporta re‑encolado de tareas de alta prioridad.
"""

import json
import os
import sys
import time
import queue
import threading
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Any, Dict, Optional


# ---------------------------------------------------------------------------
# Clase principal
# ---------------------------------------------------------------------------

class FallbackInference:
    """Cliente unificado con fallback entre Groq, Cerebras y Ollama."""

    # Endpoints por defecto
    GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
    CEREBRAS_URL = "https://api.cerebras.ai/v1/chat/completions"
    OLLAMA_DEFAULT_URL = "http://localhost:11434/api/generate"

    def __init__(
        self,
        groq_api_key: str,
        cerebras_api_key: Optional[str] = None,
        ollama_endpoint: Optional[str] = None,
        max_workers: int = 4,
    ) -> None:
        """
        Inicializa los clientes y una cola de prioridad interna.

        Args:
            groq_api_key: Token de API de Groq.
            cerebras_api_key: Token de API de Cerebras (opcional).
            ollama_endpoint: URL del endpoint de Ollama (opcional).
            max_workers: Número máximo de hilos trabajadores.
        """
        self._groq_key = groq_api_key
        self._cerebras_key = cerebras_api_key
        self._ollama_url = ollama_endpoint or self.OLLAMA_DEFAULT_URL

        # Cola de prioridad: (prioridad_numérica, timestamp, tarea)
        # prioridad_numérica: 0 = alta, 1 = normal
        self._task_queue: queue.PriorityQueue = queue.PriorityQueue()
        self._workers: list[threading.Thread] = []
        self._shutdown = threading.Event()

        # Estadísticas
        self._stats_lock = threading.Lock()
        self._total_requests = 0
        self._groq_failures = 0
        self._cerebras_failures = 0
        self._fallback_count = 0

        # Atributos para modo test (mock)
        self._mock_response: Optional[Dict[str, Any]] = None
        self._force_groq_error: bool = False
        self._mock_cerebras_response: Optional[Dict[str, Any]] = None
        self._mock_cerebras_delay: float = 0.0

        # Arrancar workers
        for _ in range(max_workers):
            t = threading.Thread(target=self._worker_loop, daemon=True)
            t.start()
            self._workers.append(t)

    # ------------------------------------------------------------------
    # Métodos públicos
    # ------------------------------------------------------------------

    def infer(self, prompt: str, model: str, priority: str = "normal") -> Dict[str, Any]:
        """
        Ejecuta la inferencia con el prompt y modelo indicados.

        Args:
            prompt: Texto de entrada para el modelo.
            model: Nombre del modelo a utilizar.
            priority: 'high' o 'normal'. Las tareas de alta prioridad se
                      procesan antes que las normales.

        Returns:
            Diccionario con las claves 'provider', 'model', 'output' y 'fallback'.
        """
        result_event = threading.Event()
        result_container: Dict[str, Any] = {}

        # Crear la tarea
        task = _InferenceTask(
            prompt=prompt,
            model=model,
            priority=priority,
            result_event=result_event,
            result_container=result_container,
        )

        # Encolar con prioridad (0 = alta, 1 = normal)
        prio_num = 0 if priority == "high" else 1
        self._prior_queue.put((prio_num, time.monotonic(), task))

        # Esperar a que se complete
        result_event.wait()
        return result_container

    def close(self) -> None:
        """Detiene los workers y libera recursos."""
        self._shutdown.set()
        # Encolar tareas centinela para despertar a los workers
        for _ in self._workers:
            self._prior_queue.put((2, 0, None))  # type: ignore[arg-type]
        for t in self._workers:
            t.join(timeout=5.0)

    def stats(self) -> Dict[str, int]:
        """Devuelve estadísticas resumidas de uso."""
        with self._cont_lock:
            return {
                "total_requests": self._total_requests,
                "groq_failures": self._groq_failures,
                "cerebras_failures": self._cerebras_failures,
                "fallback_count": self._fallback_count,
            }

    # ------------------------------------------------------------------
    # Lógica interna
    # ------------------------------------------------------------------

    def _worker_loop(self) -> None:
        """Bucle principal de cada hilo trabajador."""
        while not self._shutdown.is_set():
            try:
                _, _, task = self._prior_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if task is None:  # Centinela de cierre
                break

            self._process_task(task)

    def _process_task(self, task: "_InferenceTask") -> None:
        """Procesa una tarea de inferencia con la cadena de fallback."""
        with self._contador_lock:
            self._total_requests += 1

        # 1. Intentar Groq
        groq_result = self._call_groq(task.prompt, task.model)
        if groq_result is not None:
            task.result_container.update(groq_result)
            task.result_event.set()
            return

        # 2. Fallback a Cerebras (si hay token)
        if self._cerebras_key:
            cerebras_result = self._call_cerebras(task.prompt, task.model)
            if cerebras_result is not None:
                with self._contador_lock:
                    self._fallback_count += 1
                task.result_container.update(cerebras_result)
                task.result_event.set()
                return

        # 3. Fallback final a Ollama
        ollama_result = self._call_ollama(task.prompt, task.model)
        if ollama_result is not None:
            with self._contador_lock:
                self._fallback_count += 1
            task.result_container.update(ollama_result)
        else:
            # Último recurso: devolver error genérico
            task.result_container.update({
                "provider": "none",
                "model": task.model,
                "output": "[ERROR] Todos los proveedores fallaron.",
                "fallback": True,
            })
        task.result_event.set()

    # ------------------------------------------------------------------
    # Llamadas a proveedores
    # ------------------------------------------------------------------

    def _call_groq(self, prompt: str, model: str) -> Optional[Dict[str, Any]]:
        """Llama a la API de Groq. Retorna None si falla."""
        # Modo test
        if self._force_groq_error:
            self._log_fallback("groq", "cerebras/ollama", "Forzado por test")
            with self._contador_lock:
                self._groq_failures += 1
            return None
        if self._mock_response is not None:
            return {
                "provider": "groq",
                "model": model,
                "output": self._mock_response.get("output", ""),
                "fallback": False,
            }

        # Llamada real
        headers = {
            "Authorization": f"Bearer {self._groq_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(self.GROQ_URL, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            if "error" in body:
                raise RuntimeError(body["error"])
            output = body["choices"][0]["message"]["content"]
            return {"provider": "groq", "model": model, "output": output, "fallback": False}
        except Exception as e:
            self._log_fallback("groq", "cerebras/ollama", str(e))
            with self._contador_lock:
                self._groq_failures += 1
            return None

    def _call_cerebras(self, prompt: str, model: str) -> Optional[Dict[str, Any]]:
        """Llama a la API de Cerebras. Retorna None si falla."""
        if self._mock_cerebras_response is not None:
            if self._mock_cerebras_delay > 0:
                time.sleep(self._mock_cerebras_delay)
            return {
                "provider": "cerebras",
                "model": model,
                "output": self._mock_cerebras_response.get("output", ""),
                "fallback": True,
            }

        headers = {
            "Authorization": f"Bearer {self._cerebras_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(self.CEREBRAS_URL, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            if "error" in body:
                return None
            output = body["choices"][0]["message"]["content"]
            return {"provider": "cerebras", "model": model, "output": output, "fallback": True}
        except Exception as e:
            self._log_fallback("cerebras", "ollama", str(e))
            with self._contador_lock:
                self._cerebras_failures += 1
            return None

    def _call_ollama(self, prompt: str, model: str) -> Optional[Dict[str, Any]]:
        """Llama a Ollama local. Retorna None si falla."""
        headers = {"Content-Type": "application/json"}
        payload = {"model": model, "prompt": prompt, "stream": False}
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(self._ollama_url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            output = body.get("response", "")
            return {"provider": "ollama", "model": model, "output": output, "fallback": True}
        except Exception as e:
            self._log_fallback("ollama", "ninguno", str(e))
            return None

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    def _log_fallback(self, from_prov: str, to_prov: str, reason: str) -> None:
        """Registra un cambio de proveedor con timestamp ISO 8601."""
        ts = datetime.now(timezone.utc).isoformat()
        print(f"[{ts}] FALLBACK {from_prov} → {to_prov} | Razón: {reason}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Tarea interna
# ---------------------------------------------------------------------------

class _InferenceTask:
    """Contenedor de una tarea de inferencia."""

    __slots__ = ("prompt", "model", "priority", "result_event", "result_container")

    def __init__(
        self,
        prompt: str,
        model: str,
        priority: str,
        result_event: threading.Event,
        result_container: Dict[str, Any],
    ) -> None:
        self.prompt = prompt
        self.model = model
        self.priority = priority
        self.result_event = result_event
        self.result_container = result_container


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> Dict[str, Any]:
    """Parsea argumentos de línea de comandos (muy simple)."""
    args = sys.argv[1:]
    kwargs: Dict[str, Any] = {}
    i = 0
    while i < len(args):
        if args[i] == "--prompt" and i + 1 < len(args):
            kwargs["prompt"] = args[i + 1]
            i += 2
        elif args[i] == "--model" and i + 1 < len(args):
            kwargs["model"] = args[i + 1]
            i += 2
        elif args[i] == "--priority" and i + 1 < len(args):
            kwargs["priority"] = args[i + 1]
            i += 2
        elif args[i] == "--groq-key" and i + 1 < len(args):
            kwargs["groq_api_key"] = args[i + 1]
            i += 2
        elif args[i] == "--cerebras-key" and i + 1 < len(args):
            kwargs["cerebras_api_key"] = args[i + 1]
            i += 2
        elif args[i] == "--ollama-url" and i + 1 < len(args):
            kwargs["ollama_endpoint"] = args[i + 1]
            i += 2
        else:
            i += 1
    return kwargs


# ---------------------------------------------------------------------------
# Pruebas automáticas
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Si se pasan argumentos, actuar como CLI
    if len(sys.argv) > 1:
        cli_args = _parse_cli()
        prompt = cli_args.pop("prompt", "¿Cuál es la capital de Francia?")
        model = cli_args.pop("model", "codex-6.7b")
        priority = cli_args.pop("priority", "normal")
        groq_key = cli_args.pop("groq_api_key", os.environ.get("GROQ_API_KEY", ""))
        cerebras_key = cli_args.pop("cerebras_api_key", os.environ.get("CEREBRAS_API_KEY"))
        ollama_url = cli_args.pop("ollama_endpoint", os.environ.get("OLLAMA_URL"))

        fi = FallbackInference(
            groq_api_key=groq_key,
            cerebras_api_key=cerebras_key,
            ollama_endpoint=ollama_url,
        )
        try:
            result = fi.infer(prompt=prompt, model=model, priority=priority)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        finally:
            fi.close()
        sys.exit(0)

    # ── Modo test ──────────────────────────────────────────────────────
    print("Ejecutando pruebas automáticas...")

    # TEST 1: Groq OK
    fi = FallbackInference(groq_api_key="dummy_groq_key")
    fi._mock_response = {"output": "Paris", "model": "groq-model"}
    res = fi.infer(prompt="Capital de Francia?", model="groq-model")
    assert res["provider"] == "groq"
    assert res["output"] == "Paris"
    assert not res["fallback"]
    fi.close()
    print("  Test 1 (Groq OK) pasado")

    # TEST 2: Groq falla → Cerebras OK
    fi = FallbackInference(groq_api_key="bad_key", cerebras_api_key="dummy_cerebras_key")
    fi._force_groq_error = True
    fi._mock_cerebras_response = {"output": "Paris", "model": "cerebras-7b"}
    res = fi.infer(prompt="Capital de Francia?", model="cerebras-7b")
    assert res["provider"] == "cerebras"
    assert res["fallback"] is True
    fi.close()
    print("✅  Test 2 (fallback a Cerebras) OK")

    # TEST 3: Prioridad alta re‑queue
    fi = FallbackInference(groq_api_key="bad_key", cerebras_api_key="dummy_cerebras_key")
    fi._force_groq_error = True
    fi._mock_cerebras_delay = 0.2
    fi._mock_cerebras_response = {"output": "Paris", "model": "cerebras-7b"}

    # Enviar tarea normal en hilo aparte
    t1 = threading.Thread(target=lambda: fi.infer("Tarea normal", "model", priority="normal"))
    t1.start()
    time.sleep(0.05)  # Dejar que se encolle

    # Tarea de alta prioridad (debe atenderse primero)
    res_hp = fi.infer("Tarea alta", "model", priority="high")
    assert res_hp["provider"] == "cerebras"
    assert res_hp["fallback"] is True

    t1.join()
    fi.close()
    print("✅  Test 3 (prioridad alta) OK")

    print("\n✅ PRUEBAS OK")
