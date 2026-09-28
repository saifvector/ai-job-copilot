import { create } from 'zustand';
import {
  ApplicationDraft,
  ApplicationQuestion,
  AssistantAnalytics,
  ChecklistResponse,
  CreateDraftPayload,
  GenerateAnswersPayload,
  ReviewDraftPayload,
} from '@/types';
import { apiClient, ApiClientError } from '@/services/api-client';

export interface ApplicationAssistantState {
  draft: ApplicationDraft | null;
  drafts: ApplicationDraft[];
  answers: Record<string, string>; // questionId -> candidate edited/current answer
  checklist: ChecklistResponse | null;
  analytics: AssistantAnalytics | null;
  loading: boolean;
  isGenerating: boolean;
  isSaving: boolean;
  isSubmitting: boolean;
  error: string | null;
  activeStep: number; // 1: Job & Resume, 2: Questions & Answers, 3: Checklist & Validation, 4: Review & Confirm
  accuracyConfirmed: boolean;

  // Actions
  fetchDrafts: (statusFilter?: string) => Promise<void>;
  fetchDraft: (id: string) => Promise<ApplicationDraft | null>;
  createDraft: (payload: CreateDraftPayload) => Promise<ApplicationDraft | null>;
  generateAnswers: (payload?: Partial<GenerateAnswersPayload>) => Promise<ApplicationDraft | null>;
  updateAnswer: (questionId: string, answer: string, isReviewed?: boolean) => void;
  selectResume: (resumeId: string) => Promise<void>;
  saveReviewDraft: (options?: { confirmAccuracy?: boolean; status?: ApplicationDraft['status'] }) => Promise<ApplicationDraft | null>;
  validateChecklist: (draftId?: string) => Promise<ChecklistResponse | null>;
  submitDraft: (draftId?: string) => Promise<ApplicationDraft | null>;
  fetchAnalytics: () => Promise<void>;
  deleteDraft: (id: string) => Promise<boolean>;
  setActiveStep: (step: number) => void;
  setAccuracyConfirmed: (confirmed: boolean) => void;
  clearError: () => void;
  resetDraft: () => void;
}

export const useApplicationAssistantStore = create<ApplicationAssistantState>((set, get) => ({
  draft: null,
  drafts: [],
  answers: {},
  checklist: null,
  analytics: null,
  loading: false,
  isGenerating: false,
  isSaving: false,
  isSubmitting: false,
  error: null,
  activeStep: 1,
  accuracyConfirmed: false,

  fetchDrafts: async (statusFilter?: string) => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.getApplicationDrafts(statusFilter);
      set({ drafts: response.data || [], loading: false });
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to fetch application drafts';
      set({ error: message, loading: false });
    }
  },

  fetchDraft: async (id: string) => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.getApplicationDraft(id);
      const draft = response.data;
      const initialAnswers: Record<string, string> = {};
      if (draft.questions) {
        draft.questions.forEach((q) => {
          initialAnswers[q.id] = q.userAnswer || q.generatedAnswer || '';
        });
      }
      set({
        draft,
        answers: initialAnswers,
        checklist: draft.checklist || null,
        loading: false,
      });
      return draft;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to fetch application draft';
      set({ error: message, loading: false });
      return null;
    }
  },

  createDraft: async (payload: CreateDraftPayload) => {
    set({ loading: true, error: null });
    try {
      const response = await apiClient.createApplicationDraft(payload);
      const draft = response.data;
      const initialAnswers: Record<string, string> = {};
      if (draft.questions) {
        draft.questions.forEach((q) => {
          initialAnswers[q.id] = q.userAnswer || q.generatedAnswer || '';
        });
      }
      set((state) => ({
        draft,
        drafts: [draft, ...state.drafts.filter((d) => d.id !== draft.id)],
        answers: initialAnswers,
        checklist: draft.checklist || null,
        activeStep: 2,
        loading: false,
      }));
      return draft;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to create application draft';
      set({ error: message, loading: false });
      return null;
    }
  },

  generateAnswers: async (payload?: Partial<GenerateAnswersPayload>) => {
    const currentDraft = get().draft;
    if (!currentDraft && !payload?.draftId) {
      set({ error: 'No active application draft selected for answer generation' });
      return null;
    }

    const draftId = payload?.draftId || currentDraft!.id;
    set({ isGenerating: true, error: null });

    try {
      const response = await apiClient.generateApplicationAnswers({
        draftId,
        customQuestions: payload?.customQuestions,
        regenerateAll: payload?.regenerateAll ?? false,
      });
      const updatedDraft = response.data;
      const updatedAnswers: Record<string, string> = {};
      if (updatedDraft.questions) {
        updatedDraft.questions.forEach((q) => {
          updatedAnswers[q.id] = q.userAnswer || q.generatedAnswer || '';
        });
      }

      set((state) => ({
        draft: updatedDraft,
        drafts: state.drafts.map((d) => (d.id === updatedDraft.id ? updatedDraft : d)),
        answers: updatedAnswers,
        checklist: updatedDraft.checklist || null,
        isGenerating: false,
      }));
      return updatedDraft;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'AI answer generation failed';
      set({ error: message, isGenerating: false });
      return null;
    }
  },

  updateAnswer: (questionId: string, answer: string, isReviewed = true) => {
    set((state) => {
      const newAnswers = { ...state.answers, [questionId]: answer };
      const updatedDraft = state.draft
        ? {
            ...state.draft,
            questions: state.draft.questions.map((q) =>
              q.id === questionId ? { ...q, userAnswer: answer, isReviewed } : q
            ),
          }
        : null;

      return {
        answers: newAnswers,
        draft: updatedDraft,
      };
    });
  },

  selectResume: async (resumeId: string) => {
    const currentDraft = get().draft;
    if (!currentDraft) return;

    set((state) => ({
      draft: state.draft ? { ...state.draft, selectedResumeId: resumeId } : null,
    }));

    await get().saveReviewDraft();
  },

  saveReviewDraft: async (options?: { confirmAccuracy?: boolean; status?: ApplicationDraft['status'] }) => {
    const currentDraft = get().draft;
    if (!currentDraft) return null;

    set({ isSaving: true, error: null });
    const currentAnswers = get().answers;

    const answerUpdates = (currentDraft.questions || []).map((q) => ({
      questionId: q.id,
      userAnswer: currentAnswers[q.id] ?? q.userAnswer ?? q.generatedAnswer ?? '',
      isReviewed: q.isReviewed || (options?.confirmAccuracy ?? false),
    }));

    const payload: ReviewDraftPayload = {
      draftId: currentDraft.id,
      selectedResumeId: currentDraft.selectedResumeId || undefined,
      answers: answerUpdates,
      confirmAccuracy: options?.confirmAccuracy ?? get().accuracyConfirmed,
      status: options?.status,
    };

    try {
      const response = await apiClient.reviewApplicationDraft(payload);
      const updatedDraft = response.data;

      set((state) => ({
        draft: updatedDraft,
        drafts: state.drafts.map((d) => (d.id === updatedDraft.id ? updatedDraft : d)),
        checklist: updatedDraft.checklist || null,
        isSaving: false,
        accuracyConfirmed: options?.confirmAccuracy ?? state.accuracyConfirmed,
      }));
      return updatedDraft;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to save review edits';
      set({ error: message, isSaving: false });
      return null;
    }
  },

  validateChecklist: async (draftId?: string) => {
    const targetId = draftId || get().draft?.id;
    if (!targetId) return null;

    try {
      const response = await apiClient.getApplicationChecklist(targetId);
      const checklist = response.data;
      set((state) => ({
        checklist,
        draft: state.draft ? { ...state.draft, checklist, readinessScore: checklist.readinessScore } : null,
      }));
      return checklist;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to evaluate checklist';
      set({ error: message });
      return null;
    }
  },

  submitDraft: async (draftId?: string) => {
    const targetId = draftId || get().draft?.id;
    if (!targetId) {
      set({ error: 'No active application draft to submit' });
      return null;
    }

    set({ isSubmitting: true, error: null });
    try {
      const response = await apiClient.submitApplicationDraft(targetId);
      const submitted = response.data;

      set((state) => ({
        draft: submitted,
        drafts: state.drafts.map((d) => (d.id === submitted.id ? submitted : d)),
        checklist: submitted.checklist || null,
        isSubmitting: false,
      }));
      // Refresh analytics
      get().fetchAnalytics();
      return submitted;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Candidate submission failed';
      set({ error: message, isSubmitting: false });
      return null;
    }
  },

  fetchAnalytics: async () => {
    try {
      const response = await apiClient.getApplicationAssistantAnalytics();
      set({ analytics: response.data });
    } catch (err) {
      console.warn('Failed to load application assistant analytics:', err);
    }
  },

  deleteDraft: async (id: string) => {
    try {
      await apiClient.deleteApplicationDraft(id);
      set((state) => ({
        drafts: state.drafts.filter((d) => d.id !== id),
        draft: state.draft?.id === id ? null : state.draft,
      }));
      get().fetchAnalytics();
      return true;
    } catch (err) {
      const message = err instanceof ApiClientError ? err.message : 'Failed to delete draft';
      set({ error: message });
      return false;
    }
  },

  setActiveStep: (step: number) => set({ activeStep: step }),
  setAccuracyConfirmed: (confirmed: boolean) => set({ accuracyConfirmed: confirmed }),
  clearError: () => set({ error: null }),
  resetDraft: () => set({ draft: null, answers: {}, checklist: null, activeStep: 1, accuracyConfirmed: false }),
}));

// Backward-compatible alias matching user specification
export const applicationAssistantStore = useApplicationAssistantStore;
