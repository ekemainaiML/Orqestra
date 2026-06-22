"use client";
import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Loader2, Send, ArrowLeft } from "lucide-react";
import Link from "next/link";
import type { WorkflowSummary } from "@/lib/types";

const CUSTOMER_OPTIONS = [
  { id: "a1b2c3d4-0001-4000-8000-000000000001", name: "Sarah Mitchell — Greenfield Municipal Council" },
  { id: "a1b2c3d4-0001-4000-8000-000000000002", name: "James Okafor — NovaTech Solutions" },
  { id: "a1b2c3d4-0001-4000-8000-000000000003", name: "Chioma Adeyemi — RenPower Africa" },
  { id: "a1b2c3d4-0001-4000-8000-000000000004", name: "David Chen — Sunlight Initiative" },
];

export default function NewCasePage() {
  const [customerId, setCustomerId] = useState("");
  const [workflowType, setWorkflowType] = useState("");
  const [requestText, setRequestText] = useState("");
  const [workflows, setWorkflows] = useState<WorkflowSummary[]>([]);
  const [loadingWorkflows, setLoadingWorkflows] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  useEffect(() => {
    setLoadingWorkflows(true);
    api.workflows.list().then((r) => {
      setWorkflows(r.workflows);
      if (r.workflows.length > 0) setWorkflowType(r.workflows[0].id);
    }).catch(() => {}).finally(() => setLoadingWorkflows(false));
  }, []);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const result = await api.cases.create({
        customer_id: customerId,
        request_text: requestText,
        workflow_type: workflowType,
      });
      router.push(`/cases/${result.id}`);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to create case"
      );
      setLoading(false);
    }
  }, [customerId, requestText, workflowType, router]);

  const selectedCustomer = CUSTOMER_OPTIONS.find(
    (c) => c.id === customerId
  );
  const selectedWorkflow = workflows.find(
    (w) => w.id === workflowType
  );

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div>
        <Link
          href="/"
          className="btn-ghost inline-flex items-center gap-1.5 mb-3"
        >
          <ArrowLeft size={14} />
          Back to Dashboard
        </Link>
        <h1 className="text-2xl font-bold text-text-primary">
          New Business Request
        </h1>
        <p className="text-sm text-text-muted mt-1">
          Submit a customer order for multi-agent deliberation
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label htmlFor="customer" className="label">
            Customer
          </label>
          <div className="relative">
            <select
              id="customer"
              value={customerId}
              onChange={(e) => setCustomerId(e.target.value)}
              className="input appearance-none cursor-pointer"
              required
            >
              <option value="" disabled>
                Select a customer...
              </option>
              {CUSTOMER_OPTIONS.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3 text-text-muted">
              <svg
                width="16"
                height="16"
                viewBox="0 0 16 16"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M4 6l4 4 4-4" />
              </svg>
            </div>
          </div>
          {selectedCustomer && (
            <p className="text-xs text-text-muted mt-1.5">
              ID: {selectedCustomer.id}
            </p>
          )}
        </div>

        <div>
          <label htmlFor="workflow" className="label flex items-center gap-1.5">
            Workflow
            {loadingWorkflows && <Loader2 size={12} className="animate-spin text-text-muted" />}
          </label>
          <div className="relative">
            <select
              id="workflow"
              value={workflowType}
              onChange={(e) => setWorkflowType(e.target.value)}
              className="input appearance-none cursor-pointer"
            >
              {loadingWorkflows ? (
                <option value="" disabled>
                  Loading workflows...
                </option>
              ) : (
                workflows.map((w) => (
                  <option key={w.id} value={w.id}>
                    {w.name}
                  </option>
                ))
              )}
            </select>
            <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3 text-text-muted">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M4 6l4 4 4-4" />
              </svg>
            </div>
          </div>
          {selectedWorkflow && (
            <p className="text-xs text-text-muted mt-1.5">
              {selectedWorkflow.departments.length} departments · {selectedWorkflow.id}
            </p>
          )}
        </div>

        <div>
          <label htmlFor="request" className="label">
            Request Details
          </label>
          <textarea
            id="request"
            value={requestText}
            onChange={(e) => setRequestText(e.target.value)}
            className="input h-36 resize-none"
            placeholder="Describe the customer's order in detail. Include product, quantity, delivery timeline, and any special requirements..."
            required
          />
          <p className="text-xs text-text-muted mt-1.5 text-right">
            {requestText.length} characters
          </p>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-sm text-red-400">
            {error}
          </div>
        )}

        <div className="flex items-center gap-3 pt-2">
          <button
            type="submit"
            disabled={loading || !customerId || !requestText.trim()}
            className="btn-primary flex items-center gap-2"
          >
            {loading ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <Send size={16} />
            )}
            {loading ? "Creating..." : "Submit for Deliberation"}
          </button>
          <Link href="/" className="btn-secondary">
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}
