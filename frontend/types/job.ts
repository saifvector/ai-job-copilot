export interface Job {
  id: string;
  source: string;
  externalId: string;
  title: string;
  company: string;
  location: string;
  employmentType?: string | null;
  salaryMin?: number | null;
  salaryMax?: number | null;
  currency?: string | null;
  description: string;
  requirements?: string | null;
  applyUrl: string;
  companyWebsite?: string | null;
  postedAt?: string | null;
  createdAt: string;
  updatedAt: string;
  skills: string[];
}

export interface JobFilters {
  query?: string;
  role?: string;
  location?: string;
  source?: string;
  skill?: string;
  minSalary?: number;
  sortBy?: 'newest' | 'highest_salary' | 'most_relevant' | string;
  page?: number;
  pageSize?: number;
}

export interface JobListData {
  items: Job[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface JobSyncData {
  syncedCount: number;
  duplicatesSkipped: number;
  errorsCount: number;
  sources: Record<string, number>;
  durationMs: number;
  message: string;
}
