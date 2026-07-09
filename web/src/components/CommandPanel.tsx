import { TerminalSquare } from 'lucide-react';
import CommandCopy from './CommandCopy';

const groups = [
  {
    title: 'Uso diario',
    icon: '🚀',
    commands: ['py -m flujo app', 'py -m flujo health', 'py -m flujo verify'],
  },
  {
    title: 'Frontend React',
    icon: '⚛️',
    commands: ['cd web', 'npm ci --no-audit --no-fund', 'npm run typecheck', 'npm run build:context'],
  },
  {
    title: 'Airdrop seguro',
    icon: '📦',
    commands: ['py scripts/validate_airdrop.py', 'py scripts/run_airdrop_checks.py "mensaje"'],
  },
  {
    title: 'Operacion',
    icon: '🔧',
    commands: [
      'py -m flujo portal --repo-url https://github.com/ligereza/vibecodeine',
      'py -m flujo eventos flyer-auto "<url-instagram>"',
      'py -m flujo hub route where --area eventos --pieza flyer',
    ],
  },
  {
    title: 'Git & Sync',
    icon: '🔄',
    commands: [
      'py -m flujo github-sync --status',
      'py -m flujo github-sync --push -m "mensaje"',
      'git status --short',
    ],
  },
  {
    title: 'Resolume & Chataigne',
    icon: '🎛️',
    commands: [
      'py -m flujo resolume automatizar jobs/<job_id>',
      'py -m flujo resolume automatizar jobs/<job_id> --fps 25',
      'py -m flujo resolume automatizar jobs/<job_id> --host 127.0.0.1 --port 7000',
    ],
  },
  {
    title: 'Suplementos RD',
    icon: '💊',
    commands: [
      'py -m flujo suplementos list',
      'py -m flujo suplementos contraportada "Impulso" --output salida.svg',
      'py -m flujo suplementos validate svg/suplementos_rd/04_contraportadas/generadas/*.svg',
    ],
  },
  {
    title: 'Plano / Rider',
    icon: '🗺️',
    commands: [
      'py -m flujo plano projects/plano/ejemplos/evento_ejemplo.json --output plano.svg',
      'py -m flujo plano projects/plano/ejemplos/evento_ejemplo.json --validate',
      'py -m flujo plano projects/plano/ejemplos/evento_ejemplo.json --rider',
      'py -m flujo plano projects/plano/ejemplos/evento_ejemplo.json --costs',
    ],
  },
];

export default function CommandPanel() {
  return (
    <div className="space-y-5">
      <div>
        <h1 className="flex items-center gap-2 text-2xl font-black">
          <TerminalSquare className="h-6 w-6" /> Comandos
        </h1>
        <p className="mt-1 text-sm text-zinc-500">Comandos que sostienen el flujo diario y el build React.</p>
      </div>
      <div className="grid gap-5 lg:grid-cols-2">
        {groups.map(group => (
          <section key={group.title} className="rounded-xl border border-zinc-800/60 bg-zinc-900/40 p-4">
            <h2 className="mb-3 flex items-center gap-2 text-sm font-bold">
              <span>{group.icon}</span>
              <span className="uppercase tracking-widest text-zinc-400">{group.title}</span>
            </h2>
            <div className="space-y-2">
              {group.commands.map(command => <CommandCopy key={command} text={command} />)}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
