'use client';

import { useEffect, useState } from 'react';

export default function MetricsDashboard() {
  const [metrics, setMetrics] = useState({
    dailyActiveUsers: 1247,
    totalVideosAnalyzed: 89234,
    avgHDI: 84.7,
    microLicensesSold: 1842,
    revenueToday: 5493.58,
    errorRate: 0.08,
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics((prev) => ({
        ...prev,
        dailyActiveUsers: prev.dailyActiveUsers + Math.floor(Math.random() * 3),
        totalVideosAnalyzed: prev.totalVideosAnalyzed + Math.floor(Math.random() * 12),
        microLicensesSold: prev.microLicensesSold + (Math.random() > 0.7 ? 1 : 0),
        revenueToday: prev.revenueToday + (Math.random() > 0.8 ? 2.99 : 0),
      }));
    }, 8000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-zinc-950 text-white p-8 rounded-3xl max-w-5xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-bold">HeadFade Live Metrics</h1>
          <p className="text-emerald-400">Beta Cohort • Updated live</p>
        </div>
        <div className="text-right">
          <div className="text-xs text-zinc-500">LAST UPDATED</div>
          <div className="font-mono text-sm">{new Date().toLocaleTimeString()}</div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
        {[
          {
            label: 'Daily Active Users',
            value: metrics.dailyActiveUsers.toLocaleString(),
            change: '+12%',
          },
          {
            label: 'Videos Analyzed',
            value: metrics.totalVideosAnalyzed.toLocaleString(),
            change: '+8%',
          },
          { label: 'Avg Human Deception Index', value: `${metrics.avgHDI}%`, change: '-1.2%' },
          {
            label: 'Micro-Licenses Sold',
            value: metrics.microLicensesSold.toLocaleString(),
            change: '+24%',
          },
          { label: 'Revenue Today', value: `$${metrics.revenueToday.toFixed(2)}`, change: '+31%' },
          { label: 'Error Rate', value: `${metrics.errorRate}%`, change: '↓ 0.03%' },
        ].map((metric, i) => (
          <div key={i} className="bg-zinc-900 p-6 rounded-2xl border border-zinc-800">
            <div className="text-sm text-zinc-400 mb-1">{metric.label}</div>
            <div className="text-4xl font-semibold tracking-tighter mb-2">{metric.value}</div>
            <div
              className={`text-xs ${metric.change.startsWith('+') ? 'text-emerald-400' : 'text-rose-400'}`}
            >
              {metric.change} from yesterday
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 text-center text-xs text-zinc-500">
        Powered by Firebase Data Connect + OpenTelemetry • Antigravity Dark Factory
      </div>
    </div>
  );
}
```
