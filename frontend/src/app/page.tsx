"use client";
import Link from "next/link";
import {
  Activity,
  Search,
  X,
  Users,
  CheckCircle,
  AlertTriangle,
  Brain,
  Zap,
  BarChart3,
  ChevronRight,
  Clock,
  TrendingUp,
  Shield,
} from "lucide-react";
import { useDashboardMetrics } from "@/hooks/useDashboardMetrics";
import { MetricCard } from "@/components/MetricCard";
import { StatusBadge } from "@/components/StatusBadge";
import { useEffect, useState, useCallback } from "react";
import { api } from "@/lib/api";
import type { Case } from "@/lib/types";

const STATUS_OPTIONS = ["", "created", "independent_assessment", "adjudication", "approval_pending", "completed", "escalated"] as const;

export default function DashboardPage() {
  const { metrics, loading } = useDashboardMetrics();
  const [cases, setCases] = useState<Case[]>([]);
  const [wfNames, setWfNames] = useState<Record<string, string>>({});
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [wfFilter, setWfFilter] = useState("");

  const fetchCases = useCallback(async () => {
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (statusFilter) params.set("status", statusFilter);
    if (wfFilter) params.set("workflow_type", wfFilter);
    try {
      const data = await api.cases.list(params.toString());
      setCases(data);
    } catch { /* ignore */ }
  }, [search, statusFilter, wfFilter]);

  useEffect(() => {
    const timer = setTimeout(fetchCases, 300);
    return () => clearTimeout(timer);
  }, [fetchCases]);

  useEffect(() => {
    api.workflows.list().then((r) => {
      const map: Record<string, string> = {};
      for (const w of r.workflows) map[w.id] = w.name;
      setWfNames(map);
    }).catch(() => {});
  }, []);

  const clearFilters = useCallback(() => {
    setSearch("");
    setStatusFilter("");
    setWfFilter("");
  }, []);

  const hasFilters = search || statusFilter || wfFilter;

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds.toFixed(0)}s`;
    if (seconds < 3600) return `${(seconds / 60).toFixed(1)}m`;
    return `${(seconds / 3600).toFixed(1)}h`;
  };

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
          {[...Array(8)].map((_, i) => (
            <div key={i} className="card animate-pulse h-28">
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
            trend={metrics.cases_today > 0 ? "up" : "neutral"}
          />
          <MetricCard
            label="Completed"
            value={metrics.completed_cases}
            icon={<CheckCircle size={16} />}
            trend={metrics.completed_cases > 0 ? "up" : "neutral"}
          />
          <MetricCard
            label="Pending Approval"
            value={metrics.pending_approval}
            icon={<Clock size={16} />}
            trend={metrics.pending_approval > 0 ? "neutral" : "up"}
          />
          <MetricCard
            label="Escalated"
            value={metrics.escalated_cases}
            icon={<AlertTriangle size={16} />}
            trend={metrics.escalated_cases > 0 ? "down" : "neutral"}
          />
          <MetricCard
            label="Approval Rate"
            value={`${(metrics.approval_rate * 100).toFixed(0)}%`}
            icon={<Shield size={16} />}
            trend={metrics.approval_rate >= 0.7 ? "up" : "down"}
          />
          <MetricCard
            label="Escalation Rate"
            value={`${(metrics.escalation_rate * 100).toFixed(0)}%`}
            icon={<TrendingUp size={16} />}
            trend={metrics.escalation_rate <= 0.2 ? "up" : "down"}
          />
          <MetricCard
            label="Avg Confidence"
            value={`${(metrics.average_confidence * 100).toFixed(0)}%`}
            icon={<Brain size={16} />}
          />
          <MetricCard
            label="Avg Deliberation"
            value={formatDuration(metrics.avg_deliberation_time_s)}
            icon={<Clock size={16} />}
          />
        </div>
      ) : (
        <div className="card text-red-400 text-sm flex items-center gap-2">
          <AlertTriangle size={16} />
          Failed to load metrics
        </div>
      )}

      {metrics && Object.keys(metrics.department_performance).length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-text-primary mb-3">
            Department Performance
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {Object.entries(metrics.department_performance).map(([dept, conf]) => (
              <div key={dept} className="card p-3">
                <div className="text-xs text-text-muted uppercase tracking-wider mb-1 truncate">
                  {dept.replace(/_/g, " ")}
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-1.5 bg-surface-4 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${
                        conf >= 0.7 ? "bg-emerald-500" : conf >= 0.4 ? "bg-amber-500" : "bg-red-500"
                      }`}
                      style={{ width: `${conf * 100}%` }}
                    />
                  </div>
                  <span className={`text-xs font-medium ${
                    conf >= 0.7 ? "text-emerald-400" : conf >= 0.4 ? "text-amber-400" : "text-red-400"
                  }`}>
                    {(conf * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-text-primary">
              {hasFilters ? "Filtered Cases" : "Active Cases"}
            </h2>
            <Link
              href="/cases/new"
              className="btn-primary text-xs flex items-center gap-1.5"
            >
              <Zap size={14} />
              New Case
            </Link>
          </div>

          <div className="flex items-center gap-2 mb-3 flex-wrap">
            <div className="relative flex-1 min-w-[200px] max-w-sm">
              <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-text-muted" />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search cases..."
                className="input pl-8 text-sm h-10"
              />
              {search && (
                <button onClick={() => setSearch("")} className="absolute right-2 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary">
                  <X size={14} />
                </button>
              )}
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input text-sm h-10 w-[150px]"
            >
              <option value="">All statuses</option>
              {STATUS_OPTIONS.filter(Boolean).map((s) => (
                <option key={s} value={s}>{s.replace(/_/g, " ")}</option>
              ))}
            </select>
            <select
              value={wfFilter}
              onChange={(e) => setWfFilter(e.target.value)}
              className="input text-sm h-10 w-[170px]"
            >
              <option value="">All workflows</option>
              {Object.entries(wfNames).map(([id, name]) => (
                <option key={id} value={id}>{name}</option>
              ))}
            </select>
            {hasFilters && (
              <button onClick={clearFilters} className="btn-ghost text-xs h-8 flex items-center gap-1">
                <X size={12} /> Clear
              </button>
            )}
          </div>

          <div className="card p-0 overflow-hidden">
            {cases.length > 0 ? (
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left text-xs font-medium text-text-muted uppercase tracking-wider px-4 py-3">
                      Case
                    </th>
                    <th className="text-left text-xs font-medium text-text-muted uppercase tracking-wider px-4 py-3">
                      Customer
                    </th>
                    <th className="text-left text-xs font-medium text-text-muted uppercase tracking-wider px-4 py-3 hidden md:table-cell">
                      Request
                    </th>
                    <th className="text-left text-xs font-medium text-text-muted uppercase tracking-wider px-4 py-3 hidden lg:table-cell">
                      Created
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
                      <td className="px-4 py-3">
                        <span className="text-xs font-mono text-text-secondary">
                          {c.customer_id.slice(0, 8)}
                        </span>
                      </td>
                      <td className="px-4 py-3 hidden md:table-cell">
                        <p className="text-sm text-text-secondary truncate max-w-[250px]">
                          {c.request_text}
                        </p>
                      </td>
                      <td className="px-4 py-3 hidden lg:table-cell">
                        <span className="text-xs text-text-muted">
                          {c.created_at
                            ? new Date(c.created_at).toLocaleDateString()
                            : "--"}
                        </span>
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
                  <span className="text-text-secondary">Memory Utilization</span>
                  <span className="font-mono text-text-primary">
                    {metrics ? `${(metrics.memory_utilization_rate * 100).toFixed(0)}%` : "--"}
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
