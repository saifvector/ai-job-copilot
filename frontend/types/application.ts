export type ApplicationStatus =
  | 'SAVED'
  | 'APPLIED'
  | 'ASSESSMENT'
  | 'INTERVIEW'
  | 'OFFER'
  | 'REJECTED'
  | 'WITHDRAWN';

export type InterviewType = 'HR' | 'TECHNICAL' | 'MANAGERIAL' | 'FINAL';

export interface Interview {
  id: string;
  applicationId: string;
  interviewType: InterviewType;
  interviewDate: string;
  interviewRound: number;
  notes?: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface ApplicationEvent {
  id: string;
  applicationId: string;
  eventType: string;
  description: string;
  createdAt: string;
}

export interface ApplicationJobSummary {
  id: string;
  title: string;
  company: string;
  location: string;
  employmentType?: string | null;
  applyUrl?: string | null;
  salaryMin?: number | null;
  salaryMax?: number | null;
  currency?: string | null;
}

export interface Application {
  id: string;
  userId: string;
  jobId: string;
  tailoredResumeId?: string | null;
  status: ApplicationStatus;
  applicationDate?: string | null;
  lastUpdated: string;
  source?: string | null;
  notes?: string | null;
  createdAt: string;
  job?: ApplicationJobSummary | null;
  events: ApplicationEvent[];
  interviews: Interview[];
}

export interface ApplicationListItem {
  id: string;
  userId: string;
  jobId: string;
  jobTitle: string;
  jobCompany: string;
  jobLocation: string;
  status: ApplicationStatus;
  applicationDate?: string | null;
  lastUpdated: string;
  source?: string | null;
  notes?: string | null;
  interviewCount: number;
  nextInterviewDate?: string | null;
  tailoredResumeId?: string | null;
}

export interface PipelineData {
  saved: ApplicationListItem[];
  applied: ApplicationListItem[];
  assessment: ApplicationListItem[];
  interview: ApplicationListItem[];
  offer: ApplicationListItem[];
  rejected: ApplicationListItem[];
  withdrawn: ApplicationListItem[];
  totalActive: number;
  totalApplications: number;
}

export interface ApplicationAnalytics {
  totalApplications: number;
  applicationsSent: number;
  interviewsReceived: number;
  offersReceived: number;
  rejections: number;
  responseRate: number;
  interviewRate: number;
  offerRate: number;
  byStatus: Record<string, number>;
  bySource: Record<string, number>;
  interviewsScheduledUpcoming: number;
  applicationsThisMonth: number;
}

export interface CreateApplicationPayload {
  jobId: string;
  status?: ApplicationStatus;
  tailoredResumeId?: string;
  applicationDate?: string;
  source?: string;
  notes?: string;
}

export interface UpdateApplicationStatusPayload {
  status: ApplicationStatus;
  notes?: string;
}

export interface CreateInterviewPayload {
  interviewType: InterviewType;
  interviewDate: string;
  interviewRound?: number;
  notes?: string;
}

export interface CreateEventPayload {
  eventType: string;
  description: string;
}
