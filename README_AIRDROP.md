# 📦 FLUJO — Airdrop completo (v0.40)

Todo lo construido para Reduciendo Daño, en un solo paquete listo para el repo
`vibecodeine`. **Nada mueve/borra tus archivos** salvo que tú lo pidas; todo es
vanilla + stdlib (sin frameworks, sin dependencias, sin build).

---

## Qué trae

| Pieza | Qué hace | Comando |
|---|---|---|
| 🖥️ **serve** *(NUEVO)* | Servidor local que sirve el hub y expone `/api` (saca a los HTML del modo demo) | `py -m flujo serve --open` |
| 🧭 **route** | Resuelve dónde está / dónde va cada pieza en `C:\rd` (no mueve nada) | `py -m flujo route where --area eventos --pieza flyer` |
| 🔍 **index** | Indexa `C:\rd` para agentes: busca, versiones, duplicados, limpieza | `py -m flujo index agent-brief "..."` |
| 🩺 **doctor** *(NUEVO)* | Chequeo de entorno (hub + rutas + python) | `py -m flujo doctor` |
| 🎨 **hub** | 3 HTML corregidos y unificados (hub + plano + material) con estilo compartido | abrir `context/flujo_hub.html` |

---

## Instalar (1 paso)

**Windows:**
```
doble clic en  instalar.bat
   (o:  instalar.bat C:\ruta\a\vibecodeine )
```
Copia `src/flujo/...` y `context/...` a tu repo y corre `py -m flujo doctor`.

**Manual / Mac-Linux:** copia las carpetas `src/` y `context/` sobre el repo,
respetando la estructura. Luego desde `src/`:
```
py -m flujo doctor
py -m flujo serve --open
```

---

## Los dos modos del hub

| Modo | Cómo | Datos |
|---|---|---|
| **Demo** | doble clic en `context/flujo_hub.html` (`file://`) | embebidos en el HTML |
| **Real** | `py -m flujo serve` → `http://127.0.0.1:8777` | desde `/api/...` (Python) |

Los HTML detectan el modo solos (`Flujo.useDemo()`): `file://` = demo, servido = real.
Así puedes mostrar el hub sin internet/servidor, y cuando lo sirves, se conecta al backend.

---

## Endpoints que expone `serve`

| Endpoint | Devuelve |
|---|---|
| `GET /api/health/stats` | tarjetas del hub (lee `jobs/` si existe, si no demo) |
| `GET /api/materials` | material RD (lee `context/data/materials.json` o demo) |
| `GET /api/materials/<id>/download` | stub de descarga |
| `POST /api/plano/render` | `{layout, rider, costos, total}` (mismo formato que el demo) |

> El servidor manda una **CSP** defensiva y bloquea path-traversal. Stdlib pura
> (`http.server`), sin abrir tu red (escucha en `127.0.0.1`).

---

## Estructura del airdrop

```
src/flujo/
  __init__.py        version
  __main__.py        dispatcher: py -m flujo <serve|index|route|doctor|version>
  serve/server.py    servidor + endpoints /api  (NUEVO)
  index/indexer.py   indexador de C:\rd
  route/resolver.py  router de rutas (+ rutas_rd.json)
context/
  flujo_hub.html · plano_demo.html · svg_visualizer.html
  shared/flujo.css · flujo.js
  data/materials.json    (editable: alimenta /api/materials)
instalar.bat · abrir_hub.bat
docs/INTEGRACION_CLI.md
HANDOFF_2026-06-28_full.md
```

---

## Integrar al dispatcher existente

Si tu repo ya tiene `py -m flujo app/health/portal`, **no reemplaces tu `__main__`**:
registra estos subcomandos junto a los tuyos. Ver `docs/INTEGRACION_CLI.md`.

## Reglas respetadas
Windows + `py` · ASCII-only en handoffs · sin tokens · sin dependencias externas ·
`<script src>` clásico (no ES modules, para que el doble clic siga funcionando) · sin CDN.
