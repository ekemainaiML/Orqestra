import { CheckCircle2, Circle, Loader2 } from "lucide-react";

const WORKFLOW_STATES = [
  { key: "created", label: "Created" },
  { key: "memory_retrieval", label: "Memory Retrieval" },
  { key: "independent_assessment", label: "Assessment" },
  { key: "challenge_round", label: "Challenge Round" },
  { key: "consensus_scoring", label: "Consensus Scoring" },
  { key: "adjudication", label: "Adjudication" },
  { key: "approval_pending", label: "Approval" },
  { key: "completed", label: "Completed" },
];

export function WorkflowGraph({ status }: { status: string }) {
  const currentIdx = WORKFLOW_STATES.findIndex((s) => s.key === status);

  return (
    <div>
      <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-4">
        Workflow Progress
      </h3>
      <div className="relative">
        {WORKFLOW_STATES.map((state, i) => {
          const isCompleted = i < currentIdx;
          const isCurrent = i === currentIdx;
          return (
            <div key={state.key} className="flex items-start gap-3 relative pb-5 last:pb-0">
              {i < WORKFLOW_STATES.length - 1 && (
                <div
                  className={`absolute left-[11px] top-5 w-0.5 h-full -z-0 ${
                    isCompleted ? "bg-brand-500/40" : "bg-border"
                  }`}
                />
              )}
              <div className="relative z-10 mt-0.5">
                {isCompleted ? (
                  <CheckCircle2 size={22} className="text-brand-500" />
                ) : isCurrent ? (
                  <div className="relative">
                    <Circle size={22} className="text-brand-400" />
                    <Loader2
                      size={22}
                      className="absolute inset-0 text-brand-400 animate-spin"
                    />
                  </div>
                ) : (
                  <Circle size={22} className="text-border-2" />
                )}
              </div>
              <div className="flex-1 min-w-0 pt-0.5">
                <span
                  className={`text-sm font-medium ${
                    isCompleted
                      ? "text-text-primary"
                      : isCurrent
                        ? "text-brand-400"
                        : "text-text-muted"
                  }`}
                >
                  {state.label}
                </span>
                {isCurrent && status !== "completed" && (
                  <span className="block text-[10px] text-text-muted mt-0.5 uppercase tracking-wider">
                    In Progress
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
