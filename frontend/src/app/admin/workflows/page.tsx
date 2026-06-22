"use client";
import { useCallback, useEffect, useState, useRef } from "react";
import { api } from "@/lib/api";
import {
  Loader2,
  FileText,
  Trash2,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ChevronDown,
  ChevronRight,
  ExternalLink,
  ShieldCheck,
  Download,
  Upload,
} from "lucide-react";
import Link from "next/link";

interface WorkflowItem {
  id: string;
  name: string;
  is_builtin: boolean;
  departments: Array<{ id: string; role: string; model_tier: string }>;
  policies: Array<{ id: string; rule: string; hard_constraint: boolean }>;
  consensus_threshold: number;
  required_role: string;
}

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<WorkflowItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [expanded, setExpanded] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);
  const [importing, setImporting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchWorkflows = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const res = await api.admin.list();
      setWorkflows(res.workflows);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load workflows");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWorkflows();
  }, [fetchWorkflows]);

  const handleDelete = useCallback(async (id: string) => {
    if (!confirm(`Delete workflow "${id}"? This cannot be undone.`)) return;
    setDeleting(id);
    try {
      await api.admin.delete(id);
      setWorkflows((prev) => prev.filter((w) => w.id !== id));
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to delete");
    } finally {
      setDeleting(null);
    }
  }, []);

  const handleExport = (id: string) => {
    api.admin.exportWorkflow(id);
  };

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setImporting(true);
    try {
      await api.admin.importWorkflow(file);
      await fetchWorkflows();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Import failed");
    } finally {
      setImporting(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const toggleExpand = (id: string) => {
    setExpanded((prev) => (prev === id ? null : id));
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
        <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Workflows</h1>
          <p className="text-sm text-text-muted mt-1">
            All registered workflow configurations — built-in and custom.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept=".yaml,.yml"
            onChange={handleImport}
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={importing}
            className="btn-secondary flex items-center gap-2 text-sm"
          >
            {importing ? (
              <Loader2 size={15} className="animate-spin" />
            ) : (
              <Upload size={15} />
            )}
            Import
          </button>
          <Link href="/admin/workflows/validate" className="btn-primary flex items-center gap-2 text-sm">
            <ShieldCheck size={15} />
            New Workflow
          </Link>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-sm text-red-400">
          {error}
        </div>
      )}

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card animate-pulse h-20" />
          ))}
        </div>
      ) : workflows.length === 0 ? (
        <div className="card flex flex-col items-center py-12 text-center">
          <FileText size={32} className="text-text-muted mb-3" />
          <p className="text-sm text-text-muted">No workflows found.</p>
          <Link href="/admin/workflows/validate" className="btn-primary mt-4 text-sm">
            Create a Workflow
          </Link>
        </div>
      ) : (
        <div className="space-y-2">
          {workflows.map((wf) => {
            const isExpanded = expanded === wf.id;
            const hardCount = wf.policies.filter((p) => p.hard_constraint).length;
            return (
              <div key={wf.id} className="card p-0 overflow-hidden">
                <div
                  onClick={() => toggleExpand(wf.id)}
                  className="w-full flex items-center gap-3 px-4 py-3.5 text-left hover:bg-surface-4/30 transition-colors cursor-pointer"
                >
                  {isExpanded ? (
                    <ChevronDown size={16} className="text-text-muted shrink-0" />
                  ) : (
                    <ChevronRight size={16} className="text-text-muted shrink-0" />
                  )}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-text-primary">
                        {wf.name}
                      </span>
                      <span className={`tag text-[10px] ${wf.is_builtin ? "tag-info" : "tag-success"}`}>
                        {wf.is_builtin ? "built-in" : "custom"}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 mt-0.5">
                      <span className="text-xs text-text-muted font-mono">{wf.id}</span>
                      <span className="text-xs text-text-muted">{wf.departments.length} departments</span>
                      <span className="text-xs text-text-muted">{wf.policies.length} policies ({hardCount} hard)</span>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleExport(wf.id);
                    }}
                    className="btn-ghost p-1.5 text-text-muted hover:text-text-primary hover:bg-surface-4 shrink-0"
                    title="Export YAML"
                  >
                    <Download size={14} />
                  </button>
                  {!wf.is_builtin && (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(wf.id);
                      }}
                      disabled={deleting === wf.id}
                      className="btn-ghost p-1.5 text-red-400 hover:text-red-300 hover:bg-red-500/10 shrink-0"
                    >
                      {deleting === wf.id ? (
                        <Loader2 size={14} className="animate-spin" />
                      ) : (
                        <Trash2 size={14} />
                      )}
                    </button>
                  )}
                </div>

                {isExpanded && (
                  <div className="border-t border-border px-4 py-3 space-y-4">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {[
                        ["Departments", wf.departments.length.toString()],
                        ["Policies", wf.policies.length.toString()],
                        ["Hard Constraints", hardCount.toString()],
                        ["Threshold", `${(wf.consensus_threshold * 100).toFixed(0)}%`],
                        ["Executive", wf.required_role],
                      ].map(([label, value]) => (
                        <div key={label}>
                          <span className="text-xs text-text-muted block">{label}</span>
                          <span className="text-sm text-text-primary font-medium">{value}</span>
                        </div>
                      ))}
                    </div>

                    <div>
                      <h4 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">
                        Departments
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {wf.departments.map((d) => (
                          <span key={d.id} className="tag tag-default text-xs">
                            {d.role}
                            <span className="text-text-muted ml-1">({d.model_tier})</span>
                          </span>
                        ))}
                      </div>
                    </div>

                    {wf.policies.length > 0 && (
                      <div>
                        <h4 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">
                          Policies
                        </h4>
                        <ul className="space-y-1">
                          {wf.policies.map((p) => (
                            <li key={p.id} className="flex items-center gap-2 text-sm text-text-secondary">
                              {p.hard_constraint ? (
                                <XCircle size={12} className="text-red-400 shrink-0" />
                              ) : (
                                <AlertTriangle size={12} className="text-amber-400 shrink-0" />
                              )}
                              <span className="font-mono text-xs">{p.id}:</span>
                              <span>{p.rule}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
