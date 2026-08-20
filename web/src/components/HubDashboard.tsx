import { useEffect, useMemo, useState } from 'react';
import {
  LayoutDashboard, Boxes, ClipboardList, Calculator,
  TerminalSquare, Map, Shapes, Zap, Activity,
  CheckCircle2, Clock, AlertCircle, ArrowRight, Camera, Radio, Layers,
  Loader2,
} from 'lucide-react';
import type { AppView } from './AppShell';
import { flujoApi, type Ping, type HubStatus, type JobsResponse, type ProjectLearningSummary, type ProjectProbeResponse } from '../api/flujoApi';

interface Props {
  onNavigate: (v: AppView) => void;
}

export default function HubDashboard({ onNavigate }: Props) {
  const [ping, setPing] = useState<Ping | null>(null);
  const [jobs, setJobs] = useState<JobsResponse | null>(null);
  const [learning, setLearning] = useState<ProjectLearningSummary | null>(null);
  const [systemStatus, setSystemStatus] = useState<HubStatus | null>(null);
  const [probeOpen, setProbeOpen] = useState(false);
  const [probeText, setProbeText] = useState('');
  const [probeResult, setProbeResult] = useState<ProjectProbeResponse | null>(null);
  const [probeBusy, setProbeBusy] = useState(false);

  useEffect(() => {
    let alive = true;
    flujoApi.ping().then(d => alive && setPing(d));
    flujoApi.jobs().then(d => alive && setJobs(d));
    flujoApi.status().then(d => {
      if (!alive) return;
      setSystemStatus(d);
      setLearning(d.operational?.learning || null);
    });
    return () => { alive = false; };
  }, []);

  const openJobs = jobs?.jobs.filter(j => !String(j.estado || '').toLowerCase().includes('entregado')).length ?? 0;
  const recent = useMemo(() => (jobs?.jobs || []).slice(0, 5), [jobs]);
  const projectCount = Object.values(learning?.projects || {}).reduce((sum, count) => sum + count, 0);
  const episodeCount = Object.values(learning?.episodes || {}).reduce((sum, count) => sum + count, 0);
  const promotedRules = learning?.rules?.promoted || 0;
  const contractCount = Object.values(learning?.contracts?.counts || {}).reduce((sum, count) => sum + count, 0);
  const auditedCount = Object.values(learning?.audits?.statuses || {}).reduce((sum, count) => sum + count, 0);
  const auditAttention = learning?.audits?.attention || [];
  const latestAbstain = learning?.latest_abstain;
  const operational = systemStatus?.operational;
  const operationalStatus = String(operational?.status || 'unknown');
  const operationalStatusLabel = {
    ready: 'Listo',
    attention: 'Requiere atención',
    blocked: 'Bloqueado',
    unknown: 'No disponible',
  }[operationalStatus] || operationalStatus;
  const operationalStatusClass = operationalStatus === 'ready'
    ? 'border-emerald-800/60 bg-emerald-950/20 text-emerald-300'
    : operationalStatus === 'blocked'
      ? 'border-rose-800/60 bg-rose-950/20 text-rose-300'
      : operationalStatus === 'attention'
        ? 'border-amber-800/60 bg-amber-950/20 text-amber-300'
        : 'border-zinc-700 bg-zinc-900/60 text-zinc-400';

  const runProbe = async () => {
    setProbeBusy(true);
    setProbeResult(null);
    try {
      const parsed = JSON.parse(probeText);
      setProbeResult(await flujoApi.projectProbe(parsed));
    } catch (error) {
      setProbeResult({ ok: false, error: error instanceof Error ? error.message : String(error) });
    } finally {
      setProbeBusy(false);
    }
  };

  // Editables primero (producen trabajo dentro de la app); consulta y
  // generadores de comandos copy/paste al final.
  const actions = [
    { view: 'plano' as const, icon: Map, title: 'Plano / Rider', desc: 'Dibujá el plano del evento y sacá su rider para el recinto', color: 'from-emerald-500 to-teal-600', badge: 'editable' },
    { view: 'visualizer' as const, icon: Shapes, title: 'SVG Studio', desc: 'Revisá las piezas de diseño y ajustá textos y alineación', color: 'from-violet-500 to-purple-600', badge: 'editable' },
    { view: 'quote' as const, icon: Calculator, title: 'Cotización', desc: 'Armá el presupuesto y exportalo en PDF', color: 'from-pink-500 to-rose-600', badge: 'editable' },
    { view: 'intake' as const, icon: ClipboardList, title: 'Pegar Pedido', desc: 'Pegá el correo del cliente y queda anotado como trabajo', color: 'from-blue-500 to-cyan-600', badge: 'editable' },
    { view: 'jobs' as const, icon: Boxes, title: 'Ver trabajos', desc: 'En qué va cada trabajo, con lo que hay en disco', color: 'from-yellow-500 to-amber-600' },
    { view: 'events' as const, icon: Camera, title: 'Eventos / IG', desc: 'Prepara el flyer de un evento desde su publicación de Instagram', color: 'from-fuchsia-500 to-violet-600', badge: 'Studio' },
    { view: 'resolume' as const, icon: Radio, title: 'Resolume / Chataigne', desc: 'Arma el comando SMPTE/OSC pre-flight para shows', color: 'from-indigo-500 to-blue-600', badge: 'SMPTE' },
    { view: 'commands' as const, icon: TerminalSquare, title: 'Comandos', desc: 'Copiar checks y build', color: 'from-zinc-400 to-zinc-600' },
    { view: 'cultura' as const, icon: Layers, title: 'Cultura', desc: 'Arte-investigacion: tapiz, tilde, psicosis, precursor', color: 'from-amber-500 to-orange-700', badge: 'Cultura' },
  ];

  const statusColor = (s?: string) => {
    const v = String(s || '').toLowerCase();
    if (v.includes('entregado')) return 'text-emerald-400 bg-emerald-500/10';
    if (v.includes('revision') || v.includes('revis')) return 'text-blue-400 bg-blue-500/10';
    if (v.includes('diseno') || v.includes('dise')) return 'text-purple-400 bg-purple-500/10';
    if (v.includes('pendiente')) return 'text-yellow-400 bg-yellow-500/10';
    return 'text-zinc-400 bg-zinc-800';
  };

  return (
    <div className="space-y-8">
      {/* Hero header */}
      <div className="relative overflow-hidden rounded-2xl border border-zinc-800/70 bg-gradient-to-br from-zinc-900 via-zinc-900 to-zinc-800 p-6 md:p-8">
        <div className="absolute right-0 top-0 h-64 w-64 bg-gradient-to-bl from-emerald-500/5 to-transparent" />
        <div className="relative">
          <div className="flex items-center gap-3 mb-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 shadow-lg shadow-emerald-500/20">
              <Zap className="h-5 w-5 text-white" />
            </div>
            <div>
              <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider
                ${ping?.connected !== false ? 'border-emerald-800 bg-emerald-950/50 text-emerald-400' : 'border-zinc-700 bg-zinc-800/50 text-zinc-400'}`}>
                <span className={`h-1.5 w-1.5 rounded-full ${ping?.connected !== false ? 'bg-emerald-400 animate-pulse' : 'bg-zinc-500'}`} />
                {ping?.connected !== false ? 'todo local, sin nube' : 'modo demostración'}
              </span>
            </div>
          </div>
          <h1 className="text-2xl font-black tracking-tight md:text-3xl">Panel de trabajo</h1>
          <p className="mt-2 max-w-xl text-sm text-zinc-400 leading-relaxed">
            Desde acá se atiende el día: se reciben los pedidos, se arman los planos y riders de cada evento, se cotiza y se revisan las piezas de diseño antes de entregarlas.
          </p>
        </div>

        {/* Stats row */}
        <div className="relative mt-6 grid grid-cols-2 gap-3 md:grid-cols-4">
          {[
            { label: 'Trabajos abiertos', value: openJobs, icon: Activity, color: 'text-amber-400' },
            { label: 'Trabajos en total', value: jobs?.count ?? 0, icon: Boxes, color: 'text-blue-400' },
            { label: 'Versión', value: ping?.version || '—', icon: LayoutDashboard, color: 'text-emerald-400' },
            { label: 'Estado', value: ping?.connected !== false ? 'Conectado' : 'Demo', icon: ping?.connected !== false ? CheckCircle2 : AlertCircle, color: ping?.connected !== false ? 'text-emerald-400' : 'text-zinc-400' },
          ].map(stat => {
            const Icon = stat.icon;
            return (
              <div key={stat.label} className="rounded-xl border border-zinc-800/60 bg-black/30 p-3">
                <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-zinc-500">
                  <Icon className={`h-3.5 w-3.5 ${stat.color}`} />
                  {stat.label}
                </div>
                <div className="mt-1 text-lg font-bold">{stat.value}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Unified operational state: one source for the CLI and the Hub. */}
      <div className={`rounded-2xl border p-5 md:p-6 ${operationalStatusClass}`}>
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <div className="flex items-center gap-2">
              {operationalStatus === 'ready' ? <CheckCircle2 className="h-4 w-4" /> : <AlertCircle className="h-4 w-4" />}
              <h2 className="text-lg font-bold">Estado de la casa</h2>
              <span className="rounded-full border border-current/30 px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider">
                {operationalStatusLabel}
              </span>
            </div>
            <p className="mt-1 max-w-2xl text-xs leading-relaxed text-zinc-500">
              El Hub, el comando local y el ledger leen el mismo estado. Las abstenciones se conservan como decisiones seguras; no se convierten en falsos éxitos.
            </p>
          </div>
          <div className="shrink-0 text-right text-[10px] text-zinc-600">
            <div>{operational?.read_only === false ? 'con escritura' : 'solo lectura'}</div>
            <div>{operational?.counts?.attention || 0} atención · {operational?.counts?.blocked || 0} bloqueo</div>
          </div>
        </div>
        {operational?.attention && operational.attention.length > 0 ? (
          <div className="mt-4 grid gap-2 md:grid-cols-2">
            {operational.attention.filter(item => item.severity !== 'info').slice(0, 6).map(item => (
              <div key={item.id} className="rounded-xl border border-current/20 bg-black/20 p-3">
                <div className="text-[10px] font-bold uppercase tracking-wider text-current">{item.kind || 'estado'} · {item.status || 'unknown'}</div>
                <div className="mt-1 text-xs text-zinc-400">{item.reason || item.id}</div>
                {item.next_action && <div className="mt-2 text-[10px] text-zinc-500">Siguiente: {item.next_action}</div>}
              </div>
            ))}
          </div>
        ) : (
          <div className="mt-4 text-xs text-zinc-500">No hay excepciones operativas registradas.</div>
        )}
        {operational?.next_actions && operational.next_actions.length > 0 && (
          <div className="mt-4 border-t border-current/15 pt-3 text-[10px] text-zinc-500">
            Próximo: {operational.next_actions[0]}
          </div>
        )}
      </div>

      {/* Learning ledger: bounded visibility, no automatic execution. */}
      <div className="rounded-2xl border border-cyan-900/40 bg-gradient-to-br from-cyan-950/20 via-zinc-900/60 to-zinc-900/40 p-5 md:p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-cyan-400" />
              <h2 className="text-lg font-bold">Memoria operativa</h2>
              <span className="rounded-full border border-cyan-800/60 bg-cyan-950/40 px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider text-cyan-300">
                ledger
              </span>
            </div>
            <p className="mt-1 max-w-2xl text-xs leading-relaxed text-zinc-500">
              Registra proyectos, pruebas y abstenciones. Una abstención es una decisión segura: falta evidencia, no es un error del Hub.
            </p>
          </div>
          <div className="flex shrink-0 flex-wrap justify-end gap-2">
            <button
              onClick={() => onNavigate('intake')}
              className="inline-flex items-center justify-center gap-1.5 rounded-lg border border-zinc-700 bg-zinc-900/60 px-3 py-2 text-xs font-bold text-zinc-300 transition-colors hover:bg-zinc-800"
            >
              Abrir intake <ArrowRight className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={() => setProbeOpen(value => !value)}
              className="inline-flex items-center justify-center gap-1.5 rounded-lg border border-cyan-800/60 bg-cyan-950/30 px-3 py-2 text-xs font-bold text-cyan-300 transition-colors hover:bg-cyan-900/40"
            >
              Probe read-only
            </button>
          </div>
        </div>
        <div className="mt-5 grid grid-cols-2 gap-3 md:grid-cols-6">
          {[
            { label: 'Proyectos', value: learning?.available ? projectCount : '—', note: learning?.projects?.review_required ? `${learning.projects.review_required} en revisión` : 'ledger local', color: 'text-cyan-300' },
            { label: 'Episodios', value: learning?.available ? episodeCount : '—', note: learning?.episodes?.needs_evidence ? `${learning.episodes.needs_evidence} requieren evidencia` : 'sin pruebas pendientes', color: 'text-amber-300' },
            { label: 'Reglas promovidas', value: learning?.available ? promotedRules : '—', note: 'sin autoejecución', color: 'text-violet-300' },
            { label: 'Contratos', value: learning?.contracts?.available ? contractCount : '—', note: learning?.contracts?.available ? 'formatos + consumidores' : learning?.contracts?.reason || 'pendiente de materializar', color: 'text-emerald-300' },
            { label: 'Auditoría', value: learning?.audits?.available ? auditedCount : '—', note: learning?.audits?.available ? `${learning.audits.statuses?.verified || 0} verificados · ${learning.audits.statuses?.needs_evidence || 0} evidencia · ${learning.audits.statuses?.unavailable || 0} no disponibles` : learning?.audits?.reason || 'pendiente de auditar', color: 'text-sky-300' },
            { label: 'Último abstain', value: latestAbstain ? 'registrado' : learning?.available ? 'ninguno' : '—', note: latestAbstain?.phase || learning?.reason || 'criterio de seguridad', color: 'text-rose-300' },
          ].map(stat => (
            <div key={stat.label} className="rounded-xl border border-zinc-800/70 bg-black/25 p-3">
              <div className="text-[10px] font-bold uppercase tracking-widest text-zinc-600">{stat.label}</div>
              <div className={`mt-1 text-lg font-bold ${stat.color}`}>{stat.value}</div>
              <div className="mt-1 truncate text-[10px] text-zinc-600" title={stat.note}>{stat.note}</div>
            </div>
          ))}
        </div>
        {latestAbstain && (
          <div className="mt-3 rounded-xl border border-rose-950/60 bg-rose-950/10 px-3 py-2 text-[11px] text-zinc-500">
            <span className="font-bold text-rose-300">{latestAbstain.episode_id}</span>
            <span className="mx-1.5 text-zinc-700">·</span>
            {latestAbstain.objective || 'Episodio sin objetivo legible'}
          </div>
        )}
        {auditAttention.length > 0 && (
          <div className="mt-3 rounded-xl border border-amber-900/50 bg-amber-950/10 px-3 py-2 text-[11px] text-zinc-500">
            <span className="font-bold text-amber-300">Atención de auditoría:</span>{' '}
            {auditAttention.map(item => `${item.contract_id || 'contract'}=${item.status || 'unknown'}${item.missing?.length ? ` (${item.missing.join(', ')})` : ''}`).join(' · ')}
          </div>
        )}
        {probeOpen && (
          <div className="mt-4 rounded-xl border border-cyan-900/50 bg-black/25 p-3">
            <div className="mb-2 text-[10px] font-bold uppercase tracking-widest text-cyan-400">Evaluar Project IR sin ejecutar herramientas</div>
            <textarea
              value={probeText}
              onChange={event => setProbeText(event.target.value)}
              rows={5}
              placeholder="Pega aquí un objeto Project IR en JSON"
              className="w-full rounded-lg border border-zinc-800 bg-black/40 px-3 py-2 font-mono text-[10px] leading-5 text-zinc-300 outline-none focus:border-cyan-800"
            />
            <div className="mt-2 flex flex-wrap items-center gap-2">
              <button
                onClick={runProbe}
                disabled={probeBusy || !probeText.trim()}
                className="inline-flex items-center gap-1.5 rounded-lg bg-cyan-500 px-3 py-2 text-xs font-bold text-black hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {probeBusy && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
                Evaluar
              </button>
              <span className="text-[10px] text-zinc-600">No registra episodios y no inicia Blender, Research ni mutadores.</span>
            </div>
            {probeResult && (
              <pre className="mt-3 max-h-60 overflow-auto rounded-lg bg-black/40 p-3 text-[10px] leading-5 text-zinc-400">
                {JSON.stringify(probeResult, null, 2)}
              </pre>
            )}
          </div>
        )}
      </div>

      {/* Quick actions grid */}
      <div>
        <div className="mb-4 flex items-center gap-2">
          <h2 className="text-lg font-bold">Acciones rápidas</h2>
          <span className="text-xs text-zinc-500">operación diaria</span>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {actions.map(item => {
            const Icon = item.icon;
            return (
              <button
                key={item.view}
                onClick={() => onNavigate(item.view)}
                className="group relative overflow-hidden rounded-xl border border-zinc-800/60 bg-zinc-900/50 p-5 text-left transition-all hover:border-zinc-700 hover:bg-zinc-800/50 hover:shadow-lg"
              >
                <div className={`absolute inset-0 bg-gradient-to-br ${item.color} opacity-0 transition-opacity group-hover:opacity-[0.03]`} />
                <div className="relative">
                  <div className="flex items-start justify-between">
                    <div className={`flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br ${item.color} shadow-lg`}>
                      <Icon className="h-5 w-5 text-white" />
                    </div>
                    {'badge' in item && item.badge && (
                      <span className="rounded-full bg-violet-500/20 px-2 py-0.5 text-[10px] font-bold text-violet-300">
                        {item.badge}
                      </span>
                    )}
                  </div>
                  <h3 className="mt-3 text-sm font-bold">{item.title}</h3>
                  <p className="mt-1 text-xs text-zinc-500">{item.desc}</p>
                  <div className="mt-3 flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider text-zinc-600 group-hover:text-zinc-400">
                    Abrir <ArrowRight className="h-3 w-3" />
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Recent jobs */}
      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold">Jobs recientes</h2>
          <button onClick={() => onNavigate('jobs')} className="text-xs text-zinc-500 hover:text-zinc-300 flex items-center gap-1">
            Ver todos <ArrowRight className="h-3 w-3" />
          </button>
        </div>
        <div className="space-y-2">
          {recent.length ? recent.map(job => (
            <div key={job.path || job.name} className="flex items-center gap-4 rounded-xl border border-zinc-800/50 bg-zinc-900/30 p-3 transition-colors hover:bg-zinc-800/30">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-zinc-800">
                <Boxes className="h-4 w-4 text-zinc-500" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="text-sm font-medium truncate">{job.name}</div>
                <div className="text-[10px] text-zinc-600 truncate">{job.tipo_pieza || 'pieza'} · {job.proyecto || '—'}</div>
              </div>
              <span className={`shrink-0 rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider ${statusColor(job.estado)}`}>
                {job.estado || 'sin estado'}
              </span>
              <Clock className="h-3.5 w-3.5 text-zinc-700" />
            </div>
          )) : (
            <div className="rounded-xl border border-dashed border-zinc-800 p-8 text-center text-sm text-zinc-600">
              Sin jobs reales todavía. Usa <strong>Intake</strong> para crear uno.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
