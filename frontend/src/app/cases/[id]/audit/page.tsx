"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import type { CaseDetail } from "@/lib/types";

export default function AuditPage() {
  const params = useParams();
  const caseId = params.id as string;
  const [caseData, setCaseData] = useState<CaseDetail | null>(null);

  useEffect(() => {
    api.cases.get(caseId).then(setCaseData);
  }, [caseId]);

  if (!caseData) {
    return <div className="p-8 text-gray-400">Loading...</div>;
  }

  return (
    <div className="min-h-screen p-8">
      <h1 className="text-2xl font-bold mb-6">Audit Trail</h1>
      <p className="text-gray-400 text-sm mb-4">
        Case {caseId.slice(0, 8)} &mdash; {caseData.events.length} events
      </p>

      <div className="space-y-2">
        {caseData.events.map((evt) => (
          <div
            key={evt.id}
            className="bg-gray-900 rounded-lg p-4 border border-gray-800"
          >
            <div className="flex justify-between items-start">
              <div>
                <span className="text-xs font-mono bg-gray-800 px-2 py-0.5 rounded text-blue-400">
                  {evt.event_type}
                </span>
                <span className="text-gray-500 text-xs ml-2">
                  by {evt.actor}
                </span>
              </div>
              <span className="text-xs text-gray-600">
                {evt.timestamp
                  ? new Date(evt.timestamp).toLocaleString()
                  : ""}
              </span>
            </div>
            {evt.payload && (
              <pre className="mt-2 text-xs text-gray-500 overflow-x-auto">
                {JSON.stringify(evt.payload, null, 2).slice(0, 500)}
              </pre>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
