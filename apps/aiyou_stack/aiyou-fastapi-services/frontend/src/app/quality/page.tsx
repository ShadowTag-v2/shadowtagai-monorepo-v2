"use client";

import { AlertTriangle, CheckCircle, ShieldCheck, Target, TrendingUp, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface QualityGate {
  name: string;
  current: number | string;
  target: number | string;
  status: "pass" | "fail" | "warning";
  description: string;
}

const qualityGates: QualityGate[] = [
  {
    name: "IQ Lock",
    current: 163,
    target: 160,
    status: "pass",
    description: "Minimum intelligence quotient score for agent outputs",
  },
  {
    name: "ROI Ratio",
    current: 3.4,
    target: 3.0,
    status: "pass",
    description: "Return on investment must exceed 3x cost",
  },
  {
    name: "LTV:CAC Ratio",
    current: 4.2,
    target: 4.0,
    status: "pass",
    description: "Lifetime value to customer acquisition cost ratio",
  },
  {
    name: "SonarQube Score",
    current: "A",
    target: "B",
    status: "pass",
    description: "Code quality score from static analysis",
  },
  {
    name: "Test Coverage",
    current: 78,
    target: 80,
    status: "warning",
    description: "Percentage of code covered by tests",
  },
  {
    name: "Security Score",
    current: 94,
    target: 90,
    status: "pass",
    description: "OWASP security compliance score",
  },
];

interface CodeMetric {
  name: string;
  value: string | number;
  change: number;
  unit?: string;
}

const codeMetrics: CodeMetric[] = [
  { name: "Lines of Code", value: "45.2K", change: 2.3 },
  { name: "Duplications", value: "1.2%", change: -0.5 },
  { name: "Tech Debt", value: "2.4h", change: -1.2 },
  { name: "Bugs", value: 0, change: 0 },
  { name: "Vulnerabilities", value: 0, change: 0 },
  { name: "Code Smells", value: 12, change: -3 },
];

function StatusBadge({ status }: { status: "pass" | "fail" | "warning" }) {
  const config = {
    pass: { icon: CheckCircle, bg: "bg-green-100", text: "text-green-700", label: "PASS" },
    fail: { icon: XCircle, bg: "bg-red-100", text: "text-red-700", label: "FAIL" },
    warning: { icon: AlertTriangle, bg: "bg-amber-100", text: "text-amber-700", label: "WARNING" },
  };

  const { icon: Icon, bg, text, label } = config[status];

  return (
    <span
      className={cn("flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium", bg, text)}
    >
      <Icon className="h-3 w-3" />
      {label}
    </span>
  );
}

function GateCard({ gate }: { gate: QualityGate }) {
  return (
    <div className="bg-white rounded-xl p-6 border border-slate-100">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold">{gate.name}</h3>
        <StatusBadge status={gate.status} />
      </div>
      <div className="flex items-end gap-2 mb-2">
        <span className="text-3xl font-bold">{gate.current}</span>
        <span className="text-slate-500 mb-1">/ {gate.target}</span>
      </div>
      <p className="text-sm text-slate-500">{gate.description}</p>
    </div>
  );
}

function MetricCard({ metric }: { metric: CodeMetric }) {
  const isPositive = metric.change > 0;
  const isNeutral = metric.change === 0;

  return (
    <div className="bg-white rounded-lg p-4 border border-slate-100">
      <p className="text-sm text-slate-500">{metric.name}</p>
      <div className="flex items-center justify-between mt-1">
        <span className="text-xl font-bold">{metric.value}</span>
        {!isNeutral && (
          <span
            className={cn(
              "text-xs flex items-center gap-1",
              isPositive ? "text-red-500" : "text-green-500",
            )}
          >
            <TrendingUp className={cn("h-3 w-3", !isPositive && "rotate-180")} />
            {Math.abs(metric.change)}%
          </span>
        )}
      </div>
    </div>
  );
}

export default function QualityPage() {
  const passCount = qualityGates.filter((g) => g.status === "pass").length;
  const totalGates = qualityGates.length;
  const overallScore = (passCount / totalGates) * 100;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <ShieldCheck className="h-7 w-7 text-green-500" />
          Quality Gates
        </h1>
        <p className="text-slate-500">Value lock gates and code quality metrics</p>
      </div>

      {/* Overall Status */}
      <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-green-100">Overall Quality Score</p>
            <p className="text-4xl font-bold mt-1">{overallScore.toFixed(0)}%</p>
            <p className="text-green-100 mt-2">
              {passCount}/{totalGates} gates passing
            </p>
          </div>
          <div className="w-24 h-24 rounded-full border-4 border-white/30 flex items-center justify-center">
            <Target className="h-12 w-12" />
          </div>
        </div>
      </div>

      {/* Quality Gates Grid */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Value Lock Gates</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {qualityGates.map((gate) => (
            <GateCard key={gate.name} gate={gate} />
          ))}
        </div>
      </div>

      {/* Code Metrics */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Code Metrics (SonarQube)</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {codeMetrics.map((metric) => (
            <MetricCard key={metric.name} metric={metric} />
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-xl p-6 border border-slate-100">
        <h2 className="text-lg font-semibold mb-4">Recent Quality Checks</h2>
        <div className="space-y-3">
          {[
            { time: "5 mins ago", action: "PR #234 passed all gates", status: "pass" },
            { time: "1 hour ago", action: "Security scan completed", status: "pass" },
            {
              time: "2 hours ago",
              action: "Test coverage dropped below threshold",
              status: "warning",
            },
            { time: "4 hours ago", action: "Code quality analysis completed", status: "pass" },
          ].map((item, i) => (
            <div
              key={i}
              className="flex items-center justify-between py-2 border-b border-slate-100 last:border-0"
            >
              <div className="flex items-center gap-3">
                {item.status === "pass" ? (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                ) : (
                  <AlertTriangle className="h-5 w-5 text-amber-500" />
                )}
                <span>{item.action}</span>
              </div>
              <span className="text-sm text-slate-500">{item.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
