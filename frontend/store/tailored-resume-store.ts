import { create } from 'zustand';
import {
  TailoredResume,
  TailoredResumeListItem,
  TailorResumePayload,
} from '@/types';
import { apiClient, ApiClientError } from '@/services/api-client';

export interface TailoredResumeStoreState {
  resumes: TailoredResumeListItem[];
  selectedResume: TailoredResume | null;
  selectedVersion: 'ats' | 'recruiter' | 'balanced';
  atsScore: number | null;
  keywordCoverage: number | null;
  loading: boolean;
  exporting: boolean;
  error: string | null;

  // Actions
  fetchResumes: () => Promise<void>;
  selectResumeById: (id: string) => Promise<void>;
  selectVersion: (version: 'ats' | 'recruiter' | 'balanced') => void;
  tailorResume: (payload: TailorResumePayload) => Promise<TailoredResume | null>;
  exportResume: (
    format: 'pdf' | 'docx' | 'markdown',
    version?: 'ats' | 'recruiter' | 'balanced'
  ) => Promise<{ filename: string } | null>;
  clearSelected: () => void;
  clearError: () => void;
}

export const useTailoredResumeStore = create<TailoredResumeStoreState>((set, get) => ({
  resumes: [],
  selectedResume: null,
  selectedVersion: 'balanced',
  atsScore: null,
  keywordCoverage: null,
  loading: false,
  exporting: false,
  error: null,

  fetchResumes: async () => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.getTailoredResumes();
      if (response.success && response.data) {
        set({ resumes: response.data, loading: false });
      } else {
        set({ error: 'Failed to fetch tailored resumes', loading: false });
      }
    } catch (err) {
      const message =
        err instanceof ApiClientError ? err.message : 'An error occurred while fetching tailored resumes';
      set({ error: message, loading: false });
    }
  },

  selectResumeById: async (id: string) => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.getTailoredResumeById(id);
      if (response.success && response.data) {
        const resume = response.data;
        set({
          selectedResume: resume,
          atsScore: resume.atsScore,
          keywordCoverage: resume.keywordCoverage,
          loading: false,
        });
      } else {
        set({ error: 'Failed to load tailored resume details', loading: false });
      }
    } catch (err) {
      const message =
        err instanceof ApiClientError ? err.message : 'An error occurred while loading tailored resume';
      set({ error: message, loading: false });
    }
  },

  selectVersion: (version: 'ats' | 'recruiter' | 'balanced') => {
    set({ selectedVersion: version });
  },

  tailorResume: async (payload: TailorResumePayload) => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.tailorResume(payload);
      if (response.success && response.data) {
        const resume = response.data;
        const currentResumes = get().resumes;
        const exists = currentResumes.some((r) => r.id === resume.id);

        const updatedList: TailoredResumeListItem[] = exists
          ? currentResumes.map((r) =>
              r.id === resume.id
                ? {
                    ...r,
                    atsScore: resume.atsScore,
                    keywordCoverage: resume.keywordCoverage,
                    updatedAt: resume.updatedAt,
                  }
                : r
            )
          : [
              {
                id: resume.id,
                userId: resume.userId,
                jobId: resume.jobId,
                jobTitle: resume.title,
                jobCompany: 'Target Employer',
                title: resume.title,
                atsScore: resume.atsScore,
                keywordCoverage: resume.keywordCoverage,
                createdAt: resume.createdAt,
                updatedAt: resume.updatedAt,
              },
              ...currentResumes,
            ];

        set({
          selectedResume: resume,
          resumes: updatedList,
          atsScore: resume.atsScore,
          keywordCoverage: resume.keywordCoverage,
          selectedVersion: payload.targetVersion || 'balanced',
          loading: false,
        });
        return resume;
      } else {
        set({ error: 'Failed to generate tailored resume', loading: false });
        return null;
      }
    } catch (err) {
      const message =
        err instanceof ApiClientError ? err.message : 'An error occurred while tailoring resume';
      set({ error: message, loading: false });
      return null;
    }
  },

  exportResume: async (
    format: 'pdf' | 'docx' | 'markdown',
    version?: 'ats' | 'recruiter' | 'balanced'
  ) => {
    const selected = get().selectedResume;
    if (!selected) {
      set({ error: 'No resume selected for export' });
      return null;
    }

    const targetVersion = version || get().selectedVersion;
    set({ exporting: true, error: null });

    try {
      const { blob, filename } = await apiClient.exportTailoredResume(
        selected.id,
        format,
        targetVersion
      );

      // Trigger standard browser download
      if (typeof window !== 'undefined') {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }

      set({ exporting: false });
      return { filename };
    } catch (err) {
      const message =
        err instanceof ApiClientError ? err.message : 'Failed to export tailored resume document';
      set({ error: message, exporting: false });
      return null;
    }
  },

  clearSelected: () => {
    set({
      selectedResume: null,
      atsScore: null,
      keywordCoverage: null,
      error: null,
    });
  },

  clearError: () => set({ error: null }),
}));
