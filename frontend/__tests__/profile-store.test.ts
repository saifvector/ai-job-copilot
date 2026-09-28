import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useProfileStore } from '../store/profile-store';
import { apiClient, ApiClientError } from '../services/api-client';
import type { ResumeParseResponse } from '../types/resume-intelligence';

vi.mock('../services/api-client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../services/api-client')>();
  return {
    ...actual,
    apiClient: {
      ...actual.apiClient,
      parseResume: vi.fn(),
      getFullProfileIntelligence: vi.fn(),
      getProfileSummary: vi.fn(),
      getProfileSkills: vi.fn(),
      getProfileProjects: vi.fn(),
    },
  };
});

const mockParseResponse: ResumeParseResponse = {
  userId: 'u-12345678-0000-0000-0000-000000000001',
  candidate: {
    name: 'Alex Rivera',
    email: 'alex.rivera@example.com',
    phone: '+1 (555) 345-6789',
  },
  summary: 'Staff Software Architect specializing in AI Agents and Distributed Systems.',
  skills: [
    {
      id: 's-1',
      userId: 'u-12345678-0000-0000-0000-000000000001',
      name: 'Python',
      category: 'Programming Language',
      confidenceScore: 0.98,
      createdAt: '2026-09-27T10:00:00Z',
    },
    {
      id: 's-2',
      userId: 'u-12345678-0000-0000-0000-000000000001',
      name: 'FastAPI',
      category: 'Framework',
      confidenceScore: 0.95,
      createdAt: '2026-09-27T10:00:00Z',
    },
  ],
  projects: [
    {
      id: 'p-1',
      userId: 'u-12345678-0000-0000-0000-000000000001',
      title: 'AI Resume Intelligence Platform',
      description: 'Distributed document ingestion pipeline leveraging Gemini models.',
      technologies: ['FastAPI', 'Gemini', 'PostgreSQL', 'Next.js'],
      createdAt: '2026-09-27T10:00:00Z',
    },
  ],
  education: [
    {
      id: 'e-1',
      userId: 'u-12345678-0000-0000-0000-000000000001',
      institution: 'Stanford University',
      degree: 'M.S.',
      fieldOfStudy: 'Computer Science',
      startDate: '2019-09',
      endDate: '2021-06',
      createdAt: '2026-09-27T10:00:00Z',
    },
  ],
  experience: [
    {
      id: 'exp-1',
      userId: 'u-12345678-0000-0000-0000-000000000001',
      company: 'Tech Innovations Corp',
      role: 'Lead AI Engineer',
      description: 'Architected high-throughput inference engines and microservices.',
      startDate: '2021-07',
      endDate: 'Present',
      createdAt: '2026-09-27T10:00:00Z',
    },
  ],
  certifications: [
    {
      id: 'c-1',
      userId: 'u-12345678-0000-0000-0000-000000000001',
      name: 'Google Cloud Professional Cloud Architect',
      issuer: 'Google Cloud',
      issueDate: '2023-04',
      createdAt: '2026-09-27T10:00:00Z',
    },
  ],

  modelUsed: 'gemini-2.5-pro',
  parsedAt: '2026-09-27T10:00:00Z',
};

describe('useProfileStore', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useProfileStore.setState({
      profile: null,
      skills: [],
      projects: [],
      education: [],
      experience: [],
      certifications: [],
      loading: false,
      error: null,
      modelUsed: null,
      parsedAt: null,
    });
  });

  it('initializes with default empty candidate profile state', () => {
    const state = useProfileStore.getState();
    expect(state.profile).toBeNull();
    expect(state.skills).toEqual([]);
    expect(state.projects).toEqual([]);
    expect(state.education).toEqual([]);
    expect(state.experience).toEqual([]);
    expect(state.certifications).toEqual([]);
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
  });

  it('parses resume successfully and populates store', async () => {
    vi.mocked(apiClient.parseResume).mockResolvedValueOnce({
      success: true,
      data: mockParseResponse,
      timestamp: '2026-09-27T10:00:00Z',
    });

    const success = await useProfileStore.getState().parseResume('test-resume-id');

    expect(success).toBe(true);
    const state = useProfileStore.getState();
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
    expect(state.profile?.contact.name).toBe('Alex Rivera');
    expect(state.profile?.summary).toContain('Staff Software Architect');
    expect(state.skills.length).toBe(2);
    expect(state.projects.length).toBe(1);
    expect(state.experience.length).toBe(1);
    expect(state.education.length).toBe(1);
    expect(state.certifications.length).toBe(1);
    expect(state.modelUsed).toBe('gemini-2.5-pro');
    expect(apiClient.parseResume).toHaveBeenCalledWith('test-resume-id');
  });

  it('handles parsing errors gracefully and sets error state', async () => {
    const error = new ApiClientError('AI service rate limit exceeded', 503, 'AI_TIMEOUT');
    vi.mocked(apiClient.parseResume).mockRejectedValueOnce(error);

    const success = await useProfileStore.getState().parseResume();

    expect(success).toBe(false);
    const state = useProfileStore.getState();
    expect(state.loading).toBe(false);
    expect(state.error).toBe('AI service rate limit exceeded');
  });

  it('fetches full profile intelligence cleanly', async () => {
    vi.mocked(apiClient.getFullProfileIntelligence).mockResolvedValueOnce({
      success: true,
      data: mockParseResponse,
      timestamp: '2026-09-27T10:00:00Z',
    });

    await useProfileStore.getState().fetchProfile();

    const state = useProfileStore.getState();
    expect(state.loading).toBe(false);
    expect(state.profile?.contact.email).toBe('alex.rivera@example.com');
    expect(state.skills.length).toBe(2);
    expect(apiClient.getFullProfileIntelligence).toHaveBeenCalledTimes(1);
  });

  it('handles 404 when profile intelligence not yet generated', async () => {
    const notFound = new ApiClientError('Candidate intelligence not found', 404, 'RESOURCE_NOT_FOUND');
    vi.mocked(apiClient.getFullProfileIntelligence).mockRejectedValueOnce(notFound);

    await useProfileStore.getState().fetchProfile();

    const state = useProfileStore.getState();
    expect(state.loading).toBe(false);
    expect(state.error).toBeNull();
    expect(state.profile).toBeNull();
  });

  it('resets error and clears profile state', () => {
    useProfileStore.setState({
      profile: {
        contact: mockParseResponse.candidate,
        summary: mockParseResponse.summary,
        userId: mockParseResponse.userId,
      },
      skills: mockParseResponse.skills,
      error: 'Previous transient error',
    });

    useProfileStore.getState().resetError();
    expect(useProfileStore.getState().error).toBeNull();

    useProfileStore.getState().clearProfile();
    expect(useProfileStore.getState().profile).toBeNull();
    expect(useProfileStore.getState().skills).toEqual([]);
  });
});
