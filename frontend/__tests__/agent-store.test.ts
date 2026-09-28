import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useAgentStore } from '../store/agent-store';
import { apiClient } from '../services/api-client';
import type { AgentInfo, AgentMemory, ModelRouteRecommendation } from '../types/agent';

vi.mock('../services/api-client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../services/api-client')>();
  return {
    ...actual,
    apiClient: {
      ...actual.apiClient,
      listAgents: vi.fn(),
      getAgent: vi.fn(),
      executeAgent: vi.fn(),
      listAgentMemories: vi.fn(),
      storeAgentMemory: vi.fn(),
      routeModel: vi.fn(),
    },
  };
});

const mockAgent: AgentInfo = {
  name: 'ResumeAgent',
  description: 'Analyzes resumes and scores ATS compatibility',
  capabilities: ['resume_analysis', 'ats_scoring'],
  default_model: 'gemini-2.5-pro',
  status: 'IDLE',
};

const mockMemory: AgentMemory = {
  id: 'mem-1',
  user_id: 'user-1',
  agent: 'ResumeAgent',
  memory_type: 'preference',
  content: { preferred_roles: ['Staff Engineer'] },
  relevance_score: 1.0,
  created_at: '2026-09-28T12:00:00Z',
};

const mockRecommendation: ModelRouteRecommendation = {
  selected_model: 'gemini-2.5-pro',
  provider: 'google',
  rationale: 'High complexity task routed to Gemini 2.5 Pro',
  estimated_cost_tier: 'medium',
  context_window: 1000000,
};

describe('useAgentStore', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAgentStore.setState({
      agents: [],
      selectedAgent: null,
      memories: [],
      routeRecommendation: null,
      lastExecutionResult: null,
      loading: false,
      executing: false,
      error: null,
    });
  });

  it('fetches registered agents and sets default selected agent', async () => {
    vi.mocked(apiClient.listAgents).mockResolvedValueOnce({
      items: [mockAgent],
      total: 1,
    });

    await useAgentStore.getState().fetchAgents();

    const state = useAgentStore.getState();
    expect(state.agents).toHaveLength(1);
    expect(state.agents[0].name).toBe('ResumeAgent');
    expect(state.selectedAgent?.name).toBe('ResumeAgent');
    expect(state.loading).toBe(false);
  });

  it('executes an agent directly and records execution result', async () => {
    const mockResult = {
      agent: 'ResumeAgent',
      status: 'COMPLETED',
      result: { ats_score: 92.5 },
      duration_ms: 85.0,
      model_used: 'gemini-2.5-pro',
    };
    vi.mocked(apiClient.executeAgent).mockResolvedValueOnce(mockResult);

    const result = await useAgentStore.getState().executeAgent('ResumeAgent', { mode: 'analyze' });

    expect(result).toEqual(mockResult);
    expect(useAgentStore.getState().lastExecutionResult).toEqual(mockResult);
    expect(useAgentStore.getState().executing).toBe(false);
  });

  it('fetches agent memories', async () => {
    vi.mocked(apiClient.listAgentMemories).mockResolvedValueOnce({
      items: [mockMemory],
      total: 1,
    });

    await useAgentStore.getState().fetchMemories('ResumeAgent');

    expect(useAgentStore.getState().memories).toHaveLength(1);
    expect(useAgentStore.getState().memories[0].agent).toBe('ResumeAgent');
  });

  it('evaluates model route recommendations', async () => {
    vi.mocked(apiClient.routeModel).mockResolvedValueOnce(mockRecommendation);

    const rec = await useAgentStore.getState().evaluateModelRoute('deep_reasoning', 'HIGH');

    expect(rec).toEqual(mockRecommendation);
    expect(useAgentStore.getState().routeRecommendation?.selected_model).toBe('gemini-2.5-pro');
  });
});
