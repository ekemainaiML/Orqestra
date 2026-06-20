"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import type { CaseDetail, WorkflowEvent } from "@/lib/types";
import { StatusBadge } from "@/components/StatusBadge";
import {
  ArrowLeft,
  Clock,
  ChevronDown,
  ChevronRight,
  Search,
  Loader2,
} from "lucide-react";

const EVENT_ICONS: Record<string, string> = {
  case_created: "📋",
  deliberation_started: "🚀",
  memory_retrieved: "🧠",
  agent_assessment: "📝",
  challenge_submitted: "⚔️",
  consensus_reached: "🤝",
  adjudication: "⚖️",
  approval: "✅",
  rejection: "❌",
  modification: "📐",
  completed: "🎯",
  escalated: "🚨",
};

export default function AuditPage() {
  const params = useParams();
  const caseId = params.id as string;
  const [caseData, setCaseData] = useState<CaseDetail | null>(null);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    api.cases.get(caseId).then(setCaseData);
  }, [caseId]);

  if (!caseData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center gap-3 text-text-muted">
          <Loader2 size={20} className="animate-spin" />
          <span className="text-sm">Loading audit trail...</span>
        </div>
      </div>
    );
  }

  const filtered =
    searchQuery.trim() === ""
      ? caseData.events
      : caseData.events.filter(
          (e) =>
            e.event_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
            e.actor.toLowerCase().includes(searchQuery.toLowerCase()) ||
            JSON.stringify(e.payload)
              .toLowerCase()
              .includes(searchQuery.toLowerCase())
        );

  const toggleExpand = (id: string) => {
    const next = new Set(expanded);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setExpanded(next);
  };

  const byIteration = filtered.reduce<
    Record<number, WorkflowEvent[]>
  >((acc, e) => {
    const it = e.iteration ?? 1;
    if (!acc[it]) acc[it] = [];
    acc[it].push(e);
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      <div>
        <Link
          href={`/cases/${caseId}`}
          className="btn-ghost inline-flex items-center gap-1.5 mb-3"
        >
          <ArrowLeft size={14} />
          Back to Case
        </Link>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-text-primary">
              Audit Trail
            </h1>
            <p className="text-sm text-text-muted mt-1">
              Case <span className="font-mono">{caseId.slice(0, 8)}</span>
              &nbsp;&middot;&nbsp;{caseData.events.length} events
              &nbsp;&middot;&nbsp;
              <StatusBadge status={caseData.status} />
            </p>
          </div>
          <div className="relative w-64">
            <Search
              size={14}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted"
            />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter events..."
              className="input pl-9 text-sm"
            />
          </div>
        </div>
      </div>

      <div className="space-y-6">
        {Object.entries(byIteration)
          .sort(([a], [b]) => Number(b) - Number(a))
          .map(([iteration, events]) => (
            <div key={iteration}>
              <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3 flex items-center gap-2">
                <Clock size={14} />
                Iteration {iteration}
                <span className="text-text-muted font-normal normal-case">
                  ({events.length} events)
                </span>
              </h3>
              <div className="space-y-1.5">
                {events.map((evt) => {
                  const isExpanded = expanded.has(evt.id);
                  return (
                    <div
                      key={evt.id}
                      className="card !p-0 overflow-hidden group"
                    >
                      <button
                        onClick={() => toggleExpand(evt.id)}
                        className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-surface-4/50 transition-colors"
                      >
                        <span className="text-base">
                          {EVENT_ICONS[evt.event_type] ?? "📄"}
                        </span>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-mono bg-surface-4 px-1.5 py-0.5 rounded text-brand-400">
                              {evt.event_type}
                            </span>
                            <span className="text-sm text-text-primary font-medium">
                              {evt.actor}
                            </span>
                          </div>
                        </div>
                        <span className="text-xs text-text-muted shrink-0">
                          {evt.timestamp
                            ? new Date(evt.timestamp).toLocaleTimeString()
                            : ""}
                        </span>
                        {evt.payload &&
                          (isExpanded ? (
                            <ChevronDown size={14} className="text-text-muted" />
                          ) : (
                            <ChevronRight size={14} className="text-text-muted" />
                          ))}
                      </button>
                      {evt.payload && isExpanded && (
                        <div className="px-4 pb-3 pt-0 border-t border-border">
                          <pre className="text-xs text-text-secondary overflow-x-auto mt-2 max-h-48 overflow-y-auto scrollbar-thin">
                            {JSON.stringify(evt.payload, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}

        {filtered.length === 0 && (
          <div className="card p-8 text-center">
            <Search size={20} className="text-text-muted mx-auto mb-3" />
            <p className="text-sm text-text-muted">
              {searchQuery
                ? "No events match your filter."
                : "No events recorded for this case."}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
