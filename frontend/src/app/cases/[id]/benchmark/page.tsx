"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import type { BenchmarkResult } from "@/lib/types";

export default function BenchmarkPage() {
  const params = useParams();
  const caseId = params.id as string;
  const [benchmark, setBenchmark] = useState<BenchmarkResult | null>(null);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    api.benchmark.get(caseId).then(setBenchmark);
  }, [caseId]);

  const handleRun = async () => {
    setRunning(true);
    await api.benchmark.run(caseId);
    const result = await api.benchmark.get(caseId);
    setBenchmark(result);
    setRunning(false);
  };

  return (
    <div className="min-h-screen p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Side-by-Side Benchmark</h1>
        <button
          onClick={handleRun}
          disabled={running}
          className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {running ? "Running..." : "Run Benchmark"}
        </button>
      </div>

      {benchmark?.comparison && (
        <div className="grid grid-cols-3 gap-4 mb-6">
          <ComparisonCard
            label="Confidence"
            single={benchmark.single_agent?.confidence ?? 0}
            org={benchmark.organization?.confidence ?? 0}
            gain={benchmark.comparison.confidence_gain}
          />
          <ComparisonCard
            label="Risks Found"
            single={benchmark.single_agent?.risks_found ?? 0}
            org={benchmark.organization?.risks_found ?? 0}
            gain={benchmark.comparison.risk_detection_improvement}
          />
          <ComparisonCard
            label="Memory Used"
            single={benchmark.single_agent?.memory_used ?? 0}
            org={benchmark.organization?.memory_used ?? 0}
            gain={benchmark.comparison.memory_utilization_gain}
          />
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
          <h3 className="text-sm font-semibold text-gray-400 mb-3">
            Single Agent Baseline
          </h3>
          {benchmark?.single_agent ? (
            <div className="text-sm text-gray-300 space-y-1">
              <p>Confidence: {(benchmark.single_agent.confidence * 100).toFixed(0)}%</p>
              <p>Risks: {benchmark.single_agent.risks_found}</p>
              <p>Factors: {benchmark.single_agent.factors_considered}</p>
              <p>Reasoning: {benchmark.single_agent.reasoning_time_s}s</p>
              <p>Memory: {benchmark.single_agent.memory_used} entries</p>
            </div>
          ) : (
            <p className="text-gray-600 text-sm">Run benchmark to see results</p>
          )}
        </div>
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
          <h3 className="text-sm font-semibold text-gray-400 mb-3">
            Orqestra Organization
          </h3>
          {benchmark?.organization ? (
            <div className="text-sm text-gray-300 space-y-1">
              <p>Confidence: {(benchmark.organization.confidence * 100).toFixed(0)}%</p>
              <p>Risks: {benchmark.organization.risks_found}</p>
              <p>Factors: {benchmark.organization.factors_considered}</p>
              <p>Reasoning: {benchmark.organization.reasoning_time_s}s</p>
              <p>Memory: {benchmark.organization.memory_used} entries</p>
            </div>
          ) : (
            <p className="text-gray-600 text-sm">Run benchmark to see results</p>
          )}
        </div>
      </div>
    </div>
  );
}

function ComparisonCard({
  label,
  single,
  org,
  gain,
}: {
  label: string;
  single: number;
  org: number;
  gain: number;
}) {
  return (
    <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
      <div className="text-sm text-gray-400">{label}</div>
      <div className="flex justify-between mt-2 text-sm">
        <span className="text-gray-500">Single: {single}</span>
        <span className="text-gray-300">Orqestra: {org}</span>
      </div>
      <div
        className={`text-xs mt-1 ${
          gain > 0 ? "text-green-400" : gain < 0 ? "text-red-400" : "text-gray-500"
        }`}
      >
        {gain > 0 ? "+" : ""}
        {gain} improvement
      </div>
    </div>
  );
}
