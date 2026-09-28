import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useWorkflowStore } from '../store/workflow-store';
import { apiClient } from '../services/api-client';
import type { WorkflowTemplate, WorkflowExecution, ObservabilityMetrics } from '../types/agent';

vi.mock('../services/api-client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../services/api-client')>();
  return {
    ...actual,
    apiClient: {
      ...actual.apiClient,
      listWorkflows: vi.fn(),
      getWorkflow: vi.fn(),
      executeWorkflow: vi.fn(),
      listWorkflowExecutions: vi.fn(),
      getWorkflowExecution: vi.fn(),
      getOrchestrationTelemetry: vi.fn(),
    },
  };
});

const mockTemplate: WorkflowTemplate = {
  workflow_id: 'resume_to_match_pipeline',
  name: 'Resume-to-Match Career Pipeline',
  description: 'Multi-agent career intelligence pipeline',
  steps: [
    {
      step_id: 'step_resume',
      agent: 'ResumeAgent',
      depends_on: [],
      payload: {},
      on_failure: 'ABORT',
    },
    {
      step_id: 'step_matching',
      agent: 'MatchingAgent',
      depends_on: ['step_resume'],
      payload: {},
      on_failure: 'ABORT',
    },
  ],
};

const mockExecution: WorkflowExecution = {
  id: 'exec-123',
  user_id: 'user-1',
  workflow_type: 'resume_to_match_pipeline',
  status: 'COMPLETED',
  current_step: 'FINISHED',
  steps: [
    {
      step_id: 'step_resume',
      agent: 'ResumeAgent',
      status: 'COMPLETED',
      duration_ms: 50.0,
      model_used: 'gemini-2.5-pro',
      result_summary: 'Evaluated resume with ATS score 90',
    },
  ],
  context: { ats_score: 90.0 },
  duration_ms: 120.5,
  created_at: '2026-09-28T12:00:00Z',
  updated_at: '2026-09-28T12:00:01Z',
};

const mockMetrics: ObservabilityMetrics = {
  total_tasks: 25,
  completed_tasks: 23,
  failed_tasks: 2,
  running_tasks: 0,
  pending_tasks: 0,
  avg_duration_ms: 110.5,
  failure_rate_pct: 8.0,
  model_usage: { 'gemini-2.5-flash': 20, 'gemini-2.5-pro': 5 },
  registered_agents_count: 8,
  active_workflows_count: 3,
};

describe('useWorkflowStore', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useWorkflowStore.setState({
      templates: [],
      executions: [],
      selectedExecution: null,
      selectedTemplate: null,
      metrics: null,
      loading: false,
      executing: false,
      error: null,
    });
  });

  it('fetches workflow templates and sets default template', async () => {
    vi.mocked(apiClient.listWorkflows).mockResolvedValueOnce([mockTemplate]);

    await useWorkflowStore.getState().fetchTemplates();

    const state = useWorkflowStore.getState();
    expect(state.templates).toHaveLength(1);
    expect(state.templates[0].workflow_id).toBe('resume_to_match_pipeline');
    expect(state.selectedTemplate?.workflow_id).toBe('resume_to_match_pipeline');
  });

  it('fetches execution history', async () => {
    vi.mocked(apiClient.listWorkflowExecutions).mockResolvedValueOnce({
      items: [mockExecution],
      total: 1,
    });

    await useWorkflowStore.getState().fetchExecutions();

    expect(useWorkflowStore.getState().executions).toHaveLength(1);
    expect(useWorkflowStore.getState().executions[0].id).toBe('exec-123');
  });

  it('executes a multi-agent workflow', async () => {
    vi.mocked(apiClient.executeWorkflow).mockResolvedValueOnce({
      execution_id: 'exec-123',
      status: 'COMPLETED',
      completed_steps: 2,
    });
    vi.mocked(apiClient.listWorkflowExecutions).mockResolvedValueOnce({
      items: [mockExecution],
      total: 1,
    });
    vi.mocked(apiClient.getOrchestrationTelemetry).mockResolvedValueOnce(mockMetrics);

    const result = await useWorkflowStore.getState().executeWorkflow('resume_to_match_pipeline');

    expect(result.status).toBe('COMPLETED');
    expect(useWorkflowStore.getState().executing).toBe(false);
  });

  it('fetches orchestration telemetry metrics', async () => {
    vi.mocked(apiClient.getOrchestrationTelemetry).mockResolvedValueOnce(mockMetrics);

    await useWorkflowStore.getState().fetchMetrics();

    expect(useWorkflowStore.getState().metrics?.total_tasks).toBe(25);
    expect(useWorkflowStore.getState().metrics?.registered_agents_count).toBe(8);
  });
});
