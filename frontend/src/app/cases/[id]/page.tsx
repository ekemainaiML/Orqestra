"use client";
import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { useCaseEvents } from "@/hooks/useCaseEvents";
import type { CaseDetail, DeliberationResult, WorkflowEvent, ToolResults } from "@/lib/types";
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
  MessageSquare,
  ShieldAlert,
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
  const [toolResults, setToolResults] = useState<ToolResults | null>(null);
  const liveEvents = useCaseEvents(caseId);

  const [clarification, setClarification] = useState<{
    questions: string[];
    completeness: number;
  } | null>(null);
  const [clarifyAnswers, setClarifyAnswers] = useState<Record<string, string>>({});
  const [clarifySending, setClarifySending] = useState(false);

  const [recoveryCheck, setRecoveryCheck] = useState<{
    can_continue: boolean;
    degraded_mode: boolean;
    reasons: string[];
    checks: Record<string, boolean>;
  } | null>(null);
  const [recoveryLoading, setRecoveryLoading] = useState(false);

  const eventToState: Record<string, string> = {
    memory_retrieved: "memory_retrieval",
    recommendation_submitted: "independent_assessment",
    challenge_issued: "challenge_round",
    consensus_calculated: "consensus_scoring",
    decision_generated: "adjudication",
    brief_presented: "approval_pending",
  };
  const liveStatus = liveEvents.reduce((maxState, evt) => {
    const s = eventToState[evt.event_type];
    if (!s) return maxState;
    const order = ["created", "memory_retrieval", "independent_assessment", "challenge_round", "consensus_scoring", "adjudication", "approval_pending", "completed"];
    return order.indexOf(s) > order.indexOf(maxState) ? s : maxState;
  }, running ? "created" : (caseData?.status || "created"));

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
    api.cases.toolResults(caseId).then(setToolResults).catch(() => {});
  }, [caseId]);

  useEffect(() => {
    if (caseData?.status && caseData.status !== "created") {
      api.cases.toolResults(caseId).then(setToolResults).catch(() => {});
    }
  }, [caseId, caseData?.status]);

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

  const handleClarify = useCallback(async () => {
    setActionLoading("clarify");
    try {
      const result = await api.cases.clarify(caseId);
      if (result.questions && result.questions.length > 0) {
        setClarification({ questions: result.questions, completeness: result.completeness });
        setClarifyAnswers({});
      }
      const updated = await api.cases.get(caseId);
      setCaseData(updated);
    } finally {
      setActionLoading(null);
    }
  }, [caseId]);

  const handleClarifyRespond = useCallback(async () => {
    if (!clarification || Object.keys(clarifyAnswers).length === 0) return;
    setClarifySending(true);
    try {
      await api.cases.respondClarify(caseId, clarifyAnswers);
      setClarification(null);
      setClarifyAnswers({});
      const updated = await api.cases.get(caseId);
      setCaseData(updated);
    } finally {
      setClarifySending(false);
    }
  }, [caseId, clarification, clarifyAnswers]);

  const handleRecoveryCheck = useCallback(async () => {
    setRecoveryLoading(true);
    try {
      const result = await api.cases.recoveryCheck(caseId);
      setRecoveryCheck(result);
    } finally {
      setRecoveryLoading(false);
    }
  }, [caseId]);

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
      {clarification && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-[var(--color-surface-2)] rounded-xl border border-border shadow-2xl p-6 max-w-lg w-full mx-4">
            <div className="flex items-center gap-2 mb-4">
              <MessageSquare size={18} className="text-brand-400" />
              <h2 className="text-lg font-semibold text-text-primary">Clarification Required</h2>
            </div>
            <p className="text-sm text-text-secondary mb-4">
              The request needs additional information before deliberation can proceed
              (completeness: {(clarification.completeness * 100).toFixed(0)}%).
            </p>
            <div className="space-y-3 mb-4">
              {clarification.questions.map((q, i) => (
                <div key={i}>
                  <label className="text-xs font-medium text-text-primary mb-1 block">{q}</label>
                  <textarea
                    value={clarifyAnswers[q] || ""}
                    onChange={(e) => setClarifyAnswers((prev) => ({ ...prev, [q]: e.target.value }))}
                    className="input text-sm w-full h-20 resize-none"
                    placeholder="Your answer..."
                  />
                </div>
              ))}
            </div>
            <div className="flex items-center justify-end gap-2">
              <button
                onClick={() => setClarification(null)}
                className="btn-ghost text-xs"
              >
                Cancel
              </button>
              <button
                onClick={handleClarifyRespond}
                disabled={clarifySending || Object.keys(clarifyAnswers).length === 0}
                className="btn-primary text-xs flex items-center gap-1.5"
              >
                {clarifySending ? <Loader2 size={12} className="animate-spin" /> : <CheckCircle size={12} />}
                Submit Answers
              </button>
            </div>
          </div>
        </div>
      )}

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
        {caseData.status !== "clarification_required" && (
          <button
            onClick={handleClarify}
            disabled={actionLoading === "clarify"}
            className="btn-ghost flex items-center gap-1.5"
          >
            {actionLoading === "clarify" ? (
              <Loader2 size={14} className="animate-spin" />
            ) : (
              <MessageSquare size={14} />
            )}
            Check Clarity
          </button>
        )}
        <button
          onClick={handleRecoveryCheck}
          disabled={recoveryLoading}
          className="btn-ghost flex items-center gap-1.5"
        >
          {recoveryLoading ? (
            <Loader2 size={14} className="animate-spin" />
          ) : (
            <ShieldAlert size={14} />
          )}
          Health Check
        </button>
      </div>

      {recoveryCheck && (
        <div className={`rounded-lg border p-3 ${
          recoveryCheck.can_continue
            ? "border-emerald-500/30 bg-emerald-500/5"
            : "border-red-500/30 bg-red-500/5"
        }`}>
          <div className="flex items-center gap-2 mb-1">
            {recoveryCheck.can_continue ? (
              <CheckCircle size={14} className="text-emerald-400" />
            ) : (
              <XCircle size={14} className="text-red-400" />
            )}
            <span className={`text-sm font-medium ${recoveryCheck.can_continue ? "text-emerald-400" : "text-red-400"}`}>
              {recoveryCheck.can_continue
                ? recoveryCheck.degraded_mode ? "Degraded — can continue" : "Healthy — can continue"
                : "Cannot continue"}
            </span>
            <button onClick={() => setRecoveryCheck(null)} className="ml-auto text-text-muted hover:text-text-primary text-xs">
              Dismiss
            </button>
          </div>
          {recoveryCheck.reasons.length > 0 && (
            <ul className="mt-1 space-y-0.5">
              {recoveryCheck.reasons.map((r, i) => (
                <li key={i} className="text-xs text-text-muted flex items-start gap-1.5">
                  <span className="mt-0.5">•</span>
                  {r}
                </li>
              ))}
            </ul>
          )}
          {recoveryCheck.degraded_mode && (
            <p className="text-xs text-amber-400 mt-1">
              System operating in degraded mode — some non-critical departments are below confidence thresholds.
            </p>
          )}
        </div>
      )}

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
            <WorkflowGraph status={running ? liveStatus : caseData.status} departments={workflowDepartments} />
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

          {toolResults && toolResults.tool_count > 0 && (
            <div className="card">
              <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-4">
                Tools Used ({toolResults.tool_count} calls)
              </h3>
              <div className="space-y-3">
                {Object.entries(toolResults.tools).map(([toolName, calls]) => (
                  <div key={toolName}>
                    <div className="flex items-center gap-2 mb-2">
                      <code className="text-xs bg-brand-500/10 text-brand-300 px-1.5 py-0.5 rounded font-mono">
                        {toolName}
                      </code>
                      <span className="text-[10px] text-text-muted">{calls.length} call{calls.length > 1 ? "s" : ""}</span>
                    </div>
                    {calls.map((call, i) => {
                      const r = call.result;
                      const source = (r as Record<string, unknown>)?.source as string | undefined;
                      return (
                        <div key={i} className="text-xs bg-surface-3 rounded-lg p-3 mb-1.5 last:mb-0 space-y-1">
                          {source && (
                            <span className={`tag-default !border-0 !px-1.5 text-[10px] ${source === "simulated" ? "!bg-amber-500/10 !text-amber-300" : "!bg-emerald-500/10 !text-emerald-300"}`}>
                              {source}
                            </span>
                          )}
                          <pre className="text-text-muted leading-relaxed whitespace-pre-wrap font-sans">
                            {JSON.stringify(r, null, 1)}
                          </pre>
                        </div>
                      );
                    })}
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="card">
            <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-4">
              Deliberation Timeline
            </h3>
            <div className="space-y-1 max-h-72 overflow-y-auto scrollbar-thin">
              {allEvents.length > 0 ? (
                allEvents.map((evt, i) => {
                  const p = evt.payload as Record<string, unknown> | null;
                  const isToolCall = evt.event_type === "tool_call_executed";
                  const toolName = isToolCall ? (p?.tool as string) : null;
                  return (
                    <div
                      key={evt.id || i}
                      className="flex items-start gap-3 py-2 text-xs border-l-2 pl-3 hover:border-brand-500/30 transition-colors"
                      style={{
                        borderColor: isToolCall ? "var(--color-brand-400)" : "var(--color-border)",
                      }}
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span
                            className={`tag-default !border-0 !px-1.5 text-[10px] ${isToolCall ? "!bg-brand-500/10 !text-brand-400" : ""}`}
                          >
                            {evt.event_type as string}
                          </span>
                          <span className="font-medium text-text-primary">
                            {evt.actor as string}
                          </span>
                        </div>
                        {isToolCall && toolName ? (
                          <div className="flex items-center gap-1.5 mt-0.5">
                            <code className="text-[11px] bg-surface-3 px-1.5 py-0.5 rounded font-mono text-brand-300">
                              {toolName}
                            </code>
                            <span className="text-text-muted truncate">
                              {JSON.stringify(p?.arguments).substring(0, 80)}
                            </span>
                          </div>
                        ) : p ? (
                          <p className="text-text-muted mt-0.5 truncate">
                            {JSON.stringify(p).substring(0, 120)}
                          </p>
                        ) : null}
                      </div>
                      <span className="text-text-muted shrink-0">
                        {evt.timestamp
                          ? new Date(evt.timestamp as string).toLocaleTimeString()
                          : ""}
                      </span>
                    </div>
                  );
                })
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
