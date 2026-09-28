import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useIntelligenceStore } from '../store/intelligence-store';
import { apiClient } from '../services/api-client';
import type {
  CareerIntelligenceOverview,
  OutcomeEvent,
  ResumePerformance,
  SkillImpact,
} from '../types/career-intelligence';

vi.mock('../services/api-client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../services/api-client')>();
  return {
    ...actual,
    apiClient: {
      ...actual.apiClient,
      getCareerIntelligenceOverview: vi.fn(),
      listOutcomeEvents: vi.fn(),
      recordOutcomeEvent: vi.fn(),
      getOutcomeAnalytics: vi.fn(),
      listSkillImpacts: vi.fn(),
      listResumePerformances: vi.fn(),
      getCompanyResponseAnalytics: vi.fn(),
      getApplicationStrategyAnalytics: vi.fn(),
      getCareerRecommendations: vi.fn(),
      getCareerTrends: vi.fn(),
      createCareerSnapshot: vi.fn(),
    },
  };
});

const mockOverview: CareerIntelligenceOverview = {
  analytics: {
    totalApplications: 12,
    totalOutcomes: 4,
    interviewsReceived: 3,
    assessmentsReceived: 1,
    offersReceived: 1,
    rejectionsReceived: 0,
    withdrawals: 0,
    interviewRate: 0.25,
    assessmentRate: 0.08,
    offerRate: 0.08,
    rejectionRate: 0.0,
    avgResponseDays: 4.5,
    medianResponseDays: 4.0,
    activeFunnel: { APPLIED: 8, INTERVIEW: 3, OFFER: 1 },
  },
  topResumes: [
    {
      id: 'res-perf-1',
      tailoredResumeId: 'tailored-1',
      resumeTitle: 'Staff AI Engineer Resume',
      targetRole: 'Staff AI Engineer',
      atsScore: 92.0,
      applicationsSent: 6,
      interviewsReceived: 2,
      offersReceived: 1,
      responseRate: 0.333,
      interviewConversionRate: 0.5,
      updatedAt: '2026-09-28T12:00:00Z',
    },
  ],
  topSkills: [
    {
      id: 'skill-imp-1',
      skillName: 'FastAPI',
      interviewsInfluenced: 3,
      offersInfluenced: 1,
      averageMatchScore: 91.5,
      correlationScore: 0.45,
      sampleSize: 6,
      recommendationWeight: 'CRITICAL',
      updatedAt: '2026-09-28T12:00:00Z',
    },
  ],
  topCompanies: [
    {
      company: 'Anthropic AI',
      applicationsSent: 2,
      responsesReceived: 1,
      interviewsCount: 1,
      offersCount: 1,
      responseRate: 0.5,
      interviewRate: 0.5,
      avgResponseDays: 3.5,
    },
  ],
  strategy: {
    sourceBreakdown: [{ source: 'Referral', sent: 3, interviews: 2, response_rate: 0.667 }],
    scoreTierBreakdown: [{ tier: '90%+', sent: 4, interviews: 2, rate: 0.5 }],
    weeklyCadence: [{ week: '2026-W38', count: 6 }],
    keyInsights: ['Referral channel yields highest interview rate at 66.7%'],
  },
  recommendations: [
    {
      id: 'rec-1',
      category: 'SKILL',
      title: 'Prioritize High-Conversion Competency: FastAPI',
      description: 'Applications with FastAPI yield 3 interviews.',
      evidence: 'Observed 3 interviews across 6 applications.',
      impactLevel: 'HIGH',
      actionSuggested: 'Highlight FastAPI in resume header',
      confidenceScore: 0.92,
    },
  ],
  trends: [
    {
      date: '2026-09-20',
      applications: 4,
      interviews: 1,
      offers: 0,
      responseRate: 0.25,
    },
  ],
};

const mockEvent: OutcomeEvent = {
  id: 'evt-1',
  userId: 'user-1',
  applicationId: 'app-1',
  outcomeType: 'InterviewReceived',
  occurredAt: '2026-09-28T12:00:00Z',
  notes: 'First round interview scheduled',
  createdAt: '2026-09-28T12:00:00Z',
  jobTitle: 'Staff AI Engineer',
  company: 'Anthropic AI',
};

describe('useIntelligenceStore', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useIntelligenceStore.setState({
      overview: null,
      analytics: null,
      outcomes: [],
      totalOutcomes: 0,
      resumes: [],
      skills: [],
      companies: [],
      recommendations: [],
      trends: [],
      cohorts: [],
      loading: false,
      recordingOutcome: false,
      error: null,
    });
  });

  it('fetchOverview successfully loads executive career intelligence', async () => {
    vi.mocked(apiClient.getCareerIntelligenceOverview).mockResolvedValue(mockOverview);

    await useIntelligenceStore.getState().fetchOverview();

    const state = useIntelligenceStore.getState();
    expect(state.loading).toBe(false);
    expect(state.overview).toEqual(mockOverview);
    expect(state.analytics?.totalApplications).toBe(12);
    expect(state.analytics?.interviewRate).toBe(0.25);
    expect(state.resumes.length).toBe(1);
    expect(state.skills[0].skillName).toBe('FastAPI');
    expect(state.recommendations.length).toBe(1);
  });

  it('fetchOutcomes loads milestone event history', async () => {
    vi.mocked(apiClient.listOutcomeEvents).mockResolvedValue({
      items: [mockEvent],
      total: 1,
    });

    await useIntelligenceStore.getState().fetchOutcomes();

    const state = useIntelligenceStore.getState();
    expect(state.outcomes).toHaveLength(1);
    expect(state.outcomes[0].outcomeType).toBe('InterviewReceived');
    expect(state.totalOutcomes).toBe(1);
  });

  it('recordOutcome stores event and prepends to outcomes list', async () => {
    vi.mocked(apiClient.recordOutcomeEvent).mockResolvedValue(mockEvent);
    vi.mocked(apiClient.getCareerIntelligenceOverview).mockResolvedValue(mockOverview);

    const res = await useIntelligenceStore.getState().recordOutcome({
      application_id: 'app-1',
      outcome_type: 'InterviewReceived',
      notes: 'First round interview scheduled',
    });

    expect(res).toEqual(mockEvent);
    const state = useIntelligenceStore.getState();
    expect(state.outcomes).toHaveLength(1);
    expect(state.outcomes[0].id).toBe('evt-1');
  });

  it('createSnapshot triggers data warehouse snapshot storage', async () => {
    vi.mocked(apiClient.createCareerSnapshot).mockResolvedValue({ id: 'snap-1' });

    const success = await useIntelligenceStore.getState().createSnapshot();
    expect(success).toBe(true);
    expect(apiClient.createCareerSnapshot).toHaveBeenCalledTimes(1);
  });
});
