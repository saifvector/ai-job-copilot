import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useDashboardStore } from '../store/dashboard-store';
import { apiClient, ApiClientError } from '../services/api-client';
import type { DashboardOverview, ProfileHealthData, CareerReadinessData } from '../types/analytics';

vi.mock('../services/api-client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../services/api-client')>();
  return {
    ...actual,
    apiClient: {
      ...actual.apiClient,
      getDashboard: vi.fn(),
      getProfileHealth: vi.fn(),
      getCareerReadiness: vi.fn(),
      getSkillGapAnalysis: vi.fn(),
      getAnalytics: vi.fn(),
      createAnalyticsSnapshot: vi.fn(),
    },
  };
});

const mockDashboardData: DashboardOverview = {
  totalJobs: 150,
  jobsMatched: 45,
  averageMatchScore: 82.4,
  excellentMatches: 12,
  strongMatches: 18,
  moderateMatches: 10,
  weakMatches: 5,
  trends: {
    matchScoreDelta: 3.2,
    jobsMatchedDelta: 8,
    profileScoreDelta: 5.0,
    readinessDelta: 4.2,
  },
  topMatches: [
    {
      jobId: 'j-1',
      jobTitle: 'Senior Full Stack Engineer',
      company: 'TechCorp',
      matchScore: 94.5,
      location: 'Remote',
      source: 'RemoteOK',
      postedDate: '2026-09-27T10:00:00Z',
      applyUrl: 'https://example.com/apply/1',
      missingSkills: ['AWS'],
    },
  ],
  profileScore: 88.0,
  readinessScore: 85.5,
  latencyMs: 14.2,
  generatedAt: '2026-09-27T12:00:00Z',
};

const mockProfileHealth: ProfileHealthData = {
  overallScore: 88.0,
  breakdown: {
    resumeCompleteness: 100.0,
    skillCoverage: 85.0,
    experienceCoverage: 85.0,
    educationCoverage: 80.0,
  },
  strengths: ['Resume document uploaded', 'Strong skill repository'],
  actionableRecommendations: ['Add cloud certification'],
  lastUpdated: '2026-09-27T12:00:00Z',
};

const mockReadiness: CareerReadinessData = {
  careerReadinessScore: 85.5,
  tier: 'Market Leader',
  factors: {
    resumeQuality: 90.0,
    skillsAlignment: 88.0,
    experienceDepth: 85.0,
    marketMatchRate: 80.0,
  },
  explanation: 'High competitive readiness.',
  keyCompetencies: ['Python', 'FastAPI', 'React'],
  growthPriorities: ['Deepen Kubernetes mastery'],
  generatedAt: '2026-09-27T12:00:00Z',
};

describe('useDashboardStore', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useDashboardStore.setState({
      metrics: null,
      insights: [],
      profileHealth: null,
      careerReadiness: null,
      savedJobIds: [],
      loading: false,
      error: null,
    });
  });

  it('initializes with default empty state', () => {
    const state = useDashboardStore.getState();
    expect(state.metrics).toBeNull();
    expect(state.insights).toEqual([]);
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
  });

  it('fetches dashboard metrics successfully', async () => {
    vi.mocked(apiClient.getDashboard).mockResolvedValueOnce({
      success: true,
      data: mockDashboardData,
      timestamp: '2026-09-27T12:00:00Z',
    });

    await useDashboardStore.getState().fetchDashboard();

    const state = useDashboardStore.getState();
    expect(state.loading).toBe(false);
    expect(state.metrics?.totalJobs).toBe(150);
    expect(state.insights).toHaveLength(1);
    expect(state.insights[0].company).toBe('TechCorp');
    expect(state.error).toBeNull();
  });

  it('handles dashboard fetch error', async () => {
    vi.mocked(apiClient.getDashboard).mockRejectedValueOnce(
      new ApiClientError('Network disconnected', 503, 'SERVICE_UNAVAILABLE')
    );

    await useDashboardStore.getState().fetchDashboard();

    const state = useDashboardStore.getState();
    expect(state.loading).toBe(false);
    expect(state.error).toBe('Network disconnected');
    expect(state.metrics).toBeNull();
  });

  it('toggles saved jobs correctly', () => {
    const store = useDashboardStore.getState();
    expect(store.isJobSaved('j-1')).toBe(false);

    store.toggleSaveJob('j-1');
    expect(useDashboardStore.getState().isJobSaved('j-1')).toBe(true);

    useDashboardStore.getState().toggleSaveJob('j-1');
    expect(useDashboardStore.getState().isJobSaved('j-1')).toBe(false);
  });

  it('fetches profile health successfully', async () => {
    vi.mocked(apiClient.getProfileHealth).mockResolvedValueOnce({
      success: true,
      data: mockProfileHealth,
      timestamp: '2026-09-27T12:00:00Z',
    });

    await useDashboardStore.getState().fetchProfileHealth();

    const state = useDashboardStore.getState();
    expect(state.profileHealth?.overallScore).toBe(88.0);
    expect(state.profileHealth?.breakdown.resumeCompleteness).toBe(100.0);
  });

  it('fetches career readiness successfully', async () => {
    vi.mocked(apiClient.getCareerReadiness).mockResolvedValueOnce({
      success: true,
      data: mockReadiness,
      timestamp: '2026-09-27T12:00:00Z',
    });

    await useDashboardStore.getState().fetchCareerReadiness();

    const state = useDashboardStore.getState();
    expect(state.careerReadiness?.careerReadinessScore).toBe(85.5);
    expect(state.careerReadiness?.tier).toBe('Market Leader');
  });
});
