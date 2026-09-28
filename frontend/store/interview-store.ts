import { create } from 'zustand';
import {
  AnswerEvaluation,
  AnswerEvaluationPayload,
  CareerCoaching,
  InterviewAnalytics,
  InterviewPreparation,
  InterviewQuestion,
  MockInterviewSession,
  MockInterviewSubmissionPayload,
  QuestionGeneratePayload,
} from '@/types';
import { apiClient, ApiClientError } from '@/services/api-client';

export interface InterviewStoreState {
  questions: InterviewQuestion[];
  sessions: MockInterviewSession[];
  preparations: InterviewPreparation[];
  activePreparation: InterviewPreparation | null;
  activeQuestion: InterviewQuestion | null;
  feedback: AnswerEvaluation | null;
  coaching: CareerCoaching | null;
  analytics: InterviewAnalytics | null;
  loading: boolean;
  evaluating: boolean;
  generating: boolean;
  error: string | null;

  // Filter & Practice UI State
  activeCategory: string;
  activeDifficulty: string;
  searchQuery: string;
  practiceTimerSeconds: number;
  timerSeconds: number;
  isTimerRunning: boolean;
  selectedCategory: string;
  selectedDifficulty: string;

  // Actions
  fetchQuestions: (params?: {
    category?: string;
    difficulty?: string;
    isCompleted?: boolean;
    preparationId?: string;
  }) => Promise<void>;
  generateQuestions: (payload: QuestionGeneratePayload) => Promise<InterviewPreparation | null>;
  evaluateAnswer: (
    payloadOrQuestionId: AnswerEvaluationPayload | string,
    optionalAnswer?: string
  ) => Promise<AnswerEvaluation | null>;
  fetchHistory: () => Promise<void>;
  fetchSessions: () => Promise<void>;
  submitMockInterview: (payload: MockInterviewSubmissionPayload) => Promise<MockInterviewSession | null>;
  fetchCareerCoaching: (role?: string) => Promise<void>;
  fetchCoaching: (role?: string) => Promise<void>;
  fetchAnalytics: () => Promise<void>;
  deletePreparation: (id: string) => Promise<boolean>;

  // Local UI actions
  setActiveQuestion: (question: InterviewQuestion | null) => void;
  setActiveCategory: (category: string) => void;
  setActiveDifficulty: (difficulty: string) => void;
  setSelectedCategory: (category: string | null) => void;
  setSelectedDifficulty: (difficulty: string | null) => void;
  setSearchQuery: (query: string) => void;
  startTimer: () => void;
  pauseTimer: () => void;
  resetTimer: () => void;
  tickTimer: () => void;
  clearFeedback: () => void;
  clearError: () => void;
}

export const useInterviewStore = create<InterviewStoreState>((set, get) => ({
  questions: [],
  sessions: [],
  preparations: [],
  activePreparation: null,
  activeQuestion: null,
  feedback: null,
  coaching: null,
  analytics: null,
  loading: false,
  evaluating: false,
  generating: false,
  error: null,

  activeCategory: 'ALL',
  activeDifficulty: 'ALL',
  selectedCategory: 'ALL',
  selectedDifficulty: 'ALL',
  searchQuery: '',
  practiceTimerSeconds: 0,
  timerSeconds: 0,
  isTimerRunning: false,

  fetchQuestions: async (params) => {
    set({ loading: true, error: null });
    try {
      const res = await apiClient.getInterviewQuestions({
        category: params?.category ?? (get().activeCategory !== 'ALL' ? get().activeCategory : undefined),
        difficulty: params?.difficulty ?? (get().activeDifficulty !== 'ALL' ? get().activeDifficulty : undefined),
        isCompleted: params?.isCompleted,
        preparationId: params?.preparationId,
      });
      set({ questions: res.data ?? [], loading: false });
    } catch (err: unknown) {
      const msg = err instanceof ApiClientError ? err.message : 'Failed to fetch interview questions.';
      set({ error: msg, loading: false });
    }
  },

  generateQuestions: async (payload) => {
    set({ generating: true, error: null });
    try {
      const res = await apiClient.generateInterviewQuestions(payload);
      const prep = res.data;
      if (prep) {
        set((state) => ({
          preparations: [prep, ...state.preparations.filter((p) => p.id !== prep.id)],
          activePreparation: prep,
          questions: [...(prep.questions || []), ...state.questions],
          generating: false,
        }));
        // Refresh analytics and history
        get().fetchAnalytics();
        get().fetchHistory();
      }
      return prep;
    } catch (err: unknown) {
      const msg = err instanceof ApiClientError ? err.message : 'Failed to generate interview questions.';
      set({ error: msg, generating: false });
      return null;
    }
  },

  evaluateAnswer: async (payloadOrQuestionId, optionalAnswer) => {
    set({ evaluating: true, error: null });
    try {
      const payload: AnswerEvaluationPayload =
        typeof payloadOrQuestionId === 'string'
          ? { questionId: payloadOrQuestionId, userAnswer: optionalAnswer || '' }
          : payloadOrQuestionId;

      const res = await apiClient.evaluateAnswer(payload);
      const evalData = res.data;
      if (evalData) {
        set((state) => {
          // Optimistically update question status in list if questionId provided
          const updatedQuestions = state.questions.map((q) => {
            if (q.id === payload.questionId) {
              return {
                ...q,
                userAnswer: payload.userAnswer,
                score: evalData.score,
                feedback: evalData.feedback,
                isCompleted: true,
                evaluatedAt: evalData.evaluatedAt,
              };
            }
            return q;
          });

          const currentActive = state.activeQuestion;
          const updatedActive =
            currentActive && currentActive.id === payload.questionId
              ? {
                  ...currentActive,
                  userAnswer: payload.userAnswer,
                  score: evalData.score,
                  feedback: evalData.feedback,
                  isCompleted: true,
                  evaluatedAt: evalData.evaluatedAt,
                }
              : currentActive;

          return {
            feedback: evalData,
            questions: updatedQuestions,
            activeQuestion: updatedActive,
            evaluating: false,
          };
        });
        // Refresh analytics
        get().fetchAnalytics();
      }
      return evalData;
    } catch (err: unknown) {
      const msg = err instanceof ApiClientError ? err.message : 'Failed to evaluate answer.';
      set({ error: msg, evaluating: false });
      return null;
    }
  },

  fetchHistory: async () => {
    try {
      const res = await apiClient.getInterviewHistory();
      if (res.data) {
        set({
          sessions: res.data.mockInterviews ?? [],
          preparations: res.data.preparations ?? [],
        });
      }
    } catch (err: unknown) {
      console.error('Failed to load interview history:', err);
    }
  },

  submitMockInterview: async (payload) => {
    set({ loading: true, error: null });
    try {
      const res = await apiClient.submitMockInterview(payload);
      const session = res.data;
      if (session) {
        set((state) => ({
          sessions: [session, ...state.sessions],
          loading: false,
        }));
        get().fetchAnalytics();
      }
      return session;
    } catch (err: unknown) {
      const msg = err instanceof ApiClientError ? err.message : 'Failed to submit mock interview session.';
      set({ error: msg, loading: false });
      return null;
    }
  },

  fetchCareerCoaching: async (role) => {
    try {
      const res = await apiClient.getCareerCoaching(role);
      set({ coaching: res.data ?? null });
    } catch (err: unknown) {
      console.error('Failed to load career coaching:', err);
    }
  },

  fetchAnalytics: async () => {
    try {
      const res = await apiClient.getInterviewAnalytics();
      set({ analytics: res.data ?? null });
    } catch (err: unknown) {
      console.error('Failed to load interview analytics:', err);
    }
  },

  deletePreparation: async (id) => {
    try {
      const res = await apiClient.deleteInterviewPreparation(id);
      if (res.data) {
        set((state) => ({
          preparations: state.preparations.filter((p) => p.id !== id),
          questions: state.questions.filter((q) => q.preparationId !== id),
          activePreparation: state.activePreparation?.id === id ? null : state.activePreparation,
        }));
        get().fetchAnalytics();
        return true;
      }
      return false;
    } catch (err: unknown) {
      console.error('Failed to delete preparation:', err);
      return false;
    }
  },

  setActiveQuestion: (question) => {
    set({
      activeQuestion: question,
      feedback: question?.feedback
        ? {
            questionId: question.id,
            score: question.score ?? 75,
            strengths: ['Previous practice completed.'],
            weaknesses: [],
            suggestedImprovements: [],
            feedback: question.feedback,
            evaluatedAt: question.evaluatedAt || new Date().toISOString(),
          }
        : null,
      practiceTimerSeconds: 0,
      isTimerRunning: false,
    });
  },

  fetchSessions: async () => {
    return get().fetchHistory();
  },

  fetchCoaching: async (role?: string) => {
    return get().fetchCareerCoaching(role);
  },

  setActiveCategory: (category) => {
    set({ activeCategory: category, selectedCategory: category });
  },

  setActiveDifficulty: (difficulty) => {
    set({ activeDifficulty: difficulty, selectedDifficulty: difficulty });
  },

  setSelectedCategory: (category) => {
    const val = category || 'ALL';
    set({ activeCategory: val, selectedCategory: val });
  },

  setSelectedDifficulty: (difficulty) => {
    const val = difficulty || 'ALL';
    set({ activeDifficulty: val, selectedDifficulty: val });
  },

  setSearchQuery: (query) => {
    set({ searchQuery: query });
  },

  startTimer: () => {
    set({ isTimerRunning: true });
  },

  pauseTimer: () => {
    set({ isTimerRunning: false });
  },

  resetTimer: () => {
    set({ practiceTimerSeconds: 0, timerSeconds: 0, isTimerRunning: false });
  },

  tickTimer: () => {
    set((state) => ({
      practiceTimerSeconds: state.practiceTimerSeconds + 1,
      timerSeconds: state.practiceTimerSeconds + 1,
    }));
  },

  clearFeedback: () => {
    set({ feedback: null });
  },

  clearError: () => {
    set({ error: null });
  },
}));
