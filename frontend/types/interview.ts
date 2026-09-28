export type QuestionCategory =
  | 'HR'
  | 'Technical'
  | 'Behavioral'
  | 'Project-Based'
  | 'Resume-Based'
  | 'System Design';

export type QuestionDifficulty = 'Easy' | 'Medium' | 'Hard';

export interface InterviewQuestion {
  id: string;
  preparationId: string;
  category: QuestionCategory | string;
  difficulty: QuestionDifficulty | string;
  question: string;
  sampleAnswer: string;
  explanation: string;
  userAnswer?: string | null;
  score?: number | null;
  feedback?: string | null;
  isCompleted: boolean;
  evaluatedAt?: string | null;
  createdAt: string;
}

export interface InterviewPreparation {
  id: string;
  userId: string;
  jobId?: string | null;
  role: string;
  preparationType: string;
  generatedAt: string;
  questions: InterviewQuestion[];
  totalQuestions: number;
  completedQuestions: number;
}

export interface AnswerEvaluation {
  questionId?: string | null;
  score: number;
  strengths: string[];
  weaknesses: string[];
  suggestedImprovements: string[];
  feedback: string;
  evaluatedAt: string;
}

export interface QuestionBreakdownItem {
  question: string;
  category: string;
  score: number;
  strengths: string[];
  weaknesses: string[];
  improvements: string[];
}

export interface MockInterviewFeedback {
  overallScore?: number;
  questionsAnswered?: number;
  summary?: string;
  questionBreakdown?: QuestionBreakdownItem[];
  [key: string]: any;
}

export interface MockInterviewSession {
  id: string;
  userId: string;
  role: string;
  score: number;
  feedback: MockInterviewFeedback;
  createdAt: string;
}

export interface SkillDevelopmentRecommendation {
  skill: string;
  category: string;
  priority: 'High' | 'Medium' | 'Low' | string;
  action: string;
  estimatedDays: number;
}

export interface LearningRoadmapStep {
  phase: string;
  title: string;
  focus: string;
  duration: string;
  milestones: string[];
}

export interface CareerCoaching {
  role: string;
  interviewReadinessScore: number;
  strongAreas: string[];
  weakAreas: string[];
  skillDevelopmentRecommendations: SkillDevelopmentRecommendation[];
  learningRoadmap: LearningRoadmapStep[];
}

export interface CategoryBreakdownStats {
  total: number;
  completed: number;
  averageScore: number;
}

export interface InterviewAnalytics {
  questionsCompleted: number;
  averageScore: number;
  weakAreas: string[];
  strongAreas: string[];
  totalSessions: number;
  readinessScore: number;
  categoryBreakdown: Record<string, CategoryBreakdownStats>;
}

export interface QuestionGeneratePayload {
  role: string;
  jobId?: string | null;
  preparationType?: string;
  focusAreas?: string[];
  questionCount?: number;
}

export interface AnswerEvaluationPayload {
  questionId?: string | null;
  question?: string;
  userAnswer: string;
  category?: string;
  difficulty?: string;
  role?: string;
}

export interface MockInterviewSubmissionPayload {
  role: string;
  preparationId?: string | null;
  answers: Array<{
    questionId?: string | null;
    question: string;
    userAnswer: string;
    category?: string;
    difficulty?: string;
  }>;
}
