import { create } from 'zustand';
import { Job, JobFilters, JobSyncData } from '@/types';
import { apiClient, ApiClientError } from '@/services/api-client';

export interface JobStoreState {
  // Required state keys per specification
  jobs: Job[];
  selectedJob: Job | null;
  filters: JobFilters;
  loading: boolean;
  error: string | null;

  // Pagination & sync metadata
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  syncing: boolean;
  syncResult: JobSyncData | null;

  // Actions
  fetchJobs: () => Promise<void>;
  searchJobs: (filterOverrides?: Partial<JobFilters>) => Promise<void>;
  setFilters: (newFilters: Partial<JobFilters>) => void;
  resetFilters: () => void;
  selectJob: (job: Job | null) => void;
  fetchJobDetails: (id: string) => Promise<void>;
  syncJobs: (source?: string) => Promise<boolean>;
  setPage: (page: number) => Promise<void>;
  resetError: () => void;
}

const defaultFilters: JobFilters = {
  query: '',
  role: '',
  location: '',
  source: '',
  skill: '',
  minSalary: undefined,
  sortBy: 'newest',
  page: 1,
  pageSize: 20,
};

export const useJobStore = create<JobStoreState>((set, get) => ({
  jobs: [],
  selectedJob: null,
  filters: { ...defaultFilters },
  loading: false,
  error: null,
  total: 0,
  page: 1,
  pageSize: 20,
  totalPages: 0,
  syncing: false,
  syncResult: null,

  fetchJobs: async () => {
    set({ loading: true, error: null });
    try {
      const { filters } = get();
      const response = await apiClient.getJobs(filters);
      const data = response.data;
      set({
        jobs: data.items || [],
        total: data.total || 0,
        page: data.page || 1,
        pageSize: data.pageSize || 20,
        totalPages: data.totalPages || 0,
        loading: false,
      });
    } catch (err: unknown) {
      const msg = err instanceof ApiClientError ? err.message : 'Failed to retrieve jobs';
      set({ error: msg, loading: false });
    }
  },

  searchJobs: async (filterOverrides?: Partial<JobFilters>) => {
    set({ loading: true, error: null });
    try {
      const updatedFilters: JobFilters = {
        ...get().filters,
        ...filterOverrides,
        // Reset page to 1 on new search unless page explicitly provided
        page: filterOverrides?.page !== undefined ? filterOverrides.page : 1,
      };
      set({ filters: updatedFilters });

      const response = await apiClient.searchJobs(updatedFilters);
      const data = response.data;
      set({
        jobs: data.items || [],
        total: data.total || 0,
        page: data.page || 1,
        pageSize: data.pageSize || 20,
        totalPages: data.totalPages || 0,
        loading: false,
      });
    } catch (err: unknown) {
      const msg = err instanceof ApiClientError ? err.message : 'Search failed';
      set({ error: msg, loading: false });
    }
  },

  setFilters: (newFilters: Partial<JobFilters>) => {
    set((state) => ({
      filters: { ...state.filters, ...newFilters },
    }));
  },

  resetFilters: () => {
    set({ filters: { ...defaultFilters } });
    get().fetchJobs();
  },

  selectJob: (job: Job | null) => {
    set({ selectedJob: job });
  },

  fetchJobDetails: async (id: string) => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.getJobById(id);
      set({ selectedJob: response.data, loading: false });
    } catch (err: unknown) {
      const msg = err instanceof ApiClientError ? err.message : 'Failed to fetch job details';
      set({ error: msg, loading: false });
    }
  },

  syncJobs: async (source?: string) => {
    set({ syncing: true, error: null });
    try {
      const response = await apiClient.syncJobs(source);
      set({
        syncing: false,
        syncResult: response.data,
      });
      // Refresh list after sync
      await get().fetchJobs();
      return true;
    } catch (err: unknown) {
      const msg = err instanceof ApiClientError ? err.message : 'Job sync failed';
      set({ error: msg, syncing: false });
      return false;
    }
  },

  setPage: async (page: number) => {
    await get().searchJobs({ page });
  },

  resetError: () => {
    set({ error: null });
  },
}));
