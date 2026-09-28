export interface AgentInfo {
  name: string;
  description: string;
  capabilities: string[];
  default_model: string;
  status: 'IDLE' | 'BUSY' | 'READY';
}

export interface AgentTask {
  id: string;
  user_id?: string;
  agent: string;
  workflow_execution_id?: string | null;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  payload: Record<string, any>;
  result?: Record<string, any> | null;
  error_message?: string | null;
  model_used?: string | null;
  duration_ms?: number | null;
  retry_count: number;
  max_retries: number;
  created_at: string;
  updated_at: string;
  completed_at?: string | null;
}

export interface AgentMemory {
  id: string;
  user_id: string;
  agent: string;
  memory_type: string;
  content: Record<string, any>;
  relevance_score: number;
  created_at: string;
}

export interface WorkflowStepSpec {
  step_id: string;
  agent: string;
  depends_on: string[];
  payload: Record<string, any>;
  on_failure: 'ABORT' | 'CONTINUE';
}

export interface WorkflowTemplate {
  workflow_id: string;
  name: string;
  description: string;
  steps: WorkflowStepSpec[];
}

export interface WorkflowStepRecord {
  step_id: string;
  step_name?: string;
  agent: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'SKIPPED';
  duration_ms?: number;
  model_used?: string;
  result_summary?: string;
  error?: string;
}

export interface WorkflowExecution {
  id: string;
  user_id: string;
  workflow_type: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  current_step?: string | null;
  steps: WorkflowStepRecord[];
  context: Record<string, any>;
  duration_ms?: number | null;
  created_at: string;
  updated_at: string;
  completed_at?: string | null;
}

export interface ObservabilityMetrics {
  total_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  running_tasks: number;
  pending_tasks: number;
  avg_duration_ms: number;
  failure_rate_pct: number;
  model_usage: Record<string, number>;
  registered_agents_count: number;
  active_workflows_count: number;
}

export interface ModelRouteRecommendation {
  selected_model: string;
  provider: string;
  rationale: string;
  estimated_cost_tier: string;
  context_window: number;
}
