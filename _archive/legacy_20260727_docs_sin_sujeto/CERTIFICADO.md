# Diez documentos cuyo sujeto ya no existe

Archivados el 2026-07-27, no borrados.

## Por que

`docs/` tenia 59 documentos en su raiz, TODOS escritos el 2026-06-30 y ninguno
tocado desde entonces. Se midieron dos cosas antes de mover nada:

1. **Quien los nombra.** 27 estan citados desde algun archivo vivo del repo; 32
   no los nombra nadie.
2. **Si su sujeto existe.** De esos 32, diez describen archivos concretos (`.py`,
   `.json`, `.tsx`) y NINGUNA de las rutas que nombran existe hoy en el repo.

Esos diez son los que estan aca. Un documento que explica como usar algo que ya
no esta no es documentacion: es una pista falsa, y este repo ya perdio sesiones
siguiendo pistas falsas.

## Lo que NO se archivo, a proposito

- Los 27 citados: tienen consumidor.
- Cuatro huerfanos con sujeto vivo (INTAKE_JSON, OPERACION_APP,
  PORTAL_JEFE_GRATIS, PRIMER_DIA): que nadie los enlace es falta de indice, no
  sobra de documento.
- Dieciseis huerfanos sin rutas verificables: no habia forma de decidir con
  evidencia, y borrar sin evidencia es lo que este archivo existe para evitar.

## Como recuperarlos

`git mv _archive/legacy_20260727_docs_sin_sujeto/<X>.md docs/`. Estan completos;
lo unico que cambio es donde viven.

## Y `AGENTS.md`

Archivado el mismo dia. Era un stub de 5 lineas que decia "el contenido esta en
CLAUDE.md, no leas este archivo", y se justificaba solo: "se mantiene por
convencion (herramientas que buscan AGENTS.md por nombre fijo)".

Medido: **ningun codigo de este repo lo lee.** Las unicas menciones vivas venian
de `.agents/`, que es una carpeta del checkout del usuario y ni siquiera esta
versionada. Ultima modificacion: 2026-07-08.

Yo habia decidido conservarlo diciendo que el usuario usa Codex y que esa
convencion lo buscaria. El usuario me corrigio dos veces y tenia razon las dos:
me invente el consumidor -- confundi `cultura/mak_codex`, que es un modulo del
organismo de MAK, con el Codex de OpenAI -- y ademas aplique el criterio del repo
al reves. La regla es que lo que no tiene consumidor MEDIDO se retira; sin uso, el
default es archivar y no quedarse.

Si alguna herramienta llega a necesitarlo, recuperarlo es un `git mv` y son cinco
lineas. Lo que no se puede recuperar es el tiempo del proximo que abra el repo y
tenga que averiguar cual de las dos entradas manda.
