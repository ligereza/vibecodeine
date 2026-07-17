# Wake-on-LAN / Wake-on-WiFi de MAK

El teléfono Xiaomi (o el PC Windows) puede DESPERTAR a MAK. MAK duerme solo
por comando (nunca por inactividad: eso quedó apagado).

## Estado (verificado 2026-07-16)

| Camino | Cómo | Estado |
|---|---|---|
| **Teléfono → MAK (wifi)** | WoWLAN magic-packet a `a8:7e:ea:41:63:a1` | armado; se re-arma antes de cada suspend |
| **Windows → MAK (ethernet)** | WoL magic a `8c:47:be:20:02:67` | persistido en NetworkManager (`lan-kvm`, wake-on-lan=magic) |
| **Dormir MAK** | `python3 ~/plataforma/energia.py dormir` (`systemctl suspend`) | disponible (suspend desenmascarado) |

## Cómo despierta el teléfono a MAK

1. MAK está suspendido (S3). El hook `/lib/systemd/system-sleep/00-wowlan-mak`
   armó WoWLAN magic-packet en la wifi antes de dormir.
2. El teléfono envía un magic packet por el broadcast del hotspot:
   plugin staged `xio_puente/staged/wake_mak.py` → `GET /wake_mak/wake`.
3. La wifi de MAK, escuchando el patrón, lo despierta.

## Límite honesto

WoWLAN despierta desde **suspend (S3)**, donde la wifi sigue alimentada.
Desde **apagado total (S5)** la wifi está muerta: ahí solo despierta por
**ethernet** (magic packet desde el PC Windows a la MAC eth). Por eso hay
dos caminos.

## Instalar el lado teléfono (decisión del usuario)

`wake_mak.py` está *staged*, no desplegado. Cuando el servidor xio vuelva:
copiarlo a la carpeta de plugins, registrar el blueprint `bp`, relanzar con
`run_server.sh`. Prueba: `GET http://TELEFONO:5000/wake_mak/status`.

## Verificar en MAK

```bash
python3 ~/plataforma/energia.py estado
sudo iw phy0 wowlan show          # "magic-packet" = armado
nmcli -t -f 802-3-ethernet.wake-on-lan con show lan-kvm   # :magic
```
