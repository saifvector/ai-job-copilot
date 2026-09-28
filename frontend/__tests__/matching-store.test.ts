import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useMatchingStore } from '../store/matching-store';
import { apiClient, ApiClientError } from '../services/api-client';
import type { MatchResult, MatchResultsData, MatchRunResult } from '../types/matching';

vi.mock('../services/api-client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../services/api-client')>();
  return {
    ...actual,
    apiClient: {
      ...actual.apiClient,
      getMatchResults: vi.fn(),
      getTopMatches: vi.fn(),
      runMatching: vi.fn(),
      getMatchResultByJob: vi.fn(),
    },
  };
});

const mockMatchResult: MatchResult = {
  id: 'm-00000000-0000-0000-0000-000000000001',
  userId: 'u-00000000-0000-0000-0000-000000000001',
  jobId: 'j-00000000-0000-0000-0000-000000000001',
  overallScore: 92.5,
  skillScore: 95.0,
  experienceScore: 90.0,
  educationScore: 90.0,
  locationScore: 100.0,
  roleScore: 88.0,
  strengths: ['Strong Python background', 'Relevant FastAPI experience'],
  missingSkills: ['Kubernetes'],
  recommendations: ['Practice Kubernetes orchestration and Helm deployment charts'],
  generatedAt: '2026-09-27T12:00:00Z',
  updatedAt: '2026-09-27T12:00:00Z',
  job: {
    id: 'j-00000000-0000-0000-0000-000000000001',
    title: 'Senior AI Backend Engineer',
    company: 'Anthropic Partner',
    location: 'Remote',
    employmentType: 'Full-time',
    salaryMin: 160000,
    salaryMax: 200000,
    currency: 'USD',
    source: 'RemoteOK',
    applyUrl: 'https://example.com/apply/1',
  },
};

const mockResultsData: MatchResultsData = {
  items: [mockMatchResult],
  pagination: {
    page: 1,
    pageSize: 20,
    totalItems: 1,
    totalPages: 1,
    hasNext: false,
    hasPrev: false,
  },
};

const mockRunResult: MatchRunResult = {
  totalEvaluated: 120,
  matchesSaved: 120,
  topScore: 92.5,
  durationMs: 45.2,
};

describe('useMatchingStore', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useMatchingStore.setState({
      results: [],
      topMatches: [],
      selectedResult: null,
      loading: false,
      runningMatch: false,
      error: null,
      total: 0,
      page: 1,
      pageSize: 20,
      totalPages: 0,
      lastRunResult: null,
      filters: {
        minScore: null,
        location: '',
        company: '',
        role: '',
        page: 1,
        pageSize: 20,
      },
    });
  });

  it('initializes with default empty state', () => {
    const state = useMatchingStore.getState();
    expect(state.results).toEqual([]);
    expect(state.topMatches).toEqual([]);
    expect(state.loading).toBe(false);
    expect(state.runningMatch).toBe(false);
    expect(state.error).toBeNull();
  });

  it('fetchResults retrieves match results and updates pagination', async () => {
    vi.mocked(apiClient.getMatchResults).mockResolvedValueOnce({
      success: true,
      data: mockResultsData,
      timestamp: new Date().toISOString(),
    });

    await useMatchingStore.getState().fetchResults(1);

    const state = useMatchingStore.getState();
    expect(state.loading).toBe(false);
    expect(state.results).toHaveLength(1);
    expect(state.results[0].overallScore).toBe(92.5);
    expect(state.total).toBe(1);
  });

  it('fetchResults handles API errors gracefully', async () => {
    vi.mocked(apiClient.getMatchResults).mockRejectedValueOnce(
      new ApiClientError('Server Error', 500)
    );

    await useMatchingStore.getState().fetchResults(1);

    const state = useMatchingStore.getState();
    expect(state.loading).toBe(false);
    expect(state.error).toBe('Server Error');
  });

  it('fetchTopMatches populates topMatches state', async () => {
    vi.mocked(apiClient.getTopMatches).mockResolvedValueOnce({
      success: true,
      data: [mockMatchResult],
      timestamp: new Date().toISOString(),
    });

    await useMatchingStore.getState().fetchTopMatches(5);

    const state = useMatchingStore.getState();
    expect(state.topMatches).toHaveLength(1);
    expect(state.topMatches[0].jobId).toBe(mockMatchResult.jobId);
  });

  it('runMatching executes bulk scoring and stores execution telemetry', async () => {
    vi.mocked(apiClient.runMatching).mockResolvedValueOnce({
      success: true,
      data: mockRunResult,
      timestamp: new Date().toISOString(),
    });
    vi.mocked(apiClient.getMatchResults).mockResolvedValueOnce({
      success: true,
      data: mockResultsData,
      timestamp: new Date().toISOString(),
    });
    vi.mocked(apiClient.getTopMatches).mockResolvedValueOnce({
      success: true,
      data: [mockMatchResult],
      timestamp: new Date().toISOString(),
    });

    const success = await useMatchingStore.getState().runMatching({ limit: 500 });

    expect(success).toBe(true);
    const state = useMatchingStore.getState();
    expect(state.lastRunResult).toEqual(mockRunResult);
    expect(state.runningMatch).toBe(false);
  });

  it('setFilters updates criteria and triggers refresh', () => {
    vi.mocked(apiClient.getMatchResults).mockResolvedValueOnce({
      success: true,
      data: mockResultsData,
      timestamp: new Date().toISOString(),
    });

    useMatchingStore.getState().setFilters({ minScore: 80, role: 'AI Engineer' });

    const state = useMatchingStore.getState();
    expect(state.filters.minScore).toBe(80);
    expect(state.filters.role).toBe('AI Engineer');
    expect(state.filters.page).toBe(1);
  });

  it('selectResult sets the active inspect modal target', () => {
    useMatchingStore.getState().selectResult(mockMatchResult);
    expect(useMatchingStore.getState().selectedResult).toEqual(mockMatchResult);

    useMatchingStore.getState().selectResult(null);
    expect(useMatchingStore.getState().selectedResult).toBeNull();
  });
});
