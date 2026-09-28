import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useIntegrationStore } from '../store/integration-store';
import { apiClient, ApiClientError } from '../services/api-client';
import type { IntegrationStatus, OAuthConnection, OAuthSyncResult } from '../types/platform';

vi.mock('../services/api-client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../services/api-client')>();
  return {
    ...actual,
    apiClient: {
      ...actual.apiClient,
      listIntegrations: vi.fn(),
      connectIntegration: vi.fn(),
      disconnectIntegration: vi.fn(),
      syncIntegration: vi.fn(),
    },
  };
});

const mockIntegrationStatus: IntegrationStatus = {
  provider: 'gmail',
  category: 'email',
  display_name: 'Google Gmail',
  description: 'Sync application status and recruiter replies',
  connected: false,
  status: 'disconnected',
  scopes: ['https://www.googleapis.com/auth/gmail.readonly'],
  last_sync_at: null,
};

const mockConnection: OAuthConnection = {
  id: 'conn-123',
  user_id: 'user-123',
  provider: 'gmail',
  provider_user_id: 'user@example.com',
  scopes: ['https://www.googleapis.com/auth/gmail.readonly'],
  status: 'connected',
  metadata: {},
  last_sync_at: null,
  created_at: '2026-09-28T10:00:00Z',
  updated_at: '2026-09-28T10:00:00Z',
};

describe('Integration Store (Phase 14)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useIntegrationStore.setState({
      integrations: [],
      loading: false,
      syncingProvider: null,
      syncResult: null,
      error: null,
    });
  });

  it('fetches integration provider statuses', async () => {
    vi.mocked(apiClient.listIntegrations).mockResolvedValueOnce({
      items: [mockIntegrationStatus],
      total: 1,
    });

    await useIntegrationStore.getState().fetchIntegrations();

    const state = useIntegrationStore.getState();
    expect(state.integrations).toHaveLength(1);
    expect(state.integrations[0].provider).toBe('gmail');
  });

  it('connects an integration and refreshes status', async () => {
    vi.mocked(apiClient.connectIntegration).mockResolvedValueOnce(mockConnection);
    vi.mocked(apiClient.listIntegrations).mockResolvedValueOnce({
      items: [{ ...mockIntegrationStatus, connected: true, status: 'connected' }],
      total: 1,
    });

    const conn = await useIntegrationStore.getState().connectIntegration('gmail', { auth_code: 'code123' });
    expect(conn?.status).toBe('connected');

    expect(apiClient.listIntegrations).toHaveBeenCalled();
    expect(useIntegrationStore.getState().integrations[0].connected).toBe(true);
  });

  it('disconnects an integration successfully', async () => {
    vi.mocked(apiClient.disconnectIntegration).mockResolvedValueOnce({
      message: 'Disconnected',
      provider: 'gmail',
    });
    vi.mocked(apiClient.listIntegrations).mockResolvedValueOnce({
      items: [{ ...mockIntegrationStatus, connected: false }],
      total: 1,
    });

    const success = await useIntegrationStore.getState().disconnectIntegration('gmail');
    expect(success).toBe(true);
    expect(apiClient.disconnectIntegration).toHaveBeenCalledWith('gmail');
  });

  it('syncs an integration provider and updates state', async () => {
    const syncOutput: OAuthSyncResult = {
      provider: 'gmail',
      status: 'success',
      synced_items_count: 5,
      details: { messages_scanned: 10, recruiter_replies_found: 2 },
    };
    vi.mocked(apiClient.syncIntegration).mockResolvedValueOnce(syncOutput);
    vi.mocked(apiClient.listIntegrations).mockResolvedValueOnce({
      items: [{ ...mockIntegrationStatus, connected: true, last_sync_at: '2026-09-28T10:15:00Z' }],
      total: 1,
    });

    const res = await useIntegrationStore.getState().syncIntegration('gmail');
    expect(res?.synced_items_count).toBe(5);
    expect(useIntegrationStore.getState().syncResult?.status).toBe('success');
    expect(useIntegrationStore.getState().syncingProvider).toBeNull();
  });
});
