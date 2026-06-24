"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Loader2, Send, ArrowLeft, Search } from "lucide-react";
import Link from "next/link";
import type { WorkflowSummary, CustomerSearchResult } from "@/lib/types";

const DEBOUNCE_MS = 300;

export default function NewCasePage() {
  const [customerSearch, setCustomerSearch] = useState("");
  const [customerResults, setCustomerResults] = useState<CustomerSearchResult[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<CustomerSearchResult | null>(null);
  const [searching, setSearching] = useState(false);
  const [workflowType, setWorkflowType] = useState("");
  const [requestText, setRequestText] = useState("");
  const [workflows, setWorkflows] = useState<WorkflowSummary[]>([]);
  const [loadingWorkflows, setLoadingWorkflows] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  useEffect(() => {
    api.workflows.list().then((r) => {
      setWorkflows(r.workflows);
      if (r.workflows.length > 0) setWorkflowType(r.workflows[0].id);
    }).catch(() => {}).finally(() => setLoadingWorkflows(false));
  }, []);

  const searchRef = useRef("");

  useEffect(() => {
    if (selectedCustomer) return;
    searchRef.current = customerSearch;
    if (!customerSearch.trim()) return;
    const timer = setTimeout(async () => {
      setSearching(true);
      try {
        const r = await api.cases.customers.search(customerSearch);
        if (searchRef.current === customerSearch) {
          setCustomerResults(r.customers);
        }
      } catch {
        if (searchRef.current === customerSearch) {
          setCustomerResults([]);
        }
      } finally {
        if (searchRef.current === customerSearch) {
          setSearching(false);
        }
      }
    }, DEBOUNCE_MS);
    return () => clearTimeout(timer);
  }, [customerSearch, selectedCustomer]);

  const handleSearchChange = useCallback((value: string) => {
    setCustomerSearch(value);
    if (!value.trim()) {
      setCustomerResults([]);
    }
  }, []);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCustomer) return;
    setError("");
    setLoading(true);
    try {
      const result = await api.cases.create({
        customer_id: selectedCustomer.id,
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
  }, [selectedCustomer, requestText, workflowType, router]);

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
          <label htmlFor="customer-search" className="label">
            Customer
          </label>
          {selectedCustomer ? (
            <div className="flex items-center justify-between input py-2.5">
              <div>
                <span className="text-text-primary font-medium">{selectedCustomer.name}</span>
                <span className="text-text-muted text-xs ml-2">{selectedCustomer.company}</span>
              </div>
              <button
                type="button"
                onClick={() => { setSelectedCustomer(null); setCustomerSearch(""); }}
                className="text-xs text-brand-400 hover:text-brand-300"
              >
                Change
              </button>
            </div>
          ) : (
            <div className="relative">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
              <input
                id="customer-search"
                type="text"
                value={customerSearch}
                onChange={(e) => handleSearchChange(e.target.value)}
                className="input pl-9"
                placeholder="Search by name, email, or company..."
                autoComplete="off"
              />
              {searching && (
                <Loader2 size={14} className="absolute right-3 top-1/2 -translate-y-1/2 animate-spin text-text-muted" />
              )}
              {customerResults.length > 0 && (
                <div className="absolute z-10 mt-1 w-full rounded-lg border shadow-xl overflow-hidden bg-[var(--color-surface-4)] border-[var(--color-border)]">
                  {customerResults.map((c) => (
                    <button
                      key={c.id}
                      type="button"
                      onClick={() => setSelectedCustomer(c)}
                      className="w-full text-left px-3 py-2.5 border-b last:border-0 hover:bg-[var(--color-surface-3)] transition-colors border-[var(--color-border)]"
                    >
                      <div className="text-sm text-text-primary font-medium">{c.name}</div>
                      <div className="text-xs text-text-muted">{c.email} {c.company ? `· ${c.company}` : ""}</div>
                    </button>
                  ))}
                </div>
              )}
              {!searching && customerSearch && customerResults.length === 0 && (
                <p className="text-xs text-text-muted mt-1.5">No customers found for &ldquo;{customerSearch}&rdquo;</p>
              )}
            </div>
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
            disabled={loading || !selectedCustomer || !requestText.trim()}
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
