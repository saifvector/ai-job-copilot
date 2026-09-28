import { create } from 'zustand';
import {
  Application,
  ApplicationAnalytics,
  ApplicationEvent,
  ApplicationJobSummary,
  ApplicationListItem,
  ApplicationStatus,
  CreateApplicationPayload,
  CreateEventPayload,
  CreateInterviewPayload,
  Interview,
  PipelineData,
} from '@/types';
import { apiClient, ApiClientError } from '@/services/api-client';

export interface ApplicationStoreState {
  applications: ApplicationListItem[];
  pipeline: PipelineData;
  selectedApplication: Application | null;
  analytics: ApplicationAnalytics | null;
  loading: boolean;
  analyticsLoading: boolean;
  actionLoading: boolean;
  error: string | null;

  // Actions
  fetchApplications: (params?: { status?: string }) => Promise<void>;
  fetchPipeline: () => Promise<void>;
  fetchAnalytics: () => Promise<void>;
  selectApplicationById: (id: string) => Promise<Application | null>;
  createApplication: (payload: CreateApplicationPayload) => Promise<Application | null>;
  updateStatus: (
    id: string,
    status: ApplicationStatus,
    notes?: string
  ) => Promise<Application | null>;
  updateNotes: (id: string, notes: string) => Promise<Application | null>;
  addEvent: (id: string, payload: CreateEventPayload) => Promise<boolean>;
  addInterview: (id: string, payload: CreateInterviewPayload) => Promise<boolean>;
  deleteApplication: (id: string) => Promise<boolean>;
  clearSelected: () => void;
  clearError: () => void;
}

const emptyPipeline: PipelineData = {
  saved: [],
  applied: [],
  assessment: [],
  interview: [],
  offer: [],
  rejected: [],
  withdrawn: [],
  totalActive: 0,
  totalApplications: 0,
};

function normalizeJob(raw: any): ApplicationJobSummary | null {
  if (!raw) return null;
  return {
    id: raw.id,
    title: raw.title || '',
    company: raw.company || '',
    location: raw.location || 'Remote',
    employmentType: raw.employment_type ?? raw.employmentType ?? null,
    applyUrl: raw.apply_url ?? raw.applyUrl ?? null,
    salaryMin: raw.salary_min ?? raw.salaryMin ?? null,
    salaryMax: raw.salary_max ?? raw.salaryMax ?? null,
    currency: raw.currency ?? 'USD',
  };
}

function normalizeEvent(raw: any): ApplicationEvent {
  return {
    id: raw.id,
    applicationId: raw.application_id ?? raw.applicationId ?? '',
    eventType: raw.event_type ?? raw.eventType ?? 'NOTE_ADDED',
    description: raw.description ?? '',
    createdAt: raw.created_at ?? raw.createdAt ?? new Date().toISOString(),
  };
}

function normalizeInterview(raw: any): Interview {
  return {
    id: raw.id,
    applicationId: raw.application_id ?? raw.applicationId ?? '',
    interviewType: raw.interview_type ?? raw.interviewType ?? 'TECHNICAL',
    interviewDate: raw.interview_date ?? raw.interviewDate ?? '',
    interviewRound: raw.interview_round ?? raw.interviewRound ?? 1,
    notes: raw.notes ?? null,
    createdAt: raw.created_at ?? raw.createdAt ?? new Date().toISOString(),
    updatedAt: raw.updated_at ?? raw.updatedAt ?? new Date().toISOString(),
  };
}

function normalizeApplication(raw: any): Application {
  if (!raw) return raw;
  return {
    id: raw.id,
    userId: raw.user_id ?? raw.userId ?? '',
    jobId: raw.job_id ?? raw.jobId ?? '',
    tailoredResumeId: raw.tailored_resume_id ?? raw.tailoredResumeId ?? null,
    status: raw.status,
    applicationDate: raw.application_date ?? raw.applicationDate ?? null,
    lastUpdated:
      raw.last_updated ?? raw.lastUpdated ?? raw.created_at ?? raw.createdAt ?? new Date().toISOString(),
    source: raw.source ?? null,
    notes: raw.notes ?? null,
    createdAt: raw.created_at ?? raw.createdAt ?? new Date().toISOString(),
    job: normalizeJob(raw.job),
    events: Array.isArray(raw.events) ? raw.events.map(normalizeEvent) : [],
    interviews: Array.isArray(raw.interviews) ? raw.interviews.map(normalizeInterview) : [],
  };
}

function normalizeListItem(raw: any): ApplicationListItem {
  return {
    id: raw.id,
    userId: raw.user_id ?? raw.userId ?? '',
    jobId: raw.job_id ?? raw.jobId ?? '',
    jobTitle: raw.job_title ?? raw.jobTitle ?? raw.job?.title ?? 'Unknown Position',
    jobCompany: raw.job_company ?? raw.jobCompany ?? raw.job?.company ?? 'Unknown Company',
    jobLocation: raw.job_location ?? raw.jobLocation ?? raw.job?.location ?? 'Remote',
    status: raw.status,
    applicationDate: raw.application_date ?? raw.applicationDate ?? null,
    lastUpdated:
      raw.last_updated ?? raw.lastUpdated ?? raw.created_at ?? raw.createdAt ?? new Date().toISOString(),
    source: raw.source ?? null,
    notes: raw.notes ?? null,
    interviewCount:
      raw.interview_count ?? raw.interviewCount ?? (raw.interviews ? raw.interviews.length : 0),
    nextInterviewDate: raw.next_interview_date ?? raw.nextInterviewDate ?? null,
    tailoredResumeId: raw.tailored_resume_id ?? raw.tailoredResumeId ?? null,
  };
}

function normalizePipeline(raw: any): PipelineData {
  if (!raw) return emptyPipeline;
  return {
    saved: Array.isArray(raw.saved) ? raw.saved.map(normalizeListItem) : [],
    applied: Array.isArray(raw.applied) ? raw.applied.map(normalizeListItem) : [],
    assessment: Array.isArray(raw.assessment) ? raw.assessment.map(normalizeListItem) : [],
    interview: Array.isArray(raw.interview) ? raw.interview.map(normalizeListItem) : [],
    offer: Array.isArray(raw.offer) ? raw.offer.map(normalizeListItem) : [],
    rejected: Array.isArray(raw.rejected) ? raw.rejected.map(normalizeListItem) : [],
    withdrawn: Array.isArray(raw.withdrawn) ? raw.withdrawn.map(normalizeListItem) : [],
    totalActive: raw.total_active ?? raw.totalActive ?? 0,
    totalApplications: raw.total_applications ?? raw.totalApplications ?? 0,
  };
}

function normalizeAnalytics(raw: any): ApplicationAnalytics {
  if (!raw) {
    return {
      totalApplications: 0,
      applicationsSent: 0,
      interviewsReceived: 0,
      offersReceived: 0,
      rejections: 0,
      responseRate: 0,
      interviewRate: 0,
      offerRate: 0,
      byStatus: {
        SAVED: 0,
        APPLIED: 0,
        ASSESSMENT: 0,
        INTERVIEW: 0,
        OFFER: 0,
        REJECTED: 0,
        WITHDRAWN: 0,
      },
      bySource: {},
      interviewsScheduledUpcoming: 0,
      applicationsThisMonth: 0,
    };
  }
  return {
    totalApplications: raw.total_applications ?? raw.totalApplications ?? 0,
    applicationsSent: raw.applications_sent ?? raw.applicationsSent ?? 0,
    interviewsReceived: raw.interviews_received ?? raw.interviewsReceived ?? 0,
    offersReceived: raw.offers_received ?? raw.offersReceived ?? 0,
    rejections: raw.rejections ?? 0,
    responseRate: raw.response_rate ?? raw.responseRate ?? 0,
    interviewRate: raw.interview_rate ?? raw.interviewRate ?? 0,
    offerRate: raw.offer_rate ?? raw.offerRate ?? 0,
    byStatus: raw.by_status ?? raw.byStatus ?? {},
    bySource: raw.by_source ?? raw.bySource ?? {},
    interviewsScheduledUpcoming:
      raw.interviews_scheduled_upcoming ?? raw.interviewsScheduledUpcoming ?? 0,
    applicationsThisMonth: raw.applications_this_month ?? raw.applicationsThisMonth ?? 0,
  };
}

export const useApplicationStore = create<ApplicationStoreState>((set, get) => ({
  applications: [],
  pipeline: emptyPipeline,
  selectedApplication: null,
  analytics: null,
  loading: false,
  analyticsLoading: false,
  actionLoading: false,
  error: null,

  fetchApplications: async (params) => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.getApplications(params);
      if (response.success && response.data) {
        const normalized = Array.isArray(response.data) ? response.data.map(normalizeListItem) : [];
        set({ applications: normalized, loading: false });
      } else {
        set({ error: 'Failed to fetch applications', loading: false });
      }
    } catch (err) {
      const message =
        err instanceof ApiClientError ? err.message : 'An error occurred while fetching applications';
      set({ error: message, loading: false });
    }
  },

  fetchPipeline: async () => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.getApplicationPipeline();
      if (response.success && response.data) {
        set({ pipeline: normalizePipeline(response.data), loading: false });
      } else {
        set({ error: 'Failed to load application pipeline', loading: false });
      }
    } catch (err) {
      const message =
        err instanceof ApiClientError ? err.message : 'An error occurred while loading pipeline';
      set({ error: message, loading: false });
    }
  },

  fetchAnalytics: async () => {
    set({ analyticsLoading: true });
    try {
      const response = await apiClient.getApplicationAnalytics();
      if (response.success && response.data) {
        set({ analytics: normalizeAnalytics(response.data), analyticsLoading: false });
      } else {
        set({ analyticsLoading: false });
      }
    } catch {
      set({ analyticsLoading: false });
    }
  },

  selectApplicationById: async (id: string) => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.getApplicationById(id);
      if (response.success && response.data) {
        const app = normalizeApplication(response.data);
        set({ selectedApplication: app, loading: false });
        return app;
      } else {
        set({ error: 'Application not found', loading: false });
        return null;
      }
    } catch (err) {
      const message =
        err instanceof ApiClientError ? err.message : 'Failed to retrieve application details';
      set({ error: message, loading: false });
      return null;
    }
  },

  createApplication: async (payload: CreateApplicationPayload) => {
    set({ actionLoading: true, error: null });
    try {
      const response = await apiClient.createApplication(payload);
      if (response.success && response.data) {
        const app = normalizeApplication(response.data);
        // Refresh pipeline and analytics
        await Promise.all([get().fetchPipeline(), get().fetchAnalytics()]);
        set({ actionLoading: false });
        return app;
      } else {
        set({ error: 'Failed to track application', actionLoading: false });
        return null;
      }
    } catch (err) {
      const message =
        err instanceof ApiClientError ? err.message : 'An error occurred while tracking application';
      set({ error: message, actionLoading: false });
      return null;
    }
  },

  updateStatus: async (id: string, status: ApplicationStatus, notes?: string) => {
    // Optimistic UI state update on pipeline
    const prevPipeline = get().pipeline;
    const allItems = [
      ...prevPipeline.saved,
      ...prevPipeline.applied,
      ...prevPipeline.assessment,
      ...prevPipeline.interview,
      ...prevPipeline.offer,
      ...prevPipeline.rejected,
      ...prevPipeline.withdrawn,
    ];
    const targetItem = allItems.find((item) => item.id === id);

    if (targetItem) {
      const updatedItem: ApplicationListItem = {
        ...targetItem,
        status,
        lastUpdated: new Date().toISOString(),
      };

      const filterOut = (list: ApplicationListItem[]) => list.filter((i) => i.id !== id);

      const optimisticPipeline: PipelineData = {
        saved:
          status === 'SAVED'
            ? [updatedItem, ...filterOut(prevPipeline.saved)]
            : filterOut(prevPipeline.saved),
        applied:
          status === 'APPLIED'
            ? [updatedItem, ...filterOut(prevPipeline.applied)]
            : filterOut(prevPipeline.applied),
        assessment:
          status === 'ASSESSMENT'
            ? [updatedItem, ...filterOut(prevPipeline.assessment)]
            : filterOut(prevPipeline.assessment),
        interview:
          status === 'INTERVIEW'
            ? [updatedItem, ...filterOut(prevPipeline.interview)]
            : filterOut(prevPipeline.interview),
        offer:
          status === 'OFFER'
            ? [updatedItem, ...filterOut(prevPipeline.offer)]
            : filterOut(prevPipeline.offer),
        rejected:
          status === 'REJECTED'
            ? [updatedItem, ...filterOut(prevPipeline.rejected)]
            : filterOut(prevPipeline.rejected),
        withdrawn:
          status === 'WITHDRAWN'
            ? [updatedItem, ...filterOut(prevPipeline.withdrawn)]
            : filterOut(prevPipeline.withdrawn),
        totalActive: prevPipeline.totalActive,
        totalApplications: prevPipeline.totalApplications,
      };

      set({ pipeline: optimisticPipeline });
    }

    try {
      const response = await apiClient.updateApplicationStatus(id, { status, notes });
      if (response.success && response.data) {
        const updated = normalizeApplication(response.data);
        if (get().selectedApplication?.id === id) {
          set({ selectedApplication: updated });
        }
        // Sync analytics in background
        get().fetchAnalytics();
        return updated;
      } else {
        // Rollback
        set({ pipeline: prevPipeline, error: 'Failed to update status' });
        return null;
      }
    } catch (err) {
      set({ pipeline: prevPipeline });
      const message =
        err instanceof ApiClientError ? err.message : 'Error updating application status';
      set({ error: message });
      return null;
    }
  },

  updateNotes: async (id: string, notes: string) => {
    set({ actionLoading: true, error: null });
    try {
      const response = await apiClient.updateApplicationNotes(id, notes);
      if (response.success && response.data) {
        const updated = normalizeApplication(response.data);
        set({
          selectedApplication: updated,
          actionLoading: false,
        });
        get().fetchPipeline();
        return updated;
      } else {
        set({ error: 'Failed to save notes', actionLoading: false });
        return null;
      }
    } catch (err) {
      const message =
        err instanceof ApiClientError ? err.message : 'An error occurred while updating notes';
      set({ error: message, actionLoading: false });
      return null;
    }
  },

  addEvent: async (id: string, payload: CreateEventPayload) => {
    try {
      const response = await apiClient.addApplicationEvent(id, payload);
      if (response.success && response.data) {
        // Reload selected application
        await get().selectApplicationById(id);
        return true;
      }
      return false;
    } catch {
      return false;
    }
  },

  addInterview: async (id: string, payload: CreateInterviewPayload) => {
    try {
      const response = await apiClient.addApplicationInterview(id, payload);
      if (response.success && response.data) {
        await Promise.all([
          get().selectApplicationById(id),
          get().fetchPipeline(),
          get().fetchAnalytics(),
        ]);
        return true;
      }
      return false;
    } catch {
      return false;
    }
  },

  deleteApplication: async (id: string) => {
    try {
      const response = await apiClient.deleteApplication(id);
      if (response.success && response.data) {
        if (get().selectedApplication?.id === id) {
          set({ selectedApplication: null });
        }
        await Promise.all([get().fetchPipeline(), get().fetchAnalytics()]);
        return true;
      }
      return false;
    } catch {
      return false;
    }
  },

  clearSelected: () => set({ selectedApplication: null }),
  clearError: () => set({ error: null }),
}));
