'use client';

import React, { useEffect, useState } from 'react';
import { PageHeader } from '@/components/common/page-header';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useRecruiterStore } from '@/store';
import { ReferralBoard } from '@/features/recruiters';
import {
  Award,
  RefreshCw,
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  Clock,
  Building2,
  Users,
} from 'lucide-react';
import { ReferralStatus } from '@/types';
import Link from 'next/link';

export default function ReferralsPage() {
  const {
    referrals,
    analytics,
    loading,
    analyticsLoading,
    error,
    fetchReferrals,
    updateReferral,
    deleteReferral,
    fetchAnalytics,
    clearError,
  } = useRecruiterStore();

  const [notification, setNotification] = useState<string | null>(null);

  useEffect(() => {
    fetchReferrals();
    fetchAnalytics();
  }, [fetchReferrals, fetchAnalytics]);

  const handleRefresh = () => {
    fetchReferrals();
    fetchAnalytics();
  };

  const handleStatusChange = async (id: string, newStatus: ReferralStatus) => {
    const updated = await updateReferral(id, { status: newStatus });
    if (updated) {
      setNotification(`Referral status updated to "${newStatus}".`);
      setTimeout(() => setNotification(null), 4000);
    }
  };

  const handleDeleteReferral = async (id: string) => {
    const ok = await deleteReferral(id);
    if (ok) {
      setNotification('Referral successfully removed.');
      setTimeout(() => setNotification(null), 4000);
    }
    return ok;
  };

  const requestedCount = referrals.filter((r) => r.status.toLowerCase() === 'requested').length;
  const pendingCount = referrals.filter((r) => r.status.toLowerCase() === 'pending').length;
  const receivedCount = referrals.filter((r) => r.status.toLowerCase() === 'received').length;
  const declinedCount = referrals.filter((r) => r.status.toLowerCase() === 'declined').length;
  const totalCount = referrals.length;
  const successRate = totalCount > 0 ? Math.round((receivedCount / totalCount) * 100) : 0;

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Job Referral Tracker"
        description="Monitor internal employee endorsements and recruiter referrals from initial request through portal confirmation and interview stages."
        badge={
          <Badge
            variant="outline"
            className="border-purple-500/40 bg-purple-500/10 text-purple-400 font-medium"
          >
            <Award className="w-3.5 h-3.5 mr-1 text-purple-400" />
            Phase 10: Referral Engine
          </Badge>
        }
        action={
          <div className="flex items-center gap-2">
            <Link href="/recruiters">
              <Button
                variant="outline"
                size="sm"
                className="text-xs h-8 gap-1.5"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Recruiter Directory</span>
              </Button>
            </Link>

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

      {/* Referral KPI Highlights */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <Card className="p-3.5 rounded-xl border border-border/60 bg-card space-y-1">
          <span className="text-xs text-muted-foreground font-medium flex items-center gap-1.5">
            <Award className="h-3.5 w-3.5 text-purple-500" />
            <span>Total Referrals</span>
          </span>
          <div className="text-2xl font-bold text-foreground">{totalCount}</div>
          <p className="text-[11px] text-muted-foreground">Across all corporate contacts</p>
        </Card>

        <Card className="p-3.5 rounded-xl border border-border/60 bg-card space-y-1">
          <span className="text-xs text-muted-foreground font-medium flex items-center gap-1.5">
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
            <span>Received / Endorsed</span>
          </span>
          <div className="text-2xl font-bold text-emerald-400">{receivedCount}</div>
          <p className="text-[11px] text-emerald-500/80 font-medium">{successRate}% endorsement rate</p>
        </Card>

        <Card className="p-3.5 rounded-xl border border-border/60 bg-card space-y-1">
          <span className="text-xs text-muted-foreground font-medium flex items-center gap-1.5">
            <Clock className="h-3.5 w-3.5 text-amber-500" />
            <span>Pending Review</span>
          </span>
          <div className="text-2xl font-bold text-amber-400">{pendingCount}</div>
          <p className="text-[11px] text-muted-foreground">Awaiting recruiter action</p>
        </Card>

        <Card className="p-3.5 rounded-xl border border-border/60 bg-card space-y-1">
          <span className="text-xs text-muted-foreground font-medium flex items-center gap-1.5">
            <Users className="h-3.5 w-3.5 text-blue-500" />
            <span>Requested</span>
          </span>
          <div className="text-2xl font-bold text-blue-400">{requestedCount}</div>
          <p className="text-[11px] text-muted-foreground">Initial outreach queued</p>
        </Card>
      </div>

      {/* Referral Pipeline Board */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold tracking-tight text-foreground flex items-center gap-2">
            <Award className="h-4 w-4 text-purple-400" />
            <span>Referral Status Pipeline</span>
          </h3>
          <span className="text-xs text-muted-foreground">
            Advance referral statuses as responses are confirmed
          </span>
        </div>

        <ReferralBoard
          referrals={referrals}
          loading={loading}
          onUpdateStatus={handleStatusChange}
          onDeleteReferral={handleDeleteReferral}
        />
      </div>
    </div>
  );
}
