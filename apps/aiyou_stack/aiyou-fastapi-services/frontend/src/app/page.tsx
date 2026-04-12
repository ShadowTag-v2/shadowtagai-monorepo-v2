"use client";

import { Users, Activity, DollarSign, CheckCircle, TrendingUp, Zap } from "lucide-react";
import { formatNumber, formatCurrency } from "@/lib/utils";

// Mock data until backend endpoints are ready
const mockSwarmStats = {
  total_agents: 600,
  active_agents: 487,
  shifts: [
    { shift_id: 1, agents: 200, start_hour: 0, end_hour: 8, active: false },
    { shift_id: 2, agents: 200, start_hour: 8, end_hour: 16, active: true },
    { shift_id: 3, agents: 200, start_hour: 16, end_hour: 24, active: false },
  ],
  tier_distribution: { FREE: 450, FLASH: 120, PRO: 30 },
  tasks_completed_24h: 15234,
  revenue_24h: 4521.5,
};

const mockAgentActivity = [
  { hour: "00:00", tasks: 320 },
  { hour: "04:00", tasks: 280 },
  { hour: "08:00", tasks: 890 },
  { hour: "12:00", tasks: 1200 },
  { hour: "16:00", tasks: 950 },
  { hour: "20:00", tasks: 420 },
];

function StatCard({
  title,
  value,
  icon: Icon,
  trend,
  color = "indigo",
}: {
  title: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string }>;
  trend?: string;
  color?: string;
}) {
  const colorClasses = {
    indigo: "bg-indigo-50 text-indigo-600",
    green: "bg-green-50 text-green-600",
    purple: "bg-purple-50 text-purple-600",
    amber: "bg-amber-50 text-amber-600",
  };

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-500">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
          {trend && (
            <p className="text-sm text-green-600 mt-1 flex items-center gap-1">
              <TrendingUp className="h-3 w-3" />
              {trend}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color as keyof typeof colorClasses]}`}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </div>
  );
}

function ShiftIndicator({ shifts }: { shifts: typeof mockSwarmStats.shifts }) {
  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100">
      <h3 className="font-semibold mb-4">Shift Status</h3>
      <div className="space-y-3">
        {shifts.map((shift) => (
          <div key={shift.shift_id} className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div
                className={`w-3 h-3 rounded-full ${shift.active ? "bg-green-500" : "bg-slate-300"}`}
              />
              <span className="text-sm">
                Shift {shift.shift_id} ({shift.start_hour}:00 - {shift.end_hour}:00)
              </span>
            </div>
            <span className="text-sm text-slate-500">{shift.agents} agents</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function TierDistribution({ distribution }: { distribution: Record<string, number> }) {
  const total = Object.values(distribution).reduce((a, b) => a + b, 0);
  const colors = {
    FREE: "bg-slate-400",
    FLASH: "bg-amber-400",
    PRO: "bg-purple-500",
  };

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100">
      <h3 className="font-semibold mb-4">Tier Distribution</h3>
      <div className="flex h-4 rounded-full overflow-hidden mb-4">
        {Object.entries(distribution).map(([tier, count]) => (
          <div
            key={tier}
            className={`${colors[tier as keyof typeof colors]}`}
            style={{ width: `${(count / total) * 100}%` }}
          />
        ))}
      </div>
      <div className="grid grid-cols-3 gap-2">
        {Object.entries(distribution).map(([tier, count]) => (
          <div key={tier} className="text-center">
            <p className="text-lg font-semibold">{count}</p>
            <p className="text-xs text-slate-500">{tier}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function ActivityChart({ data }: { data: typeof mockAgentActivity }) {
  const maxTasks = Math.max(...data.map((d) => d.tasks));

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100">
      <h3 className="font-semibold mb-4">24h Task Activity</h3>
      <div className="flex items-end justify-between h-32 gap-2">
        {data.map((item) => (
          <div key={item.hour} className="flex-1 flex flex-col items-center">
            <div
              className="w-full bg-shadowtag_v4-primary rounded-t"
              style={{ height: `${(item.tasks / maxTasks) * 100}%` }}
            />
            <span className="text-xs text-slate-500 mt-2">{item.hour.slice(0, 2)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Dashboard() {
  // In production, this would fetch from the API
  const stats = mockSwarmStats;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-slate-500">Autoresearch Swarm Overview</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Agents" value={stats.total_agents} icon={Users} color="indigo" />
        <StatCard
          title="Active Now"
          value={stats.active_agents}
          icon={Activity}
          trend="+12% from yesterday"
          color="green"
        />
        <StatCard
          title="Tasks (24h)"
          value={formatNumber(stats.tasks_completed_24h)}
          icon={CheckCircle}
          trend="+8.2%"
          color="purple"
        />
        <StatCard
          title="Revenue (24h)"
          value={formatCurrency(stats.revenue_24h)}
          icon={DollarSign}
          trend="+15.3%"
          color="amber"
        />
      </div>

      {/* Secondary Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <ShiftIndicator shifts={stats.shifts} />
        <TierDistribution distribution={stats.tier_distribution} />
        <ActivityChart data={mockAgentActivity} />
      </div>

      {/* Value Lock Gates */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100">
        <h3 className="font-semibold mb-4 flex items-center gap-2">
          <Zap className="h-5 w-5 text-amber-500" />
          Value Lock Gates
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <p className="text-2xl font-bold text-green-600">160</p>
            <p className="text-sm text-slate-600">IQ Lock</p>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <p className="text-2xl font-bold text-green-600">3.2x</p>
            <p className="text-sm text-slate-600">ROI Ratio</p>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <p className="text-2xl font-bold text-green-600">4.1:1</p>
            <p className="text-sm text-slate-600">LTV:CAC</p>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <p className="text-2xl font-bold text-green-600">A</p>
            <p className="text-sm text-slate-600">SonarQube</p>
          </div>
        </div>
      </div>
    </div>
  );
}
