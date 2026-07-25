# failed-handoff — sesion 2026-07-25

Sesion cerrada como **intento fallido**. Nada se commiteo ni se pusheo en el
cierre. Este documento existe para que quien retome no reconstruya nada.

Motivo del cierre: perdida de norte del asistente. Se dispersaba persiguiendo
cada hallazgo en vez de sostener el encargo (construir estructura), hacia tareas
que le habian pedido explicitamente que no hiciera, y abria frentes nuevos
dejando otros a medias.

---

## 1. Que quedo commiteado (ya en la rama, verificado)

Rama: `show/dref-preshow-20260724`. **No pusheada en el cierre.**

| Commit | Que |
|---|---|
| `8ac242c` | Perfiles de app + plano compartible (`dist_compartir/plano_rd.html`, 1 archivo sin instalacion) + iconos sillon doble / toalla nova |
| `b72efcb` | Panel **Show kit** + endpoint `/api/rd-db` + version real + rider **sin bloque de contactos** |
| `27a100b` | Panel **Automatizaciones** (cola Gmail -> issue -> render) |
| `9c30802` | Purga de informacion desactualizada en la app (7 hallazgos) |
| `1be876b` | Modulo de vectorizacion de logos |
| `e82e54c` | Panel **Base de datos RD** con reemplazo de logo + hub sin efectos al arrancar |

### Hallazgos reales corregidos ahi

- **La app mentia la version**: decia `0.51.0` con el repo en `0.56.1`, en 3 lugares.
- **El pipeline de IG que mostraba la app ya no existia**: citaba imginn (hoy en
  403 por Cloudflare) y Photoshop Droplet (retirado). La via real es parth-dl +
  Blender por nodos.
- **3 rutas de archivo citadas por la app no existian.** Queda un chequeo
  mecanico: de 21 rutas citadas, 0 rotas.
- **Bug de matcheo de logos**: los archivos no siempre se llaman como el slug
  (`grid_system.svg` vs slug `gridsystem`). Se reportaba "sin vector" sobre
  logos que si existian: el estado de la DB se veia peor que la realidad.
- **`flujo app` ejecutaba trabajo al abrirse.** `run_pending_flyers` se llamaba
  con `root=` en vez de `base_dir=`; el `except` se tragaba el TypeError y la
  automatizacion llevaba tiempo apagada sin que nadie lo supiera. Al corregirlo
  se encendio de golpe y proceso 7 jobs. Ahora es opt-in
  (`flujo app --procesar-pendientes`).

---

## 2. SIN COMMITEAR — en el working tree ahora mismo

**Ojo: esto esta en disco, funciona, y no esta en ningun commit.**

- `src/flujo/rd/eventos.py` (nuevo)
- `tests/test_rd_eventos.py` (nuevo, **18 tests verdes**)
- `src/flujo/web/hub.py` (modificado: integra los eventos normalizados en `_get_rd_db`)

Estado verificado antes de cerrar: `pytest tests/test_rd_eventos.py -q` -> 18
pass; `compileall` OK; endpoint probado contra un servidor real levantado.

**Que resuelve:** la triangulacion pendiente es "fecha + headliner ->
productora", pero en los datos la fecha es prosa (`"12 septiembre 2026"`,
`"MAR 28 (año no confirmado)"`) y el headliner esta enterrado en el titulo del
evento (`"... -- lineup PARTIBOI69 (co-org GLOVOX)"`). **No existian los dos
campos que cruzar.** El modulo los extrae a `fecha_iso`, `lineup[]` y
`co_organiza[]`, con nivel de confianza y sin inventar el año cuando falta.

**El numero que aparecio al integrarlo** (antes no se podia medir):

```
eventos: 7 | triangulables: 1 | sin lineup: 6 | sin fecha_iso: 3
```

Conclusion util: **la triangulacion no puede avanzar hoy aunque MAK vuelva.**
Faltan datos, no procesamiento.

Quedo sin hacer: mostrar esos contadores en `RdDbPanel.tsx` (4 lineas).

---

## 3. Anotado y NO tocado a proposito

| Que | Nota |
|---|---|
| `projects/piezas_vectoriales/cotizacion-general-...` | **Untracked.** Lo creo una prueba del asistente al procesar los 7 jobs. Es trabajo real generado sin pedirlo: borrarlo o conservarlo es decision del usuario |
| `test_ig_cffi_fallback` | Falla preexistente, verificado con el arbol limpio. Test fragil: asume `curl_cffi` ausente y esta instalado |
| `thegrid` vs `gridsystem` | Probable duplicado en la DB de productoras |
| Fondo transparente al vectorizar | **Sin resolver.** vtracer parte el fondo en varios paths; quitarlos por color borra partes del logo del mismo color. Documentado como limite en el modulo |
| `datadrops`, `delegate`, `cotizacion/render`, SSE | Backend sin UI. **datadrops medido: abandonado desde 2026-06-22** — no vale la pena hacerle pantalla |
| Logos de productoras | Los busca el usuario por web. **No via Instagram** (un subagente intento entrar a su cuenta: prohibido) |
| 8 SVG vectorizados | En `C:\Users\issvk\Documents\logos\svg\`. **Quedaron con fondo**, que el usuario declaro inservible. No se metieron al repo |

---

## 4. Contexto que costo reconstruir (no perderlo)

- **El portafolio no vive en este repo**: esta en `github.com/ligereza/portfolio-auto`
  (clon local `C:\IA\portfolio-auto-real`), publicado en **iskvw.cl**, vivo y con
  TLS OK. La rama `iskvw` de este repo es linea de gobernanza, no tiene el sitio.
- **La idea del portafolio, textual del usuario (2026-07-22):** *"3 secciones...
  cada seccion con su estetica independiente mas el menu de entrada... no que se
  muestren como ventanas sino como mundos separados, no que sean todas scifi
  tipo tablero neon verde sino que se diferencien."* Los 3 mundos:
  **[2D/3D] | [RD] | [VIBE-CODEINE]**. Norte actual: **app de portafolio
  automatica** (se deja una obra en una carpeta y corre la cadena curatoria ->
  publicacion). n8n ya fallo: **no reintentar**, va con watcher propio.
- **La referencia scifi** (`ref_scifi/`, en el scratchpad de la sesion
  `ef0dfb85`) no es un portafolio: es una **terminal con instrumentos
  generativos corriendo** (reaccion-difusion, Lorenz, red de nodos), con HUD de
  telemetria y audio. En la seccion 3D **el material cargado se vuelve textura
  del mesh**; en la 2D el canvas NO lee los pixeles del material (verificado:
  cero `getImageData`).
- **El intento v3 del portafolio** quedo completo en el working tree del clon en
  el scratchpad de `ef0dfb85`, **nunca pusheado**, y el PR #6 esta **cerrado sin
  merge**. El usuario lo evaluo: *"un portafolio tipico y horrible"* — el
  subagente no miro la referencia.
- **`doublecup` / el vaso semantico**: llego por bundle (`refs/remotes/bundle/svg`,
  commit `473c69f`, 127 archivos). Sistema generativo que **lee el repo** y
  produce un SVG autoanimado sin JS. Su README pide `servidor.py` para
  regeneracion por visita: *"es lo que justifica que la pieza salga de GitHub y
  viva en portafolio propio"*. **No esta en ninguna rama.**
- **La curatoria de MAK** quedo estancada en 2430/3132 fichas por `ollama`
  caido, y su salida (`~/curatoria/fichas/fichas.jsonl`) **nunca salio del disco
  de MAK**. Primer paso cuando MAK vuelva: copiarla a WIN antes de perderla.
- **RD**: reunion con los dos jefes fundadores. La jefa de eventos **no comparte
  contactos** (por eso el rider ya no los lleva). La herramienta de plano es
  privada para ella, para presentar a productoras.

---

## 5. Plan para retomar (en orden)

1. **Cerrar lo del punto 2**: commitear `eventos.py` + tests + `hub.py`, y
   mostrar los 4 contadores en `RdDbPanel.tsx`.
2. **Manual de independencia** en `docs/`: como se opera la app, como se agrega
   un perfil/panel/endpoint/icono, y las trampas ya pagadas (el rider no lleva
   contactos; los logos no se recortan de flyers; el hub no procesa jobs al
   arrancar; el server del telefono no arranca solo tras reboot; la IP cambia
   por DHCP en el venue).
3. **Division RD / ISKVW** sobre los perfiles ya construidos.
4. **Suplementos en la app** (es RD vivo, hoy solo existe como texto).

Fuera de alcance definido: portafolio automatico, modelo de datos enriquecido
del hub de AI Studio, y la propuesta a la directiva RD (no es codigo).

---

## 6. Reglas que el usuario dejo explicitas

1. **Estructura, no tareas.** Se construye la maquina; el usuario la dispara. Si
   aparece trabajo pendiente, **se anota y se sigue**.
2. **Nada a medias.** No se empieza lo siguiente sin cerrar lo anterior.
3. **Suciedad bajo la alfombra: se anota, no se limpia.**
4. **Cero efectos secundarios.** Ninguna prueba puede modificar datos del usuario.
5. **Medir antes de afirmar.**
6. **Subagentes solo para lectura de volumen acotada.** Nunca "construi esta
   feature": ya fallo dos veces.
7. **Nada de Instagram.** Ni scraping, ni la sesion del usuario.

---

## Verificacion al momento del cierre

```
py -m compileall src/flujo                  OK
py -m pytest tests/test_rd_eventos.py -q    18 passed
py -m pytest tests/ -q                      1 fallo: test_ig_cffi_fallback (preexistente)
npm run typecheck / build:context / build:plano   OK
```

Sin commit y sin push en el cierre, por orden del usuario.
