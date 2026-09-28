import { create } from 'zustand';
import { ObservabilityMetrics, WorkflowExecution, WorkflowTemplate } from '@/types';
import { apiClient, ApiClientError } from '@/services/api-client';

export interface WorkflowStoreState {
  templates: WorkflowTemplate[];
  executions: WorkflowExecution[];
  selectedExecution: WorkflowExecution | null;
  selectedTemplate: WorkflowTemplate | null;
  metrics: ObservabilityMetrics | null;
  loading: boolean;
  executing: boolean;
  error: string | null;

  // Actions
  fetchTemplates: () => Promise<void>;
  fetchExecutions: (workflowType?: string, status?: string) => Promise<void>;
  fetchExecutionDetail: (id: string) => Promise<WorkflowExecution | null>;
  executeWorkflow: (workflowType: string, initialContext?: Record<string, any>) => Promise<any>;
  fetchMetrics: () => Promise<void>;
  selectTemplate: (template: WorkflowTemplate | null) => void;
  selectExecution: (execution: WorkflowExecution | null) => void;
  clearError: () => void;
}

export const useWorkflowStore = create<WorkflowStoreState>((set, get) => ({
  templates: [],
  executions: [],
  selectedExecution: null,
  selectedTemplate: null,
  metrics: null,
  loading: false,
  executing: false,
  error: null,

  fetchTemplates: async () => {
    set({ loading: true, error: null });
    try {
      const templates = await apiClient.listWorkflows();
      set({
        templates,
        selectedTemplate: templates.length > 0 && !get().selectedTemplate ? templates[0] : get().selectedTemplate,
        loading: false,
      });
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to fetch workflow templates';
      set({ error: message, loading: false });
    }
  },

  fetchExecutions: async (workflowType, status) => {
    try {
      const res = await apiClient.listWorkflowExecutions({
        workflow_type: workflowType,
        status,
      });
      set({ executions: res.items });
    } catch (err) {
      console.error('Failed to fetch workflow executions', err);
    }
  },

  fetchExecutionDetail: async (id: string) => {
    try {
      const detail = await apiClient.getWorkflowExecution(id);
      set({ selectedExecution: detail });
      return detail;
    } catch (err) {
      console.error('Failed to fetch execution detail', err);
      return null;
    }
  },

  executeWorkflow: async (workflowType: string, initialContext: Record<string, any> = {}) => {
    set({ executing: true, error: null });
    try {
      const result = await apiClient.executeWorkflow({
        workflow_type: workflowType,
        initial_context: initialContext,
      });
      set({ executing: false });
      // Refresh executions list
      await get().fetchExecutions();
      await get().fetchMetrics();
      return result;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : `Workflow execution for ${workflowType} failed`;
      set({ error: message, executing: false });
      return null;
    }
  },

  fetchMetrics: async () => {
    try {
      const telemetry = await apiClient.getOrchestrationTelemetry();
      set({ metrics: telemetry });
    } catch (err) {
      console.error('Failed to fetch orchestration metrics', err);
    }
  },

  selectTemplate: (template) => set({ selectedTemplate: template }),
  selectExecution: (execution) => set({ selectedExecution: execution }),
  clearError: () => set({ error: null }),
}));
