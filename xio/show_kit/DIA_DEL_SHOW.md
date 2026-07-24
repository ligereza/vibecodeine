# DÍA DEL SHOW — kit FOH (cero código, todo doble click)

Señales de HOY: **TC** (LTC por M-Audio → Chataigne → OSC) + **VISUAL** (Resolume OSC)
+ setlist + registro. Las luces son de la grandMA3 del venue con red propia: **NO se toca**.
El tile **LUCES quedará N/D (gris) toda la noche y eso es lo esperado, no una falla**
(solo cambia si el técnico acepta el apéndice del final).

IP del teléfono en modo hotspot: **192.168.127.125** (verifícala en el paso 3;
si difiere, usa la real en todos lados).

## Soundcheck (pasos en orden)

1. **Teléfono**: enciende el hotspot del Xiaomi. Conéctalo a corriente/powerbank.
   Si el server no estuviera corriendo: abrir Termux y `sh /sdcard/xio_termux/run_server.sh`.
2. **Laptop**: conéctala al WiFi del hotspot.
3. **Chequeo GO/NO-GO**: doble click a `check_show.bat` (esta carpeta).
   Todo verde (los AVISOS amarillos de audio/setlist no bloquean) → seguir.
   Anota la IP que imprime: es la que se dicta a todo el mundo.
4. **Chataigne**: abrir `festival_sentir.noisette` (esta carpeta). Ya trae el
   módulo OSC apuntando a 192.168.127.125:7000 y el módulo Sound Card con LTC
   habilitado. Quedan **2 pasos manuales** (el generador validado del repo no
   cubre mappings, no se improvisa):
   - Módulo **Sound Card** → Inspector → seleccionar la **M-Audio** como
     dispositivo de entrada (el LTC entra por ahí).
   - Menú del panel State Machine o botón derecho → **Add Mapping**:
     - Input: `Sound Card > LTC > Time`
     - Output: módulo `OSC > Custom Message`, address **`/timecode`**, 1 argumento
       con el valor del input (string o float, el monitor acepta ambos).
   Dale play al LTC de la sesión: el tile TC del panel debe correr en verde.
5. **Resolume** (laptop de visuales): Preferences → OSC → **OSC Output**:
   IP `192.168.127.125`, puerto `7000`. Con eso el tile VISUAL se enciende
   cuando Resolume manda actividad.
6. **Setlist**: editar `setlist_festival_sentir.txt` (un tema por línea) y
   doble click a `cargar_setlist.bat`.
7. **Panel en el teléfono**: abrir en el navegador del Xiaomi
   `http://127.0.0.1:5000/api/plugins/foh_monitor/panel`, pantalla completa.
   Subir brillo y poner tiempo de pantalla en "10 min" o más
   (Ajustes → Pantalla); tocar una vez el panel arma el wake-lock del navegador.
   Dejarlo fijo en FOH.

## Líneas exactas para dictar

- Al de visuales (Resolume): «OSC Output a **192.168.127.125 puerto 7000**».
- El TC ya sale de nuestra Chataigne, nadie más configura nada.
- (Luces: solo si acepta el técnico — ver apéndice.)

## Si algo falla (playbook)

| Síntoma | Acción |
|---|---|
| Panel congelado / no refresca | Refrescar la página del navegador. |
| Tile TC rojo CONGELADO | El LTC se detuvo o Chataigne dejó de mapear: revisar play de la sesión y el mapping. |
| Tile TC rojo CAÍDO | No llegan paquetes: ¿laptop sigue en el WiFi del hotspot? ¿Chataigne abierto? |
| Nada llega de un equipo | Verificar que ESE equipo está EN la red del hotspot (no en el WiFi del venue) y que apunta a la IP del paso 3. |
| Server caído (check_show en rojo) | En el teléfono: abrir Termux → `sh /sdcard/xio_termux/run_server.sh` (vuelve en ~15 s; el supervisor también lo revive solo en ~90 s). |
| Hotspot caído | `hotspot_watch` lo revive solo en 30–90 s. Si no: Ajustes → Hotspot, un toque al toggle. |
| Post-show | Bajar el registro: `curl -O http://192.168.127.125:5000/api/plugins/foh_monitor/log` (cada evento lleva el timecode vigente para correlacionar con la sesión). |

## Batería para el show

- Cargar el teléfono **al 100 % antes de salir**.
- En FOH: enchufado a powerbank toda la noche. El charge-limiter **no corta**
  con powerbank común (viene apagado por defecto); si la noche es larga y
  quieres cuidar la batería, **desenchufa el powerbank al llegar a ~90 %** y
  vuelve a enchufar si baja de ~40 %.
- El panel muestra nivel y temperatura; ≥45 °C sale en rojo.

---

## APÉNDICE — LUCES: SI EL TÉCNICO ACEPTA (2 minutos)

Vía pre-armada por si el técnico de la grandMA3 ofrece una copia de Art-Net,
aunque sea a último minuto. Cable de la consola al puerto ethernet de la
laptop; la laptop reenvía por WiFi al teléfono (`relay_luces.bat`).

**Mensaje corto para mandarle al técnico si acepta:**

> Agrégame una salida Art-Net en una interfaz libre de la MA3, destino unicast
> `2.0.0.2` (mi laptop por cable), universo el que ustedes usen. Yo pongo
> `2.0.0.1/255.0.0.0` de tu lado si quieres, o dime qué IP le pongo a mi
> extremo. Es solo escucha, no mando nada.

**En la grandMA3 (dictar):**
1. Menú → **In & Out / Network Protocols → Art-Net → Add** (salida/output).
2. Interfaz: la libre (no la de su rig). Destino: **IP de la laptop en ese
   cable** (sugerido `2.0.0.2`). Universo: el que ellos usen.
3. Convención clásica Art-Net para el cable directo: consola `2.0.0.1`,
   laptop `2.0.0.2`, máscara `255.0.0.0` en ambos.

**En la laptop (3 clicks + doble click):**
1. Configuración → Red e Internet → Ethernet → el adaptador del cable →
   Editar asignación de IP → **Manual, IPv4**: IP `2.0.0.2`,
   máscara `255.0.0.0` (longitud 8), puerta de enlace vacía → Guardar.
2. Doble click a **`relay_luces.bat`**: muestra las IPs locales y un contador
   de paquetes en vivo (si el contador sube, la consola está llegando).
3. Verificar en el panel del teléfono: **tile LUCES pasa de N/D a verde**.

Si en vez de Art-Net ofrecen sACN, es el mismo relay (reenvía ambos puertos);
en la MA3 sería Network Protocols → sACN → output unicast a la laptop.

Nota técnica: el relay reenvía los paquetes tal cual por unicast a
`192.168.127.125:6454/5568`; el monitor solo escucha, jamás emite hacia el rig.
