interface AgentCardProps {
  name: string;
  role: string;
  status: "pending" | "assessing" | "completed" | "unavailable";
  confidence?: number;
  recommendation?: string;
}

export function AgentCard({
  name,
  role,
  status,
  confidence,
  recommendation,
}: AgentCardProps) {
  const statusColors: Record<string, string> = {
    pending: "bg-gray-700",
    assessing: "bg-yellow-600 animate-pulse",
    completed: "bg-green-600",
    unavailable: "bg-red-600",
  };

  return (
    <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
      <div className="flex items-center justify-between mb-2">
        <div>
          <h4 className="font-medium text-sm">{name}</h4>
          <p className="text-xs text-gray-500">{role}</p>
        </div>
        <div className={`w-2 h-2 rounded-full ${statusColors[status]}`} />
      </div>
      {confidence !== undefined && (
        <div className="text-xs text-gray-400">
          Confidence: {(confidence * 100).toFixed(0)}%
        </div>
      )}
      {recommendation && (
        <p className="text-xs text-gray-500 mt-1 line-clamp-2">
          {recommendation}
        </p>
      )}
    </div>
  );
}
