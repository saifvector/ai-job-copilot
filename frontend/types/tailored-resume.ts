/**
 * Type definitions for Phase 7 AI Resume Tailoring Engine.
 */

export interface KeywordAnalysis {
  matchedKeywords: string[];
  missingKeywords: string[];
  coveragePercentage: number;
  requiredSkills: string[];
  preferredSkills: string[];
  technologies: string[];
  responsibilities: string[];
  keywords: string[];
}

export interface ATSScoreBreakdown {
  overallScore: number;
  keywordMatch: number;
  skillMatch: number;
  sectionQuality: number;
  experienceRelevance: number;
  formattingStructure: number;
  suggestions: string[];
}

export interface ResumeSectionExperience {
  id?: string;
  company: string;
  role: string;
  startDate?: string;
  endDate?: string;
  description: string;
  bulletPoints: string[];
  highlightedKeywords: string[];
}

export interface ResumeSectionSkillGroup {
  category: string;
  skills: string[];
}

export interface ResumeSectionProject {
  id?: string;
  title: string;
  description: string;
  technologies: string[];
  bulletPoints: string[];
}

export interface ResumeSectionEducation {
  id?: string;
  institution: string;
  degree: string;
  fieldOfStudy?: string;
  startDate?: string;
  endDate?: string;
}

export interface ResumeSectionCertification {
  id?: string;
  name: string;
  issuer: string;
  issueDate?: string;
}

export interface ResumeVersion {
  versionType: 'ats' | 'recruiter' | 'balanced';
  label: string;
  summary: string;
  skills: ResumeSectionSkillGroup[];
  experience: ResumeSectionExperience[];
  education: ResumeSectionEducation[];
  projects: ResumeSectionProject[];
  certifications: ResumeSectionCertification[];
}

export interface TailoredResume {
  id: string;
  userId: string;
  jobId: string;
  originalResumeId?: string | null;
  title: string;
  summary: string;
  atsScore: number;
  keywordCoverage: number;
  versions: Record<string, ResumeVersion>;
  keywordAnalysis: KeywordAnalysis;
  atsBreakdown: ATSScoreBreakdown;
  recommendations: string[];
  telemetry?: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface TailoredResumeListItem {
  id: string;
  userId: string;
  jobId: string;
  jobTitle: string;
  jobCompany: string;
  title: string;
  atsScore: number;
  keywordCoverage: number;
  createdAt: string;
  updatedAt: string;
}

export interface TailorResumePayload {
  jobId: string;
  resumeId?: string;
  targetVersion?: 'ats' | 'recruiter' | 'balanced';
  customInstructions?: string;
}
