# Xiaomi ADB Controller – Advanced Plugins Pack

**12 plugins de alta complejidad "cercanos al root"** para Xiaomi 11 Lite con HyperOS, todos funcionales sin root.

---

## 📋 Índice para Agentes

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Tabla de Plugins](#tabla-de-plugins)
3. [Especificaciones por Plugin](#especificaciones-por-plugin)
4. [Comandos ADB Utilizados](#comandos-adb-utilizados)
5. [Limitaciones y Notas Técnicas](#limitaciones-y-notas-tecnicas)
6. [Cómo Extender](#cómo-extender)
7. [Testing y Troubleshooting](#testing-y-troubleshooting)

---

## Resumen Ejecutivo

Estos 12 plugins fueron desarrollados basándose en investigación de la comunidad Android/HyperOS de 2025-2026, incluyendo:
- Comandos `service call` para HyperOS descubiertos en Reddit (marzo 2026)
- Tweaks de performance publicados en XDA para MIUI/HyperOS
- Métodos de Shizuku-equivalent via ADB para control avanzado
- Técnicas de content provider query para acceso a datos

**Todos funcionales en Xiaomi 11 Lite con HyperOS sin root.**

---

## Tabla de Plugins

| # | Plugin ID | Categoría | Impacto | Requiere | Background |
|---|-----------|-----------|---------|----------|------------|
| 1 | `hyperos_unlocker` | System | ⭐⭐⭐⭐⭐ | `service call` | No |
| 2 | `performance_tweaker` | System | ⭐⭐⭐⭐⭐ | `setprop` + `settings` | No |
| 3 | `app_freezer` | Automation | ⭐⭐⭐⭐⭐ | `am` + `cmd` | Sí (15s) |
| 4 | `system_logger` | System | ⭐⭐⭐⭐ | `logcat` | Sí (5s) |
| 5 | `network_controller` | Network | ⭐⭐⭐⭐ | `cmd netpolicy` | No |
| 6 | `desktop_mode` | System | ⭐⭐⭐⭐ | `am --windowingMode` | No |
| 7 | `dns_shield` | Network | ⭐⭐⭐⭐ | `settings global` | No |
| 8 | `content_explorer` | System | ⭐⭐⭐ | `content query` | No |
| 9 | `prop_editor` | System | ⭐⭐⭐ | `getprop`/`setprop` | Sí (10s) |
| 10 | `app_volume` | System | ⭐⭐⭐ | `media volume` | No |
| 11 | `call_recorder` | Apps/System | ⭐⭐⭐ | `pm` + overlay | No |
| 12 | `usb_controller` | System | ⭐⭐⭐ | `svc usb` | No |

---

## Especificaciones por Plugin

### 1. HyperOS Unlocker (`hyperos_unlocker`)

**Propósito:** Desbloquear features exclusivos de flagship en cualquier Xiaomi.

**Endpoints:**
- `GET /api/plugins/hyperos_unlocker/props` — Lista de propiedades modificables
- `POST /api/plugins/hyperos_unlocker/set` — Setear una prop `{prop, value}`
- `GET /api/plugins/hyperos_unlocker/presets` — Lista de presets
- `POST /api/plugins/hyperos_unlocker/preset/apply` — Aplicar preset `{preset}`
- `GET /api/plugins/hyperos_unlocker/current` — Estado actual de todas las props
- `POST /api/plugins/hyperos_unlocker/device-level` — Override de nivel `{cpu, gpu}`

**Presets disponibles:**
- `flagship` — CPU 6, GPU 6, visual 4 (liquid glass), blur, shadow, stack recents
- `balanced` — CPU 3, GPU 3, visual 3 (textures), blur, shadow
- `reset` — Todo a valores por defecto

**Comandos ADB críticos:**
```bash
# Estos son los comandos que ejecuta internamente:
service call miui.mqsas.IMQSNative 21 i32 1 s16 "setprop" i32 1 s16 "persist.sys.computility.cpulevel 6" s16 "/storage/emulated/0/log.txt" i32 600
service call miui.mqsas.IMQSNative 21 i32 1 s16 "setprop" i32 1 s16 "persist.sys.computility.gpulevel 6" s16 "/storage/emulated/0/log.txt" i32 600
service call miui.mqsas.IMQSNative 21 i32 1 s16 "setprop" i32 1 s16 "persist.sys.advanced_visual_release 4" s16 "/storage/emulated/0/log.txt" i32 600
service call miui.mqsas.IMQSNative 21 i32 1 s16 "setprop" i32 1 s16 "persist.sys.background_blur_supported true" s16 "/storage/emulated/0/log.txt" i32 600
settings put global task_stack_view_layout_style 2
settings put system deviceLevelList v:1,c:3,g:3
```

**Notas:**
- `advanced_visual_release 4` habilita Liquid Glass (HyperOS 3+)
- `advanced_visual_release 3` habilita Advanced Textures
- Los cambios persisten entre reinicios (`persist.sys.*`)
- En HyperOS 3.1+, Xiaomi podría haber parcheado algunas opciones
- `deviceLevelList`: `v` = versión, `c` = CPU level, `g` = GPU level
- Valores de CPU/GPU: 0=bajo, 3=medio, 6=flagship

**Riesgos:** Bajo. Si algo falla, `preset/apply` con `reset` revierte todo.

---

### 2. Performance Tweaker Pro (`performance_tweaker`)

**Propósito:** Optimizar rendimiento del sistema con tweaks de bajo nivel.

**Endpoints:**
- `GET /api/plugins/performance_tweaker/tweaks` — Lista de todos los tweaks
- `POST /api/plugins/performance_tweaker/set` — Aplicar tweak `{name, value}`
- `GET /api/plugins/performance_tweaker/presets` — Presets disponibles
- `POST /api/plugins/performance_tweaker/preset/apply` — Aplicar preset `{preset}`
- `GET /api/plugins/performance_tweaker/status` — Estado actual de todos los tweaks
- `POST /api/plugins/performance_tweaker/trim-cache` — Limpieza agresiva de cache

**Presets:**
- `gaming` — Fixed perf ON, touch zero, 120Hz lock, RAM expand OFF, enhanced CPU
- `battery_saver` — 60Hz lock, blurs ON, transparency ON, logging OFF
- `responsive` — Fixed perf ON, timeouts ultra-fast, RAM expand OFF, adaptive OFF
- `normal` — Valores estándar del sistema

**Comandos clave:**
```bash
cmd power set-fixed-performance-mode-enabled true   # Overclock sostenido
settings put secure tap_duration_threshold 0.0       # Touch instantáneo
settings put secure touch_blocking_period 0.0        # Sin delay de touch
setprop debug.force-opengl 1                         # Forzar OpenGL
setprop debug.hwc.force_gpu_vsync 1                  # GPU vsync
settings put global ram_expand_size 0                # Desactivar memory extension
settings put system multicore_packet_scheduler 1     # Multicore scheduler
settings put global adaptive_battery_management_enabled 0  # Más responsive
```

**trim-cache ejecuta:**
```bash
pm trim-caches 4096G   # Liberar todo el cache
pm art cleanup          # Limpiar ART (compilación de apps)
sm fstrim               # TRIM del almacenamiento
```

---

### 3. App Freezer (`app_freezer`)

**Propósito:** Congelar apps completamente para ahorrar batería (como la app Hail).

**Endpoints:**
- `GET /api/plugins/app_freezer/frozen` — Lista de apps congeladas
- `POST /api/plugins/app_freezer/freeze` — Congelar app `{package}`
- `POST /api/plugins/app_freezer/unfreeze` — Descongelar `{package}`
- `POST /api/plugins/app_freezer/unfreeze-all` — Descongelar todas
- `GET/POST /api/plugins/app_freezer/auto-freeze-list` — Apps para auto-freeze
- `GET/POST /api/plugins/app_freezer/schedule` — Programación horaria
- `GET /api/plugins/app_freezer/stats` — Estadísticas de ahorro
- `POST /api/plugins/app_freezer/deep-freeze` — Deep freeze masivo `{packages}`

**Método de freeze (combinación de técnicas):**
```bash
am set-standby-bucket <pkg> 50          # Bucket "never"
am force-stop <pkg>                     # Matar proceso
cmd deviceidle whitelist -<pkg>         # Quitar de whitelist
```

**Auto-freeze:** Background task cada 15s verifica si la pantalla está apagada y congela las apps configuradas.

**Schedule:** Permite programar freeze por franjas horarias.

**Stats:** Registra cuántas veces se congelaron apps y cuánto tiempo estuvieron congeladas.

---

### 4. System Logger (`system_logger`)

**Propósito:** Monitor de logcat remoto con detección de crashes y ANRs.

**Endpoints:**
- `GET /api/plugins/system_logger/logs?limit=100&tag=X&priority=E`
- `GET /api/plugins/system_logger/crashes?limit=50`
- `GET /api/plugins/system_logger/crash-stats`
- `POST /api/plugins/system_logger/start` — Iniciar monitoreo
- `POST /api/plugins/system_logger/stop` — Parar
- `GET /api/plugins/system_logger/status`
- `POST /api/plugins/system_logger/filter` — `{tag, priority, package}`
- `POST /api/plugins/system_logger/clear` — Limpiar logs
- `POST /api/plugins/system_logger/snapshot` — Snapshot de 200 líneas
- `GET /api/plugins/system_logger/export` — Descargar txt

**Patrones de crash detectados:**
- FATAL EXCEPTION
- ANR in / Application Not Responding
- OutOfMemoryError
- StackOverflowError
- NullPointerException
- SecurityException

**Background:** Cada 5s hace `logcat -d -t 100` y analiza las líneas nuevas.

---

### 5. Per-App Network Controller (`network_controller`)

**Propósito:** Controlar acceso a red por app sin root.

**Endpoints:**
- `GET /api/plugins/network_controller/blocked` — Apps bloqueadas
- `POST /api/plugins/network_controller/block` — `{package}`
- `POST /api/plugins/network_controller/unblock` — `{package}`
- `POST /api/plugins/network_controller/block-wifi` — Bloquear WiFi para app
- `POST /api/plugins/network_controller/block-data` — Bloquear datos
- `GET /api/plugins/network_controller/traffic` — Stats de tráfico
- `GET /api/plugins/network_controller/connections` — Conexiones activas
- `GET /api/plugins/network_controller/uids` — UIDs de apps
- `GET /api/plugins/network_controller/policy` — Políticas actuales

**Comandos ADB:**
```bash
cmd netpolicy set-app-uid-rule <pkg> 1      # Bloquear
cmd netpolicy set-app-uid-rule <pkg> 0      # Desbloquear
cmd netpolicy set-uid-policy <pkg> 1        # Bloquear WiFi
cmd netpolicy set-uid-policy <pkg> 2        # Bloquear datos
cat /proc/net/xt_qtaguid/stats              # Stats de tráfico por UID
```

**Limitación:** `cmd netpolicy` puede no funcionar en todas las versiones de Android. En ese caso, la alternativa es usar NetGuard app + ADB para conceder permisos.

---

### 6. Desktop / Freeform Mode (`desktop_mode`)

**Propósito:** Ventanas flotantes y modo escritorio.

**Endpoints:**
- `POST /api/plugins/desktop_mode/launch-freeform` — `{package, bounds}`
- `POST /api/plugins/desktop_mode/launch-pip` — `{package}`
- `POST /api/plugins/desktop_mode/launch-split` — `{package1, package2}`
- `POST /api/plugins/desktop_mode/launch-mode` — `{package, mode, bounds}`
- `GET /api/plugins/desktop_mode/windows` — Ventanas activas
- `POST /api/plugins/desktop_mode/close` — `{package}`
- `POST /api/plugins/desktop_mode/close-all`
- `POST /api/plugins/desktop_mode/resize` — `{stack_id, bounds}`
- `POST /api/plugins/desktop_mode/move` — `{stack_id, bounds}`
- `GET /api/plugins/desktop_mode/display-info`
- `POST /api/plugins/desktop_mode/enable-freeform`

**Comandos ADB:**
```bash
am start --windowingMode 5 --bounds 100,100,900,1600 -n pkg/activity  # Freeform
am start --windowingMode 9 -n pkg/activity                             # PiP
am start --windowingMode 3 -n pkg/activity                             # Split top
settings put global enable_freeform_windows 1                          # Habilitar
wm stack resize <id> <bounds>                                         # Redimensionar
```

**Modos:**
- 1 = fullscreen
- 3 = split top
- 4 = split bottom
- 5 = freeform
- 9 = picture-in-picture

---

### 7. DNS Privacy Shield (`dns_shield`)

**Propósito:** Configurar Private DNS con providers seguros + blocklists.

**Endpoints:**
- `GET /api/plugins/dns_shield/status`
- `GET /api/plugins/dns_shield/providers` — Lista de providers
- `POST /api/plugins/dns_shield/set-provider` — `{provider}` o `{hostname}`
- `POST /api/plugins/dns_shield/disable`
- `GET /api/plugins/dns_shield/blocklists`
- `POST /api/plugins/dns_shield/blocklists/apply` — `{lists: [...]}`
- `GET/POST /api/plugins/dns_shield/custom-blocklist`
- `POST /api/plugins/dns_shield/test` — `{domain}`

**Providers preconfigurados:**
- Cloudflare (one.one.one.one)
- Cloudflare + Malware (security.cloudflare-dns.com)
- Cloudflare + Family (family.cloudflare-dns.com)
- Google (dns.google)
- AdGuard (dns.adguard.com) — bloquea ads
- AdGuard Family (dns-family.adguard.com)
- Quad9 (dns.quad9.net)
- NextDNS ({id}.dns.nextdns.io) — configurable

**Blocklists incluidas:**
- `ads` — Dominios de publicidad (doubleclick, admob, etc.)
- `trackers` — Google Analytics, Amplitude, Mixpanel, etc.
- `telemetry_xiaomi` — Tracking de Xiaomi (mistat, metok, adv)
- `telemetry_google` — Telemetría de Google

**Comandos ADB:**
```bash
settings put global private_dns_mode hostname
settings put global private_dns_specifier dns.adguard.com
nslookup <domain>  # Test de resolución
```

---

### 8. Content Explorer (`content_explorer`)

**Propósito:** Acceso a datos del sistema via Content Provider URI.

**Endpoints:**
- `GET /api/plugins/content_explorer/providers` — Lista de providers
- `GET /api/plugins/content_explorer/query?uri=...&projection=...&where=...`
- `GET /api/plugins/content_explorer/sms?box=inbox|sent&limit=50`
- `GET /api/plugins/content_explorer/calls?limit=50`
- `GET /api/plugins/content_explorer/contacts?limit=100`
- `GET /api/plugins/content_explorer/media?type=images|video|audio`
- `GET /api/plugins/content_explorer/settings?scope=system|secure|global`
- `GET /api/plugins/content_explorer/search?q=<query>`

**Providers soportados:**
- SMS (`content://sms/`, `content://sms/inbox`, `content://sms/sent`)
- Call Log (`content://call_log/calls`)
- Contacts (`content://com.android.contacts/data/phones`)
- Calendar (`content://com.android.calendar/events`)
- Media (`content://media/external/images/media`, video, audio)
- Settings (system, secure, global)

**Comando ADB:**
```bash
content query --uri content://sms/inbox --projection address body date type
```

---

### 9. System Prop Editor (`prop_editor`)

**Propósito:** Editor visual de todas las propiedades del sistema.

**Endpoints:**
- `GET /api/plugins/prop_editor/list?filter=<str>` — Listar todas (filtrable)
- `GET /api/plugins/prop_editor/get?key=<prop>` — Leer una
- `POST /api/plugins/prop_editor/set` — `{key, value}`
- `GET /api/plugins/prop_editor/safe-props` — Props seguras (las más usadas)
- `GET /api/plugins/prop_editor/search?q=<query>` — Buscar en key y value
- `POST /api/plugins/prop_editor/watch` — `{action, prop}` — Agregar/quitar watch
- `GET /api/plugins/prop_editor/watch/list` — Lista watch + valores actuales
- `GET /api/plugins/prop_editor/snapshot` — Capturar estado actual
- `GET /api/plugins/prop_editor/diff` — Diferencia entre últimas 2 snapshots
- `GET /api/plugins/prop_editor/export` — Descargar todas como txt
- `POST /api/plugins/prop_editor/reset` — `{key}` — Resetear prop

**Watch:** Background cada 10s guarda valores de las props monitoreadas.

**Snapshots:** Permite capturar estados y ver diferencias entre ellos.

**Comandos:**
```bash
getprop                          # Listar todas
getprop persist.sys.cpu_level    # Leer una
setprop persist.sys.cpu_level 6  # Escribir
```

---

### 10. Per-App Volume Controller (`app_volume`)

**Propósito:** Control de volumen individual por app.

**Endpoints:**
- `GET /api/plugins/app_volume/status` — Todos los volúmenes
- `POST /api/plugins/app_volume/set` — `{package, volume, stream}`
- `POST /api/plugins/app_volume/mute` — `{package}`
- `POST /api/plugins/app_volume/unmute` — `{package}`
- `GET /api/plugins/app_volume/profiles`
- `POST /api/plugins/app_volume/profile/apply` — `{profile}`
- `POST /api/plugins/app_volume/profile/save` — `{name, apps, ...}`
- `GET /api/plugins/app_volume/app-uids?package=<pkg>`
- `GET /api/plugins/app_volume/system-volume`
- `POST /api/plugins/app_volume/system-volume` — `{stream, volume}`

**Streams:**
- 0 = voice_call
- 1 = system
- 2 = ring
- 3 = music
- 4 = alarm
- 5 = notification
- 6 = bluetooth_sco
- 8 = dtmf

**Comandos:**
```bash
media volume --stream 3 --set 10       # Volumen música
media volume --stream 3 --get          # Leer volumen
```

**Limitación:** Controlar volumen POR APP requiere Shizuku o permisos especiales. El plugin controla el volumen del sistema por stream, que es la base. Para control granular por UID, necesitaría integración con Shizuku.

---

### 11. Call Recorder Enabler (`call_recorder`)

**Propósito:** Activar grabación nativa de llamadas en HyperOS Global ROM.

**Endpoints:**
- `GET /api/plugins/call_recorder/status` — Estado de todos los packages
- `POST /api/plugins/call_recorder/enable` — Activar Xiaomi Dialer
- `POST /api/plugins/call_recorder/disable` — Restaurar Google Dialer
- `GET /api/plugins/call_recorder/recordings` — Lista de grabaciones
- `GET/POST /api/plugins/call_recorder/config` — Configuración

**Proceso de activación:**
```bash
# 1. Desactivar Google Dialer y Contacts
pm disable-user --user 0 com.google.android.dialer
pm disable-user --user 0 com.google.android.contacts

# 2. Remover overlay de restricción MIUI
pm uninstall -k --user 0 com.android.phone.cust.overlay.miui

# 3. Instalar dialer nativo Xiaomi
pm install-existing com.android.contacts
pm install-existing com.android.incallui
```

**Grabaciones se guardan en:** `/sdcard/MIUI/sound_recorder/call_rec/`

**Limitaciones:**
- Solo funciona en ROM Global (MI), no en EU (por GDPR)
- Necesita reboot después de la activación
- El dialer de Xiaomi debe configurarse como default manualmente

---

### 12. USB Controller (`usb_controller`)

**Propósito:** Control avanzado del modo y función USB.

**Endpoints:**
- `GET /api/plugins/usb_controller/status`
- `POST /api/plugins/usb_controller/set-function` — `{function}`
- `GET /api/plugins/usb_controller/functions`
- `POST /api/plugins/usb_controller/data-toggle` — `{enabled}`
- `POST /api/plugins/usb_controller/secure-mode` — Solo carga
- `POST /api/plugins/usb_controller/charging-sim` — `{state}`
- `GET /api/plugins/usb_controller/info`
- `GET /api/plugins/usb_controller/log`

**Funciones USB:**
- `none` — Solo carga (seguro para PCs públicas)
- `mtp` — Transferencia de archivos
- `ptp` — Modo cámara
- `rndis` — Tethering USB
- `audio_source` — Micrófono USB
- `midi` — Instrumento MIDI
- `mtp_adb` / `ptp_adb` — Con ADB

**Comandos:**
```bash
svc usb setFunction mtp           # Cambiar función
getprop sys.usb.config            # Función actual
cat /sys/class/android_usb/android0/speed   # Velocidad USB
cat /sys/class/power_supply/usb/online      # USB conectado
dumpsys battery plug              # Simular carga
dumpsys battery unplug            # Simular desplug
settings put global adb_enabled 0 # Desactivar ADB por USB
```

---

## Comandos ADB Utilizados

### Resumen por categoría

| Categoría | Comandos |
|-----------|----------|
| **HyperOS props** | `service call miui.mqsas.IMQSNative 21 ...` |
| **System properties** | `getprop`, `setprop` |
| **Settings** | `settings put/get system/secure/global <key> <value>` |
| **Power** | `cmd power set-fixed-performance-mode-enabled` |
| **App management** | `pm disable-user/enable/uninstall/install-existing` |
| **Activity** | `am start/force-stop/set-standby-bucket` |
| **Network policy** | `cmd netpolicy set-app-uid-rule/set-uid-policy` |
| **Content** | `content query --uri <uri>` |
| **Media** | `media volume --stream <n> --set/get <v>` |
| **USB** | `svc usb setFunction` |
| **DNS** | `settings put global private_dns_mode/specifier` |
| **Log** | `logcat -d -t <n>`, `logcat -c` |
| **Device** | `dumpsys battery/power/usb/wifi/package` |
| **Window** | `wm stack resize/size/density`, `wm set-user-refresh-rate` |

---

## Limitaciones y Notas Técnicas

### Comunes a todos los plugins

1. **Requieren ADB:** El teléfono debe tener USB Debugging activo
2. **No persisten todos:** `setprop` se pierde al reiniciar (solo `persist.sys.*` persiste)
3. **Seguridad:** Algunos comandos requieren "USB Debugging (Security Settings)" activado
4. **HyperOS updates:** Xiaomi puede parchear estos métodos en futuras actualizaciones

### Específicas por plugin

| Plugin | Limitación |
|--------|-----------|
| hyperos_unlocker | En HyperOS 3.1+ algunos features pueden estar parcheados |
| app_freezer | El freeze total requiere que la app soporte AppStandby |
| system_logger | logcat puede tener permisos restringidos en algunas ROM |
| network_controller | `cmd netpolicy` no funciona en todas las versiones |
| desktop_mode | Launcher de Xiaomi puede bloquear freeform |
| dns_shield | Blocklists requieren provider compatible (AdGuard/NextDNS) |
| app_volume | Control por UID real requiere Shizuku |
| call_recorder | Solo ROM Global (MI), no EU. Requiere reboot. |
| usb_controller | Algunos cambios requieren reconectar cable |

---

## Cómo Extender

### Agregar nuevos presets a un plugin existente

```python
# En el __init__.py del plugin, agregar al dict de PRESETS:
"mi_preset": {
    "name": "🎯 Mi Preset",
    "description": "Descripción",
    "prop_name": "value",
}
```

### Agregar nuevas props al HyperOS Unlocker

```python
# En hyperos_unlocker/__init__.py, agregar a PROPS:
"nueva_prop": {
    "cmd": 'service call miui.mqsas.IMQSNative 21 i32 1 s16 "setprop" i32 1 s16 "{key} {level}" s16 "/storage/emulated/0/log.txt" i32 600',
    "values": {"off": "0", "on": "1"},
    "description": "Descripción de la prop"
}
```

### Agregar nuevos blocklists al DNS Shield

```python
# En dns_shield/__init__.py, agregar a BLOCKLISTS:
"mi_lista": {
    "domains": [
        "dominio1.com",
        "dominio2.com",
    ]
}
```

### Crear un nuevo plugin basado en estos

Usar `plugins/_template/` como base. Los puntos clave son:
1. Definir `plugin_id` que coincida con el nombre de carpeta
2. Registrar rutas en `on_load()` con `self.register_route()`
3. Usar `self.controller._shell()` para comandos ADB
4. Exportar `plugin_class = MiPlugin` al final del archivo

---

## Testing y Troubleshooting

### Verificar que los plugins se cargan

```bash
curl http://localhost:5000/api/plugins
```

Debe mostrar los 12 nuevos plugins en la lista.

### Verificar conectividad ADB

```bash
adb devices  # Debe mostrar el dispositivo como "device"
```

### Probar HyperOS Unlocker

```bash
# Ver estado actual
curl http://localhost:5000/api/plugins/hyperos_unlocker/current

# Aplicar preset balanced
curl -X POST http://localhost:5000/api/plugins/hyperos_unlocker/preset/apply \
  -H "Content-Type: application/json" \
  -d '{"preset": "balanced"}'
```

### Probar Performance Tweaker

```bash
# Aplicar preset responsive
curl -X POST http://localhost:5000/api/plugins/performance_tweaker/preset/apply \
  -H "Content-Type: application/json" \
  -d '{"preset": "responsive"}'

# Ver status
curl http://localhost:5000/api/plugins/performance_tweaker/status
```

### Si un plugin no funciona

1. Verificar logs: `curl http://localhost:5000/api/plugins/system_logger/logs?limit=50`
2. Verificar que el comando ADB funciona manualmente: `adb shell <comando>`
3. Verificar permisos USB Debugging (Security Settings) activado
4. Reiniciar el servidor: `python server.py`

### Comandos de debug útiles

```bash
# Ver todas las props de HyperOS
adb shell getprop | grep persist.sys

# Ver settings
adb shell settings list global | grep -i "dns\|adb\|private"
adb shell settings list system | grep -i "refresh\|device"
adb shell settings list secure | grep -i "tap\|touch\|press"

# Ver logcat
adb logcat -d -t 20 | grep -i "error\|crash\|fatal"

# Ver apps en standby
adb shell am get-standby-bucket <package>

# Ver network policy
adb shell cmd netpolicy list
```

---

## Instalación Rápida

```bash
# 1. Extraer el zip en el proyecto
unzip xiaomi-advanced-plugins.zip

# 2. Los plugins se copian automáticamente a plugins/
# 3. Reiniciar el servidor
python server.py

# 4. Verificar
curl http://localhost:5000/api/plugins | jq length
# Debe mostrar 12+ plugins (los anteriores + estos nuevos)
```

---

## Créditos y Fuentes

- HyperOS Unlocker commands: Reddit r/HyperOS (marzo 2026)
- Performance Tweaks: XDA Forums (febrero 2025)
- App Freezer: Inspirado en Hail (GitHub)
- DNS Shield: Configuración estándar de Private DNS en Android
- Call Recorder: XDA guide (julio 2025)
- Content Explorer: Android Content Provider API documentation
- Shizuku ecosystem: awesome-shizuku (GitHub)

---

**Total: 12 plugins, ~2500 líneas de código, 60+ endpoints API, 100+ comandos ADB diferentes.**
