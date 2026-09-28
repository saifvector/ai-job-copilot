import { create } from 'zustand';
import {
  CareerReadinessData,
  DashboardOverview,
  MatchInsightItem,
  ProfileHealthData,
} from '@/types';
import { apiClient, ApiClientError } from '@/services/api-client';

export interface DashboardStoreState {
  metrics: DashboardOverview | null;
  insights: MatchInsightItem[];
  profileHealth: ProfileHealthData | null;
  careerReadiness: CareerReadinessData | null;
  savedJobIds: string[];
  loading: boolean;
  error: string | null;

  // Actions
  fetchDashboard: () => Promise<void>;
  fetchProfileHealth: () => Promise<void>;
  fetchCareerReadiness: () => Promise<void>;
  toggleSaveJob: (jobId: string) => void;
  isJobSaved: (jobId: string) => boolean;
  clearError: () => void;
}

export const useDashboardStore = create<DashboardStoreState>((set, get) => ({
  metrics: null,
  insights: [],
  profileHealth: null,
  careerReadiness: null,
  savedJobIds: [],
  loading: false,
  error: null,

  fetchDashboard: async () => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.getDashboard();
      if (response.success && response.data) {
        set({
          metrics: response.data,
          insights: response.data.topMatches || [],
          loading: false,
        });
      } else {
        set({ error: 'Failed to load dashboard metrics', loading: false });
      }
    } catch (err) {
      const message =
        err instanceof ApiClientError ? err.message : 'An error occurred while loading dashboard metrics';
      set({ error: message, loading: false });
    }
  },

  fetchProfileHealth: async () => {
    try {
      const response = await apiClient.getProfileHealth();
      if (response.success && response.data) {
        set({ profileHealth: response.data });
      }
    } catch (err) {
      console.error('Failed to fetch profile health:', err);
    }
  },

  fetchCareerReadiness: async () => {
    try {
      const response = await apiClient.getCareerReadiness();
      if (response.success && response.data) {
        set({ careerReadiness: response.data });
      }
    } catch (err) {
      console.error('Failed to fetch career readiness:', err);
    }
  },

  toggleSaveJob: (jobId: string) => {
    const { savedJobIds } = get();
    const isSaved = savedJobIds.includes(jobId);
    const updated = isSaved
      ? savedJobIds.filter((id) => id !== jobId)
      : [...savedJobIds, jobId];
    set({ savedJobIds: updated });
  },

  isJobSaved: (jobId: string) => {
    return get().savedJobIds.includes(jobId);
  },

  clearError: () => set({ error: null }),
}));
