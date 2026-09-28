export type OutcomeType =
  | 'InterviewReceived'
  | 'AssessmentReceived'
  | 'OfferReceived'
  | 'Rejected'
  | 'Withdrawn';

export interface OutcomeEvent {
  id: string;
  userId: string;
  applicationId: string;
  outcomeType: OutcomeType;
  occurredAt: string;
  notes?: string;
  metadata?: Record<string, unknown>;
  createdAt: string;
  jobTitle?: string;
  company?: string;
}

export interface OutcomeAnalyticsSummary {
  totalApplications: number;
  totalOutcomes: number;
  interviewsReceived: number;
  assessmentsReceived: number;
  offersReceived: number;
  rejectionsReceived: number;
  withdrawals: number;
  interviewRate: number;
  assessmentRate: number;
  offerRate: number;
  rejectionRate: number;
  avgResponseDays: number;
  medianResponseDays: number;
  activeFunnel: Record<string, number>;
}

export interface ResumePerformance {
  id: string;
  tailoredResumeId?: string;
  resumeTitle?: string;
  targetRole?: string;
  atsScore?: number;
  applicationsSent: number;
  interviewsReceived: number;
  offersReceived: number;
  responseRate: number;
  interviewConversionRate: number;
  updatedAt: string;
}

export interface SkillImpact {
  id: string;
  skillName: string;
  interviewsInfluenced: number;
  offersInfluenced: number;
  averageMatchScore: number;
  correlationScore: number;
  sampleSize: number;
  recommendationWeight: 'CRITICAL' | 'HIGH' | 'MODERATE' | 'LOW';
  updatedAt: string;
}

export interface CompanyResponseMetric {
  company: string;
  applicationsSent: number;
  responsesReceived: number;
  interviewsCount: number;
  offersCount: number;
  responseRate: number;
  interviewRate: number;
  avgResponseDays: number;
}

export interface ApplicationStrategyMetric {
  sourceBreakdown: Array<{
    source: string;
    sent: number;
    interviews: number;
    response_rate: number;
  }>;
  scoreTierBreakdown: Array<{
    tier: string;
    sent: number;
    interviews: number;
    rate: number;
  }>;
  weeklyCadence: Array<{
    week: string;
    count: number;
  }>;
  keyInsights: string[];
}

export interface RecommendationItem {
  id: string;
  category: 'SKILL' | 'RESUME' | 'STRATEGY' | 'ROLE';
  title: string;
  description: string;
  evidence: string;
  impactLevel: 'HIGH' | 'MEDIUM' | 'LOW';
  actionSuggested: string;
  confidenceScore: number;
}

export interface TrendPoint {
  date: string;
  applications: number;
  interviews: number;
  offers: number;
  responseRate: number;
}

export interface CohortPoint {
  cohort: string;
  applications: number;
  interviews: number;
  conversionRate: number;
}

export interface HistoricalTrendResponse {
  trends: TrendPoint[];
  cohorts: CohortPoint[];
}

export interface CareerIntelligenceOverview {
  analytics: OutcomeAnalyticsSummary;
  topResumes: ResumePerformance[];
  topSkills: SkillImpact[];
  topCompanies: CompanyResponseMetric[];
  strategy: ApplicationStrategyMetric;
  recommendations: RecommendationItem[];
  trends: TrendPoint[];
}

export interface RecordOutcomePayload {
  application_id: string;
  outcome_type: OutcomeType;
  occurred_at?: string;
  notes?: string;
  metadata?: Record<string, unknown>;
}
