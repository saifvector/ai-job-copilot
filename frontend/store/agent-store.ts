import { create } from 'zustand';
import { AgentInfo, AgentMemory, ModelRouteRecommendation } from '@/types';
import { apiClient, ApiClientError } from '@/services/api-client';

export interface AgentStoreState {
  agents: AgentInfo[];
  selectedAgent: AgentInfo | null;
  memories: AgentMemory[];
  routeRecommendation: ModelRouteRecommendation | null;
  lastExecutionResult: Record<string, any> | null;
  loading: boolean;
  executing: boolean;
  error: string | null;

  // Actions
  fetchAgents: () => Promise<void>;
  selectAgent: (agent: AgentInfo | null) => void;
  executeAgent: (agentName: string, payload: Record<string, any>, modelOverride?: string) => Promise<any>;
  fetchMemories: (agent?: string) => Promise<void>;
  storeMemory: (agent: string, memoryType: string, content: Record<string, any>, score?: number) => Promise<AgentMemory | null>;
  evaluateModelRoute: (taskType: string, complexity?: string, speed?: string, cost?: string, privacy?: string) => Promise<ModelRouteRecommendation | null>;
  clearError: () => void;
}

export const useAgentStore = create<AgentStoreState>((set, get) => ({
  agents: [],
  selectedAgent: null,
  memories: [],
  routeRecommendation: null,
  lastExecutionResult: null,
  loading: false,
  executing: false,
  error: null,

  fetchAgents: async () => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.listAgents();
      set({
        agents: response.items,
        selectedAgent: response.items.length > 0 && !get().selectedAgent ? response.items[0] : get().selectedAgent,
        loading: false,
      });
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to fetch registered agents';
      set({ error: message, loading: false });
    }
  },

  selectAgent: (agent) => {
    set({ selectedAgent: agent });
  },

  executeAgent: async (agentName: string, payload: Record<string, any>, modelOverride?: string) => {
    set({ executing: true, error: null });
    try {
      const res = await apiClient.executeAgent(agentName, payload, modelOverride);
      set({ lastExecutionResult: res, executing: false });
      return res;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : `Execution of ${agentName} failed`;
      set({ error: message, executing: false });
      return null;
    }
  },

  fetchMemories: async (agent?: string) => {
    try {
      const response = await apiClient.listAgentMemories(agent);
      set({ memories: response.items });
    } catch (err) {
      console.error('Failed to fetch agent memories', err);
    }
  },

  storeMemory: async (agent, memoryType, content, score = 1.0) => {
    try {
      const created = await apiClient.storeAgentMemory({
        agent,
        memory_type: memoryType,
        content,
        relevance_score: score,
      });
      set((state) => ({ memories: [created, ...state.memories] }));
      return created;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to persist agent memory';
      set({ error: message });
      return null;
    }
  },

  evaluateModelRoute: async (taskType, complexity = 'MEDIUM', speed = 'BALANCED', cost = 'STANDARD', privacy = 'CLOUD') => {
    try {
      const recommendation = await apiClient.routeModel({
        task_type: taskType,
        complexity,
        speed_preference: speed,
        cost_preference: cost,
        privacy_level: privacy,
      });
      set({ routeRecommendation: recommendation });
      return recommendation;
    } catch (err) {
      console.error('Model route evaluation failed', err);
      return null;
    }
  },

  clearError: () => set({ error: null }),
}));
