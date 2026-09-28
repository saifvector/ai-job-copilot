'use client';

import * as React from 'react';
import Link from 'next/link';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/common/page-header';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useDashboardStore } from '@/store/dashboard-store';
import { useAnalyticsStore } from '@/store/analytics-store';
import {
  DashboardKpiCards,
  MatchInsightsTable,
  ProfileHealthCard,
  CareerReadinessCard,
  SkillGapWidget,
} from '@/features/dashboard';
import { MatchDistributionChart } from '@/features/analytics';
import {
  BarChart3,
  Compass,
  HeartPulse,
  RefreshCw,
  Sparkles,
  Target,
} from 'lucide-react';

export default function DashboardPage() {
  const {
    metrics,
    insights,
    profileHealth,
    careerReadiness,
    savedJobIds,
    loading,
    error,
    fetchDashboard,
    fetchProfileHealth,
    fetchCareerReadiness,
    toggleSaveJob,
  } = useDashboardStore();

  const { charts, skillGaps, fetchAnalytics, fetchSkillGaps } = useAnalyticsStore();

  React.useEffect(() => {
    fetchDashboard();
    fetchProfileHealth();
    fetchCareerReadiness();
    fetchAnalytics();
    fetchSkillGaps();
  }, [fetchDashboard, fetchProfileHealth, fetchCareerReadiness, fetchAnalytics, fetchSkillGaps]);

  const handleRefresh = async () => {
    await Promise.all([
      fetchDashboard(),
      fetchProfileHealth(),
      fetchCareerReadiness(),
      fetchAnalytics(),
      fetchSkillGaps(),
    ]);
  };

  return (
    <AppShell>
      <PageHeader
        title="Dashboard"
        description="Comprehensive career telemetry, top job matches, profile health, and market readiness."
        badge={
          <Badge variant="outline" className="font-mono text-xs">
            Phase 6 Analytics
          </Badge>
        }
        action={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={loading}
              className="h-8 gap-1.5 text-xs"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
              Refresh Telemetry
            </Button>
            <Link
              href="/analytics"
              className="inline-flex items-center justify-center rounded-md text-xs font-medium h-8 px-3 bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              <BarChart3 className="h-3.5 w-3.5 mr-1.5" />
              Interactive Analytics
            </Link>
          </div>
        }
      />

      <div className="space-y-6">
        {/* Error notification banner if any */}
        {error && (
          <Card className="border-rose-500/20 bg-rose-500/5">
            <CardContent className="p-4 flex items-center justify-between text-xs text-rose-500">
              <span>{error}</span>
              <Button variant="ghost" size="sm" onClick={handleRefresh} className="h-7 text-xs">
                Retry
              </Button>
            </CardContent>
          </Card>
        )}

        {/* 1. Dashboard KPI Cards (7 Core Summary Cards) */}
        <DashboardKpiCards metrics={metrics} loading={loading} />

        {/* 2. Profile Health & Career Readiness twin columns */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ProfileHealthCard data={profileHealth} loading={loading} />
          <CareerReadinessCard data={careerReadiness} loading={loading} />
        </div>

        {/* 3. Match Insights (Top 10 Opportunities) */}
        <MatchInsightsTable
          matches={insights}
          savedJobIds={savedJobIds}
          onToggleSave={toggleSaveJob}
          loading={loading}
        />

        {/* 4. Match Distribution & Skill Gap Intelligence */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <MatchDistributionChart data={charts?.matchDistribution || null} loading={loading} />
          </div>
          <div className="lg:col-span-2">
            <SkillGapWidget data={skillGaps} loading={loading} />
          </div>
        </div>

        {/* Workspace Quick Links banner */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
          <Link
            href="/matching"
            className="p-4 rounded-xl border border-border/70 bg-card/40 hover:bg-card/80 transition-colors flex items-center gap-3.5 group"
          >
            <div className="p-2.5 rounded-lg bg-primary/10 text-primary group-hover:scale-105 transition-transform">
              <Target className="h-5 w-5" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-foreground">AI Job Matching</h4>
              <p className="text-xs text-muted-foreground">Run batch comparisons and custom score filters</p>
            </div>
          </Link>

          <Link
            href="/profile-health"
            className="p-4 rounded-xl border border-border/70 bg-card/40 hover:bg-card/80 transition-colors flex items-center gap-3.5 group"
          >
            <div className="p-2.5 rounded-lg bg-rose-500/10 text-rose-500 group-hover:scale-105 transition-transform">
              <HeartPulse className="h-5 w-5" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-foreground">Profile Health Audit</h4>
              <p className="text-xs text-muted-foreground">Examine 4-pillar scores and actionable checklist</p>
            </div>
          </Link>

          <Link
            href="/insights"
            className="p-4 rounded-xl border border-border/70 bg-card/40 hover:bg-card/80 transition-colors flex items-center gap-3.5 group"
          >
            <div className="p-2.5 rounded-lg bg-cyan-500/10 text-cyan-500 group-hover:scale-105 transition-transform">
              <Compass className="h-5 w-5" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-foreground">Match Insights & Gaps</h4>
              <p className="text-xs text-muted-foreground">Inspect market skills and saved opportunities</p>
            </div>
          </Link>
        </div>
      </div>
    </AppShell>
  );
}
