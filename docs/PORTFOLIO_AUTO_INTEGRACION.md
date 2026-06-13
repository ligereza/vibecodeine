# Integración — portfolio-auto

Fecha: 2026-06-12
Repo revisado: https://github.com/ligereza/portfolio-auto
Estado: público, dejado a medias / requiere integración con sistema de checkpoints.

---

## Resumen del repo

`portfolio-auto` es un portafolio/archivo digital estático para ISKVW / Maximiliano, armado con HTML, CSS y JavaScript vanilla.

Su objetivo declarado es funcionar como un portafolio dinámico y escalable, con carga de obras desde `data/works.json` y una idea de automatización mediante `CURATOR.html` + webhook n8n.

---

## Estructura observada

```txt
/
├── index.html
├── about.html
├── 2d.html
├── 3d-immersion.html
├── obra.html
├── 404.html
├── CURATOR.html
├── README.md
├── README-AGENTS.txt
├── package.json
├── wrangler.jsonc
├── _headers
├── _routes.json
├── manifest.json
├── robots.txt
├── sitemap.xml
├── css/
│   └── styles.css
├── js/
│   ├── app.js
│   ├── obra.js
│   └── 3d-scene.js
├── data/
│   └── works.json
└── assets/
    ├── favicon.svg
    └── og-cover.svg
```

---

## Qué ya tiene resuelto

### 1. Sitio estático funcional

- HTML/CSS/JS sin frameworks.
- Páginas base de portafolio.
- Home con archivo/galería.
- Página de obra individual `obra.html?id=...`.
- Página 2D.
- Página WebGL/3D.
- About y 404.

### 2. Sistema de datos

Usa:

```txt
data/works.json
```

como base de datos de obras.

Cada obra tiene un contrato tipo:

```json
{
  "id": "obra-slug",
  "title": "Título",
  "category": "2D | 3D | Animación | Generative | Foto",
  "year": 2026,
  "placeholder": true,
  "description": "Descripción corta",
  "descriptionLong": "Statement extendido",
  "image": "URL o asset",
  "gallery": [],
  "video": null,
  "tags": [],
  "technique": "",
  "mediaType": "image | video",
  "src": "",
  "poster": null
}
```

### 3. Curator panel

`CURATOR.html` funciona como panel privado para enviar payload a un webhook n8n.

Idea del flujo:

```txt
CURATOR.html
> webhook n8n
> validar payload
> leer data/works.json desde GitHub API
> insertar nueva obra
> commit/push
> rebuild Cloudflare Pages
```

### 4. Memoria de agentes

`README-AGENTS.txt` ya funciona como checkpoint/handover interno para futuras IAs.

Tiene:

- historial
- estado actual del código
- contrato de `works.json`
- principios de diseño
- roadmap
- instrucciones para el siguiente agente

Esto se integra bien con nuestro sistema actual de checkpoints.

---

## Problemas / deuda técnica detectada

### 1. Repo a medias

El portafolio está estructurado, pero parece todavía en estado WIP:

- `data/works.json` contiene placeholders.
- Falta subir obras reales.
- Falta cerrar automatización n8n.
- Falta validar si Cloudflare Pages está desplegando correctamente.
- Falta automatización real para optimizar/subir assets.

### 2. Dependencia de imágenes externas

`works.json` usa imágenes de Unsplash y un video externo de prueba.

Riesgos:

- dependencia de red externa
- performance variable
- estética placeholder
- no representa obra real
- posible inconsistencia si URLs cambian

### 3. Curator depende de n8n no implementado

El panel existe, pero el flujo n8n/GitHub API parece conceptual o pendiente.

Necesita:

- webhook real
- validación de payload
- manejo de errores
- token GitHub seguro
- read/modify/write de `works.json`
- commit automático
- trigger/rebuild

### 4. Falta pipeline de assets

No hay todavía un flujo completo para:

```txt
obra original
> optimización WebP/AVIF
> thumbnails
> poster video
> metadata
> works.json
> commit
> deploy
```

### 5. Falta conexión con tu sistema de diseño/motion

Todavía no está conectado con:

- flyers Blender/Photoshop
- slowmo Blender/After Effects
- Canva/CSV
- Illustrator/JSON
- checkpoints de producción
- IA avanzada para revisión visual

---

## Cómo integrarlo con ai-workflow-checkpoints

### Decisión propuesta

`portfolio-auto` no debe reemplazar el repo de checkpoints. Debe ser tratado como un **proyecto externo vinculado**.

```txt
ai-workflow-checkpoints = memoria/productor técnico/sistema operativo
portfolio-auto = producto/proyecto web/portfolio público
```

### Integración recomendada

Dentro de `ai-workflow-checkpoints`, registrar:

```txt
projects/portfolio-auto/
├── README.md
├── CONTEXTO.md
├── ESTADO_ACTUAL.md
├── ERRORES_PENDIENTES.md
├── PLAN_INTEGRACION.md
├── prompts/
└── checkpoints/
```

No copiar necesariamente todo el repo dentro del repo de checkpoints. Mejor usar link, submodule o clone local separado.

---

## Flujo futuro ideal

```txt
Obra/diseño/motion terminado
> script genera previews optimizados
> asistente genera metadata/statement
> IA avanzada revisa composición/contexto
> humano aprueba
> se crea entrada JSON
> se actualiza data/works.json
> commit en portfolio-auto
> deploy Cloudflare Pages
> checkpoint en ai-workflow-checkpoints
```

---

## Próximo paso recomendado

Cuando el usuario suba archivos o clone este repo localmente:

1. Auditar `portfolio-auto` con scripts.
2. Validar `works.json`.
3. Crear `projects/portfolio-auto/` dentro de checkpoints.
4. Marcar estado actual como WIP/error controlado.
5. Crear plan para reemplazar placeholders por obras reales.
6. Diseñar pipeline assets → metadata → JSON → deploy.

---

## Preguntas pendientes

1. ¿`portfolio-auto` será el portafolio público real o solo experimento?
2. ¿Quieres mantener estética ISKVW monocromo/editorial?
3. ¿Cloudflare Pages está funcionando ahora?
4. ¿Quieres usar n8n o prefieres scripts Git Bash/Python primero?
5. ¿Las obras reales vendrán desde carpetas locales, Instagram, Blender, After Effects o Canva?
