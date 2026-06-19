"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { DashboardMetrics } from "@/lib/types";

export function useDashboardMetrics() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.dashboard
      .metrics()
      .then(setMetrics)
      .finally(() => setLoading(false));
  }, []);

  return { metrics, loading };
}
