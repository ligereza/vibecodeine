import { useState } from 'react';
import { Calculator, Plus, Trash2, Settings } from 'lucide-react';
import { cn } from '../utils/cn';

type Preset = 'under' | 'base' | 'mainstream';

interface ManualItem {
  id: string;
  label: string;
  qty: number;
  price: number;
}

export default function QuotePanel() {
  const [view, setView] = useState<'quote' | 'config'>('quote');
  const [preset, setPreset] = useState<Preset>('base');
  const [eventName, setEventName] = useState('Evento RD');
  const [manualItems, setManualItems] = useState<ManualItem[]>([]);

  // Configuración de precios (Persistente)
  const [prices, setProposalPrices] = useState({
    under: 250000,
    base: 450000,
    mainstream: 850000,
    voluntario: 35000,
    reactivos: 120000,
    fee_gestion: 15
  });

  const basePrice = prices[preset];
  const manualTotal = manualItems.reduce((sum, it) => sum + (it.qty * it.price), 0);
  const grandTotal = basePrice + manualTotal;

  const addManualItem = () => {
    setManualItems([...manualItems, { id: Date.now().toString(), label: "Nuevo Item", qty: 1, price: 0 }]);
  };

  const removeManualItem = (id: string) => {
    setManualItems(manualItems.filter(it => it.id !== id));
  };

  const copyToClipboard = () => {
    const text = `COTIZACIÓN: ${eventName.toUpperCase()}\n` +
                 `Preset: ${preset.toUpperCase()}\n` +
                 `---------------------------\n` +
                 `Base Operativa: $${basePrice.toLocaleString('es-CL')}\n` +
                 manualItems.map(it => `${it.label} (x${it.qty}): $${(it.qty * it.price).toLocaleString('es-CL')}`).join('\n') +
                 `\n---------------------------\n` +
                 `TOTAL: $${grandTotal.toLocaleString('es-CL')}\n` +
                 `Validez: 15 días. Sujeto a disponibilidad de equipo.`;
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="h-full flex flex-col bg-zinc-950 text-white selection:bg-emerald-500/30">
      <header className="p-6 border-b border-zinc-800 flex justify-between items-center bg-black/40 backdrop-blur-xl">
        <div className="flex items-center gap-4">
           <Calculator className="w-6 h-6 text-emerald-400" />
           <h2 className="text-xl font-black italic tracking-tighter uppercase">Cotización Pro RD</h2>
        </div>
        <div className="flex gap-2">
           <button onClick={() => setView(view === 'quote' ? 'config' : 'quote')} className="p-2 bg-zinc-900 border border-zinc-800 rounded-xl hover:bg-zinc-800"><Settings className="w-5 h-5"/></button>
           <button onClick={copyToClipboard} className="bg-emerald-500 text-black px-6 py-2 rounded-xl font-black text-xs uppercase tracking-widest hover:bg-emerald-400 transition-all">Copiar Cotización</button>
        </div>
      </header>

      <div className="flex-1 overflow-hidden flex">
        {view === 'quote' ? (
          <>
            <aside className="w-80 border-r border-zinc-800 p-8 space-y-8 bg-zinc-900/20 overflow-y-auto">
               <div className="space-y-4">
                  <label className="text-[10px] font-black uppercase text-zinc-500 tracking-widest">Nombre del Evento</label>
                  <input value={eventName} onChange={e => setEventName(e.target.value)} className="w-full bg-black border border-zinc-800 p-4 rounded-2xl text-sm font-bold focus:border-emerald-500 outline-none transition-all" />
               </div>

               <div className="space-y-4">
                  <label className="text-[10px] font-black uppercase text-zinc-500 tracking-widest">Seleccionar Preset</label>
                  <div className="space-y-2">
                     {(['under', 'base', 'mainstream'] as const).map(p => (
                       <button key={p} onClick={() => setPreset(p)} className={cn("w-full p-4 rounded-2xl border-2 text-left transition-all", preset===p ? "bg-emerald-500 border-emerald-400 text-black shadow-lg shadow-emerald-500/20" : "bg-black/20 border-zinc-800 text-zinc-500 hover:border-zinc-700")}>
                          <div className="font-black uppercase text-xs">{p}</div>
                          <div className={cn("text-[10px] mt-1 font-bold", preset===p ? "text-black/60" : "text-zinc-600")}>$ {prices[p].toLocaleString('es-CL')} base</div>
                       </button>
                     ))}
                  </div>
               </div>
            </aside>

            <main className="flex-1 p-12 overflow-y-auto space-y-12">
               <section>
                  <div className="flex justify-between items-center mb-8">
                     <h3 className="text-2xl font-black tracking-tighter">Items Adicionales / Logística</h3>
                     <button onClick={addManualItem} className="p-3 bg-zinc-800 rounded-2xl hover:bg-zinc-700 transition-all text-emerald-400"><Plus className="w-6 h-6"/></button>
                  </div>
                  
                  <div className="space-y-3">
                     {manualItems.map(it => (
                       <div key={it.id} className="flex gap-4 items-center bg-zinc-900/40 p-4 rounded-3xl border border-zinc-800 group">
                          <input value={it.label} onChange={e => setManualItems(manualItems.map(x => x.id===it.id ? {...x, label:e.target.value} : x))} className="flex-1 bg-transparent border-none outline-none font-bold text-sm" placeholder="Descripción del servicio..." />
                          <div className="flex items-center bg-black/40 rounded-xl px-4 py-2 border border-zinc-800">
                             <span className="text-[10px] font-black text-zinc-600 mr-3">QTY</span>
                             <input type="number" value={it.qty} onChange={e => setManualItems(manualItems.map(x => x.id===it.id ? {...x, qty: Number(e.target.value)} : x))} className="w-12 bg-transparent text-center font-mono text-sm font-bold outline-none" />
                          </div>
                          <div className="flex items-center bg-black/40 rounded-xl px-4 py-2 border border-zinc-800">
                             <span className="text-[10px] font-black text-zinc-600 mr-3">$</span>
                             <input type="number" value={it.price} onChange={e => setManualItems(manualItems.map(x => x.id===it.id ? {...x, price: Number(e.target.value)} : x))} className="w-24 bg-transparent text-right font-mono text-sm font-bold outline-none" />
                          </div>
                          <button onClick={() => removeManualItem(it.id)} className="text-zinc-700 hover:text-red-500 transition-colors"><Trash2 className="w-5 h-5"/></button>
                       </div>
                     ))}
                     {manualItems.length === 0 && (
                        <div className="p-20 text-center border-2 border-dashed border-zinc-800 rounded-[3rem]">
                           <p className="text-zinc-600 font-bold uppercase tracking-widest text-[10px]">No hay items manuales registrados</p>
                        </div>
                     )}
                  </div>
               </section>

               <section className="bg-emerald-500 rounded-[3rem] p-12 text-black shadow-2xl shadow-emerald-500/20">
                  <div className="flex justify-between items-end">
                     <div>
                        <p className="text-[10px] font-black uppercase tracking-[0.3em] opacity-60 mb-2">Total Estimado</p>
                        <h4 className="text-6xl font-black tracking-tighter">$ {grandTotal.toLocaleString('es-CL')}</h4>
                     </div>
                     <div className="text-right">
                        <p className="text-xs font-bold opacity-60">Sujeto a confirmación técnica</p>
                        <p className="text-[10px] font-black uppercase mt-1 opacity-60">NGO Reduciendo Daño</p>
                     </div>
                  </div>
               </section>
            </main>
          </>
        ) : (
          <div className="flex-1 p-20 overflow-y-auto bg-black/40">
             <div className="max-w-3xl mx-auto space-y-12">
                <header>
                   <h2 className="text-4xl font-black tracking-tighter">Valores de Referencia</h2>
                   <p className="text-zinc-500 text-xs mt-2 uppercase tracking-widest font-mono">Lógica Comercial para NGO RD</p>
                </header>

                <div className="grid grid-cols-3 gap-6">
                   {['under', 'base', 'mainstream'].map(p => (
                     <div key={p} className="space-y-4">
                        <label className="text-[10px] font-black uppercase text-emerald-500">Preset {p}</label>
                        <input type="number" value={prices[p as Preset]} onChange={e => setProposalPrices({...prices, [p]: Number(e.target.value)})} className="w-full bg-zinc-900 border border-zinc-800 p-4 rounded-2xl text-sm font-mono font-bold" />
                     </div>
                   ))}
                </div>

                <div className="pt-12 border-t border-zinc-800">
                   <button onClick={() => setView('quote')} className="w-full py-5 bg-zinc-800 rounded-3xl font-black text-xs uppercase tracking-widest hover:bg-zinc-700 transition-all">Guardar Cambios y Volver</button>
                </div>
             </div>
          </div>
        )}
      </div>
    </div>
  );
}
