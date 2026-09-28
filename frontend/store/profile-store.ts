import { create } from 'zustand';
import {
  Skill,
  Project,
  Education,
  Experience,
  Certification,
  CandidateContact,
  ResumeParseResponse,
} from '@/types';
import { apiClient, ApiClientError } from '@/services/api-client';

export interface CandidateProfileState {
  // Required state keys per specification
  profile: {
    contact: CandidateContact;
    summary: string;
    userId: string;
  } | null;
  skills: Skill[];
  projects: Project[];
  education: Education[];
  experience: Experience[];
  certifications: Certification[];
  loading: boolean;
  error: string | null;

  // Metadata
  modelUsed: string | null;
  parsedAt: string | null;

  // Actions
  fetchProfile: () => Promise<void>;
  parseResume: (resumeId?: string) => Promise<boolean>;
  fetchSummary: () => Promise<void>;
  fetchSkills: (category?: string) => Promise<void>;
  fetchProjects: () => Promise<void>;
  resetError: () => void;
  clearProfile: () => void;
}

export const useProfileStore = create<CandidateProfileState>((set, get) => ({
  profile: null,
  skills: [],
  projects: [],
  education: [],
  experience: [],
  certifications: [],
  loading: false,
  error: null,
  modelUsed: null,
  parsedAt: null,

  fetchProfile: async () => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.getFullProfileIntelligence();
      const data: ResumeParseResponse = response.data;
      set({
        profile: {
          contact: data.candidate,
          summary: data.summary,
          userId: data.userId,
        },
        skills: data.skills || [],
        projects: data.projects || [],
        education: data.education || [],
        experience: data.experience || [],
        certifications: data.certifications || [],
        modelUsed: data.modelUsed,
        parsedAt: data.parsedAt,
        loading: false,
      });
    } catch (err: unknown) {
      if (err instanceof ApiClientError && err.status === 404) {
        set({ loading: false });
      } else {
        const errorMsg =
          err instanceof ApiClientError ? err.message : 'Failed to load profile intelligence';
        set({ error: errorMsg, loading: false });
      }
    }
  },

  parseResume: async (resumeId?: string) => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.parseResume(resumeId);
      const data: ResumeParseResponse = response.data;
      set({
        profile: {
          contact: data.candidate,
          summary: data.summary,
          userId: data.userId,
        },
        skills: data.skills || [],
        projects: data.projects || [],
        education: data.education || [],
        experience: data.experience || [],
        certifications: data.certifications || [],
        modelUsed: data.modelUsed,
        parsedAt: data.parsedAt,
        loading: false,
        error: null,
      });
      return true;
    } catch (err: unknown) {
      const errorMsg =
        err instanceof ApiClientError
          ? err.message
          : 'Failed to extract candidate intelligence from resume.';
      set({ error: errorMsg, loading: false });
      return false;
    }
  },

  fetchSummary: async () => {
    try {
      const response = await apiClient.getProfileSummary();
      const currentProfile = get().profile;
      if (currentProfile) {
        set({
          profile: {
            ...currentProfile,
            summary: response.data.summary,
          },
        });
      }
    } catch (err: unknown) {
      const errorMsg =
        err instanceof ApiClientError ? err.message : 'Failed to fetch summary';
      set({ error: errorMsg });
    }
  },

  fetchSkills: async (category?: string) => {
    try {
      const response = await apiClient.getProfileSkills(category);
      set({ skills: response.data || [] });
    } catch (err: unknown) {
      const errorMsg =
        err instanceof ApiClientError ? err.message : 'Failed to fetch skills';
      set({ error: errorMsg });
    }
  },

  fetchProjects: async () => {
    try {
      const response = await apiClient.getProfileProjects();
      set({ projects: response.data || [] });
    } catch (err: unknown) {
      const errorMsg =
        err instanceof ApiClientError ? err.message : 'Failed to fetch projects';
      set({ error: errorMsg });
    }
  },

  resetError: () => set({ error: null }),

  clearProfile: () =>
    set({
      profile: null,
      skills: [],
      projects: [],
      education: [],
      experience: [],
      certifications: [],
      loading: false,
      error: null,
      modelUsed: null,
      parsedAt: null,
    }),
}));

// Named alias matching specification
export const profileStore = useProfileStore;
