import type { DashboardMetrics } from "@/lib/types";

interface HealthMetricsProps {
  metrics: DashboardMetrics;
}

export function HealthMetrics({ metrics }: HealthMetricsProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      <MetricItem label="Cases Today" value={metrics.cases_today} />
      <MetricItem label="Completed" value={metrics.completed_cases} />
      <MetricItem label="Escalated" value={metrics.escalated_cases} />
      <MetricItem
        label="Avg Confidence"
        value={`${(metrics.average_confidence * 100).toFixed(0)}%`}
      />
    </div>
  );
}

function MetricItem({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="bg-gray-800 rounded p-3">
      <div className="text-xs text-gray-500">{label}</div>
      <div className="text-lg font-semibold text-white mt-0.5">{value}</div>
    </div>
  );
}
