// ShowPanel — el show kit de xio dentro del hub.
//
// Contexto para quien lo lea despues: el dia del show hay DOS sistemas
// independientes a proposito (ver xio/show_kit/DIA_DEL_SHOW.md):
//   - LAPTOP (activo): Chataigne decodifica LTC -> OSC, cue_engine dispara clips
//     en Resolume. Es el show en si.
//   - XIO / telefono (pasivo): solo escucha y registra. Si muere, el show sigue.
// Este panel NO controla nada del show: muestra lo que vive en el repo (setlist,
// cues, duraciones, registros ya corridos) y da los comandos exactos del dia.
// El estado en vivo del telefono se consulta directo a su IP, no via este hub.

import { useEffect, useState } from 'react';
import { Radio, ListMusic, FileClock, Terminal, AlertTriangle, Clock } from 'lucide-react';

interface Tema {
  indice: number;
  timecode: string;
  tema: string;
  duracion_s: number | null;
}
interface Cue {
  timecode: string;
  layer: number | null;
  clip: number | null;
  nota: string;
}
interface ArchivoReg {
  nombre: string;
  eventos: number;
  kb: number;
}
interface Registro {
  show: string;
  archivos: ArchivoReg[];
}
interface ShowKit {
  setlist: Tema[];
  cues: Cue[];
  fps: number | null;
  registros: Registro[];
  resumen?: {
    temas: number;
    cues: number;
    con_duracion: number;
    shows_registrados: number;
  };
  error?: string;
}

const mmss = (s: number | null): string => {
  if (s == null) return '—';
  const t = Math.round(s);
  return `${Math.floor(t / 60)}:${String(t % 60).padStart(2, '0')}`;
};

export default function ShowPanel() {
  const [data, setData] = useState<ShowKit | null>(null);
  const [estado, setEstado] = useState<'cargando' | 'ok' | 'sin-backend'>('cargando');

  useEffect(() => {
    let vivo = true;
    fetch('/api/show-kit')
      .then(r => r.json())
      .then(d => {
        if (!vivo) return;
        setData(d);
        setEstado('ok');
      })
      .catch(() => vivo && setEstado('sin-backend'));
    return () => {
      vivo = false;
    };
  }, []);

  const r = data?.resumen;
  const totalEventos = (data?.registros || []).reduce(
    (acc, reg) => acc + reg.archivos.reduce((a, f) => a + f.eventos, 0),
    0,
  );

  return (
    <div className="space-y-6">
      <header className="flex items-start gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-violet-900/40 text-violet-300">
          <Radio className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-xl font-bold tracking-tight">Show kit</h1>
          <p className="text-sm text-zinc-500">
            Setlist con timecode, cues de Resolume y registros de shows corridos. Fuente:{' '}
            <code className="text-zinc-400">xio/show_kit/</code>
          </p>
        </div>
      </header>

      {estado === 'sin-backend' && (
        <div className="flex items-start gap-2 rounded-xl border border-amber-800/50 bg-amber-950/30 p-4 text-sm text-amber-300">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          <div>
            Sin backend. Este panel lee el show kit desde el repo, así que necesita{' '}
            <code className="text-amber-200">py -m flujo app</code> corriendo.
          </div>
        </div>
      )}

      {estado === 'ok' && r && (
        <>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {[
              { k: 'Temas', v: r.temas, d: `${r.con_duracion} con duración` },
              { k: 'Cues', v: r.cues, d: data?.fps ? `${data.fps} fps` : '' },
              { k: 'Shows registrados', v: r.shows_registrados, d: `${totalEventos} eventos` },
              { k: 'Sistema', v: 'pasivo', d: 'no controla el show' },
            ].map(c => (
              <div key={c.k} className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4">
                <div className="text-[10px] font-bold uppercase tracking-widest text-zinc-600">{c.k}</div>
                <div className="mt-1 text-2xl font-black text-zinc-100">{c.v}</div>
                {c.d && <div className="text-[11px] text-zinc-600">{c.d}</div>}
              </div>
            ))}
          </div>

          <section className="rounded-xl border border-zinc-800 bg-zinc-900/40">
            <div className="flex items-center gap-2 border-b border-zinc-800 px-4 py-3">
              <ListMusic className="h-4 w-4 text-violet-400" />
              <h2 className="text-sm font-bold">Setlist</h2>
              <span className="text-[11px] text-zinc-600">timecode → tema → duración del clip</span>
            </div>
            <div className="max-h-[420px] overflow-y-auto">
              <table className="w-full text-sm">
                <tbody>
                  {(data?.setlist || []).map(t => (
                    <tr key={t.indice} className="border-b border-zinc-800/60 last:border-0">
                      <td className="w-10 px-4 py-2 text-right text-[11px] text-zinc-600">{t.indice + 1}</td>
                      <td className="w-32 py-2 font-mono text-[12px] text-violet-300">{t.timecode}</td>
                      <td className="py-2 text-zinc-200">{t.tema}</td>
                      <td className="w-20 px-4 py-2 text-right font-mono text-[12px] text-zinc-500">
                        {mmss(t.duracion_s)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {(data?.registros || []).length > 0 && (
            <section className="rounded-xl border border-zinc-800 bg-zinc-900/40">
              <div className="flex items-center gap-2 border-b border-zinc-800 px-4 py-3">
                <FileClock className="h-4 w-4 text-violet-400" />
                <h2 className="text-sm font-bold">Registros de show</h2>
                <span className="text-[11px] text-zinc-600">evidencia cruda, no editar</span>
              </div>
              <div className="divide-y divide-zinc-800/60">
                {(data?.registros || []).map(reg => (
                  <div key={reg.show} className="px-4 py-3">
                    <div className="font-mono text-[13px] text-zinc-200">{reg.show}</div>
                    <div className="mt-1 flex flex-wrap gap-2">
                      {reg.archivos.map(a => (
                        <span
                          key={a.nombre}
                          className="rounded-md border border-zinc-800 bg-zinc-950 px-2 py-1 text-[11px] text-zinc-500"
                        >
                          {a.nombre} · <strong className="text-zinc-300">{a.eventos}</strong> ev · {a.kb} KB
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}
        </>
      )}

      {/* Siempre visible: no depende del backend y es lo que se busca con apuro. */}
      <section className="rounded-xl border border-zinc-800 bg-zinc-900/40">
        <div className="flex items-center gap-2 border-b border-zinc-800 px-4 py-3">
          <Terminal className="h-4 w-4 text-violet-400" />
          <h2 className="text-sm font-bold">Día del show</h2>
          <span className="text-[11px] text-zinc-600">xio/show_kit/DIA_DEL_SHOW.md</span>
        </div>
        <div className="space-y-3 p-4 text-sm">
          <div className="flex items-start gap-2 rounded-lg border border-amber-800/40 bg-amber-950/20 p-3 text-[13px] text-amber-300">
            <Clock className="mt-0.5 h-4 w-4 shrink-0" />
            <div>
              <strong>El server del teléfono no arranca solo tras un reboot.</strong> Si se apagó (batería a 0,
              por ejemplo), hay que lanzarlo a mano desde Termux. Y la IP cambia sola en un venue con DHCP:
              si el panel no responde, buscá la IP real antes que nada.
            </div>
          </div>
          {[
            { t: 'Arrancar el server (en el teléfono, Termux)', c: 'sh /sdcard/xio_termux/run_server.sh' },
            { t: 'Chequeo GO / NO-GO antes del show', c: 'py xio/show_kit/check_show.py <IP>' },
            { t: 'Cargar el setlist al panel FOH', c: 'xio\\show_kit\\cargar_setlist.bat' },
            { t: 'Motor de cues (dispara clips en Resolume)', c: 'xio\\show_kit\\cue_engine.bat' },
          ].map(x => (
            <div key={x.t}>
              <div className="text-[11px] text-zinc-500">{x.t}</div>
              <code className="mt-0.5 block rounded-lg border border-zinc-800 bg-zinc-950 px-3 py-2 font-mono text-[12px] text-emerald-300">
                {x.c}
              </code>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
