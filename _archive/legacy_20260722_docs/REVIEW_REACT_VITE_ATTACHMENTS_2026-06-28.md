# Revision de archivos React/Vite adjuntos

Fecha: 2026-06-28
Archivos revisados desde upload:

- `package.json`
- `package-lock.json`
- `tsconfig.json`
- `vite.config.ts`
- `index.html`
- `index.css`
- `main.tsx`
- `flujo.ts`

## Juicio corto

No conviene integrar estos archivos tal cual al repo `vibecodeine`.

Si se consideran, deben tratarse como un prototipo visual externo para inspirar el hub actual, no como reemplazo directo de `context/flujo_hub.html` ni de la app Python/local-first.

## Problemas tecnicos detectados

1. Archivos cruzados o mal nombrados

- `index.css` contiene codigo React/TSX completo (`function App()`, JSX, imports). No es CSS.
- `main.tsx` contiene CSS real (`@import "tailwindcss"`, estilos scrollbar, `.font-mono`).
- `flujo.ts` contiene codigo de bootstrap React con JSX, pero la extension `.ts` no corresponde. Deberia ser `.tsx`.

2. Estructura Vite incompleta

`index.html` apunta a:

```html
<script type="module" src="/src/main.tsx"></script>
```

Pero los archivos adjuntos no vienen dentro de `src/` y falta una estructura consistente:

```txt
src/main.tsx
src/App.tsx
src/index.css
src/types/flujo.ts
src/utils/cn.ts
```

3. Imports faltantes

El componente importa:

```ts
import { MOCK_JOBS, MOCK_ISSUES, JobStatus } from './types/flujo';
import { cn } from './utils/cn';
```

Pero esos archivos no fueron adjuntados.

4. Versiones y dependencias pesadas para el objetivo actual

El prototipo agrega stack Node/Vite/React/Tailwind/Framer/Lucide. Eso choca con la direccion actual del repo:

- hub local simple;
- Python stdlib/vanilla para la app real;
- sin build obligatorio;
- compatible con Windows y airdrop;
- preview offline-friendly.

5. Datos mock y fechas/versiones incorrectas

El prototipo muestra datos hardcodeados como:

- `flujo v2.4.0-stable`
- `DATE: 2024-05-16`
- `Python 3.11.2`

El repo real esta en `0.40.1` y la continuidad activa esta en `context/LAST_HANDOFF.md`.

## Que si vale la pena rescatar

El prototipo tiene buenas ideas de UI:

- Sidebar clara: Hub Diario, Eventos, Suplementos, GitHub Issues, Logo Clean Lab.
- Header con command input tipo `py -m flujo ...`.
- Tarjetas de estado para jobs activos, revision, entregas, issues.
- Secciones separadas para EVENTOS, SUPLEMENTOS e Issues.
- Bloque de continuidad/handoff visible en el dashboard.
- Estetica dark/zinc/purple consistente con una app operativa moderna.

## Recomendacion de integracion

No crear una app React dentro del repo por ahora.

Mejor camino:

1. Usar este prototipo como referencia visual.
2. Portar solo conceptos al hub existente:
   - `context/flujo_hub.html`
   - `context/shared/flujo.css`
   - `context/shared/flujo.js`
3. Conectar las tarjetas a APIs existentes del server local:
   - `/api/health/stats`
   - `/api/materials`
   - APIs futuras de jobs/issues si se agregan.
4. Mantener `flujo app` como entrada diaria sin build Node.
5. Si mas adelante se decide adoptar React, hacerlo como subproyecto aislado, por ejemplo:

```txt
tools/hub_react_prototype/
```

y no como parte del runtime principal hasta que el build sea reproducible y el HTML final pueda empaquetarse offline.

## Si se quiere reparar el prototipo

Estructura minima sugerida:

```txt
hub-react-prototype/
  package.json
  package-lock.json
  tsconfig.json
  vite.config.ts
  index.html
  src/
    main.tsx        # contenido actual de flujo.ts
    App.tsx         # contenido actual de index.css
    index.css       # contenido actual de main.tsx
    types/flujo.ts  # MOCK_JOBS, MOCK_ISSUES, JobStatus
    utils/cn.ts     # clsx + tailwind-merge
```

Pero esto debe entrar como prototipo, no como reemplazo de la app principal.
