import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useTailoredResumeStore } from '../store/tailored-resume-store';
import { apiClient, ApiClientError } from '../services/api-client';
import type { TailoredResume, TailoredResumeListItem } from '../types/tailored-resume';

vi.mock('../services/api-client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../services/api-client')>();
  return {
    ...actual,
    apiClient: {
      ...actual.apiClient,
      tailorResume: vi.fn(),
      getTailoredResumes: vi.fn(),
      getTailoredResumeById: vi.fn(),
      exportTailoredResume: vi.fn(),
    },
  };
});

const mockResumeListItem: TailoredResumeListItem = {
  id: 'tr-00000000-0000-0000-0000-000000000001',
  userId: 'u-00000000-0000-0000-0000-000000000001',
  jobId: 'j-00000000-0000-0000-0000-000000000001',
  jobTitle: 'Staff Backend Engineer',
  jobCompany: 'Stripe',
  title: 'Staff Backend Engineer - Stripe Tailored',
  atsScore: 94.5,
  keywordCoverage: 88.0,
  createdAt: '2026-09-27T12:00:00Z',
  updatedAt: '2026-09-27T12:00:00Z',
};

const mockTailoredResume: TailoredResume = {
  id: 'tr-00000000-0000-0000-0000-000000000001',
  userId: 'u-00000000-0000-0000-0000-000000000001',
  jobId: 'j-00000000-0000-0000-0000-000000000001',
  originalResumeId: 'r-00000000-0000-0000-0000-000000000001',
  title: 'Staff Backend Engineer - Stripe Tailored',
  summary: 'Staff Software Architect specialized in high-throughput distributed systems and FastAPI.',
  atsScore: 94.5,
  keywordCoverage: 88.0,
  createdAt: '2026-09-27T12:00:00Z',
  updatedAt: '2026-09-27T12:00:00Z',
  recommendations: ['Consider highlighting Docker experience if applicable.'],
  keywordAnalysis: {
    requiredSkills: ['Python', 'PostgreSQL', 'Distributed Systems'],
    preferredSkills: ['Redis', 'Docker'],
    technologies: ['FastAPI', 'PostgreSQL', 'Docker'],
    responsibilities: ['Architect microservices', 'Scale data layer'],
    keywords: ['Python', 'FastAPI', 'PostgreSQL', 'Redis'],
    matchedKeywords: ['Python', 'FastAPI', 'PostgreSQL'],
    missingKeywords: ['Docker'],
    coveragePercentage: 88.0,
  },
  atsBreakdown: {
    overallScore: 94.5,
    keywordMatch: 95.0,
    skillMatch: 92.0,
    sectionQuality: 94.0,
    experienceRelevance: 96.0,
    formattingStructure: 95.0,
    suggestions: ['Consider highlighting Docker experience if applicable.'],
  },
  versions: {
    ats: {
      versionType: 'ats',
      label: 'Version A: ATS Optimized',
      summary: 'ATS tailored summary focusing on distributed systems and Python.',
      skills: [{ category: 'Languages', skills: ['Python', 'TypeScript', 'SQL'] }],
      experience: [
        {
          role: 'Staff Engineer',
          company: 'TechCorp',
          description: 'Engineered scalable microservices.',
          bulletPoints: ['Engineered scalable microservices.'],
          highlightedKeywords: ['Python', 'Microservices'],
        },
      ],
      projects: [],
      education: [],
      certifications: [],
    },
    recruiter: {
      versionType: 'recruiter',
      label: 'Version B: Recruiter Optimized',
      summary: 'Impact-first summary emphasizing cross-functional leadership.',
      skills: [{ category: 'Languages', skills: ['Python', 'TypeScript'] }],
      experience: [],
      projects: [],
      education: [],
      certifications: [],
    },
    balanced: {
      versionType: 'balanced',
      label: 'Version C: Balanced',
      summary: 'Comprehensive engineering profile.',
      skills: [{ category: 'Languages', skills: ['Python', 'TypeScript'] }],
      experience: [],
      projects: [],
      education: [],
      certifications: [],
    },
  },
};

describe('useTailoredResumeStore', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useTailoredResumeStore.setState({
      resumes: [],
      selectedResume: null,
      selectedVersion: 'balanced',
      atsScore: null,
      keywordCoverage: null,
      loading: false,
      exporting: false,
      error: null,
    });
  });

  it('initializes with default empty state', () => {
    const state = useTailoredResumeStore.getState();
    expect(state.resumes).toEqual([]);
    expect(state.selectedResume).toBeNull();
    expect(state.selectedVersion).toBe('balanced');
    expect(state.atsScore).toBeNull();
    expect(state.keywordCoverage).toBeNull();
    expect(state.loading).toBe(false);
    expect(state.exporting).toBe(false);
    expect(state.error).toBeNull();
  });

  it('fetches tailored resumes successfully', async () => {
    vi.mocked(apiClient.getTailoredResumes).mockResolvedValueOnce({
      success: true,
      data: [mockResumeListItem],
      timestamp: '2026-09-27T12:00:00Z',
    });

    await useTailoredResumeStore.getState().fetchResumes();

    const state = useTailoredResumeStore.getState();
    expect(state.resumes).toHaveLength(1);
    expect(state.resumes[0].title).toBe('Staff Backend Engineer - Stripe Tailored');
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
  });

  it('handles error when fetching resumes fails', async () => {
    vi.mocked(apiClient.getTailoredResumes).mockRejectedValueOnce(
      new ApiClientError('Network disconnected', 503)
    );

    await useTailoredResumeStore.getState().fetchResumes();

    const state = useTailoredResumeStore.getState();
    expect(state.resumes).toEqual([]);
    expect(state.loading).toBe(false);
    expect(state.error).toBe('Network disconnected');
  });

  it('selects a resume by ID and loads full details', async () => {
    vi.mocked(apiClient.getTailoredResumeById).mockResolvedValueOnce({
      success: true,
      data: mockTailoredResume,
      timestamp: '2026-09-27T12:00:00Z',
    });

    await useTailoredResumeStore.getState().selectResumeById('tr-00000000-0000-0000-0000-000000000001');

    const state = useTailoredResumeStore.getState();
    expect(state.selectedResume).not.toBeNull();
    expect(state.selectedResume?.id).toBe(mockTailoredResume.id);
    expect(state.atsScore).toBe(94.5);
    expect(state.keywordCoverage).toBe(88.0);
    expect(state.loading).toBe(false);
  });

  it('handles error when selecting resume by ID fails', async () => {
    vi.mocked(apiClient.getTailoredResumeById).mockRejectedValueOnce(
      new ApiClientError('Resume not found', 404)
    );

    await useTailoredResumeStore.getState().selectResumeById('invalid-id');

    const state = useTailoredResumeStore.getState();
    expect(state.selectedResume).toBeNull();
    expect(state.loading).toBe(false);
    expect(state.error).toBe('Resume not found');
  });

  it('switches the active version view', () => {
    useTailoredResumeStore.getState().selectVersion('ats');
    expect(useTailoredResumeStore.getState().selectedVersion).toBe('ats');

    useTailoredResumeStore.getState().selectVersion('recruiter');
    expect(useTailoredResumeStore.getState().selectedVersion).toBe('recruiter');
  });

  it('generates a new tailored resume and prepends to list', async () => {
    vi.mocked(apiClient.tailorResume).mockResolvedValueOnce({
      success: true,
      data: mockTailoredResume,
      timestamp: '2026-09-27T12:00:00Z',
    });

    const result = await useTailoredResumeStore.getState().tailorResume({
      jobId: 'j-00000000-0000-0000-0000-000000000001',
      targetVersion: 'ats',
    });

    expect(result).not.toBeNull();
    expect(result?.id).toBe(mockTailoredResume.id);

    const state = useTailoredResumeStore.getState();
    expect(state.selectedResume?.id).toBe(mockTailoredResume.id);
    expect(state.resumes).toHaveLength(1);
    expect(state.selectedVersion).toBe('ats');
    expect(state.atsScore).toBe(94.5);
    expect(state.loading).toBe(false);
  });

  it('updates an existing tailored resume in list if regenerated', async () => {
    useTailoredResumeStore.setState({
      resumes: [mockResumeListItem],
    });

    const updatedResume = {
      ...mockTailoredResume,
      atsScore: 98.0,
      keywordCoverage: 95.0,
      updatedAt: '2026-09-27T13:00:00Z',
    };

    vi.mocked(apiClient.tailorResume).mockResolvedValueOnce({
      success: true,
      data: updatedResume,
      timestamp: '2026-09-27T12:00:00Z',
    });

    await useTailoredResumeStore.getState().tailorResume({
      jobId: 'j-00000000-0000-0000-0000-000000000001',
    });

    const state = useTailoredResumeStore.getState();
    expect(state.resumes).toHaveLength(1);
    expect(state.resumes[0].atsScore).toBe(98.0);
    expect(state.resumes[0].keywordCoverage).toBe(95.0);
  });

  it('handles failure when tailoring resume', async () => {
    vi.mocked(apiClient.tailorResume).mockRejectedValueOnce(
      new ApiClientError('AI generation limit exceeded', 429)
    );

    const result = await useTailoredResumeStore.getState().tailorResume({
      jobId: 'j-test',
    });

    expect(result).toBeNull();
    const state = useTailoredResumeStore.getState();
    expect(state.loading).toBe(false);
    expect(state.error).toBe('AI generation limit exceeded');
  });

  it('fails to export if no resume is selected', async () => {
    const res = await useTailoredResumeStore.getState().exportResume('pdf');
    expect(res).toBeNull();
    expect(useTailoredResumeStore.getState().error).toBe('No resume selected for export');
  });

  it('exports a resume document successfully', async () => {
    useTailoredResumeStore.setState({
      selectedResume: mockTailoredResume,
      selectedVersion: 'ats',
    });

    const mockBlob = new Blob(['%PDF-1.4 test'], { type: 'application/pdf' });
    vi.mocked(apiClient.exportTailoredResume).mockResolvedValueOnce({
      blob: mockBlob,
      filename: 'Resume_ATS.pdf',
    });

    // Mock DOM elements for download
    const createObjectURLMock = vi.fn().mockReturnValue('blob:http://localhost/mock-uuid');
    const revokeObjectURLMock = vi.fn();
    window.URL.createObjectURL = createObjectURLMock;
    window.URL.revokeObjectURL = revokeObjectURLMock;

    const res = await useTailoredResumeStore.getState().exportResume('pdf', 'ats');

    expect(res).toEqual({ filename: 'Resume_ATS.pdf' });
    expect(apiClient.exportTailoredResume).toHaveBeenCalledWith(
      mockTailoredResume.id,
      'pdf',
      'ats'
    );
    expect(createObjectURLMock).toHaveBeenCalledWith(mockBlob);
    expect(revokeObjectURLMock).toHaveBeenCalled();
    expect(useTailoredResumeStore.getState().exporting).toBe(false);
  });

  it('clears selection and errors accurately', () => {
    useTailoredResumeStore.setState({
      selectedResume: mockTailoredResume,
      atsScore: 90,
      keywordCoverage: 80,
      error: 'Some error',
    });

    useTailoredResumeStore.getState().clearError();
    expect(useTailoredResumeStore.getState().error).toBeNull();

    useTailoredResumeStore.getState().clearSelected();
    expect(useTailoredResumeStore.getState().selectedResume).toBeNull();
    expect(useTailoredResumeStore.getState().atsScore).toBeNull();
    expect(useTailoredResumeStore.getState().keywordCoverage).toBeNull();
  });
});
