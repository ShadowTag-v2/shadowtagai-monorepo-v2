"use client";

import { Brain, LayoutDashboard, MessageSquare, Settings, ShieldCheck, Users } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Atomic Chat", href: "/atomic-chat", icon: MessageSquare },
  { name: "Intel", href: "/intel", icon: Brain },
  { name: "Quality", href: "/quality", icon: ShieldCheck },
  { name: "Agents", href: "/agents", icon: Users },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-shadowtag_v4-dark text-white flex flex-col">
      <div className="p-6">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-shadowtag_v4-primary to-shadowtag_v4-accent bg-clip-text text-transparent">
          ShadowTag-v2
        </h1>
        <p className="text-slate-400 text-sm mt-1">Autoresearch Platform</p>
      </div>

      <nav className="flex-1 px-4">
        <ul className="space-y-2">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 px-4 py-3 rounded-lg transition-colors",
                    isActive
                      ? "bg-shadowtag_v4-primary text-white"
                      : "text-slate-300 hover:bg-slate-800",
                  )}
                >
                  <item.icon className="h-5 w-5" />
                  {item.name}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="p-4 border-t border-slate-700">
        <div className="flex items-center gap-3 px-4 py-2">
          <div className="w-8 h-8 rounded-full bg-shadowtag_v4-secondary flex items-center justify-center">
            <span className="text-sm font-medium">FM</span>
          </div>
          <div>
            <p className="text-sm font-medium">Swarm Active</p>
            <p className="text-xs text-green-400">600 agents online</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
