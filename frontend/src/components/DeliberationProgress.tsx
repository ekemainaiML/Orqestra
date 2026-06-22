import type { WorkflowEvent } from "@/lib/types";
import {
  Loader2,
  Brain,
  MessageSquare,
  Sword,
  BarChart3,
  Scale,
  CheckCircle2,
} from "lucide-react";

const STEPS = [
  { event: "memory_retrieved", label: "Memory", icon: Brain },
  { event: "recommendation_submitted", label: "Assessment", icon: MessageSquare },
  { event: "challenge_issued", label: "Challenge", icon: Sword },
  { event: "consensus_calculated", label: "Consensus", icon: BarChart3 },
  { event: "decision_generated", label: "Adjudication", icon: Scale },
  { event: "brief_presented", label: "Approval", icon: CheckCircle2 },
];

const STEP_MAP: Record<string, { label: string; icon: typeof Loader2 }> = {};
for (const s of STEPS) {
  STEP_MAP[s.event] = { label: s.label, icon: s.icon };
}

export function DeliberationProgress({ events }: { events: WorkflowEvent[] }) {
  const latest = events.length > 0 ? events[events.length - 1] : null;
  const step = latest ? STEP_MAP[latest.event_type] ?? null : null;
  const recent = events.slice(-10).reverse();

  const currentStepIdx = latest
    ? STEPS.findIndex((s) => s.event === latest.event_type)
    : -1;
  const percent =
    currentStepIdx >= 0
      ? Math.round(((currentStepIdx + 1) / STEPS.length) * 100)
      : 0;

  return (
    <div className="card border-brand-500/30 bg-brand-500/5">
      <div className="flex items-center gap-2 mb-3">
        <Loader2 size={14} className="animate-spin text-brand-400" />
        <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">
          Deliberation in Progress
        </span>
        <span className="text-xs text-text-muted ml-auto">{percent}%</span>
      </div>

      <div className="flex items-center gap-1 mb-4">
        {STEPS.map((s, i) => {
          const done = i <= currentStepIdx;
          const active = i === currentStepIdx;
          return (
            <div key={s.event} className="flex-1 flex flex-col items-center gap-1">
              <div
                className={`w-full h-1 rounded-full transition-colors ${
                  active
                    ? "bg-brand-500"
                    : done
                      ? "bg-brand-500/40"
                      : "bg-surface-4"
                }`}
              />
              <div className="flex items-center gap-1">
                {active && <Loader2 size={8} className="animate-spin text-brand-400" />}
                <span
                  className={`text-[10px] font-medium ${
                    active ? "text-brand-400" : done ? "text-text-muted" : "text-text-muted/40"
                  }`}
                >
                  {s.label}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {step && latest && (
        <div className="flex items-center gap-2 mb-3 p-2 rounded-lg bg-surface-4/50">
          <step.icon size={16} className="text-brand-400" />
          <span className="text-sm font-medium text-text-primary">{step.label}</span>
          {latest.actor && (
            <span className="text-xs text-text-muted">
              &middot; Currently consulting <strong>{latest.actor as string}</strong>
            </span>
          )}
        </div>
      )}

      <div className="space-y-1 max-h-40 overflow-y-auto scrollbar-thin">
        {recent.map((evt) => (
          <div
            key={evt.id}
            className="flex items-center gap-2 text-xs py-1 border-l-2 border-border pl-3"
          >
            <span className="tag-default !border-0 !px-1 text-[10px] shrink-0">
              {evt.event_type}
            </span>
            <span className="text-text-secondary truncate">{evt.actor}</span>
            <span className="text-text-muted ml-auto shrink-0">
              {evt.timestamp
                ? new Date(evt.timestamp).toLocaleTimeString()
                : ""}
            </span>
          </div>
        ))}
        {events.length === 0 && (
          <p className="text-xs text-text-muted py-2">
            Waiting for agents to respond...
          </p>
        )}
      </div>
    </div>
  );
}
