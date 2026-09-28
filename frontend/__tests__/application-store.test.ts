import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useApplicationStore } from '../store/application-store';
import { apiClient, ApiClientError } from '../services/api-client';
import type {
  Application,
  ApplicationAnalytics,
  ApplicationListItem,
  PipelineData,
} from '../types/application';

vi.mock('../services/api-client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../services/api-client')>();
  return {
    ...actual,
    apiClient: {
      ...actual.apiClient,
      getApplications: vi.fn(),
      getApplicationPipeline: vi.fn(),
      getApplicationAnalytics: vi.fn(),
      getApplicationById: vi.fn(),
      createApplication: vi.fn(),
      updateApplicationStatus: vi.fn(),
      updateApplicationNotes: vi.fn(),
      addApplicationEvent: vi.fn(),
      addApplicationInterview: vi.fn(),
      deleteApplication: vi.fn(),
    },
  };
});

const mockApplicationListItem: ApplicationListItem = {
  id: 'app-00000000-0000-0000-0000-000000000001',
  userId: 'u-00000000-0000-0000-0000-000000000001',
  jobId: 'j-00000000-0000-0000-0000-000000000001',
  jobTitle: 'Senior Platform Engineer',
  jobCompany: 'Datadog',
  jobLocation: 'Remote',
  status: 'APPLIED',
  applicationDate: '2026-09-20T12:00:00Z',
  lastUpdated: '2026-09-27T12:00:00Z',
  source: 'Wellfound',
  notes: 'Submitted customized resume',
  interviewCount: 1,
  nextInterviewDate: '2026-10-05T14:00:00Z',
  tailoredResumeId: 'tr-1',
};

const mockApplication: Application = {
  id: 'app-00000000-0000-0000-0000-000000000001',
  userId: 'u-00000000-0000-0000-0000-000000000001',
  jobId: 'j-00000000-0000-0000-0000-000000000001',
  tailoredResumeId: 'tr-1',
  status: 'APPLIED',
  applicationDate: '2026-09-20T12:00:00Z',
  lastUpdated: '2026-09-27T12:00:00Z',
  source: 'Wellfound',
  notes: 'Submitted customized resume',
  createdAt: '2026-09-20T12:00:00Z',
  job: {
    id: 'j-00000000-0000-0000-0000-000000000001',
    title: 'Senior Platform Engineer',
    company: 'Datadog',
    location: 'Remote',
    employmentType: 'Full-time',
    applyUrl: 'https://example.com/apply/1',
    salaryMin: 180000,
    salaryMax: 220000,
    currency: 'USD',
  },
  events: [
    {
      id: 'e-1',
      applicationId: 'app-00000000-0000-0000-0000-000000000001',
      eventType: 'CREATED',
      description: 'Application tracked as SAVED',
      createdAt: '2026-09-20T12:00:00Z',
    },
    {
      id: 'e-2',
      applicationId: 'app-00000000-0000-0000-0000-000000000001',
      eventType: 'STATUS_CHANGE',
      description: 'Transitioned to APPLIED',
      createdAt: '2026-09-21T10:00:00Z',
    },
  ],
  interviews: [
    {
      id: 'i-1',
      applicationId: 'app-00000000-0000-0000-0000-000000000001',
      interviewType: 'TECHNICAL',
      interviewDate: '2026-10-05T14:00:00Z',
      interviewRound: 1,
      notes: 'Prepare concurrency topics',
      createdAt: '2026-09-25T11:00:00Z',
      updatedAt: '2026-09-25T11:00:00Z',
    },
  ],
};

const mockPipeline: PipelineData = {
  saved: [],
  applied: [mockApplicationListItem],
  assessment: [],
  interview: [],
  offer: [],
  rejected: [],
  withdrawn: [],
  totalActive: 1,
  totalApplications: 1,
};

const mockAnalytics: ApplicationAnalytics = {
  totalApplications: 12,
  applicationsSent: 10,
  interviewsReceived: 4,
  offersReceived: 2,
  rejections: 2,
  responseRate: 80.0,
  interviewRate: 40.0,
  offerRate: 20.0,
  byStatus: {
    SAVED: 2,
    APPLIED: 4,
    ASSESSMENT: 1,
    INTERVIEW: 1,
    OFFER: 2,
    REJECTED: 2,
    WITHDRAWN: 0,
  },
  bySource: {
    Wellfound: 5,
    RemoteOK: 5,
    Direct: 2,
  },
  interviewsScheduledUpcoming: 2,
  applicationsThisMonth: 6,
};

describe('useApplicationStore', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useApplicationStore.setState({
      applications: [],
      pipeline: {
        saved: [],
        applied: [],
        assessment: [],
        interview: [],
        offer: [],
        rejected: [],
        withdrawn: [],
        totalActive: 0,
        totalApplications: 0,
      },
      selectedApplication: null,
      analytics: null,
      loading: false,
      analyticsLoading: false,
      actionLoading: false,
      error: null,
    });
  });

  it('initializes with default empty state', () => {
    const state = useApplicationStore.getState();
    expect(state.applications).toEqual([]);
    expect(state.pipeline.totalApplications).toBe(0);
    expect(state.selectedApplication).toBeNull();
    expect(state.analytics).toBeNull();
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
  });

  it('fetches applications list successfully', async () => {
    vi.mocked(apiClient.getApplications).mockResolvedValueOnce({
      success: true,
      data: [mockApplicationListItem],
      timestamp: '2026-09-27T12:00:00Z',
    });

    await useApplicationStore.getState().fetchApplications();

    const state = useApplicationStore.getState();
    expect(state.applications).toHaveLength(1);
    expect(state.applications[0].jobTitle).toBe('Senior Platform Engineer');
    expect(state.loading).toBe(false);
  });

  it('handles error when fetching applications fails', async () => {
    vi.mocked(apiClient.getApplications).mockRejectedValueOnce(
      new ApiClientError('Internal error', 500)
    );

    await useApplicationStore.getState().fetchApplications();

    const state = useApplicationStore.getState();
    expect(state.applications).toEqual([]);
    expect(state.error).toBe('Internal error');
    expect(state.loading).toBe(false);
  });

  it('fetches pipeline Kanban data successfully', async () => {
    vi.mocked(apiClient.getApplicationPipeline).mockResolvedValueOnce({
      success: true,
      data: mockPipeline,
      timestamp: '2026-09-27T12:00:00Z',
    });

    await useApplicationStore.getState().fetchPipeline();

    const state = useApplicationStore.getState();
    expect(state.pipeline.applied).toHaveLength(1);
    expect(state.pipeline.totalActive).toBe(1);
    expect(state.loading).toBe(false);
  });

  it('fetches pipeline analytics successfully', async () => {
    vi.mocked(apiClient.getApplicationAnalytics).mockResolvedValueOnce({
      success: true,
      data: mockAnalytics,
      timestamp: '2026-09-27T12:00:00Z',
    });

    await useApplicationStore.getState().fetchAnalytics();

    const state = useApplicationStore.getState();
    expect(state.analytics).not.toBeNull();
    expect(state.analytics?.responseRate).toBe(80.0);
    expect(state.analytics?.interviewRate).toBe(40.0);
    expect(state.analyticsLoading).toBe(false);
  });

  it('selects application by ID and loads full details', async () => {
    vi.mocked(apiClient.getApplicationById).mockResolvedValueOnce({
      success: true,
      data: mockApplication,
      timestamp: '2026-09-27T12:00:00Z',
    });

    const res = await useApplicationStore
      .getState()
      .selectApplicationById('app-00000000-0000-0000-0000-000000000001');

    expect(res).not.toBeNull();
    expect(res?.id).toBe(mockApplication.id);
    expect(useApplicationStore.getState().selectedApplication?.job?.company).toBe('Datadog');
    expect(useApplicationStore.getState().loading).toBe(false);
  });

  it('creates an application and triggers pipeline & analytics refresh', async () => {
    vi.mocked(apiClient.createApplication).mockResolvedValueOnce({
      success: true,
      data: mockApplication,
      timestamp: '2026-09-27T12:00:00Z',
    });
    vi.mocked(apiClient.getApplicationPipeline).mockResolvedValueOnce({
      success: true,
      data: mockPipeline,
      timestamp: '2026-09-27T12:00:00Z',
    });
    vi.mocked(apiClient.getApplicationAnalytics).mockResolvedValueOnce({
      success: true,
      data: mockAnalytics,
      timestamp: '2026-09-27T12:00:00Z',
    });

    const created = await useApplicationStore.getState().createApplication({
      jobId: 'j-00000000-0000-0000-0000-000000000001',
      status: 'APPLIED',
    });

    expect(created).not.toBeNull();
    expect(apiClient.createApplication).toHaveBeenCalled();
    expect(apiClient.getApplicationPipeline).toHaveBeenCalled();
    expect(apiClient.getApplicationAnalytics).toHaveBeenCalled();
    expect(useApplicationStore.getState().actionLoading).toBe(false);
  });

  it('performs optimistic update on updateStatus and handles rollback on failure', async () => {
    useApplicationStore.setState({
      pipeline: mockPipeline,
    });

    // Test failure rollback
    vi.mocked(apiClient.updateApplicationStatus).mockRejectedValueOnce(
      new ApiClientError('Transition forbidden', 400)
    );

    const res = await useApplicationStore
      .getState()
      .updateStatus('app-00000000-0000-0000-0000-000000000001', 'OFFER');

    expect(res).toBeNull();
    // After error, pipeline is rolled back to original
    expect(useApplicationStore.getState().pipeline.applied).toHaveLength(1);
    expect(useApplicationStore.getState().error).toBe('Transition forbidden');
  });

  it('updates notes on application', async () => {
    const updatedApp = { ...mockApplication, notes: 'Updated salary expectation: $210k' };
    vi.mocked(apiClient.updateApplicationNotes).mockResolvedValueOnce({
      success: true,
      data: updatedApp,
      timestamp: '2026-09-27T12:00:00Z',
    });
    vi.mocked(apiClient.getApplicationPipeline).mockResolvedValueOnce({
      success: true,
      data: mockPipeline,
      timestamp: '2026-09-27T12:00:00Z',
    });

    const res = await useApplicationStore
      .getState()
      .updateNotes('app-00000000-0000-0000-0000-000000000001', 'Updated salary expectation: $210k');

    expect(res?.notes).toBe('Updated salary expectation: $210k');
    expect(useApplicationStore.getState().selectedApplication?.notes).toBe(
      'Updated salary expectation: $210k'
    );
  });

  it('deletes application and refreshes pipeline', async () => {
    useApplicationStore.setState({
      selectedApplication: mockApplication,
    });

    vi.mocked(apiClient.deleteApplication).mockResolvedValueOnce({
      success: true,
      data: true,
      timestamp: '2026-09-27T12:00:00Z',
    });
    vi.mocked(apiClient.getApplicationPipeline).mockResolvedValueOnce({
      success: true,
      data: { ...mockPipeline, applied: [], totalApplications: 0, totalActive: 0 },
      timestamp: '2026-09-27T12:00:00Z',
    });
    vi.mocked(apiClient.getApplicationAnalytics).mockResolvedValueOnce({
      success: true,
      data: { ...mockAnalytics, totalApplications: 0 },
      timestamp: '2026-09-27T12:00:00Z',
    });

    const ok = await useApplicationStore
      .getState()
      .deleteApplication('app-00000000-0000-0000-0000-000000000001');

    expect(ok).toBe(true);
    expect(useApplicationStore.getState().selectedApplication).toBeNull();
  });

  it('clears selection and errors cleanly', () => {
    useApplicationStore.setState({
      selectedApplication: mockApplication,
      error: 'Some error message',
    });

    useApplicationStore.getState().clearError();
    expect(useApplicationStore.getState().error).toBeNull();

    useApplicationStore.getState().clearSelected();
    expect(useApplicationStore.getState().selectedApplication).toBeNull();
  });
});
