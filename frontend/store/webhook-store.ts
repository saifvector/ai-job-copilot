import { create } from 'zustand';
import {
  Webhook,
  WebhookCreatePayload,
  WebhookUpdatePayload,
  WebhookTestResult,
  WebhookDeliveryLog,
} from '@/types';
import { apiClient, ApiClientError } from '@/services/api-client';

export interface WebhookStoreState {
  webhooks: Webhook[];
  selectedWebhookId: string | null;
  deliveries: WebhookDeliveryLog[];
  testResult: WebhookTestResult | null;
  loading: boolean;
  testing: boolean;
  error: string | null;

  // Actions
  fetchWebhooks: () => Promise<void>;
  createWebhook: (payload: WebhookCreatePayload) => Promise<Webhook | null>;
  updateWebhook: (id: string, payload: WebhookUpdatePayload) => Promise<Webhook | null>;
  deleteWebhook: (id: string) => Promise<boolean>;
  testWebhook: (id: string, event?: string) => Promise<WebhookTestResult | null>;
  fetchDeliveries: (id: string, limit?: number) => Promise<void>;
  selectWebhook: (id: string | null) => void;
  clearTestResult: () => void;
  clearError: () => void;
}

export const useWebhookStore = create<WebhookStoreState>((set, get) => ({
  webhooks: [],
  selectedWebhookId: null,
  deliveries: [],
  testResult: null,
  loading: false,
  testing: false,
  error: null,

  fetchWebhooks: async () => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.listWebhooks();
      set({ webhooks: response.items, loading: false });
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to fetch webhooks';
      set({ error: message, loading: false });
    }
  },

  createWebhook: async (payload: WebhookCreatePayload) => {
    set({ loading: true, error: null });
    try {
      const created = await apiClient.createWebhook(payload);
      set((state) => ({
        webhooks: [created, ...state.webhooks],
        loading: false,
      }));
      return created;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to register webhook';
      set({ error: message, loading: false });
      return null;
    }
  },

  updateWebhook: async (id: string, payload: WebhookUpdatePayload) => {
    set({ loading: true, error: null });
    try {
      const updated = await apiClient.updateWebhook(id, payload);
      set((state) => ({
        webhooks: state.webhooks.map((w) => (w.id === id ? updated : w)),
        loading: false,
      }));
      return updated;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to update webhook';
      set({ error: message, loading: false });
      return null;
    }
  },

  deleteWebhook: async (id: string) => {
    set({ loading: true, error: null });
    try {
      await apiClient.deleteWebhook(id);
      set((state) => ({
        webhooks: state.webhooks.filter((w) => w.id !== id),
        selectedWebhookId: state.selectedWebhookId === id ? null : state.selectedWebhookId,
        loading: false,
      }));
      return true;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to delete webhook';
      set({ error: message, loading: false });
      return false;
    }
  },

  testWebhook: async (id: string, event: string = 'job.matched') => {
    set({ testing: true, error: null, testResult: null });
    try {
      const res = await apiClient.testWebhook(id, event);
      set({ testResult: res, testing: false });
      return res;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Webhook test delivery failed';
      set({ error: message, testing: false });
      return null;
    }
  },

  fetchDeliveries: async (id: string, limit: number = 20) => {
    try {
      const res = await apiClient.getWebhookDeliveries(id, limit);
      set({ deliveries: res.items, selectedWebhookId: id });
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to load delivery logs';
      set({ error: message });
    }
  },

  selectWebhook: (id: string | null) => {
    set({ selectedWebhookId: id });
    if (id) {
      get().fetchDeliveries(id);
    } else {
      set({ deliveries: [], testResult: null });
    }
  },

  clearTestResult: () => set({ testResult: null }),
  clearError: () => set({ error: null }),
}));
