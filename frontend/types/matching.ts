export type MatchScoreCategory = 'excellent' | 'strong' | 'moderate' | 'weak';

export interface MatchJobSnippet {
  id: string;
  title: string;
  company: string;
  location: string;
  employmentType?: string | null;
  salaryMin?: number | null;
  salaryMax?: number | null;
  currency?: string | null;
  source: string;
  applyUrl: string;
  companyWebsite?: string | null;
  postedAt?: string | null;
  description?: string | null;
  requirements?: string | null;
}

export interface MatchResult {
  id: string;
  userId: string;
  jobId: string;
  overallScore: number;
  skillScore: number;
  experienceScore: number;
  educationScore: number;
  locationScore: number;
  roleScore: number;
  strengths: string[];
  missingSkills: string[];
  recommendations: string[];
  generatedAt: string;
  updatedAt: string;
  job?: MatchJobSnippet | null;
}

export interface MatchFilters {
  minScore?: number | null;
  location?: string;
  company?: string;
  role?: string;
  page?: number;
  pageSize?: number;
}

export interface MatchRunResult {
  totalEvaluated: number;
  matchesSaved: number;
  topScore: number;
  durationMs: number;
}

export interface MatchPaginationData {
  page: number;
  pageSize: number;
  totalItems: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export interface MatchResultsData {
  items: MatchResult[];
  pagination: MatchPaginationData;
}
