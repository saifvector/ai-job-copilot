import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useRecruiterStore } from '../store/recruiter-store';
import { apiClient, ApiClientError } from '../services/api-client';
import type {
  ContactInteraction,
  NetworkingAnalytics,
  Recruiter,
  Referral,
} from '../types/recruiter';

vi.mock('../services/api-client', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../services/api-client')>();
  return {
    ...actual,
    apiClient: {
      ...actual.apiClient,
      getRecruiters: vi.fn(),
      getRecruiterById: vi.fn(),
      createRecruiter: vi.fn(),
      updateRecruiter: vi.fn(),
      deleteRecruiter: vi.fn(),
      addInteraction: vi.fn(),
      getRecruiterHistory: vi.fn(),
      addReferral: vi.fn(),
      getReferrals: vi.fn(),
      updateReferral: vi.fn(),
      deleteReferral: vi.fn(),
      getNetworkingAnalytics: vi.fn(),
    },
  };
});

const mockRecruiter: Recruiter = {
  id: 'rec-00000000-0000-0000-0000-000000000001',
  userId: 'u-00000000-0000-0000-0000-000000000001',
  name: 'Sarah Jenkins',
  company: 'Stripe',
  title: 'Lead Technical Recruiter',
  email: 'sjenkins@stripe.com',
  linkedinUrl: 'https://linkedin.com/in/sarahjenkins',
  notes: 'Met at Bay Area Tech Summit',
  interactionCount: 2,
  referralCount: 1,
  lastInteractionDate: '2026-09-27T12:00:00Z',
  createdAt: '2026-09-20T12:00:00Z',
  updatedAt: '2026-09-27T12:00:00Z',
  interactions: [],
  referrals: [],
};

const mockInteraction: ContactInteraction = {
  id: 'int-00000000-0000-0000-0000-000000000001',
  recruiterId: mockRecruiter.id,
  interactionType: 'Message',
  summary: 'Inquired about open Staff Backend roles',
  interactionDate: '2026-09-27T12:00:00Z',
  createdAt: '2026-09-27T12:00:00Z',
};

const mockReferral: Referral = {
  id: 'ref-00000000-0000-0000-0000-000000000001',
  recruiterId: mockRecruiter.id,
  company: 'Stripe',
  role: 'Staff Infrastructure Engineer',
  status: 'Requested',
  notes: 'Submitted resume via internal portal',
  createdAt: '2026-09-27T12:00:00Z',
  updatedAt: '2026-09-27T12:00:00Z',
  recruiterName: 'Sarah Jenkins',
};

const mockAnalytics: NetworkingAnalytics = {
  recruitersContacted: 5,
  responseRate: 40.0,
  referralSuccessRate: 50.0,
  companiesReached: 4,
  messagesSent: 10,
  responsesReceived: 4,
  referralsRequested: 2,
  referralsReceived: 1,
  interactionsByType: { Message: 6, Email: 4, Call: 2 },
  referralsByStatus: { Requested: 1, Received: 1 },
};

describe('useRecruiterStore', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    useRecruiterStore.setState({
      recruiters: [],
      selectedRecruiter: null,
      referrals: [],
      interactions: [],
      analytics: null,
      companies: [],
      totalRecruiters: 0,
      loading: false,
      analyticsLoading: false,
      error: null,
    });
  });

  describe('fetchRecruiters', () => {
    it('successfully fetches and normalizes recruiters', async () => {
      vi.mocked(apiClient.getRecruiters).mockResolvedValueOnce({
        success: true,
        data: {
          recruiters: [mockRecruiter as any],
          total: 1,
          companies: ['Stripe'],
        },
        timestamp: '2026-09-27T12:00:00Z',
      });

      await useRecruiterStore.getState().fetchRecruiters();

      const state = useRecruiterStore.getState();
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
      expect(state.recruiters).toHaveLength(1);
      expect(state.recruiters[0].name).toBe('Sarah Jenkins');
      expect(state.companies).toEqual(['Stripe']);
      expect(state.totalRecruiters).toBe(1);
    });

    it('handles api errors gracefully', async () => {
      vi.mocked(apiClient.getRecruiters).mockRejectedValueOnce(
        new ApiClientError('Network Error', 503)
      );

      await useRecruiterStore.getState().fetchRecruiters();

      const state = useRecruiterStore.getState();
      expect(state.loading).toBe(false);
      expect(state.error).toBe('Network Error');
    });
  });

  describe('createRecruiter', () => {
    it('successfully creates a recruiter and updates analytics', async () => {
      vi.mocked(apiClient.createRecruiter).mockResolvedValueOnce({
        success: true,
        data: mockRecruiter as any,
        timestamp: '2026-09-27T12:00:00Z',
      });
      vi.mocked(apiClient.getNetworkingAnalytics).mockResolvedValueOnce({
        success: true,
        data: mockAnalytics as any,
        timestamp: '2026-09-27T12:00:00Z',
      });

      const res = await useRecruiterStore.getState().createRecruiter({
        name: 'Sarah Jenkins',
        company: 'Stripe',
      });

      expect(res).not.toBeNull();
      expect(res?.id).toBe(mockRecruiter.id);
      const state = useRecruiterStore.getState();
      expect(state.recruiters).toHaveLength(1);
      expect(state.totalRecruiters).toBe(1);
    });
  });

  describe('updateRecruiter', () => {
    it('updates recruiter attributes in store', async () => {
      useRecruiterStore.setState({ recruiters: [mockRecruiter] });

      const updatedRecruiter = { ...mockRecruiter, title: 'VP Talent' };
      vi.mocked(apiClient.updateRecruiter).mockResolvedValueOnce({
        success: true,
        data: updatedRecruiter as any,
        timestamp: '2026-09-27T12:00:00Z',
      });

      const res = await useRecruiterStore.getState().updateRecruiter(mockRecruiter.id, {
        title: 'VP Talent',
      });

      expect(res?.title).toBe('VP Talent');
      expect(useRecruiterStore.getState().recruiters[0].title).toBe('VP Talent');
    });
  });

  describe('deleteRecruiter', () => {
    it('deletes recruiter from store', async () => {
      useRecruiterStore.setState({
        recruiters: [mockRecruiter],
        totalRecruiters: 1,
      });

      vi.mocked(apiClient.deleteRecruiter).mockResolvedValueOnce({
        success: true,
        data: true,
        timestamp: '2026-09-27T12:00:00Z',
      });
      vi.mocked(apiClient.getNetworkingAnalytics).mockResolvedValueOnce({
        success: true,
        data: mockAnalytics as any,
        timestamp: '2026-09-27T12:00:00Z',
      });

      const ok = await useRecruiterStore.getState().deleteRecruiter(mockRecruiter.id);
      expect(ok).toBe(true);
      expect(useRecruiterStore.getState().recruiters).toHaveLength(0);
      expect(useRecruiterStore.getState().totalRecruiters).toBe(0);
    });
  });

  describe('addInteraction', () => {
    it('records touchpoint and updates interactionCount on recruiter', async () => {
      useRecruiterStore.setState({
        recruiters: [mockRecruiter],
        selectedRecruiter: mockRecruiter,
      });

      vi.mocked(apiClient.addInteraction).mockResolvedValueOnce({
        success: true,
        data: mockInteraction as any,
        timestamp: '2026-09-27T12:00:00Z',
      });
      vi.mocked(apiClient.getNetworkingAnalytics).mockResolvedValueOnce({
        success: true,
        data: mockAnalytics as any,
        timestamp: '2026-09-27T12:00:00Z',
      });

      const res = await useRecruiterStore.getState().addInteraction(mockRecruiter.id, {
        interactionType: 'Message',
        summary: 'Inquired about open Staff Backend roles',
      });

      expect(res).not.toBeNull();
      const state = useRecruiterStore.getState();
      expect(state.interactions).toHaveLength(1);
      expect(state.recruiters[0].interactionCount).toBe(3);
    });
  });

  describe('referrals workflow', () => {
    it('adds referral and increments referralCount', async () => {
      useRecruiterStore.setState({
        recruiters: [mockRecruiter],
      });

      vi.mocked(apiClient.addReferral).mockResolvedValueOnce({
        success: true,
        data: mockReferral as any,
        timestamp: '2026-09-27T12:00:00Z',
      });
      vi.mocked(apiClient.getNetworkingAnalytics).mockResolvedValueOnce({
        success: true,
        data: mockAnalytics as any,
        timestamp: '2026-09-27T12:00:00Z',
      });

      const res = await useRecruiterStore.getState().addReferral(mockRecruiter.id, {
        company: 'Stripe',
        role: 'Staff Infrastructure Engineer',
      });

      expect(res).not.toBeNull();
      const state = useRecruiterStore.getState();
      expect(state.referrals).toHaveLength(1);
      expect(state.recruiters[0].referralCount).toBe(2);
    });

    it('updates referral status in store', async () => {
      useRecruiterStore.setState({ referrals: [mockReferral] });

      const updated = { ...mockReferral, status: 'Received' as const };
      vi.mocked(apiClient.updateReferral).mockResolvedValueOnce({
        success: true,
        data: updated as any,
        timestamp: '2026-09-27T12:00:00Z',
      });
      vi.mocked(apiClient.getNetworkingAnalytics).mockResolvedValueOnce({
        success: true,
        data: mockAnalytics as any,
        timestamp: '2026-09-27T12:00:00Z',
      });

      const res = await useRecruiterStore.getState().updateReferral(mockReferral.id, {
        status: 'Received',
      });

      expect(res?.status).toBe('Received');
      expect(useRecruiterStore.getState().referrals[0].status).toBe('Received');
    });
  });

  describe('fetchAnalytics', () => {
    it('populates networking analytics correctly', async () => {
      vi.mocked(apiClient.getNetworkingAnalytics).mockResolvedValueOnce({
        success: true,
        data: mockAnalytics as any,
        timestamp: '2026-09-27T12:00:00Z',
      });

      await useRecruiterStore.getState().fetchAnalytics();

      const state = useRecruiterStore.getState();
      expect(state.analytics).not.toBeNull();
      expect(state.analytics?.recruitersContacted).toBe(5);
      expect(state.analytics?.responseRate).toBe(40.0);
      expect(state.analytics?.referralSuccessRate).toBe(50.0);
    });
  });
});
