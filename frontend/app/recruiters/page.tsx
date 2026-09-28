'use client';

import React, { useEffect, useState } from 'react';
import { PageHeader } from '@/components/common/page-header';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useRecruiterStore } from '@/store';
import {
  NetworkingAnalyticsHeader,
  RecruiterCard,
  CreateRecruiterModal,
  AddInteractionModal,
  AddReferralModal,
  RecruiterDetailModal,
} from '@/features/recruiters';
import {
  Users,
  Plus,
  RefreshCw,
  Search,
  Building2,
  AlertCircle,
  CheckCircle2,
  Sparkles,
  ArrowRight,
} from 'lucide-react';
import {
  CreateInteractionPayload,
  CreateRecruiterPayload,
  CreateReferralPayload,
  Recruiter,
} from '@/types';
import Link from 'next/link';

export default function RecruitersPage() {
  const {
    recruiters,
    selectedRecruiter,
    analytics,
    companies,
    totalRecruiters,
    loading,
    analyticsLoading,
    error,
    fetchRecruiters,
    selectRecruiterById,
    createRecruiter,
    updateRecruiter,
    deleteRecruiter,
    addInteraction,
    addReferral,
    fetchAnalytics,
    clearSelected,
    clearError,
  } = useRecruiterStore();

  const [search, setSearch] = useState('');
  const [selectedCompany, setSelectedCompany] = useState<string>('ALL');

  // Modals state
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [isInteractionOpen, setIsInteractionOpen] = useState(false);
  const [isReferralOpen, setIsReferralOpen] = useState(false);
  const [modalTargetRecruiter, setModalTargetRecruiter] = useState<Recruiter | null>(null);

  const [notification, setNotification] = useState<string | null>(null);

  useEffect(() => {
    fetchRecruiters();
    fetchAnalytics();
  }, [fetchRecruiters, fetchAnalytics]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setSearch(val);
    fetchRecruiters({
      search: val || undefined,
      company: selectedCompany !== 'ALL' ? selectedCompany : undefined,
    });
  };

  const handleCompanyChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setSelectedCompany(val);
    fetchRecruiters({
      search: search || undefined,
      company: val !== 'ALL' ? val : undefined,
    });
  };

  const handleRefresh = () => {
    fetchRecruiters({
      search: search || undefined,
      company: selectedCompany !== 'ALL' ? selectedCompany : undefined,
    });
    fetchAnalytics();
  };

  const handleSelectRecruiter = async (recruiter: Recruiter) => {
    const full = await selectRecruiterById(recruiter.id);
    if (full) {
      setIsDetailOpen(true);
    }
  };

  const handleOpenInteractionModal = (recruiter: Recruiter) => {
    setModalTargetRecruiter(recruiter);
    setIsInteractionOpen(true);
  };

  const handleOpenReferralModal = (recruiter: Recruiter) => {
    setModalTargetRecruiter(recruiter);
    setIsReferralOpen(true);
  };

  const handleCreateSubmit = async (payload: CreateRecruiterPayload) => {
    const created = await createRecruiter(payload);
    if (created) {
      setNotification(`Added "${created.name}" at ${created.company} to your CRM.`);
      setTimeout(() => setNotification(null), 5000);
      return created;
    }
    return null;
  };

  const handleInteractionSubmit = async (
    recruiterId: string,
    payload: CreateInteractionPayload
  ) => {
    const res = await addInteraction(recruiterId, payload);
    if (res) {
      setNotification(`Touchpoint recorded with ${modalTargetRecruiter?.name || 'recruiter'}.`);
      setTimeout(() => setNotification(null), 5000);
      return res;
    }
    return null;
  };

  const handleReferralSubmit = async (
    recruiterId: string,
    payload: CreateReferralPayload
  ) => {
    const res = await addReferral(recruiterId, payload);
    if (res) {
      setNotification(`Referral request logged for ${payload.role} at ${payload.company}.`);
      setTimeout(() => setNotification(null), 5000);
      return res;
    }
    return null;
  };

  const handleDeleteRecruiter = async (id: string) => {
    const ok = await deleteRecruiter(id);
    if (ok) {
      setNotification('Recruiter successfully removed from network.');
      setTimeout(() => setNotification(null), 5000);
    }
    return ok;
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Recruiter CRM & Networking"
        description="Organize recruiters, hiring managers, and professional contacts. Track outreach touchpoints, response metrics, and internal job referrals."
        badge={
          <Badge
            variant="outline"
            className="border-primary/40 bg-primary/10 text-primary font-medium"
          >
            <Users className="w-3.5 h-3.5 mr-1 text-primary" />
            Phase 10: Networking CRM
          </Badge>
        }
        action={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={loading}
              className="text-xs h-8 gap-1.5"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </Button>

            <Link href="/referrals">
              <Button
                variant="outline"
                size="sm"
                className="text-xs h-8 gap-1.5 border-purple-500/40 text-purple-400 hover:bg-purple-500/10"
              >
                <span>Referral Tracker</span>
                <ArrowRight className="w-3 h-3" />
              </Button>
            </Link>

            <Button
              size="sm"
              onClick={() => setIsCreateOpen(true)}
              className="text-xs h-8 gap-1.5 shadow-sm bg-primary hover:bg-primary/90 text-primary-foreground font-medium"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Recruiter</span>
            </Button>
          </div>
        }
      />

      {/* Notifications */}
      {notification && (
        <div className="flex items-center justify-between p-3.5 rounded-lg border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 text-sm animate-fade-in">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-400 flex-shrink-0" />
            <span>{notification}</span>
          </div>
          <button
            onClick={() => setNotification(null)}
            className="text-xs underline hover:opacity-80"
          >
            Dismiss
          </button>
        </div>
      )}

      {error && (
        <div className="flex items-center justify-between p-3.5 rounded-lg border border-rose-500/30 bg-rose-500/10 text-rose-400 text-sm animate-fade-in">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-rose-400 flex-shrink-0" />
            <span>{error}</span>
          </div>
          <button
            onClick={clearError}
            className="text-xs underline hover:opacity-80"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Analytics KPI Header */}
      <NetworkingAnalyticsHeader analytics={analytics} loading={analyticsLoading} />

      {/* Search & Filter Toolbar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 p-3 rounded-xl border border-border/60 bg-card/80 backdrop-blur-sm">
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
          <Input
            value={search}
            onChange={handleSearchChange}
            placeholder="Search by name, company, title..."
            className="pl-9 text-xs h-9 bg-background/50 border-border/70"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Building2 className="h-3.5 w-3.5" />
            <span>Company:</span>
          </div>
          <select
            value={selectedCompany}
            onChange={handleCompanyChange}
            className="text-xs h-9 rounded-md border border-border/70 bg-background/50 px-2.5 text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option value="ALL">All Companies ({companies.length})</option>
            {companies.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Recruiters Cards Grid */}
      {recruiters.length === 0 ? (
        <div className="text-center py-16 px-4 border border-dashed border-border/60 rounded-xl bg-muted/10 space-y-3">
          <div className="p-3 rounded-full bg-primary/10 text-primary w-fit mx-auto border border-primary/20">
            <Users className="h-6 w-6" />
          </div>
          <div className="space-y-1">
            <h3 className="text-sm font-bold text-foreground">
              {search || selectedCompany !== 'ALL'
                ? 'No recruiters match your search filters'
                : 'No recruiters or contacts registered yet'}
            </h3>
            <p className="text-xs text-muted-foreground max-w-sm mx-auto">
              Start building your professional CRM to log conversation history, follow-ups, and track job referrals.
            </p>
          </div>
          <Button
            size="sm"
            onClick={() => setIsCreateOpen(true)}
            className="text-xs h-8 bg-primary hover:bg-primary/90 text-primary-foreground font-medium"
          >
            <Plus className="h-3.5 w-3.5 mr-1" />
            <span>Add First Contact</span>
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {recruiters.map((recruiter) => (
            <RecruiterCard
              key={recruiter.id}
              recruiter={recruiter}
              onSelect={handleSelectRecruiter}
              onAddInteraction={handleOpenInteractionModal}
              onAddReferral={handleOpenReferralModal}
            />
          ))}
        </div>
      )}

      {/* Modals */}
      <CreateRecruiterModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onSubmit={handleCreateSubmit}
        loading={loading}
      />

      <RecruiterDetailModal
        recruiter={selectedRecruiter}
        isOpen={isDetailOpen}
        onClose={() => {
          setIsDetailOpen(false);
          clearSelected();
        }}
        onAddInteraction={handleOpenInteractionModal}
        onAddReferral={handleOpenReferralModal}
        onDeleteRecruiter={handleDeleteRecruiter}
      />

      <AddInteractionModal
        recruiter={modalTargetRecruiter}
        isOpen={isInteractionOpen}
        onClose={() => {
          setIsInteractionOpen(false);
          setModalTargetRecruiter(null);
        }}
        onSubmit={handleInteractionSubmit}
      />

      <AddReferralModal
        recruiter={modalTargetRecruiter}
        isOpen={isReferralOpen}
        onClose={() => {
          setIsReferralOpen(false);
          setModalTargetRecruiter(null);
        }}
        onSubmit={handleReferralSubmit}
      />
    </div>
  );
}
