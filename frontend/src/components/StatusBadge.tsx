const STATUS_CONFIG: Record<
  string,
  { label: string; className: string }
> = {
  created: { label: "Created", className: "tag-default" },
  memory_retrieval: { label: "Memory Retrieval", className: "tag-info" },
  independent_assessment: {
    label: "Assessing",
    className: "tag-info",
  },
  challenge_round: { label: "Challenge Round", className: "tag-warning" },
  consensus_scoring: { label: "Scoring", className: "tag-info" },
  adjudication: { label: "Adjudication", className: "tag-warning" },
  approval_pending: { label: "Approval Pending", className: "tag-warning" },
  completed: { label: "Completed", className: "tag-success" },
  escalated: { label: "Escalated", className: "tag-danger" },
};

export function StatusBadge({ status }: { status: string }) {
  const config = STATUS_CONFIG[status] ?? {
    label: status,
    className: "tag-default",
  };
  return <span className={config.className}>{config.label}</span>;
}
