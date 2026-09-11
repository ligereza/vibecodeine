import { StrictMode, type ReactNode, useState } from 'react';
import { Activity, Camera, Clapperboard, ExternalLink, Layers, Lightbulb, Radio, Shapes } from 'lucide-react';
import { createRoot } from 'react-dom/client';
import './index.css';
import FohPanel from './components/FohPanel';
import ShowPanel from './components/ShowPanel';
import MappingTool from './components/MappingTool';
import ResolumePanel from './components/ResolumePanel';
import EventsPanel from './components/EventsPanel';
import SvgVisualizer from './components/SvgVisualizer';
import PortafolioPanel from './components/PortafolioPanel';
import CulturaPanel from './components/CulturaPanel';

type Vista = 'foh' | 'show' | 'mapping' | 'resolume' | 'events' | 'visualizer' | 'portafolio' | 'cultura';
const VISTAS: Array<{ id: Vista; nombre: string; icon: typeof Radio; descripcion: string }> = [
  { id: 'foh', nombre: 'FOH', icon: Radio, descripcion: 'Monitor de señales y contexto del show' },
  { id: 'show', nombre: 'Show kit', icon: Clapperboard, descripcion: 'Setlist, cues y registro del show' },
  { id: 'mapping', nombre: 'Mapping LED', icon: Lightbulb, descripcion: 'Rigging y pixel mapping' },
  { id: 'resolume', nombre: 'Resolume / Chataigne', icon: Activity, descripcion: 'Pre-flight SMPTE/OSC' },
  { id: 'events', nombre: 'Eventos / IG', icon: Camera, descripcion: 'Referencia de eventos' },
  { id: 'visualizer', nombre: 'SVG Studio', icon: Shapes, descripcion: 'Galería y editor visual' },
  { id: 'portafolio', nombre: 'Portafolio', icon: Layers, descripcion: 'Catálogo público' },
  { id: 'cultura', nombre: 'Cultura', icon: Layers, descripcion: 'Líneas de obra' },
];

function VistaActual({ vista }: { vista: Vista }): ReactNode {
  if (vista === 'foh') return <FohPanel />;
  if (vista === 'show') return <ShowPanel />;
  if (vista === 'mapping') return <MappingTool />;
  if (vista === 'resolume') return <ResolumePanel />;
  if (vista === 'events') return <EventsPanel />;
  if (vista === 'visualizer') return <SvgVisualizer />;
  if (vista === 'portafolio') return <PortafolioPanel />;
  return <CulturaPanel />;
}

function IskvwHub() {
  const [vista, setVista] = useState<Vista>('foh');
  const actual = VISTAS.find(item => item.id === vista)!;
  return <div className="min-h-screen bg-zinc-950 text-zinc-200">
    <header className="sticky top-0 z-20 border-b border-zinc-900 bg-zinc-950/95">
      <div className="mx-auto flex max-w-[1600px] flex-wrap items-center gap-4 px-4 py-3 md:px-6">
        <div className="mr-2 min-w-[150px]"><p className="text-[10px] font-bold uppercase tracking-widest text-violet-400">FLUJO / ISKVW</p><h1 className="text-sm font-bold tracking-wide text-zinc-100">Hub VJ operativo</h1><p className="text-[11px] text-zinc-600">Sólo herramientas ISKVW y FOH</p></div>
        <nav className="flex min-w-0 flex-1 gap-1.5 overflow-x-auto pb-1" aria-label="Herramientas ISKVW">
          {VISTAS.map(item => { const Icon = item.icon; return <button key={item.id} type="button" title={item.descripcion} onClick={() => setVista(item.id)} className={`flex shrink-0 items-center gap-1.5 rounded-lg border px-3 py-2 text-xs font-bold transition-colors ${vista === item.id ? 'border-violet-800 bg-violet-950/50 text-violet-300' : 'border-zinc-800 bg-zinc-900 text-zinc-500 hover:text-zinc-200'}`}><Icon className="h-3.5 w-3.5" />{item.nombre}</button>; })}
        </nav>
        <a href="/api/plugins/foh_monitor/context" className="hidden items-center gap-1 text-[10px] text-zinc-600 hover:text-violet-300 sm:flex">evento FOH <ExternalLink className="h-3 w-3" /></a>
      </div>
    </header>
    <div className="mx-auto max-w-[1600px] px-4 pt-4 text-xs text-zinc-500 md:px-6">{actual.descripcion}</div>
    <main className="mx-auto max-w-[1600px] px-4 py-4 md:px-6"><VistaActual vista={vista} /></main>
  </div>;
}

createRoot(document.getElementById('root')!).render(<StrictMode><IskvwHub /></StrictMode>);
