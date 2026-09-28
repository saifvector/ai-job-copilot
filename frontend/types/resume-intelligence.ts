/**
 * Phase 3 Resume Intelligence and Candidate Profile Types.
 */

export type SkillCategory =
  | 'Programming Language'
  | 'Framework'
  | 'Database'
  | 'Cloud'
  | 'AI/ML'
  | 'Tool'
  | 'Other';

export interface Skill {
  id: string;
  userId: string;
  name: string;
  category: SkillCategory;
  confidenceScore: number;
  createdAt: string;
}

export interface Project {
  id: string;
  userId: string;
  title: string;
  description: string;
  technologies: string[];
  createdAt: string;
}

export interface Education {
  id: string;
  userId: string;
  institution: string;
  degree: string;
  fieldOfStudy?: string | null;
  startDate?: string | null;
  endDate?: string | null;
  createdAt: string;
}

export interface Experience {
  id: string;
  userId: string;
  company: string;
  role: string;
  description: string;
  startDate?: string | null;
  endDate?: string | null;
  createdAt: string;
}

export interface Certification {
  id: string;
  userId: string;
  name: string;
  issuer: string;
  issueDate?: string | null;
  createdAt: string;
}

export interface CandidateContact {
  name: string;
  email?: string;
  phone?: string;
}

export interface ResumeParseResponse {
  userId: string;
  candidate: CandidateContact;
  summary: string;
  skills: Skill[];
  projects: Project[];
  education: Education[];
  experience: Experience[];
  certifications: Certification[];
  modelUsed: string;
  parsedAt: string;
}

export interface ProfileSummaryResponse {
  userId: string;
  summary: string;
  updatedAt?: string;
}
