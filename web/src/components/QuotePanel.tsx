import { useState } from 'react';
import { Calculator, Copy, Loader2 } from 'lucide-react';

type Preset = 'under' | 'base' | 'mainstream';

type QuoteResult = {
  total_clp?: string;
  markdown?: string;
  items?: Array<{ code: string; label: string; qty: number; subtotal: number; notes?: string }>;
  error?: string;
};

const presets: Array<{ id: Preset; label: string; hint: string }> = [
  { id: 'under', label: 'UNDER', hint: '2 voluntarios · 1 mesa' },
  { id: 'base', label: 'BASE', hint: '4 voluntarios · testeo' },
  { id: 'mainstream', label: 'MAINSTREAM', hint: '8 voluntarios · alto flujo' },
];

export default function QuotePanel() {
  const [preset, setPreset] = useState<Preset>('mainstream');
  const [name, setName] = useState('Demo jefe - evento mainstream');
  const [cartelera, setCartelera] = useState(true);
  const [flyer, setFlyer] = useState(false);
  const [result, setResult] = useState<QuoteResult | null>(null);
  const [busy, setBusy] = useState(false);

  const render = async () => {
    setBusy(true);
    try {
      if (window.location.protocol === 'file:') {
        setResult({ error: 'Abre con py -m flujo app para calcular con backend local.' });
        return;
      }
      const response = await fetch('/api/cotizacion/render', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ evento: { nombre: name, preset }, incluir_cartelera: cartelera, incluir_flyer_impreso: flyer }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      setResult(await response.json());
    } catch (error) {
      setResult({ error: error instanceof Error ? error.message : String(error) });
    } finally {
      setBusy(false);
    }
  };

  const copy = async () => {
    if (result?.markdown) await navigator.clipboard?.writeText(result.markdown);
  };

  return (
    <div className="grid gap-5 xl:grid-cols-[420px_1fr]">
      <section className="rounded-2xl border border-zinc-800 bg-zinc-900/45 p-5">
        <h1 className="flex items-center gap-2 text-2xl font-black"><Calculator className="h-6 w-6" /> Cotización base</h1>
        <p className="mt-2 text-sm leading-6 text-zinc-500">Base referencial para conversar con jefatura/productora. No reemplaza revisión final de precios.</p>

        <label className="mt-5 block text-[10px] font-bold uppercase tracking-widest text-zinc-500">Nombre</label>
        <input value={name} onChange={e => setName(e.target.value)} className="mt-2 w-full rounded-xl border border-zinc-800 bg-black/40 px-4 py-3 text-sm outline-none focus:border-zinc-600" />

        <div className="mt-5 text-[10px] font-bold uppercase tracking-widest text-zinc-500">Preset evento</div>
        <div className="mt-2 grid gap-2">
          {presets.map(p => (
            <button key={p.id} onClick={() => setPreset(p.id)} className={`rounded-xl border p-3 text-left transition ${preset === p.id ? 'border-white bg-white text-black' : 'border-zinc-800 bg-black/30 text-zinc-300 hover:border-zinc-600'}`}>
              <div className="font-bold">{p.label}</div>
              <div className={`text-xs ${preset === p.id ? 'text-black/60' : 'text-zinc-500'}`}>{p.hint}</div>
            </button>
          ))}
        </div>

        <div className="mt-5 space-y-2 text-sm text-zinc-400">
          <label className="flex items-center gap-2"><input type="checkbox" checked={cartelera} onChange={e => setCartelera(e.target.checked)} /> Incluir cartelera digital</label>
          <label className="flex items-center gap-2"><input type="checkbox" checked={flyer} onChange={e => setFlyer(e.target.checked)} /> Incluir flyer impreso 10x14</label>
        </div>

        <button onClick={render} disabled={busy} className="mt-5 flex w-full items-center justify-center gap-2 rounded-xl bg-white px-4 py-3 text-sm font-black text-black hover:bg-zinc-200 disabled:opacity-60">
          {busy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Calculator className="h-4 w-4" />} Generar cotización
        </button>
      </section>

      <section className="rounded-2xl border border-zinc-800 bg-zinc-900/45 p-5">
        <div className="mb-4 flex items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-bold">Resultado</h2>
            {result?.total_clp && <div className="mt-1 text-3xl font-black text-emerald-300">{result.total_clp}</div>}
          </div>
          <button onClick={copy} disabled={!result?.markdown} className="flex items-center gap-2 rounded-lg border border-zinc-800 bg-black/30 px-3 py-2 text-xs font-bold text-zinc-300 hover:bg-zinc-800 disabled:opacity-40"><Copy className="h-4 w-4" /> Copiar</button>
        </div>
        {result?.error && <div className="rounded-xl border border-red-900/60 bg-red-950/30 p-4 text-sm text-red-300">{result.error}</div>}
        {result?.markdown ? <pre className="max-h-[620px] overflow-auto whitespace-pre-wrap rounded-xl bg-black/40 p-4 text-xs leading-6 text-zinc-300">{result.markdown}</pre> : <div className="rounded-xl border border-dashed border-zinc-800 p-10 text-center text-zinc-500">Genera una cotización para ver tabla y total.</div>}
      </section>
    </div>
  );
}
