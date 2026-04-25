import { CreditCard, Image as ImageIcon, LogOut, Sparkles } from 'lucide-react';
import Link from 'next/link';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  // Pure UI Scaffold (Supabase Auth verification omitted for MVP brevity)
  // In production, we check cookies() and redirect('/login') if unauthorized.

  return (
    <div className="min-h-screen bg-black text-white flex overflow-hidden">
      {/* Background Ambience */}
      <div className="fixed inset-0 bg-[radial-gradient(circle_at_50%_120%,rgba(16,185,129,0.05),transparent_40%)]" />

      {/* Sidebar Navigation */}
      <aside className="w-64 border-r border-white/10 glass-panel flex flex-col z-10 hidden md:flex">
        <div className="p-6 border-b border-white/5">
          <Link href="/" className="flex items-center gap-2 group">
            <Sparkles className="w-6 h-6 text-emerald-400 group-hover:rotate-12 transition-transform" />
            <span className="font-bold text-xl tracking-tight">
              Thumbly<span className="text-emerald-500">.</span>
            </span>
          </Link>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          <Link
            href="/dashboard"
            className="flex items-center gap-3 px-4 py-3 rounded-xl bg-white/5 text-emerald-300 border border-white/10 shadow-[0_0_15px_rgba(16,185,129,0.1)]"
          >
            <ImageIcon className="w-4 h-4" />
            <span className="font-medium text-sm text-emerald-100">Studio</span>
          </Link>
          <Link
            href="/dashboard/billing"
            className="flex items-center gap-3 px-4 py-3 rounded-xl text-zinc-400 hover:text-white hover:bg-white/5 transition-colors"
          >
            <CreditCard className="w-4 h-4" />
            <span className="font-medium text-sm">Billing</span>
          </Link>
        </nav>

        <div className="p-4 border-t border-white/5">
          <button className="flex items-center justify-between w-full px-4 py-3 rounded-xl text-zinc-400 hover:text-white hover:bg-red-500/10 hover:border-red-500/20 border border-transparent transition-all">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-emerald-500 to-cyan-500 p-[1px]">
                <div className="w-full h-full bg-black rounded-full" />
              </div>
              <span className="text-sm font-medium">Founder</span>
            </div>
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </aside>

      {/* Main Content Pane */}
      <main className="flex-1 relative z-10 p-6 lg:p-10 overflow-auto">{children}</main>
    </div>
  );
}
