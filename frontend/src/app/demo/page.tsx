"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { DemoCase } from "@/lib/types";

const SCENARIO_COLORS: Record<string, string> = {
  standard_order: "border-green-500",
  ambiguous_request: "border-yellow-500",
  deadlock: "border-red-500",
  executive_modification: "border-purple-500",
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
    <div className="min-h-screen p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold">Demo Case Library</h1>
        <p className="text-gray-400 mt-1">
          Launch a pre-configured scenario to demonstrate Orqestra's
          organizational decision-making
        </p>
      </header>

      <div className="grid gap-4">
        {cases.map((dc) => (
          <div
            key={dc.id}
            className={`bg-gray-900 rounded-lg p-6 border-l-4 ${
              SCENARIO_COLORS[dc.scenario] || "border-gray-600"
            }`}
          >
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-lg font-semibold capitalize">
                  {dc.scenario.replace(/_/g, " ")}
                </h3>
                <p className="text-gray-400 mt-1 text-sm">{dc.description}</p>
                <p className="text-gray-500 mt-2 text-sm italic">
                  &ldquo;{dc.request_text.substring(0, 120)}...&rdquo;
                </p>
              </div>
              <button
                onClick={() => handleLaunch(dc.scenario)}
                disabled={launching === dc.scenario}
                className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50 transition"
              >
                {launching === dc.scenario ? "Launching..." : "Launch"}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
