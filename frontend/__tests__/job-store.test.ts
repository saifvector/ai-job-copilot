import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useJobStore } from '../store/job-store';
import { apiClient, ApiClientError } from '../services/api-client';
import type { Job, JobListData, JobSyncData } from '../types/job';

vi.mock('../services/api-client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../services/api-client')>();
  return {
    ...actual,
    apiClient: {
      ...actual.apiClient,
      getJobs: vi.fn(),
      searchJobs: vi.fn(),
      getJobById: vi.fn(),
      syncJobs: vi.fn(),
    },
  };
});

const mockJob: Job = {
  id: 'j-00000000-0000-0000-0000-000000000001',
  source: 'RemoteOK',
  externalId: 'remoteok-101',
  title: 'Senior Backend Engineer',
  company: 'Automattic',
  location: 'Remote',
  employmentType: 'Full-time',
  salaryMin: 140000,
  salaryMax: 185000,
  currency: 'USD',
  description: 'Scalable backend services using Python and FastAPI.',
  requirements: '5+ years experience with distributed systems and PostgreSQL.',
  applyUrl: 'https://remoteok.com/apply/101',
  companyWebsite: 'https://automattic.com',
  postedAt: '2026-09-25T12:00:00Z',
  createdAt: '2026-09-27T10:00:00Z',
  updatedAt: '2026-09-27T10:00:00Z',
  skills: ['Python', 'FastAPI', 'PostgreSQL', 'Docker'],
};

const mockListData: JobListData = {
  items: [mockJob],
  total: 1,
  page: 1,
  pageSize: 20,
  totalPages: 1,
};

const mockSyncData: JobSyncData = {
  syncedCount: 12,
  duplicatesSkipped: 3,
  errorsCount: 0,
  sources: { RemoteOK: 4, Greenhouse: 3, Lever: 3, Wellfound: 2 },
  durationMs: 420.5,
  message: 'Synchronized 12 jobs from 4 sources.',
};

describe('useJobStore', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useJobStore.setState({
      jobs: [],
      selectedJob: null,
      filters: {
        query: '',
        role: '',
        location: '',
        source: '',
        skill: '',
        minSalary: undefined,
        sortBy: 'newest',
        page: 1,
        pageSize: 20,
      },
      loading: false,
      error: null,
      total: 0,
      page: 1,
      pageSize: 20,
      totalPages: 0,
      syncing: false,
      syncResult: null,
    });
  });

  it('initializes with default empty state', () => {
    const state = useJobStore.getState();
    expect(state.jobs).toEqual([]);
    expect(state.selectedJob).toBeNull();
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
    expect(state.total).toBe(0);
    expect(state.filters.sortBy).toBe('newest');
  });

  it('fetches jobs list successfully', async () => {
    vi.mocked(apiClient.getJobs).mockResolvedValueOnce({
      success: true,
      data: mockListData,
      timestamp: '2026-09-27T10:00:00Z',
    });

    await useJobStore.getState().fetchJobs();

    const state = useJobStore.getState();
    expect(state.jobs).toEqual([mockJob]);
    expect(state.total).toBe(1);
    expect(state.loading).toBe(false);
    expect(apiClient.getJobs).toHaveBeenCalledTimes(1);
  });

  it('searches jobs with filter overrides', async () => {
    vi.mocked(apiClient.searchJobs).mockResolvedValueOnce({
      success: true,
      data: mockListData,
      timestamp: '2026-09-27T10:00:00Z',
    });

    await useJobStore.getState().searchJobs({ role: 'Backend', location: 'Remote' });

    const state = useJobStore.getState();
    expect(state.filters.role).toBe('Backend');
    expect(state.filters.location).toBe('Remote');
    expect(state.jobs.length).toBe(1);
    expect(apiClient.searchJobs).toHaveBeenCalledWith(
      expect.objectContaining({ role: 'Backend', location: 'Remote' })
    );
  });

  it('selects and deselects job', () => {
    useJobStore.getState().selectJob(mockJob);
    expect(useJobStore.getState().selectedJob).toEqual(mockJob);

    useJobStore.getState().selectJob(null);
    expect(useJobStore.getState().selectedJob).toBeNull();
  });

  it('fetches individual job details', async () => {
    vi.mocked(apiClient.getJobById).mockResolvedValueOnce({
      success: true,
      data: mockJob,
      timestamp: '2026-09-27T10:00:00Z',
    });

    await useJobStore.getState().fetchJobDetails(mockJob.id);

    const state = useJobStore.getState();
    expect(state.selectedJob).toEqual(mockJob);
    expect(state.loading).toBe(false);
    expect(apiClient.getJobById).toHaveBeenCalledWith(mockJob.id);
  });

  it('synchronizes jobs and stores sync result', async () => {
    vi.mocked(apiClient.syncJobs).mockResolvedValueOnce({
      success: true,
      data: mockSyncData,
      timestamp: '2026-09-27T10:00:00Z',
    });
    vi.mocked(apiClient.getJobs).mockResolvedValueOnce({
      success: true,
      data: mockListData,
      timestamp: '2026-09-27T10:00:00Z',
    });

    const success = await useJobStore.getState().syncJobs();

    expect(success).toBe(true);
    const state = useJobStore.getState();
    expect(state.syncing).toBe(false);
    expect(state.syncResult).toEqual(mockSyncData);
    expect(apiClient.syncJobs).toHaveBeenCalledTimes(1);
    expect(apiClient.getJobs).toHaveBeenCalledTimes(1);
  });

  it('records error when fetch fails', async () => {
    const error = new ApiClientError('Server offline', 500, 'SERVER_ERROR');
    vi.mocked(apiClient.getJobs).mockRejectedValueOnce(error);

    await useJobStore.getState().fetchJobs();

    const state = useJobStore.getState();
    expect(state.loading).toBe(false);
    expect(state.error).toBe('Server offline');

    useJobStore.getState().resetError();
    expect(useJobStore.getState().error).toBeNull();
  });
});
