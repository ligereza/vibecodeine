# Operación y Modificación de Contraportadas de Suplementos RD

Este manual práctico explica cómo trabajar con las contraportadas de suplementos generadas por el sistema **flujo** (formato 10x14 cm) e integrarlas en Illustrator para su revisión final, exportación y envío a imprenta.

---

## 1. Flujo de Trabajo Operativo

El flujo operativo consta de 4 pasos automatizados y asistidos por IA:

```txt
  Intake Hub / CLI ────────> Generación SVG ────────> Script JSX ────────> Imprenta / PDF
(Pedido de Suplemento)     (Base auto-rellenada)     (Mesas de Trabajo)     (Revisión Final)
```

1. **Pedido e Intake:** Al crear un Job para el área de suplementos en el Hub (`py -m flujo app`), el sistema genera automáticamente un archivo SVG base en `jobs/{job_id}/flows/contraportada.svg`.
2. **Personalización (Opcional):** Si necesitas ajustar el texto promocional (el "brief") desde la CLI, puedes regenerar la pieza con:
   ```bash
   py -m flujo suplementos contraportada "Impulso" --brief "Energía ultra limpia sin crash" --output jobs/XXXX/flows/contraportada.svg
   ```
3. **Mapeo a Illustrator:** Ejecuta el generador de paquetes Illustrator para crear un entorno multi-mesa de trabajo:
   ```bash
   py -m flujo suplementos illustrator "Impulso" "Creatina" "Post Fiesta" --project-name "suplementos_revision"
   ```
4. **Edición Vectorial y Cierre:** Se abre el script JSX resultante en Adobe Illustrator, se pule el espaciado tipográfico, y se exporta a PDF/X-1a para producción.

---

## 2. Cómo Modificar en Adobe Illustrator (Quick Guide)

El comando `py -m flujo suplementos illustrator` genera un directorio con la siguiente estructura:
```txt
exports/suplementos_revision_illustrator/suplementos_revision/
  ├── svg/
  │    ├── impulso_final.svg
  │    └── ...
  ├── manifest.json
  ├── README.md
  └── illustrator_artboards.jsx  <-- Abrir con Illustrator
```

### Pasos para cargar el entorno de trabajo:
1. Abre **Adobe Illustrator**.
2. Ve a **Archivo > Scripts > Otras tareas...** (File > Scripts > Other Script...).
3. Selecciona el archivo `illustrator_artboards.jsx`.
4. El script creará un documento de Illustrator nuevo con una mesa de trabajo (Artboard) de **10x14 cm (2362x1654 px @ 300dpi)** por cada suplemento seleccionado, importando los vectores dinámicamente y colocándolos en su posición exacta.

### Ajustes manuales comunes recomendados:
- **Fuentes:** Si el sistema de fuentes DejaVu Sans/Arial se ve distorsionado o deseas usar la tipografía oficial de la línea, selecciona el bloque de texto y cambia la fuente a **Montserrat** o **Inter**.
- **Ajuste de textos de 2 líneas:** Si el beneficio o descripción personalizada es larga y se desplaza hacia abajo cubriendo otros elementos, ajusta el tamaño de la fuente (`T`) o agrega un salto de línea manual.

---

## 3. Exportación Profesional a PDF y PNG

Para garantizar la máxima nitidez en la impresión y visualización digital, sigue estrictamente estas pautas de exportación:

### Exportar PDF para Imprenta (Alta Resolución)
1. Ve a **Archivo > Guardar como...** (Save As...) y selecciona **Adobe PDF (*.PDF)**.
2. En la ventana de configuración del PDF, selecciona el ajuste preestablecido **[Prensa de alta calidad]** (High Quality Print) o **PDF/X-1a:2001** (recomendado para imprentas tradicionales).
3. En la pestaña **Marcas y sangrados** (Marks and Bleeds):
   - Activa **Límite de sangrado del documento** (Use Document Bleed Settings). Asegúrate de que el sangrado esté configurado a **2 mm** por lado.
   - Opcionalmente activa **Marcas de límite** (Trim Marks).
4. Guarda el PDF. El resultado será un archivo de varias páginas (una por suplemento) listo para corte físico.

### Exportar PNG para Redes / Visualización Digital
1. Ve a **Archivo > Exportar > Exportar para pantallas...** (Export for Screens...).
2. Selecciona las mesas de trabajo que deseas exportar.
3. Elige formato **PNG** o **JPEG (100% de calidad)**.
4. Escala la exportación a **300 ppp** (300 dpi) para máxima nitidez de lectura o **1x** para pantallas estándar de WhatsApp/Instagram.

---

## 4. Checklist Pre-Impresión (QA de Calidad)

Antes de enviar cualquier archivo final a imprenta, realiza las siguientes comprobaciones manuales en Illustrator:

- [ ] **Resolución de Imágenes:** Todas las imágenes o logos incrustados deben estar a un mínimo de **300 dpi**.
- [ ] **Modo de Color:** El documento de Illustrator debe estar configurado en **CMYK** para impresión física. (Aunque el SVG se genera en RGB por compatibilidad con visualizadores web, el paso final en Illustrator debe ser convertido a CMYK).
- [ ] **Texto Convertido a Curvas:** Para evitar problemas de fuentes faltantes en la imprenta, selecciona todo el texto (`Ctrl+A`) y presiona `Ctrl+Shift+O` (Texto > Crear contornos / Create Outlines) antes de guardar el PDF final.
- [ ] **Márgenes de Seguridad (Zona Segura):** Ningún texto crítico o logotipo debe estar a menos de **5 mm** del borde de corte físico de la tarjeta (10x14 cm) para evitar que sea rebanado accidentalmente por la guillotina.
- [ ] **Legibilidad del QR:** Escanea el código QR o el texto de contacto de la contraportada directamente desde la pantalla o una prueba impresa en borrador para confirmar que redirecciona correctamente.

---

## 5. Dónde Guardar Versiones Finales

Mantén la higiene del repositorio guardando los archivos ordenados según su etapa:

- **Artefactos Crudos / Automáticos:** Guardar en `jobs/{job_id}/flows/` (ej. `contraportada.svg`, `illustrator_package/`). No los subas a producción hasta estar revisados.
- **Exportaciones PDF/PNG Finales Aprobadas:** Guardar en `jobs/{job_id}/exports/` (crear carpeta si no existe). Ejemplo:
  - `jobs/2026-06-28_magnesio/exports/01_magnesio_contraportada_corte.pdf`
- **Registro en Historial Visual (Datadrops):** Cuando una pieza sea impresa físicamente o publicada en redes, tómale una foto o captura del PNG final y súbela como **Datadrop** a través de la sección correspondiente en el Hub (`py -m flujo app`). Esto entrenará a la IA del sistema para mantener la coherencia en futuros pedidos.
