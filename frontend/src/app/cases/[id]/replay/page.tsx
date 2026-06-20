"use client";
import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import type { CaseDetail, WorkflowEvent } from "@/lib/types";
import { StatusBadge } from "@/components/StatusBadge";
import {
  ArrowLeft,
  SkipBack,
  ChevronLeft,
  ChevronRight,
  SkipForward,
  Play,
  Pause,
  Loader2,
} from "lucide-react";

const WORKFLOW_STEPS = [
  { key: "created", label: "Created", desc: "Case initiated and logged" },
  {
    key: "memory_retrieval",
    label: "Memory Retrieval",
    desc: "Relevant past experiences loaded",
  },
  {
    key: "independent_assessment",
    label: "Assessment",
    desc: "Agents evaluate independently",
  },
  {
    key: "challenge_round",
    label: "Challenge Round",
    desc: "Agents challenge each other's positions",
  },
  {
    key: "consensus_scoring",
    label: "Consensus Scoring",
    desc: "Scores computed across 5 dimensions",
  },
  {
    key: "adjudication",
    label: "Adjudication",
    desc: "Escalated for tiebreak resolution",
  },
  {
    key: "approval_pending",
    label: "Approval",
    desc: "Awaiting executive decision",
  },
  {
    key: "completed",
    label: "Completed",
    desc: "Resolution achieved",
  },
];

export default function ReplayPage() {
  const params = useParams();
  const caseId = params.id as string;
  const [caseData, setCaseData] = useState<CaseDetail | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [playing, setPlaying] = useState(false);

  useEffect(() => {
    api.cases.get(caseId).then(setCaseData);
  }, [caseId]);

  useEffect(() => {
    if (!playing) return;
    const interval = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev >= WORKFLOW_STEPS.length - 1) {
          setPlaying(false);
          return prev;
        }
        return prev + 1;
      });
    }, 1200);
    return () => clearInterval(interval);
  }, [playing]);

  const goTo = useCallback(
    (step: number) => setCurrentStep(Math.max(0, Math.min(WORKFLOW_STEPS.length - 1, step))),
    []
  );

  if (!caseData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center gap-3 text-text-muted">
          <Loader2 size={20} className="animate-spin" />
          <span className="text-sm">Loading replay data...</span>
        </div>
      </div>
    );
  }

  const eventsAtStep = caseData.events.filter((_, i) => i <= currentStep);
  const step = WORKFLOW_STEPS[currentStep];
  const isLastStep = currentStep >= WORKFLOW_STEPS.length - 1;

  return (
    <div className="space-y-6">
      <div>
        <Link
          href={`/cases/${caseId}`}
          className="btn-ghost inline-flex items-center gap-1.5 mb-3"
        >
          <ArrowLeft size={14} />
          Back to Case
        </Link>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-text-primary">
              Governance Replay
            </h1>
            <p className="text-sm text-text-muted mt-1">
              Case <span className="font-mono">{caseId.slice(0, 8)}</span>
              &nbsp;&middot;&nbsp;Step-by-step playback of the deliberation
            </p>
          </div>
          <StatusBadge status={caseData.status} />
        </div>
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-1">
            <button
              onClick={() => goTo(0)}
              disabled={currentStep === 0}
              className="btn-ghost p-2"
              title="Skip to start"
            >
              <SkipBack size={16} />
            </button>
            <button
              onClick={() => goTo(currentStep - 1)}
              disabled={currentStep === 0}
              className="btn-ghost p-2"
              title="Previous step"
            >
              <ChevronLeft size={16} />
            </button>
            <button
              onClick={() => setPlaying(!playing)}
              className="btn-primary flex items-center gap-1.5 mx-1"
            >
              {playing ? (
                <Pause size={14} />
              ) : (
                <Play size={14} />
              )}
              {playing ? "Pause" : "Play"}
            </button>
            <button
              onClick={() => goTo(currentStep + 1)}
              disabled={isLastStep}
              className="btn-ghost p-2"
              title="Next step"
            >
              <ChevronRight size={16} />
            </button>
            <button
              onClick={() => goTo(WORKFLOW_STEPS.length - 1)}
              disabled={isLastStep}
              className="btn-ghost p-2"
              title="Skip to end"
            >
              <SkipForward size={16} />
            </button>
          </div>
          <span className="text-xs text-text-muted">
            Step {currentStep + 1} of {WORKFLOW_STEPS.length}
          </span>
        </div>

        <div className="relative">
          <div className="absolute top-5 left-6 right-6 h-0.5 bg-border -z-0" />
          <div
            className="absolute top-5 left-6 h-0.5 bg-brand-500 -z-0 transition-all duration-500"
            style={{
              width: `${(currentStep / (WORKFLOW_STEPS.length - 1)) * (100 - 12)}%`,
            }}
          />
          <div className="flex justify-between relative z-10">
            {WORKFLOW_STEPS.map((s, i) => {
              const isActive = i === currentStep;
              const isDone = i < currentStep;
              return (
                <button
                  key={s.key}
                  onClick={() => goTo(i)}
                  className={`flex flex-col items-center gap-1.5 transition-all duration-300 ${
                    isActive
                      ? "scale-110"
                      : isDone
                        ? "opacity-70 hover:opacity-100"
                        : "opacity-40 hover:opacity-70"
                  }`}
                >
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center text-xs font-bold border-2 transition-all duration-300 ${
                      isActive
                        ? "bg-brand-500 border-brand-500 text-gray-950 shadow-lg shadow-brand-500/30"
                        : isDone
                          ? "bg-brand-500/20 border-brand-500/50 text-brand-400"
                          : "bg-surface-4 border-border text-text-muted"
                    }`}
                  >
                    {isDone ? (
                      <svg
                        width="14"
                        height="14"
                        viewBox="0 0 14 14"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                      >
                        <path d="M3 7l3 3 5-5" />
                      </svg>
                    ) : (
                      i + 1
                    )}
                  </div>
                  <span
                    className={`text-[10px] font-medium whitespace-nowrap ${
                      isActive ? "text-brand-400" : "text-text-muted"
                    }`}
                  >
                    {s.label}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-5">
        <div className="md:col-span-2 card">
          <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-2">
            Current Step
          </h3>
          <h2 className="text-lg font-bold text-text-primary mb-1">
            {step.label}
          </h2>
          <p className="text-sm text-text-secondary mb-4">{step.desc}</p>
          <div className="space-y-2">
            {eventsAtStep.length > 0 ? (
              eventsAtStep.map((evt) => (
                <div
                  key={evt.id}
                  className="flex items-center gap-2 text-xs p-2 rounded-lg bg-surface-4/50"
                >
                  <span className="tag-default !border-0 !px-1 text-[10px]">
                    {evt.event_type}
                  </span>
                  <span className="text-text-secondary">{evt.actor}</span>
                </div>
              ))
            ) : (
              <p className="text-xs text-text-muted">No events yet.</p>
            )}
          </div>
        </div>

        <div className="md:col-span-3 card">
          <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-3">
            Event Details
          </h3>
          <div className="space-y-1 max-h-80 overflow-y-auto scrollbar-thin">
            {eventsAtStep.length > 0 ? (
              eventsAtStep.map((evt) => (
                <div
                  key={evt.id}
                  className="border-l-2 border-border pl-3 py-2 hover:border-brand-500/30 transition-colors"
                >
                  <div className="flex items-center gap-2 text-xs">
                    <span className="font-mono text-brand-400">
                      {evt.event_type}
                    </span>
                    <span className="text-text-muted">by</span>
                    <span className="font-medium text-text-primary">
                      {evt.actor}
                    </span>
                    <span className="text-text-muted ml-auto">
                      {evt.timestamp
                        ? new Date(evt.timestamp as string).toLocaleTimeString()
                        : ""}
                    </span>
                  </div>
                  {evt.payload && (
                    <pre className="text-xs text-text-muted mt-1 overflow-x-auto max-h-24 overflow-y-auto">
                      {JSON.stringify(evt.payload, null, 2).substring(
                        0,
                        300
                      )}
                    </pre>
                  )}
                </div>
              ))
            ) : (
              <div className="flex items-center justify-center h-20 text-xs text-text-muted">
                No events at this step
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
