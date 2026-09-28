import { create } from 'zustand';
import { Resume } from '@/types';
import { apiClient, ApiClientError } from '@/services/api-client';

interface ResumeState {
  resume: Resume | null;
  loading: boolean;
  uploadProgress: number;
  error: string | null;

  // Actions
  fetchResume: () => Promise<void>;
  uploadResume: (file: File) => Promise<boolean>;
  deleteResume: () => Promise<boolean>;
  downloadResume: () => Promise<void>;
  setUploadProgress: (progress: number) => void;
  resetError: () => void;
  clearResume: () => void;
}

export const useResumeStore = create<ResumeState>((set, get) => ({
  resume: null,
  loading: false,
  uploadProgress: 0,
  error: null,

  fetchResume: async () => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.getResume();
      set({ resume: response.data, loading: false });
    } catch (err: unknown) {
      // If 404 not found, it simply means no resume is uploaded yet
      if (err instanceof ApiClientError && err.status === 404) {
        set({ resume: null, loading: false });
      } else {
        const errorMsg =
          err instanceof ApiClientError ? err.message : 'Failed to fetch resume metadata';
        set({ error: errorMsg, loading: false });
      }
    }
  },

  uploadResume: async (file: File) => {
    set({ loading: true, uploadProgress: 0, error: null });
    try {
      const response = await apiClient.uploadResume(file, (percent) => {
        set({ uploadProgress: percent });
      });
      set({
        resume: response.data,
        loading: false,
        uploadProgress: 100,
        error: null,
      });
      return true;
    } catch (err: unknown) {
      const errorMsg =
        err instanceof ApiClientError
          ? err.message
          : (err as Error)?.message || 'Resume upload failed';
      set({ error: errorMsg, loading: false, uploadProgress: 0 });
      return false;
    }
  },

  deleteResume: async () => {
    set({ loading: true, error: null });
    try {
      await apiClient.deleteResume();
      set({ resume: null, loading: false, uploadProgress: 0 });
      return true;
    } catch (err: unknown) {
      const errorMsg =
        err instanceof ApiClientError ? err.message : 'Failed to delete resume document';
      set({ error: errorMsg, loading: false });
      return false;
    }
  },

  downloadResume: async () => {
    try {
      const { blob, filename } = await apiClient.downloadResume();

      // Trigger native browser download
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err: unknown) {
      const errorMsg =
        err instanceof ApiClientError ? err.message : 'Failed to download resume document';
      set({ error: errorMsg });
    }
  },

  setUploadProgress: (uploadProgress: number) => set({ uploadProgress }),
  resetError: () => set({ error: null }),
  clearResume: () => set({ resume: null, uploadProgress: 0, error: null }),
}));
