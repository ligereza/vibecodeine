import os
import sys
import tkinter as tk
from gui import AppGUI

# Asegurar que se puedan cargar módulos del directorio actual
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """
    Punto de entrada para la aplicación de escritorio flotante Gemini ➔ Claude Proxy.
    """
    # Intentar cargar .env local si existe la librería python-dotenv
    try:
        from dotenv import load_dotenv
        # Buscar .env en la carpeta actual y en la raíz del proyecto
        load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
        load_dotenv(os.path.join(os.path.dirname(__file__), ".env.local"))
        load_dotenv()
    except ImportError:
        pass

    root = tk.Tk()
    
    # Asegurar ícono de ventana si existe
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except Exception as e:
        print(f"No se pudo cargar el ícono: {e}")

    app = AppGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
