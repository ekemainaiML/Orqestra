"use client";
import { useCallback, useState } from "react";
import { api } from "@/lib/api";
import {
  Loader2,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Info,
  FileText,
  Clipboard,
  Save,
  ExternalLink,
} from "lucide-react";
import type { ValidationResult } from "@/lib/types";
import Link from "next/link";

const SAMPLE_YAML = `id: custom_workflow
name: Custom Validation
departments:
  - id: sales
    role: Sales
    model_tier: operational
    objectives:
      - Interpret customer intent
      - Generate accurate quotations
    policies:
      - Standard pricing applies
    tools:
      - pricing_engine
  - id: operations_manager
    role: Operations Manager
    model_tier: executive
    objectives:
      - Synthesize recommendations
      - Make final decision
    policies:
      - Consider all inputs before deciding
    tools:
      - policy_engine
decision_dimensions:
  - customer_satisfaction
  - profitability
governance:
  consensus_threshold: 0.75
  deadlock_resolution: executive_override
approval:
  required_role: operations_manager
policies:
  - id: minimum_margin
    rule: gross_margin >= 0.15
    hard_constraint: true
`;

export default function ValidateWorkflowPage() {
  const [yaml, setYaml] = useState("");
  const [result, setResult] = useState<ValidationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState<string | null>(null);
  const [error, setError] = useState("");

  const handleValidate = useCallback(async () => {
    if (!yaml.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    setSaved(null);
    try {
      const res = await api.admin.validate(yaml);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Validation request failed");
    } finally {
      setLoading(false);
    }
  }, [yaml]);

  const handleSave = useCallback(async () => {
    if (!yaml.trim() || !result?.valid) return;
    setSaving(true);
    setSaved(null);
    try {
      const res = await api.admin.save(yaml);
      setSaved(res.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save workflow");
    } finally {
      setSaving(false);
    }
  }, [yaml, result]);

  const handlePasteSample = useCallback(() => {
    setYaml(SAMPLE_YAML);
    setResult(null);
    setError("");
  }, []);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
        handleValidate();
      }
    },
    [handleValidate]
  );

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">
          Validate Workflow Config
        </h1>
        <p className="text-sm text-text-muted mt-1">
          Paste a workflow YAML configuration to validate it against the schema and agent registry.
          Results are local — no config is saved. Press{" "}
          <kbd className="px-1.5 py-0.5 rounded bg-surface-4 text-xs font-mono">Cmd+Enter</kbd> to validate.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="label mb-0" htmlFor="yaml-editor">
              Workflow YAML
            </label>
            <button
              type="button"
              onClick={handlePasteSample}
              className="btn-ghost text-xs flex items-center gap-1"
            >
              <Clipboard size={12} />
              Paste Sample
            </button>
          </div>
          <textarea
            id="yaml-editor"
            value={yaml}
            onChange={(e) => setYaml(e.target.value)}
            onKeyDown={handleKeyDown}
            className="input font-mono text-xs leading-relaxed resize-none h-[520px] scrollbar-thin"
            placeholder="# Paste your workflow YAML here..."
            spellCheck={false}
          />
          <div className="flex items-center gap-2 flex-wrap">
            <button
              type="button"
              onClick={handleValidate}
              disabled={loading || !yaml.trim()}
              className="btn-primary flex items-center gap-2 text-sm"
            >
              {loading ? (
                <Loader2 size={15} className="animate-spin" />
              ) : (
                <FileText size={15} />
              )}
              {loading ? "Validating..." : "Validate"}
            </button>
            {result?.valid && !saved && (
              <button
                type="button"
                onClick={handleSave}
                disabled={saving}
                className="btn-success flex items-center gap-2 text-sm"
              >
                {saving ? (
                  <Loader2 size={15} className="animate-spin" />
                ) : (
                  <Save size={15} />
                )}
                {saving ? "Saving..." : "Save Workflow"}
              </button>
            )}
            {saved && (
              <Link
                href="/admin/workflows"
                className="btn-secondary flex items-center gap-2 text-sm"
              >
                <ExternalLink size={15} />
                View in Workflows
              </Link>
            )}
            {yaml.trim() && (
              <span className="text-xs text-text-muted">
                {yaml.split("\n").length} lines
              </span>
            )}
          </div>
        </div>

        <div className="space-y-3">
          <span className="label">Results</span>
          <div className="min-h-[520px]">
            {error && (
              <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-sm text-red-400 mb-3">
                {error}
              </div>
            )}

            {loading && (
              <div className="card flex items-center gap-3 text-text-muted">
                <Loader2 size={18} className="animate-spin" />
                <span className="text-sm">Validating configuration...</span>
              </div>
            )}

            {result && !loading && (
              <div className="space-y-4">
                <div
                  className={`card flex items-start gap-3 ${
                    result.valid
                      ? "border-emerald-500/30"
                      : "border-red-500/30"
                  }`}
                >
                  {result.valid ? (
                    <CheckCircle2
                      size={20}
                      className="text-emerald-400 mt-0.5 shrink-0"
                    />
                  ) : (
                    <XCircle
                      size={20}
                      className="text-red-400 mt-0.5 shrink-0"
                    />
                  )}
                  <div>
                    <p
                      className={`text-sm font-semibold ${
                        result.valid ? "text-emerald-400" : "text-red-400"
                      }`}
                    >
                      {result.valid
                        ? "Configuration is valid"
                        : "Configuration has errors"}
                    </p>
                    <p className="text-xs text-text-muted mt-0.5">
                      {result.workflow_id && result.workflow_name
                        ? `${result.workflow_name} (${result.workflow_id})`
                        : "Could not determine workflow ID"}
                    </p>
                  </div>
                </div>

                {result.errors.length > 0 && (
                  <div>
                    <h3 className="text-xs font-semibold text-red-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <XCircle size={12} />
                      Errors ({result.errors.length})
                    </h3>
                    <ul className="space-y-1.5">
                      {result.errors.map((e, i) => (
                        <li
                          key={i}
                          className="text-sm p-2.5 rounded-lg bg-red-500/10 border border-red-500/20 text-red-300"
                        >
                          {e}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {result.warnings.length > 0 && (
                  <div>
                    <h3 className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <AlertTriangle size={12} />
                      Warnings ({result.warnings.length})
                    </h3>
                    <ul className="space-y-1.5">
                      {result.warnings.map((w, i) => (
                        <li
                          key={i}
                          className="text-sm p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-300"
                        >
                          {w}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {result.summary && (
                  <div>
                    <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2 flex items-center gap-1.5">
                      <Info size={12} />
                      Summary
                    </h3>
                    <div className="card space-y-2 text-sm">
                      {[
                        ["Workflow ID", result.summary.workflow_id],
                        ["Name", result.summary.workflow_name],
                        ["Departments", `${result.summary.departments} (${result.summary.operational_departments} operational, ${result.summary.agents_resolved} agents resolved)`],
                        ["Decision Dimensions", result.summary.decision_dimensions.toString()],
                        ["Policies", `${result.summary.policies} (${result.summary.hard_constraints} hard constraints)`],
                        ["Consensus Threshold", result.summary.consensus_threshold.toString()],
                        ["Deadlock Resolution", result.summary.deadlock_resolution],
                        ["Executive Role", result.summary.required_role],
                      ].map(([label, value]) => (
                        <div
                          key={label}
                          className="flex items-center justify-between"
                        >
                          <span className="text-text-secondary">{label}</span>
                          <span className="text-text-primary font-mono text-xs text-right max-w-[60%] truncate ml-4">
                            {value}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {saved && (
                  <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-sm text-emerald-300 flex items-start gap-2">
                    <CheckCircle2 size={16} className="mt-0.5 shrink-0" />
                    <span>
                      Workflow saved as <strong>{saved}</strong>. It is now available when creating new cases.
                    </span>
                  </div>
                )}

                {result.valid &&
                  result.errors.length === 0 &&
                  result.warnings.length === 0 &&
                  result.summary && !saved && (
                    <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-sm text-emerald-300 flex items-start gap-2">
                      <Info size={16} className="mt-0.5 shrink-0" />
                      <span>
                        No warnings or errors. This workflow is ready to save.
                      </span>
                    </div>
                  )}
              </div>
            )}

            {!result && !loading && !error && (
              <div className="card flex flex-col items-center justify-center h-full min-h-[200px] text-center">
                <FileText
                  size={32}
                  className="text-text-muted mb-3"
                />
                <p className="text-sm text-text-muted">
                  Paste a YAML config and click{" "}
                  <span className="text-text-secondary font-medium">
                    Validate
                  </span>
                </p>
                <p className="text-xs text-text-muted mt-1">
                  Or use the{" "}
                  <button
                    type="button"
                    onClick={handlePasteSample}
                    className="link text-xs"
                  >
                    Paste Sample
                  </button>{" "}
                  button to try a valid config.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
