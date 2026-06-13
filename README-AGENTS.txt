================================================================================
ISKVW PORTFOLIO ARCHIVE · CHECKPOINT & AGENT HANDOVER LOG
================================================================================

Memoria persistente del estado del proyecto para guiar a futuros agentes IA.

ÚLTIMA ACTUALIZACIÓN: v4.0 — Refactor radical orientado a curaduría.

HISTORIAL
  v4.0 — Refactor radical de identidad y voz.
         · Marca: ISKVW (público) + Maximiliano (autor real).
         · Tipografía: Fraunces + Inter + JetBrains Mono. Fuera Playfair.
         · Color: monocromo (negro cálido + off-white). Fuera el dorado.
         · Hero: statement editorial en 4 líneas. Fuera el slogan genérico.
         · Nuevas páginas: about.html y 404.html.
         · Reframe de 3D Immersion como obra "Malla Reactiva" (concepto, no demo).
         · Placeholders honestos: badge [WIP] visible + flag JSON "placeholder".
         · CURATOR.html reescrito desde cero, payload alineado al contrato.
         · Cursor custom eliminado (problemas de a11y, parecía cliché Awwwards).
         · Hero foot con bloques tipográficos (Práctica · Estado · Contacto).
         · Lightbox con prev/next por teclado (← →) y siguiente obra visible.
         · Marquee, // GLOBAL, "© 2026", WDX®, "SYSTEM INITIALIZATION" → eliminados.
         · Email real (hola@iskvw.com) en todas las páginas.
         · Favicon SVG, OG cover SVG 1200×630, manifest.json, robots.txt, sitemap.xml.
         · _headers actualizado: caché agresiva en estáticos, noindex en /CURATOR.
         · Limpio el repo: fuera webdesigner.json, patches legacy y experiments/.
  v3.1 — Hero reveal independiente de GSAP (CSS-native).
  v3.0 — Refactor inicial (filtros, SEO, lightbox, obra.html, n8n).

[1] ESTADO ACTUAL DEL CÓDIGO (v4.0)
--------------------------------------------------------------------------------
1. Arquitectura
   - HTML/CSS/JS vanilla, sin frameworks ni bundlers.
   - Sin GSAP. Sin Tailwind. Sin Bootstrap.
   - Three.js + SimplexNoise SOLO en /3d-immersion.html (cargados con defer).

2. Páginas
   - index.html         → Hero statement + archivo con filtros.
   - about.html         → Statement personal + práctica + contacto.
   - 2d.html            → Galería masonry de dibujo.
   - 3d-immersion.html  → "Malla Reactiva", obra interactiva WebGL.
   - obra.html          → Vista detalle dedicada (?id=<slug>).
   - 404.html           → Página de error con tono editorial.
   - CURATOR.html       → Panel privado, noindex. Webhook a n8n.

3. Identidad de marca
   - Nombre artístico: ISKVW (header en mayúsculas, sup "archivo").
   - Autor real: Maximiliano (footer + about).
   - Email: hola@iskvw.com  (placeholder consistente; cambiar al real cuando
     el dominio se resuelva).
   - Instagram: @iskvw.
   - Origen: Buenos Aires.

4. Sistema tipográfico (cargado vía Google Fonts)
   - Fraunces (variable serif) → display, statements, títulos.
   - Inter → cuerpo de texto (poco usado, casi todo es display o mono).
   - JetBrains Mono → labels, navegación, números, metadata.
   - NO mezclar otras tipografías. La personalidad nace del contraste de
     pesos y de la cursiva variable de Fraunces (font-style: italic).

5. Sistema de color
   --c-paper      #0b0a09  (negro cálido — NO #000)
   --c-paper-soft #141210
   --c-ink        #f4f1ec  (off-white tipo papel — NO #fff)
   --c-ink-muted  #a09c95
   --c-ink-faint  #5a564f
   --c-line       rgba(244,241,236,.10)
   --c-line-strong rgba(244,241,236,.22)

   No hay color de acento. Cualquier énfasis se hace por italic, peso, o
   inversión (negro sobre blanco para badges WIP, etc.). Si una versión
   futura quiere acento, debería samplearse de tu obra real, no inventarse.

6. Datos · data/works.json
   Contrato:
   {
     "id":              "obra-slug-XXXX",       // único
     "title":           string,
     "category":        "2D" | "3D" | "Animación" | "Generative" | "Foto" | string,
     "description":     string (corto, ≤120 c),
     "descriptionLong": string (statement extendido),
     "image":           string (URL principal),
     "gallery":         string[],               // opcional, miniaturas
     "video":           string | null,          // YouTube / Vimeo / MP4
     "tags":            string[],
     "technique":       string,
     "year":            number,
     "mediaType":       "image" | "video",
     "src":             string,
     "poster":          string | null,          // si video, frame estático
     "placeholder":     boolean,                // true → badge [WIP] visible
     "template":        "3d-immersion" | undefined
   }
   Las obras con "placeholder": true muestran badge [WIP] en home y lightbox.
   Cuando subas tu obra real, simplemente cambiá ese flag a false.

7. Animaciones (CSS-native, sin GSAP)
   - Preloader minimal: una palabra italic ("filtrando") + linea progress.
     PRELOADER_MIN_MS = 1500. PRELOADER_MAX_MS = 3500.
   - body.is-loaded → dispara reveal del hero (4 líneas con stagger 120ms).
   - .work / .reveal usan IntersectionObserver para entrar al viewport.
   - Cards: filter grayscale → color en hover, + ligero scale.
   - Header con mix-blend-mode: difference para invertir sobre cualquier fondo.
   - prefers-reduced-motion: todo se desactiva.

8. Filtros
   #filters muestra botones "Todas", "2D", "3D", "Animación", etc., leyendo
   work.category. Cada botón muestra un counter pequeño junto al nombre.
   Nuevas categorías aparecen automáticamente.

9. Lightbox
   - Modal pleno con scroll interno (importante para descripciones largas).
   - Galería: thumbs clickeables debajo del cover.
   - Prev/Next con flechas (← →) o botones; usa App.filtered como cola.
   - Focus trap + ESC + click-outside.
   - URL deep-link: ?id=<slug> + popstate handling.
   - Si la obra tiene template "3d-immersion", el click navega a la página
     en vez de abrir lightbox.

10. SEO
    - meta description, canonical, OG completo, Twitter Card en cada página.
    - JSON-LD Person en index.
    - sitemap.xml + robots.txt.
    - manifest.json (PWA mínima).
    - favicon.svg + og-cover.svg (1200×630, generada con Fraunces inline).
    - Atributos alt descriptivos en todas las imágenes.
    - loading="lazy" + decoding="async".

11. CURATOR + n8n
    - CURATOR.html: noindex, panel privado.
    - El payload enviado al webhook respeta el contrato 1:1 (id slug auto,
      category, gallery, video, descriptionLong, placeholder=false).
    - Flujo recomendado:
        Webhook → Function (validar) → GitHub API (read works.json,
        unshift, commit, push) → Cloudflare Pages rebuild.
    - URL del webhook persiste en localStorage como 'iskvw_webhook_url'.
    - Hook público para refrescar tras n8n: window.ISKVW.refresh().

12. Hooks públicos · window.ISKVW
    - .refresh()         → re-fetch + re-render galería actual.
    - .open(id)          → abre lightbox por id.
    - .close()           → cierra lightbox.
    - .state             → estado interno read-only.

13. Estructura de archivos
    /
    ├── index.html         → Home / archivo
    ├── about.html         → Statement + contacto (NUEVO v4.0)
    ├── 2d.html            → Masonry dibujo
    ├── 3d-immersion.html  → Pieza "Malla Reactiva"
    ├── obra.html          → Detalle ?id=<slug>
    ├── 404.html           → No encontrada (NUEVO v4.0)
    ├── CURATOR.html       → Panel privado n8n
    ├── README-AGENTS.txt  → Este archivo
    ├── manifest.json
    ├── robots.txt
    ├── sitemap.xml
    ├── _headers           → Cloudflare Pages headers
    ├── _routes.json
    ├── wrangler.jsonc
    ├── package.json
    ├── .gitignore
    ├── .vscode/settings.json
    ├── css/styles.css
    ├── js/app.js          → controlador home/2d/lightbox
    ├── js/obra.js         → renderer obra.html
    ├── js/3d-scene.js     → escena Three.js
    ├── data/works.json    → 5 obras placeholder con flag "placeholder":true
    └── assets/
        ├── favicon.svg
        ├── og-cover.svg   → 1200×630 social share
        └── apple-touch-icon.png  (opcional, no incluido aún)

[2] PRINCIPIOS DE DISEÑO — NO ROMPER
--------------------------------------------------------------------------------
- Una sola tipografía display (Fraunces). Una sola mono (JetBrains).
  Si querés añadir tipografía, primero quitá una.
- Monocromo. Sin acento. La italic es el único "color".
- Espacios grandes. Padding generoso. El whitespace es contenido.
- El header es siempre mix-blend-mode: difference. No agregar fondo sólido.
- Las obras con placeholder:true llevan badge [WIP] visible. No esconderlo
  por estética. La transparencia es parte de la voz.
- Los textos del sitio NO usan: "exploración", "sintetiza", "yuxtapone",
  "curatorial", "disrupción", "dualidad", "narrativa visual". Son palabras
  que delatan IA o portafolio genérico. Preferir verbos + sustantivos
  concretos.
- Email, año, instagram, ciudad: SIEMPRE consistentes en todo el sitio.

[3] ROADMAP (futuro)
--------------------------------------------------------------------------------
1. Reemplazar las obras [WIP] por obras reales de Maximiliano.
   - Subir imágenes optimizadas WebP/AVIF a /assets/works/.
   - Cambiar "placeholder": false en cada entrada de works.json.
2. Conectar n8n: subida desde Instagram → Cloudflare R2 → commit a works.json.
3. Apple touch icon PNG real (180×180).
4. Página /press o /selected con texto editorial sobre obras puntuales.
5. Sitemap dinámico generado a partir de works.json (script Node).
6. Audit Lighthouse / axe-core en CI.

[4] INSTRUCCIONES PARA EL SIGUIENTE AGENTE
--------------------------------------------------------------------------------
- NUNCA inyectar HTML sin sanear. js/app.js y js/obra.js exponen esc().
- NO crear README.md adicionales.
- NO reintroducir el cursor custom (problemas de a11y).
- NO reintroducir GSAP a menos que justifiques una animación específica
  imposible en CSS. La regla es: si lo podés hacer con transition o
  IntersectionObserver, hacelo así.
- NO usar lorem ipsum. Si falta texto, dejá comentario <!-- TODO --> o
  pediselo a Maximiliano.
- ESTE archivo es el checkpoint. Actualizalo en cada cambio significativo.

// FIN DE ARCHIVO — v4.0
