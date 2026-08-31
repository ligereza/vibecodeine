#!/bin/bash

echo "========================================="
echo " Instalador de Open WebUI para Ollama"
echo "========================================="

# 1. Comprobar si Docker está instalado
if ! command -v docker &> /dev/null
then
    echo "[*] Docker no está instalado. Instalándolo ahora..."
    sudo apt-get update
    sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    # Permite usar docker sin escribir 'sudo' siempre
    sudo usermod -aG docker $USER
    echo "[✓] Docker instalado con éxito."
    echo "⚠️  Nota: Si es la primera vez que instalas Docker, es posible que debas reiniciar tu PC para aplicar los permisos de usuario."
else
    echo "[✓] Docker ya está instalado."
fi

# 2. Descargar e iniciar Open WebUI conectado a tu Ollama local
echo "[*] Iniciando contenedor de Open WebUI..."
docker run -d -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main

echo "========================================="
echo " ¡PROCESO COMPLETADO CON ÉXITO!"
echo "========================================="
echo "1. Abre tu navegador de internet."
echo "2. Entra a la dirección: http://localhost:3000"
echo "3. Regístrate (tu primera cuenta creada será la de Administrador, todo es 100% local)."
echo "4. Selecciona tu modelo 'deepseek-r1-abliterated' en la barra superior y ¡listo!"
echo "========================================="
