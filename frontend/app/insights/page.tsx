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
import { MatchInsightsTable, SkillGapWidget } from '@/features/dashboard';
import {
  Bookmark,
  Compass,
  Filter,
  Layers,
  LayoutDashboard,
  RefreshCw,
  Sparkles,
  Target,
} from 'lucide-react';

export default function InsightsPage() {
  const {
    insights,
    savedJobIds,
    loading,
    error,
    fetchDashboard,
    toggleSaveJob,
  } = useDashboardStore();

  const { skillGaps, fetchSkillGaps } = useAnalyticsStore();

  const [filterMode, setFilterMode] = React.useState<'all' | 'saved'>('all');

  React.useEffect(() => {
    fetchDashboard();
    fetchSkillGaps();
  }, [fetchDashboard, fetchSkillGaps]);

  const displayedMatches =
    filterMode === 'saved'
      ? insights.filter((item) => savedJobIds.includes(item.jobId))
      : insights;

  return (
    <AppShell>
      <PageHeader
        title="Match Insights"
        description="Exploration workspace for top ranked opportunities, missing qualifications, and bookmarked roles."
        badge={
          <Badge variant="outline" className="font-mono text-xs">
            Opportunities
          </Badge>
        }
        action={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                fetchDashboard();
                fetchSkillGaps();
              }}
              disabled={loading}
              className="h-8 gap-1.5 text-xs"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>

            <Link
              href="/dashboard"
              className="inline-flex items-center justify-center rounded-md text-xs font-medium h-8 px-3 border border-border bg-background hover:bg-muted text-foreground transition-colors"
            >
              <LayoutDashboard className="h-3.5 w-3.5 mr-1.5" />
              Dashboard
            </Link>
          </div>
        }
      />

      <div className="space-y-6">
        {/* Error banner if any */}
        {error && (
          <Card className="border-rose-500/20 bg-rose-500/5">
            <CardContent className="p-4 flex items-center justify-between text-xs text-rose-500">
              <span>{error}</span>
              <Button variant="ghost" size="sm" onClick={() => fetchDashboard()} className="h-7 text-xs">
                Retry
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Filter bar */}
        <div className="flex items-center justify-between p-2.5 rounded-xl border border-border/70 bg-card/60">
          <div className="flex items-center gap-2">
            <Button
              variant={filterMode === 'all' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setFilterMode('all')}
              className="h-8 text-xs gap-1.5"
            >
              <Sparkles className="h-3.5 w-3.5" />
              All Top Matches ({insights.length})
            </Button>

            <Button
              variant={filterMode === 'saved' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setFilterMode('saved')}
              className="h-8 text-xs gap-1.5"
            >
              <Bookmark className="h-3.5 w-3.5 text-amber-500" />
              Saved Bookmarks ({savedJobIds.length})
            </Button>
          </div>

          <span className="text-xs text-muted-foreground mr-2 font-mono">
            {displayedMatches.length} opportunity results
          </span>
        </div>

        {/* Top Matches Table */}
        <MatchInsightsTable
          matches={displayedMatches}
          savedJobIds={savedJobIds}
          onToggleSave={toggleSaveJob}
          loading={loading}
        />

        {/* Skill Gap Analysis Intelligence */}
        <SkillGapWidget data={skillGaps} loading={loading} />
      </div>
    </AppShell>
  );
}
