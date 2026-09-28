import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useInterviewStore } from '../store/interview-store';
import { apiClient, ApiClientError } from '../services/api-client';
import type {
  InterviewQuestion,
  InterviewPreparation,
  AnswerEvaluation,
  MockInterviewSession,
  CareerCoaching,
  InterviewAnalytics,
} from '../types/interview';

vi.mock('../services/api-client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../services/api-client')>();
  return {
    ...actual,
    apiClient: {
      ...actual.apiClient,
      getInterviewQuestions: vi.fn(),
      generateInterviewQuestions: vi.fn(),
      evaluateAnswer: vi.fn(),
      getInterviewHistory: vi.fn(),
      submitMockInterview: vi.fn(),
      getCareerCoaching: vi.fn(),
      getInterviewAnalytics: vi.fn(),
      deleteInterviewPreparation: vi.fn(),
    },
  };
});

const mockQuestion: InterviewQuestion = {
  id: 'q-101',
  preparationId: 'prep-1',
  category: 'Technical',
  difficulty: 'Hard',
  question: 'Explain Python GIL and memory management with reference counting.',
  sampleAnswer: 'The GIL prevents multi-threaded Python bytecode execution. Memory is managed via reference counting and cyclical garbage collection.',
  explanation: 'Tests deep runtime internals.',
  userAnswer: null,
  score: null,
  feedback: null,
  isCompleted: false,
  evaluatedAt: null,
  createdAt: '2026-09-27T10:00:00Z',
};

const mockPreparation: InterviewPreparation = {
  id: 'prep-1',
  userId: 'user-1',
  jobId: null,
  role: 'Senior Full-Stack Engineer',
  preparationType: 'Comprehensive',
  generatedAt: '2026-09-27T10:00:00Z',
  questions: [mockQuestion],
  totalQuestions: 1,
  completedQuestions: 0,
};

const mockEvaluation: AnswerEvaluation = {
  questionId: 'q-101',
  score: 88,
  strengths: ['Clear explanation of GIL', 'Mentioned cyclic GC'],
  weaknesses: ['Could mention tracemalloc'],
  suggestedImprovements: ['Contrast with multiprocessing pool'],
  feedback: 'Strong understanding of Python internals.',
  evaluatedAt: '2026-09-27T10:05:00Z',
};

const mockSession: MockInterviewSession = {
  id: 'session-1',
  userId: 'user-1',
  role: 'Senior Full-Stack Engineer',
  score: 85,
  feedback: {
    overallScore: 85,
    summary: 'Candidate demonstrated senior-level technical depth and structured communication.',
    questionBreakdown: [
      {
        question: 'Explain Python GIL',
        category: 'Technical',
        score: 88,
        strengths: ['Detailed GIL knowledge'],
        weaknesses: [],
        improvements: ['Include benchmarks'],
      },
    ],
  },
  createdAt: '2026-09-27T10:10:00Z',
};

const mockCoaching: CareerCoaching = {
  role: 'Senior Full-Stack Engineer',
  interviewReadinessScore: 82,
  strongAreas: ['Python', 'System Architecture', 'REST APIs'],
  weakAreas: ['Distributed Caching', 'Kubernetes'],
  skillDevelopmentRecommendations: [
    {
      skill: 'Distributed Caching',
      category: 'System Design',
      priority: 'High',
      action: 'Study Redis eviction policies and Sentinel HA replication',
      estimatedDays: 4,
    },
  ],
  learningRoadmap: [
    {
      phase: 'Week 1',
      title: 'Core Concurrency & Data Structures',
      focus: 'Asyncio, event loop, locks',
      duration: '7 days',
      milestones: ['Build custom async worker pool'],
    },
  ],
};

const mockAnalytics: InterviewAnalytics = {
  questionsCompleted: 12,
  averageScore: 84.5,
  weakAreas: ['Distributed Caching'],
  strongAreas: ['Python', 'FastAPI'],
  totalSessions: 3,
  readinessScore: 82,
  categoryBreakdown: {
    Technical: { total: 10, completed: 8, averageScore: 85 },
  },
};

describe('Interview Store', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useInterviewStore.setState({
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
    });
  });

  it('fetchQuestions should populate questions state', async () => {
    vi.mocked(apiClient.getInterviewQuestions).mockResolvedValueOnce({
      success: true,
      data: [mockQuestion],
    } as any);

    await useInterviewStore.getState().fetchQuestions();

    const state = useInterviewStore.getState();
    expect(state.questions).toHaveLength(1);
    expect(state.questions[0].id).toBe('q-101');
    expect(state.loading).toBe(false);
  });

  it('generateQuestions should call AI engine and prepend to state', async () => {
    vi.mocked(apiClient.generateInterviewQuestions).mockResolvedValueOnce({
      success: true,
      data: mockPreparation,
    } as any);
    vi.mocked(apiClient.getInterviewAnalytics).mockResolvedValueOnce({
      success: true,
      data: mockAnalytics,
    } as any);
    vi.mocked(apiClient.getInterviewHistory).mockResolvedValueOnce({
      success: true,
      data: { preparations: [mockPreparation], mockInterviews: [] },
    } as any);

    const result = await useInterviewStore.getState().generateQuestions({
      role: 'Senior Full-Stack Engineer',
      preparationType: 'Comprehensive',
      questionCount: 5,
    });

    expect(result).toBeDefined();
    expect(result?.role).toBe('Senior Full-Stack Engineer');
    const state = useInterviewStore.getState();
    expect(state.preparations).toHaveLength(1);
    expect(state.questions).toHaveLength(1);
  });

  it('evaluateAnswer should evaluate response and optimistically update question status', async () => {
    useInterviewStore.setState({
      questions: [mockQuestion],
      activeQuestion: mockQuestion,
    });

    vi.mocked(apiClient.evaluateAnswer).mockResolvedValueOnce({
      success: true,
      data: mockEvaluation,
    } as any);
    vi.mocked(apiClient.getInterviewAnalytics).mockResolvedValueOnce({
      success: true,
      data: mockAnalytics,
    } as any);

    const result = await useInterviewStore.getState().evaluateAnswer({
      questionId: 'q-101',
      userAnswer: 'The GIL coordinates thread execution in CPython.',
    });

    expect(result).toBeDefined();
    expect(result?.score).toBe(88);

    const state = useInterviewStore.getState();
    expect(state.questions[0].isCompleted).toBe(true);
    expect(state.questions[0].score).toBe(88);
    expect(state.activeQuestion?.isCompleted).toBe(true);
    expect(state.feedback?.score).toBe(88);
  });

  it('submitMockInterview should store completed mock session', async () => {
    vi.mocked(apiClient.submitMockInterview).mockResolvedValueOnce({
      success: true,
      data: mockSession,
    } as any);
    vi.mocked(apiClient.getInterviewAnalytics).mockResolvedValueOnce({
      success: true,
      data: mockAnalytics,
    } as any);

    const result = await useInterviewStore.getState().submitMockInterview({
      role: 'Senior Full-Stack Engineer',
      answers: [{ question: 'Explain GIL', userAnswer: 'GIL limits execution' }],
    });

    expect(result).toBeDefined();
    expect(result?.score).toBe(85);
    const state = useInterviewStore.getState();
    expect(state.sessions).toHaveLength(1);
  });

  it('fetchCareerCoaching should populate coaching roadmap and recommendations', async () => {
    vi.mocked(apiClient.getCareerCoaching).mockResolvedValueOnce({
      success: true,
      data: mockCoaching,
    } as any);

    await useInterviewStore.getState().fetchCareerCoaching('Senior Full-Stack Engineer');

    const state = useInterviewStore.getState();
    expect(state.coaching).toBeDefined();
    expect(state.coaching?.interviewReadinessScore).toBe(82);
    expect(state.coaching?.learningRoadmap).toHaveLength(1);
  });

  it('timer controls should increment and reset properly', () => {
    const store = useInterviewStore.getState();

    store.startTimer();
    expect(useInterviewStore.getState().isTimerRunning).toBe(true);

    store.tickTimer();
    expect(useInterviewStore.getState().practiceTimerSeconds).toBe(1);
    expect(useInterviewStore.getState().timerSeconds).toBe(1);

    store.pauseTimer();
    expect(useInterviewStore.getState().isTimerRunning).toBe(false);

    store.resetTimer();
    expect(useInterviewStore.getState().practiceTimerSeconds).toBe(0);
    expect(useInterviewStore.getState().timerSeconds).toBe(0);
  });

  it('filtering actions should set category and search queries', () => {
    const store = useInterviewStore.getState();

    store.setSelectedCategory('Technical');
    expect(useInterviewStore.getState().activeCategory).toBe('Technical');
    expect(useInterviewStore.getState().selectedCategory).toBe('Technical');

    store.setSelectedDifficulty('Hard');
    expect(useInterviewStore.getState().activeDifficulty).toBe('Hard');
    expect(useInterviewStore.getState().selectedDifficulty).toBe('Hard');

    store.setSearchQuery('Python');
    expect(useInterviewStore.getState().searchQuery).toBe('Python');
  });
});
