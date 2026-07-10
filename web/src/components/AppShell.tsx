import { type ReactNode, useState } from 'react';
import {
  LayoutDashboard, Boxes, ClipboardList, Calculator,
  TerminalSquare, Map, Shapes, Menu, X, ChevronRight,
  Heart, Music, Camera, Cpu, Radio, Lightbulb, Layers,
} from 'lucide-react';

export type AppView =
  | 'hub'
  | 'jobs'
  | 'intake'
  | 'quote'
  | 'commands'
  | 'plano'
  | 'visualizer'
  | 'events'
  | 'resolume'
  | 'mapping'
  | 'cultura';

export type WorkspaceMode = 'rd' | 'studio' | 'cultura';

interface NavItem {
  view: AppView;
  icon: typeof LayoutDashboard;
  label: string;
  desc: string;
  // true = permite editar/crear contenido dentro de la app (editor, formulario
  // con salida real); false = consulta o generador de comandos copy/paste.
  edit: boolean;
}

// Editables primero: son las herramientas que producen trabajo dentro de la app.
const RD_NAV: NavItem[] = [
  { view: 'hub', icon: LayoutDashboard, label: 'Dashboard', desc: 'Vista general RD', edit: false },
  { view: 'plano', icon: Map, label: 'Plano / Rider', desc: 'Editor de layout de evento', edit: true },
  { view: 'visualizer', icon: Shapes, label: 'SVG Studio', desc: 'Galeria + editor visual', edit: true },
  { view: 'quote', icon: Calculator, label: 'Cotizacion', desc: 'Presupuesto editable', edit: true },
  { view: 'intake', icon: ClipboardList, label: 'Intake', desc: 'Parsear pedidos y crear jobs', edit: true },
  { view: 'jobs', icon: Boxes, label: 'Jobs / Suplementos', desc: 'Estado de trabajos', edit: false },
];

const STUDIO_NAV: NavItem[] = [
  { view: 'hub', icon: LayoutDashboard, label: 'Dashboard', desc: 'Vista general Studio', edit: false },
  { view: 'visualizer', icon: Shapes, label: 'SVG Studio', desc: 'Galeria + editor visual', edit: true },
  { view: 'mapping', icon: Lightbulb, label: 'Mapping LED', desc: 'Rigging / pixel mapping', edit: true },
  { view: 'events', icon: Camera, label: 'Eventos / IG', desc: 'Comando flyer-auto', edit: false },
  { view: 'resolume', icon: Radio, label: 'Resolume / Chataigne', desc: 'Comando SMPTE/OSC', edit: false },
  { view: 'commands', icon: TerminalSquare, label: 'Comandos', desc: 'CLI reference', edit: false },
];

// Cultura: ala de arte-investigacion (tapiz, tilde, psicosis, precursor).
// Por ahora un solo panel de consulta; las herramientas ganan panel al madurar.
const CULTURA_NAV: NavItem[] = [
  { view: 'hub', icon: LayoutDashboard, label: 'Dashboard', desc: 'Vista general Cultura', edit: false },
  { view: 'cultura', icon: Layers, label: 'Cultura', desc: 'Instrumentos y lineas de obra', edit: false },
];

const NAV_BY_MODE: Record<WorkspaceMode, NavItem[]> = {
  rd: RD_NAV,
  studio: STUDIO_NAV,
  cultura: CULTURA_NAV,
};

interface Props {
  view: AppView;
  onViewChange: (v: AppView) => void;
  children: ReactNode;
}

export default function AppShell({ view, onViewChange, children }: Props) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [mode, setMode] = useState<WorkspaceMode>('rd');

  const navItems = NAV_BY_MODE[mode];
  const currentLabel = navItems.find(i => i.view === view)?.label
    || RD_NAV.find(i => i.view === view)?.label
    || STUDIO_NAV.find(i => i.view === view)?.label
    || CULTURA_NAV.find(i => i.view === view)?.label
    || 'flujo';

  const switchMode = (m: WorkspaceMode) => {
    setMode(m);
    // If current view doesn't exist in the new mode, go to hub
    const targetNav = NAV_BY_MODE[m];
    if (!targetNav.find(n => n.view === view)) {
      onViewChange('hub');
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-zinc-950 text-zinc-100">
      {/* Sidebar overlay on mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-zinc-800/70 bg-zinc-950
          transition-transform duration-300 lg:static lg:translate-x-0
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Brand */}
        <div className="flex h-16 items-center gap-3 border-b border-zinc-800/70 px-5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-500 to-teal-600">
            <span className="text-sm font-black text-white">f</span>
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tight">flujo</h1>
            <p className="text-[10px] text-zinc-500">hub operativo</p>
          </div>
          <button onClick={() => setSidebarOpen(false)} className="ml-auto rounded-lg p-1 text-zinc-500 hover:text-zinc-300 lg:hidden">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Mode Selector */}
        <div className="border-b border-zinc-800/70 px-3 py-3">
          <div className="text-[10px] font-bold uppercase tracking-widest text-zinc-600 mb-2 px-2">Workspace</div>
          <div className="flex gap-1.5">
            <button
              onClick={() => switchMode('rd')}
              className={`flex flex-1 items-center justify-center gap-1.5 rounded-lg px-2 py-2 text-[11px] font-bold transition-all ${
                mode === 'rd'
                  ? 'bg-emerald-900/50 text-emerald-300 border border-emerald-700/50 shadow-sm shadow-emerald-900/30'
                  : 'text-zinc-500 hover:bg-zinc-800/50 hover:text-zinc-300 border border-transparent'
              }`}
            >
              <Heart className="h-3.5 w-3.5" />
              Modo RD
            </button>
            <button
              onClick={() => switchMode('studio')}
              className={`flex flex-1 items-center justify-center gap-1.5 rounded-lg px-2 py-2 text-[11px] font-bold transition-all ${
                mode === 'studio'
                  ? 'bg-violet-900/50 text-violet-300 border border-violet-700/50 shadow-sm shadow-violet-900/30'
                  : 'text-zinc-500 hover:bg-zinc-800/50 hover:text-zinc-300 border border-transparent'
              }`}
            >
              <Music className="h-3.5 w-3.5" />
              Studio
            </button>
            <button
              onClick={() => switchMode('cultura')}
              className={`flex flex-1 items-center justify-center gap-1.5 rounded-lg px-2 py-2 text-[11px] font-bold transition-all ${
                mode === 'cultura'
                  ? 'bg-amber-900/50 text-amber-300 border border-amber-700/50 shadow-sm shadow-amber-900/30'
                  : 'text-zinc-500 hover:bg-zinc-800/50 hover:text-zinc-300 border border-transparent'
              }`}
            >
              <Layers className="h-3.5 w-3.5" />
              Cultura
            </button>
          </div>
          <div className="mt-2 px-2 text-[9px] text-zinc-600 leading-relaxed">
            {mode === 'rd'
              ? 'ONG Reduciendo Dano: Suplementos, Cotizaciones, Plano/Rider, SVG Studio.'
              : mode === 'studio'
                ? 'VJ & Club: Comandos, Eventos/IG, SVG Studio eventos, Resolume/Chataigne.'
                : 'Arte-investigacion: tapiz, tilde, psicosis, precursor. Instrumento -> material -> pieza.'}
          </div>
        </div>

        {/* Nav: editables primero, consulta despues */}
        <nav className="flex-1 overflow-y-auto px-3 py-4">
          {[
            { title: mode === 'rd' ? 'Edicion RD' : mode === 'studio' ? 'Edicion Studio' : 'Cultura', items: navItems.filter(i => i.view === 'hub' || i.edit) },
            { title: 'Consulta / referencia', items: navItems.filter(i => i.view !== 'hub' && !i.edit) },
          ].map(section => section.items.length > 0 && (
            <div key={section.title} className="mb-4">
              <div className="mb-2 px-2 text-[10px] font-bold uppercase tracking-widest text-zinc-600">
                {section.title}
              </div>
              {section.items.map(item => {
                const Icon = item.icon;
                const active = view === item.view;
                const accentColor = mode === 'rd' ? 'text-emerald-400' : mode === 'studio' ? 'text-violet-400' : 'text-amber-400';
                return (
                  <button
                    key={item.view}
                    onClick={() => { onViewChange(item.view); setSidebarOpen(false); }}
                    className={`
                      group mb-0.5 flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left transition-all
                      ${active
                        ? 'bg-zinc-800/80 text-white shadow-sm'
                        : 'text-zinc-400 hover:bg-zinc-800/40 hover:text-zinc-200'}
                    `}
                  >
                    <Icon className={`h-4 w-4 shrink-0 ${active ? accentColor : 'text-zinc-500 group-hover:text-zinc-400'}`} />
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-1.5 text-sm font-medium">
                        {item.label}
                        {item.edit && (
                          <span className={`rounded px-1 py-px text-[8px] font-bold uppercase tracking-wider ${
                            mode === 'rd' ? 'bg-emerald-900/60 text-emerald-400' : mode === 'studio' ? 'bg-violet-900/60 text-violet-400' : 'bg-amber-900/60 text-amber-400'
                          }`}>edit</span>
                        )}
                      </div>
                      <div className="truncate text-[10px] text-zinc-600">{item.desc}</div>
                    </div>
                    {active && <ChevronRight className="h-3 w-3 text-zinc-600" />}
                  </button>
                );
              })}
            </div>
          ))}
        </nav>

        {/* Footer */}
        <div className="border-t border-zinc-800/70 px-5 py-3">
          <div className="flex items-center gap-2">
            {mode === 'rd'
              ? <Heart className="h-3 w-3 text-emerald-500" />
              : mode === 'studio'
                ? <Cpu className="h-3 w-3 text-violet-500" />
                : <Layers className="h-3 w-3 text-amber-500" />
            }
            <span className="text-[10px] text-zinc-600">
              {mode === 'rd' ? 'Reduciendo Dano' : mode === 'studio' ? 'Studio / Personal' : 'Cultura / Arte'}
            </span>
          </div>
          <div className="text-[10px] text-zinc-600 mt-1">
            v0.49.0 | gratis/local
          </div>
          <div className="text-[10px] text-zinc-700">
            py -m flujo app
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Mobile header */}
        <header className="flex h-14 items-center gap-3 border-b border-zinc-800/70 px-4 lg:hidden">
          <button onClick={() => setSidebarOpen(true)} className="rounded-lg p-1.5 text-zinc-400 hover:text-zinc-200">
            <Menu className="h-5 w-5" />
          </button>
          <div className="flex items-center gap-2">
            {mode === 'rd'
              ? <span className="rounded-md bg-emerald-900/50 px-1.5 py-0.5 text-[9px] font-bold text-emerald-300">RD</span>
              : mode === 'studio'
                ? <span className="rounded-md bg-violet-900/50 px-1.5 py-0.5 text-[9px] font-bold text-violet-300">STUDIO</span>
                : <span className="rounded-md bg-amber-900/50 px-1.5 py-0.5 text-[9px] font-bold text-amber-300">CULTURA</span>
            }
            <span className="text-sm font-bold">{currentLabel}</span>
          </div>
        </header>

        {/* Scrollable content */}
        <main className="flex-1 overflow-y-auto">
          <div className="mx-auto w-full max-w-[1600px] p-4 md:p-6 lg:p-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
