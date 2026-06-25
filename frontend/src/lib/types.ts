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
  approval_rate: number;
  escalation_rate: number;
  memory_utilization_rate: number;
  avg_deliberation_time_s: number;
  department_performance: Record<string, number>;
  pending_approval: number;
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

export interface WorkflowSummary {
  id: string;
  name: string;
  departments: Array<{ id: string; role: string; model_tier: string }>;
}

export interface AdminWorkflowDetail {
  id: string;
  name: string;
  is_builtin: boolean;
  yaml_content: string;
  config: {
    id: string;
    name: string;
    departments: Array<{ id: string; role: string; model_tier: string; objectives: string[]; policies: string[]; tools: string[] }>;
    decision_dimensions: string[];
    consensus_threshold: number;
    policies: Array<{ id: string; rule: string; hard_constraint: boolean }>;
    required_role: string;
  };
}

export interface AdminWorkflowListResponse {
  workflows: Array<{
    id: string;
    name: string;
    is_builtin: boolean;
    departments: Array<{ id: string; role: string; model_tier: string }>;
    decision_dimensions: string[];
    consensus_threshold: number;
    policies: Array<{ id: string; rule: string; hard_constraint: boolean }>;
    required_role: string;
  }>;
}

export interface SaveWorkflowResponse {
  id: string;
  name: string;
  message: string;
}

export interface ValidationResult {
  valid: boolean;
  workflow_id: string | null;
  workflow_name: string | null;
  errors: string[];
  warnings: string[];
  summary: {
    workflow_id: string;
    workflow_name: string;
    departments: number;
    operational_departments: number;
    decision_dimensions: number;
    policies: number;
    hard_constraints: number;
    consensus_threshold: number;
    deadlock_resolution: string;
    required_role: string;
    agents_resolved: number;
  } | null;
}

export interface DemoCase {
  id: string;
  scenario: string;
  customer_id: string;
  request_text: string;
  description: string;
}

export interface CustomerSearchResult {
  id: string;
  name: string;
  email: string;
  company: string;
}

export interface ToolCallResult {
  actor: string;
  arguments: Record<string, unknown>;
  result: Record<string, unknown>;
  timestamp: string | null;
}

export interface ToolResults {
  case_id: string;
  tools: Record<string, ToolCallResult[]>;
  tool_count: number;
}

export interface TrendPoint {
  date: string;
  cases_created: number;
  cases_completed: number;
  avg_confidence: number;
}

export interface IntegrationHealth {
  [key: string]: {
    configured: boolean;
    status: string;
  };
}

export interface TenantInfo {
  id: string;
  name: string;
  slug: string;
  created_at: string | null;
}

export interface NotificationSettings {
  smtp_host: string;
  smtp_port: number;
  smtp_username: string;
  smtp_password: string;
  smtp_from: string;
  slack_webhook_url: string;
}
