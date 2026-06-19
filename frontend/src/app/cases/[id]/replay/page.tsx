"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import type { CaseDetail } from "@/lib/types";

export default function ReplayPage() {
  const params = useParams();
  const caseId = params.id as string;
  const [caseData, setCaseData] = useState<CaseDetail | null>(null);
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    api.cases.get(caseId).then(setCaseData);
  }, [caseId]);

  if (!caseData) {
    return <div className="p-8 text-gray-400">Loading...</div>;
  }

  const steps = [
    { label: "Case Created", state: "created" },
    { label: "Memory Retrieval", state: "memory_retrieval" },
    { label: "Independent Assessment", state: "independent_assessment" },
    { label: "Challenge Round", state: "challenge_round" },
    { label: "Consensus Scoring", state: "consensus_scoring" },
    { label: "Adjudication", state: "adjudication" },
    { label: "Approval Pending", state: "approval_pending" },
    { label: "Completed", state: "completed" },
  ];

  const currentEvents = caseData.events.filter(
    (_, i) => i <= currentStep
  );

  return (
    <div className="min-h-screen p-8">
      <h1 className="text-2xl font-bold mb-2">Governance Replay</h1>
      <p className="text-gray-400 text-sm mb-6">
        Case {caseId.slice(0, 8)} &mdash; Iteration playback
      </p>

      <div className="flex gap-4 mb-6">
        <button
          onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
          disabled={currentStep === 0}
          className="px-3 py-1 bg-gray-700 rounded hover:bg-gray-600 disabled:opacity-50"
        >
          ← Previous
        </button>
        <span className="text-gray-400 text-sm self-center">
          Step {currentStep + 1} of {steps.length}
        </span>
        <button
          onClick={() =>
            setCurrentStep(Math.min(steps.length - 1, currentStep + 1))
          }
          disabled={currentStep >= steps.length - 1}
          className="px-3 py-1 bg-gray-700 rounded hover:bg-gray-600 disabled:opacity-50"
        >
          Next →
        </button>
        <button
          onClick={() => setCurrentStep(steps.length - 1)}
          className="px-3 py-1 bg-blue-700 rounded hover:bg-blue-600 text-sm"
        >
          Skip to End
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
          <h3 className="text-sm font-semibold text-gray-400 mb-3">
            Workflow Steps
          </h3>
          <div className="space-y-2">
            {steps.map((step, i) => (
              <div
                key={step.state}
                className={`flex items-center gap-2 p-2 rounded text-sm ${
                  i === currentStep
                    ? "bg-blue-900/30 border border-blue-800"
                    : i < currentStep
                    ? "text-gray-300"
                    : "text-gray-600"
                }`}
              >
                <div
                  className={`w-2 h-2 rounded-full ${
                    i <= currentStep ? "bg-blue-500" : "bg-gray-700"
                  }`}
                />
                {step.label}
              </div>
            ))}
          </div>
        </div>
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
          <h3 className="text-sm font-semibold text-gray-400 mb-3">
            Events at This Step
          </h3>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {currentEvents.length > 0 ? (
              currentEvents.map((evt) => (
                <div
                  key={evt.id}
                  className="text-xs border-l-2 border-gray-700 pl-3 py-1"
                >
                  <span className="text-blue-400">{evt.event_type}</span>
                  <span className="text-gray-600 ml-2">by {evt.actor}</span>
                  <div className="text-gray-600 mt-0.5">
                    {evt.timestamp
                      ? new Date(evt.timestamp).toLocaleTimeString()
                      : ""}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-gray-600 text-xs">
                No events at this step.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
