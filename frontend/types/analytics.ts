/**
 * TypeScript types for Phase 6 Dashboard and Analytics Workspace.
 */

export interface MatchInsightItem {
  jobId: string;
  jobTitle: string;
  company: string;
  matchScore: number;
  location: string;
  source: string;
  postedDate: string | null;
  employmentType?: string | null;
  salaryMin?: number | null;
  salaryMax?: number | null;
  currency?: string | null;
  applyUrl: string;
  companyWebsite?: string | null;
  missingSkills: string[];
  isSaved?: boolean;
}

export interface DashboardTrends {
  matchScoreDelta: number;
  jobsMatchedDelta: number;
  profileScoreDelta: number;
  readinessDelta: number;
}

export interface DashboardOverview {
  totalJobs: number;
  jobsMatched: number;
  averageMatchScore: number;
  excellentMatches: number;
  strongMatches: number;
  moderateMatches: number;
  weakMatches: number;
  trends: DashboardTrends;
  topMatches: MatchInsightItem[];
  profileScore: number;
  readinessScore: number;
  latencyMs: number;
  generatedAt: string;
}

export interface ProfileHealthBreakdown {
  resumeCompleteness: number;
  skillCoverage: number;
  experienceCoverage: number;
  educationCoverage: number;
}

export interface ProfileHealthData {
  overallScore: number;
  breakdown: ProfileHealthBreakdown;
  strengths: string[];
  actionableRecommendations: string[];
  lastUpdated: string;
}

export interface CareerReadinessFactors {
  resumeQuality: number;
  skillsAlignment: number;
  experienceDepth: number;
  marketMatchRate: number;
}

export interface CareerReadinessData {
  careerReadinessScore: number;
  tier: string;
  factors: CareerReadinessFactors;
  explanation: string;
  keyCompetencies: string[];
  growthPriorities: string[];
  generatedAt: string;
}

export interface SkillFrequencyItem {
  name: string;
  count: number;
  percentage: number;
  inCandidateProfile: boolean;
  priority?: string | null;
  category?: string | null;
  recommendation?: string | null;
}

export interface SkillGapAnalysisData {
  totalAnalyzedJobs: number;
  candidateSkillsCount: number;
  mostRequestedSkills: SkillFrequencyItem[];
  missingSkills: SkillFrequencyItem[];
  emergingSkills: SkillFrequencyItem[];
  recommendations: string[];
}

export interface DistributionItem {
  name: string;
  value: number;
  color: string;
  percentage: number;
}

export interface MatchDistributionData {
  excellent: number;
  strong: number;
  moderate: number;
  weak: number;
  total: number;
  items: DistributionItem[];
}

export interface TopSkillDemandItem {
  name: string;
  demand: number;
  valueScore: number;
}

export interface MissingSkillItem {
  name: string;
  frequency: number;
  importance: string;
}

export interface LocationDistributionItem {
  type: string;
  count: number;
  percentage: number;
}

export interface AnalyticsSnapshotItem {
  id: string;
  timestamp: string;
  profileScore: number;
  readinessScore: number;
  averageMatchScore: number;
  excellentMatches: number;
  strongMatches: number;
  moderateMatches: number;
  weakMatches: number;
}

export interface AnalyticsDashboardData {
  matchDistribution: MatchDistributionData;
  topSkills: TopSkillDemandItem[];
  missingSkills: MissingSkillItem[];
  locationDistribution: LocationDistributionItem[];
  profileProgress: AnalyticsSnapshotItem[];
  latencyMs: number;
  generatedAt: string;
}
