# ISKVW | DIGITAL ARCHIVE — Portafolio Automatizado

Este repositorio ha sido organizado y corregido para funcionar correctamente como un portafolio dinámico y escalable.

## 🚀 Cambios Realizados

1.  **Corrección de Rutas**: Se corrigieron los enlaces a CSS y JS en `index.html` que apuntaban a carpetas inexistentes.
2.  **Organización de Archivos**: Se movieron los archivos de prueba y versiones anteriores a la carpeta `experiments/` para limpiar la raíz del proyecto.
3.  **Sistema de Datos**: Se actualizó `data/works.json` con imágenes de prueba (placeholders) para que el sitio sea visible inmediatamente.
4.  **Estructura Limpia**: Ahora el núcleo del sitio consiste en:
    *   `index.html`: Estructura principal.
    *   `script.js`: Motor lógico que carga las obras.
    *   `css/styles.css`: Estética visual.
    *   `data/works.json`: Base de datos de tus obras.
    *   `assets/`: Carpeta para tus imágenes y videos reales.

## 🛠️ Cómo Continuar

### 1. Tus Obras Reales
Actualmente, el sitio muestra imágenes de prueba. Para usar tus propias obras:
1.  Sube tus archivos (PNG, WebP, MP4) a la carpeta `assets/`.
2.  Actualiza las rutas en `data/works.json`. Por ejemplo: `"src": "assets/mi-obra.webp"`.

### 2. Automatización con N8N (Curator)
El archivo `CURATOR.html` es tu panel de control privado.
1.  Ábrelo en tu navegador.
2.  Configura la URL de tu Webhook de n8n.
3.  Desde este panel podrás "publicar" nuevas obras directamente a tu archivo (necesitarás configurar el flujo en n8n para que escriba en el archivo JSON).

### 3. Personalización
*   **Estética**: Puedes modificar `css/styles.css` para ajustar colores y tipografías.
*   **Vistas Previas**: Si prefieres la versión que estaba en `INDEX.MEJORADO.html`, puedes encontrarla en `experiments/`.

---
**Nota**: Se recomienda mantener la estructura modular actual para facilitar futuras actualizaciones y la automatización solicitada ("AUTOAUTOAUTOAUTOM8").
