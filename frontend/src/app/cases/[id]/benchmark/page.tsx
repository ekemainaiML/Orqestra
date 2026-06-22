"use client";
import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import type { BenchmarkResult } from "@/lib/types";
import {
  ArrowLeft,
  BarChart3,
  Brain,
  Target,
  AlertTriangle,
  Lightbulb,
  Clock,
  Database,
  Zap,
  Loader2,
  ChevronDown,
  ChevronRight,
} from "lucide-react";

const METRICS = [
  {
    key: "confidence" as const,
    label: "Decision Confidence",
    icon: Target,
    unit: "%",
    format: (v: number) => `${(v * 100).toFixed(0)}%`,
    higher: true,
  },
  {
    key: "risks_found" as const,
    label: "Risks Identified",
    icon: AlertTriangle,
    unit: "",
    format: (v: number) => `${v}`,
    higher: true,
  },
  {
    key: "factors_considered" as const,
    label: "Factors Considered",
    icon: Lightbulb,
    unit: "",
    format: (v: number) => `${v}`,
    higher: true,
  },
  {
    key: "reasoning_time_s" as const,
    label: "Reasoning Time",
    icon: Clock,
    unit: "s",
    format: (v: number) => `${v.toFixed(1)}s`,
    higher: false,
  },
  {
    key: "memory_used" as const,
    label: "Memory Used",
    icon: Database,
    unit: "entries",
    format: (v: number) => `${v}`,
    higher: true,
  },
];

export default function BenchmarkPage() {
  const params = useParams();
  const caseId = params.id as string;
  const [benchmark, setBenchmark] = useState<BenchmarkResult | null>(null);
  const [running, setRunning] = useState(false);
  const [workflowName, setWorkflowName] = useState("");
  const [allWorkflows, setAllWorkflows] = useState<WorkflowSummary[]>([]);
  const [currentWf, setCurrentWf] = useState<string>("");
  const [wfCompareOpen, setWfCompareOpen] = useState(false);

  useEffect(() => {
    api.cases.get(caseId).then((c) => {
      setCurrentWf(c.workflow_type);
      api.workflows.list().then((r) => {
        const wf = r.workflows.find((w) => w.id === c.workflow_type);
        if (wf) setWorkflowName(wf.name);
        setAllWorkflows(r.workflows);
      }).catch(() => {});
    });
  }, [caseId]);

  const load = useCallback(
    () => api.benchmark.get(caseId).then(setBenchmark),
    [caseId]
  );

  useEffect(() => {
    load();
  }, [load]);

  const handleRun = async () => {
    setRunning(true);
    await api.benchmark.run(caseId);
    await load();
    setRunning(false);
  };

  const single = benchmark?.single_agent;
  const org = benchmark?.organization;

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
              Benchmark Comparison
            </h1>
            <p className="text-sm text-text-muted mt-1">
              {workflowName && <>{workflowName} &middot; </>}
              Single-agent baseline vs Orqestra organization
            </p>
          </div>
          <button
            onClick={handleRun}
            disabled={running}
            className="btn-primary flex items-center gap-1.5"
          >
            {running ? (
              <Loader2 size={14} className="animate-spin" />
            ) : (
              <Zap size={14} />
            )}
            {running ? "Running..." : "Run Benchmark"}
          </button>
        </div>
      </div>

      {benchmark?.comparison && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {METRICS.slice(0, 3).map((m) => {
            const sVal = single?.[m.key] ?? 0;
            const oVal = org?.[m.key] ?? 0;
            const gain = (() => {
              switch (m.key) {
                case "confidence":
                  return benchmark.comparison?.confidence_gain ?? 0;
                case "risks_found":
                  return benchmark.comparison?.risk_detection_improvement ?? 0;
                case "factors_considered":
                  return benchmark.comparison?.factors_considered_gain ?? 0;
                default:
                  return oVal - sVal;
              }
            })();
            const Icon = m.icon;

            return (
              <div key={m.key} className="card">
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-8 h-8 rounded-lg bg-brand-500/10 flex items-center justify-center">
                    <Icon size={15} className="text-brand-400" />
                  </div>
                  <span className="text-xs font-medium text-text-muted uppercase tracking-wider">
                    {m.label}
                  </span>
                </div>
                <div className="flex items-end justify-between mb-2">
                  <div className="space-y-0.5">
                    <span className="text-xl font-bold text-text-primary">
                      {m.format(oVal)}
                    </span>
                    <span className="text-xs text-emerald-400 flex items-center gap-0.5 ml-0.5">
                      <Zap size={12} />
                      {gain > 0 ? "+" : ""}
                      {m.key === "confidence"
                        ? `${(gain * 100).toFixed(0)}%`
                        : gain.toFixed(1)}{" "}
                      vs single
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-text-muted block">
                      Single: {m.format(sVal)}
                    </span>
                  </div>
                </div>
                <div className="h-2 rounded-full bg-surface-4 overflow-hidden relative">
                  <div
                    className="h-full rounded-full bg-text-muted/30 absolute left-0 top-0"
                    style={{
                      width: `${Math.min((sVal / Math.max(sVal, oVal)) * 100, 100)}%`,
                    }}
                  />
                  <div
                    className="h-full rounded-full bg-brand-500 absolute left-0 top-0 transition-all duration-500"
                    style={{
                      width: `${Math.min((oVal / Math.max(sVal, oVal)) * 100, 100)}%`,
                      zIndex: 1,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}

      {allWorkflows.length > 1 && (
        <div className="card">
          <button
            type="button"
            onClick={() => setWfCompareOpen(!wfCompareOpen)}
            className="w-full flex items-center gap-2 text-left"
          >
            {wfCompareOpen ? <ChevronDown size={16} className="text-text-muted" /> : <ChevronRight size={16} className="text-text-muted" />}
            <h3 className="text-sm font-semibold text-text-primary">
              Workflow Comparison
            </h3>
            <span className="text-xs text-text-muted">
              {allWorkflows.length} types available
            </span>
          </button>

          {wfCompareOpen && (
            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left font-medium text-text-muted uppercase tracking-wider py-2 pr-4">Metric</th>
                    {allWorkflows.map((wf) => (
                      <th
                        key={wf.id}
                        className={`text-left font-medium py-2 px-3 ${
                          wf.id === currentWf ? "text-brand-400" : "text-text-muted"
                        } uppercase tracking-wider`}
                      >
                        <div className="flex items-center gap-1.5">
                          {wf.id === currentWf && <Zap size={10} />}
                          {wf.name}
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {[
                    { label: "Departments", value: (wf: WorkflowSummary) => wf.departments.length.toString() },
                    { label: "Executive Role", value: (wf: WorkflowSummary) => {
                        const exec = wf.departments.find(d => d.model_tier === "executive");
                        return exec?.role ?? "—";
                      }
                    },
                    { label: "Operational Agents", value: (wf: WorkflowSummary) => {
                        return wf.departments.filter(d => d.model_tier !== "executive").length.toString();
                      }
                    },
                    { label: "Model Tiers", value: (wf: WorkflowSummary) => {
                        const tiers = [...new Set(wf.departments.map(d => d.model_tier))];
                        return tiers.join(", ");
                      }
                    },
                  ].map((row) => (
                    <tr key={row.label} className="hover:bg-surface-4/30">
                      <td className="py-2 pr-4 text-text-secondary font-medium">{row.label}</td>
                      {allWorkflows.map((wf) => (
                        <td
                          key={wf.id}
                          className={`py-2 px-3 ${
                            wf.id === currentWf ? "text-text-primary" : "text-text-muted"
                          }`}
                        >
                          {row.value(wf)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="text-[10px] text-text-muted mt-3">
                <Zap size={10} className="inline" /> Current case workflow
              </p>
            </div>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div className="card">
          <div className="flex items-center gap-2.5 mb-5">
            <div className="w-9 h-9 rounded-lg bg-blue-500/10 flex items-center justify-center">
              <Brain size={18} className="text-blue-400" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-text-primary">
                Single Agent Baseline
              </h3>
              <p className="text-[10px] text-text-muted uppercase tracking-wider">
                Individual LLM Assessment
              </p>
            </div>
          </div>
          {single ? (
            <div className="space-y-3">
              {METRICS.map((m) => {
                const Icon = m.icon;
                const val = single[m.key];
                return (
                  <div
                    key={m.key}
                    className="flex items-center justify-between py-1.5"
                  >
                    <div className="flex items-center gap-2">
                      <Icon size={13} className="text-text-muted" />
                      <span className="text-xs text-text-secondary">
                        {m.label}
                      </span>
                    </div>
                    <span className="text-sm font-mono text-text-primary">
                      {m.format(val)}
                    </span>
                  </div>
                );
              })}
            </div>
          ) : (
            <EmptyBenchmark />
          )}
        </div>

        <div className="card border-brand-500/20">
          <div className="flex items-center gap-2.5 mb-5">
            <div className="w-9 h-9 rounded-lg bg-brand-500/10 flex items-center justify-center">
              <BarChart3 size={18} className="text-brand-400" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-text-primary">
                Orqestra Organization
              </h3>
              <p className="text-[10px] text-text-muted uppercase tracking-wider">
                Multi-Agent Governance
              </p>
            </div>
          </div>
          {org ? (
            <div className="space-y-3">
              {METRICS.map((m) => {
                const Icon = m.icon;
                const val = org[m.key];
                const sVal = single?.[m.key] ?? 0;
                const diff = val - sVal;
                return (
                  <div
                    key={m.key}
                    className="flex items-center justify-between py-1.5"
                  >
                    <div className="flex items-center gap-2">
                      <Icon size={13} className="text-brand-400" />
                      <span className="text-xs text-text-secondary">
                        {m.label}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-mono text-text-primary">
                        {m.format(val)}
                      </span>
                      {single && (
                        <span
                          className={`text-[10px] font-medium ${
                            m.higher
                              ? diff > 0
                                ? "text-emerald-400"
                                : diff < 0
                                  ? "text-red-400"
                                  : "text-text-muted"
                              : diff < 0
                                ? "text-emerald-400"
                                : diff > 0
                                  ? "text-red-400"
                                  : "text-text-muted"
                          }`}
                        >
                          {diff > 0 ? "+" : ""}
                          {m.key === "confidence"
                            ? `${(diff * 100).toFixed(0)}%`
                            : diff.toFixed(1)}
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <EmptyBenchmark />
          )}
        </div>
      </div>
    </div>
  );
}

function EmptyBenchmark() {
  return (
    <div className="py-8 text-center">
      <BarChart3 size={20} className="text-text-muted mx-auto mb-2" />
      <p className="text-xs text-text-muted">
        Run benchmark to see comparison
      </p>
    </div>
  );
}
