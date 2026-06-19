"use client";
import Link from "next/link";
import { useDashboardMetrics } from "@/hooks/useDashboardMetrics";

const STATUS_COLORS: Record<string, string> = {
  completed: "bg-green-500",
  escalated: "bg-red-500",
  approval_pending: "bg-yellow-500",
  adjudication: "bg-blue-500",
  default: "bg-gray-500",
};

export default function DashboardPage() {
  const { metrics, loading } = useDashboardMetrics();

  return (
    <div className="min-h-screen p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-white">Orqestra</h1>
        <p className="text-gray-400 mt-1">Organization Health Dashboard</p>
      </header>

      {loading ? (
        <div className="text-gray-400">Loading metrics...</div>
      ) : metrics ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <MetricCard label="Cases Today" value={metrics.cases_today} />
          <MetricCard label="Total Cases" value={metrics.total_cases} />
          <MetricCard
            label="Completed"
            value={metrics.completed_cases}
            color="green"
          />
          <MetricCard
            label="Escalated"
            value={metrics.escalated_cases}
            color="red"
          />
          <MetricCard
            label="Avg Confidence"
            value={`${(metrics.average_confidence * 100).toFixed(0)}%`}
          />
          <MetricCard label="Total Events" value={metrics.total_events} />
          <MetricCard
            label="Memory Retrievals"
            value={metrics.memory_retrievals}
          />
        </div>
      ) : (
        <div className="text-red-400">Failed to load metrics</div>
      )}

      <nav className="flex gap-4 mb-8">
        <Link
          href="/demo"
          className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 transition"
        >
          Demo Case Library
        </Link>
        <Link
          href="/cases/new"
          className="px-4 py-2 bg-gray-700 rounded hover:bg-gray-600 transition"
        >
          New Request
        </Link>
      </nav>

      <CasesList />
    </div>
  );
}

function MetricCard({
  label,
  value,
  color,
}: {
  label: string;
  value: string | number;
  color?: string;
}) {
  return (
    <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
      <div className="text-sm text-gray-400">{label}</div>
      <div className={`text-2xl font-bold mt-1 ${color ? `text-${color}-400` : "text-white"}`}>
        {value}
      </div>
    </div>
  );
}

function CasesList() {
  const { metrics } = useDashboardMetrics();

  return (
    <div className="mt-8">
      <h2 className="text-xl font-semibold mb-4">Active Cases</h2>
      <div className="text-gray-500 text-sm">
        Launch a demo case or create a new request to get started.
      </div>
    </div>
  );
}
