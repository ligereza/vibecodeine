# MEMORIAS.md

Memoria consolidada de MAK, auditada el 2026-09-03. Este archivo conserva
continuidad útil para el operador; no es contrato, no reemplaza una medición y
no convierte una hipótesis histórica en un hecho actual.

## Contexto del operador

- `MAK` es el computador Linux completo.
- La rama MAK está montada en `/home/mak`; la rama FLUJO está montada en
  `/home/mak/flujo`. Son dos checkouts del mismo proyecto, con responsabilidades
  distintas.
- `vibecodeine` es el repositorio y `ISKVW`/`iskvw.cl` es la superficie pública
  del trabajo artístico. `IRIS` es el sistema interno de orden y relación.
- Reduciendo Daño (RD), Cultura, el trabajo VJ y el archivo ISKVW comparten
  intereses en eventos, productoras y venues, pero no se deben confundir sus
  autoridades ni sus datos.
- FLUJO APP es un conjunto de herramientas de autoría/integración. El flujo
  operativo que el operador reconoce como real es la señal de correo con tema
  `EVENTO`, que llega a Git y crea un issue. La lectura de esos issues debe ser
  de solo lectura para no generar un bucle de respuesta.
- La descarga del flyer, OCR/visión, render Blender, Drive y las bases de
  eventos/productoras/venues son partes relacionadas del trabajo, pero cada
  relación debe demostrarse por consumidor y fuente, no por proximidad de
  carpetas.

## Historia que se conserva sin elevarla a presente

- Las memorias de continuidad de Codex registran trabajos sobre IRIS/Atlas,
  Hub, archivo ISKVW, bases, conciliaciones, pruebas, XIO y exportaciones.
- Las memorias de Claude registran lecciones de búsqueda, autoridad local,
  issues, entregas RD, operación VJ, XIO y límites de los agentes.
- `MEMORIA_DIRECCION.md`, los handoffs, informes y documentos de sesiones
  contienen ideas y decisiones valiosas, pero sus cifras y rutas se consideran
  históricas hasta volver a medirlas.
- Los documentos `CAPACIDADES_MAK.md` y `CAPACIDADES_FLUJO.md` anteriores se usaron como fuentes de
  contraste. Sus duplicados, worktrees y copias de `_archive` no son nuevas
  autoridades: son historia o material de otra ejecución.

## Corrección puntual — 2026-09-08 (no es una nueva auditoría del resto)

`IRIS` nombra dos cosas distintas y hoy las dos están vivas; equivocar cuál se
mira es el error que dos agentes seguidos cometieron:

- el **sistema interno de orden y relación** (línea de arriba), que vive
  *dentro* del checkout MAK — `cultura/mak_plataforma/hub.py`,
  `iskvw/editor.html` + `iskvw/mesa_montaje.js` — y donde ocurre casi todo el
  trabajo reciente con scope de commit `iris:` (mesa de montaje, modo de
  performance en vivo, etc.);
- el **repositorio `ligereza/IRIS`**, clonado aparte en `/home/mak/IRIS`.
  Medido el 2026-09-08: sigue siendo un límite de producto vacío en código
  (`Establish IRIS private product boundary`) y desde el 2026-09-07 además
  contiene, en la rama `postulacion/fondart-regional-2027`, el dossier de la
  postulación FONDART Regional Creación 2027. Ninguna obra ni código de la
  mesa de montaje vive ahí todavía.

`/home/mak/flujo` es un **worktree** del mismo `.git` de `/home/mak`
(`gitdir: /home/mak/.git/worktrees/flujo-closeout`), no un segundo
repositorio — vale la pena decirlo explícito porque "dos checkouts" (línea de
arriba) se lee fácil como "dos repos".

