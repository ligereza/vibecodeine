# Revision del segundo set React/Vite adjunto

Fecha: 2026-06-28
Archivos revisados desde upload:

- `index.html`
- `package.json`
- `package-lock.json`
- `tsconfig.json`
- `vite.config.ts`
- `App.tsx`
- `index.css`
- `main.tsx`
- `NavBar.tsx`
- `Plano.tsx`
- `Visualizer.tsx`
- `Hub.tsx`
- `cn.ts`
- `flujo.ts`

## Veredicto

Este segundo set esta mucho mejor que el anterior. Si se ordena en una estructura Vite normal, compila y genera un HTML single-file.

Aun asi, mi recomendacion es no convertirlo todavia en el runtime principal de `flujo app`. Conviene tratarlo como prototipo visual serio / laboratorio UI y portar sus mejores ideas al hub vanilla actual, o guardarlo aislado en `tools/hub_react_prototype/`.

## Prueba tecnica ejecutada

Reordene temporalmente los archivos asi:

```txt
react_review/
  package.json
  package-lock.json
  tsconfig.json
  vite.config.ts
  index.html
  src/
    main.tsx
    App.tsx
    index.css
    components/
      NavBar.tsx
      Hub.tsx
      Plano.tsx
      Visualizer.tsx
    utils/
      cn.ts
```

Comandos ejecutados:

```bash
npm ci --no-audit --no-fund
npm run build
npx tsc --noEmit
```

Resultado:

- `npm ci`: OK
- `npm run build`: OK
- `npx tsc --noEmit`: OK
- salida single-file: `dist/index.html`, aprox. 246 KB, gzip aprox. 73 KB

## Problemas / ajustes necesarios antes de integrar

1. Estructura de carpetas

Los archivos llegaron planos, pero `App.tsx` importa:

```ts
import NavBar from './components/NavBar';
import Hub from './components/Hub';
import Plano from './components/Plano';
import Visualizer from './components/Visualizer';
```

Por lo tanto deben vivir dentro de `src/components/`.

2. `flujo.ts` parece duplicado u obsoleto

`flujo.ts` contiene el mismo bootstrap que `main.tsx`, pero con JSX dentro de `.ts`. No deberia integrarse. Usar solo `src/main.tsx`.

3. Version desactualizada

La UI muestra `v0.36.3`, pero el repo quedo sincronizado como `0.40.1`.

Debe cambiarse a una version dinamica o al menos a `0.40.1`.

4. Datos demo hardcodeados

`Hub.tsx`, `Plano.tsx` y `Visualizer.tsx` tienen muy buena maqueta, pero la mayoria opera con arrays locales/demo.

Para integracion real deberia conectarse progresivamente a:

```txt
/api/health/stats
/api/list-jobs
/api/list-svg-works
/api/materials
POST /api/plano/render
```

5. Fuente externa

`index.css` importa Google Fonts:

```css
@import url('https://fonts.googleapis.com/...');
```

El preview interno y la filosofia offline/local-first no deben depender de red. Mejor usar font stack local o bundlear fuente si algun dia se justifica.

6. Stack Node como dependencia nueva

Agregar React/Vite/Tailwind al repo raiz cambia el modelo de mantenimiento:

- nuevo `package.json` en raiz;
- `package-lock.json` grande;
- build step Node;
- dependencias y posibles alertas npm;
- otra ruta de CI.

Esto puede ser correcto mas adelante, pero no deberia mezclarse con el hotfix actual de coherencia/versionado.

7. `dangerouslySetInnerHTML`

`Visualizer.tsx` usa `dangerouslySetInnerHTML` para SVG demo generado internamente. Esta bien para demo controlada, pero si se alimenta desde archivos o datos externos necesita sanitizacion/allowlist.

## Lo que vale mucho la pena rescatar

Este set ya esta conceptualmente alineado con el repo:

- `Hub.tsx`: dashboard operativo con pipeline, intake, comandos, rutas EVENTOS/SUPLEMENTOS y estado.
- `Plano.tsx`: buen prototipo UI para `POST /api/plano/render`; tiene formulario, SVG, rider y costos.
- `Visualizer.tsx`: buen prototipo de catalogo visual con filtros, grid/list y modal.
- `NavBar.tsx`: navegacion simple Hub / Plano / Visualizador coherente con `context/flujo_hub.html`, `plano_demo.html`, `svg_visualizer.html`.
- `vite-plugin-singlefile`: buena decision si se quiere exportar un solo HTML offline.

## Recomendacion practica

### Opcion A - recomendada ahora

No integrar React todavia. Portar visualmente las mejoras a:

```txt
context/flujo_hub.html
context/plano_demo.html
context/svg_visualizer.html
context/shared/flujo.css
context/shared/flujo.js
```

Ventaja: mantiene `py -m flujo app` simple, sin Node, sin build y compatible con airdrop.

### Opcion B - laboratorio aislado

Guardar el prototipo como subproyecto aislado:

```txt
tools/hub_react_prototype/
```

Con README claro:

```bash
cd tools/hub_react_prototype
npm ci
npm run build
```

Y NO usarlo como entrada diaria hasta conectar APIs reales.

### Opcion C - futuro runtime React

Solo si se decide que React sera la UI oficial:

1. mover fuentes a `src/flujo/webapp/` o `tools/hub_react_prototype/`;
2. CI separado para `npm ci && npm run build && npx tsc --noEmit`;
3. generar single-file y copiarlo a `context/flujo_hub.html` o asset empaquetado;
4. eliminar Google Fonts externa;
5. conectar APIs reales;
6. preservar fallback demo/doble clic.

## Decision sugerida

Para el arreglo actual: no meter estos archivos al runtime.

Para el siguiente paso visual: usar este segundo set como blueprint para una mejora del hub vanilla actual, especialmente:

- nueva estructura de tabs Hub / Plano / Visualizador;
- cards y comandos de `Hub.tsx`;
- layout de formulario/rider/costos de `Plano.tsx`;
- filtros grid/list/modal de `Visualizer.tsx`.
