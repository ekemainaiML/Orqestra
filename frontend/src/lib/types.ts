export interface Case {
  id: string;
  customer_id: string;
  request_text: string;
  status: string;
  iteration: number;
  workflow_type: string;
  confidence: number | null;
  completeness: number | null;
  created_at: string | null;
  completed_at: string | null;
}

export interface CaseDetail extends Case {
  events: WorkflowEvent[];
  directives: Directive[];
}

export interface WorkflowEvent {
  id: string;
  case_id: string;
  event_type: string;
  actor: string;
  payload: Record<string, unknown> | null;
  iteration: number;
  timestamp: string | null;
}

export interface Directive {
  id: string;
  directive_type: string;
  value: Record<string, unknown>;
  iteration: number;
}

export interface DeliberationResult {
  status: string;
  case_id: string;
  assessment: { recommendations: unknown[]; challenges: unknown[] };
  consensus: Record<string, unknown>;
  decision: Record<string, unknown>;
  brief: Record<string, unknown>;
}

export interface DashboardMetrics {
  cases_today: number;
  total_cases: number;
  completed_cases: number;
  escalated_cases: number;
  average_confidence: number;
  total_events: number;
  memory_retrievals: number;
}

export interface BenchmarkResult {
  single_agent: MetricSet | null;
  organization: MetricSet | null;
  comparison: Comparison | null;
}

interface MetricSet {
  recommendation: Record<string, unknown>;
  confidence: number;
  risks_found: number;
  factors_considered: number;
  reasoning_time_s: number;
  memory_used: number;
}

interface Comparison {
  confidence_gain: number;
  risk_detection_improvement: number;
  factors_considered_gain: number;
  memory_utilization_gain: number;
}

export interface DemoCase {
  id: string;
  scenario: string;
  customer_id: string;
  request_text: string;
  description: string;
}
