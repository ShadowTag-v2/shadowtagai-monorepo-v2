"use client";

import { AlertCircle, Brain, CheckCircle, Clock, FileText, Search } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

interface IntelReport {
  id: string;
  title: string;
  summary: string;
  confidence: number;
  status: "complete" | "processing" | "pending";
  sources: number;
  created_at: string;
  category: string;
}

const mockReports: IntelReport[] = [
  {
    id: "1",
    title: "Market Analysis: AI Infrastructure Q4 2024",
    summary:
      "Comprehensive analysis of AI infrastructure investments and trends. Key findings indicate 45% growth in cloud GPU deployments.",
    confidence: 0.92,
    status: "complete",
    sources: 24,
    created_at: "2024-01-15T10:30:00Z",
    category: "Market Research",
  },
  {
    id: "2",
    title: "Competitor Intelligence: LLM Providers",
    summary:
      "Analysis of major LLM providers including pricing strategies, model capabilities, and market positioning.",
    confidence: 0.87,
    status: "complete",
    sources: 18,
    created_at: "2024-01-14T14:20:00Z",
    category: "Competitive Analysis",
  },
  {
    id: "3",
    title: "Technical Deep Dive: PSO Optimization",
    summary:
      "Research into particle swarm optimization techniques for neural network weight optimization.",
    confidence: 0.78,
    status: "processing",
    sources: 12,
    created_at: "2024-01-15T16:45:00Z",
    category: "Technical Research",
  },
  {
    id: "4",
    title: "Revenue Optimization Opportunities",
    summary:
      "Identifying new revenue streams and optimization opportunities in the current product lineup.",
    confidence: 0.65,
    status: "pending",
    sources: 8,
    created_at: "2024-01-15T18:00:00Z",
    category: "Business Strategy",
  },
];

function ConfidenceBadge({ confidence }: { confidence: number }) {
  const color = confidence >= 0.85 ? "green" : confidence >= 0.7 ? "amber" : "red";
  const colorClasses = {
    green: "bg-green-100 text-green-700",
    amber: "bg-amber-100 text-amber-700",
    red: "bg-red-100 text-red-700",
  };

  return (
    <span className={cn("px-2 py-1 rounded-full text-xs font-medium", colorClasses[color])}>
      {(confidence * 100).toFixed(0)}% confidence
    </span>
  );
}

function StatusIcon({ status }: { status: string }) {
  switch (status) {
    case "complete":
      return <CheckCircle className="h-5 w-5 text-green-500" />;
    case "processing":
      return <Clock className="h-5 w-5 text-amber-500 animate-pulse" />;
    default:
      return <AlertCircle className="h-5 w-5 text-slate-400" />;
  }
}

export default function IntelPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const categories = [...new Set(mockReports.map((r) => r.category))];

  const filteredReports = mockReports.filter((report) => {
    const matchesSearch =
      report.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      report.summary.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = !selectedCategory || report.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Brain className="h-7 w-7 text-shadowtag_v4-primary" />
          Intelligence Hub
        </h1>
        <p className="text-slate-500">Research reports and analysis from the swarm</p>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
          <input
            type="text"
            placeholder="Search reports..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-shadowtag_v4-primary"
          />
        </div>
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setSelectedCategory(null)}
            className={cn(
              "px-3 py-2 rounded-lg text-sm transition-colors",
              !selectedCategory
                ? "bg-shadowtag_v4-primary text-white"
                : "bg-slate-100 hover:bg-slate-200",
            )}
          >
            All
          </button>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={cn(
                "px-3 py-2 rounded-lg text-sm transition-colors",
                selectedCategory === cat
                  ? "bg-shadowtag_v4-primary text-white"
                  : "bg-slate-100 hover:bg-slate-200",
              )}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 border border-slate-100">
          <p className="text-2xl font-bold">{mockReports.length}</p>
          <p className="text-sm text-slate-500">Total Reports</p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-slate-100">
          <p className="text-2xl font-bold">
            {mockReports.filter((r) => r.status === "complete").length}
          </p>
          <p className="text-sm text-slate-500">Completed</p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-slate-100">
          <p className="text-2xl font-bold">{mockReports.reduce((a, b) => a + b.sources, 0)}</p>
          <p className="text-sm text-slate-500">Sources Analyzed</p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-slate-100">
          <p className="text-2xl font-bold">
            {(
              (mockReports.reduce((a, b) => a + b.confidence, 0) / mockReports.length) *
              100
            ).toFixed(0)}
            %
          </p>
          <p className="text-sm text-slate-500">Avg Confidence</p>
        </div>
      </div>

      {/* Reports List */}
      <div className="space-y-4">
        {filteredReports.map((report) => (
          <div
            key={report.id}
            className="bg-white rounded-xl p-6 border border-slate-100 hover:shadow-md transition-shadow cursor-pointer"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <StatusIcon status={report.status} />
                  <h3 className="font-semibold">{report.title}</h3>
                </div>
                <p className="text-slate-600 text-sm mb-3">{report.summary}</p>
                <div className="flex items-center gap-4 text-sm text-slate-500">
                  <span className="flex items-center gap-1">
                    <FileText className="h-4 w-4" />
                    {report.sources} sources
                  </span>
                  <span>{report.category}</span>
                  <span>{new Date(report.created_at).toLocaleDateString()}</span>
                </div>
              </div>
              <ConfidenceBadge confidence={report.confidence} />
            </div>
          </div>
        ))}
      </div>

      {filteredReports.length === 0 && (
        <div className="text-center py-12 text-slate-500">
          No reports found matching your criteria
        </div>
      )}
    </div>
  );
}
