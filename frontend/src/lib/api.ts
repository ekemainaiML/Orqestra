const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const RUN_TIMEOUT_MS = 300_000;

function getAuthHeaders(): Record<string, string> {
  if (typeof window === "undefined") return {};
  const token = localStorage.getItem("orqestra_auth_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function fetchJSON<T>(
  path: string,
  options?: RequestInit & { timeout?: number }
): Promise<T> {
  const timeout = path.endsWith("/run") ? RUN_TIMEOUT_MS : options?.timeout ?? 30_000;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json", ...getAuthHeaders(), ...options?.headers },
      signal: controller.signal,
      ...options,
    });
    if (!res.ok) {
      const body = await res.text().catch(() => "");
      throw new Error(`API ${res.status}: ${res.statusText}${body ? ` — ${body.slice(0, 200)}` : ""}`);
    }
    return res.json();
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new Error(`Request timed out after ${timeout / 1000}s`);
    }
    if (err instanceof TypeError && err.message === "Failed to fetch") {
      throw new Error(`Network error — is the backend running at ${API_BASE}?`);
    }
    throw err;
  } finally {
    clearTimeout(timer);
  }
}

export async function uploadFile(path: string, file: File): Promise<unknown> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: formData,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`API ${res.status}: ${res.statusText}${body ? ` — ${body.slice(0, 200)}` : ""}`);
  }
  return res.json();
}

export const api = {
  workflows: {
    list: () =>
      fetchJSON<{ workflows: import("./types").WorkflowSummary[] }>("/cases/workflows"),
  },
  cases: {
    list: (query?: string) => fetchJSON<import("./types").Case[]>(`/cases${query ? `?${query}` : ""}`),
    get: (id: string) => fetchJSON<import("./types").CaseDetail>(`/cases/${id}`),
    create: (data: { customer_id: string; request_text: string; workflow_type?: string }) =>
      fetchJSON<import("./types").Case>("/cases", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    run: (id: string) =>
      fetchJSON<import("./types").DeliberationResult>(`/cases/${id}/run`, {
        method: "POST",
      }),
    approve: (id: string) =>
      fetchJSON<{ status: string }>(`/cases/${id}/approve`, { method: "POST" }),
    reject: (id: string) =>
      fetchJSON<{ status: string }>(`/cases/${id}/reject`, { method: "POST" }),
    modify: (id: string, directive: Record<string, unknown>) =>
      fetchJSON<{ status: string; iteration: number }>(`/cases/${id}/modify`, {
        method: "POST",
        body: JSON.stringify(directive),
      }),
    brief: (id: string) => fetchJSON(`/cases/${id}/brief`),
    directives: {
      list: (id: string) =>
        fetchJSON<import("./types").Directive[]>(`/cases/${id}/directives`),
      delete: (caseId: string, directiveId: string) =>
        fetchJSON<{ message: string }>(`/cases/${caseId}/directives/${directiveId}`, {
          method: "DELETE",
        }),
    },
  },
  demo: {
    list: () => fetchJSON<import("./types").DemoCase[]>("/demo/cases"),
    launch: (scenario: string) =>
      fetchJSON<{ case_id: string; scenario: string; message: string }>(
        `/demo/launch/${scenario}`,
        { method: "POST" }
      ),
  },
  benchmark: {
    get: (caseId: string) =>
      fetchJSON<import("./types").BenchmarkResult>(`/benchmark/${caseId}`),
    run: (caseId: string) =>
      fetchJSON<{ message: string; confidence_gain: number }>(
        `/benchmark/${caseId}/run`,
        { method: "POST" }
      ),
  },
  admin: {
    validate: (yamlContent: string) =>
      fetchJSON<import("./types").ValidationResult>("/admin/workflows/validate", {
        method: "POST",
        body: JSON.stringify({ yaml_content: yamlContent }),
      }),
    save: (yamlContent: string) =>
      fetchJSON<import("./types").SaveWorkflowResponse>("/admin/workflows", {
        method: "POST",
        body: JSON.stringify({ yaml_content: yamlContent }),
      }),
    list: () =>
      fetchJSON<import("./types").AdminWorkflowListResponse>("/admin/workflows"),
    get: (id: string) =>
      fetchJSON<import("./types").AdminWorkflowDetail>(`/admin/workflows/${id}`),
    delete: (id: string) =>
      fetchJSON<{ message: string }>(`/admin/workflows/${id}`, {
        method: "DELETE",
      }),
    exportWorkflow: (id: string) => {
      const url = `${API_BASE}/admin/workflows/${id}/export`;
      window.open(url, "_blank");
    },
    importWorkflow: (file: File) => uploadFile("/admin/workflows/import", file),
  },
  dashboard: {
    metrics: () =>
      fetchJSON<import("./types").DashboardMetrics>("/dashboard/metrics"),
  },
};
