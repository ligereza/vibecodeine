# SPEC · Resolume + Chataigne Automator

## 1. Objetivo

Crear una ruta local y verificable para convertir pedidos de shows en vivo del area **EVENTOS** en una sesion de automatizacion para **Chataigne**, disparando acciones OSC hacia **Resolume Arena**.

Entrada operativa esperada:

```txt
Gmail subject:eventos
  -> Google Apps Script / GitHub Issue [EVENTOS]
  -> job local en jobs/{job_id}/
  -> py -m flujo resolume automatizar jobs/<job_id>
  -> jobs/{job_id}/deliverables/show_automation.xml
```

## 2. Alcance inicial

El automator base realiza un pre-flight funcional:

1. Lee un job local desde `jobs/{job_id}/`.
2. Detecta setlists con timecode SMPTE en `intake.json` o `brief.md`.
3. Normaliza marcas `HH:MM:SS:FF`.
4. Genera XML valido con estructura de sesion, modulos, salida OSC y cues.
5. Enruta acciones OSC hacia Resolume Arena en `127.0.0.1:7000`.

El objetivo es dejar un contrato estable para que un agente de pipeline expanda el formato `.noisette` nativo cuando se confirme el esquema exacto requerido por la instalacion local de Chataigne.

## 3. Formatos de entrada

### 3.1 `intake.json`

El parser acepta una de estas llaves principales:

```json
{
  "area": "eventos",
  "fps": 30,
  "setlist": [
    {
      "title": "Intro",
      "start": "00:00:00:00",
      "duration": "00:02:15:00",
      "clip": 1,
      "layer": 1
    },
    {
      "title": "Tema 1",
      "smpte": "00:02:15:00",
      "duration_seconds": 180,
      "clip": 2,
      "layer": 1
    }
  ]
}
```

Tambien se reconocen las llaves `tracks`, `songs`, `scenes`, `escenas`, `temas` o `canciones` cuando contienen una lista de objetos.

Campos equivalentes aceptados por escena:

- Nombre: `title`, `name`, `tema`, `song`, `scene`, `escena`.
- Inicio SMPTE: `start`, `smpte`, `timecode`, `tc`, `inicio`.
- Duracion: `duration`, `duracion`, `length`, `duration_seconds`.
- Capa Resolume: `layer`, `capa`.
- Clip Resolume: `clip`, `columna`, `column`.

### 3.2 `brief.md`

El parser detecta lineas que incluyan SMPTE `HH:MM:SS:FF`. Ejemplos validos:

```markdown
- 00:00:00:00 Intro / apertura layer 1 clip 1
- 00:02:15:00 Tema 1 layer 1 clip 2 duracion 180s
00:05:15:00 | Tema 2 | layer:1 | clip:3
```

Si faltan layer o clip, el pre-flight asigna `layer=1` y `clip` incremental segun el orden.

## 4. Timecode SMPTE

Formato obligatorio:

```txt
HH:MM:SS:FF
```

Donde:

- `HH` horas, dos digitos.
- `MM` minutos, `00` a `59`.
- `SS` segundos, `00` a `59`.
- `FF` frames, menor al FPS seleccionado.

FPS por defecto: `30`. El valor puede venir desde `intake.json` (`fps`, `frame_rate`) o desde el comando CLI.

## 5. Salida XML pre-flight

Archivo generado:

```txt
jobs/{job_id}/deliverables/show_automation.xml
```

Contenido conceptual:

```xml
<chataigneSession version="preflight-1" generator="flujo.resolume.automator">
  <modules>
    <timecode fps="30" source="smpte" />
    <oscOutput name="Resolume Arena" host="127.0.0.1" port="7000" />
  </modules>
  <timeline>
    <cue name="Intro" smpte="00:00:00:00">
      <osc address="/composition/layers/1/clips/1/connect" value="1" />
    </cue>
  </timeline>
</chataigneSession>
```

El XML es deliberadamente simple, legible y validable con `xml.etree.ElementTree`. Sirve como contrato intermedio estable y como base para producir `.noisette` si se necesita compatibilidad nativa completa.

## 6. Mapping OSC hacia Resolume

Destino por defecto:

```txt
Host: 127.0.0.1
Port: 7000
```

Patron OSC por defecto para disparar clips:

```txt
/composition/layers/{layer}/clips/{clip}/connect
```

Valor enviado:

```txt
1
```

## 7. Comando operativo

```bash
py -m flujo resolume automatizar jobs/<job_id>
```

Opciones previstas:

```bash
py -m flujo resolume automatizar jobs/<job_id> --fps 25
py -m flujo resolume automatizar jobs/<job_id> --host 127.0.0.1 --port 7000
```

## 8. Criterios de aceptacion

- Si el job no existe, el comando falla con mensaje claro.
- Si no hay `intake.json` ni `brief.md`, el comando falla con mensaje claro.
- Si no hay escenas con SMPTE valido, el comando falla con mensaje claro.
- Si un timestamp tiene frames fuera del FPS configurado, el comando falla con mensaje claro.
- El XML generado debe poder parsearse con `xml.etree.ElementTree`.
- No se deben guardar credenciales ni rutas externas sensibles.
