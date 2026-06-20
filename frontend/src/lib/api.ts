const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchJSON<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`);
  return res.json();
}

export const api = {
  cases: {
    list: () => fetchJSON<import("./types").Case[]>("/cases"),
    get: (id: string) => fetchJSON<import("./types").CaseDetail>(`/cases/${id}`),
    create: (data: { customer_id: string; request_text: string }) =>
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
  dashboard: {
    metrics: () =>
      fetchJSON<import("./types").DashboardMetrics>("/dashboard/metrics"),
  },
};
