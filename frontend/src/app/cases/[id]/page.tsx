"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useCaseEvents } from "@/hooks/useCaseEvents";
import type { CaseDetail, DeliberationResult } from "@/lib/types";

export default function CaseDetailPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params.id as string;
  const [caseData, setCaseData] = useState<CaseDetail | null>(null);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<DeliberationResult | null>(null);
  const liveEvents = useCaseEvents(caseId);

  useEffect(() => {
    api.cases.get(caseId).then(setCaseData);
  }, [caseId]);

  const handleRun = async () => {
    setRunning(true);
    try {
      const r = await api.cases.run(caseId);
      setResult(r);
      setCaseData((prev) =>
        prev ? { ...prev, status: r.status } : prev
      );
    } finally {
      setRunning(false);
    }
  };

  if (!caseData) {
    return <div className="p-8 text-gray-400">Loading case...</div>;
  }

  return (
    <div className="min-h-screen p-8">
      <header className="mb-6">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold">Case {caseId.slice(0, 8)}</h1>
          <StatusBadge status={caseData.status} />
        </div>
        <p className="text-gray-400 mt-2">{caseData.request_text}</p>
      </header>

      <div className="flex gap-4 mb-6">
        <button
          onClick={handleRun}
          disabled={running || caseData.status !== "created"}
          className="px-4 py-2 bg-green-600 rounded hover:bg-green-700 disabled:opacity-50 transition"
        >
          {running ? "Running..." : "Run Deliberation"}
        </button>
        {caseData.status === "approval_pending" && (
          <>
            <button
              onClick={() => api.cases.approve(caseId).then(() => router.refresh())}
              className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 transition"
            >
              Approve
            </button>
            <button
              onClick={() => api.cases.reject(caseId).then(() => router.refresh())}
              className="px-4 py-2 bg-red-600 rounded hover:bg-red-700 transition"
            >
              Reject
            </button>
            <button
              onClick={async () => {
                const directive = { minimum_margin: 20, priority: "delivery" };
                await api.cases.modify(caseId, directive);
                router.refresh();
              }}
              className="px-4 py-2 bg-purple-600 rounded hover:bg-purple-700 transition"
            >
              Modify
            </button>
          </>
        )}
      </div>

      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
          <WorkflowGraph status={caseData.status} />
        </div>
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-800 col-span-2">
          <h3 className="text-sm font-semibold text-gray-400 mb-2">
            Deliberation Timeline
          </h3>
          <div className="space-y-1 max-h-64 overflow-y-auto">
            {liveEvents.map((evt, i) => (
              <div key={i} className="text-xs text-gray-500">
                <span className="text-gray-400">[{evt.event_type as string}]</span>{" "}
                <span className="text-gray-300">{evt.actor as string}</span>
                <span className="text-gray-600 ml-1">
                  {new Date(evt.timestamp as string).toLocaleTimeString()}
                </span>
              </div>
            ))}
            {liveEvents.length === 0 && (
              <div className="text-gray-600 text-xs">
                No events yet. Run deliberation to start.
              </div>
            )}
          </div>
        </div>
      </div>

      {result && (
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-800 mb-6">
          <h3 className="text-sm font-semibold text-gray-400 mb-2">
            Decision Board
          </h3>
          <div className="text-sm text-gray-300">
            <p>
              <span className="text-gray-500">Decision:</span>{" "}
              {JSON.stringify(result.decision?.recommendation ?? "")}
            </p>
            <p>
              <span className="text-gray-500">Confidence:</span>{" "}
              {result.decision?.confidence
                ? `${(result.decision.confidence as number * 100).toFixed(0)}%`
                : "N/A"}
            </p>
          </div>
        </div>
      )}

      <div className="flex gap-4">
        <a
          href={`/cases/${caseId}/audit`}
          className="text-sm text-blue-400 hover:underline"
        >
          Audit Trail →
        </a>
        <a
          href={`/cases/${caseId}/benchmark`}
          className="text-sm text-blue-400 hover:underline"
        >
          Benchmark →
        </a>
        <a
          href={`/cases/${caseId}/replay`}
          className="text-sm text-blue-400 hover:underline"
        >
          Replay →
        </a>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    completed: "bg-green-600",
    escalated: "bg-red-600",
    approval_pending: "bg-yellow-600",
    created: "bg-gray-600",
    adjudication: "bg-blue-600",
  };
  return (
    <span
      className={`px-2 py-0.5 rounded text-xs font-medium ${
        colors[status] || "bg-gray-600"
      }`}
    >
      {status.replace(/_/g, " ")}
    </span>
  );
}

function WorkflowGraph({ status }: { status: string }) {
  const states = [
    "created",
    "memory_retrieval",
    "independent_assessment",
    "challenge_round",
    "consensus_scoring",
    "adjudication",
    "approval_pending",
    "completed",
  ];
  const idx = states.indexOf(status);

  return (
    <div>
      <h3 className="text-sm font-semibold text-gray-400 mb-3">
        Workflow Status
      </h3>
      <div className="space-y-1">
        {states.map((s, i) => (
          <div key={s} className="flex items-center gap-2 text-xs">
            <div
              className={`w-2 h-2 rounded-full ${
                i <= idx ? "bg-blue-500" : "bg-gray-700"
              }`}
            />
            <span
              className={i <= idx ? "text-gray-300" : "text-gray-600"}
            >
              {s.replace(/_/g, " ")}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
