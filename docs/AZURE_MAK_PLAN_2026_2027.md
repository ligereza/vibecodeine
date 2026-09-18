# Plan de integracion Azure para MAK — 2026-2027

Fecha del corte: 2026-09-18  
Alcance: usar Azure como apoyo acotado del motor local MAK, FLUJO y XIO.  
Autoridad: MAK local y sus repositorios. Azure es una proyeccion auxiliar, nunca una segunda autoridad de datos.

## 1. Decisiones que fijan el plan

- MAK sigue siendo el motor estacionario: Hub `8900`, Research/Codex por sockets Unix, SearXNG local, Ollama y sus stores locales.
- FLUJO sigue siendo repositorio hermano y XIO sigue siendo el campo movil. Este plan no mueve el runtime XIO ni agrega pestañas o puertos.
- La base RD canonica no se migra masivamente a Azure. Azure puede recibir indices, respaldos o proyecciones declaradas; nunca reemplazar `data/rd.db`.
- La cuenta anual es MAK/Azure for Students: la sesion devuelve `quotaId=AzureForStudents_2018-01-01`, `spendingLimit=On` y credito de 100 USD por 12 meses.
- ISSVKK queda fuera del presupuesto anual de MAK y no se mezcla con Azure for Students. Puede ser usado por un agente ejecutor que corre en MAK, pero con presupuesto y control separados: su suscripcion devuelve `PayAsYouGo_2014-09-01` y `spendingLimit=Off`.
- Un servicio visible no se considera conectado. La prueba minima es: recurso vivo, credencial disponible, llamada exitosa, salida persistida y consumidor identificado.

## 2. Estado vivo que manda

Comprobado desde MAK por Azure CLI y ARM REST el 2026-09-18:

| Recurso | Estado/uso observado |
|---|---|
| `MAKINTOUCH` | AI Services + proyecto Foundry en Brazil South; tambien APIM |
| `makmak-5202-resource` | AI Services + proyecto en Brazil South; `gpt-oss-120b`, GlobalStandard, capacidad 50 |
| `makmak-7457-resource` | AI Services + proyecto en Central US; sin deployment confirmado |
| `makmak-5202-resource-appinsights` / `-logs` | recursos de observabilidad vivos |
| `makmak-7457-resource-appinsights` / `-logs` | recursos de observabilidad vivos |
| `makinspace` | `FileStorage`, `StandardV2_GRS`; no es Blob Storage normal |
| `maklinux` | `Microsoft.DesktopVirtualization/workspaces`; no confundirlo con VM de computo |
| `makmak-ml-workspace` | workspace Azure Machine Learning en `brazilsouth`, provisioning `Succeeded` |
| `makmak-cpu-cluster` | AmlCompute `Standard_DS2_v2`, 0 nodos actuales, min 0, max 1, scale-down `PT2M` |
| `makmakmlstorage` | StorageV2 `Standard_LRS`, dependencia del workspace ML |
| `makmak-ml-kv` | Key Vault `standard`, dependencia del workspace ML, acceso publico habilitado |
| `makmakmlregistry` | Azure Container Registry `Basic`, admin local deshabilitado |
| `makmak-ml-insights` | Application Insights `web`, dependencia del workspace ML |
| `makmak-search` | Azure AI Search `Free`, `brazilsouth`, running, 1 particion y 1 replica |

Nombres que aparecen en usage historico pero no en el inventario vivo actual: `mak-search-free`, `mak-postgres-free`, `mak-servicebus-free`, `mak-cloud-kv`, `mak-agente-libre`, `makloud` y `mak-language-free`. No deben usarse como si siguieran creados.

`docs/AZURE_MAK_TEMPORAL.md` conserva decisiones y rutas utiles, pero sus nombres de recursos deben reconciliarse antes de ejecutar comandos. Su afirmacion de que `makloud` y `mak-language-free` estan activos no supera al inventario vivo.

Estado local medido:

- Hub MAK: `127.0.0.1:8900`.
- Research y Codex: sockets Unix internos.
- SearXNG: `127.0.0.1:8888`, busqueda local sin credito externo.
- Ollama: `127.0.0.1:11434`, fallback local.
- Jobs: `/home/mak/research/jobs`.
- Registry: `/home/mak/research/jardines_interpretativos/jardines_interpretativos.sqlite`.
- Configuracion Research: `/home/mak/research/research.env`, modo privado.
- Contrato PostgreSQL: `/home/mak/flujo/src/flujo/knowledge/postgres_runtime.py`, por defecto socket Unix y database `mak_knowledge`.
- Azure ISSVKK para el agente y Continue: `/home/mak/.config/issvkk/azure-issvkk.env`; Continue usa ademas `/home/mak/.continue/.env`. Esta es una credencial de inferencia del recurso ISSVKK, no una credencial de administracion de Azure for Students.
- Azure ML: el workspace tiene los datastores predeterminados `workspaceworkingdirectory`, `workspaceartifactstore`, `workspaceblobstore` y `workspacefilestore`.
- Azure ML: no hay jobs, data assets, modelos, online endpoints ni batch endpoints observados en el corte.
- Azure ML: la extension CLI `az ml` no pudo ejecutarse por `No module named 'rpds.rpds'`; el estado se verifico mediante ARM REST y no se instalo nada.

## 3. Contrato de ejecucion del agente

El agente ejecutor corre en MAK. Windows/Luna solo dirige, revisa y recibe resultados; no debe ser necesario que Windows tenga Azure CLI, la clave ISSVKK ni una sesion de Azure para que el agente trabaje.

### Invocacion real desde MAK

La credencial ya disponible en MAK se carga sin imprimirla:

```bash
set -a
source /home/mak/.config/issvkk/azure-issvkk.env
set +a
```

Los deployments confirmados son:

- `DeepSeek-V4-Pro`
- `grok-4.6`

La ruta probada es `https://issvkk2-resource.services.ai.azure.com/openai/v1/chat/completions`. El agente puede usar un cliente OpenAI-compatible o `urllib`/`curl`, siempre con `model` igual al nombre exacto del deployment y `api-key` igual a `$AZURE_AI_API_KEY`. Para DeepSeek no se debe enviar `temperature` si el endpoint la rechaza.

Prueba minima no destructiva:

```bash
curl -sS --fail-with-body \
  'https://issvkk2-resource.services.ai.azure.com/openai/v1/chat/completions' \
  -H 'Content-Type: application/json' \
  -H "api-key: $AZURE_AI_API_KEY" \
  -d '{"model":"DeepSeek-V4-Pro","messages":[{"role":"user","content":"Responde solo OK"}],"max_tokens":4}'
```

Esta llamada se ejecuta en MAK. No se debe copiar la clave a Windows, al prompt, al repositorio ni a un archivo de salida.

### Continue/VS Code y agente autonomo no son lo mismo

- Continue/VS Code usa `/home/mak/.continue/.env` y `/home/mak/.continue/config.yaml` para el chat interactivo.
- Un agente autonomo de Research/MAK debe usar `/home/mak/.config/issvkk/azure-issvkk.env` o un adaptador que lo lea; no depende de que VS Code este abierto.
- El roster activo de `cultura/mak_research/research_lib.py` y `cultura/mak_plataforma/providers.py` aun contiene Groq, Gemini, Cerebras y Ollama, pero no Azure. Tener la clave cargada no significa que Research ya lo use.
- Para incorporarlo al runtime hay que añadir un proveedor Azure opt-in, registrar `provider`, `model`, `prompt_hash`, `usage`, `status` y error, y respetar `cuotas.py`/el conductor antes de habilitar fallback automatico.

### Frontera de trabajo

El agente puede leer archivos, consultar fuentes, llamar al deployment y dejar resultados en los jobs locales. No puede decidir por si solo cambiar RBAC, crear recursos, modificar facturacion, hacer push, desplegar, migrar `data/rd.db` ni convertir una respuesta del modelo en dato canonico.

## 4. Principio de integracion

Cada servicio necesita cinco piezas antes de considerarse listo:

1. Entrada: que archivo, evento o consulta recibe.
2. Adaptador: que script existente lo llama.
3. Salida: ruta local y/o recurso remoto donde deja el resultado.
4. Consumidor: que Hub, job, panel o pipeline lo usa.
5. Guardas: limite, procedencia, rollback y criterio de no uso.

La ruta normal es:

`entrada local -> adaptador Azure opcional -> resultado derivado local -> consumidor MAK -> revision o publicacion explicita`

Nunca debe ser:

`entrada local -> Azure -> escritura silenciosa de RD, portafolio, identidad o verdad curatorial`.

## 5. Plan especifico por servicio

### A. Azure AI Search — memoria consultable de Research

**Estado vivo e integrado:** `makmak-search` existe en `brazilsouth`, SKU `Free`, estado `running`, 1 particion y 1 replica. Se verificaron los tres indices existentes (`mak-inbox-v1`, `mak-rd-v1`, `mak-tools-v1`) sin imprimir claves. El consumidor canonico es el Hub MAK: `/api/azure/search/tools`; `tools/consultar_mak_search.py` quedo como wrapper diagnostico del mismo adaptador.

**Ejecucion:**

1. Medir el corpus real y seleccionar solo Markdown final, transcripciones autorizadas, capturas verificadas, contratos y dossiers.
2. Excluir claves, `.env`, Trash, caches, vendor trees, conversaciones privadas completas y la SQLite RD completa.
3. Cada documento debe incluir `source_ref`, hash, fecha, dominio y estado de evidencia.
4. Usar el servicio Free existente para un unico indice solo si filesystem + SearXNG no bastan; no crear otro Search.
5. Sincronizar incrementalmente por hash; un documento sin cambios no se reenvia.

**Se reutiliza:** `flujo/tools/research_job_router.py`, `tools/execute_research_job.py`, `cultura/mak_research/source_pipeline.py`, `flujo/src/flujo/web/hub.py`, `SourceCorpusStore` y los endpoints `/api/research/jobs` / `/api/research/operations-context`.

**Conectado:** retriever read-only sobre el indice compartido `mak-tools-v1`, con filtros por `area` y `departamento`, autenticacion AAD desde la sesion `az login`, y contrato estable `mak-azure-search-tools-v1`. No se creo otro indice ni se modifica RD.

**Resultado:** la recuperacion devuelve fragmento + fuente + hash + fecha; el job registra la consulta en `job_sources`/`audit_events`; el contexto queda en `/home/mak/research/jobs/<job_id>/`. Nunca modifica `data/rd.db`.

**Limite:** Free: 50 MB, 10.000 documentos y 3 indices. Usar un indice y una cuota de corpus definida.

**Aceptacion verificada:** consulta real desde el Hub devolvio documentos de `mak-tools-v1`; el CLI devolvio el mismo resultado; tests de contrato y degradacion pasaron. La indexacion/remocion no se activa desde MAK porque el objetivo actual es consulta gratuita y read-only.

### B. Storage — respaldos y archivos pesados

**Estado:** `backup.sh` ya produce `/home/mak/backups/mak-YYYYMMDD.tar.gz` y conserva 7 dias. La ruta cloud espera `makloud` + Blob, pero el recurso vivo es `makinspace` FileStorage. Hay una discrepancia que bloquea la subida automatica.

**Ejecucion:**

1. Confirmar si `makinspace` tiene File Shares utilizables; no asumir que sirve el comando Blob.
2. No cambiar `backup.sh` hasta confirmar cuenta, tipo de almacenamiento y rol de datos.
3. Subir solo el archivo empaquetado por el backup: no claves, `.env`, sesiones privadas ni `data/rd.db` completa.
4. Escribir un receipt local con hash, tamaño, fecha, cuenta y destino.
5. Probar restauracion a un directorio temporal antes de llamarlo respaldo.
6. Aplicar retencion remota corta; la copia local sigue siendo la primera autoridad.

**Resultado:** local `/home/mak/backups/`; remoto privado solo si el tier y acceso son compatibles. Consumidor: recuperacion manual de MAK, no lectura normal del Hub.

**Guardas:** Storage no es base de datos; no publicar objetos; no dejar una subida diaria a un recurso cuyo SKU no este confirmado.

### C. Azure Language — candidatos para Curatoria/RD

**Estado:** el adaptador ya existe en `cultura/mak_curatoria/triangular.py` como `_azure_language_ner`, con variables `AZURE_LANGUAGE_ENDPOINT`, `AZURE_LANGUAGE_KEY`, `AZURE_LANGUAGE_API_VERSION` y `AZURE_LANGUAGE_TIMEOUT`. No hay recurso Language vivo ni clave activa confirmados.

**Ejecucion:** texto OCR de flyers/fichas -> candidatos deterministas locales -> entidades Azure opcionales -> salida de triangulacion. El adaptador corta a 5.000 caracteres, conserva errores como estado y no escribe `data/rd.db`.

**Resultado:** candidatos en la salida de `triangular.py` e informes; nunca promocion automatica de productora, artista, venue o evento.

**Falta:** reconciliar un recurso vivo, configurar clave solo en proceso/archivo privado, ejecutar `tests/test_curatoria_triangular.py` y medir falsos candidatos. Queda opt-in, no fallback automatico.

**Valor:** alto para nombres de flyer; no sirve para OSC, Art-Net ni timecode.

### D. Document Intelligence — flyers, riders y PDFs

**Estado:** no hay recurso vivo confirmado ni adaptador especifico.

**Ejecucion:**

1. Seleccionar un PDF/imagen por orden de Research, nunca una carpeta completa.
2. Conservar el original local y su hash.
3. Enviar solo la copia seleccionada para extraer texto, tablas y estructura.
4. Guardar respuesta cruda, texto por pagina, campos, hash y estado de licencia.
5. Entregar candidatos a `triangular.py` o `SourceCorpusStore`; no escribir entidades canonicas.

**Resultado propuesto:** `/home/mak/research/source_corpus/<source_hash>/document_intelligence.json`, texto por pagina y `job_sources.text_path`. El job sigue en `jardines_interpretativos.sqlite`.

**Cuota:** pilotar 10-20 documentos con F0/free. Si la extraccion local ya es fiable, no llamar Azure.

### E. Vision — RD y percepcion visual

**Estado:** el pipeline activo es local: `tools/run_vision_feedback.py`, `vision_feedback_memory.py` y `cultura/mak_plataforma/mineria_rd.py` usan Ollama/OCR. No hay Vision cloud vivo confirmado.

**Ejecucion:**

1. `mineria_rd.py` corre primero y produce `mineria_candidatos.jsonl`.
2. Azure Vision recibe solo imagenes seleccionadas cuando la pasada local es insuficiente.
3. Su respuesta queda en un sidecar separado, con motor, fecha y hash.
4. Comparar por campo; no reemplazar fichas completas.
5. Si se fusiona, conservar por campo si vino de Ollama o Azure.

**Resultado propuesto:** `mineria_azure_vision.jsonl` + memoria de feedback visual; los originales y `data/rd.db` quedan intactos hasta la revision ya existente.

**Guardas:** color/forma/similitud no son identidad ni autoria; Azure es segunda medicion, no verdad.

### F. Speech — archivo FOH, no control en vivo

**Estado:** no hay Speech vivo confirmado. FOH ya se basa en OSC, Art-Net, sACN, timecode, Resolume y Chataigne.

**Ejecucion:** audio grabado seleccionado -> Speech-to-Text -> segmentos/timestamps -> recap FOH. Se asocia a `event_ref` y `session_id`, pero no entra al loop de control.

**Resultado propuesto:** `/home/mak/XIO/xio_evidence/<event_ref>/speech/` con `transcript.json`, `transcript.txt` y receipt. Consumidores: informe FOH, timeline y busqueda futura.

**Limite:** usar el free tier solo con material elegido. Para timestamp tecnico sigue mandando OSC/timecode.

### G. PostgreSQL — ledger operativo, no RD

**Estado:** no hay PostgreSQL cloud vivo confirmado. Si existe un registro historico, no se reactiva por nombre. El contrato local y la migracion segura ya existen.

**Ejecucion futura:** medir transporte, generar plan con `postgres_migration.py`, migrar solo jobs/leases/provenance/audit con consumidor, validar hashes y recuentos, mantener SQLite/RD como autoridad.

**Resultado:** PostgreSQL remoto seria un ledger operativo; el plan y receipt quedan locales. No cargar masivamente `data/rd.db`.

**Decision anual:** no provisionar mientras `mak_knowledge` por socket Unix cumpla.

### H. Service Bus — cola remota solo con concurrencia real

**Estado:** no hay Service Bus vivo confirmado. MAK ya tiene conductor, leases, colas internas y sockets.

**Ejecucion futura:** mensaje pequeno con `job_id`, `task_type`, `source_refs`, `idempotency_key` y deadline; el worker escribe el resultado en la SQLite/jobs local y devuelve receipt. Nunca incluir corpus ni secretos.

**Decision anual:** no crear Service Bus para un chat o un agente unico; su costo y complejidad superan a la cola local.

### I. Application Insights / Azure Monitor — medir sin subir contenido

**Estado integrado:** hay recursos App Insights y Log Analytics vivos para `makmak-5202`, `makmak-7457` y el workspace ML. `cultura/mak_plataforma/azure_services.py` envia eventos tecnicos mediante ingestion REST cuando se solicita el status o se usa el endpoint Foundry.

**Ejecucion:** enviar solo `health`, `latency_ms`, `provider`, `model`, `status`, `error_class`, conteos de tokens y hash de `job_id`.

**Se reutiliza:** `mak_heartbeat.py`, `_record_activity` de `research_lib.py`, `/api/status`, `cuotas.py` y `salud_proveedores.json`.

**Verificacion:** `/api/azure/status?emit=1` envio un evento real a `makmak-ml-insights`. Si falla, el Hub local sigue funcionando y el error queda nombrado; no se suben prompts, corpus, fotos, audio, transcripts, PII ni claves.

**No enviar:** prompts, documentos, fotos, audio, transcripts, PII ni claves.

### J. APIM MAKINTOUCH — no usar todavia como gateway

**Estado:** existe una API wildcard para `makmak-7457-resource`, `subscriptionRequired=true`, sin `serviceUrl` y con operaciones `/*`. Eso no prueba que enrute a un modelo o servicio.

**Decision:** mantener sin cambios. No conectar XIO, no publicar el gateway vacio y no sumar tokens/capas a la red hotspot. Solo serviria despues para una API read-only concreta con backend, rate limit, logging sin contenido y rollback.

### K. Azure Machine Learning — estado vivo y uso recomendado

**Estado al 2026-09-18:** el workspace `makmak-ml-workspace` ya existe en `brazilsouth` y esta `Succeeded`. Tiene `makmak-cpu-cluster` como AmlCompute `Standard_DS2_v2`, con 0 nodos actuales, minimo 0, maximo 1 e idle scale-down de 2 minutos. No se observaron jobs, data assets, modelos, online endpoints ni batch endpoints.

Dependencias vivas: `makmakmlstorage` (`StorageV2`, `Standard_LRS`), `makmak-ml-kv` (`Key Vault standard`), `makmakmlregistry` (`ACR Basic`, admin local deshabilitado) y `makmak-ml-insights` (Application Insights). El workspace expone cuatro datastores predeterminados: `workspaceworkingdirectory`, `workspaceartifactstore`, `workspaceblobstore` y `workspacefilestore`.

**Uso que si sirve para MAK:**

- `Data assets`: versionar datasets sanitizados de RD, FOH o vision sin subir `data/rd.db` completa.
- `Jobs` y `Pipelines`: ejecutar limpieza, entrenamiento, evaluacion y comparacion reproducibles.
- `Model registry`: guardar versiones, hashes y metricas de modelos propios.
- `Batch endpoints`: procesar lotes historicos de imagenes, texto o audio y liberar compute al terminar.
- `Responsible AI`: revisar errores, interpretabilidad y cohortes cuando exista un modelo tabular propio; no es un auditor universal de DeepSeek ni de RD.
- `Application Insights`: medir jobs, fallos y latencia sin enviar prompts, fotos, audio ni PII.

**No usar por ahora:** online endpoints permanentes, compute instance siempre encendida, GPU, AKS o feature store. Para el credito anual conviene serverless o el cluster actual con `min_nodes=0`; el workspace ML no es el costo principal, pero Storage, Key Vault, ACR, Monitor y compute si consumen credito.

**Ruta de datos propuesta:** staging local sanitizado en `/home/mak/research/azure-ml/staging/<run_id>/`; resultado remoto en job/data asset/model; receipt local en `/home/mak/research/azure-ml/runs/<run_id>/receipt.json`. Nunca escribir automaticamente `data/rd.db`.

**Estado integrado para el alcance actual:** `tools/reportar_calibracion_deepseek.py` registro una corrida real en MLflow del workspace (`10` aciertos, `4` fallos, `accuracy=0.714`). `tools/azure_ml_learning_dataset.py` exporto 28 evaluaciones sanitizadas, genero receipt/hash local y registro en MLflow una corrida `FINISHED` con `dataset_rows=28` y `dataset_fingerprints=26`; el artefacto remoto se verifica como `datasets/learning_evaluations.jsonl`. La incompatibilidad de firma entre `mlflow 3.16.1` y `azureml-mlflow 1.60.0` queda resuelta por `tools/azure_ml_mlflow_compat.py`, sin modificar `site-packages`. No se crean jobs, endpoints ni entrenamiento. La extension `az ml` sigue inutilizable por `No module named 'rpds.rpds'`, pero no bloquea el flujo de lineage, calibracion ni el inventario ARM read-only.

## 6. Calendario de un año

### Semanas 1-2: reconciliacion y freno de costos

- Status read-only que marque cada recurso como `live`, `historic` o `absent`.
- Reconciliar `backup.sh` contra `makinspace`.
- Mantener sin crear otro Search, PostgreSQL, Service Bus, VM, Key Vault o APIM nuevos.

### Meses 1-3: observabilidad y Language opt-in

- Instrumentar health/actividad tecnica en App Insights.
- Reconciliar Language y medir una muestra de OCR.
- Mantener SearXNG/Ollama como ruta por defecto.

### Meses 3-5: conectar el Search Free existente o decidir no usarlo

- Medir corpus; si filesystem + SearXNG bastan, documentar no-creacion.
- Si no bastan, crear un unico indice en `makmak-search` e integrarlo a `job_sources`.

### Meses 5-7: Document Intelligence

- Piloto de 10-20 flyers/riders/PDFs, comparacion local/Azure y receipt por pagina.

### Meses 7-9: Vision RD

- Lote pequeno, local primero, Azure como segunda medicion y fusion por campo con procedencia.

### Meses 9-10: Speech FOH

- Solo audio grabado; segmentos ligados a evento/sesion, nunca control OSC.

### Meses 10-12: decision de escala

- Solo si el volumen lo demuestra: PostgreSQL para ledger, Service Bus para concurrencia y APIM para una API concreta. Si no, conservar SQLite, sockets y SearXNG.

## 7. Control economico

- MAK: `spendingLimit=On`, 100 USD/12 meses.
- Prioridad: Free/F0, una instancia, una region y una funcion por servicio.
- No confundir recurso existente con recurso gratuito.
- Registrar servicio, funcion, job hash, unidades, estado y error.
- `cost=None` en usage significa facturacion pendiente, no costo cero.
- ISSVKK no entra al presupuesto MAK ni al fallback automatico; si el agente lo usa, sus llamadas se registran en un contador separado.
- No dejar corriendo VM, APIM, colas o almacenamiento que no tengan consumidor medido.

## 8. Criterio de cierre

Para cada servicio debe poder regenerarse una fila con recurso real, SKU, estado, credencial sin exponerla, prueba, entrada, salida, ruta local, consumidor, limite, costo o desconocido y rollback.

El plan no se considera ejecutado por crear recursos. Se considera ejecutado cuando la matriz se puede reconstruir desde comandos y archivos reales, y cada resultado puede volver a su fuente sin duplicar ninguna autoridad.

En MAK la matriz viva se reconstruye desde `/api/azure/status`. Cada fila separa
`resource_state` de `integration_state`: Search, MLflow y Application Insights
son `operational`; Foundry es `operational_guarded`; Storage, Key Vault y ACR
son `metadata_only`/`dependency_only`; APIM es `not_operational` porque su API
no tiene backend. Los modelos estudiantiles permanecen bloqueados por defecto
mediante `MAK_AZURE_ALLOW_CREDIT`.

## Fuentes locales consultadas

- `/home/mak/REPOS.md`
- `/home/mak/context/MD_CONTEXT_MASTER.md`
- `/home/mak/context/OWNER_MANIFEST.md`
- `/home/mak/CAPACIDADES_MAK.md`
- `/home/mak/MAPA.md`
- `/home/mak/docs/AZURE_MAK_TEMPORAL.md`
- `/home/mak/cultura/mak_research/research_lib.py`
- `/home/mak/cultura/mak_plataforma/providers.py`
- `/home/mak/cultura/mak_plataforma/cuotas.py`
- `/home/mak/cultura/mak_plataforma/backup.sh`
- `/home/mak/cultura/mak_curatoria/triangular.py`
- `/home/mak/tools/execute_research_job.py`
- `/home/mak/tools/research_source_capture.py`
- `/home/mak/flujo/src/flujo/knowledge/postgres_runtime.py`
- `/home/mak/flujo/src/flujo/knowledge/postgres_migration.py`

## Fuentes web oficiales consultadas el 2026-09-18

- Azure Machine Learning pricing: https://azure.microsoft.com/en-us/pricing/details/machine-learning/
- Azure ML workspace dependencies: https://learn.microsoft.com/en-us/azure/machine-learning/how-to-manage-rest
- Azure ML serverless compute: https://learn.microsoft.com/en-us/azure/machine-learning/how-to-use-serverless-compute
- Azure ML batch endpoints: https://learn.microsoft.com/en-us/azure/machine-learning/concept-endpoints-batch
- Azure ML quotas: https://learn.microsoft.com/en-us/azure/machine-learning/how-to-manage-quotas
- Azure ML data assets: https://learn.microsoft.com/en-us/azure/machine-learning/how-to-create-data-assets
