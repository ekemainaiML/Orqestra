"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { DemoCase } from "@/lib/types";
import {
  Zap,
  HelpCircle,
  ShieldAlert,
  GitBranch,
  Loader2,
  Sparkles,
} from "lucide-react";

const SCENARIO_META: Record<
  string,
  {
    icon: React.ElementType;
    color: string;
    gradient: string;
    label: string;
  }
> = {
  standard_order: {
    icon: Zap,
    color: "text-emerald-400",
    gradient: "from-emerald-500/10 to-transparent",
    label: "Standard Order",
  },
  ambiguous_request: {
    icon: HelpCircle,
    color: "text-amber-400",
    gradient: "from-amber-500/10 to-transparent",
    label: "Ambiguous Request",
  },
  deadlock: {
    icon: ShieldAlert,
    color: "text-rose-400",
    gradient: "from-rose-500/10 to-transparent",
    label: "Department Deadlock",
  },
  executive_modification: {
    icon: GitBranch,
    color: "text-violet-400",
    gradient: "from-violet-500/10 to-transparent",
    label: "Executive Modification",
  },
};

const SCENARIO_DETAILS: Record<
  string,
  { difficulty: string; agents: number; type: string }
> = {
  standard_order: {
    difficulty: "Easy",
    agents: 4,
    type: "Fulfillment",
  },
  ambiguous_request: {
    difficulty: "Medium",
    agents: 5,
    type: "Clarification",
  },
  deadlock: {
    difficulty: "Hard",
    agents: 6,
    type: "Conflict Resolution",
  },
  executive_modification: {
    difficulty: "Hard",
    agents: 6,
    type: "Re-negotiation",
  },
};

export default function DemoPage() {
  const [cases, setCases] = useState<DemoCase[]>([]);
  const [launching, setLaunching] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    api.demo.list().then(setCases);
  }, []);

  const handleLaunch = async (scenario: string) => {
    setLaunching(scenario);
    try {
      const result = await api.demo.launch(scenario);
      router.push(`/cases/${result.case_id}`);
    } catch {
      setLaunching(null);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-text-primary">
          Demo Case Library
        </h1>
        <p className="text-sm text-text-muted mt-1">
          Launch pre-configured scenarios to demonstrate Orqestra&apos;s
          multi-agent governance protocol
        </p>
      </div>

      <div className="grid gap-5">
        {cases.map((dc) => {
          const meta = SCENARIO_META[dc.scenario] ?? {
            icon: Sparkles,
            color: "text-blue-400",
            gradient: "from-blue-500/10 to-transparent",
            label: dc.scenario,
          };
          const details = SCENARIO_DETAILS[dc.scenario] ?? {
            difficulty: "N/A",
            agents: 0,
            type: "Unknown",
          };
          const Icon = meta.icon;
          const isLaunching = launching === dc.scenario;

          return (
            <div
              key={dc.id}
              className="card overflow-hidden group hover:border-brand-500/20 transition-all duration-300"
            >
              <div className={`absolute inset-0 bg-gradient-to-br ${meta.gradient} opacity-50 pointer-events-none`} />
              <div className="relative">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-10 h-10 rounded-xl bg-surface-4 flex items-center justify-center ${meta.color}`}
                    >
                      <Icon size={20} />
                    </div>
                    <div>
                      <h3 className="text-base font-semibold text-text-primary">
                        {meta.label}
                      </h3>
                      <p className="text-xs text-text-muted">
                        {dc.description}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleLaunch(dc.scenario)}
                    disabled={isLaunching}
                    className="btn-primary flex items-center gap-1.5 shrink-0"
                  >
                    {isLaunching ? (
                      <>
                        <Loader2 size={14} className="animate-spin" />
                        Launching...
                      </>
                    ) : (
                      <>
                        <Zap size={14} />
                        Launch Demo
                      </>
                    )}
                  </button>
                </div>

                <div className="flex items-center gap-4 text-xs">
                  <span
                    className={`tag ${
                      details.difficulty === "Easy"
                        ? "tag-success"
                        : details.difficulty === "Medium"
                          ? "tag-warning"
                          : "tag-danger"
                    }`}
                  >
                    {details.difficulty}
                  </span>
                  <span className="text-text-muted">
                    {details.agents} agents
                  </span>
                  <span className="text-text-muted">{details.type}</span>
                  <span className="text-text-muted italic truncate hidden sm:inline">
                    &ldquo;{dc.request_text.substring(0, 80)}...&rdquo;
                  </span>
                </div>
              </div>
            </div>
          );
        })}

        {cases.length === 0 && (
          <div className="card p-12 text-center">
            <Loader2
              size={24}
              className="animate-spin text-text-muted mx-auto mb-3"
            />
            <p className="text-sm text-text-muted">
              Loading demo scenarios...
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
