import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useApplicationAssistantStore } from '../store/application-assistant-store';
import { apiClient, ApiClientError } from '../services/api-client';
import type {
  ApplicationDraft,
  ApplicationQuestion,
  AssistantAnalytics,
  ChecklistResponse,
} from '../types/application-assistant';

vi.mock('../services/api-client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../services/api-client')>();
  return {
    ...actual,
    apiClient: {
      ...actual.apiClient,
      createApplicationDraft: vi.fn(),
      getApplicationDraft: vi.fn(),
      generateApplicationAnswers: vi.fn(),
      reviewApplicationDraft: vi.fn(),
      submitApplicationDraft: vi.fn(),
      getApplicationChecklist: vi.fn(),
      getApplicationDrafts: vi.fn(),
      getApplicationAssistantAnalytics: vi.fn(),
      deleteApplicationDraft: vi.fn(),
    },
  };
});

const mockQuestion: ApplicationQuestion = {
  id: 'q-1',
  draftId: 'draft-1',
  question: 'Why do you want this role?',
  generatedAnswer: 'I am excited by the company mission and high engineering standards.',
  userAnswer: null,
  answerType: 'Text',
  options: [],
  isRequired: true,
  isReviewed: false,
  order: 1,
  createdAt: '2026-09-28T10:00:00Z',
  updatedAt: '2026-09-28T10:00:00Z',
};

const mockChecklist: ChecklistResponse = {
  readinessScore: 85,
  isReadyForReview: true,
  items: [
    { category: 'Document', label: 'Resume Selected', isCompleted: true },
    { category: 'Questions', label: 'All Required Questions Answered', isCompleted: true },
  ],
  missingFields: [],
};

const mockDraft: ApplicationDraft = {
  id: 'draft-1',
  userId: 'user-1',
  jobId: 'job-1',
  status: 'Draft',
  generatedAnswers: null,
  selectedResumeId: 'resume-1',
  readinessScore: 85,
  checklist: mockChecklist,
  notes: 'Testing notes',
  submittedAt: null,
  createdAt: '2026-09-28T10:00:00Z',
  updatedAt: '2026-09-28T10:00:00Z',
  questions: [mockQuestion],
  job: {
    id: 'job-1',
    title: 'Senior Software Engineer',
    company: 'Innovate AI',
    location: 'Remote',
  },
};

const mockAnalytics: AssistantAnalytics = {
  draftsCreated: 5,
  draftsCompleted: 3,
  averageCompletionTimeMinutes: 12.5,
  statusCounts: { Draft: 2, SubmittedByUser: 3 },
  totalQuestionsAnswered: 24,
};

describe('useApplicationAssistantStore', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useApplicationAssistantStore.getState().resetDraft();
  });

  it('initializes with default empty state', () => {
    const state = useApplicationAssistantStore.getState();
    expect(state.draft).toBeNull();
    expect(state.drafts).toEqual([]);
    expect(state.answers).toEqual({});
    expect(state.checklist).toBeNull();
    expect(state.activeStep).toBe(1);
    expect(state.loading).toBe(false);
  });

  it('fetches application drafts and stores them', async () => {
    vi.mocked(apiClient.getApplicationDrafts).mockResolvedValueOnce({
      success: true,
      timestamp: '2026-09-28T10:00:00Z',
      data: [mockDraft],
      message: 'Success',
    });

    await useApplicationAssistantStore.getState().fetchDrafts();

    const state = useApplicationAssistantStore.getState();
    expect(state.drafts).toHaveLength(1);
    expect(state.drafts[0].id).toBe('draft-1');
    expect(state.loading).toBe(false);
  });

  it('creates an application draft and advances to step 2', async () => {
    vi.mocked(apiClient.createApplicationDraft).mockResolvedValueOnce({
      success: true,
      timestamp: '2026-09-28T10:00:00Z',
      data: mockDraft,
      message: 'Created',
    });

    const result = await useApplicationAssistantStore.getState().createDraft({
      jobId: 'job-1',
      selectedResumeId: 'resume-1',
    });

    expect(result).not.toBeNull();
    const state = useApplicationAssistantStore.getState();
    expect(state.draft?.id).toBe('draft-1');
    expect(state.answers['q-1']).toBe(mockQuestion.generatedAnswer);
    expect(state.activeStep).toBe(2);
  });

  it('generates answers and updates draft in state', async () => {
    useApplicationAssistantStore.setState({ draft: mockDraft });

    const updatedDraft: ApplicationDraft = {
      ...mockDraft,
      questions: [
        {
          ...mockQuestion,
          generatedAnswer: 'Synthesized tailored answer grounded in past projects.',
        },
      ],
    };

    vi.mocked(apiClient.generateApplicationAnswers).mockResolvedValueOnce({
      success: true,
      timestamp: '2026-09-28T10:00:00Z',
      data: updatedDraft,
      message: 'Success',
    });

    const res = await useApplicationAssistantStore.getState().generateAnswers();
    expect(res).not.toBeNull();
    const state = useApplicationAssistantStore.getState();
    expect(state.draft?.questions[0].generatedAnswer).toBe('Synthesized tailored answer grounded in past projects.');
    expect(state.isGenerating).toBe(false);
  });

  it('updates candidate answer and marks reviewed', () => {
    useApplicationAssistantStore.setState({ draft: mockDraft, answers: { 'q-1': 'Old answer' } });

    useApplicationAssistantStore.getState().updateAnswer('q-1', 'Updated truthful answer', true);

    const state = useApplicationAssistantStore.getState();
    expect(state.answers['q-1']).toBe('Updated truthful answer');
    expect(state.draft?.questions[0].userAnswer).toBe('Updated truthful answer');
    expect(state.draft?.questions[0].isReviewed).toBe(true);
  });

  it('validates checklist and updates readiness score', async () => {
    useApplicationAssistantStore.setState({ draft: mockDraft });

    vi.mocked(apiClient.getApplicationChecklist).mockResolvedValueOnce({
      success: true,
      timestamp: '2026-09-28T10:00:00Z',
      data: mockChecklist,
      message: 'Success',
    });

    const checklist = await useApplicationAssistantStore.getState().validateChecklist('draft-1');
    expect(checklist?.readinessScore).toBe(85);
    expect(useApplicationAssistantStore.getState().checklist?.readinessScore).toBe(85);
  });

  it('submits draft explicitly by candidate', async () => {
    useApplicationAssistantStore.setState({ draft: mockDraft });

    const submittedDraft: ApplicationDraft = {
      ...mockDraft,
      status: 'SubmittedByUser',
      submittedAt: '2026-09-28T10:30:00Z',
    };

    vi.mocked(apiClient.submitApplicationDraft).mockResolvedValueOnce({
      success: true,
      timestamp: '2026-09-28T10:00:00Z',
      data: submittedDraft,
      message: 'Submitted',
    });

    vi.mocked(apiClient.getApplicationAssistantAnalytics).mockResolvedValueOnce({
      success: true,
      timestamp: '2026-09-28T10:00:00Z',
      data: mockAnalytics,
      message: 'Success',
    });

    const res = await useApplicationAssistantStore.getState().submitDraft('draft-1');
    expect(res?.status).toBe('SubmittedByUser');
    expect(useApplicationAssistantStore.getState().draft?.status).toBe('SubmittedByUser');
  });

  it('fetches analytics metrics', async () => {
    vi.mocked(apiClient.getApplicationAssistantAnalytics).mockResolvedValueOnce({
      success: true,
      timestamp: '2026-09-28T10:00:00Z',
      data: mockAnalytics,
      message: 'Success',
    });

    await useApplicationAssistantStore.getState().fetchAnalytics();
    expect(useApplicationAssistantStore.getState().analytics?.draftsCreated).toBe(5);
    expect(useApplicationAssistantStore.getState().analytics?.draftsCompleted).toBe(3);
  });

  it('deletes draft and updates local state', async () => {
    useApplicationAssistantStore.setState({
      drafts: [mockDraft],
      draft: mockDraft,
    });

    vi.mocked(apiClient.deleteApplicationDraft).mockResolvedValueOnce({
      success: true,
      timestamp: '2026-09-28T10:00:00Z',
      data: true,
      message: 'Deleted',
    });

    vi.mocked(apiClient.getApplicationAssistantAnalytics).mockResolvedValueOnce({
      success: true,
      timestamp: '2026-09-28T10:00:00Z',
      data: mockAnalytics,
      message: 'Success',
    });

    const deleted = await useApplicationAssistantStore.getState().deleteDraft('draft-1');
    expect(deleted).toBe(true);
    expect(useApplicationAssistantStore.getState().drafts).toHaveLength(0);
    expect(useApplicationAssistantStore.getState().draft).toBeNull();
  });
});
