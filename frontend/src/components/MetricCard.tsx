import { TrendingUp, TrendingDown } from "lucide-react";

interface MetricCardProps {
  label: string;
  value: string | number;
  trend?: "up" | "down" | "neutral";
  icon?: React.ReactNode;
  format?: "number" | "percent";
}

export function MetricCard({
  label,
  value,
  trend,
  icon,
}: MetricCardProps) {
  return (
    <div className="card">
      <div className="flex items-start justify-between mb-3">
        <span className="text-xs font-medium text-text-muted uppercase tracking-wider">
          {label}
        </span>
        {icon && (
          <div className="w-8 h-8 rounded-lg bg-brand-500/10 flex items-center justify-center text-brand-400">
            {icon}
          </div>
        )}
      </div>
      <div className="flex items-end gap-2">
        <span className="text-2xl font-bold text-text-primary tracking-tight">
          {value}
        </span>
        {trend && (
          <span
            className={`flex items-center text-xs font-medium mb-0.5 ${
              trend === "up"
                ? "text-emerald-400"
                : trend === "down"
                  ? "text-red-400"
                  : "text-text-muted"
            }`}
          >
            {trend === "up" ? (
              <TrendingUp size={14} className="mr-0.5" />
            ) : (
              <TrendingDown size={14} className="mr-0.5" />
            )}
          </span>
        )}
      </div>
    </div>
  );
}
