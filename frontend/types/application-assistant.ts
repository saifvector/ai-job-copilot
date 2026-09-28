/**
 * Phase 12: Application Assistant TypeScript Types & Interfaces.
 */

export type AnswerType = 'Text' | 'YesNo' | 'MultiSelect' | 'Numeric';

export type DraftStatus = 'Draft' | 'ReadyForReview' | 'SubmittedByUser' | 'Cancelled';

export interface ApplicationQuestion {
  id: string;
  draftId: string;
  question: string;
  generatedAnswer?: string | null;
  userAnswer?: string | null;
  answerType: AnswerType;
  options: string[];
  isRequired: boolean;
  isReviewed: boolean;
  order: number;
  createdAt: string;
  updatedAt: string;
}

export interface ChecklistItem {
  category: 'Document' | 'Questions' | 'Review' | 'Profile' | string;
  label: string;
  isCompleted: boolean;
  details?: string | null;
}

export interface ChecklistResponse {
  readinessScore: number;
  isReadyForReview: boolean;
  items: ChecklistItem[];
  missingFields: string[];
}

export interface ApplicationDraftJob {
  id: string;
  title: string;
  company: string;
  location: string;
  salary?: string;
  description?: string;
  requirements?: string[];
  applyUrl?: string;
}

export interface ApplicationDraft {
  id: string;
  userId: string;
  jobId: string;
  status: DraftStatus;
  generatedAnswers?: string | null;
  selectedResumeId?: string | null;
  readinessScore: number;
  checklist?: ChecklistResponse | null;
  notes?: string | null;
  submittedAt?: string | null;
  createdAt: string;
  updatedAt: string;
  questions: ApplicationQuestion[];
  job?: ApplicationDraftJob | null;
}

export interface AssistantAnalytics {
  draftsCreated: number;
  draftsCompleted: number;
  averageCompletionTimeMinutes: number;
  statusCounts: Record<string, number>;
  totalQuestionsAnswered: number;
}

export interface CreateDraftPayload {
  jobId: string;
  selectedResumeId?: string;
  notes?: string;
  customQuestions?: Array<{
    question: string;
    answerType?: AnswerType;
    options?: string[];
    isRequired?: boolean;
    order?: number;
  }>;
}

export interface GenerateAnswersPayload {
  draftId: string;
  customQuestions?: Array<{
    question: string;
    answerType?: AnswerType;
    options?: string[];
    isRequired?: boolean;
    order?: number;
  }>;
  regenerateAll?: boolean;
}

export interface QuestionUpdatePayload {
  questionId: string;
  userAnswer?: string | null;
  isReviewed: boolean;
}

export interface ReviewDraftPayload {
  draftId: string;
  selectedResumeId?: string;
  answers?: QuestionUpdatePayload[];
  notes?: string;
  confirmAccuracy?: boolean;
  status?: DraftStatus;
}
