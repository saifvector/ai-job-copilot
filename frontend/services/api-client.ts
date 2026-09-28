import {
  ApiResponse,
  HealthResponse,
  User,
  Profile,
  Resume,
  ResumeDeleteResponse,
  Skill,
  Project,
  Education,
  Experience,
  Certification,
  ResumeParseResponse,
  ProfileSummaryResponse,
  Job,
  JobFilters,
  JobListData,
  JobSyncData,
  MatchFilters,
  MatchResult,
  MatchResultsData,
  MatchRunResult,
  DashboardOverview,
  ProfileHealthData,
  CareerReadinessData,
  SkillGapAnalysisData,
  AnalyticsDashboardData,
  AnalyticsSnapshotItem,
  TailorResumePayload,
  TailoredResume,
  TailoredResumeListItem,
  Application,
  ApplicationListItem,
  PipelineData,
  ApplicationAnalytics,
  CreateApplicationPayload,
  UpdateApplicationStatusPayload,
  CreateInterviewPayload,
  CreateEventPayload,
  Interview,
  ApplicationEvent,
  Report,
  ReportGeneratePayload,
  ReportListData,
  Recruiter,
  RecruiterListData,
  CreateRecruiterPayload,
  UpdateRecruiterPayload,
  ContactInteraction,
  CreateInteractionPayload,
  Referral,
  CreateReferralPayload,
  UpdateReferralPayload,
  NetworkingAnalytics,
  InterviewQuestion,
  InterviewPreparation,
  AnswerEvaluation,
  MockInterviewSession,
  CareerCoaching,
  InterviewAnalytics,
  QuestionGeneratePayload,
  AnswerEvaluationPayload,
  MockInterviewSubmissionPayload,
  ApplicationDraft,
  ChecklistResponse,
  AssistantAnalytics,
  CreateDraftPayload,
  GenerateAnswersPayload,
  ReviewDraftPayload,
  ApiKey,
  ApiKeyCreated,
  ApiKeyCreatePayload,
  ApiKeyRotatePayload,
  Webhook,
  WebhookCreatePayload,
  WebhookUpdatePayload,
  WebhookTestResult,
  WebhookDeliveryLog,
  OAuthConnection,
  IntegrationStatus,
  OAuthConnectPayload,
  OAuthSyncResult,
  PluginManifest,
  PluginRegisterPayload,
  PluginExecutionResult,
  ApiAnalyticsSummary,
  AgentInfo,
  AgentMemory,
  ModelRouteRecommendation,
  AgentTask,
  WorkflowTemplate,
  WorkflowExecution,
  ObservabilityMetrics,
  OutcomeType,
  OutcomeEvent,
  OutcomeAnalyticsSummary,
  ResumePerformance,
  SkillImpact,
  CompanyResponseMetric,
  ApplicationStrategyMetric,
  RecommendationItem,
  TrendPoint,
  HistoricalTrendResponse,
  CareerIntelligenceOverview,
  RecordOutcomePayload,
} from '@/types';



const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClientError extends Error {
  public code: string;
  public status: number;
  public details?: unknown;

  constructor(message: string, status: number, code: string = 'API_ERROR', details?: unknown) {
    super(message);
    this.name = 'ApiClientError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

interface RequestOptions extends RequestInit {
  timeoutMs?: number;
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { timeoutMs = 10000, headers, ...restOptions } = options;
  const url = `${API_BASE_URL}${endpoint}`;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  const defaultHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  };

  try {
    const response = await fetch(url, {
      ...restOptions,
      headers: {
        ...defaultHeaders,
        ...headers,
      },
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    // Parse JSON safely
    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const errorMsg = data?.error?.message || data?.detail || `HTTP Error ${response.status}`;
      const errorCode = data?.error?.code || `HTTP_${response.status}`;
      throw new ApiClientError(errorMsg, response.status, errorCode, data?.error?.details);
    }

    return data as T;
  } catch (err: unknown) {
    clearTimeout(timeoutId);
    if (err instanceof ApiClientError) {
      throw err;
    }
    if ((err as Error)?.name === 'AbortError') {
      throw new ApiClientError('Request timed out', 408, 'REQUEST_TIMEOUT');
    }
    throw new ApiClientError(
      (err as Error)?.message || 'Network request failed',
      0,
      'NETWORK_ERROR'
    );
  }
}

export const apiClient = {
  // Direct GET /health check
  checkRootHealth: async (): Promise<{ status: string }> => {
    return request<{ status: string }>('/health');
  },

  // Detailed GET /api/v1/health check
  checkDetailedHealth: async (): Promise<HealthResponse> => {
    return request<HealthResponse>('/api/v1/health');
  },

  // Users API
  getUsers: async (page = 1, pageSize = 10) => {
    return request<ApiResponse<{ items: User[]; pagination: unknown }>>(
      `/api/v1/users?page=${page}&page_size=${pageSize}`
    );
  },

  getUserById: async (userId: string) => {
    return request<ApiResponse<User>>(`/api/v1/users/${userId}`);
  },

  createUser: async (payload: { name: string; email: string }) => {
    return request<ApiResponse<User>>('/api/v1/users', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  // Profiles API
  getProfile: async (userId: string) => {
    return request<ApiResponse<Profile>>(`/api/v1/profiles/${userId}`);
  },

  upsertProfile: async (userId: string, payload: Partial<Profile>) => {
    return request<ApiResponse<Profile>>(`/api/v1/profiles/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  },

  // ============================================================================
  // Phase 2: Resume Upload & File Management API
  // ============================================================================
  uploadResume: async (
    file: File,
    onProgress?: (percent: number) => void
  ): Promise<ApiResponse<Resume>> => {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      const url = `${API_BASE_URL}/api/v1/resume/upload`;
      const formData = new FormData();
      formData.append('file', file);

      xhr.open('POST', url, true);
      xhr.setRequestHeader('Accept', 'application/json');

      if (onProgress && xhr.upload) {
        xhr.upload.onprogress = (event) => {
          if (event.lengthComputable) {
            const percent = Math.round((event.loaded / event.total) * 100);
            onProgress(percent);
          }
        };
      }

      xhr.onload = () => {
        let jsonResponse: any = null;
        try {
          jsonResponse = JSON.parse(xhr.responseText);
        } catch {
          // Response wasn't valid JSON
        }

        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(jsonResponse as ApiResponse<Resume>);
        } else {
          const message =
            jsonResponse?.error?.message ||
            jsonResponse?.detail ||
            `Upload failed with HTTP ${xhr.status}`;
          const code = jsonResponse?.error?.code || `HTTP_${xhr.status}`;
          reject(new ApiClientError(message, xhr.status, code, jsonResponse?.error?.details));
        }
      };

      xhr.onerror = () => {
        reject(new ApiClientError('Network communication error during file upload', 0, 'NETWORK_ERROR'));
      };

      xhr.ontimeout = () => {
        reject(new ApiClientError('Upload request timed out', 408, 'REQUEST_TIMEOUT'));
      };

      xhr.timeout = 60000; // 60s timeout for large uploads
      xhr.send(formData);
    });
  },

  getResume: async (): Promise<ApiResponse<Resume>> => {
    return request<ApiResponse<Resume>>('/api/v1/resume');
  },

  deleteResume: async (): Promise<ApiResponse<ResumeDeleteResponse>> => {
    return request<ApiResponse<ResumeDeleteResponse>>('/api/v1/resume', {
      method: 'DELETE',
    });
  },

  downloadResume: async (): Promise<{ blob: Blob; filename: string }> => {
    const url = `${API_BASE_URL}/api/v1/resume/download`;
    const response = await fetch(url, {
      method: 'GET',
    });

    if (!response.ok) {
      const data = await response.json().catch(() => null);
      const errorMsg = data?.error?.message || data?.detail || `Download failed with HTTP ${response.status}`;
      throw new ApiClientError(errorMsg, response.status, data?.error?.code || 'DOWNLOAD_ERROR');
    }

    // Extract filename from Content-Disposition header if available
    let filename = 'resume.pdf';
    const disposition = response.headers.get('content-disposition');
    if (disposition && disposition.includes('filename=')) {
      const match = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
      if (match && match[1]) {
        filename = match[1].replace(/['"]/g, '');
      }
    }

    const blob = await response.blob();
    return { blob, filename };
  },

  // ==========================================
  // Phase 3: Resume Intelligence & Profile API
  // ==========================================

  parseResume: async (resumeId?: string): Promise<ApiResponse<ResumeParseResponse>> => {
    const query = resumeId ? `?resume_id=${encodeURIComponent(resumeId)}` : '';
    return request<ApiResponse<ResumeParseResponse>>(`/api/v1/resume/parse${query}`, {
      method: 'POST',
      timeoutMs: 60000, // Allow up to 60s for multi-attempt Gemini AI pipeline
    });
  },

  getProfileSummary: async (): Promise<ApiResponse<ProfileSummaryResponse>> => {
    return request<ApiResponse<ProfileSummaryResponse>>('/api/v1/profile/summary');
  },

  getProfileSkills: async (category?: string): Promise<ApiResponse<Skill[]>> => {
    const query = category ? `?category=${encodeURIComponent(category)}` : '';
    return request<ApiResponse<Skill[]>>(`/api/v1/profile/skills${query}`);
  },

  getProfileProjects: async (): Promise<ApiResponse<Project[]>> => {
    return request<ApiResponse<Project[]>>('/api/v1/profile/projects');
  },

  getProfileEducation: async (): Promise<ApiResponse<Education[]>> => {
    return request<ApiResponse<Education[]>>('/api/v1/profile/education');
  },

  getProfileExperience: async (): Promise<ApiResponse<Experience[]>> => {
    return request<ApiResponse<Experience[]>>('/api/v1/profile/experience');
  },

  getProfileCertifications: async (): Promise<ApiResponse<Certification[]>> => {
    return request<ApiResponse<Certification[]>>('/api/v1/profile/certifications');
  },

  getFullProfileIntelligence: async (): Promise<ApiResponse<ResumeParseResponse>> => {
    return request<ApiResponse<ResumeParseResponse>>('/api/v1/profile/full');
  },

  // ==========================================
  // Phase 4: Job Discovery & Search API
  // ==========================================

  getJobs: async (params?: JobFilters): Promise<ApiResponse<JobListData>> => {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.pageSize) searchParams.set('pageSize', params.pageSize.toString());
    if (params?.sortBy) searchParams.set('sortBy', params.sortBy);
    if (params?.role) searchParams.set('role', params.role);
    if (params?.location) searchParams.set('location', params.location);
    if (params?.source) searchParams.set('source', params.source);
    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return request<ApiResponse<JobListData>>(`/api/v1/jobs${query}`);
  },

  searchJobs: async (params?: JobFilters): Promise<ApiResponse<JobListData>> => {
    const searchParams = new URLSearchParams();
    if (params?.query) searchParams.set('query', params.query);
    if (params?.role) searchParams.set('role', params.role);
    if (params?.location) searchParams.set('location', params.location);
    if (params?.source) searchParams.set('source', params.source);
    if (params?.skill) searchParams.set('skill', params.skill);
    if (params?.minSalary) searchParams.set('minSalary', params.minSalary.toString());
    if (params?.sortBy) searchParams.set('sortBy', params.sortBy);
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.pageSize) searchParams.set('pageSize', params.pageSize.toString());
    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return request<ApiResponse<JobListData>>(`/api/v1/jobs/search${query}`);
  },

  getJobById: async (id: string): Promise<ApiResponse<Job>> => {
    return request<ApiResponse<Job>>(`/api/v1/jobs/${encodeURIComponent(id)}`);
  },

  syncJobs: async (source?: string, limitPerSource: number = 50): Promise<ApiResponse<JobSyncData>> => {
    return request<ApiResponse<JobSyncData>>('/api/v1/jobs/sync', {
      method: 'POST',
      body: JSON.stringify({
        source: source || null,
        limitPerSource,
      }),
      timeoutMs: 45000,
    });
  },

  // ==========================================
  // Phase 5: AI Job Matching Engine API
  // ==========================================

  runMatching: async (params?: { jobIds?: string[]; limit?: number }): Promise<ApiResponse<MatchRunResult>> => {
    return request<ApiResponse<MatchRunResult>>('/api/v1/matching/run', {
      method: 'POST',
      body: JSON.stringify({
        jobIds: params?.jobIds || null,
        limit: params?.limit || 500,
      }),
      timeoutMs: 30000,
    });
  },

  getMatchResults: async (params?: MatchFilters): Promise<ApiResponse<MatchResultsData>> => {
    const searchParams = new URLSearchParams();
    if (params?.minScore !== undefined && params?.minScore !== null) {
      searchParams.set('minScore', params.minScore.toString());
    }
    if (params?.location) searchParams.set('location', params.location);
    if (params?.company) searchParams.set('company', params.company);
    if (params?.role) searchParams.set('role', params.role);
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.pageSize) searchParams.set('pageSize', params.pageSize.toString());
    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return request<ApiResponse<MatchResultsData>>(`/api/v1/matching/results${query}`);
  },

  getTopMatches: async (limit: number = 10): Promise<ApiResponse<MatchResult[]>> => {
    return request<ApiResponse<MatchResult[]>>(`/api/v1/matching/top?limit=${limit}`);
  },

  getMatchResultByJob: async (jobId: string, enrichAi: boolean = false): Promise<ApiResponse<MatchResult>> => {
    const query = enrichAi ? '?enrichAi=true' : '';
    return request<ApiResponse<MatchResult>>(`/api/v1/matching/results/${encodeURIComponent(jobId)}${query}`);
  },

  // ==========================================
  // Phase 6: Dashboard & Analytics API
  // ==========================================

  getDashboard: async (): Promise<ApiResponse<DashboardOverview>> => {
    return request<ApiResponse<DashboardOverview>>('/api/v1/dashboard');
  },

  getProfileHealth: async (): Promise<ApiResponse<ProfileHealthData>> => {
    return request<ApiResponse<ProfileHealthData>>('/api/v1/dashboard/profile-health');
  },

  getCareerReadiness: async (): Promise<ApiResponse<CareerReadinessData>> => {
    return request<ApiResponse<CareerReadinessData>>('/api/v1/dashboard/readiness');
  },

  getSkillGapAnalysis: async (): Promise<ApiResponse<SkillGapAnalysisData>> => {
    return request<ApiResponse<SkillGapAnalysisData>>('/api/v1/dashboard/skills');
  },

  getAnalytics: async (): Promise<ApiResponse<AnalyticsDashboardData>> => {
    return request<ApiResponse<AnalyticsDashboardData>>('/api/v1/dashboard/analytics');
  },

  createAnalyticsSnapshot: async (): Promise<ApiResponse<AnalyticsSnapshotItem>> => {
    return request<ApiResponse<AnalyticsSnapshotItem>>('/api/v1/dashboard/snapshot', {
      method: 'POST',
    });
  },

  // ==========================================
  // Phase 7: AI Resume Tailoring API
  // ==========================================

  tailorResume: async (payload: TailorResumePayload): Promise<ApiResponse<TailoredResume>> => {
    return request<ApiResponse<TailoredResume>>('/api/v1/resume/tailor', {
      method: 'POST',
      body: JSON.stringify(payload),
      timeoutMs: 60000,
    });
  },

  getTailoredResumes: async (): Promise<ApiResponse<TailoredResumeListItem[]>> => {
    return request<ApiResponse<TailoredResumeListItem[]>>('/api/v1/resume/tailored');
  },

  getTailoredResumeById: async (id: string): Promise<ApiResponse<TailoredResume>> => {
    return request<ApiResponse<TailoredResume>>(`/api/v1/resume/tailored/${encodeURIComponent(id)}`);
  },

  exportTailoredResume: async (
    id: string,
    format: 'pdf' | 'docx' | 'markdown' = 'pdf',
    version: 'ats' | 'recruiter' | 'balanced' = 'balanced'
  ): Promise<{ blob: Blob; filename: string }> => {
    const url = `${API_BASE_URL}/api/v1/resume/tailored/${encodeURIComponent(id)}/export?format=${format}&version=${version}`;
    const response = await fetch(url, {
      method: 'GET',
    });

    if (!response.ok) {
      const data = await response.json().catch(() => null);
      const errorMsg = data?.error?.message || data?.detail || `Export failed with HTTP ${response.status}`;
      throw new ApiClientError(errorMsg, response.status, data?.error?.code || 'EXPORT_ERROR');
    }

    let filename = `tailored_resume_${version}.${format === 'markdown' ? 'md' : format}`;
    const disposition = response.headers.get('content-disposition');
    if (disposition && disposition.includes('filename=')) {
      const match = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
      if (match && match[1]) {
        filename = decodeURIComponent(match[1].replace(/['"]/g, ''));
      }
    }

    const blob = await response.blob();
    return { blob, filename };
  },

  // ==========================================
  // Phase 8: Application Tracking System API
  // ==========================================

  createApplication: async (payload: CreateApplicationPayload): Promise<ApiResponse<Application>> => {
    return request<ApiResponse<Application>>('/api/v1/applications', {
      method: 'POST',
      body: JSON.stringify({
        job_id: payload.jobId,
        status: payload.status || 'SAVED',
        tailored_resume_id: payload.tailoredResumeId || null,
        application_date: payload.applicationDate || null,
        source: payload.source || null,
        notes: payload.notes || null,
      }),
    });
  },

  getApplications: async (params?: { status?: string; limit?: number; skip?: number }): Promise<ApiResponse<ApplicationListItem[]>> => {
    const sp = new URLSearchParams();
    if (params?.status) sp.set('status', params.status);
    if (params?.limit) sp.set('limit', params.limit.toString());
    if (params?.skip) sp.set('skip', params.skip.toString());
    const query = sp.toString() ? `?${sp.toString()}` : '';
    return request<ApiResponse<ApplicationListItem[]>>(`/api/v1/applications${query}`);
  },

  getApplicationPipeline: async (): Promise<ApiResponse<PipelineData>> => {
    return request<ApiResponse<PipelineData>>('/api/v1/applications/pipeline');
  },

  getApplicationAnalytics: async (): Promise<ApiResponse<ApplicationAnalytics>> => {
    return request<ApiResponse<ApplicationAnalytics>>('/api/v1/applications/analytics');
  },

  getApplicationById: async (id: string): Promise<ApiResponse<Application>> => {
    return request<ApiResponse<Application>>(`/api/v1/applications/${encodeURIComponent(id)}`);
  },

  updateApplicationStatus: async (
    id: string,
    payload: UpdateApplicationStatusPayload
  ): Promise<ApiResponse<Application>> => {
    return request<ApiResponse<Application>>(`/api/v1/applications/${encodeURIComponent(id)}/status`, {
      method: 'PATCH',
      body: JSON.stringify({
        status: payload.status,
        notes: payload.notes || null,
      }),
    });
  },

  updateApplicationNotes: async (id: string, notes: string): Promise<ApiResponse<Application>> => {
    return request<ApiResponse<Application>>(`/api/v1/applications/${encodeURIComponent(id)}/notes`, {
      method: 'PATCH',
      body: JSON.stringify({ notes }),
    });
  },

  addApplicationEvent: async (
    id: string,
    payload: CreateEventPayload
  ): Promise<ApiResponse<ApplicationEvent>> => {
    return request<ApiResponse<ApplicationEvent>>(`/api/v1/applications/${encodeURIComponent(id)}/events`, {
      method: 'POST',
      body: JSON.stringify({
        event_type: payload.eventType,
        description: payload.description,
      }),
    });
  },

  addApplicationInterview: async (
    id: string,
    payload: CreateInterviewPayload
  ): Promise<ApiResponse<Interview>> => {
    return request<ApiResponse<Interview>>(`/api/v1/applications/${encodeURIComponent(id)}/interviews`, {
      method: 'POST',
      body: JSON.stringify({
        interview_type: payload.interviewType,
        interview_date: payload.interviewDate,
        interview_round: payload.interviewRound || 1,
        notes: payload.notes || null,
      }),
    });
  },

  deleteApplication: async (id: string): Promise<ApiResponse<boolean>> => {
    return request<ApiResponse<boolean>>(`/api/v1/applications/${encodeURIComponent(id)}`, {
      method: 'DELETE',
    });
  },

  generateReport: async (payload: ReportGeneratePayload): Promise<ApiResponse<Report>> => {
    return request<ApiResponse<Report>>('/api/v1/reports/generate', {
      method: 'POST',
      body: JSON.stringify({
        report_type: payload.reportType,
        format: payload.format,
        title: payload.title || null,
        date_range_days: payload.dateRangeDays ?? 30,
        include_details: payload.includeDetails ?? true,
      }),
    });
  },

  getReports: async (params?: {
    report_type?: string;
    format?: string;
  }): Promise<ApiResponse<ReportListData>> => {
    const searchParams = new URLSearchParams();
    if (params?.report_type) searchParams.append('report_type', params.report_type);
    if (params?.format) searchParams.append('format', params.format);
    const queryString = searchParams.toString();
    const endpoint = `/api/v1/reports${queryString ? `?${queryString}` : ''}`;
    return request<ApiResponse<ReportListData>>(endpoint);
  },

  getReportById: async (id: string): Promise<ApiResponse<Report>> => {
    return request<ApiResponse<Report>>(`/api/v1/reports/${encodeURIComponent(id)}`);
  },

  deleteReport: async (id: string): Promise<ApiResponse<boolean>> => {
    return request<ApiResponse<boolean>>(`/api/v1/reports/${encodeURIComponent(id)}`, {
      method: 'DELETE',
    });
  },

  getReportDownloadUrl: (id: string): string => {
    return `${API_BASE_URL}/api/v1/reports/${encodeURIComponent(id)}/download`;
  },

  // ---------------------------------------------------------------------------
  // Phase 10: Recruiter CRM & Networking Intelligence Endpoints
  // ---------------------------------------------------------------------------

  getRecruiters: async (params?: {
    company?: string;
    search?: string;
    limit?: number;
    offset?: number;
  }): Promise<ApiResponse<RecruiterListData>> => {
    const searchParams = new URLSearchParams();
    if (params?.company) searchParams.append('company', params.company);
    if (params?.search) searchParams.append('search', params.search);
    if (params?.limit) searchParams.append('limit', params.limit.toString());
    if (params?.offset) searchParams.append('offset', params.offset.toString());
    const queryString = searchParams.toString();
    return request<ApiResponse<RecruiterListData>>(`/api/v1/recruiters${queryString ? `?${queryString}` : ''}`);
  },

  getRecruiterById: async (id: string): Promise<ApiResponse<Recruiter>> => {
    return request<ApiResponse<Recruiter>>(`/api/v1/recruiters/${encodeURIComponent(id)}`);
  },

  createRecruiter: async (payload: CreateRecruiterPayload): Promise<ApiResponse<Recruiter>> => {
    return request<ApiResponse<Recruiter>>('/api/v1/recruiters', {
      method: 'POST',
      body: JSON.stringify({
        name: payload.name,
        company: payload.company,
        title: payload.title || null,
        email: payload.email || null,
        linkedin_url: payload.linkedinUrl || null,
        notes: payload.notes || null,
      }),
    });
  },

  updateRecruiter: async (id: string, payload: UpdateRecruiterPayload): Promise<ApiResponse<Recruiter>> => {
    return request<ApiResponse<Recruiter>>(`/api/v1/recruiters/${encodeURIComponent(id)}`, {
      method: 'PATCH',
      body: JSON.stringify({
        name: payload.name,
        company: payload.company,
        title: payload.title,
        email: payload.email,
        linkedin_url: payload.linkedinUrl,
        notes: payload.notes,
      }),
    });
  },

  deleteRecruiter: async (id: string): Promise<ApiResponse<boolean>> => {
    return request<ApiResponse<boolean>>(`/api/v1/recruiters/${encodeURIComponent(id)}`, {
      method: 'DELETE',
    });
  },

  addInteraction: async (
    recruiterId: string,
    payload: CreateInteractionPayload
  ): Promise<ApiResponse<ContactInteraction>> => {
    return request<ApiResponse<ContactInteraction>>(`/api/v1/recruiters/${encodeURIComponent(recruiterId)}/interactions`, {
      method: 'POST',
      body: JSON.stringify({
        interaction_type: payload.interactionType,
        summary: payload.summary,
        interaction_date: payload.interactionDate || null,
      }),
    });
  },

  getRecruiterHistory: async (recruiterId: string): Promise<ApiResponse<ContactInteraction[]>> => {
    return request<ApiResponse<ContactInteraction[]>>(`/api/v1/recruiters/${encodeURIComponent(recruiterId)}/history`);
  },

  addReferral: async (
    recruiterId: string,
    payload: CreateReferralPayload
  ): Promise<ApiResponse<Referral>> => {
    return request<ApiResponse<Referral>>(`/api/v1/recruiters/${encodeURIComponent(recruiterId)}/referrals`, {
      method: 'POST',
      body: JSON.stringify({
        company: payload.company,
        role: payload.role,
        status: payload.status || 'Requested',
        notes: payload.notes || null,
      }),
    });
  },

  getReferrals: async (params?: {
    status?: string;
    company?: string;
  }): Promise<ApiResponse<Referral[]>> => {
    const searchParams = new URLSearchParams();
    if (params?.status && params.status !== 'ALL') searchParams.append('status', params.status);
    if (params?.company) searchParams.append('company', params.company);
    const queryString = searchParams.toString();
    return request<ApiResponse<Referral[]>>(`/api/v1/referrals${queryString ? `?${queryString}` : ''}`);
  },

  updateReferral: async (id: string, payload: UpdateReferralPayload): Promise<ApiResponse<Referral>> => {
    return request<ApiResponse<Referral>>(`/api/v1/referrals/${encodeURIComponent(id)}`, {
      method: 'PATCH',
      body: JSON.stringify({
        company: payload.company,
        role: payload.role,
        status: payload.status,
        notes: payload.notes,
      }),
    });
  },

  deleteReferral: async (id: string): Promise<ApiResponse<boolean>> => {
    return request<ApiResponse<boolean>>(`/api/v1/referrals/${encodeURIComponent(id)}`, {
      method: 'DELETE',
    });
  },

  getNetworkingAnalytics: async (): Promise<ApiResponse<NetworkingAnalytics>> => {
    return request<ApiResponse<NetworkingAnalytics>>('/api/v1/recruiters/analytics');
  },

  // ==========================================
  // Phase 11: AI Interview Preparation API
  // ==========================================

  generateInterviewQuestions: async (payload: QuestionGeneratePayload): Promise<ApiResponse<InterviewPreparation>> => {
    return request<ApiResponse<InterviewPreparation>>('/api/v1/interview/generate', {
      method: 'POST',
      body: JSON.stringify(payload),
      timeoutMs: 60000,
    });
  },

  evaluateAnswer: async (payload: AnswerEvaluationPayload): Promise<ApiResponse<AnswerEvaluation>> => {
    return request<ApiResponse<AnswerEvaluation>>('/api/v1/interview/evaluate', {
      method: 'POST',
      body: JSON.stringify(payload),
      timeoutMs: 45000,
    });
  },

  getInterviewQuestions: async (params?: {
    category?: string;
    difficulty?: string;
    isCompleted?: boolean;
    preparationId?: string;
    limit?: number;
    offset?: number;
  }): Promise<ApiResponse<InterviewQuestion[]>> => {
    const searchParams = new URLSearchParams();
    if (params?.category && params.category !== 'ALL') searchParams.append('category', params.category);
    if (params?.difficulty && params.difficulty !== 'ALL') searchParams.append('difficulty', params.difficulty);
    if (params?.isCompleted !== undefined) searchParams.append('isCompleted', String(params.isCompleted));
    if (params?.preparationId) searchParams.append('preparationId', params.preparationId);
    if (params?.limit) searchParams.append('limit', String(params.limit));
    if (params?.offset) searchParams.append('offset', String(params.offset));
    const queryString = searchParams.toString();
    return request<ApiResponse<InterviewQuestion[]>>(`/api/v1/interview/questions${queryString ? `?${queryString}` : ''}`);
  },

  getInterviewHistory: async (): Promise<ApiResponse<{ mockInterviews: MockInterviewSession[]; preparations: InterviewPreparation[]; totalSessions: number }>> => {
    return request<ApiResponse<{ mockInterviews: MockInterviewSession[]; preparations: InterviewPreparation[]; totalSessions: number }>>('/api/v1/interview/history');
  },

  submitMockInterview: async (payload: MockInterviewSubmissionPayload): Promise<ApiResponse<MockInterviewSession>> => {
    return request<ApiResponse<MockInterviewSession>>('/api/v1/interview/mock', {
      method: 'POST',
      body: JSON.stringify(payload),
      timeoutMs: 60000,
    });
  },

  getCareerCoaching: async (role: string = 'Senior Full-Stack Engineer'): Promise<ApiResponse<CareerCoaching>> => {
    return request<ApiResponse<CareerCoaching>>(`/api/v1/interview/coaching?role=${encodeURIComponent(role)}`);
  },

  getInterviewAnalytics: async (): Promise<ApiResponse<InterviewAnalytics>> => {
    return request<ApiResponse<InterviewAnalytics>>('/api/v1/interview/analytics');
  },

  getInterviewPreparationById: async (id: string): Promise<ApiResponse<InterviewPreparation>> => {
    return request<ApiResponse<InterviewPreparation>>(`/api/v1/interview/preparations/${encodeURIComponent(id)}`);
  },

  deleteInterviewPreparation: async (id: string): Promise<ApiResponse<boolean>> => {
    return request<ApiResponse<boolean>>(`/api/v1/interview/preparations/${encodeURIComponent(id)}`, {
      method: 'DELETE',
    });
  },

  // ==========================================
  // Phase 12: Application Assistant API
  // ==========================================

  createApplicationDraft: async (payload: CreateDraftPayload): Promise<ApiResponse<ApplicationDraft>> => {
    return request<ApiResponse<ApplicationDraft>>('/api/v1/application-assistant/create', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  getApplicationDraft: async (id: string): Promise<ApiResponse<ApplicationDraft>> => {
    return request<ApiResponse<ApplicationDraft>>(`/api/v1/application-assistant/${encodeURIComponent(id)}`);
  },

  generateApplicationAnswers: async (payload: GenerateAnswersPayload): Promise<ApiResponse<ApplicationDraft>> => {
    return request<ApiResponse<ApplicationDraft>>('/api/v1/application-assistant/generate-answers', {
      method: 'POST',
      body: JSON.stringify(payload),
      timeoutMs: 60000,
    });
  },

  reviewApplicationDraft: async (payload: ReviewDraftPayload): Promise<ApiResponse<ApplicationDraft>> => {
    return request<ApiResponse<ApplicationDraft>>('/api/v1/application-assistant/review', {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
  },

  submitApplicationDraft: async (id: string): Promise<ApiResponse<ApplicationDraft>> => {
    return request<ApiResponse<ApplicationDraft>>(`/api/v1/application-assistant/${encodeURIComponent(id)}/submit`, {
      method: 'POST',
    });
  },

  getApplicationChecklist: async (id: string): Promise<ApiResponse<ChecklistResponse>> => {
    return request<ApiResponse<ChecklistResponse>>(`/api/v1/application-assistant/${encodeURIComponent(id)}/checklist`);
  },

  getApplicationDrafts: async (statusFilter?: string): Promise<ApiResponse<ApplicationDraft[]>> => {
    const qs = statusFilter ? `?status=${encodeURIComponent(statusFilter)}` : '';
    return request<ApiResponse<ApplicationDraft[]>>(`/api/v1/application-assistant/drafts${qs}`);
  },

  getApplicationAssistantAnalytics: async (): Promise<ApiResponse<AssistantAnalytics>> => {
    return request<ApiResponse<AssistantAnalytics>>('/api/v1/application-assistant/analytics');
  },

  deleteApplicationDraft: async (id: string): Promise<ApiResponse<boolean>> => {
    return request<ApiResponse<boolean>>(`/api/v1/application-assistant/${encodeURIComponent(id)}`, {
      method: 'DELETE',
    });
  },

  // --- Developer Portal & API Keys ---
  listApiKeys: async (): Promise<{ items: ApiKey[]; total: number }> => {
    return request<{ items: ApiKey[]; total: number }>('/api/v1/developer/keys');
  },

  createApiKey: async (payload: ApiKeyCreatePayload): Promise<ApiKeyCreated> => {
    return request<ApiKeyCreated>('/api/v1/developer/keys', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  rotateApiKey: async (keyId: string, payload: ApiKeyRotatePayload = {}): Promise<ApiKeyCreated> => {
    return request<ApiKeyCreated>(`/api/v1/developer/keys/${encodeURIComponent(keyId)}/rotate`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  revokeApiKey: async (keyId: string): Promise<{ message: string; key_id: string }> => {
    return request<{ message: string; key_id: string }>(`/api/v1/developer/keys/${encodeURIComponent(keyId)}`, {
      method: 'DELETE',
    });
  },

  getApiAnalytics: async (days: number = 7): Promise<ApiAnalyticsSummary> => {
    return request<ApiAnalyticsSummary>(`/api/v1/developer/analytics?days=${days}`);
  },

  // --- Integrations ---
  listIntegrations: async (): Promise<{ items: IntegrationStatus[]; total: number }> => {
    return request<{ items: IntegrationStatus[]; total: number }>('/api/v1/developer/integrations');
  },

  connectIntegration: async (provider: string, payload: OAuthConnectPayload = {}): Promise<OAuthConnection> => {
    return request<OAuthConnection>(`/api/v1/developer/integrations/${encodeURIComponent(provider)}/connect`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  disconnectIntegration: async (provider: string): Promise<{ message: string; provider: string }> => {
    return request<{ message: string; provider: string }>(`/api/v1/developer/integrations/${encodeURIComponent(provider)}`, {
      method: 'DELETE',
    });
  },

  syncIntegration: async (provider: string): Promise<OAuthSyncResult> => {
    return request<OAuthSyncResult>(`/api/v1/developer/integrations/${encodeURIComponent(provider)}/sync`, {
      method: 'POST',
    });
  },

  // --- Plugins ---
  listPlugins: async (): Promise<{ items: PluginManifest[]; total: number }> => {
    return request<{ items: PluginManifest[]; total: number }>('/api/v1/developer/plugins');
  },

  registerPlugin: async (payload: PluginRegisterPayload): Promise<PluginManifest> => {
    return request<PluginManifest>('/api/v1/developer/plugins', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  executePluginHook: async (
    pluginId: string,
    hook: string,
    payload: Record<string, any> = {}
  ): Promise<PluginExecutionResult> => {
    return request<PluginExecutionResult>(`/api/v1/developer/plugins/${encodeURIComponent(pluginId)}/execute`, {
      method: 'POST',
      body: JSON.stringify({ hook, payload }),
    });
  },

  // --- Webhooks ---
  listWebhooks: async (): Promise<{ items: Webhook[]; total: number }> => {
    return request<{ items: Webhook[]; total: number }>('/api/v1/webhooks');
  },

  createWebhook: async (payload: WebhookCreatePayload): Promise<Webhook> => {
    return request<Webhook>('/api/v1/webhooks', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  updateWebhook: async (id: string, payload: WebhookUpdatePayload): Promise<Webhook> => {
    return request<Webhook>(`/api/v1/webhooks/${encodeURIComponent(id)}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
  },

  deleteWebhook: async (id: string): Promise<{ message: string; webhook_id: string }> => {
    return request<{ message: string; webhook_id: string }>(`/api/v1/webhooks/${encodeURIComponent(id)}`, {
      method: 'DELETE',
    });
  },

  testWebhook: async (id: string, event: string = 'job.matched'): Promise<WebhookTestResult> => {
    return request<WebhookTestResult>(`/api/v1/webhooks/${encodeURIComponent(id)}/test`, {
      method: 'POST',
      body: JSON.stringify({ event }),
    });
  },

  getWebhookDeliveries: async (id: string, limit: number = 20): Promise<{ items: WebhookDeliveryLog[]; total: number }> => {
    return request<{ items: WebhookDeliveryLog[]; total: number }>(`/api/v1/webhooks/${encodeURIComponent(id)}/deliveries?limit=${limit}`);
  },

  // --- AI Agent Orchestration (Phase 15) ---
  listAgents: async (): Promise<{ items: AgentInfo[]; total: number }> => {
    return request<{ items: AgentInfo[]; total: number }>('/api/v1/agents');
  },

  getAgent: async (name: string): Promise<AgentInfo> => {
    return request<AgentInfo>(`/api/v1/agents/${encodeURIComponent(name)}`);
  },

  executeAgent: async (
    name: string,
    payload: Record<string, any>,
    modelOverride?: string
  ): Promise<any> => {
    return request<any>(`/api/v1/agents/${encodeURIComponent(name)}/execute`, {
      method: 'POST',
      body: JSON.stringify({ payload, model_override: modelOverride }),
    });
  },

  listAgentMemories: async (agent?: string): Promise<{ items: AgentMemory[]; total: number }> => {
    const query = agent ? `?agent=${encodeURIComponent(agent)}` : '';
    return request<{ items: AgentMemory[]; total: number }>(`/api/v1/agents/memories${query}`);
  },

  storeAgentMemory: async (payload: {
    agent: string;
    memory_type: string;
    content: Record<string, any>;
    relevance_score?: number;
  }): Promise<AgentMemory> => {
    return request<AgentMemory>('/api/v1/agents/memories', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  routeModel: async (payload: {
    task_type: string;
    complexity?: string;
    speed_preference?: string;
    cost_preference?: string;
    privacy_level?: string;
  }): Promise<ModelRouteRecommendation> => {
    return request<ModelRouteRecommendation>('/api/v1/agents/model-route', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  listTasks: async (filters?: { agent?: string; status?: string }): Promise<{ items: AgentTask[]; total: number }> => {
    const params = new URLSearchParams();
    if (filters?.agent) params.append('agent', filters.agent);
    if (filters?.status) params.append('status', filters.status);
    const qs = params.toString() ? `?${params.toString()}` : '';
    return request<{ items: AgentTask[]; total: number }>(`/api/v1/tasks${qs}`);
  },

  getTask: async (id: string): Promise<AgentTask> => {
    return request<AgentTask>(`/api/v1/tasks/${encodeURIComponent(id)}`);
  },

  createTask: async (payload: {
    agent: string;
    payload: Record<string, any>;
    model_override?: string;
  }): Promise<AgentTask> => {
    return request<AgentTask>('/api/v1/tasks', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  retryTask: async (id: string): Promise<AgentTask> => {
    return request<AgentTask>(`/api/v1/tasks/${encodeURIComponent(id)}/retry`, {
      method: 'POST',
    });
  },

  cancelTask: async (id: string): Promise<AgentTask> => {
    return request<AgentTask>(`/api/v1/tasks/${encodeURIComponent(id)}/cancel`, {
      method: 'POST',
    });
  },

  listWorkflows: async (): Promise<WorkflowTemplate[]> => {
    return request<WorkflowTemplate[]>('/api/v1/workflows');
  },

  getWorkflow: async (id: string): Promise<WorkflowTemplate> => {
    return request<WorkflowTemplate>(`/api/v1/workflows/${encodeURIComponent(id)}`);
  },

  executeWorkflow: async (payload: {
    workflow_type: string;
    initial_context?: Record<string, any>;
  }): Promise<any> => {
    return request<any>('/api/v1/workflows/execute', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  listWorkflowExecutions: async (filters?: {
    workflow_type?: string;
    status?: string;
  }): Promise<{ items: WorkflowExecution[]; total: number }> => {
    const params = new URLSearchParams();
    if (filters?.workflow_type) params.append('workflow_type', filters.workflow_type);
    if (filters?.status) params.append('status', filters.status);
    const qs = params.toString() ? `?${params.toString()}` : '';
    return request<{ items: WorkflowExecution[]; total: number }>(`/api/v1/workflows/executions${qs}`);
  },

  getWorkflowExecution: async (id: string): Promise<WorkflowExecution> => {
    return request<WorkflowExecution>(`/api/v1/workflows/executions/${encodeURIComponent(id)}`);
  },

  getOrchestrationTelemetry: async (): Promise<ObservabilityMetrics> => {
    return request<ObservabilityMetrics>('/api/v1/workflows/telemetry/metrics');
  },

  // Phase 16 Career Intelligence & Outcome Learning Platform
  getCareerIntelligenceOverview: async (): Promise<CareerIntelligenceOverview> => {
    return request<CareerIntelligenceOverview>('/api/v1/intelligence/overview');
  },

  listOutcomeEvents: async (filters?: {
    outcome_type?: string;
    limit?: number;
    offset?: number;
  }): Promise<{ items: OutcomeEvent[]; total: number }> => {
    const params = new URLSearchParams();
    if (filters?.outcome_type) params.append('outcome_type', filters.outcome_type);
    if (filters?.limit) params.append('limit', String(filters.limit));
    if (filters?.offset) params.append('offset', String(filters.offset));
    const qs = params.toString() ? `?${params.toString()}` : '';
    return request<{ items: OutcomeEvent[]; total: number }>(`/api/v1/intelligence/outcomes${qs}`);
  },

  recordOutcomeEvent: async (payload: RecordOutcomePayload): Promise<OutcomeEvent> => {
    return request<OutcomeEvent>('/api/v1/intelligence/outcomes', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  getOutcomeAnalytics: async (): Promise<OutcomeAnalyticsSummary> => {
    return request<OutcomeAnalyticsSummary>('/api/v1/intelligence/analytics');
  },

  listSkillImpacts: async (): Promise<{ items: SkillImpact[]; total: number; disclaimer: string }> => {
    return request<{ items: SkillImpact[]; total: number; disclaimer: string }>('/api/v1/intelligence/skills');
  },

  listResumePerformances: async (): Promise<{ items: ResumePerformance[]; total: number }> => {
    return request<{ items: ResumePerformance[]; total: number }>('/api/v1/intelligence/resumes');
  },

  getCompanyResponseAnalytics: async (): Promise<{ companies: CompanyResponseMetric[]; total_companies: number }> => {
    return request<{ companies: CompanyResponseMetric[]; total_companies: number }>('/api/v1/intelligence/companies');
  },

  getApplicationStrategyAnalytics: async (): Promise<ApplicationStrategyMetric> => {
    return request<ApplicationStrategyMetric>('/api/v1/intelligence/strategy');
  },

  getCareerRecommendations: async (): Promise<{
    recommendations: RecommendationItem[];
    generated_at: string;
    basis_data_points: number;
  }> => {
    return request<{
      recommendations: RecommendationItem[];
      generated_at: string;
      basis_data_points: number;
    }>('/api/v1/intelligence/recommendations');
  },

  getCareerTrends: async (days: number = 90): Promise<HistoricalTrendResponse> => {
    return request<HistoricalTrendResponse>(`/api/v1/intelligence/trends?days=${days}`);
  },

  createCareerSnapshot: async (): Promise<any> => {
    return request<any>('/api/v1/intelligence/snapshots', {
      method: 'POST',
    });
  },
};

export { ApiClientError };

