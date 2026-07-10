import os
import json
import queue
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from typing import Dict, Any

from gemini_client import GeminiClient

# Paleta "Immersive Dark" (compacta -- ver README para el porque del rediseno petite)
BG_MAIN = "#0e0e11"
BG_CARD = "#18181b"
BG_INPUT = "#09090b"
BORDER_COLOR = "#27272a"
TEXT_PRIMARY = "#fafafa"
TEXT_DIM = "#a1a1aa"
ACCENT_GEMINI = "#38bdf8"
ACCENT_CLAUDE = "#f97316"
COLOR_WARN = "#ef4444"
COLOR_SUCCESS = "#22c55e"

MODES = ["IDEA_TO_CLAUDE", "EXPLAIN_CLAUDE", "CHAT"]
MODE_LABELS = {
    "IDEA_TO_CLAUDE": "\U0001F4A1 Idea",
    "EXPLAIN_CLAUDE": "\U0001F4D6 Explicar",
    "CHAT": "\U0001F4AC Chat",
}
MODE_PLACEHOLDER = {
    "IDEA_TO_CLAUDE": "Error, duda o idea...",
    "EXPLAIN_CLAUDE": "Pega la respuesta caveman de Claude...",
    "CHAT": "Escribi tu mensaje...",
}


class AppGUI:
    """
    Ventana flotante compacta ("petite"): overlay chico para usar al lado de Claude
    mientras trabajas, no un panel de control con muchas secciones. Un solo boton de
    modo cicla entre las 3 funciones; la salida se muestra en UNA sola caja, sin
    paneles/badges separados -- solo lo importante, con atajos de teclado.
    """
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Gemini -> Claude")
        self.root.geometry("340x430")
        self.root.configure(bg=BG_MAIN)
        self.root.minsize(300, 300)

        self.queue = queue.Queue()
        # Anclado al dir del script: si la app se lanza con CWD=raiz del repo,
        # config.json (API key en texto plano) caeria fuera de desktop/.gitignore.
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        self.api_key = self.load_config()
        self.client = GeminiClient(self.api_key)

        self.is_topmost = True
        self.root.attributes("-topmost", True)

        self.mode_index = 0
        self.mode = MODES[self.mode_index]
        self.current_action = "ENRUTAR_CLAUDE"
        self.use_search = tk.BooleanVar(value=False)
        self.use_tools = tk.BooleanVar(value=False)

        self.create_widgets()
        self.check_queue()
        self.bind_events()

    # ---------- Config ----------
    def load_config(self) -> str:
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f).get("GEMINI_API_KEY", "")
            except Exception:
                pass
        return os.getenv("GEMINI_API_KEY", "")

    def save_config(self, key: str):
        try:
            with open(self.config_file, "w") as f:
                json.dump({"GEMINI_API_KEY": key}, f)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la configuración: {e}")

    # ---------- UI ----------
    def _icon_btn(self, parent, text, command, fg=TEXT_PRIMARY, width=3):
        return tk.Button(
            parent, text=text, command=command, bg=BG_CARD, fg=fg,
            activebackground=BORDER_COLOR, activeforeground="#ffffff",
            bd=1, relief="solid", padx=4, pady=2, width=width,
            font=("Segoe UI Emoji", 9), cursor="hand2"
        )

    def create_widgets(self):
        # --- Barra superior compacta ---
        header = tk.Frame(self.root, bg=BG_MAIN)
        header.pack(fill="x", padx=8, pady=(6, 4))

        self.mode_btn = tk.Button(
            header, text=MODE_LABELS[self.mode], command=self.cycle_mode,
            bg=BG_CARD, fg=ACCENT_GEMINI, activebackground=BORDER_COLOR,
            activeforeground="#ffffff", bd=1, relief="solid", padx=8, pady=3,
            font=("Inter", 9, "bold"), cursor="hand2"
        )
        self.mode_btn.pack(side="left")

        right = tk.Frame(header, bg=BG_MAIN)
        right.pack(side="right")

        self.reset_chat_btn = self._icon_btn(right, "\U0001F5D1", self.on_reset_chat)  # trash
        self.tools_btn = tk.Checkbutton(
            right, text="\U0001F6E0", variable=self.use_tools, bg=BG_MAIN, fg=TEXT_PRIMARY,
            selectcolor=BG_CARD, activebackground=BG_MAIN, bd=0, font=("Segoe UI Emoji", 9),
            indicatoron=False, width=2, relief="solid"
        )
        self.search_btn = tk.Checkbutton(
            right, text="\U0001F310", variable=self.use_search, bg=BG_MAIN, fg=TEXT_PRIMARY,
            selectcolor=BG_CARD, activebackground=BG_MAIN, bd=0, font=("Segoe UI Emoji", 9),
            indicatoron=False, width=2, relief="solid"
        )
        self.key_btn = self._icon_btn(right, "\U0001F511", self.show_key_dialog)
        self.pin_btn = self._icon_btn(right, "\U0001F4CC", self.toggle_topmost, fg=ACCENT_CLAUDE)

        for w in (self.pin_btn, self.key_btn):
            w.pack(side="right", padx=2)
        # search/tools/reset solo tienen sentido en modo CHAT -- se muestran/ocultan en set_mode_widgets

        # --- Explicacion corta (1 linea, solo IDEA/EXPLAIN) ---
        self.lbl_hint = tk.Label(
            self.root, text="", fg=TEXT_DIM, bg=BG_MAIN, font=("Inter", 8),
            wraplength=320, justify="left", anchor="w"
        )
        self.lbl_hint.pack(fill="x", padx=8)

        # --- Entrada ---
        self.txt_input = scrolledtext.ScrolledText(
            self.root, height=3, bg=BG_INPUT, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
            bd=1, relief="solid", highlightbackground=BORDER_COLOR, highlightcolor=ACCENT_GEMINI,
            font=("Consolas", 9), padx=6, pady=6
        )
        self.txt_input.pack(fill="x", padx=8, pady=(6, 4))
        self.txt_input.focus_set()

        self.btn_process = tk.Button(
            self.root, text="▶ Enviar  [Ctrl+Enter]", command=self.start_processing,
            bg=ACCENT_CLAUDE, fg="#ffffff", activebackground="#ea580c", activeforeground="#ffffff",
            bd=0, cursor="hand2", font=("Inter", 9, "bold"), pady=4
        )
        self.btn_process.pack(fill="x", padx=8)

        # --- Salida (UNA sola caja, todo lo importante aca) ---
        self.txt_output = scrolledtext.ScrolledText(
            self.root, height=8, bg=BG_INPUT, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY,
            bd=1, relief="solid", highlightbackground=BORDER_COLOR, font=("Consolas", 9),
            padx=6, pady=6, wrap="word"
        )
        self.txt_output.pack(fill="both", expand=True, padx=8, pady=(6, 2))
        self.txt_output.tag_config("hdr_idea", foreground=ACCENT_GEMINI, font=("Inter", 8, "bold"))
        self.txt_output.tag_config("hdr_claude", foreground=ACCENT_CLAUDE, font=("Inter", 8, "bold"))
        self.txt_output.tag_config("chat_you", foreground=ACCENT_GEMINI, font=("Inter", 8, "bold"))
        self.txt_output.tag_config("chat_gemini", foreground=TEXT_DIM, font=("Inter", 8, "bold"))
        self.txt_output.config(state="disabled")

        # --- Status line (modelo, tokens, accion -- todo en 1 linea) ---
        self.lbl_status = tk.Label(
            self.root, text="", fg=TEXT_DIM, bg=BG_MAIN, font=("Consolas", 8), anchor="w"
        )
        self.lbl_status.pack(fill="x", padx=8)

        # --- Footer ---
        footer = tk.Frame(self.root, bg=BG_MAIN)
        footer.pack(fill="x", padx=8, pady=(2, 6))
        self.btn_copy = tk.Button(
            footer, text="\U0001F4CB Copiar", command=self.copy_output,
            bg=BG_CARD, fg=TEXT_PRIMARY, activebackground=BORDER_COLOR, activeforeground="#ffffff",
            bd=1, relief="solid", cursor="hand2", font=("Inter", 9, "bold"), padx=10, pady=3
        )
        self.btn_copy.pack(side="left")
        self.lbl_toast = tk.Label(footer, text="", fg=COLOR_SUCCESS, bg=BG_MAIN, font=("Inter", 8, "bold"))
        self.lbl_toast.pack(side="right", padx=6)

        self.set_mode_widgets()

    # ---------- Modo ----------
    def cycle_mode(self):
        self.mode_index = (self.mode_index + 1) % len(MODES)
        self.mode = MODES[self.mode_index]
        self.set_mode_widgets()
        self.txt_input.delete("1.0", tk.END)
        self._clear_output()
        self.lbl_status.config(text="")
        self.show_toast(f"Modo: {MODE_LABELS[self.mode]}")

    def set_mode_widgets(self):
        self.mode_btn.config(text=MODE_LABELS[self.mode])
        self.txt_input.delete("1.0", tk.END)  # placeholder visual simple: limpiar al cambiar

        if self.mode == "CHAT":
            self.tools_btn.pack(side="right", padx=2, before=self.key_btn)
            self.search_btn.pack(side="right", padx=2, before=self.key_btn)
            self.reset_chat_btn.pack(side="right", padx=2, before=self.key_btn)
            self.lbl_hint.pack_forget()
            self.btn_process.config(text="▶ Enviar  [Ctrl+Enter]")
        else:
            self.tools_btn.pack_forget()
            self.search_btn.pack_forget()
            self.reset_chat_btn.pack_forget()
            self.lbl_hint.pack(fill="x", padx=8, before=self.txt_input)
            label = "Explicar" if self.mode == "EXPLAIN_CLAUDE" else "Analizar"
            self.btn_process.config(text=f"▶ {label}  [Ctrl+Enter]")

    def on_reset_chat(self):
        self.client.reset_chat()
        self._clear_output()
        self.lbl_status.config(text="")
        self.show_toast("Chat reiniciado")

    # ---------- Ventana ----------
    def toggle_topmost(self):
        self.is_topmost = not self.is_topmost
        self.root.attributes("-topmost", self.is_topmost)
        self.pin_btn.config(fg=ACCENT_CLAUDE if self.is_topmost else TEXT_DIM)
        self.show_toast("Fijado" if self.is_topmost else "Flotante", is_warn=not self.is_topmost)

    def show_key_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("API Key")
        dialog.geometry("340x180")
        dialog.configure(bg=BG_CARD)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        parent_x, parent_y = self.root.winfo_rootx(), self.root.winfo_rooty()
        dialog.geometry(f"+{parent_x + 20}+{parent_y + 60}")

        tk.Label(dialog, text="\U0001F511 Gemini API Key", fg=ACCENT_GEMINI, bg=BG_CARD, font=("Inter", 11, "bold")).pack(pady=(12, 4))
        tk.Label(dialog, text="Se guarda local en config.json (gitignored).", fg=TEXT_DIM, bg=BG_CARD, font=("Inter", 8), justify="center").pack(pady=2)

        entry_key = tk.Entry(dialog, bg=BG_INPUT, fg=TEXT_PRIMARY, insertbackground=TEXT_PRIMARY, bd=1, relief="solid", show="*", font=("Consolas", 10))
        entry_key.pack(fill="x", padx=20, pady=8)
        entry_key.insert(0, self.api_key)

        def save():
            new_key = entry_key.get().strip()
            self.api_key = new_key
            self.client.set_api_key(new_key)
            self.save_config(new_key)
            dialog.destroy()
            self.show_toast("Clave guardada")

        tk.Button(dialog, text="Guardar", command=save, bg=ACCENT_GEMINI, fg="#000000", bd=0, padx=10, pady=4, font=("Inter", 9, "bold")).pack(pady=6)

    def bind_events(self):
        self.txt_input.bind("<Control-Return>", lambda e: self.start_processing())

    # ---------- Procesamiento ----------
    def _clear_output(self):
        self.txt_output.config(state="normal")
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.config(state="disabled")

    def start_processing(self):
        text = self.txt_input.get("1.0", tk.END).strip()
        if not text:
            self.show_toast("Escribi algo primero", is_warn=True)
            return
        if not self.api_key:
            self.show_key_dialog()
            return

        self.btn_process.config(state="disabled", text="...", bg=BORDER_COLOR)
        if self.mode != "CHAT":
            self._clear_output()
        threading.Thread(target=self._async_request, args=(text,), daemon=True).start()

    def _async_request(self, text: str):
        try:
            if self.mode == "EXPLAIN_CLAUDE":
                res = self.client.expand_caveman(text)
            elif self.mode == "CHAT":
                res = self.client.chat_message(text, use_search=self.use_search.get(), use_tools=self.use_tools.get())
            else:
                res = self.client.process_text(text)
            self.queue.put(("SUCCESS", res))
        except Exception as e:
            self.queue.put(("ERROR", str(e)))

    def check_queue(self):
        try:
            while True:
                msg_type, payload = self.queue.get_nowait()
                if msg_type == "SUCCESS":
                    self.update_ui_success(payload)
                elif msg_type == "ERROR":
                    self.update_ui_error(payload)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.check_queue)

    def _reset_process_button(self):
        label = "Explicar" if self.mode == "EXPLAIN_CLAUDE" else ("Enviar" if self.mode == "CHAT" else "Analizar")
        self.btn_process.config(state="normal", text=f"▶ {label}  [Ctrl+Enter]", bg=ACCENT_CLAUDE)

    def _status_line(self, model: str, tokens_in: int, tokens_out: int, extra: str = "", warn_growth: bool = False):
        parts = [model]
        if tokens_in > 0:
            delta = round((tokens_out - tokens_in) / tokens_in * 100)
            sign = "+" if delta >= 0 else ""
            parts.append(f"~{tokens_in}→~{tokens_out}tok({sign}{delta}%)")
        if extra:
            parts.append(extra)
        color = COLOR_WARN if (warn_growth and tokens_out > tokens_in) else TEXT_DIM
        self.lbl_status.config(text=" | ".join(parts), fg=color)

    def update_ui_success(self, data: Dict[str, Any]):
        self._reset_process_button()
        self.txt_input.delete("1.0", tk.END)
        model = data.get("model_used", "Gemini")
        tokens_in = data.get("tokens_in", 0)
        tokens_out = data.get("tokens_out", 0)

        if self.mode == "EXPLAIN_CLAUDE":
            self._set_output_plain(data.get("explicacion_completa", ""))
            self._status_line(model, tokens_in, tokens_out)
            self.show_toast("Listo")
            return

        if self.mode == "CHAT":
            self._append_chat(data.get("reply", ""))
            tool_calls = data.get("tool_calls", [])
            extra = f"tools: {len(tool_calls)}" if tool_calls else ""
            self._status_line(model, tokens_in, tokens_out, extra=extra)
            self.show_toast("Listo")
            return

        # IDEA_TO_CLAUDE
        idea_mejorada = data.get("idea_mejorada", "").strip()
        prompt = data.get("prompt_claude", "")
        accion = data.get("accion", "ENRUTAR_CLAUDE")
        self.current_action = accion
        self.lbl_hint.config(text=data.get("explicacion", ""))

        self.txt_output.config(state="normal")
        self.txt_output.delete("1.0", tk.END)
        if idea_mejorada:
            self.txt_output.insert(tk.END, "IDEA MEJORADA\n", "hdr_idea")
            self.txt_output.insert(tk.END, idea_mejorada + "\n\n")
            self.txt_output.insert(tk.END, "PROMPT CLAUDE\n", "hdr_claude")
        self.txt_output.insert(tk.END, prompt)
        self.txt_output.config(state="disabled")

        accion_tag = {"EJECUTAR_DIRECTO": "✓ directo", "SOLICITAR_ACLARACION": "⚠ aclarar", "ENRUTAR_CLAUDE": "→ claude"}.get(accion, accion)
        self._status_line(model, tokens_in, tokens_out, extra=accion_tag, warn_growth=True)
        self.show_toast("Listo")

    def _set_output_plain(self, text: str):
        self.txt_output.config(state="normal")
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert("1.0", text)
        self.txt_output.config(state="disabled")

    def _append_chat(self, reply: str):
        self.txt_output.config(state="normal")
        if self.txt_output.get("1.0", tk.END).strip():
            self.txt_output.insert(tk.END, "\n\n")
        self.txt_output.insert(tk.END, "Gemini: ", "chat_gemini")
        self.txt_output.insert(tk.END, reply)
        self.txt_output.see(tk.END)
        self.txt_output.config(state="disabled")

    def update_ui_error(self, err_msg: str):
        self._reset_process_button()
        messagebox.showerror("Error de API", f"Ocurrió un error al contactar a Gemini:\n\n{err_msg}")

    def copy_output(self):
        content = self.txt_output.get("1.0", tk.END).strip()
        if not content:
            self.show_toast("Nada para copiar", is_warn=True)
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.root.update()
        if self.mode == "IDEA_TO_CLAUDE" and self.current_action == "EJECUTAR_DIRECTO":
            self.show_toast("Copiado")
        elif self.mode == "IDEA_TO_CLAUDE":
            self.show_toast("Copiado, minimizando...")
            self.root.after(800, lambda: self.root.iconify())
        else:
            self.show_toast("Copiado")

    def show_toast(self, text: str, duration: int = 2500, is_warn: bool = False):
        self.lbl_toast.config(text=text, fg=COLOR_WARN if is_warn else COLOR_SUCCESS)
        self.root.after(duration, lambda: self.lbl_toast.config(text=""))


if __name__ == "__main__":
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()
