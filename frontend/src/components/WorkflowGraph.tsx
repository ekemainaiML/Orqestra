import { CheckCircle2, Circle, Loader2, Users } from "lucide-react";

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

export function WorkflowGraph({
  status,
  departments,
}: {
  status: string;
  departments?: Array<{ id: string; role: string }>;
}) {
  const currentIdx = WORKFLOW_STATES.findIndex((s) => s.key === status);
  const indeIdx = WORKFLOW_STATES.findIndex((s) => s.key === "independent_assessment");
  const adjIdx = WORKFLOW_STATES.findIndex((s) => s.key === "adjudication");
  const isInDepartmentsPhase = currentIdx >= indeIdx && currentIdx < adjIdx;
  const inDept =
    isInDepartmentsPhase ? currentIdx - indeIdx : -1;

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

      {departments && departments.length > 0 && (
        <div className="mt-4 pt-4 border-t border-border">
          <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3 flex items-center gap-1.5">
            <Users size={12} />
            Departments
          </h3>
          <div className="space-y-1.5">
            {departments.map((d, i) => {
              const isDone = i < inDept;
              const isActive = i === inDept;
              return (
                <div key={d.id} className="flex items-center gap-2 px-1">
                  <div
                    className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                      isDone
                        ? "bg-brand-500"
                        : isActive
                          ? "bg-brand-400 animate-pulse"
                          : "bg-border"
                    }`}
                  />
                  <span
                    className={`text-xs ${
                      isDone || isActive
                        ? "text-text-primary font-medium"
                        : "text-text-muted"
                    }`}
                  >
                    {d.role}
                  </span>
                  {isActive && (
                    <Loader2 size={10} className="animate-spin text-brand-400 shrink-0" />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
