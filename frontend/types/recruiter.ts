export type InteractionType =
  | 'Message'
  | 'Email'
  | 'Referral'
  | 'Call'
  | 'Interview';

export type ReferralStatus =
  | 'Requested'
  | 'Received'
  | 'Declined'
  | 'Pending';

export interface ContactInteraction {
  id: string;
  recruiterId: string;
  interactionType: InteractionType;
  summary: string;
  interactionDate: string;
  createdAt: string;
}

export interface Referral {
  id: string;
  recruiterId: string;
  company: string;
  role: string;
  status: ReferralStatus;
  notes?: string | null;
  createdAt: string;
  updatedAt: string;
  recruiterName?: string | null;
}

export interface Recruiter {
  id: string;
  userId: string;
  name: string;
  company: string;
  title?: string | null;
  email?: string | null;
  linkedinUrl?: string | null;
  notes?: string | null;
  interactionCount: number;
  referralCount: number;
  lastInteractionDate?: string | null;
  createdAt: string;
  updatedAt: string;
  interactions?: ContactInteraction[];
  referrals?: Referral[];
}

export interface NetworkingAnalytics {
  recruitersContacted: number;
  responseRate: number;
  referralSuccessRate: number;
  companiesReached: number;
  messagesSent: number;
  responsesReceived: number;
  referralsRequested: number;
  referralsReceived: number;
  interactionsByType: Record<string, number>;
  referralsByStatus: Record<string, number>;
}

export interface CreateRecruiterPayload {
  name: string;
  company: string;
  title?: string;
  email?: string;
  linkedinUrl?: string;
  notes?: string;
}

export interface UpdateRecruiterPayload {
  name?: string;
  company?: string;
  title?: string;
  email?: string;
  linkedinUrl?: string;
  notes?: string;
}

export interface CreateInteractionPayload {
  interactionType: InteractionType;
  summary: string;
  interactionDate?: string;
}

export interface CreateReferralPayload {
  company: string;
  role: string;
  status?: ReferralStatus;
  notes?: string;
}

export interface UpdateReferralPayload {
  company?: string;
  role?: string;
  status?: ReferralStatus;
  notes?: string;
}

export interface RecruiterListData {
  recruiters: Recruiter[];
  total: number;
  companies: string[];
}
