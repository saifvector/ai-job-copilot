'use client';

import * as React from 'react';
import Link from 'next/link';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/common/page-header';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useAnalyticsStore } from '@/store/analytics-store';
import {
  MatchDistributionChart,
  SkillDemandChart,
  MissingSkillsChart,
  LocationDistributionChart,
  ProfileProgressChart,
} from '@/features/analytics';
import {
  BarChart3,
  Calendar,
  Clock,
  Compass,
  LayoutDashboard,
  RefreshCw,
  Sparkles,
} from 'lucide-react';

export default function AnalyticsPage() {
  const {
    charts,
    snapshots,
    loading,
    creatingSnapshot,
    error,
    fetchAnalytics,
    fetchSkillGaps,
    createSnapshot,
  } = useAnalyticsStore();

  React.useEffect(() => {
    fetchAnalytics();
    fetchSkillGaps();
  }, [fetchAnalytics, fetchSkillGaps]);

  const handleRefresh = async () => {
    await Promise.all([fetchAnalytics(), fetchSkillGaps()]);
  };

  return (
    <AppShell>
      <PageHeader
        title="Analytics Workspace"
        description="Interactive visualization workspace exploring match distributions, skill demand, location splits, and profile velocity."
        badge={
          <Badge variant="outline" className="font-mono text-xs">
            Visual Telemetry
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
              Refresh Charts
            </Button>

            <Link
              href="/dashboard"
              className="inline-flex items-center justify-center rounded-md text-xs font-medium h-8 px-3 border border-border bg-background hover:bg-muted text-foreground transition-colors"
            >
              <LayoutDashboard className="h-3.5 w-3.5 mr-1.5" />
              Dashboard Overview
            </Link>
          </div>
        }
      />

      <div className="space-y-6">
        {/* Error State */}
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

        {/* Telemetry metadata banner */}
        <div className="rounded-xl border border-primary/20 bg-primary/5 p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0">
              <BarChart3 className="h-4 w-4" />
            </div>
            <div>
              <span className="font-semibold text-foreground block">
                Continuous Market Benchmarking Online
              </span>
              <span className="text-muted-foreground">
                Visualizing aggregated scores from target job postings and candidate profile intelligence.
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4 text-muted-foreground self-start sm:self-auto font-mono text-[11px]">
            {charts?.latencyMs !== undefined && (
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3 text-emerald-500" />
                Query: {charts.latencyMs}ms
              </span>
            )}
            {charts?.generatedAt && (
              <span className="flex items-center gap-1">
                <Calendar className="h-3 w-3 text-indigo-500" />
                Updated: {new Date(charts.generatedAt).toLocaleTimeString()}
              </span>
            )}
          </div>
        </div>

        {/* 1. Profile Progress & Readiness Trend Chart (AreaChart) */}
        <div>
          <ProfileProgressChart
            data={snapshots}
            loading={loading}
            onRecordSnapshot={createSnapshot}
            recordingSnapshot={creatingSnapshot}
          />
        </div>

        {/* 2. Match Distribution & Workplace Location (2 Columns) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <MatchDistributionChart data={charts?.matchDistribution || null} loading={loading} />
          <LocationDistributionChart data={charts?.locationDistribution || []} loading={loading} />
        </div>

        {/* 3. Skill Demand & Missing Skill Hotspots (2 Columns) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <SkillDemandChart data={charts?.topSkills || []} loading={loading} />
          <MissingSkillsChart data={charts?.missingSkills || []} loading={loading} />
        </div>
      </div>
    </AppShell>
  );
}
