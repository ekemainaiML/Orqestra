"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function NewCasePage() {
  const [customerId, setCustomerId] = useState("");
  const [requestText, setRequestText] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const result = await api.cases.create({
        customer_id: customerId,
        request_text: requestText,
      });
      router.push(`/cases/${result.id}`);
    } catch {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-8">
      <h1 className="text-2xl font-bold mb-6">New Business Request</h1>
      <form onSubmit={handleSubmit} className="max-w-lg space-y-4">
        <div>
          <label className="block text-sm text-gray-400 mb-1">
            Customer ID
          </label>
          <input
            value={customerId}
            onChange={(e) => setCustomerId(e.target.value)}
            className="w-full px-3 py-2 bg-gray-800 rounded border border-gray-700"
            placeholder="a1b2c3d4-0001-4000-8000-000000000001"
            required
          />
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">
            Request Text
          </label>
          <textarea
            value={requestText}
            onChange={(e) => setRequestText(e.target.value)}
            className="w-full px-3 py-2 bg-gray-800 rounded border border-gray-700 h-32"
            placeholder="Describe the customer's request..."
            required
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Creating..." : "Create Case"}
        </button>
      </form>
    </div>
  );
}
