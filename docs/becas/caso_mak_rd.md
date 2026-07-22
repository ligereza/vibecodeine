# Anexo tecnico -- Plataforma de datos RD (caso MAK)

Anexo para postulaciones de Reduciendo Dano (RD). Describe el componente
tecnologico existente de la ONG en lenguaje para evaluadores de fondos.
Todo lo descrito aqui YA existe y es verificable en el repositorio de
trabajo de la ONG; nada es promesa futura salvo lo marcado "en curso".

ASCII-only. Redaccion: direccion del proyecto (F4b del plan liberacion).

---

## 1. Resumen para evaluadores

RD opera una plataforma propia de registro y reporte de datos de campo
(testeo presuntivo de sustancias, atenciones, encuestas) con tres
propiedades poco comunes en organizaciones de este tamanio:

1. **Privacidad por diseno, no por promesa.** La base de datos de campo
   no tiene columnas de identidad (nombre, RUT, telefono, email). Un
   dato personal no se puede guardar ni por error, porque no existe
   lugar donde guardarlo. Ademas, todo texto libre pasa por un filtro
   automatico que rechaza o sanitiza patrones de identidad (RUT,
   tarjetas) antes de tocar la base.
2. **Costo marginal cercano a cero.** Corre sobre hardware propio
   reutilizado y software libre. Sin licencias, sin suscripciones, sin
   servicios cloud pagados. El consumo electrico se mide con registro
   automatico y las tareas pesadas se ejecutan en horario valle
   (00-07h) por politica.
3. **Verificacion continua.** Todo cambio al software pasa por revision
   y pruebas automaticas (integracion continua) antes de entrar en
   produccion; la rama principal del codigo esta protegida y nadie
   (ni administradores) puede saltarse ese control.

## 2. Que registra y que reporta

- **Registros de testeo presuntivo:** fecha (sin hora exacta), evento,
  sustancia declarada, reactivo usado, resultado, familia detectada,
  coincidencia declarado-vs-detectado, adulterante presunto.
- **Atenciones:** tipo, derivacion, rango etario (nunca edad exacta).
- **Encuestas:** agregadas.
- **Salidas:** tendencias, tasa de adulteracion, informe trimestral
  agregado con disclaimer de caracter presuntivo obligatorio (el
  analisis colorimetrico no es confirmatorio de laboratorio y el
  sistema lo dice en cada reporte).

El patron de anonimizacion (pseudonimizacion, agregacion espacial y
temporal, fecha sin hora) coincide con el que usan los referentes
internacionales de testeo (DanceSafe, Energy Control, TEDI).

## 3. Arquitectura en una pagina

- **Servidor de datos (MAK):** equipo propio reutilizado, sistema Linux,
  operando como estacion de datos y procesamiento local de la ONG.
- **Base de datos de campo:** SQLite local (data separada del catalogo
  publico), fuera del control de versiones, respaldable.
- **Catalogo de reactivos y packs:** base consultable regenerable desde
  archivos de texto versionados (auditable linea por linea).
- **Procesamiento de archivo historico:** OCR y vision por computador
  locales (tesseract + modelo de vision abierto que corre en el propio
  equipo) para minar el archivo grafico de la ONG (~1700 archivos:
  flyers, planos, registros) sin subir nada a servicios externos.
- **Panel para directiva (en curso):** acceso remoto de solo lectura a
  reportes agregados, protegido por autenticacion por correo de la
  directiva, sobre tunel cifrado gratuito. Cero datos individuales
  expuestos.
- **Energia:** registro automatico de consumo (GPU y CPU) cada 5
  minutos con resumen diario en Wh; politica de tareas pesadas solo en
  horario valle. Este registro permite postular equipamiento eficiente
  con linea base medida, no estimada.

## 4. Por que esto importa para un fondo

- **El dinero no se va en software.** El desarrollo ya esta hecho y es
  software libre mantenido por la propia organizacion. Un fondo
  destinado a RD financia insumos, terreno o equipamiento -- no
  licencias ni consultoras.
- **Rendicion verificable.** Los indicadores de actividad salen de un
  sistema con historial auditable, no de planillas manuales
  reconstruidas a fin de proyecto.
- **Riesgo de datos minimizado de raiz.** Para un financista, el
  escenario "filtracion de datos de personas usuarias" es
  estructuralmente imposible en la base de campo: no hay datos de
  personas que filtrar.
- **Replicabilidad.** El patron (schema sin identidad + filtro de PII +
  reportes agregados) es documentable y transferible a otras
  organizaciones de reduccion de danos de la region.

## 5. Limites declarados (honestidad tecnica)

- El analisis con reactivos colorimetricos es PRESUNTIVO. La plataforma
  lo marca en cada salida; no sustituye confirmacion de laboratorio.
- El marco legal de actuacion (Ley 20.000, Ley 19.628) esta en proceso
  de validacion con asesoria profesional; el alcance operativo declarado
  en cada postulacion se ajusta a esa validacion.
- Los datos de campo mostrados en demos son ficticios (generados con
  semilla fija); los reportes reales solo existiran con operacion real
  en terreno.

## 6. Solicitudes tipicas que este anexo respalda

| Tipo de fondo | Que pedir | Como lo respalda la plataforma |
|---|---|---|
| Salud / prevencion (SENDA, fondos regionales) | Insumos de testeo, operacion en terreno | Registro agregado de cobertura y tendencias por evento |
| Equipamiento / energia | Hardware eficiente, respaldo electrico | Linea base de consumo medida (Wh/dia) |
| Tecnologia para ONGs (Google/GitHub for Nonprofits, Cloudflare Galileo) | Cuentas y servicios gratuitos para ONG | Plataforma existente que los aprovecha de inmediato |
| Fundaciones harm-reduction internacionales | Operacion + fortalecimiento de datos | Patron privacy-by-design alineado a referentes (DanceSafe/EC/TEDI) |

## 7. Contacto tecnico

- Responsable de plataforma: [COMPLETAR -- nombre o rol institucional]
- Repositorio y documentacion: disponibles para revision de evaluadores
  bajo acuerdo (el codigo es auditable; los datos de campo no se
  comparten por diseno).
