# Ruta de convocatorias para MAK

Estado: candidatos sin verificar; no son oportunidades vigentes.

La fuente de esta tanda es el archivo `convocatorias.jsonl` del zip
`convocatorias-mak.zip`, recibido el 8 de agosto de 2026. Se conserva como
entrada de busqueda, no como calendario ni como verdad publicada.

## Regla de integracion

MAK usa el perfil existente `opportunity_radar` y el contrato
`faro-opportunity-card-v1`. Cada candidato conserva:

- titulo y URL original;
- fuente declarada, sin llamarla oficial automaticamente;
- fecha de cierre en bruto, hasta que una fuente primaria la confirme;
- elegibilidad declarada, separada de la elegibilidad verificada;
- areas, monto y fecha de captura;
- estado `unverified` y siguiente accion humana de verificacion.

No se instala el monitor, el dashboard ni otro sistema de convocatorias del
zip. Sus semillas entran a la cola existente para evitar duplicar ledger,
router o notificador.

## Criterio de promocion

Un candidato solo puede pasar a una tarjeta de oportunidad revisable cuando
MAK confirme en la fuente primaria: bases o convocatoria oficial, fecha
exacta, elegibilidad aplicable y siguiente accion. Los cierres vagos, enlaces
rotos, montos no confirmados y convocatorias vencidas permanecen como
`unverified` o se archivan; nunca se convierten en una postulacion automatica.

El borrador `grados_de_desacuerdo.md` puede usar esta cola para explorar
compatibilidad, pero la propuesta artistica y la convocatoria permanecen
separadas.
