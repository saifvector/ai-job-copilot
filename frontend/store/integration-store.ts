import { create } from 'zustand';
import {
  IntegrationStatus,
  OAuthConnectPayload,
  OAuthSyncResult,
  OAuthConnection,
} from '@/types';
import { apiClient, ApiClientError } from '@/services/api-client';

export interface IntegrationStoreState {
  integrations: IntegrationStatus[];
  loading: boolean;
  syncingProvider: string | null;
  syncResult: OAuthSyncResult | null;
  error: string | null;

  // Actions
  fetchIntegrations: () => Promise<void>;
  connectIntegration: (provider: string, payload?: OAuthConnectPayload) => Promise<OAuthConnection | null>;
  disconnectIntegration: (provider: string) => Promise<boolean>;
  syncIntegration: (provider: string) => Promise<OAuthSyncResult | null>;
  clearSyncResult: () => void;
  clearError: () => void;
}

export const useIntegrationStore = create<IntegrationStoreState>((set, get) => ({
  integrations: [],
  loading: false,
  syncingProvider: null,
  syncResult: null,
  error: null,

  fetchIntegrations: async () => {
    set({ loading: true, error: null });
    try {
      const res = await apiClient.listIntegrations();
      set({ integrations: res.items, loading: false });
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to fetch integrations';
      set({ error: message, loading: false });
    }
  },

  connectIntegration: async (provider: string, payload: OAuthConnectPayload = {}) => {
    set({ loading: true, error: null });
    try {
      const conn = await apiClient.connectIntegration(provider, payload);
      // Refresh integration statuses
      await get().fetchIntegrations();
      return conn;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : `Failed to connect ${provider}`;
      set({ error: message, loading: false });
      return null;
    }
  },

  disconnectIntegration: async (provider: string) => {
    set({ loading: true, error: null });
    try {
      await apiClient.disconnectIntegration(provider);
      // Refresh integration statuses
      await get().fetchIntegrations();
      return true;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : `Failed to disconnect ${provider}`;
      set({ error: message, loading: false });
      return false;
    }
  },

  syncIntegration: async (provider: string) => {
    set({ syncingProvider: provider, error: null, syncResult: null });
    try {
      const res = await apiClient.syncIntegration(provider);
      set({ syncResult: res, syncingProvider: null });
      // Refresh to update last_sync_at timestamp
      await get().fetchIntegrations();
      return res;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : `Failed to sync ${provider}`;
      set({ error: message, syncingProvider: null });
      return null;
    }
  },

  clearSyncResult: () => set({ syncResult: null }),
  clearError: () => set({ error: null }),
}));
