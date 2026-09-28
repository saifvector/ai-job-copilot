import { create } from 'zustand';
import { MatchFilters, MatchPaginationData, MatchResult, MatchRunResult } from '@/types';
import { apiClient, ApiClientError } from '@/services/api-client';

export interface MatchingStoreState {
  // Required core state keys per specification
  results: MatchResult[];
  topMatches: MatchResult[];
  loading: boolean;
  error: string | null;

  // Active item & detailed inspection
  selectedResult: MatchResult | null;
  filters: MatchFilters;
  runningMatch: boolean;
  enrichingJobId: string | null;
  lastRunResult: MatchRunResult | null;

  // Pagination metadata
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;

  // Actions
  fetchResults: (pageOverride?: number) => Promise<void>;
  fetchTopMatches: (limit?: number) => Promise<void>;
  runMatching: (params?: { jobIds?: string[]; limit?: number }) => Promise<boolean>;
  enrichJobMatch: (jobId: string) => Promise<void>;
  setFilters: (newFilters: Partial<MatchFilters>) => void;
  resetFilters: () => void;
  selectResult: (result: MatchResult | null) => void;
  setPage: (page: number) => Promise<void>;
  clearError: () => void;
}

const defaultFilters: MatchFilters = {
  minScore: null,
  location: '',
  company: '',
  role: '',
  page: 1,
  pageSize: 20,
};

export const useMatchingStore = create<MatchingStoreState>((set, get) => ({
  results: [],
  topMatches: [],
  loading: false,
  error: null,
  selectedResult: null,
  filters: { ...defaultFilters },
  runningMatch: false,
  enrichingJobId: null,
  lastRunResult: null,
  total: 0,
  page: 1,
  pageSize: 20,
  totalPages: 0,

  fetchResults: async (pageOverride?: number) => {
    set({ loading: true, error: null });
    const { filters, page } = get();
    const targetPage = pageOverride || page || 1;

    try {
      const response = await apiClient.getMatchResults({
        ...filters,
        page: targetPage,
      });

      const data = response.data;
      set({
        results: data.items,
        total: data.pagination.totalItems,
        page: data.pagination.page,
        pageSize: data.pagination.pageSize,
        totalPages: data.pagination.totalPages,
        loading: false,
      });
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to retrieve match results.';
      set({ error: message, loading: false });
    }
  },

  fetchTopMatches: async (limit: number = 10) => {
    try {
      const response = await apiClient.getTopMatches(limit);
      set({ topMatches: response.data });
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to retrieve top recommendations.';
      set({ error: message });
    }
  },

  runMatching: async (params) => {
    set({ runningMatch: true, error: null });
    try {
      const response = await apiClient.runMatching(params);
      set({ lastRunResult: response.data, runningMatch: false });

      // Refresh both list and top matches
      await Promise.all([
        get().fetchResults(1),
        get().fetchTopMatches(10),
      ]);
      return true;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to execute job matching.';
      set({ error: message, runningMatch: false });
      return false;
    }
  },

  enrichJobMatch: async (jobId: string) => {
    set({ enrichingJobId: jobId, error: null });
    try {
      const response = await apiClient.getMatchResultByJob(jobId, true);
      const updated = response.data;

      // Update in results list
      set((state) => ({
        results: state.results.map((r) => (r.jobId === jobId ? updated : r)),
        topMatches: state.topMatches.map((r) => (r.jobId === jobId ? updated : r)),
        selectedResult: state.selectedResult?.jobId === jobId ? updated : state.selectedResult,
        enrichingJobId: null,
      }));
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to enrich job recommendations.';
      set({ error: message, enrichingJobId: null });
    }
  },

  setFilters: (newFilters) => {
    set((state) => ({
      filters: {
        ...state.filters,
        ...newFilters,
        page: 1, // Reset to page 1 on filter modification
      },
    }));
    get().fetchResults(1);
  },

  resetFilters: () => {
    set({
      filters: { ...defaultFilters },
      page: 1,
    });
    get().fetchResults(1);
  },

  selectResult: (result) => {
    set({ selectedResult: result });
  },

  setPage: async (newPage: number) => {
    set({ page: newPage });
    await get().fetchResults(newPage);
  },

  clearError: () => {
    set({ error: null });
  },
}));

// Named export matching specification
export const matchingStore = useMatchingStore;
