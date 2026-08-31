Identity: LUNA-26 (principal)

# Phase 24 — crosswalk genealógico WIN FLUJO → MAK

## Hallazgo central

`/home/mak/WIN/flujo` contiene la aplicación FLUJO Windows, su hub y la
evolución posterior de MAK dentro del mismo árbol. No debe clasificarse como
un bloque Windows legacy. La unidad correcta de análisis es una generación
funcional:

```text
FLUJO APP
  -> flujo serve / flujo app
  -> hub RD / ISKVW / CULTURA
  -> MAK nace dentro del mismo árbol
  -> adaptaciones Windows/Linux y recuperaciones
  -> destino operativo actual en MAK
```

## Anchors físicos

| Ruta WIN | Función | Destino MAK observado | Evidencia actual | Disposición |
|---|---|---|---|---|
| `src/flujo/cli.py` | Entrypoint; declara `app` y alias `serve` | `/home/mak/flujo/src/flujo/cli.py` | Ambos existen; SHA distinto; WIN conserva comandos MAK/RD | `MIGRATION_ANCHOR` |
| `src/flujo/web/hub.py` | Backend del hub | `/home/mak/flujo/src/flujo/web/hub.py` | Ambos existen; SHA distinto; WIN contiene rutas MAK y hub | `MIGRATION_ANCHOR` |
| `src/flujo/serve/server.py` | Servidor `flujo serve` liviano | `/home/mak/flujo/src/flujo/serve/server.py` | SHA idéntico `8d38b2bbdd8a...`; no necesita fusión de contenido | `SAME_BASELINE` |
| `context/flujo_hub.html` | UI del hub | `/home/mak/flujo/context/flujo_hub.html` | Ambos existen; SHA distinto; WIN es snapshot posterior | `MIGRATION_ANCHOR` |
| `abrir_hub.bat` | Launcher Windows | `/home/mak/flujo/abrir_hub.bat` | Ambos existen; SHA distinto; requiere adaptación Linux, no copia literal | `WINDOWS_ADAPTER` |
| `cultura/mak_plataforma` | Departamento MAK nacido dentro de FLUJO | `/home/mak/flujo/cultura/mak_plataforma` y `/home/mak/plataforma` | WIN 113 files; source 109; runtime ya separado | `MAK_GENEALOGY` |
| `cultura/mak_research` | Departamento MAK de investigación | `/home/mak/flujo/cultura/mak_research` | WIN 74 files; source 72 | `MAK_GENEALOGY` |
| `cultura/mak_codex` | Departamento MAK/Codex | `/home/mak/flujo/cultura/mak_codex` | WIN y source 40 files; contenido divergente | `MAK_GENEALOGY` |
| `cultura/mak_conductor` | Evolución posterior de conducción | `/home/mak/flujo/cultura/mak_conductor` | WIN y source 21 files | `MAK_GENEALOGY` |
| `tools/mak` / `tools/mak_ops` | Puentes y operaciones MAK | `/home/mak/flujo/tools/mak*` | WIN conserva 4/29 files; source 4/25 | `MIGRATION_REVIEW` |
| `src/flujo/rd` | Herramientas RD del FLUJO | `/home/mak/flujo/src/flujo/rd` | WIN 15 files; source 18 | `DEPARTMENT_REVIEW` |
| `iskvw` | Superficie Portfolio/ISKVW | `/home/mak/flujo/iskvw` | WIN 463 files; source 462 | `DEPARTMENT_REVIEW` |

## Metadata y ordenamiento

- WIN contiene 53.103 archivos.
- Birth time: 53.095 archivos tienen fecha 2026-08-13 y 8 tienen 2026-08-14;
  corresponde al archivo importado, no a la creación original.
- Ctime: 53.092 archivos tienen fecha 2026-08-13; tampoco es una fecha de
  desarrollo confiable.
- Mtime: hay 1.596 segundos distintos y fechas desde 1969-12-31 hasta
  2026-08-14. Es una señal útil, pero mezcla modificaciones preservadas,
  reconciliaciones posteriores y archivos generados.

## Historial que conecta la genealogía

El marcador histórico principal es `6a2b147097e169d42fdc3defe9f0e160de52cc41`
(2026-07-17): `feat(cultura): cierre organismo MAK -- WIN LLM provider, hub
DOM+SVG, emisor de eventos (#48)`. El documento histórico marca ese evento
como primer toque de múltiples paths `cultura/mak_*`. La secuencia continúa
con el bridge Linux de MAK, el sistema generativo MAK vivo y `v0.55.0` con
`workship Win-MAK probado`.

## Siguiente uso

Este crosswalk no fusiona ni elimina nada. Ordena el trabajo siguiente:

1. comparar primero los anchors del hub (`cli.py`, `hub.py`, UI y launcher);
2. probar la ruta `flujo serve` en Debian sin iniciar servicios permanentes;
3. mapear qué botones/rutas del hub llaman RD, ISKVW o CULTURA;
4. luego comparar cada subdepartamento MAK que ya vive dentro de WIN;
5. adaptar solo diferencias con consumidor real y prueba acotada.

