# Implementacion 3D y vision por evento

Estado: plan tecnico derivado de la arquitectura de evento comun, 2026-09-20.

Documento base:
[`ARQUITECTURA_EVENTO_PRODUCTORA_RD_VJ_IRIS_XIO.md`](ARQUITECTURA_EVENTO_PRODUCTORA_RD_VJ_IRIS_XIO.md).

## 1. Dos representaciones 3D, dos funciones

No conviene pedirle a un unico artefacto 3D precision operacional y expresion
visual al mismo tiempo.

### Modelo operacional

Una escena `GLB/glTF` liviana, en metros y con sistema de coordenadas
declarado. Contiene:

- piso, limites y zonas transitables;
- escenario, FOH, accesos, salidas y stand RD;
- pantallas, proyectores, luminarias y puntos de energia;
- anclas medibles, oclusiones y rutas;
- procedencia, precision estimada y fecha de captura.

Este modelo pertenece a `venue_revision_ref`. Un evento referencia una
revision congelada y puede agregar un overlay de montaje temporal.

### Captura expresiva

Un Gaussian Splat `PLY` maestro y `SPZ` movil conserva apariencia, luz y
atmosfera. Sirve a IRIS como memoria espacial y al VJ como material visual
reactivo. No se usa para afirmar distancias, aforo, rutas de evacuacion ni
medidas de seguridad.

## 2. Pipeline 3D

```text
captura XIO
  -> fotos/video + IMU + patron de escala + event_id
  -> limpieza y exclusion de rostros/datos sensibles
  -> offload: poses COLMAP
  -> A) malla/plano operacional -> GLB
  -> B) entrenamiento 3DGS -> PLY maestro -> SPZ movil
  -> registro IRIS + paquete offline XIO
```

Decisiones de implementacion:

1. Empezar con plano 2D extruido y anclas manuales; entrega utilidad antes de
   depender de reconstruccion automatica.
2. Capturar con exposicion bloqueada y un marcador de escala visible. Sin
   escala o calibracion, declarar geometria relativa.
3. Entrenar COLMAP/3DGS fuera del Xiaomi, en GPU local o nube. XIO captura y
   renderiza; no entrena.
4. Mantener `PLY` como maestro y generar `SPZ` para el visor WebGL/WebGPU del
   telefono. Mantener el GLB operacional por separado.
5. Asociar cada salida con hashes de las capturas, version de pipeline,
   `event_id`, `venue_revision_ref` y restricciones de uso.
6. En eventos posteriores, comparar la nueva captura contra la revision
   anterior. Proponer cambios; nunca asumir que el layout sigue igual.

Primera entrega util: visor offline con un GLB, cinco tipos de ancla
(`stage`, `foh`, `rd`, `access`, `projection_surface`) y overlay separado para
cada evento. Segunda entrega: SPZ reactivo por OSC. Tercera: automapping de
luminarias a partir de mediciones calibradas.

## 3. El modelo de vision no es uno solo

Se comparte la infraestructura de captura y evidencia, no los objetivos ni
los datos. Deben existir cabezas/modelos separados.

### Vision RD: similitud visual de muestras

Objetivo: recuperar candidatos visualmente parecidos para revision. Nunca
afirmar identidad quimica, pureza, dosis ni seguridad.

```text
foto
  -> control de calidad
  -> segmentacion de la muestra
  -> color + forma + proporcion + relieve + marca/OCR
  -> embedding visual
  -> busqueda en indices pharma e ilicito separados
  -> calibracion open-set / abstencion
  -> candidatos + evidencia + revision
```

Implementacion incremental:

1. Baseline reproducible con las features existentes y busqueda por embedding.
2. Dataset por `group_id` de muestra/pilltype; nunca split aleatorio por foto.
3. Backbone movil (`EfficientNet-Lite0` o `MobileNetV3`) entrenado como
   embedding metrico, no como clasificador cerrado de identidad.
4. Holdout por muestra, serie y fuente; calibracion separada del umbral de
   desconocido.
5. Fusion tardia: similitud del embedding mas color/forma/marca, conservando
   cada evidencia visible.
6. Exportacion TFLite cuantizada para inferencia offline en XIO.
7. Prediccion original y anotacion posterior permanecen en campos distintos.

Metricas minimas: recall@k, precision de rechazo open-set, calibracion,
cobertura/abstencion y resultados separados por corpus. Accuracy cerrada por
si sola no alcanza.

### Vision venue/show: espacio, luz y operacion

Objetivo: producir observaciones para la revision espacial del venue y para
el preflight del evento.

- detectar superficies de proyeccion, escenario, FOH, accesos y luminarias;
- estimar zonas y anclas, siempre con confianza y posibilidad de correccion;
- medir brillo, color y flicker con captura calibrada;
- describir ocupacion solo de forma agregada, sin reconocimiento facial;
- alimentar reconstruccion 3D con frames seleccionados y poses.

El detector no decide rutas de seguridad ni modifica cues. Publica una
propuesta que IRIS relaciona y que XIO puede presentar al operador.

## 4. Contrato comun de observacion

```json
{
  "observation_id": "obs_<id>",
  "event_id": "evt_<id>",
  "domain": "rd|vj_foh|venue",
  "captured_at": "<UTC>",
  "sensor_ref": "xio:<device>",
  "subject_ref": "<referencia de dominio>",
  "model_ref": "<nombre@version>",
  "output": {},
  "confidence": 0.0,
  "abstained": false,
  "evidence_refs": [],
  "privacy_class": "operational|protected|restricted"
}
```

La salida entra al flujo de XIO:

```text
observacion -> snapshot -> propuesta -> accion explicita -> resultado -> audit
```

## 5. Entrenamiento y despliegue

- Preparacion, splits y evaluacion se ejecutan en MAK.
- Azure ML/MLflow registra dataset fingerprint, codigo, metricas y artefactos
  sanitizados. El cluster CPU existente sirve para ETL/evaluacion; el
  fine-tuning visual requerira GPU local o compute GPU temporal.
- XIO recibe solamente el TFLite versionado, etiquetas, umbrales, contrato y
  hash. Funciona offline.
- IRIS recibe observaciones y relaciones; no necesita copiar imagenes RD
  protegidas para aprender el contexto del evento.
- Cada nueva version debe vencer al baseline en replay sin mezclar fotos del
  mismo grupo entre train y test.

## 6. Orden de construccion decidido

1. Crosswalk `event_id` sin migrar ni fusionar las autoridades existentes.
2. Contrato de observacion y paquete de evento offline.
3. GLB operacional manual/semi-manual con overlays por evento.
4. Baseline visual RD con abstencion y evaluacion por grupos.
5. Vision venue/show sin biometria.
6. Pipeline COLMAP + 3DGS offload y visor SPZ movil.
7. Aprendizaje entre eventos mediante propuestas trazables de IRIS.

Este orden produce utilidad de campo temprano y evita que una reconstruccion
3D o un modelo visual no calibrado se conviertan en autoridad.

## 7. Vertical ejecutable integrada

El incremento del 2026-09-20 materializa dos piezas que faltaban:

1. FLUJO consume el ledger append-only de MAK, verifica su cadena hash y crea
   una proyección SQLite regenerable. Cada referencia se consulta por igualdad
   exacta en su autoridad: `eventRef` en RD y `eventKey` en VJ/FOH. Los nombres,
   fechas y productoras nunca producen una equivalencia automática.
2. `XIO_LAYER.core.event_session` compone preflight, observaciones, GLB/SPZ,
   snapshot, propuesta, acción explícita, resultado, auditoría y cierre. La
   validación completa precede a cualquier escritura o handler.

El cierre `iris-event-memory-v1` no copia outputs ni sujetos de observaciones.
Conserva fuente, modelo, confianza, abstención y fingerprints SHA-256 de la
evidencia, además de relaciones de evento y hashes de artefactos espaciales.
El GLB sigue perteneciendo a `venue_revision_ref`; el SPZ conserva memoria
expresiva de `event_id` y no adquiere autoridad geométrica.

En el smoke local había 68 referencias RD y 7 eventos VJ. Dos crosswalks
independientes apuntaron a una referencia real de cada autoridad y ambos se
resolvieron exactamente. No se unieron como una misma ocurrencia porque no
existe evidencia revisada que autorice esa relación. La sesión completa se
validó con un fixture representativo que incluye una observación RD protegida,
una observación de venue, GLB, SPZ, propuesta, autorización, resultado,
auditoría y memoria IRIS sanitizada.

La validación Android pendiente se ejecutó en la misma fecha con Temurin
17.0.20.1, plataforma Android 34, build-tools 34.0.0, platform-tools 37.0.1 y
Gradle 8.7. Los proyectos RD Field y FOH Monitor completaron
`clean assembleDebug`; la instalación y prueba física en el Xiaomi siguen
siendo un gate distinto.

Ese gate físico se completó después: los APK debug RD Field 0.1.0 y FOH Monitor
0.4.0 se instalaron con conservación de datos en el Xiaomi Android 14. Los dos
arrancaron en frío, mantuvieron proceso vivo y no registraron excepciones
fatales. Las capturas de validación no se incorporaron al repositorio porque
contienen estado operacional local.

La vertical de campo real permanece correctamente bloqueada: no se encontró
un ledger crosswalk revisado ni archivos GLB, SPZ o PLY reales. El sistema no
crea esos artefactos ni una equivalencia RD/VJ para satisfacer una prueba.
