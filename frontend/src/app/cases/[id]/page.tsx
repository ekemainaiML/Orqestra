"use client";
import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { useCaseEvents } from "@/hooks/useCaseEvents";
import type { CaseDetail, DeliberationResult, WorkflowEvent } from "@/lib/types";
import { StatusBadge } from "@/components/StatusBadge";
import { WorkflowGraph } from "@/components/WorkflowGraph";
import { DecisionBoard } from "@/components/DecisionBoard";
import { DeliberationProgress } from "@/components/DeliberationProgress";
import { DepartmentAssessments } from "@/components/DepartmentAssessments";
import { DirectivePanel } from "@/components/DirectivePanel";
import {
  Play,
  CheckCircle,
  XCircle,
  Edit3,
  Loader2,
  Clock,
  FileText,
  BarChart3,
  RotateCcw,
} from "lucide-react";
import Link from "next/link";

export default function CaseDetailPage() {
  const params = useParams();
  const caseId = params.id as string;
  const [caseData, setCaseData] = useState<CaseDetail | null>(null);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<DeliberationResult | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [workflowName, setWorkflowName] = useState("");
  const [workflowDepartments, setWorkflowDepartments] = useState<Array<{ id: string; role: string }> | undefined>(undefined);
  const liveEvents = useCaseEvents(caseId);

  useEffect(() => {
    api.cases.get(caseId).then((c) => {
      setCaseData(c);
      api.workflows.list().then((r) => {
        const wf = r.workflows.find((w) => w.id === c.workflow_type);
        if (wf) {
          setWorkflowName(wf.name);
          setWorkflowDepartments(wf.departments);
        }
      }).catch(() => {});
    });
  }, [caseId]);

  const [runError, setRunError] = useState<string | null>(null);

  const handleRun = useCallback(async () => {
    setRunning(true);
    setRunError(null);
    try {
      const r = await api.cases.run(caseId);
      setResult(r);
      const updated = await api.cases.get(caseId);
      setCaseData(updated);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Unknown error";
      setRunError(msg);
      console.error("Deliberation run failed:", err);
    } finally {
      setRunning(false);
    }
  }, [caseId]);

  const handleAction = useCallback(
    async (action: string, fn: () => Promise<unknown>) => {
      setActionLoading(action);
      try {
        await fn();
        const updated = await api.cases.get(caseId);
        setCaseData(updated);
      } finally {
        setActionLoading(null);
      }
    },
    [caseId]
  );

  if (!caseData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center gap-3 text-text-muted">
          <Loader2 size={20} className="animate-spin" />
          <span className="text-sm">Loading case...</span>
        </div>
      </div>
    );
  }

  const allEvents = [...caseData.events, ...liveEvents].filter(
    (e, i, a) => a.findIndex((x) => x.id === e.id) === i
  ) as WorkflowEvent[];

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h1 className="text-2xl font-bold text-text-primary font-mono">
              {caseId.slice(0, 8)}
            </h1>
            <StatusBadge status={caseData.status} />
            <span className="text-xs text-text-muted">
              {workflowName || caseData.workflow_type}
            </span>
            <span className="text-xs text-text-muted">
              Iteration {caseData.iteration}
            </span>
          </div>
          <p className="text-sm text-text-secondary leading-relaxed max-w-2xl">
            {caseData.request_text}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2 flex-wrap">
        {(caseData.status === "created" ||
          caseData.status === "approval_pending" ||
          caseData.status === "adjudication") && (
          <button
            onClick={handleRun}
            disabled={running}
            className="btn-primary flex items-center gap-1.5"
          >
            {running ? (
              <Loader2 size={14} className="animate-spin" />
            ) : (
              <Play size={14} />
            )}
            {running
              ? "Running..."
              : caseData.status === "created"
                ? "Run Deliberation"
                : "Continue Deliberation"}
          </button>
        )}
        {caseData.status === "approval_pending" && (
          <>
            <button
              onClick={() =>
                handleAction("approve", () => api.cases.approve(caseId))
              }
              disabled={actionLoading === "approve"}
              className="btn-success flex items-center gap-1.5"
            >
              {actionLoading === "approve" ? (
                <Loader2 size={14} className="animate-spin" />
              ) : (
                <CheckCircle size={14} />
              )}
              Approve
            </button>
            <button
              onClick={() =>
                handleAction("reject", () => api.cases.reject(caseId))
              }
              disabled={actionLoading === "reject"}
              className="btn-danger flex items-center gap-1.5"
            >
              {actionLoading === "reject" ? (
                <Loader2 size={14} className="animate-spin" />
              ) : (
                <XCircle size={14} />
              )}
              Reject
            </button>
            <button
              onClick={() =>
                handleAction("modify", () =>
                  api.cases.modify(caseId, {
                    minimum_margin: 20,
                    priority: "delivery",
                  })
                )
              }
              disabled={actionLoading === "modify"}
              className="btn-secondary flex items-center gap-1.5"
            >
              {actionLoading === "modify" ? (
                <Loader2 size={14} className="animate-spin" />
              ) : (
                <Edit3 size={14} />
              )}
              Modify
            </button>
          </>
        )}
      </div>

      {runError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Deliberation failed: {runError}
        </div>
      )}

      {running && (
        <DeliberationProgress events={liveEvents} />
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="space-y-5">
          <div className="card">
            <WorkflowGraph status={caseData.status} departments={workflowDepartments} />
          </div>
          <div className="card">
            <DirectivePanel caseId={caseId} iteration={caseData.iteration} />
          </div>
          <div className="card">
            <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-4">
              Case Info
            </h3>
            <div className="space-y-2.5 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-text-muted">Created</span>
                <span className="text-text-primary">
                  {caseData.created_at
                    ? new Date(caseData.created_at).toLocaleDateString()
                    : "--"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-text-muted">Confidence</span>
                <span
                  className={`font-medium ${
                    caseData.confidence !== null
                      ? caseData.confidence >= 0.7
                        ? "text-emerald-400"
                        : caseData.confidence >= 0.4
                          ? "text-amber-400"
                          : "text-red-400"
                      : "text-text-muted"
                  }`}
                >
                  {caseData.confidence !== null
                    ? `${(caseData.confidence * 100).toFixed(0)}%`
                    : "--"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-text-muted">Events</span>
                <span className="text-text-primary font-mono">
                  {caseData.events.length}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 space-y-5">
          {result && (
            <div className="card">
              <DecisionBoard result={result} />
            </div>
          )}

          {allEvents.length > 0 && (
            <div className="card">
              <DepartmentAssessments events={allEvents} />
            </div>
          )}

          <div className="card">
            <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-4">
              Deliberation Timeline
            </h3>
            <div className="space-y-1 max-h-72 overflow-y-auto scrollbar-thin">
              {allEvents.length > 0 ? (
                allEvents.map((evt, i) => (
                  <div
                    key={evt.id || i}
                    className="flex items-start gap-3 py-2 text-xs border-l-2 border-border pl-3 hover:border-brand-500/30 transition-colors"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="tag-default !border-0 !px-1.5 text-[10px]">
                          {evt.event_type as string}
                        </span>
                        <span className="font-medium text-text-primary">
                          {evt.actor as string}
                        </span>
                      </div>
                      {evt.payload && (
                        <p className="text-text-muted mt-0.5 truncate">
                          {JSON.stringify(evt.payload).substring(0, 120)}
                        </p>
                      )}
                    </div>
                    <span className="text-text-muted shrink-0">
                      {evt.timestamp
                        ? new Date(evt.timestamp as string).toLocaleTimeString()
                        : ""}
                    </span>
                  </div>
                ))
              ) : (
                <div className="flex items-center gap-2 text-text-muted py-4">
                  <Clock size={14} />
                  <span>No events yet. Run deliberation to start.</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2 border-t border-border pt-5">
        <Link
          href={`/cases/${caseId}/audit`}
          className="btn-ghost flex items-center gap-1.5"
        >
          <FileText size={14} />
          Audit Trail
        </Link>
        <Link
          href={`/cases/${caseId}/benchmark`}
          className="btn-ghost flex items-center gap-1.5"
        >
          <BarChart3 size={14} />
          Benchmark
        </Link>
        <Link
          href={`/cases/${caseId}/replay`}
          className="btn-ghost flex items-center gap-1.5"
        >
          <RotateCcw size={14} />
          Replay
        </Link>
      </div>
    </div>
  );
}
