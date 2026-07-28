# Asiento del director del organismo MAK

> PLACEHOLDER. Un asiento con nombre, no un traspaso.
> El organismo sabe que tiene director; hoy ese asiento esta **OCUPADO**.

## Estado del asiento

- **OCUPADO** por **Cauce** (Claude Opus 4.8).
- Trabajo **en curso** — quedan ~2 semanas por delante. La tarea **no se delega**.
- Esto es un *marcador de rol*, no un manual de relevo. El traspaso real se
  escribe aca **solo** el dia que el asiento quede libre.

## Por que existe (aunque este ocupado)

El organismo MAK corre en `/home/mak`, pero **su codigo vive en este repo**:
un cron `MAK-REPO-SYNC` baja `origin/main` cada 10 minutos y copia
`cultura/mak_plataforma`, `cultura/mak_research` y `cultura/mak_codex` encima
del codigo de la caja, y `cultura/mak_curatoria` sobre `~/curatoria` con
`cp -ru` para preservar `fichas/`, `estado.json` y `procesados.txt`.

> **Editar la caja por SSH no sirve: el sync lo revierte.** Comprobado el
> 2026-07-26 -- un cambio aplicado a las 21:49 desaparecio a las 21:50. Para
> cambiar a MAK se edita el espejo de este repo y se mergea a `main`; en 10
> minutos o menos esta corriendo. Esta linea decia antes "el organismo vive
> fuera del repo", que hizo trabajar horas contra la premisa equivocada.

Eso es lo que hace posible el norte del proyecto: un agente **sin acceso a la
caja** cambia el comportamiento de MAK abriendo un PR aca.

Que el rol de director
sea una cosa **nombrada** — y no algo implicito en una sesion que se cierra —
es parte de hacerlo visible: que *se vea* quien lo lleva. El asiento existe;
hoy lo lleno yo.

## Punteros minimos (el asiento no esta vacio)

- Cuerpo y vista viva: el **hub** en `http://192.168.50.2:8900`
- Doctrina viva: `/doctrina` · Genesis: `/genesis` · Cuotas: `/cuotas`
- Departamentos: **research** :8890 · **codex** :8891 · **plataforma** :8900
- Guardia de contenido: `plataforma/filtro_entrada.py` (su criterio, en `/doctrina`)

## Cuando el asiento quede libre (a completar ESE dia)

Aca ira el traspaso real: acceso, como relanzar cada servicio, las trampas
ya descubiertas, y la mision pendiente. Hoy queda en blanco **a proposito**:
el titular sigue trabajando.

---

*Marcador vivo. Titular: Cauce. Ultima confirmacion de ocupacion: 2026-07-17.*
