#!/usr/bin/env python3
"""energia_log.py -- medicion de energia Wh/dia GPU+CPU y politica valle.

Lee potencia instantanea de GPU (nvidia-smi) y CPU (RAPL intel-rapl:0 energy_uj),
muestrea cada intervalo_s, acumula en JSONL con timestamp ISO, y resume en tabla
Wh/dia integrada sobre N dias.

Tolerante a hardware faltante: sin GPU/RAPL -> campos None, sigue.

    python3 energia_log.py muestra         # muestreo unitario, append a energia.jsonl (cron)
    python3 energia_log.py resumen [dias]  # tabla ASCII Wh/dia por componente
"""
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path


def leer_gpu_w() -> float | None:
    """Lee potencia GPU en watts via nvidia-smi.

    Returns:
        Potencia en watts, o None si GPU no existe/no responde.
    """
    try:
        output = subprocess.run(
            ["nvidia-smi", "--query-gpu=power.draw",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=3
        ).stdout.strip()
        if output:
            return float(output.split()[0])
    except (OSError, subprocess.TimeoutExpired, ValueError, IndexError):
        pass
    return None


def leer_cpu_uj() -> int | None:
    """Lee energia acumulada CPU via RAPL intel-rapl:0.

    Returns:
        Energia en microjoules, o None si no existe.
    """
    try:
        path = Path("/sys/class/powercap/intel-rapl:0/energy_uj")
        if path.exists():
            return int(path.read_text().strip())
    except (OSError, ValueError):
        pass
    return None


def muestrear(intervalo_s=5) -> dict:
    """Toma una muestra de energia instantanea.

    Args:
        intervalo_s: duracion en segundos para calculo CPU (delta entre 2 lecturas).

    Returns:
        dict con keys: ts (ISO 8601), gpu_w (float|None), cpu_w (float|None).
        cpu_w = (delta energia_uj entre 2 lecturas) / intervalo_s / 1e6 watts.
    """
    ts = datetime.utcnow().isoformat() + "Z"
    gpu_w = leer_gpu_w()

    cpu_uj_1 = leer_cpu_uj()
    if cpu_uj_1 is not None:
        import time
        time.sleep(intervalo_s)
        cpu_uj_2 = leer_cpu_uj()
        if cpu_uj_2 is not None:
            cpu_w = (cpu_uj_2 - cpu_uj_1) / intervalo_s / 1e6
        else:
            cpu_w = None
    else:
        cpu_w = None

    return {"ts": ts, "gpu_w": gpu_w, "cpu_w": cpu_w}


def acumular(ruta_jsonl: str) -> None:
    """Append una muestra a energia.jsonl.

    Args:
        ruta_jsonl: path al archivo JSONL (se crea si no existe).
    """
    muestra = muestrear()
    path = Path(ruta_jsonl)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        json.dump(muestra, f, ensure_ascii=False)
        f.write("\n")


def resumen(ruta_jsonl: str, dias: int = 7) -> str:
    """Genera tabla ASCII Wh/dia integrando muestras sobre N dias.

    Estructura esperada: cada linea = JSON {"ts": "ISO", "gpu_w": float|None, "cpu_w": float|None}.
    Integra potencia media * horas con muestras; cuenta intervalo entre muestras consecutivas.

    Args:
        ruta_jsonl: path al archivo JSONL de muestras.
        dias: ventana temporal (dias atras desde ahora).

    Returns:
        Tabla ASCII con columnas: Fecha, GPU Wh/dia, CPU Wh/dia, Total Wh/dia.
        Si archivo vacio/no existe, retorna "(sin datos)".
    """
    path = Path(ruta_jsonl)
    if not path.exists():
        return "(sin datos)"

    muestras = []
    try:
        with open(path) as f:
            for linea in f:
                linea = linea.strip()
                if linea:
                    muestras.append(json.loads(linea))
    except (OSError, json.JSONDecodeError):
        return "(error al leer %s)" % ruta_jsonl

    if not muestras:
        return "(sin datos)"

    # Filtrar por ventana temporal
    ahora = datetime.utcnow()
    limite = ahora - timedelta(days=dias)

    def parse_ts(ts_str):
        # Soporta "2026-07-22T12:34:56.789Z" y variantes
        # Retorna datetime naive en UTC (compatible con datetime.utcnow())
        ts_clean = ts_str.replace("Z", "")
        try:
            # Intenta parse con microsegundos
            return datetime.fromisoformat(ts_clean)
        except ValueError:
            # Si falla, intenta formato basico
            return datetime.fromisoformat(ts_clean.split(".")[0])

    muestras_filtradas = []
    for m in muestras:
        try:
            ts = parse_ts(m.get("ts", ""))
            if ts >= limite:
                muestras_filtradas.append((ts, m))
        except (ValueError, TypeError):
            pass

    if not muestras_filtradas:
        return "(sin datos en los ultimos %d dias)" % dias

    # Agrupar por dia
    dias_dict = {}
    for ts, m in muestras_filtradas:
        fecha = ts.date()
        if fecha not in dias_dict:
            dias_dict[fecha] = []
        dias_dict[fecha].append((ts, m))

    # Calcular Wh/dia por componente
    lineas = []
    lineas.append("Fecha        | GPU Wh/dia | CPU Wh/dia | Total Wh/dia")
    lineas.append("-" * 60)

    total_global_gpu = 0.0
    total_global_cpu = 0.0

    for fecha in sorted(dias_dict.keys()):
        muestras_dia = sorted(dias_dict[fecha], key=lambda x: x[0])

        wh_gpu = 0.0
        wh_cpu = 0.0

        for i in range(len(muestras_dia) - 1):
            ts_curr, m_curr = muestras_dia[i]
            ts_next, m_next = muestras_dia[i + 1]
            delta_h = (ts_next - ts_curr).total_seconds() / 3600.0

            if m_curr.get("gpu_w") is not None and m_next.get("gpu_w") is not None:
                gpu_w_avg = (m_curr["gpu_w"] + m_next["gpu_w"]) / 2.0
                wh_gpu += gpu_w_avg * delta_h

            if m_curr.get("cpu_w") is not None and m_next.get("cpu_w") is not None:
                cpu_w_avg = (m_curr["cpu_w"] + m_next["cpu_w"]) / 2.0
                wh_cpu += cpu_w_avg * delta_h

        total_global_gpu += wh_gpu
        total_global_cpu += wh_cpu
        total = wh_gpu + wh_cpu

        lineas.append("%s | %10.2f | %10.2f | %12.2f" % (
            fecha.isoformat(),
            wh_gpu,
            wh_cpu,
            total
        ))

    lineas.append("-" * 60)
    lineas.append("%-13s | %10.2f | %10.2f | %12.2f" % (
        "TOTAL",
        total_global_gpu,
        total_global_cpu,
        total_global_gpu + total_global_cpu
    ))

    return "\n".join(lineas)


def main():
    """CLI: muestra (cron) | resumen [dias]"""
    if len(sys.argv) < 2:
        print("uso: energia_log.py [muestra|resumen [dias]]")
        return 2

    cmd = sys.argv[1]
    ruta_default = Path(__file__).parent / "energia.jsonl"

    if cmd == "muestra":
        try:
            acumular(str(ruta_default))
            return 0
        except Exception as e:
            print("ERROR muestra: %s" % e, file=sys.stderr)
            return 1

    elif cmd == "resumen":
        dias = 7
        if len(sys.argv) > 2:
            try:
                dias = int(sys.argv[2])
            except ValueError:
                print("ERROR: dias debe ser entero", file=sys.stderr)
                return 1
        try:
            print(resumen(str(ruta_default), dias))
            return 0
        except Exception as e:
            print("ERROR resumen: %s" % e, file=sys.stderr)
            return 1

    else:
        print("uso: energia_log.py [muestra|resumen [dias]]")
        return 2


if __name__ == "__main__":
    sys.exit(main())
