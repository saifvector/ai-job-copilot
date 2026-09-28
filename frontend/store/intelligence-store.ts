import { create } from 'zustand';
import {
  CareerIntelligenceOverview,
  CohortPoint,
  CompanyResponseMetric,
  OutcomeAnalyticsSummary,
  OutcomeEvent,
  RecommendationItem,
  RecordOutcomePayload,
  ResumePerformance,
  SkillImpact,
  TrendPoint,
} from '@/types';
import { apiClient, ApiClientError } from '@/services/api-client';

export interface IntelligenceStoreState {
  overview: CareerIntelligenceOverview | null;
  analytics: OutcomeAnalyticsSummary | null;
  outcomes: OutcomeEvent[];
  totalOutcomes: number;
  resumes: ResumePerformance[];
  skills: SkillImpact[];
  companies: CompanyResponseMetric[];
  recommendations: RecommendationItem[];
  trends: TrendPoint[];
  cohorts: CohortPoint[];
  loading: boolean;
  recordingOutcome: boolean;
  error: string | null;

  // Actions
  fetchOverview: () => Promise<void>;
  fetchOutcomes: (type?: string, limit?: number, offset?: number) => Promise<void>;
  recordOutcome: (payload: RecordOutcomePayload) => Promise<OutcomeEvent | null>;
  fetchSkills: () => Promise<void>;
  fetchResumes: () => Promise<void>;
  fetchCompanies: () => Promise<void>;
  fetchTrends: (days?: number) => Promise<void>;
  createSnapshot: () => Promise<boolean>;
  clearError: () => void;
}

export const useIntelligenceStore = create<IntelligenceStoreState>((set, get) => ({
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

  fetchOverview: async () => {
    set({ loading: true, error: null });
    try {
      const data = await apiClient.getCareerIntelligenceOverview();
      set({
        overview: data,
        analytics: data.analytics,
        resumes: data.topResumes,
        skills: data.topSkills,
        companies: data.topCompanies,
        recommendations: data.recommendations,
        trends: data.trends,
        loading: false,
      });
    } catch (err) {
      const msg = err instanceof ApiClientError ? err.message : 'Failed to load career intelligence overview';
      set({ error: msg, loading: false });
    }
  },

  fetchOutcomes: async (type?: string, limit: number = 50, offset: number = 0) => {
    set({ loading: true, error: null });
    try {
      const data = await apiClient.listOutcomeEvents({ outcome_type: type, limit, offset });
      set({
        outcomes: data.items,
        totalOutcomes: data.total,
        loading: false,
      });
    } catch (err) {
      const msg = err instanceof ApiClientError ? err.message : 'Failed to load outcome events';
      set({ error: msg, loading: false });
    }
  },

  recordOutcome: async (payload: RecordOutcomePayload) => {
    set({ recordingOutcome: true, error: null });
    try {
      const event = await apiClient.recordOutcomeEvent(payload);
      // Prepend to current outcomes list
      set((state) => ({
        outcomes: [event, ...state.outcomes],
        totalOutcomes: state.totalOutcomes + 1,
        recordingOutcome: false,
      }));
      // Silently refresh overview in background
      get().fetchOverview();
      return event;
    } catch (err) {
      const msg = err instanceof ApiClientError ? err.message : 'Failed to record application outcome';
      set({ error: msg, recordingOutcome: false });
      return null;
    }
  },

  fetchSkills: async () => {
    try {
      const data = await apiClient.listSkillImpacts();
      set({ skills: data.items });
    } catch (err) {
      const msg = err instanceof ApiClientError ? err.message : 'Failed to fetch skill impact metrics';
      set({ error: msg });
    }
  },

  fetchResumes: async () => {
    try {
      const data = await apiClient.listResumePerformances();
      set({ resumes: data.items });
    } catch (err) {
      const msg = err instanceof ApiClientError ? err.message : 'Failed to fetch resume performance metrics';
      set({ error: msg });
    }
  },

  fetchCompanies: async () => {
    try {
      const data = await apiClient.getCompanyResponseAnalytics();
      set({ companies: data.companies });
    } catch (err) {
      const msg = err instanceof ApiClientError ? err.message : 'Failed to fetch company response analytics';
      set({ error: msg });
    }
  },

  fetchTrends: async (days: number = 90) => {
    try {
      const data = await apiClient.getCareerTrends(days);
      set({
        trends: data.trends,
        cohorts: data.cohorts,
      });
    } catch (err) {
      const msg = err instanceof ApiClientError ? err.message : 'Failed to fetch career trends';
      set({ error: msg });
    }
  },

  createSnapshot: async () => {
    set({ loading: true, error: null });
    try {
      await apiClient.createCareerSnapshot();
      set({ loading: false });
      return true;
    } catch (err) {
      const msg = err instanceof ApiClientError ? err.message : 'Failed to create warehouse snapshot';
      set({ error: msg, loading: false });
      return false;
    }
  },

  clearError: () => set({ error: null }),
}));
