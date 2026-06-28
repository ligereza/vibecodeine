import { useMemo, useState } from 'react';
import { Map, Shapes } from 'lucide-react';
import PlanoTool from './components/PlanoTool';
import SvgVisualizer from './components/SvgVisualizer';
import { cn } from './utils/cn';

type View = 'plano' | 'visualizer';

function initialView(): View {
  if (typeof window !== 'undefined' && window.location.pathname.toLowerCase().includes('svg')) {
    return 'visualizer';
  }
  return 'plano';
}

export default function App() {
  const [view, setView] = useState<View>(initialView);
  const title = useMemo(() => view === 'plano' ? 'Plano / Rider RD' : 'Visualizador SVG', [view]);

  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-100 font-sans">
      <header className="sticky top-0 z-50 border-b border-zinc-800 bg-[#09090b]/90 backdrop-blur-xl">
        <div className="mx-auto flex min-h-14 max-w-[1500px] flex-wrap items-center justify-between gap-3 px-6 py-2">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded bg-white text-lg font-black italic text-black">F</div>
            <div>
              <div className="text-sm font-bold tracking-tight">flujo</div>
              <div className="text-[10px] uppercase tracking-[0.22em] text-zinc-500">{title}</div>
            </div>
          </div>

          <nav className="flex items-center gap-2 rounded-xl border border-zinc-800 bg-zinc-950/70 p-1">
            <button
              onClick={() => setView('plano')}
              className={cn(
                'flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-semibold transition-colors',
                view === 'plano' ? 'bg-white text-black' : 'text-zinc-500 hover:bg-zinc-900 hover:text-zinc-200'
              )}
            >
              <Map className="h-4 w-4" />
              Plano
            </button>
            <button
              onClick={() => setView('visualizer')}
              className={cn(
                'flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-semibold transition-colors',
                view === 'visualizer' ? 'bg-white text-black' : 'text-zinc-500 hover:bg-zinc-900 hover:text-zinc-200'
              )}
            >
              <Shapes className="h-4 w-4" />
              SVG Visualizer
            </button>
          </nav>

          <div className="flex items-center gap-3 text-[10px] font-mono uppercase tracking-widest text-zinc-500">
            <span className="h-1.5 w-1.5 rounded-full bg-green-500 shadow-[0_0_10px_rgba(34,197,94,.8)]" />
            <span>local-first</span>
            <span className="hidden sm:inline">v0.40.4</span>
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-[1500px] p-6">
        {view === 'plano' ? <PlanoTool /> : <SvgVisualizer />}
      </main>
    </div>
  );
}
