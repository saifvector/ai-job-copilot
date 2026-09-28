import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useWebhookStore } from '../store/webhook-store';
import { apiClient, ApiClientError } from '../services/api-client';
import type { Webhook, WebhookTestResult, WebhookDeliveryLog } from '../types/platform';

vi.mock('../services/api-client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../services/api-client')>();
  return {
    ...actual,
    apiClient: {
      ...actual.apiClient,
      listWebhooks: vi.fn(),
      createWebhook: vi.fn(),
      updateWebhook: vi.fn(),
      deleteWebhook: vi.fn(),
      testWebhook: vi.fn(),
      getWebhookDeliveries: vi.fn(),
    },
  };
});

const mockWebhook: Webhook = {
  id: 'wh-123',
  endpoint: 'https://api.acme.com/webhooks',
  events: ['job.matched', 'application.created'],
  enabled: true,
  secret_preview: 'whsec_abcd',
  created_at: '2026-09-28T10:00:00Z',
  updated_at: '2026-09-28T10:00:00Z',
};

const mockDelivery: WebhookDeliveryLog = {
  id: 'del-123',
  webhook_id: 'wh-123',
  event: 'job.matched',
  status_code: 200,
  duration_ms: 45.5,
  success: true,
  error_message: null,
  created_at: '2026-09-28T10:05:00Z',
};

describe('Webhook Store (Phase 14)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useWebhookStore.setState({
      webhooks: [],
      selectedWebhookId: null,
      deliveries: [],
      testResult: null,
      loading: false,
      testing: false,
      error: null,
    });
  });

  it('fetches webhook subscriptions', async () => {
    vi.mocked(apiClient.listWebhooks).mockResolvedValueOnce({
      items: [mockWebhook],
      total: 1,
    });

    await useWebhookStore.getState().fetchWebhooks();

    const state = useWebhookStore.getState();
    expect(state.webhooks).toHaveLength(1);
    expect(state.webhooks[0].endpoint).toBe('https://api.acme.com/webhooks');
  });

  it('creates a new webhook subscription', async () => {
    vi.mocked(apiClient.createWebhook).mockResolvedValueOnce(mockWebhook);

    const res = await useWebhookStore.getState().createWebhook({
      endpoint: 'https://api.acme.com/webhooks',
      events: ['job.matched'],
    });

    expect(res).not.toBeNull();
    expect(useWebhookStore.getState().webhooks).toHaveLength(1);
  });

  it('updates an existing webhook subscription', async () => {
    useWebhookStore.setState({ webhooks: [mockWebhook] });
    const updatedWebhook: Webhook = {
      ...mockWebhook,
      enabled: false,
    };
    vi.mocked(apiClient.updateWebhook).mockResolvedValueOnce(updatedWebhook);

    const res = await useWebhookStore.getState().updateWebhook('wh-123', { enabled: false });
    expect(res?.enabled).toBe(false);
    expect(useWebhookStore.getState().webhooks[0].enabled).toBe(false);
  });

  it('deletes a webhook subscription', async () => {
    useWebhookStore.setState({ webhooks: [mockWebhook], selectedWebhookId: 'wh-123' });
    vi.mocked(apiClient.deleteWebhook).mockResolvedValueOnce({
      message: 'Deleted',
      webhook_id: 'wh-123',
    });

    const success = await useWebhookStore.getState().deleteWebhook('wh-123');
    expect(success).toBe(true);
    expect(useWebhookStore.getState().webhooks).toHaveLength(0);
    expect(useWebhookStore.getState().selectedWebhookId).toBeNull();
  });

  it('tests webhook delivery ping', async () => {
    const testResult: WebhookTestResult = {
      success: true,
      status_code: 200,
      duration_ms: 32.1,
      error: null,
      signature: 't=12345,v1=abcdef',
    };
    vi.mocked(apiClient.testWebhook).mockResolvedValueOnce(testResult);

    const res = await useWebhookStore.getState().testWebhook('wh-123', 'job.matched');
    expect(res?.success).toBe(true);
    expect(useWebhookStore.getState().testResult?.signature).toBe('t=12345,v1=abcdef');
  });

  it('fetches webhook delivery logs', async () => {
    vi.mocked(apiClient.getWebhookDeliveries).mockResolvedValueOnce({
      items: [mockDelivery],
      total: 1,
    });

    await useWebhookStore.getState().fetchDeliveries('wh-123');
    expect(useWebhookStore.getState().deliveries).toHaveLength(1);
    expect(useWebhookStore.getState().deliveries[0].status_code).toBe(200);
  });
});
