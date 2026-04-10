"use client";

import { useState } from "react";
import { Settings, Bell, Shield, Zap, Database, Globe } from "lucide-react";
import { cn } from "@/lib/utils";

interface SettingToggle {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  category: string;
}

const initialSettings: SettingToggle[] = [
  {
    id: "realtime",
    name: "Real-time Updates",
    description: "Enable live dashboard updates via WebSocket",
    enabled: true,
    category: "Performance",
  },
  {
    id: "notifications",
    name: "Desktop Notifications",
    description: "Show notifications for important events",
    enabled: false,
    category: "Notifications",
  },
  {
    id: "email_alerts",
    name: "Email Alerts",
    description: "Send email for critical quality gate failures",
    enabled: true,
    category: "Notifications",
  },
  {
    id: "auto_scale",
    name: "Auto-scale Agents",
    description: "Automatically adjust agent count based on load",
    enabled: true,
    category: "Swarm",
  },
  {
    id: "pro_priority",
    name: "PRO Tier Priority",
    description: "Prioritize PRO tier agents for complex tasks",
    enabled: true,
    category: "Swarm",
  },
  {
    id: "dead_mans_switch",
    name: "Dead Man's Switch",
    description: "Automatic safety shutdown if no activity for 24h",
    enabled: true,
    category: "Security",
  },
  {
    id: "audit_logging",
    name: "Audit Logging",
    description: "Log all agent actions for compliance",
    enabled: true,
    category: "Security",
  },
  {
    id: "api_caching",
    name: "API Response Caching",
    description: "Cache API responses to improve performance",
    enabled: false,
    category: "Performance",
  },
];

function Toggle({ enabled, onToggle }: { enabled: boolean; onToggle: () => void }) {
  return (
    <button
      onClick={onToggle}
      className={cn(
        "relative w-12 h-6 rounded-full transition-colors",
        enabled ? "bg-shadowtag_v4-primary" : "bg-slate-200",
      )}
    >
      <span
        className={cn(
          "absolute top-1 left-1 w-4 h-4 rounded-full bg-white transition-transform",
          enabled && "translate-x-6",
        )}
      />
    </button>
  );
}

export default function SettingsPage() {
  const [settings, setSettings] = useState(initialSettings);

  const toggleSetting = (id: string) => {
    setSettings((prev) => prev.map((s) => (s.id === id ? { ...s, enabled: !s.enabled } : s)));
  };

  const categories = [...new Set(settings.map((s) => s.category))];

  const categoryIcons: Record<string, React.ComponentType<{ className?: string }>> = {
    Performance: Zap,
    Notifications: Bell,
    Swarm: Database,
    Security: Shield,
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Settings className="h-7 w-7 text-slate-600" />
          Settings
        </h1>
        <p className="text-slate-500">Configure platform behavior and preferences</p>
      </div>

      {/* API Configuration */}
      <div className="bg-white rounded-xl p-6 border border-slate-100">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Globe className="h-5 w-5" />
          API Configuration
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Backend API URL</label>
            <input
              type="text"
              defaultValue="http://localhost:8000"
              className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-shadowtag_v4-primary"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Autoresearch Server
            </label>
            <input
              type="text"
              defaultValue="http://localhost:8600"
              className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-shadowtag_v4-primary"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Gemini API Key</label>
            <input
              type="password"
              [VAPORIZED_PWD]="••••••••••••••••"
              className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-shadowtag_v4-primary"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              FastGPT Endpoint
            </label>
            <input
              type="text"
              defaultValue="https://api.fastgpt.in"
              className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-shadowtag_v4-primary"
            />
          </div>
        </div>
      </div>

      {/* Settings by Category */}
      {categories.map((category) => {
        const Icon = categoryIcons[category] || Settings;
        const categorySettings = settings.filter((s) => s.category === category);

        return (
          <div key={category} className="bg-white rounded-xl p-6 border border-slate-100">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Icon className="h-5 w-5" />
              {category}
            </h2>
            <div className="space-y-4">
              {categorySettings.map((setting) => (
                <div
                  key={setting.id}
                  className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0"
                >
                  <div>
                    <p className="font-medium">{setting.name}</p>
                    <p className="text-sm text-slate-500">{setting.description}</p>
                  </div>
                  <Toggle enabled={setting.enabled} onToggle={() => toggleSetting(setting.id)} />
                </div>
              ))}
            </div>
          </div>
        );
      })}

      {/* Save Button */}
      <div className="flex justify-end gap-4">
        <button className="px-4 py-2 rounded-lg border border-slate-200 hover:bg-slate-50 transition-colors">
          Reset to Defaults
        </button>
        <button className="px-4 py-2 rounded-lg bg-shadowtag_v4-primary text-white hover:bg-indigo-600 transition-colors">
          Save Changes
        </button>
      </div>
    </div>
  );
}
