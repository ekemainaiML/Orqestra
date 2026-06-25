"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { IntegrationHealth } from "@/lib/types";
import { Loader2, CheckCircle, AlertTriangle, RefreshCw } from "lucide-react";

const integrationLabels: Record<string, string> = {
  hubspot: "HubSpot CRM",
  odoo: "Odoo ERP",
  paystack: "Paystack Payments",
  dhl: "DHL Logistics",
  qwen: "Qwen AI (DashScope)",
  slack: "Slack Notifications",
  smtp: "Email (SMTP)",
};

export default function IntegrationsPage() {
  const [health, setHealth] = useState<IntegrationHealth | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchHealth = () => {
    api.health.integrations().then(setHealth).catch(() => {}).finally(() => setLoading(false));
  };

  useEffect(() => { fetchHealth(); }, []);

  if (loading) return <div className="flex items-center justify-center h-64"><Loader2 size={20} className="animate-spin text-text-muted" /></div>;

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Integrations</h1>
          <p className="text-sm text-text-muted mt-1">Status of connected services</p>
        </div>
        <button onClick={fetchHealth} className="btn-ghost text-xs flex items-center gap-1.5">
          <RefreshCw size={12} /> Refresh
        </button>
      </div>

      <div className="grid gap-3">
        {health && Object.entries(health).map(([key, val]) => (
          <div key={key} className="card p-4 flex items-center gap-3">
            {val.status === "connected" ? (
              <CheckCircle size={20} className="text-green-400 shrink-0" />
            ) : (
              <AlertTriangle size={20} className="text-yellow-400 shrink-0" />
            )}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-text-primary">{integrationLabels[key] || key}</p>
              <p className="text-xs text-text-muted mt-0.5">
                {val.status === "connected" ? "Connected and ready" : "Not configured — API key or credentials missing"}
              </p>
            </div>
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full shrink-0 ${
              val.status === "connected"
                ? "bg-green-500/10 text-green-400"
                : "bg-yellow-500/10 text-yellow-400"
            }`}>
              {val.status === "connected" ? "Active" : "Inactive"}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
