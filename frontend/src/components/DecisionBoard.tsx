import { CheckCircle2, AlertTriangle, Target } from "lucide-react";
import type { DeliberationResult } from "@/lib/types";

interface DecisionBoardProps {
  result: DeliberationResult;
}

export function DecisionBoard({ result }: DecisionBoardProps) {
  const decision = result.decision ?? {};
  const rec = (decision.recommendation as string) ?? "";
  const confidence = (decision.confidence as number) ?? 0;
  const reasoning = (decision.reasoning as string) ?? "";
  const risks = (result.consensus?.risks as string[]) ?? [];

  return (
    <div>
      <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-4">
        Decision Board
      </h3>

      <div className="space-y-4">
        <div className="flex items-center justify-between p-3 rounded-lg bg-surface-4 border border-border-2">
          <div className="flex items-center gap-2.5">
            <Target size={16} className="text-brand-400" />
            <span className="text-sm text-text-secondary">Confidence</span>
          </div>
          <span className="text-lg font-bold text-brand-400">
            {(confidence * 100).toFixed(0)}%
          </span>
        </div>

        {rec && (
          <div>
            <span className="text-xs text-text-muted block mb-1.5">
              Recommendation
            </span>
            <p className="text-sm text-text-primary leading-relaxed">
              {rec}
            </p>
          </div>
        )}

        {reasoning && (
          <div>
            <span className="text-xs text-text-muted block mb-1.5">
              Reasoning
            </span>
            <p className="text-sm text-text-secondary leading-relaxed">
              {reasoning}
            </p>
          </div>
        )}

        {risks.length > 0 && (
          <div>
            <span className="text-xs text-text-muted block mb-1.5">
              Identified Risks
            </span>
            <div className="space-y-1.5">
              {risks.map((r, i) => (
                <div
                  key={i}
                  className="flex items-start gap-2 text-xs text-red-400"
                >
                  <AlertTriangle size={12} className="mt-0.5 shrink-0" />
                  <span>{r}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex items-center gap-2 text-xs text-emerald-400 pt-2 border-t border-border">
          <CheckCircle2 size={14} />
          <span>Consensus achieved across {result.assessment?.recommendations?.length ?? 0} agents</span>
        </div>
      </div>
    </div>
  );
}
