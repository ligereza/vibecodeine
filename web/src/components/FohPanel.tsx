import { useEffect, useState } from 'react';
import { Activity, ExternalLink, Radio, RefreshCw } from 'lucide-react';

interface Channel {
  active?: boolean;
  pps?: number;
  age?: number | null;
}

interface FohStatus {
  ok?: boolean;
  domain?: string;
  channels?: { artnet?: Channel; sacn?: Channel; osc?: Channel; audio?: Channel };
  timecode?: { state?: string; value?: string | null };
}

interface FohContext {
  current?: { eventKey?: string; name?: string; producerName?: string; venueName?: string } | null;
}

const BASE = '/api/plugins/foh_monitor';

/**
 * FLUJO-ISKVW only exposes the existing FOH host surface. It does not listen
 * to UDP itself and it does not import RD data; XIO-FOH remains the active
 * listener and owns the JSONL evidence when it is the host.
 */
export default function FohPanel() {
  const [status, setStatus] = useState<FohStatus | null>(null);
  const [context, setContext] = useState<FohContext | null>(null);
  const [error, setError] = useState('');

  const cargar = () => {
    Promise.all([
      fetch(`${BASE}/status`, { cache: 'no-store' }).then(r => r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))),
      fetch(`${BASE}/context/data`, { cache: 'no-store' }).then(r => r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))),
    ])
      .then(([nextStatus, nextContext]) => {
        setStatus(nextStatus);
        setContext(nextContext);
        setError('');
      })
      .catch(err => setError(`Host FOH no disponible en esta dirección (${String(err?.message || err)}).`));
  };

  useEffect(() => {
    cargar();
    const timer = window.setInterval(cargar, 3000);
    return () => window.clearInterval(timer);
  }, []);

  const channels = status?.channels || {};
  const signal = (name: string, channel?: Channel) => ({
    name,
    active: Boolean(channel?.active),
    detail: channel?.active ? `${channel.pps ?? 0} paquetes/s` : 'sin señal reciente',
  });
  const signals = [signal('Art-Net', channels.artnet), signal('OSC / visual', channels.osc), signal('Audio', channels.audio)];

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-violet-900/40 text-violet-300">
            <Radio className="h-5 w-5" />
          </div>
          <div>
            <p className="text-[10px] font-bold uppercase tracking-widest text-violet-400">FLUJO / ISKVW</p>
            <h1 className="text-xl font-bold tracking-tight">FOH</h1>
            <p className="mt-1 max-w-2xl text-sm text-zinc-500">Vista para el equipo del show. XIO-FOH escucha las señales; este hub sólo las visualiza y relaciona con el contexto exacto del evento.</p>
          </div>
        </div>
        <button type="button" onClick={cargar} className="flex items-center gap-2 rounded-lg border border-zinc-800 px-3 py-2 text-xs text-zinc-400 hover:text-zinc-200">
          <RefreshCw className="h-3.5 w-3.5" /> actualizar
        </button>
      </header>

      {error && <div className="rounded-xl border border-amber-800/50 bg-amber-950/20 p-4 text-sm text-amber-300">{error}<span className="mt-1 block text-xs text-amber-500/70">Abre esta misma sección desde el host XIO-FOH para ver actividad en vivo.</span></div>}

      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {signals.map(item => (
          <div key={item.name} className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4">
            <div className="flex items-center justify-between gap-2"><span className="text-[10px] font-bold uppercase tracking-widest text-zinc-600">{item.name}</span><span className={`h-2 w-2 rounded-full ${item.active ? 'bg-emerald-400' : 'bg-zinc-700'}`} /></div>
            <div className="mt-2 flex items-center gap-2 text-lg font-bold text-zinc-100"><Activity className="h-4 w-4 text-violet-400" />{item.active ? 'activo' : 'inactivo'}</div>
            <p className="mt-1 text-[11px] text-zinc-600">{item.detail}</p>
          </div>
        ))}
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4">
          <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-600">Timecode</span>
          <div className="mt-2 text-lg font-bold text-zinc-100">{status?.timecode?.value || status?.timecode?.state || 'sin señal'}</div>
          <p className="mt-1 text-[11px] text-zinc-600">canal separado de OSC visual</p>
        </div>
      </section>

      <section className="rounded-xl border border-violet-900/50 bg-violet-950/10 p-4 sm:p-5">
        <div className="flex items-start gap-3">
          <div className="min-w-0 flex-1"><p className="text-[10px] font-bold uppercase tracking-widest text-violet-400">Contexto del show</p><h2 className="mt-1 text-lg font-bold text-zinc-100">{context?.current?.name || 'Ningún evento FOH seleccionado'}</h2><p className="mt-1 text-xs text-zinc-500">{context?.current ? `${context.current.producerName || 'Productora/artista pendiente'} · ${context.current.venueName || 'venue pendiente'} · eventKey exacto` : 'Selecciona el evento desde el host XIO-FOH; no se crea uno por nombre.'}</p></div>
          <span className="rounded-lg border border-violet-900/60 px-2 py-1 text-[10px] text-violet-300">{context?.current?.eventKey || 'sin eventKey'}</span>
        </div>
      </section>

      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {[['Panel en vivo', `${BASE}/panel`], ['Evento', `${BASE}/context`], ['Registro', `${BASE}/registro`], ['Resumen', `${BASE}/resumen`]].map(([label, href]) => <a key={href} href={href} className="flex items-center justify-between rounded-xl border border-zinc-800 bg-zinc-900/40 p-4 text-sm text-zinc-300 hover:border-violet-800 hover:text-white"><span>{label}</span><ExternalLink className="h-3.5 w-3.5 text-zinc-600" /></a>)}
      </section>

      <div className="overflow-hidden rounded-xl border border-zinc-800 bg-zinc-950">
        <div className="flex items-center justify-between border-b border-zinc-800 px-4 py-3"><h2 className="text-sm font-bold">Monitor FOH del host</h2><span className="text-[10px] text-zinc-600">lectura en vivo · sin interpretación</span></div>
        <iframe title="Monitor FOH del host XIO" src={`${BASE}/panel`} className="h-[520px] w-full border-0 bg-[#07090d]" loading="lazy" />
      </div>
    </div>
  );
}
