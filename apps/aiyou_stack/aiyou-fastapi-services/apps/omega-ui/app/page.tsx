import { AgentDebugger } from '../components/AgentDebugger';

export default function Home() {
  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col gap-8 row-start-2 items-center sm:items-start">
        <h1 className="text-4xl font-bold">ShadowTag Omega // UI</h1>
        <p className="text-xl">
          Protocol: AG-UI <span className="text-green-500 font-mono">[ACTIVE]</span>
        </p>
        <p className="text-sm text-gray-400">Backend: Autoresearch v2 (Judge 6 Wired)</p>

        <div className="p-4 border border-gray-700 rounded-lg bg-gray-900/50">
          <h2 className="font-mono text-xs uppercase tracking-widest mb-2 text-gray-500">
            System Status
          </h2>
          <ul className="text-sm space-y-2 font-mono">
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              CopilotKit Provider: <span className="text-green-400">ON</span>
            </li>
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 bg-green-500 rounded-full" />
              API Route: <span className="text-green-400">/api/copilotkit</span>
            </li>
            <li className="flex items-center gap-2">
              <span className="w-2 h-2 bg-green-500 rounded-full" />
              Governance: <span className="text-green-400">JUDGE 6 OMEGA</span>
            </li>
          </ul>
        </div>
      </main>
      <AgentDebugger />
    </div>
  );
}
