import { create } from 'zustand';
import { AgentTask } from '@/types';
import { apiClient, ApiClientError } from '@/services/api-client';

export interface TaskStoreState {
  tasks: AgentTask[];
  selectedTask: AgentTask | null;
  filterStatus: string | null;
  filterAgent: string | null;
  loading: boolean;
  actionLoading: boolean;
  error: string | null;

  // Actions
  fetchTasks: () => Promise<void>;
  createTask: (agent: string, payload: Record<string, any>, modelOverride?: string) => Promise<AgentTask | null>;
  retryTask: (id: string) => Promise<boolean>;
  cancelTask: (id: string) => Promise<boolean>;
  selectTask: (task: AgentTask | null) => void;
  setFilterStatus: (status: string | null) => void;
  setFilterAgent: (agent: string | null) => void;
  clearError: () => void;
}

export const useTaskStore = create<TaskStoreState>((set, get) => ({
  tasks: [],
  selectedTask: null,
  filterStatus: null,
  filterAgent: null,
  loading: false,
  actionLoading: false,
  error: null,

  fetchTasks: async () => {
    set({ loading: true, error: null });
    try {
      const { filterAgent, filterStatus } = get();
      const res = await apiClient.listTasks({
        agent: filterAgent || undefined,
        status: filterStatus || undefined,
      });
      set({
        tasks: res.items,
        selectedTask: res.items.length > 0 && !get().selectedTask ? res.items[0] : get().selectedTask,
        loading: false,
      });
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to fetch agent tasks';
      set({ error: message, loading: false });
    }
  },

  createTask: async (agent, payload, modelOverride) => {
    set({ actionLoading: true, error: null });
    try {
      const created = await apiClient.createTask({
        agent,
        payload,
        model_override: modelOverride,
      });
      set((state) => ({
        tasks: [created, ...state.tasks],
        actionLoading: false,
      }));
      return created;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to enqueue agent task';
      set({ error: message, actionLoading: false });
      return null;
    }
  },

  retryTask: async (id: string) => {
    set({ actionLoading: true, error: null });
    try {
      const retried = await apiClient.retryTask(id);
      set((state) => ({
        tasks: state.tasks.map((t) => (t.id === id ? retried : t)),
        selectedTask: state.selectedTask?.id === id ? retried : state.selectedTask,
        actionLoading: false,
      }));
      return true;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to retry task';
      set({ error: message, actionLoading: false });
      return false;
    }
  },

  cancelTask: async (id: string) => {
    set({ actionLoading: true, error: null });
    try {
      const cancelled = await apiClient.cancelTask(id);
      set((state) => ({
        tasks: state.tasks.map((t) => (t.id === id ? cancelled : t)),
        selectedTask: state.selectedTask?.id === id ? cancelled : state.selectedTask,
        actionLoading: false,
      }));
      return true;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to cancel task';
      set({ error: message, actionLoading: false });
      return false;
    }
  },

  selectTask: (task) => set({ selectedTask: task }),
  setFilterStatus: (status) => {
    set({ filterStatus: status });
    get().fetchTasks();
  },
  setFilterAgent: (agent) => {
    set({ filterAgent: agent });
    get().fetchTasks();
  },
  clearError: () => set({ error: null }),
}));
