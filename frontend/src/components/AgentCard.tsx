import { Brain, CheckCircle2, Clock, Ban, AlertCircle } from "lucide-react";

interface AgentCardProps {
  name: string;
  role: string;
  status: "pending" | "assessing" | "completed" | "unavailable";
  confidence?: number;
  recommendation?: string;
}

const STATUS_CONFIG = {
  pending: {
    icon: Clock,
    color: "text-text-muted",
    bg: "bg-surface-4",
    border: "border-border",
    label: "Pending",
  },
  assessing: {
    icon: Brain,
    color: "text-blue-400",
    bg: "bg-blue-500/5",
    border: "border-blue-500/20",
    label: "Assessing",
  },
  completed: {
    icon: CheckCircle2,
    color: "text-emerald-400",
    bg: "bg-emerald-500/5",
    border: "border-emerald-500/20",
    label: "Completed",
  },
  unavailable: {
    icon: Ban,
    color: "text-red-400",
    bg: "bg-red-500/5",
    border: "border-red-500/20",
    label: "Unavailable",
  },
};

export function AgentCard({
  name,
  role,
  status,
  confidence,
  recommendation,
}: AgentCardProps) {
  const cfg = STATUS_CONFIG[status];

  return (
    <div
      className={`rounded-xl border p-4 transition-all duration-300 ${cfg.bg} ${cfg.border}`}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2.5">
          <div className={`w-8 h-8 rounded-lg bg-surface-4 flex items-center justify-center ${cfg.color}`}>
            <cfg.icon size={16} />
          </div>
          <div>
            <h4 className="text-sm font-semibold text-text-primary">{name}</h4>
            <p className="text-xs text-text-muted">{role}</p>
          </div>
        </div>
        <span className={`text-[10px] font-medium ${cfg.color}`}>
          {cfg.label}
        </span>
      </div>

      {status === "assessing" && (
        <div className="flex items-center gap-2 text-xs text-text-muted">
          <AlertCircle size={12} className="text-blue-400 animate-pulse" />
          <span>Consulting knowledge base...</span>
        </div>
      )}

      {confidence !== undefined && (
        <div className="mb-2">
          <div className="flex items-center justify-between text-xs mb-1">
            <span className="text-text-muted">Confidence</span>
            <span className="font-medium text-text-primary">
              {(confidence * 100).toFixed(0)}%
            </span>
          </div>
          <div className="h-1.5 rounded-full bg-surface-4 overflow-hidden">
            <div
              className="h-full rounded-full bg-brand-500 transition-all duration-500"
              style={{ width: `${confidence * 100}%` }}
            />
          </div>
        </div>
      )}

      {recommendation && (
        <p className="text-xs text-text-secondary leading-relaxed line-clamp-2">
          {recommendation}
        </p>
      )}
    </div>
  );
}
