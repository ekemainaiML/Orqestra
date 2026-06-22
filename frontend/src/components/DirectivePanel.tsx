"use client";
import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Directive } from "@/lib/types";
import { BookX, Loader2, Trash2, Plus } from "lucide-react";

const DIRECTIVE_TYPES = [
  { value: "modify_parameter", label: "Modify Parameter" },
  { value: "override_threshold", label: "Override Threshold" },
  { value: "add_constraint", label: "Add Constraint" },
  { value: "override_decision", label: "Override Decision" },
];

export function DirectivePanel({ caseId, iteration }: { caseId: string; iteration: number }) {
  const [directives, setDirectives] = useState<Directive[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [directiveType, setDirectiveType] = useState(DIRECTIVE_TYPES[0].value);
  const [directiveKey, setDirectiveKey] = useState("");
  const [directiveValue, setDirectiveValue] = useState("");
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const list = await api.cases.directives.list(caseId);
      setDirectives(list);
    } catch {
      // silently fail
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    load();
  }, [load, iteration]);

  const handleAdd = useCallback(async () => {
    if (!directiveKey || !directiveValue) return;
    setSaving(true);
    try {
      await api.cases.modify(caseId, {
        [directiveKey]: directiveValue,
      });
      setShowForm(false);
      setDirectiveKey("");
      setDirectiveValue("");
      await load();
    } catch {
      // silently fail
    } finally {
      setSaving(false);
    }
  }, [caseId, directiveKey, directiveValue, load]);

  const handleDelete = useCallback(
    async (directiveId: string) => {
      setDeleting(directiveId);
      try {
        await api.cases.directives.delete(caseId, directiveId);
        setDirectives((prev) => prev.filter((d) => d.id !== directiveId));
      } catch {
        // silently fail
      } finally {
        setDeleting(null);
      }
    },
    [caseId]
  );

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider">
          Directives
        </h3>
        <button
          onClick={() => setShowForm(!showForm)}
          className="btn-ghost p-1 text-text-muted hover:text-text-primary"
          title="Add Directive"
        >
          <Plus size={14} />
        </button>
      </div>

      {showForm && (
        <div className="mb-4 p-3 rounded-lg bg-surface-4/50 space-y-2">
          <select
            value={directiveType}
            onChange={(e) => setDirectiveType(e.target.value)}
            className="input text-xs w-full"
          >
            {DIRECTIVE_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
          <input
            type="text"
            value={directiveKey}
            onChange={(e) => setDirectiveKey(e.target.value)}
            placeholder="Parameter key (e.g. minimum_margin)"
            className="input text-xs w-full"
          />
          <input
            type="text"
            value={directiveValue}
            onChange={(e) => setDirectiveValue(e.target.value)}
            placeholder="Value"
            className="input text-xs w-full"
          />
          <div className="flex items-center gap-2">
            <button
              onClick={handleAdd}
              disabled={saving || !directiveKey || !directiveValue}
              className="btn-primary text-xs flex items-center gap-1"
            >
              {saving && <Loader2 size={12} className="animate-spin" />}
              Save Directive
            </button>
            <button
              onClick={() => setShowForm(false)}
              className="btn-ghost text-xs"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex items-center gap-2 text-xs text-text-muted py-2">
          <Loader2 size={12} className="animate-spin" />
          Loading...
        </div>
      ) : directives.length === 0 ? (
        <div className="flex items-center gap-2 text-xs text-text-muted py-2">
          <BookX size={14} />
          <span>No directives. Add one to modify deliberation behavior.</span>
        </div>
      ) : (
        <div className="space-y-1.5 max-h-48 overflow-y-auto">
          {directives.map((d) => (
            <div
              key={d.id}
              className="flex items-start gap-2 py-1.5 px-2 rounded-lg bg-surface-4/30 text-xs"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-1.5">
                  <span className="tag tag-warning !border-0 !px-1 text-[10px]">
                    {d.directive_type}
                  </span>
                  <span className="text-text-muted">iter {d.iteration}</span>
                </div>
                <p className="text-text-primary truncate mt-0.5 font-mono">
                  {JSON.stringify(d.value).slice(0, 100)}
                </p>
              </div>
              <button
                onClick={() => handleDelete(d.id)}
                disabled={deleting === d.id}
                className="p-1 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded shrink-0"
              >
                {deleting === d.id ? (
                  <Loader2 size={12} className="animate-spin" />
                ) : (
                  <Trash2 size={12} />
                )}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
