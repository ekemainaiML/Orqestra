"use client";
import { useState } from "react";
import { ChevronDown, ChevronRight, AlertTriangle, CheckCircle2, TrendingUp, TrendingDown } from "lucide-react";
import type { WorkflowEvent } from "@/lib/types";

interface RecPayload {
  recommendation: string;
  confidence: number;
  reasoning: string;
  risks: string[];
  factors: string[];
  agent_id: string;
}

const EXECUTIVE_ROLES = new Set(["operations_manager", "procurement_director"]);

export function DepartmentAssessments({ events }: { events: WorkflowEvent[] }) {
  const recs = events
    .filter((e) => e.event_type === "recommendation_submitted")
    .map((e) => ({ id: e.id, actor: e.actor, payload: e.payload as unknown as RecPayload, timestamp: e.timestamp }));

  if (recs.length === 0) return null;

  const avgConfidence =
    recs.reduce((s, r) => s + (r.payload?.confidence ?? 0), 0) / recs.length;
  const dissenting = recs.filter(
    (r) => (r.payload?.confidence ?? 0) < avgConfidence - 0.15
  );

  const executive = recs.find((r) => EXECUTIVE_ROLES.has(r.actor));
  const operational = recs.filter((r) => !EXECUTIVE_ROLES.has(r.actor));

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider">
          Department Assessments
        </h3>
        {dissenting.length > 0 && (
          <span className="tag tag-warning text-[10px] flex items-center gap-1">
            <AlertTriangle size={10} />
            {dissenting.length} dissenting
          </span>
        )}
      </div>

      <div className="space-y-2">
        {operational.map((rec) => (
          <DepartmentCard key={rec.id} rec={rec} avgConfidence={avgConfidence} />
        ))}
      </div>

      {executive && (
        <>
          <div className="border-t border-border my-3" />
          <div>
            <h4 className="text-[10px] font-semibold text-text-muted uppercase tracking-wider mb-2">
              Executive Decision
            </h4>
            <DepartmentCard rec={executive} avgConfidence={avgConfidence} isExecutive />
          </div>
        </>
      )}
    </div>
  );
}

function DepartmentCard({
  rec,
  avgConfidence,
  isExecutive,
}: {
  rec: { actor: string; payload: RecPayload; timestamp: string | null };
  avgConfidence: number;
  isExecutive?: boolean;
}) {
  const [expanded, setExpanded] = useState(false);
  const p = rec.payload;
  if (!p) return null;

  const isDissenting = !isExecutive && p.confidence < avgConfidence - 0.15;
  const displayName = p.agent_id
    ? p.agent_id.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())
    : rec.actor.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

  return (
    <div
      className={`card p-3 ${
        isDissenting
          ? "border-amber-500/30"
          : isExecutive
            ? "border-brand-500/20"
            : ""
      }`}
    >
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-start gap-2 text-left"
      >
        <div className="mt-0.5">
          {expanded ? (
            <ChevronDown size={14} className="text-text-muted" />
          ) : (
            <ChevronRight size={14} className="text-text-muted" />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-text-primary">{displayName}</span>
            {isDissenting && (
              <span className="tag tag-warning text-[10px] flex items-center gap-0.5">
                <AlertTriangle size={9} />
                Dissenting
              </span>
            )}
            {isExecutive && (
              <span className="tag tag-info text-[10px]">Executive</span>
            )}
          </div>
          <p className="text-sm text-text-secondary mt-0.5 line-clamp-2">
            {p.recommendation}
          </p>
          <div className="flex items-center gap-3 mt-1.5">
            <ConfidenceBadge value={p.confidence} />
            {p.risks && p.risks.length > 0 && (
              <span className="text-xs text-text-muted">
                {p.risks.length} risk{p.risks.length !== 1 ? "s" : ""}
              </span>
            )}
            {p.factors && p.factors.length > 0 && (
              <span className="text-xs text-text-muted">
                {p.factors.length} factor{p.factors.length !== 1 ? "s" : ""}
              </span>
            )}
          </div>
        </div>
      </button>

      {expanded && (
        <div className="mt-3 pt-3 border-t border-border space-y-3">
          {p.reasoning && (
            <div>
              <h5 className="text-[10px] font-semibold text-text-muted uppercase tracking-wider mb-1">
                Reasoning
              </h5>
              <p className="text-xs text-text-secondary leading-relaxed whitespace-pre-wrap">
                {p.reasoning}
              </p>
            </div>
          )}

          {p.risks && p.risks.length > 0 && (
            <div>
              <h5 className="text-[10px] font-semibold text-text-muted uppercase tracking-wider mb-1">
                Risks
              </h5>
              <ul className="space-y-0.5">
                {p.risks.map((risk, i) => (
                  <li key={i} className="text-xs text-red-400 flex items-start gap-1.5">
                    <AlertTriangle size={10} className="mt-0.5 shrink-0" />
                    {risk}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {p.factors && p.factors.length > 0 && (
            <div>
              <h5 className="text-[10px] font-semibold text-text-muted uppercase tracking-wider mb-1">
                Factors Considered
              </h5>
              <ul className="space-y-0.5">
                {p.factors.map((factor, i) => (
                  <li key={i} className="text-xs text-text-secondary flex items-start gap-1.5">
                    <CheckCircle2 size={10} className="mt-0.5 text-emerald-400 shrink-0" />
                    {factor}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ConfidenceBadge({ value }: { value: number }) {
  const isHigh = value >= 0.8;
  const isMedium = value >= 0.5;
  return (
    <span
      className={`inline-flex items-center gap-1 text-xs font-medium ${
        isHigh ? "text-emerald-400" : isMedium ? "text-amber-400" : "text-red-400"
      }`}
    >
      {isHigh ? <TrendingUp size={11} /> : isMedium ? <TrendingDown size={11} /> : <AlertTriangle size={11} />}
      {(value * 100).toFixed(0)}% confidence
    </span>
  );
}
