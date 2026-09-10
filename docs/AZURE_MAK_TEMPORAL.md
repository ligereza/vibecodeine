# Azure como apoyo temporal de MAK

Estado: apoyo remoto habilitado, no sustituto de la autoridad local.

Verificado el 2026-09-10: `mak-language-free` respondió una extracción NER
real y `mak-backups` quedó privado con el respaldo
`mak-20260814.tar.gz` (43.844.558 bytes). La cuenta de trabajo necesitó el rol
`Storage Blob Data Contributor` limitado al recurso `makloud`; sin ese rol
`--auth-mode login` puede ver la cuenta pero no operar sus blobs.

## Roles permitidos

- `mak-language-free` (`TextAnalytics`, F0): enriquecimiento opcional de OCR
  en `cultura/mak_curatoria/triangular.py`. Sus entidades sólo agregan
  candidatos; nunca confirman una productora, un artista ni una obra.
- `makloud` (`StorageV2`): copia privada de los respaldos que produce
  `cultura/mak_plataforma/backup.sh`. El contenedor se llama `mak-backups`.
- `mak-postgres-free` y `mak-cosmos-free`: reservas de infraestructura para
  apoyo remoto futuro; no son autoridad paralela ni deben recibir una copia
  masiva del archivo sin un consumidor y contrato propios.
- `mak-agente-libre`: VM temporal de apoyo. No se considera runtime de MAK ni
  failover automático; su estado y arquitectura ARM64 deben verificarse antes
  de instalar cargas de trabajo.

## Activar cada función

NER usa variables de proceso, nunca archivos del repositorio:

```bash
export AZURE_LANGUAGE_ENDPOINT="https://...cognitiveservices.azure.com"
export AZURE_LANGUAGE_KEY="..."
```

El respaldo remoto es deliberado y usa la sesión de Azure CLI:

```bash
MAK_AZURE_BACKUP_UPLOAD=1 /home/mak/cultura/mak_plataforma/backup.sh
```

Se puede cambiar la cuenta o el contenedor con `MAK_AZURE_STORAGE_ACCOUNT` y
`MAK_AZURE_STORAGE_CONTAINER`. La ruta usa `--auth-mode login`, no acepta keys
de Storage y mantiene el Blob privado.

## Límite operativo

Cuando MAK está apagado, Azure conserva el respaldo y puede ejecutar tareas
remotas acotadas; la interfaz local no aparece mágicamente en Azure. Para
ofrecer una ruta remota de lectura o recuperación hay que desplegar un
consumidor concreto, con su contrato, costo, procedencia y rollback. No se
declara failover automático mientras eso no exista.
