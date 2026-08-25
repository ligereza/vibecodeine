# C02 Blender endpoint — LUNA A

- Contrato: `luna-a-c02-blender-native-observation-v1`
- Extractor: `luna-a-c02-blender-endpoint-v1`; upstream `mak-blender-scene-snapshot-run-v1`
- Estado: **observed**
- Alcance: observación nativa read-only; no render, no save, no copia ni reempaquetado del `.blend`.

## Contrato de evidencia

Cada hecho observado debe corresponder al snapshot nativo y a su digest de estado. El digest del archivo fuente se comprueba antes y después. Las rutas absolutas se eliminan del JSON entregado; los valores de ruta declarados por Blender se conservan como texto observado. `negative_is_evidence=false`: la ausencia en este probe no demuestra ausencia en el archivo.

## Integridad y ejecución

- Fuente: `/home/mak/curatoria_inbox/ARICA/RAYU.blend`
- SHA-256 esperado: `acafc1db0088016139921b1ea2c9d7a5310247658117fa7021662e13e907ce86`
- SHA-256 antes: `acafc1db0088016139921b1ea2c9d7a5310247658117fa7021662e13e907ce86`
- SHA-256 después: `acafc1db0088016139921b1ea2c9d7a5310247658117fa7021662e13e907ce86`
- Igualdad antes/después: `True`
- Exit code del wrapper: `0`
- Blender: `Blender 4.5.4 LTS`

## Hechos observados

- El probe devolvió `1` escena(s).
- Escena `Scene`: frames `1`–`300`, frame actual `274`, objetos `7`, colecciones `['Collection']`, view layer(s) `['ViewLayer']`.
- Cámara observada: `Camera` (`present=True`, tipo `CAMERA`).
- Settings observados: engine `CYCLES`, resolución `1920x1080` al `100%`, formato `PNG`, `film_transparent=True`, filepath declarado `C:/ARICA/LOGOOO/2/`.
- Estado nativo reportado por Blender: `dirty=True`; esto es estado de la sesión de lectura, no evidencia de que este endpoint haya guardado o modificado el archivo.
- Objeto observado `Spot`: tipo `LIGHT`, materiales `[]`, datos `{'name': 'Spot', 'type': 'SunLight'}`.
- Objeto observado `Line`: tipo `MESH`, materiales `['Light Soft', 'Light Strong', 'Plastic Black']`, datos `{'name': 'Cube.001', 'polygons_count': 46, 'type': 'Mesh', 'vertices_count': 48}`.
- Objeto observado `Cylinder`: tipo `MESH`, materiales `['Plastic Black']`, datos `{'name': 'Cylinder', 'polygons_count': 58, 'type': 'Mesh', 'vertices_count': 64}`.
- Objeto observado `Recurso 3`: tipo `MESH`, materiales `['Gold']`, datos `{'name': 'Recurso 3', 'polygons_count': 37400, 'type': 'Mesh', 'vertices_count': 18726}`.
- Objeto observado `Camera`: tipo `CAMERA`, materiales `[]`, datos `{'name': 'Camera.001', 'type': 'Camera'}`.
- Objeto observado `Ceiling Light Line`: tipo `EMPTY`, materiales `[]`, datos `{'name': None, 'type': 'NoneType'}`.
- Objeto observado `Recurso 2`: tipo `MESH`, materiales `['Glass Cyan']`, datos `{'name': 'Recurso 2', 'polygons_count': 3554, 'type': 'Mesh', 'vertices_count': 1777}`.
- Dependencias expuestas por el probe: `2`.
- Dependencia observada: tipo `image`, ruta declarada `//../Users/issvk/blenderkit_data/materials/glass-cyan_5ea2e67d-8f2c-4bab-bd98-2ec70634882d/textures_1k/metal-smudge-smoothness-3.jpg`, exists=`False`, packed=`True`; su ruta absoluta fue sanitizada del JSON.
- Dependencia observada: tipo `image`, ruta declarada `//../Users/issvk/blenderkit_data/materials/glass-imperfecti_04f951be-04b6-4e21-bd5d-36272a7d6f37/textures_1k/metal-smudge-smoothness-2.jpg`, exists=`False`, packed=`True`; su ruta absoluta fue sanitizada del JSON.

## Candidatos (no confirmados)

- El `render.filepath` observado es un candidato a destino configurado de render; no prueba que se haya renderizado allí ningún archivo.
- `RAYU.blend` es un candidato a archivo de authoring nativo observado; este endpoint no declara una obra final, entregable ni autoría.
- Las dos referencias de imagen son candidatas a recursos externos declarados por el documento. `packed=true` y `exists=false` se mantienen como hechos separados; no se declara automáticamente una textura faltante.

## Unknown

- No se puede determinar desde este snapshot si existe un MP4, si fue generado por este `.blend`, o si cualquier archivo de la carpeta es un entregable. La mera coexistencia de un MP4 no sería evidencia de salida del `.blend`.
- No se puede determinar la intención artística, la obra final, la versión aprobada, la calidad visual ni la relación con un catálogo público.
- El probe no expone una validación semántica completa de materiales, nodos o calidad visual; `exists=false` de una ruta externa no equivale por sí solo a recurso no disponible cuando `packed=true`.

## Reproducción

El comando efectivo de Blender está registrado en `evidence.probe.effective_blender_command` del JSON. El wrapper usado fue `python tools/blender_scene_probe.py --snapshot --input ARICA/RAYU.blend --output blender_endpoint/tmpea0dvxqb.json --timeout 120`.
