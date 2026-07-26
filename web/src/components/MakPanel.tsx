// MakPanel — the machine that works on its own, finally visible.
//
// MAK is the Linux box running research/codex/plataforma, whose whole point is
// keeping the repo moving without Claude. Until 2026-07-26 it had NOT ONE
// reference in web/src and no hub endpoint: there was no way to see whether it
// was alive, what it had produced, or what was queued. Its only trace was a log
// file inside the box itself.
//
// READ-ONLY on purpose. The panel GETs /api/mak and nothing else; the backend in
// turn only queries the box's /api/organismo. No actions, no button that orders
// anything. Same rule as xio_puente: live infrastructure is watched, not poked
// from a screen.
//
// If FLUJO_MAK_URL is missing, the panel says so and explains what to define.
// If the box is off, it says that. It never invents a green state.
//
// Visible copy stays in Spanish: this is what the user reads.

import { useEffect, useState } from 'react';
import { Cpu, HardDrive, Activity, AlertTriangle, PowerOff, Boxes } from 'lucide-react';

interface Gpu {
  vram_total_mb?: number;
  vram_usada_mb?: number;
  uso_pct?: number;
}
interface Data {
  disponible: boolean;
  configurado?: boolean;
  error?: string;
  ts?: string;
  uptime_s?: number;
  load?: number[];
  mem_disponible_mb?: number;
  disco_libre_gb?: number;
  gpu?: Gpu;
  servicios?: Record<string, boolean>;
  productos?: Record<string, Record<string, number>>;
  micelio_chunks?: number;
}

function duracion(segundos?: number): string {
  if (!segundos && segundos !== 0) return 'sin dato';
  const h = Math.floor(segundos / 3600);
  const m = Math.floor((segundos % 3600) / 60);
  if (h >= 24) return `${Math.floor(h / 24)} d ${h % 24} h`;
  return h > 0 ? `${h} h ${m} min` : `${m} min`;
}

export default function MakPanel() {
  const [data, setData] = useState<Data | null>(null);
  const [cargando, setCargando] = useState(true);

  async function cargar() {
    try {
      const r = await fetch('/api/mak');
      setData(await r.json());
    } catch (e) {
      setData({ disponible: false, error: String(e) });
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    cargar();
    // The box changes slowly: refreshing every 30 s is enough and does not bother it.
    const t = setInterval(cargar, 30000);
    return () => clearInterval(t);
  }, []);

  if (cargando) {
    return <div className="p-6 text-sm text-neutral-400">Consultando la máquina…</div>;
  }

  if (!data?.disponible) {
    const sinConfigurar = data?.configurado === false;
    return (
      <div className="p-6">
        <div className="flex items-center gap-2 mb-3">
          {sinConfigurar ? (
            <AlertTriangle className="w-5 h-5 text-amber-400" />
          ) : (
            <PowerOff className="w-5 h-5 text-neutral-500" />
          )}
          <h2 className="text-lg font-semibold">
            {sinConfigurar ? 'MAK no está configurado' : 'MAK no responde'}
          </h2>
        </div>
        <p className="text-sm text-neutral-400 max-w-2xl">
          {sinConfigurar
            ? 'Falta la variable de entorno FLUJO_MAK_URL, que dice dónde vive el hub de la máquina (por ejemplo http://<ip-del-box>:8900). Está documentada en MAPA.md, sección de configuración.'
            : 'La máquina está apagada o fuera de la red. Esto no rompe nada del resto del programa.'}
        </p>
        {data?.error && (
          <pre className="mt-3 text-xs text-neutral-500 whitespace-pre-wrap">{data.error}</pre>
        )}
      </div>
    );
  }

  const servicios = Object.entries(data.servicios ?? {});
  const caidos = servicios.filter(([, vivo]) => !vivo);
  const gpu = data.gpu ?? {};

  return (
    <div className="p-6 space-y-6">
      <div>
        <div className="flex items-center gap-2">
          <Cpu className="w-5 h-5 text-emerald-400" />
          <h2 className="text-lg font-semibold">MAK · la máquina que trabaja sola</h2>
        </div>
        <p className="text-sm text-neutral-400 mt-1">
          Estado leído directamente del box. Solo lectura: desde acá no se le ordena nada.
          {data.ts ? ` Medido a las ${data.ts}.` : ''}
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Tarjeta icono={<Activity className="w-4 h-4" />} titulo="Encendida hace">
          {duracion(data.uptime_s)}
        </Tarjeta>
        <Tarjeta icono={<Activity className="w-4 h-4" />} titulo="Carga (1 min)">
          {data.load?.[0] ?? 'sin dato'}
        </Tarjeta>
        <Tarjeta icono={<HardDrive className="w-4 h-4" />} titulo="Disco libre">
          {data.disco_libre_gb != null ? `${data.disco_libre_gb} GB` : 'sin dato'}
        </Tarjeta>
        <Tarjeta icono={<Cpu className="w-4 h-4" />} titulo="Memoria de video">
          {gpu.vram_usada_mb != null && gpu.vram_total_mb != null
            ? `${gpu.vram_usada_mb} / ${gpu.vram_total_mb} MB`
            : 'sin dato'}
        </Tarjeta>
      </div>

      <div>
        <h3 className="text-sm font-semibold mb-2">Servicios</h3>
        {servicios.length === 0 ? (
          <p className="text-sm text-neutral-500">El box no reportó servicios.</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {servicios.map(([nombre, vivo]) => (
              <span
                key={nombre}
                className={
                  'text-xs px-2 py-1 rounded border ' +
                  (vivo
                    ? 'border-emerald-700 text-emerald-300'
                    : 'border-red-700 text-red-300')
                }
              >
                {nombre} · {vivo ? 'vivo' : 'caído'}
              </span>
            ))}
          </div>
        )}
        {caidos.length > 0 && (
          <p className="text-xs text-red-300 mt-2">
            {caidos.length === 1
              ? 'Hay un servicio caído.'
              : `Hay ${caidos.length} servicios caídos.`}{' '}
            Los vigilantes del box intentan revivirlos solos cada 5 minutos.
          </p>
        )}
      </div>

      <div>
        <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
          <Boxes className="w-4 h-4" /> Lo que produjo
        </h3>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {Object.entries(data.productos ?? {}).map(([depto, valores]) => (
            <div key={depto} className="rounded border border-neutral-800 p-3">
              <div className="text-xs uppercase tracking-wide text-neutral-500 mb-1">{depto}</div>
              <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm">
                {Object.entries(valores).map(([k, v]) => (
                  <span key={k} className="text-neutral-300">
                    <b className="text-emerald-300">{v}</b> {k}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
        {data.micelio_chunks != null && (
          <p className="text-xs text-neutral-500 mt-2">
            Micelio semántico: {data.micelio_chunks} fragmentos indexados.
          </p>
        )}
      </div>
    </div>
  );
}

function Tarjeta({
  icono,
  titulo,
  children,
}: {
  icono: React.ReactNode;
  titulo: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded border border-neutral-800 p-3">
      <div className="flex items-center gap-2 text-xs uppercase tracking-wide text-neutral-500">
        {icono}
        {titulo}
      </div>
      <div className="text-lg mt-1">{children}</div>
    </div>
  );
}
