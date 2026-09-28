import { create } from 'zustand';
import {
  ContactInteraction,
  CreateInteractionPayload,
  CreateRecruiterPayload,
  CreateReferralPayload,
  NetworkingAnalytics,
  Recruiter,
  Referral,
  UpdateRecruiterPayload,
  UpdateReferralPayload,
} from '@/types';
import { apiClient, ApiClientError } from '@/services/api-client';

export interface RecruiterStoreState {
  recruiters: Recruiter[];
  selectedRecruiter: Recruiter | null;
  referrals: Referral[];
  interactions: ContactInteraction[];
  analytics: NetworkingAnalytics | null;
  companies: string[];
  totalRecruiters: number;
  loading: boolean;
  analyticsLoading: boolean;
  error: string | null;

  // Actions
  fetchRecruiters: (params?: { company?: string; search?: string }) => Promise<void>;
  selectRecruiterById: (id: string) => Promise<Recruiter | null>;
  createRecruiter: (payload: CreateRecruiterPayload) => Promise<Recruiter | null>;
  updateRecruiter: (id: string, payload: UpdateRecruiterPayload) => Promise<Recruiter | null>;
  deleteRecruiter: (id: string) => Promise<boolean>;

  addInteraction: (recruiterId: string, payload: CreateInteractionPayload) => Promise<ContactInteraction | null>;
  fetchHistory: (recruiterId: string) => Promise<void>;

  addReferral: (recruiterId: string, payload: CreateReferralPayload) => Promise<Referral | null>;
  fetchReferrals: (params?: { status?: string; company?: string }) => Promise<void>;
  updateReferral: (id: string, payload: UpdateReferralPayload) => Promise<Referral | null>;
  deleteReferral: (id: string) => Promise<boolean>;

  fetchAnalytics: () => Promise<void>;
  clearSelected: () => void;
  clearError: () => void;
}

function normalizeRecruiter(raw: any): Recruiter {
  if (!raw) return raw;
  return {
    id: raw.id,
    userId: raw.user_id ?? raw.userId ?? '',
    name: raw.name ?? '',
    company: raw.company ?? '',
    title: raw.title ?? null,
    email: raw.email ?? null,
    linkedinUrl: raw.linkedin_url ?? raw.linkedinUrl ?? null,
    notes: raw.notes ?? null,
    interactionCount: raw.interaction_count ?? raw.interactionCount ?? 0,
    referralCount: raw.referral_count ?? raw.referralCount ?? 0,
    lastInteractionDate: raw.last_interaction_date ?? raw.lastInteractionDate ?? null,
    createdAt: raw.created_at ?? raw.createdAt ?? new Date().toISOString(),
    updatedAt: raw.updated_at ?? raw.updatedAt ?? new Date().toISOString(),
    interactions: (raw.interactions || []).map(normalizeInteraction),
    referrals: (raw.referrals || []).map(normalizeReferral),
  };
}

function normalizeInteraction(raw: any): ContactInteraction {
  if (!raw) return raw;
  return {
    id: raw.id,
    recruiterId: raw.recruiter_id ?? raw.recruiterId ?? '',
    interactionType: raw.interaction_type ?? raw.interactionType ?? 'Message',
    summary: raw.summary ?? '',
    interactionDate: raw.interaction_date ?? raw.interactionDate ?? new Date().toISOString(),
    createdAt: raw.created_at ?? raw.createdAt ?? new Date().toISOString(),
  };
}

function normalizeReferral(raw: any): Referral {
  if (!raw) return raw;
  return {
    id: raw.id,
    recruiterId: raw.recruiter_id ?? raw.recruiterId ?? '',
    company: raw.company ?? '',
    role: raw.role ?? '',
    status: raw.status ?? 'Requested',
    notes: raw.notes ?? null,
    createdAt: raw.created_at ?? raw.createdAt ?? new Date().toISOString(),
    updatedAt: raw.updated_at ?? raw.updatedAt ?? new Date().toISOString(),
    recruiterName: raw.recruiter_name ?? raw.recruiterName ?? null,
  };
}

function normalizeAnalytics(raw: any): NetworkingAnalytics {
  if (!raw) {
    return {
      recruitersContacted: 0,
      responseRate: 0.0,
      referralSuccessRate: 0.0,
      companiesReached: 0,
      messagesSent: 0,
      responsesReceived: 0,
      referralsRequested: 0,
      referralsReceived: 0,
      interactionsByType: {},
      referralsByStatus: {},
    };
  }
  return {
    recruitersContacted: raw.recruiters_contacted ?? raw.recruitersContacted ?? 0,
    responseRate: raw.response_rate ?? raw.responseRate ?? 0.0,
    referralSuccessRate: raw.referral_success_rate ?? raw.referralSuccessRate ?? 0.0,
    companiesReached: raw.companies_reached ?? raw.companiesReached ?? 0,
    messagesSent: raw.messages_sent ?? raw.messagesSent ?? 0,
    responsesReceived: raw.responses_received ?? raw.responsesReceived ?? 0,
    referralsRequested: raw.referrals_requested ?? raw.referralsRequested ?? 0,
    referralsReceived: raw.referrals_received ?? raw.referralsReceived ?? 0,
    interactionsByType: raw.interactions_by_type ?? raw.interactionsByType ?? {},
    referralsByStatus: raw.referrals_by_status ?? raw.referralsByStatus ?? {},
  };
}

export const useRecruiterStore = create<RecruiterStoreState>((set, get) => ({
  recruiters: [],
  selectedRecruiter: null,
  referrals: [],
  interactions: [],
  analytics: null,
  companies: [],
  totalRecruiters: 0,
  loading: false,
  analyticsLoading: false,
  error: null,

  fetchRecruiters: async (params) => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.getRecruiters(params);
      if (response.success && response.data) {
        const normalized = (response.data.recruiters || []).map(normalizeRecruiter);
        set({
          recruiters: normalized,
          totalRecruiters: response.data.total ?? normalized.length,
          companies: response.data.companies ?? [],
          loading: false,
        });
      } else {
        set({ error: 'Failed to retrieve recruiters', loading: false });
      }
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Error loading recruiters';
      set({ error: message, loading: false });
    }
  },

  selectRecruiterById: async (id: string) => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.getRecruiterById(id);
      if (response.success && response.data) {
        const recruiter = normalizeRecruiter(response.data);
        set({
          selectedRecruiter: recruiter,
          interactions: recruiter.interactions || [],
          loading: false,
        });
        return recruiter;
      } else {
        set({ error: 'Recruiter not found', loading: false });
        return null;
      }
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to load recruiter details';
      set({ error: message, loading: false });
      return null;
    }
  },

  createRecruiter: async (payload: CreateRecruiterPayload) => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.createRecruiter(payload);
      if (response.success && response.data) {
        const newRecruiter = normalizeRecruiter(response.data);
        set((state) => ({
          recruiters: [newRecruiter, ...state.recruiters],
          totalRecruiters: state.totalRecruiters + 1,
          loading: false,
        }));
        get().fetchAnalytics();
        return newRecruiter;
      } else {
        set({ error: 'Failed to add recruiter', loading: false });
        return null;
      }
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Error adding recruiter';
      set({ error: message, loading: false });
      return null;
    }
  },

  updateRecruiter: async (id: string, payload: UpdateRecruiterPayload) => {
    try {
      const response = await apiClient.updateRecruiter(id, payload);
      if (response.success && response.data) {
        const updated = normalizeRecruiter(response.data);
        set((state) => ({
          recruiters: state.recruiters.map((r) => (r.id === id ? { ...r, ...updated } : r)),
          selectedRecruiter:
            state.selectedRecruiter?.id === id
              ? { ...state.selectedRecruiter, ...updated }
              : state.selectedRecruiter,
        }));
        return updated;
      }
      return null;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Error updating recruiter';
      set({ error: message });
      return null;
    }
  },

  deleteRecruiter: async (id: string) => {
    try {
      const response = await apiClient.deleteRecruiter(id);
      if (response.success && response.data) {
        set((state) => ({
          recruiters: state.recruiters.filter((r) => r.id !== id),
          totalRecruiters: Math.max(0, state.totalRecruiters - 1),
          selectedRecruiter: state.selectedRecruiter?.id === id ? null : state.selectedRecruiter,
        }));
        get().fetchAnalytics();
        return true;
      }
      return false;
    } catch {
      return false;
    }
  },

  addInteraction: async (recruiterId: string, payload: CreateInteractionPayload) => {
    try {
      const response = await apiClient.addInteraction(recruiterId, payload);
      if (response.success && response.data) {
        const newInteraction = normalizeInteraction(response.data);
        set((state) => ({
          interactions: [newInteraction, ...state.interactions],
          recruiters: state.recruiters.map((r) =>
            r.id === recruiterId
              ? {
                  ...r,
                  interactionCount: r.interactionCount + 1,
                  lastInteractionDate: newInteraction.interactionDate,
                }
              : r
          ),
          selectedRecruiter:
            state.selectedRecruiter?.id === recruiterId
              ? {
                  ...state.selectedRecruiter,
                  interactionCount: state.selectedRecruiter.interactionCount + 1,
                  lastInteractionDate: newInteraction.interactionDate,
                  interactions: [newInteraction, ...(state.selectedRecruiter.interactions || [])],
                }
              : state.selectedRecruiter,
        }));
        get().fetchAnalytics();
        return newInteraction;
      }
      return null;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Error recording interaction';
      set({ error: message });
      return null;
    }
  },

  fetchHistory: async (recruiterId: string) => {
    try {
      const response = await apiClient.getRecruiterHistory(recruiterId);
      if (response.success && response.data) {
        const list = response.data.map(normalizeInteraction);
        set({ interactions: list });
      }
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Error fetching interaction history';
      set({ error: message });
    }
  },

  addReferral: async (recruiterId: string, payload: CreateReferralPayload) => {
    try {
      const response = await apiClient.addReferral(recruiterId, payload);
      if (response.success && response.data) {
        const newReferral = normalizeReferral(response.data);
        set((state) => ({
          referrals: [newReferral, ...state.referrals],
          recruiters: state.recruiters.map((r) =>
            r.id === recruiterId ? { ...r, referralCount: r.referralCount + 1 } : r
          ),
          selectedRecruiter:
            state.selectedRecruiter?.id === recruiterId
              ? {
                  ...state.selectedRecruiter,
                  referralCount: state.selectedRecruiter.referralCount + 1,
                  referrals: [newReferral, ...(state.selectedRecruiter.referrals || [])],
                }
              : state.selectedRecruiter,
        }));
        get().fetchAnalytics();
        return newReferral;
      }
      return null;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Error logging referral';
      set({ error: message });
      return null;
    }
  },

  fetchReferrals: async (params) => {
    try {
      const response = await apiClient.getReferrals(params);
      if (response.success && response.data) {
        set({ referrals: response.data.map(normalizeReferral) });
      }
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Error loading referrals';
      set({ error: message });
    }
  },

  updateReferral: async (id: string, payload: UpdateReferralPayload) => {
    try {
      const response = await apiClient.updateReferral(id, payload);
      if (response.success && response.data) {
        const updated = normalizeReferral(response.data);
        set((state) => ({
          referrals: state.referrals.map((r) => (r.id === id ? { ...r, ...updated } : r)),
        }));
        get().fetchAnalytics();
        return updated;
      }
      return null;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Error updating referral';
      set({ error: message });
      return null;
    }
  },

  deleteReferral: async (id: string) => {
    try {
      const response = await apiClient.deleteReferral(id);
      if (response.success && response.data) {
        set((state) => ({
          referrals: state.referrals.filter((r) => r.id !== id),
        }));
        get().fetchAnalytics();
        return true;
      }
      return false;
    } catch {
      return false;
    }
  },

  fetchAnalytics: async () => {
    set({ analyticsLoading: true });
    try {
      const response = await apiClient.getNetworkingAnalytics();
      if (response.success && response.data) {
        set({
          analytics: normalizeAnalytics(response.data),
          analyticsLoading: false,
        });
      }
    } catch {
      set({ analyticsLoading: false });
    }
  },

  clearSelected: () => set({ selectedRecruiter: null, interactions: [] }),
  clearError: () => set({ error: null }),
}));
