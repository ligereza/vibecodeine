import React, { useState, useRef } from "react";
import { 
  Download, LayersOff, 
  ChevronRight, Printer, Settings, Trash2, Copy, Zap, RefreshCw, Box, Droplet, ShieldAlert
} from "lucide-react";
import { cn } from "../utils/cn";

interface PlanoElement {
  id: string;
  type: "rect" | "circle" | "symbol";
  symbolType?: "power" | "heating" | "rack" | "extinguisher" | "water";
  x: number; y: number; width: number; height: number;
  label: string; color: string; rotation: number;
  locked: boolean; visible: boolean;
}

const ZONE_COLORS: Record<string, string> = {
  testeo: "#2d5a4a", contencion: "#7c3aed", informativo: "#0369a1",
  descanso: "#059669", coordinacion: "#ca8a04", circulacion: "#9ca3af",
  power: "#f59e0b", heating: "#ef4444", rack: "#4b5563", extinguisher: "#dc2626", water: "#2563eb"
};

const ZONE_LABELS: Record<string, string> = {
  testeo: "Stand de Testeo", contencion: "Contención", informativo: "Stand Informativo",
  descanso: "Zona Descanso", coordinacion: "Coordinación", circulacion: "Circulación",
  power: "Punto Eléctrico", heating: "Calefacción", rack: "Rack Almacén", extinguisher: "Extintor", water: "Punto de Agua"
};

const PROPOSAL_INFO = {
  who: "Fundada en 2018, Reduciendo Daño es una ONG líder en reducción de daños en Chile.",
  goal: "Informar, orientar y acompañar mediante estrategias enfocadas en la seguridad y el cuidado informado.",
  benefits: [
    "Disminución de conflictos y situaciones críticas.",
    "Contención en terreno que reduce carga sobre equipos médicos.",
    "Fortalecimiento de la imagen del evento como espacio responsable."
  ]
};

export default function PlanoTool() {
  const [page, setPage] = useState<"req" | "map" | "config">("req");
  const [elements, setElements] = useState<PlanoElement[]>([
    { id: "toldo", type: "rect", x: 150, y: 100, width: 500, height: 350, label: "Toldo RD", color: "#2d5a4a20", rotation: 0, locked: false, visible: true },
  ]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [dragging, setDragging] = useState<{ id: string; ox: number; oy: number } | null>(null);
  const [legendPos, setLegendPos] = useState({ x: 580, y: 40 });
  const [checkedItems, setCheckedItems] = useState<string[]>([]);
  
  const [proposal, setProposal] = useState({
    who: PROPOSAL_INFO.who,
    goal: PROPOSAL_INFO.goal,
    checklist: [
      { t: "Espacio", i: ["Superficie estable y nivelada", "Circulación pública segura", "Medidas del recinto"] },
      { t: "Infraestructura", i: ["Toldo / Carpa confirmado", "Mobiliario (Mesas/Sillas)", "Rack de almacenamiento"] },
      { t: "Condiciones", i: ["Punto eléctrico dedicado", "Calefacción / Iluminación", "Alimentación (>5h)"] }
    ]
  });

  const svgRef = useRef<SVGSVGElement>(null);
  const selectedElement = elements.find(e => e.id === selectedId);

  const onMouseDown = (e: React.MouseEvent, id: string) => {
    const el = elements.find(x => x.id === id);
    if (!el || el.locked) return;
    const svg = svgRef.current; if (!svg) return;
    const pt = svg.createSVGPoint(); pt.x = e.clientX; pt.y = e.clientY;
    const p = pt.matrixTransform(svg.getScreenCTM()?.inverse());
    setDragging({ id, ox: p.x - el.x, oy: p.y - el.y });
    setSelectedId(id);
    e.stopPropagation();
  };

  const onMouseMove = (e: React.MouseEvent) => {
    if (!dragging) return;
    const svg = svgRef.current; if (!svg) return;
    const pt = svg.createSVGPoint(); pt.x = e.clientX; pt.y = e.clientY;
    const p = pt.matrixTransform(svg.getScreenCTM()?.inverse());
    setElements(prev => prev.map(el => el.id === dragging.id ? { ...el, x: Math.round((p.x - dragging.ox)/10)*10, y: Math.round((p.y - dragging.oy)/10)*10 } : el));
  };

  const addSymbol = (st: PlanoElement["symbolType"]) => {
    const id = `s-${Date.now()}`;
    setElements([...elements, { id, type: "symbol", symbolType: st, x: 300, y: 300, width: 40, height: 40, label: ZONE_LABELS[st!], color: ZONE_COLORS[st!], rotation: 0, locked: false, visible: true }]);
    setSelectedId(id);
  };

  const moveLayer = (dir: "up" | "down") => {
    if (!selectedId) return;
    const i = elements.findIndex(e => e.id === selectedId);
    const target = dir === "up" ? i + 1 : i - 1;
    if (target < 0 || target >= elements.length) return;
    const next = [...elements];
    [next[i], next[target]] = [next[target], next[i]];
    setElements(next);
  };

  const renderSymbol = (el: PlanoElement, isPrint = false) => {
    const color = isPrint ? "#000" : el.color;
    return (
      <g key={el.id} transform={`translate(${el.x},${el.y})`} onMouseDown={(e) => onMouseDown(e, el.id)} className="cursor-move">
        <rect width={el.width} height={el.height} fill="transparent" stroke={el.id===selectedId ? "#3b82f6" : "none"} />
        {el.symbolType === "power" && (
          <g stroke={color} strokeWidth="2" fill="none">
            <circle cx="20" cy="20" r="12" />
            <path d="M20 12 L16 22 H24 L20 32" stroke={color} strokeWidth="2.5" />
          </g>
        )}
        {el.symbolType === "heating" && (
          <g stroke={color} strokeWidth="2" fill="none">
             <rect x="8" y="10" width="24" height="20" rx="2" />
             <path d="M14 14 V26 M20 14 V26 M26 14 V26" />
          </g>
        )}
        {el.symbolType === "rack" && (
           <g stroke={color} strokeWidth="2" fill="none">
              <rect x="5" y="5" width="30" height="30" />
              <path d="M5 15 H35 M5 25 H35 M15 5 V35 M25 5 V35" strokeOpacity="0.3" />
           </g>
        )}
        {el.symbolType === "extinguisher" && (
           <g fill={color}>
              <rect x="15" y="12" width="10" height="25" rx="2" />
              <path d="M17 12 V8 H23 V12 M23 15 H28" stroke={color} fill="none" strokeWidth="2" />
           </g>
        )}
        {el.symbolType === "water" && (
           <g stroke={color} strokeWidth="2" fill="none">
              <circle cx="20" cy="20" r="12" />
              <path d="M20 15 Q25 25 20 30 Q15 25 20 15" fill={color} />
           </g>
        )}
        <text x="20" y="55" textAnchor="middle" fontSize="8" fill={color} fontWeight="bold" fontFamily="monospace">{el.label.toUpperCase()}</text>
      </g>
    );
  };

  return (
    <div className="h-full flex flex-col bg-zinc-950 text-white" onMouseMove={onMouseMove} onMouseUp={() => setDragging(null)}>
      {/* Print Document */}
      <div className="hidden print:block p-16 text-black bg-white font-sans">
        <header className="border-b-8 border-black pb-6 mb-12 flex justify-between items-end">
          <div>
            <h1 className="text-5xl font-black italic tracking-tighter">RIDER TÉCNICO RD</h1>
            <p className="text-sm uppercase tracking-[0.3em] font-bold mt-2">Documentación de Intervención en Terreno</p>
          </div>
          <div className="text-right">
            <p className="text-xl font-bold">NGO REDUCIENDO DAÑO</p>
            <p className="text-sm opacity-60">Propuesta de Servicio v2026</p>
          </div>
        </header>

        <section className="mb-12">
           <h2 className="text-2xl font-black mb-4 uppercase tracking-tight">1. Antecedentes</h2>
           <div className="grid grid-cols-1 gap-6 text-sm leading-relaxed text-zinc-700">
              <p><strong>Quiénes Somos:</strong> {proposal.who}</p>
              <p><strong>Objetivo del Servicio:</strong> {proposal.goal}</p>
           </div>
        </section>

        <section className="mb-12">
           <h2 className="text-2xl font-black mb-4 uppercase tracking-tight">2. Requerimientos Técnicos</h2>
           <div className="grid grid-cols-2 gap-x-12 gap-y-6">
              {proposal.checklist.map(s => (
                <div key={s.t}>
                  <h3 className="font-bold text-xs uppercase mb-3 border-b border-zinc-300">{s.t}</h3>
                  <ul className="space-y-2">
                    {s.i.map(it => (
                      <li key={it} className="flex items-center gap-3 text-xs">
                        <div className={cn("w-4 h-4 border-2 border-black", checkedItems.includes(it) ? "bg-black" : "")} />
                        {it}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
           </div>
        </section>

        <div className="break-before-page" style={{ height: "40px" }} />

        <section className="h-full flex flex-col">
           <h2 className="text-2xl font-black mb-4 uppercase tracking-tight">3. Esquema de Distribución</h2>
           <div className="flex-1 border-2 border-black p-4 bg-zinc-50 relative">
              <p className="text-[10px] uppercase font-bold text-zinc-400 mb-4 tracking-widest">Visualización Técnica NGO RD</p>
              {/* Note: SVG Printing is handled by its natural inclusion in the DOM flow */}
           </div>
        </section>
      </div>

      {/* Screen Interface */}
      <header className="flex-shrink-0 p-4 border-b border-zinc-800 bg-black/50 backdrop-blur-xl flex justify-between items-center print:hidden">
        <div className="flex items-center gap-4">
          <div className="p-2 bg-emerald-500/20 rounded-xl"><Layers className="text-emerald-400 w-6 h-6"/></div>
          <h1 className="font-black italic uppercase text-lg tracking-tighter text-emerald-400">Plano Pro <span className="text-white opacity-40 font-light">RD</span></h1>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setPage("config")} className="p-2 bg-zinc-900 border border-zinc-800 rounded-lg hover:bg-zinc-800 transition-colors"><Settings className="w-4 h-4"/></button>
          <button onClick={() => window.print()} className="flex items-center gap-2 px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-xs font-bold hover:bg-zinc-700"><Printer className="w-4 h-4"/> Imprimir Rider</button>
          <button className="flex items-center gap-2 px-6 py-2 bg-white text-black rounded-lg text-xs font-black hover:bg-zinc-200 transition-transform active:scale-95"><Download className="w-4 h-4"/> Exportar</button>
        </div>
      </header>

      {/* Main Nav */}
      <nav className="flex-shrink-0 px-8 border-b border-zinc-800 bg-zinc-900/20 print:hidden flex gap-8">
         {(["req", "map", "config"] as const).map(n => (
           <button key={n} onClick={() => setPage(n)} className={cn("py-4 text-[10px] font-black uppercase tracking-[0.2em] border-b-2 transition-all", page===n ? "border-emerald-500 text-emerald-400" : "border-transparent text-zinc-500 hover:text-white")}>
             {n === "req" ? "1. Requerimientos" : n === "map" ? "2. Distribución" : "Ajustes"}
           </button>
         ))}
      </nav>

      {/* Content Area */}
      <div className="flex-1 flex overflow-hidden print:hidden">
        {page === "req" && (
          <div className="flex-1 overflow-y-auto p-12">
             <div className="max-w-4xl mx-auto space-y-12">
                <header>
                   <h2 className="text-4xl font-black tracking-tighter">Checklist Operativo</h2>
                   <p className="text-zinc-500 font-mono text-xs mt-2 uppercase tracking-widest">Validación NGO Reduciendo Daño</p>
                </header>
                <div className="grid grid-cols-2 gap-8">
                   {proposal.checklist.map(s => (
                     <div key={s.t} className="p-8 bg-zinc-900/40 border border-zinc-800 rounded-3xl group hover:border-emerald-500/30 transition-all">
                        <h4 className="text-[10px] font-black text-emerald-500/60 uppercase mb-6 tracking-widest">{s.t}</h4>
                        <div className="space-y-4">
                           {s.i.map(it => (
                             <label key={it} className="flex items-center gap-4 cursor-pointer group/item">
                                <input type="checkbox" checked={checkedItems.includes(it)} onChange={() => setCheckedItems(prev => prev.includes(it) ? prev.filter(x => x!==it) : [...prev, it])} className="hidden" />
                                <div className={cn("w-6 h-6 border-2 rounded-lg flex items-center justify-center transition-all shadow-lg", checkedItems.includes(it) ? "bg-emerald-500 border-emerald-500 rotate-0" : "border-zinc-700 group-hover/item:border-zinc-500 rotate-3")} >
                                   {checkedItems.includes(it) && <Zap className="w-3.5 h-3.6 text-black" fill="currentColor"/>}
                                </div>
                                <span className={cn("text-sm transition-colors", checkedItems.includes(it) ? "text-white font-bold" : "text-zinc-500 group-hover/item:text-zinc-300")}>{it}</span>
                             </label>
                           ))}
                        </div>
                     </div>
                   ))}
                </div>
                <button onClick={() => setPage("map")} className="w-full py-5 bg-emerald-500 text-black font-black rounded-3xl shadow-xl shadow-emerald-500/10 hover:bg-emerald-400 transition-all flex items-center justify-center gap-4 text-lg active:scale-[0.98]">Ir al Plano de Distribución <ChevronRight className="w-6 h-6"/></button>
             </div>
          </div>
        )}

        {page === "map" && (
          <>
            <aside className="w-72 border-r border-zinc-800 p-6 space-y-8 bg-zinc-900/40 overflow-y-auto">
               <div>
                  <h4 className="text-[10px] font-black text-zinc-500 uppercase mb-4 tracking-widest">Zonas de Montaje</h4>
                  <div className="grid grid-cols-2 gap-2">
                     {["testeo","contencion","informativo","descanso"].map(k => (
                       <button key={k} onClick={() => {
                          const id = `z-${Date.now()}`;
                          setElements([...elements, { id, type:"rect", x:250, y:250, width:180, height:90, label:ZONE_LABELS[k], color:ZONE_COLORS[k], rotation:0, locked:false, visible:true }]);
                          setSelectedId(id);
                       }} className="p-3 bg-zinc-900 border border-zinc-800 rounded-xl text-[10px] font-bold flex items-center gap-3 hover:bg-zinc-800 transition-all">
                          <div className="w-3 h-3 rounded-full" style={{background:ZONE_COLORS[k]}}/> {k}
                       </button>
                     ))}
                  </div>
               </div>

               <div>
                  <h4 className="text-[10px] font-black text-zinc-500 uppercase mb-4 tracking-widest">Símbolos Técnicos</h4>
                  <div className="grid grid-cols-3 gap-2">
                     {(["power","heating","rack","extinguisher","water"] as const).map(s => (
                       <button key={s} onClick={() => addSymbol(s)} className="flex flex-col items-center p-3 bg-zinc-900 border border-zinc-800 rounded-xl hover:bg-zinc-800 group transition-all">
                          {s==="power" && <Zap className="w-4 h-4 text-yellow-500"/>}
                          {s==="heating" && <RefreshCw className="w-4 h-4 text-red-500"/>}
                          {s==="rack" && <Box className="w-4 h-4 text-zinc-400"/>}
                          {s==="extinguisher" && <ShieldAlert className="w-4 h-4 text-red-600"/>}
                          {s==="water" && <Droplet className="w-4 h-4 text-blue-500"/>}
                          <span className="mt-2 text-[7px] uppercase font-black opacity-40 group-hover:opacity-100">{s}</span>
                       </button>
                     ))}
                  </div>
               </div>

               {selectedElement && (
                 <div className="p-5 bg-zinc-900 border border-zinc-800 rounded-3xl space-y-5 shadow-2xl">
                    <h4 className="text-[10px] font-black text-emerald-500 uppercase tracking-widest">Propiedades</h4>
                    <input value={selectedElement.label} onChange={e => setElements(prev => prev.map(el => el.id===selectedId ? {...el, label:e.target.value} : el))} className="w-full bg-black border border-zinc-800 p-3 rounded-xl text-xs font-bold outline-none focus:border-emerald-500 transition-colors" />
                    <div className="flex gap-1.5 flex-wrap">
                       {Object.values(ZONE_COLORS).map(c => (
                         <button key={c} onClick={() => setElements(prev => prev.map(el => el.id===selectedId ? {...el, color:c} : el))} className={cn("w-6 h-6 rounded-full border-2 transition-all", selectedElement.color===c ? "border-white scale-125" : "border-transparent hover:scale-110")} style={{background:c}} />
                       ))}
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                       <button onClick={() => moveLayer("up")} className="p-3 bg-zinc-800 rounded-xl text-[9px] font-black uppercase flex items-center justify-center gap-2 hover:bg-zinc-700 transition-colors"><Layers className="w-3 h-3"/> Subir</button>
                       <button onClick={() => moveLayer("down")} className="p-3 bg-zinc-800 rounded-xl text-[9px] font-black uppercase flex items-center justify-center gap-2 hover:bg-zinc-700 transition-colors"><Layers className="w-3 h-3"/> Bajar</button>
                    </div>
                    <div className="flex gap-2">
                       <button onClick={() => {
                          const id = `dup-${Date.now()}`;
                          const i = elements.findIndex(e => e.id === selectedId);
                          const next = [...elements];
                          next.splice(i+1, 0, {...selectedElement, id, x:selectedElement.x+20, y:selectedElement.y+20});
                          setElements(next); setSelectedId(id);
                       }} className="flex-1 p-3 bg-zinc-800 rounded-xl text-[9px] font-black uppercase hover:bg-zinc-700"><Copy className="w-3 h-3 mx-auto" /></button>
                       <button onClick={() => { setElements(prev => prev.filter(x => x.id!==selectedId)); setSelectedId(null); }} className="flex-1 p-3 bg-red-900/20 text-red-400 rounded-xl text-[9px] font-black uppercase hover:bg-red-900/40 transition-colors"><Trash2 className="w-3 h-3 mx-auto" /></button>
                    </div>
                 </div>
               )}
            </aside>

            <main className="flex-1 flex items-center justify-center bg-zinc-950 overflow-hidden relative">
               <div className="relative bg-white shadow-[0_0_100px_rgba(0,0,0,0.5)] transition-all" style={{width:800, height:600}}>
                  <svg ref={svgRef} viewBox="0 0 800 600" className="w-full h-full">
                     <defs><pattern id="technogrid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0 L0 0 0 40" fill="none" stroke="#f0f0f0" strokeWidth="1"/></pattern></defs>
                     <rect width="100%" height="100%" fill="url(#technogrid)" />
                     
                     {elements.filter(el => el.visible).map(el => {
                       if (el.type === "symbol") return renderSymbol(el);
                       const isSelected = el.id === selectedId;
                       const common = { onMouseDown: (e:any) => onMouseDown(e, el.id), className: cn("cursor-move transition-opacity", isSelected && "outline-[3px] outline-emerald-500") };
                       if (el.type === "rect") return <rect key={el.id} x={el.x} y={el.y} width={el.width} height={el.height} fill={el.color} {...common} fillOpacity="0.9" rx="4" />;
                       return null;
                     })}

                     {/* Legend (Movable) */}
                     <g transform={`translate(${legendPos.x},${legendPos.y})`} onMouseDown={(e) => {
                        const svg = svgRef.current; if (!svg) return;
                        const pt = svg.createSVGPoint(); pt.x = e.clientX; pt.y = e.clientY;
                        const p = pt.matrixTransform(svg.getScreenCTM()?.inverse());
                        const startX = p.x; const startY = p.y;
                        const lx = legendPos.x; const ly = legendPos.y;
                        const move = (me:any) => {
                           const mpt = svg.createSVGPoint(); mpt.x = me.clientX; mpt.y = me.clientY;
                           const mp = mpt.matrixTransform(svg.getScreenCTM()?.inverse());
                           setLegendPos({ x: lx + (mp.x - startX), y: ly + (mp.y - startY) });
                        };
                        const up = () => { window.removeEventListener("mousemove", move); window.removeEventListener("mouseup", up); };
                        window.addEventListener("mousemove", move); window.addEventListener("mouseup", up);
                        e.stopPropagation();
                     }} className="cursor-grab active:cursor-grabbing">
                        <rect width="180" height={180} fill="white" fillOpacity="0.95" stroke="#161513" strokeWidth="1.5" rx="16" />
                        <text x="15" y="28" fontSize="10" fontWeight="black" fill="#161513" fontFamily="monospace" tracking="0.1em">LEYENDA TÉCNICA</text>
                        {['testeo','contencion','power','heating','extinguisher'].map((k,i) => (
                          <g key={k} transform={`translate(15, ${50+i*24})`}>
                             {['power','heating','extinguisher'].includes(k) ? (
                                <g transform="scale(0.4)">
                                   {k==='power' && <Zap className="w-8 h-8" fill={ZONE_COLORS[k]}/>}
                                   {k==='heating' && <RefreshCw className="w-8 h-8" stroke={ZONE_COLORS[k]} strokeWidth="4"/>}
                                   {k==='extinguisher' && <ShieldAlert className="w-8 h-8" fill={ZONE_COLORS[k]}/>}
                                </g>
                             ) : (
                                <rect width="12" height="12" fill={ZONE_COLORS[k]} rx="3" />
                             )}
                             <text x="24" y="10" fontSize="9" fill="#161513" fontWeight="bold" fontFamily="Inter">{ZONE_LABELS[k]}</text>
                          </g>
                        ))}
                     </g>
                  </svg>
               </div>
            </main>
          </>
        )}

        {page === "config" && (
          <div className="flex-1 overflow-y-auto p-12 bg-black/40">
             <div className="max-w-3xl mx-auto space-y-12">
                <header>
                   <h2 className="text-4xl font-black tracking-tighter">Configuración NGO RD</h2>
                   <p className="text-zinc-500 text-xs mt-2 uppercase tracking-widest font-mono">Memoria Operativa para Rider Técnico</p>
                </header>
                
                <section className="space-y-8">
                   <div className="space-y-4">
                      <label className="text-[10px] font-black uppercase text-emerald-500 tracking-[0.2em]">Quiénes Somos</label>
                      <textarea value={proposal.who} onChange={e => setProposal({...proposal, who: e.target.value})} className="w-full bg-zinc-900 border border-zinc-800 p-6 rounded-3xl text-sm min-h-[120px] outline-none focus:border-emerald-500 transition-colors leading-relaxed shadow-inner" />
                   </div>
                   <div className="space-y-4">
                      <label className="text-[10px] font-black uppercase text-emerald-500 tracking-[0.2em]">Objetivo del Servicio</label>
                      <textarea value={proposal.goal} onChange={e => setProposal({...proposal, goal: e.target.value})} className="w-full bg-zinc-900 border border-zinc-800 p-6 rounded-3xl text-sm min-h-[120px] outline-none focus:border-emerald-500 transition-colors leading-relaxed shadow-inner" />
                   </div>
                </section>

                <div className="p-10 bg-zinc-900/50 border border-dashed border-zinc-800 rounded-[3rem] text-center">
                   <p className="text-zinc-400 text-xs italic leading-relaxed">Los cambios en esta sección se reflejan en tiempo real en la vista de impresión del Rider Técnico.</p>
                </div>
                
                <button onClick={() => setPage("req")} className="w-full py-5 bg-zinc-800 rounded-3xl font-black text-xs uppercase tracking-widest hover:bg-zinc-700 transition-all active:scale-[0.99]">Guardar Ajustes y Volver</button>
             </div>
          </div>
        )}
      </div>
    </div>
  );
}


