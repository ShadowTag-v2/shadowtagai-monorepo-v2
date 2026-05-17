"use client";

import { Search, Star, Users } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

interface Agent {
  id: string;
  name: string;
  level: string;
  tier: "FREE" | "FLASH" | "PRO";
  status: "active" | "idle" | "busy";
  tasks_completed: number;
  rating: number;
  specialization: string;
}

const mockAgents: Agent[] = [
  {
    id: "fm-001",
    name: "FM-ANALYST-001",
    level: "L3 Partner",
    tier: "PRO",
    status: "busy",
    tasks_completed: 1245,
    rating: 4.9,
    specialization: "Data Analysis",
  },
  {
    id: "fm-002",
    name: "FM-WRITER-042",
    level: "L2 Associate",
    tier: "FLASH",
    status: "active",
    tasks_completed: 892,
    rating: 4.7,
    specialization: "Content Generation",
  },
  {
    id: "fm-003",
    name: "FM-RESEARCH-015",
    level: "L3 Partner",
    tier: "PRO",
    status: "active",
    tasks_completed: 1567,
    rating: 4.8,
    specialization: "Research",
  },
  {
    id: "fm-004",
    name: "FM-CODE-088",
    level: "L2 Associate",
    tier: "FLASH",
    status: "idle",
    tasks_completed: 456,
    rating: 4.5,
    specialization: "Code Review",
  },
  {
    id: "fm-005",
    name: "FM-QA-033",
    level: "L1 Paralegal",
    tier: "FREE",
    status: "active",
    tasks_completed: 234,
    rating: 4.3,
    specialization: "Quality Assurance",
  },
  {
    id: "fm-006",
    name: "FM-DISPATCH",
    level: "L4 Senior Partner",
    tier: "PRO",
    status: "busy",
    tasks_completed: 5678,
    rating: 5.0,
    specialization: "Task Routing",
  },
  {
    id: "fm-007",
    name: "FM-INTEL-007",
    level: "L3 Partner",
    tier: "PRO",
    status: "active",
    tasks_completed: 2345,
    rating: 4.9,
    specialization: "Intelligence",
  },
  {
    id: "fm-008",
    name: "FM-SUPPORT-121",
    level: "L1 Paralegal",
    tier: "FREE",
    status: "idle",
    tasks_completed: 123,
    rating: 4.1,
    specialization: "Customer Support",
  },
];

function TierBadge({ tier }: { tier: "FREE" | "FLASH" | "PRO" }) {
  const config = {
    FREE: "bg-slate-100 text-slate-600",
    FLASH: "bg-amber-100 text-amber-700",
    PRO: "bg-purple-100 text-purple-700",
  };

  return (
    <span className={cn("px-2 py-0.5 rounded text-xs font-medium", config[tier])}>{tier}</span>
  );
}

function StatusDot({ status }: { status: string }) {
  const colors = {
    active: "bg-green-500",
    busy: "bg-amber-500",
    idle: "bg-slate-300",
  };

  return <span className={cn("w-2 h-2 rounded-full", colors[status as keyof typeof colors])} />;
}

function RatingStars({ rating }: { rating: number }) {
  return (
    <div className="flex items-center gap-1">
      <Star className="h-4 w-4 fill-amber-400 text-amber-400" />
      <span className="text-sm font-medium">{rating.toFixed(1)}</span>
    </div>
  );
}

export default function AgentsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [filterTier, setFilterTier] = useState<string | null>(null);

  const filteredAgents = mockAgents.filter((agent) => {
    const matchesSearch =
      agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.specialization.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesTier = !filterTier || agent.tier === filterTier;
    return matchesSearch && matchesTier;
  });

  const stats = {
    total: mockAgents.length,
    active: mockAgents.filter((a) => a.status === "active").length,
    busy: mockAgents.filter((a) => a.status === "busy").length,
    idle: mockAgents.filter((a) => a.status === "idle").length,
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Users className="h-7 w-7 text-shadowtag_v4-primary" />
          Agent Registry
        </h1>
        <p className="text-slate-500">Autoresearch swarm agents</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 border border-slate-100 text-center">
          <p className="text-3xl font-bold">{stats.total}</p>
          <p className="text-sm text-slate-500">Total Agents</p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-slate-100 text-center">
          <div className="flex items-center justify-center gap-2">
            <StatusDot status="active" />
            <p className="text-3xl font-bold text-green-600">{stats.active}</p>
          </div>
          <p className="text-sm text-slate-500">Active</p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-slate-100 text-center">
          <div className="flex items-center justify-center gap-2">
            <StatusDot status="busy" />
            <p className="text-3xl font-bold text-amber-600">{stats.busy}</p>
          </div>
          <p className="text-sm text-slate-500">Busy</p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-slate-100 text-center">
          <div className="flex items-center justify-center gap-2">
            <StatusDot status="idle" />
            <p className="text-3xl font-bold text-slate-400">{stats.idle}</p>
          </div>
          <p className="text-sm text-slate-500">Idle</p>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
          <input
            type="text"
            placeholder="Search agents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-shadowtag_v4-primary"
          />
        </div>
        <div className="flex gap-2">
          {["FREE", "FLASH", "PRO"].map((tier) => (
            <button
              key={tier}
              onClick={() => setFilterTier(filterTier === tier ? null : tier)}
              className={cn(
                "px-3 py-2 rounded-lg text-sm transition-colors",
                filterTier === tier
                  ? "bg-shadowtag_v4-primary text-white"
                  : "bg-slate-100 hover:bg-slate-200",
              )}
            >
              {tier}
            </button>
          ))}
        </div>
      </div>

      {/* Agents Table */}
      <div className="bg-white rounded-xl border border-slate-100 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-100">
            <tr>
              <th className="text-left px-6 py-3 text-sm font-medium text-slate-500">Agent</th>
              <th className="text-left px-6 py-3 text-sm font-medium text-slate-500">Level</th>
              <th className="text-left px-6 py-3 text-sm font-medium text-slate-500">Tier</th>
              <th className="text-left px-6 py-3 text-sm font-medium text-slate-500">Status</th>
              <th className="text-left px-6 py-3 text-sm font-medium text-slate-500">Tasks</th>
              <th className="text-left px-6 py-3 text-sm font-medium text-slate-500">Rating</th>
              <th className="text-left px-6 py-3 text-sm font-medium text-slate-500">
                Specialization
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filteredAgents.map((agent) => (
              <tr key={agent.id} className="hover:bg-slate-50 cursor-pointer">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-shadowtag_v4-primary flex items-center justify-center text-white text-xs font-medium">
                      {agent.name.split("-")[1]?.slice(0, 2)}
                    </div>
                    <span className="font-medium">{agent.name}</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm">{agent.level}</td>
                <td className="px-6 py-4">
                  <TierBadge tier={agent.tier} />
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <StatusDot status={agent.status} />
                    <span className="text-sm capitalize">{agent.status}</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm">{agent.tasks_completed.toLocaleString()}</td>
                <td className="px-6 py-4">
                  <RatingStars rating={agent.rating} />
                </td>
                <td className="px-6 py-4 text-sm text-slate-500">{agent.specialization}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredAgents.length === 0 && (
        <div className="text-center py-12 text-slate-500">
          No agents found matching your criteria
        </div>
      )}
    </div>
  );
}
