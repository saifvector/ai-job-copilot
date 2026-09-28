import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useDeveloperStore } from '../store/developer-store';
import { apiClient, ApiClientError } from '../services/api-client';
import type { ApiKey, ApiKeyCreated, ApiAnalyticsSummary, PluginManifest, PluginExecutionResult } from '../types/platform';

vi.mock('../services/api-client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../services/api-client')>();
  return {
    ...actual,
    apiClient: {
      ...actual.apiClient,
      listApiKeys: vi.fn(),
      createApiKey: vi.fn(),
      rotateApiKey: vi.fn(),
      revokeApiKey: vi.fn(),
      getApiAnalytics: vi.fn(),
      listPlugins: vi.fn(),
      registerPlugin: vi.fn(),
      executePluginHook: vi.fn(),
    },
  };
});

const mockApiKey: ApiKey = {
  id: 'key-123',
  name: 'CI/CD Pipeline',
  prefix: 'ajc_live_9999',
  scopes: ['read:profile', 'read:matches'],
  rate_limit: 60,
  monthly_limit: 10000,
  usage_count: 42,
  is_active: true,
  expires_at: null,
  last_used_at: '2026-09-28T10:00:00Z',
  created_at: '2026-09-28T09:00:00Z',
};

const mockApiKeyCreated: ApiKeyCreated = {
  ...mockApiKey,
  secret_key: 'ajc_live_9999_secret_token_123',
};

const mockAnalytics: ApiAnalyticsSummary = {
  period_days: 7,
  total_requests: 1250,
  total_errors: 10,
  error_rate: 0.8,
  p95_latency_ms: 45.2,
  endpoint_breakdown: [
    {
      endpoint: '/api/public/v1/profile',
      method: 'GET',
      count: 800,
      error_count: 2,
      avg_latency_ms: 18.5,
    },
  ],
};

const mockPlugin: PluginManifest = {
  id: 'notion_export',
  name: 'Notion Workspace Export',
  version: '1.0.0',
  description: 'Syncs resumes and applications to Notion',
  author: 'Platform Core',
  hooks: ['on_custom_export'],
  enabled: true,
};

describe('Developer Store (Phase 14)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useDeveloperStore.setState({
      apiKeys: [],
      newKeySecret: null,
      analytics: null,
      plugins: [],
      lastHookResult: null,
      loading: false,
      error: null,
    });
  });

  it('fetches api keys successfully', async () => {
    vi.mocked(apiClient.listApiKeys).mockResolvedValueOnce({
      items: [mockApiKey],
      total: 1,
    });

    await useDeveloperStore.getState().fetchApiKeys();

    const state = useDeveloperStore.getState();
    expect(state.apiKeys).toHaveLength(1);
    expect(state.apiKeys[0].name).toBe('CI/CD Pipeline');
    expect(state.loading).toBe(false);
  });

  it('creates an api key and stores raw secret for copy', async () => {
    vi.mocked(apiClient.createApiKey).mockResolvedValueOnce(mockApiKeyCreated);

    const res = await useDeveloperStore.getState().createApiKey({
      name: 'CI/CD Pipeline',
      scopes: ['read:profile'],
    });

    expect(res).not.toBeNull();
    expect(res?.secret_key).toBe('ajc_live_9999_secret_token_123');

    const state = useDeveloperStore.getState();
    expect(state.apiKeys).toHaveLength(1);
    expect(state.newKeySecret?.secret_key).toBe('ajc_live_9999_secret_token_123');

    // Dismiss key
    useDeveloperStore.getState().dismissNewKeySecret();
    expect(useDeveloperStore.getState().newKeySecret).toBeNull();
  });

  it('rotates an api key successfully', async () => {
    useDeveloperStore.setState({ apiKeys: [mockApiKey] });
    const rotatedKey: ApiKeyCreated = {
      ...mockApiKey,
      secret_key: 'ajc_live_new_rotated_secret',
    };
    vi.mocked(apiClient.rotateApiKey).mockResolvedValueOnce(rotatedKey);

    const res = await useDeveloperStore.getState().rotateApiKey('key-123');
    expect(res?.secret_key).toBe('ajc_live_new_rotated_secret');
    expect(useDeveloperStore.getState().apiKeys[0].id).toBe('key-123');
  });

  it('revokes an api key and updates store list', async () => {
    useDeveloperStore.setState({ apiKeys: [mockApiKey] });
    vi.mocked(apiClient.revokeApiKey).mockResolvedValueOnce({
      message: 'Key revoked',
      key_id: 'key-123',
    });

    const success = await useDeveloperStore.getState().revokeApiKey('key-123');
    expect(success).toBe(true);
    expect(useDeveloperStore.getState().apiKeys).toHaveLength(0);
  });

  it('fetches api analytics telemetry', async () => {
    vi.mocked(apiClient.getApiAnalytics).mockResolvedValueOnce(mockAnalytics);

    await useDeveloperStore.getState().fetchAnalytics(7);

    const state = useDeveloperStore.getState();
    expect(state.analytics).not.toBeNull();
    expect(state.analytics?.total_requests).toBe(1250);
    expect(state.analytics?.p95_latency_ms).toBe(45.2);
  });

  it('lists plugins and executes a plugin hook', async () => {
    vi.mocked(apiClient.listPlugins).mockResolvedValueOnce({
      items: [mockPlugin],
      total: 1,
    });

    const hookOutput: PluginExecutionResult = {
      plugin_id: 'notion_export',
      hook: 'on_custom_export',
      success: true,
      result: { page_id: 'notion_page_123', status: 'exported' },
    };
    vi.mocked(apiClient.executePluginHook).mockResolvedValueOnce(hookOutput);

    await useDeveloperStore.getState().fetchPlugins();
    expect(useDeveloperStore.getState().plugins).toHaveLength(1);

    const result = await useDeveloperStore.getState().executePluginHook(
      'notion_export',
      'on_custom_export',
      { title: 'Resume' }
    );

    expect(result?.success).toBe(true);
    expect(useDeveloperStore.getState().lastHookResult?.plugin_id).toBe('notion_export');
  });
});
