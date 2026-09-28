import { create } from 'zustand';
import {
  AnalyticsDashboardData,
  AnalyticsSnapshotItem,
  SkillGapAnalysisData,
} from '@/types';
import { apiClient, ApiClientError } from '@/services/api-client';

export interface AnalyticsStoreState {
  charts: AnalyticsDashboardData | null;
  skillGaps: SkillGapAnalysisData | null;
  snapshots: AnalyticsSnapshotItem[];
  loading: boolean;
  creatingSnapshot: boolean;
  error: string | null;

  // Actions
  fetchAnalytics: () => Promise<void>;
  fetchSkillGaps: () => Promise<void>;
  createSnapshot: () => Promise<boolean>;
  clearError: () => void;
}

export const useAnalyticsStore = create<AnalyticsStoreState>((set, get) => ({
  charts: null,
  skillGaps: null,
  snapshots: [],
  loading: false,
  creatingSnapshot: false,
  error: null,

  fetchAnalytics: async () => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.getAnalytics();
      if (response.success && response.data) {
        set({
          charts: response.data,
          snapshots: response.data.profileProgress || [],
          loading: false,
        });
      } else {
        set({ error: 'Failed to load analytics datasets', loading: false });
      }
    } catch (err) {
      const message =
        err instanceof ApiClientError ? err.message : 'An error occurred while loading analytics';
      set({ error: message, loading: false });
    }
  },

  fetchSkillGaps: async () => {
    try {
      const response = await apiClient.getSkillGapAnalysis();
      if (response.success && response.data) {
        set({ skillGaps: response.data });
      }
    } catch (err) {
      console.error('Failed to fetch skill gap analysis:', err);
    }
  },

  createSnapshot: async () => {
    set({ creatingSnapshot: true, error: null });
    try {
      const response = await apiClient.createAnalyticsSnapshot();
      if (response.success && response.data) {
        const currentSnapshots = get().snapshots;
        set({
          snapshots: [...currentSnapshots, response.data],
          creatingSnapshot: false,
        });
        // Refresh charts
        await get().fetchAnalytics();
        return true;
      }
      set({ creatingSnapshot: false });
      return false;
    } catch (err) {
      const message =
        err instanceof ApiClientError ? err.message : 'Failed to capture snapshot';
      set({ error: message, creatingSnapshot: false });
      return false;
    }
  },

  clearError: () => set({ error: null }),
}));
