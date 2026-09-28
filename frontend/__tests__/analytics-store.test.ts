import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useAnalyticsStore } from '../store/analytics-store';
import { apiClient, ApiClientError } from '../services/api-client';
import type { AnalyticsDashboardData, SkillGapAnalysisData, AnalyticsSnapshotItem } from '../types/analytics';

vi.mock('../services/api-client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../services/api-client')>();
  return {
    ...actual,
    apiClient: {
      ...actual.apiClient,
      getAnalytics: vi.fn(),
      getSkillGapAnalysis: vi.fn(),
      createAnalyticsSnapshot: vi.fn(),
    },
  };
});

const mockChartsData: AnalyticsDashboardData = {
  matchDistribution: {
    excellent: 10,
    strong: 20,
    moderate: 8,
    weak: 2,
    total: 40,
    items: [
      { name: 'Excellent', value: 10, color: '#10b981', percentage: 25.0 },
      { name: 'Strong', value: 20, color: '#3b82f6', percentage: 50.0 },
      { name: 'Moderate', value: 8, color: '#f59e0b', percentage: 20.0 },
      { name: 'Weak', value: 2, color: '#ef4444', percentage: 5.0 },
    ],
  },
  topSkills: [{ name: 'Python', demand: 35, valueScore: 87.5 }],
  missingSkills: [{ name: 'AWS', frequency: 15, importance: 'High' }],
  locationDistribution: [
    { type: 'Remote', count: 28, percentage: 70.0 },
    { type: 'Hybrid', count: 8, percentage: 20.0 },
    { type: 'Onsite', count: 4, percentage: 10.0 },
  ],
  profileProgress: [
    {
      id: 'snap-1',
      timestamp: '2026-09-27T10:00:00Z',
      profileScore: 85.0,
      readinessScore: 82.0,
      averageMatchScore: 78.5,
      excellentMatches: 8,
      strongMatches: 15,
      moderateMatches: 10,
      weakMatches: 4,
    },
  ],
  latencyMs: 12.5,
  generatedAt: '2026-09-27T12:00:00Z',
};

const mockSkillGaps: SkillGapAnalysisData = {
  totalAnalyzedJobs: 40,
  candidateSkillsCount: 12,
  mostRequestedSkills: [{ name: 'Python', count: 35, percentage: 87.5, inCandidateProfile: true }],
  missingSkills: [{ name: 'AWS', count: 15, percentage: 37.5, inCandidateProfile: false, priority: 'High' }],
  emergingSkills: [{ name: 'Kubernetes', count: 12, percentage: 30.0, inCandidateProfile: false, category: 'High-Growth' }],
  recommendations: ['Learn AWS services to increase match yield'],
};

describe('useAnalyticsStore', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useAnalyticsStore.setState({
      charts: null,
      skillGaps: null,
      snapshots: [],
      loading: false,
      creatingSnapshot: false,
      error: null,
    });
  });

  it('initializes with default empty state', () => {
    const state = useAnalyticsStore.getState();
    expect(state.charts).toBeNull();
    expect(state.skillGaps).toBeNull();
    expect(state.snapshots).toEqual([]);
    expect(state.loading).toBe(false);
  });

  it('fetches analytics datasets successfully', async () => {
    vi.mocked(apiClient.getAnalytics).mockResolvedValueOnce({
      success: true,
      data: mockChartsData,
      timestamp: '2026-09-27T12:00:00Z',
    });

    await useAnalyticsStore.getState().fetchAnalytics();

    const state = useAnalyticsStore.getState();
    expect(state.loading).toBe(false);
    expect(state.charts?.matchDistribution.total).toBe(40);
    expect(state.snapshots).toHaveLength(1);
    expect(state.charts?.topSkills[0].name).toBe('Python');
  });

  it('fetches skill gap analysis successfully', async () => {
    vi.mocked(apiClient.getSkillGapAnalysis).mockResolvedValueOnce({
      success: true,
      data: mockSkillGaps,
      timestamp: '2026-09-27T12:00:00Z',
    });

    await useAnalyticsStore.getState().fetchSkillGaps();

    const state = useAnalyticsStore.getState();
    expect(state.skillGaps?.totalAnalyzedJobs).toBe(40);
    expect(state.skillGaps?.missingSkills[0].name).toBe('AWS');
  });

  it('creates an analytics snapshot and refreshes charts', async () => {
    const newSnapshot: AnalyticsSnapshotItem = {
      id: 'snap-2',
      timestamp: '2026-09-27T12:30:00Z',
      profileScore: 90.0,
      readinessScore: 88.0,
      averageMatchScore: 84.0,
      excellentMatches: 14,
      strongMatches: 18,
      moderateMatches: 6,
      weakMatches: 2,
    };

    vi.mocked(apiClient.createAnalyticsSnapshot).mockResolvedValueOnce({
      success: true,
      data: newSnapshot,
      timestamp: '2026-09-27T12:30:00Z',
    });
    vi.mocked(apiClient.getAnalytics).mockResolvedValueOnce({
      success: true,
      data: {
        ...mockChartsData,
        profileProgress: [mockChartsData.profileProgress[0], newSnapshot],
      },
      timestamp: '2026-09-27T12:30:00Z',
    });

    const success = await useAnalyticsStore.getState().createSnapshot();
    expect(success).toBe(true);

    const state = useAnalyticsStore.getState();
    expect(state.creatingSnapshot).toBe(false);
    expect(state.snapshots).toHaveLength(2);
  });
});
