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
  actividad?: Evento[];
  trabajo?: { hoy?: number; max?: number; ultimo?: string };
  memoria?: Memoria;
  operacion?: {
    estado?: string;
    servicios_vivos?: string[];
    servicios_totales?: number;
    bloquea_produccion?: boolean;
    proximo_paso?: string;
    capacidad_declarada?: string[];
  };
  tandas?: Tandas;
}

interface Memoria {
  accion?: string;
  entradas?: number;
  estados?: Record<string, number>;
  slugs_duplicados?: string[];
  origenes_faltantes?: string[];
  entidades_bloqueadas?: Array<{ id?: string; razon?: string; estado?: string }>;
  bloquea_produccion?: boolean;
}

interface Evento {
  depto: string;
  texto: string;
  estado: string;
  t: string;
  seg?: number;
  razon?: string;
}

interface Tandas {
  common_rows?: number;
  batch_rows?: number;
  accepted?: number;
  rejected_or_revise?: number;
  decisions?: number;
  pending_human?: number;
  by_domain?: Record<string, number>;
  by_provider?: Record<string, number>;
  pending?: Array<{ domain: string; claim: string; action: string; reason: string }>;
  last_batches?: Array<{ area?: string; provider?: string; status?: string; items?: number }>;
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

      <div>
        <h3 className="text-sm font-semibold mb-2">Oportunidades en revisión humana</h3>
        <p className="text-sm text-neutral-400">
          {data.tandas?.pending_human ?? 0} listings guardados por Vigia esperan
          verificar fuente, elegibilidad y encaje artístico. MAK no contacta ni postula.
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

      {data.operacion && (
        <div className="rounded border border-neutral-800 bg-neutral-950/40 p-3">
          <div className="text-sm font-semibold mb-2">Capacidad operativa real</div>
          <div className="grid gap-2 sm:grid-cols-3 text-xs text-neutral-400">
            <span>Estado: <b className={data.operacion.bloquea_produccion ? 'text-amber-300' : 'text-emerald-300'}>{data.operacion.estado}</b></span>
            <span>Servicios vivos: <b className="text-neutral-200">{data.operacion.servicios_vivos?.length ?? 0}/{data.operacion.servicios_totales ?? 0}</b></span>
            <span>Capacidades declaradas: <b className="text-neutral-200">{data.operacion.capacidad_declarada?.length ?? 0}</b></span>
          </div>
          <p className="text-xs text-neutral-500 mt-2">Proximo paso: {data.operacion.proximo_paso}</p>
        </div>
      )}

      <div>
        {data.memoria && data.memoria.accion !== 'auditoria_no_disponible' && (
          <div className="mb-4 rounded border border-neutral-800 bg-neutral-950/40 p-3">
            <div className="text-sm font-semibold mb-2 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" /> Memoria operativa MAK
            </div>
            <div className="grid gap-2 sm:grid-cols-3 text-xs text-neutral-400">
              <span>Entradas: <b className="text-neutral-200">{data.memoria.entradas ?? 0}</b></span>
              <span>Slugs repetidos: <b className="text-amber-300">{data.memoria.slugs_duplicados?.length ?? 0}</b></span>
              <span>Origenes faltantes: <b className="text-amber-300">{data.memoria.origenes_faltantes?.length ?? 0}</b></span>
            </div>
            <div className={data.memoria.accion === 'revisar_memoria' ? 'text-amber-300 text-xs mt-2' : 'text-emerald-400 text-xs mt-2'}>
              {data.memoria.accion === 'revisar_memoria' ? 'MAK detiene nueva produccion generada y prioriza repasar.' : 'Memoria sin bloqueos mecanicos.'}
            </div>
          </div>
        )}
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
        {/* Un departamento que existe y casi no produjo se pierde entre los
            otros: el conteo esta ahi, pero nadie compara tres tarjetas para
            darse cuenta. Se dice. */}
        {departamentosParados(data.productos).length > 0 && (
          <p className="text-xs text-amber-400/90 mt-2">
            Sin trabajo real:{' '}
            {departamentosParados(data.productos).join(', ')}. El departamento está
            levantado pero casi no produjo nada.
          </p>
        )}
      </div>

      {/* Lo que el usuario echaba de menos, textual: "veo casi nada de lo que
          hace, ningun pensamiento, nada corriendo". La caja publica esto y el
          hub no lo mostraba. */}
      <div>
        <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
          <Activity className="w-4 h-4" /> Lo que está haciendo
        </h3>

        {data.trabajo?.max != null && (
          <p className="text-xs text-neutral-400 mb-2">
            Trabajos hoy: <b className="text-neutral-200">{data.trabajo.hoy ?? 0}</b> de{' '}
            {data.trabajo.max}.{' '}
            {(data.trabajo.hoy ?? 0) < data.trabajo.max / 4 && (
              <span className="text-amber-400/90">
                Está muy por debajo de su capacidad: le sobra máquina y le falta trabajo.
              </span>
            )}
          </p>
        )}

        {fallidos(data.actividad).length > 0 && (
          <div className="rounded border border-red-900/60 bg-red-950/20 p-3 mb-2">
            <div className="text-xs font-semibold text-red-300 mb-1">
              {fallidos(data.actividad).length} de los últimos {(data.actividad ?? []).length}{' '}
              trabajos fallaron
            </div>
            {fallidos(data.actividad).slice(0, 3).map((e, i) => (
              <div key={i} className="text-xs text-neutral-400">
                {e.t} · {e.depto} · {e.texto.slice(0, 70)}
                {e.razon ? ` — ${e.razon.slice(0, 60)}` : ''}
              </div>
            ))}
          </div>
        )}

        <div className="rounded border border-neutral-800 divide-y divide-neutral-800/70">
          {(data.actividad ?? []).slice(0, 12).map((e, i) => (
            <div key={i} className="flex items-start gap-2 p-2 text-xs">
              <span className="text-neutral-600 tabular-nums shrink-0">{e.t}</span>
              <span className="text-neutral-500 uppercase shrink-0 w-16">{e.depto}</span>
              <span className="flex-1 text-neutral-300">{e.texto}</span>
              <span
                className={`shrink-0 ${
                  e.estado === 'FALLO' ? 'text-red-400' : 'text-emerald-400/80'
                }`}
              >
                {e.estado === 'FALLO' ? 'falló' : `${e.seg ?? '?'}s`}
              </span>
            </div>
          ))}
          {(data.actividad ?? []).length === 0 && (
            <p className="p-3 text-xs text-neutral-500">
              La caja no reportó actividad. Puede ser que no haya trabajado, o que el
              registro se haya cortado.
            </p>
          )}
        </div>
        <p className="text-xs text-neutral-500 mt-2">
          Cada línea es un trabajo <b>ya terminado</b>: la caja publica cuando cierra,
          no mientras piensa. Por eso nunca se ve nada «corriendo».
        </p>
      </div>

      <div>
        <h3 className="text-sm font-semibold mb-2 flex items-center gap-2">
          <Boxes className="w-4 h-4" /> Tandas externas y juicio local
        </h3>
        {data.tandas && (data.tandas.common_rows ?? 0) > 0 ? (
          <div className="space-y-3">
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <Tarjeta icono={<Activity className="w-4 h-4" />} titulo="Aceptadas">
                {data.tandas.accepted ?? 0}
              </Tarjeta>
              <Tarjeta icono={<AlertTriangle className="w-4 h-4" />} titulo="Revisar/rechazar">
                {data.tandas.rejected_or_revise ?? 0}
              </Tarjeta>
              <Tarjeta icono={<Boxes className="w-4 h-4" />} titulo="Decisiones">
                {data.tandas.decisions ?? 0}
              </Tarjeta>
              <Tarjeta icono={<Activity className="w-4 h-4" />} titulo="Corridas">
                {data.tandas.batch_rows ?? 0}
              </Tarjeta>
            </div>
            <div className="grid gap-3 lg:grid-cols-2">
              <MiniConteo titulo="Áreas" valores={data.tandas.by_domain} />
              <MiniConteo titulo="Proveedores" valores={data.tandas.by_provider} />
            </div>
            {(data.tandas.pending ?? []).length > 0 && (
              <div className="rounded border border-amber-900/60 bg-amber-950/10 p-3">
                <div className="text-xs font-semibold text-amber-300 mb-1">
                  Pendiente de revisión
                </div>
                {(data.tandas.pending ?? []).map((item, i) => (
                  <div key={i} className="text-xs text-neutral-400">
                    {item.domain} · {item.action} · {item.claim}
                    {item.reason ? ` — ${item.reason}` : ''}
                  </div>
                ))}
              </div>
            )}
            <div className="rounded border border-neutral-800 divide-y divide-neutral-800/70">
              {(data.tandas.last_batches ?? []).slice(-6).map((b, i) => (
                <div key={i} className="flex gap-2 p-2 text-xs">
                  <span className="text-neutral-500 uppercase w-28">{b.area}</span>
                  <span className="text-neutral-400 w-16">{b.provider}</span>
                  <span className={b.status === 'accepted' ? 'text-emerald-400' : 'text-amber-300'}>
                    {b.status}
                  </span>
                  <span className="text-neutral-500">{b.items ?? 0} items</span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <p className="text-xs text-neutral-500">
            Todavía no hay ledger de tandas externas visible. Cuando Groq/Gemini produzcan
            hallazgos, entran acá solo después del juicio local.
          </p>
        )}
      </div>
    </div>
  );
}

/** Departamentos levantados que casi no produjeron: se dicen, no se deducen. */
function departamentosParados(productos?: Record<string, Record<string, number>>): string[] {
  return Object.entries(productos ?? {})
    .filter(([, valores]) => Object.values(valores).reduce((a, b) => a + b, 0) <= 1)
    .map(([depto]) => depto);
}

function fallidos(eventos?: Evento[]): Evento[] {
  return (eventos ?? []).filter(e => e.estado === 'FALLO');
}

function MiniConteo({ titulo, valores }: { titulo: string; valores?: Record<string, number> }) {
  const pares = Object.entries(valores ?? {});
  return (
    <div className="rounded border border-neutral-800 p-3">
      <div className="text-xs uppercase tracking-wide text-neutral-500 mb-2">{titulo}</div>
      {pares.length === 0 ? (
        <p className="text-xs text-neutral-500">sin datos</p>
      ) : (
        <div className="flex flex-wrap gap-2">
          {pares.map(([k, v]) => (
            <span key={k} className="text-xs px-2 py-1 rounded border border-neutral-700 text-neutral-300">
              {k}: <b className="text-emerald-300">{v}</b>
            </span>
          ))}
        </div>
      )}
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
