import { create } from 'zustand';
import {
  ApiKey,
  ApiKeyCreated,
  ApiKeyCreatePayload,
  ApiKeyRotatePayload,
  ApiAnalyticsSummary,
  PluginManifest,
  PluginRegisterPayload,
  PluginExecutionResult,
} from '@/types';
import { apiClient, ApiClientError } from '@/services/api-client';

export interface DeveloperStoreState {
  apiKeys: ApiKey[];
  newKeySecret: ApiKeyCreated | null;
  analytics: ApiAnalyticsSummary | null;
  plugins: PluginManifest[];
  lastHookResult: PluginExecutionResult | null;
  loading: boolean;
  error: string | null;

  // Actions
  fetchApiKeys: () => Promise<void>;
  createApiKey: (payload: ApiKeyCreatePayload) => Promise<ApiKeyCreated | null>;
  rotateApiKey: (keyId: string, payload?: ApiKeyRotatePayload) => Promise<ApiKeyCreated | null>;
  revokeApiKey: (keyId: string) => Promise<boolean>;
  dismissNewKeySecret: () => void;
  fetchAnalytics: (days?: number) => Promise<void>;
  fetchPlugins: () => Promise<void>;
  registerPlugin: (payload: PluginRegisterPayload) => Promise<PluginManifest | null>;
  executePluginHook: (pluginId: string, hook: string, payload?: Record<string, any>) => Promise<PluginExecutionResult | null>;
  clearError: () => void;
}

export const useDeveloperStore = create<DeveloperStoreState>((set, get) => ({
  apiKeys: [],
  newKeySecret: null,
  analytics: null,
  plugins: [],
  lastHookResult: null,
  loading: false,
  error: null,

  fetchApiKeys: async () => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.listApiKeys();
      set({ apiKeys: response.items, loading: false });
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to fetch API keys';
      set({ error: message, loading: false });
    }
  },

  createApiKey: async (payload: ApiKeyCreatePayload) => {
    set({ loading: true, error: null });
    try {
      const created = await apiClient.createApiKey(payload);
      set((state) => ({
        apiKeys: [created, ...state.apiKeys],
        newKeySecret: created,
        loading: false,
      }));
      return created;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to create API key';
      set({ error: message, loading: false });
      return null;
    }
  },

  rotateApiKey: async (keyId: string, payload: ApiKeyRotatePayload = {}) => {
    set({ loading: true, error: null });
    try {
      const rotated = await apiClient.rotateApiKey(keyId, payload);
      set((state) => ({
        apiKeys: [rotated, ...state.apiKeys.filter((k) => k.id !== keyId)],
        newKeySecret: rotated,
        loading: false,
      }));
      return rotated;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to rotate API key';
      set({ error: message, loading: false });
      return null;
    }
  },

  revokeApiKey: async (keyId: string) => {
    set({ loading: true, error: null });
    try {
      await apiClient.revokeApiKey(keyId);
      set((state) => ({
        apiKeys: state.apiKeys.filter((k) => k.id !== keyId),
        loading: false,
      }));
      return true;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to revoke API key';
      set({ error: message, loading: false });
      return false;
    }
  },

  dismissNewKeySecret: () => {
    set({ newKeySecret: null });
  },

  fetchAnalytics: async (days: number = 7) => {
    set({ loading: true, error: null });
    try {
      const data = await apiClient.getApiAnalytics(days);
      set({ analytics: data, loading: false });
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to load API analytics';
      set({ error: message, loading: false });
    }
  },

  fetchPlugins: async () => {
    set({ loading: true, error: null });
    try {
      const res = await apiClient.listPlugins();
      set({ plugins: res.items, loading: false });
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to load plugins';
      set({ error: message, loading: false });
    }
  },

  registerPlugin: async (payload: PluginRegisterPayload) => {
    set({ loading: true, error: null });
    try {
      const created = await apiClient.registerPlugin(payload);
      set((state) => ({
        plugins: [...state.plugins, created],
        loading: false,
      }));
      return created;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to register plugin';
      set({ error: message, loading: false });
      return null;
    }
  },

  executePluginHook: async (pluginId: string, hook: string, payload: Record<string, any> = {}) => {
    try {
      const result = await apiClient.executePluginHook(pluginId, hook, payload);
      set({ lastHookResult: result });
      return result;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Hook execution failed';
      set({ error: message });
      return null;
    }
  },

  clearError: () => set({ error: null }),
}));
