"use client";
import Link from "next/link";
import {
  Activity,
  Users,
  CheckCircle,
  AlertTriangle,
  Brain,
  Zap,
  BarChart3,
  ChevronRight,
} from "lucide-react";
import { useDashboardMetrics } from "@/hooks/useDashboardMetrics";
import { MetricCard } from "@/components/MetricCard";
import { StatusBadge } from "@/components/StatusBadge";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Case, WorkflowSummary } from "@/lib/types";

export default function DashboardPage() {
  const { metrics, loading } = useDashboardMetrics();
  const [cases, setCases] = useState<Case[]>([]);
  const [wfNames, setWfNames] = useState<Record<string, string>>({});

  useEffect(() => {
    api.cases.list().then(setCases).catch(() => {});
    api.workflows.list().then((r) => {
      const map: Record<string, string> = {};
      for (const w of r.workflows) map[w.id] = w.name;
      setWfNames(map);
    }).catch(() => {});
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Dashboard</h1>
        <p className="text-sm text-text-muted mt-1">
          Organization health and case overview
        </p>
      </div>

      {loading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div
              key={i}
              className="card animate-pulse h-28"
            >
              <div className="h-3 w-20 bg-surface-4 rounded mb-4" />
              <div className="h-8 w-16 bg-surface-4 rounded" />
            </div>
          ))}
        </div>
      ) : metrics ? (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            label="Cases Today"
            value={metrics.cases_today}
            icon={<Activity size={16} />}
            trend="up"
          />
          <MetricCard
            label="Completed"
            value={metrics.completed_cases}
            icon={<CheckCircle size={16} />}
            trend={metrics.completed_cases > 0 ? "up" : "neutral"}
          />
          <MetricCard
            label="Escalated"
            value={metrics.escalated_cases}
            icon={<AlertTriangle size={16} />}
            trend={metrics.escalated_cases > 0 ? "down" : "neutral"}
          />
          <MetricCard
            label="Avg Confidence"
            value={`${(metrics.average_confidence * 100).toFixed(0)}%`}
            icon={<Brain size={16} />}
            format="percent"
          />
        </div>
      ) : (
        <div className="card text-red-400 text-sm flex items-center gap-2">
          <AlertTriangle size={16} />
          Failed to load metrics
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-text-primary">
              Active Cases
            </h2>
            <Link
              href="/cases/new"
              className="btn-primary text-xs flex items-center gap-1.5"
            >
              <Zap size={14} />
              New Case
            </Link>
          </div>

          <div className="card p-0 overflow-hidden">
            {cases.length > 0 ? (
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left text-xs font-medium text-text-muted uppercase tracking-wider px-4 py-3">
                      Case
                    </th>
                    <th className="text-left text-xs font-medium text-text-muted uppercase tracking-wider px-4 py-3 hidden md:table-cell">
                      Request
                    </th>
                    <th className="text-left text-xs font-medium text-text-muted uppercase tracking-wider px-4 py-3 hidden lg:table-cell">
                      Workflow
                    </th>
                    <th className="text-left text-xs font-medium text-text-muted uppercase tracking-wider px-4 py-3">
                      Status
                    </th>
                    <th className="text-right text-xs font-medium text-text-muted uppercase tracking-wider px-4 py-3">
                      Confidence
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {cases.map((c) => (
                    <tr
                      key={c.id}
                      className="hover:bg-surface-4/50 transition-colors cursor-pointer group"
                      onClick={() => (window.location.href = `/cases/${c.id}`)}
                    >
                      <td className="px-4 py-3">
                        <span className="text-sm font-mono text-text-primary">
                          {c.id.slice(0, 8)}
                        </span>
                        <span className="text-xs text-text-muted ml-2">
                          v{c.iteration}
                        </span>
                      </td>
                      <td className="px-4 py-3 hidden md:table-cell">
                        <p className="text-sm text-text-secondary truncate max-w-[300px]">
                          {c.request_text}
                        </p>
                      </td>
                      <td className="px-4 py-3 hidden lg:table-cell">
                        <span className="text-xs text-text-muted">
                          {wfNames[c.workflow_type] || c.workflow_type}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <StatusBadge status={c.status} />
                      </td>
                      <td className="px-4 py-3 text-right">
                        {c.confidence !== null ? (
                          <span
                            className={`text-sm font-medium ${
                              c.confidence >= 0.7
                                ? "text-emerald-400"
                                : c.confidence >= 0.4
                                  ? "text-amber-400"
                                  : "text-red-400"
                            }`}
                          >
                            {(c.confidence * 100).toFixed(0)}%
                          </span>
                        ) : (
                          <span className="text-text-muted text-sm">--</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="p-8 text-center">
                <div className="w-12 h-12 rounded-xl bg-surface-4 flex items-center justify-center mx-auto mb-3">
                  <BarChart3 size={20} className="text-text-muted" />
                </div>
                <p className="text-sm text-text-muted">
                  No cases yet. Launch a{" "}
                  <Link href="/demo" className="link">
                    demo scenario
                  </Link>{" "}
                  or create a{" "}
                  <Link href="/cases/new" className="link">
                    new request
                  </Link>
                  .
                </p>
              </div>
            )}
          </div>
        </div>

        <div>
          <h2 className="text-lg font-semibold text-text-primary mb-4">
            Quick Actions
          </h2>
          <div className="space-y-3">
            <Link
              href="/demo"
              className="card flex items-center gap-3 group hover:border-brand-500/30"
            >
              <div className="w-10 h-10 rounded-lg bg-brand-500/10 flex items-center justify-center text-brand-400 group-hover:bg-brand-500/20 transition-colors">
                <Zap size={18} />
              </div>
              <div className="flex-1 min-w-0">
                <span className="text-sm font-medium text-text-primary block">
                  Launch Demo
                </span>
                <span className="text-xs text-text-muted">
                  4 pre-configured scenarios
                </span>
              </div>
              <ChevronRight size={16} className="text-text-muted" />
            </Link>
            <Link
              href="/cases/new"
              className="card flex items-center gap-3 group hover:border-blue-500/30"
            >
              <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400 group-hover:bg-blue-500/20 transition-colors">
                <Users size={18} />
              </div>
              <div className="flex-1 min-w-0">
                <span className="text-sm font-medium text-text-primary block">
                  New Request
                </span>
                <span className="text-xs text-text-muted">
                  Submit a business case
                </span>
              </div>
              <ChevronRight size={16} className="text-text-muted" />
            </Link>
            <div className="card">
              <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3">
                System Status
              </h3>
              <div className="space-y-2.5">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-text-secondary">Total Events</span>
                  <span className="font-mono text-text-primary">
                    {metrics?.total_events ?? "--"}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-text-secondary">
                    Memory Retrievals
                  </span>
                  <span className="font-mono text-text-primary">
                    {metrics?.memory_retrievals ?? "--"}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-text-secondary">Total Cases</span>
                  <span className="font-mono text-text-primary">
                    {metrics?.total_cases ?? "--"}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
