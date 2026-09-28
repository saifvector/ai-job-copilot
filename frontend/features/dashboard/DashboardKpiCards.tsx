'use client';

import * as React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { DashboardOverview } from '@/types';
import {
  Briefcase,
  Target,
  Award,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  TrendingUp,
  TrendingDown,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface DashboardKpiCardsProps {
  metrics: DashboardOverview | null;
  loading?: boolean;
}

export function DashboardKpiCards({ metrics, loading }: DashboardKpiCardsProps) {
  if (loading || !metrics) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
        {[...Array(7)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-4 space-y-2">
              <div className="h-3 w-16 bg-muted rounded" />
              <div className="h-7 w-12 bg-muted rounded" />
              <div className="h-3 w-20 bg-muted rounded" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  const { trends } = metrics;

  const cards = [
    {
      label: 'Jobs Available',
      value: metrics.totalJobs.toLocaleString(),
      subtext: 'Global discovery pool',
      icon: Briefcase,
      color: 'text-primary',
      bg: 'bg-primary/10',
      delta: null,
    },
    {
      label: 'Jobs Matched',
      value: metrics.jobsMatched.toLocaleString(),
      subtext: 'Evaluated profiles',
      icon: Target,
      color: 'text-indigo-500',
      bg: 'bg-indigo-500/10',
      delta: trends.jobsMatchedDelta,
      deltaSuffix: ' new',
    },
    {
      label: 'Avg Match Score',
      value: `${metrics.averageMatchScore}%`,
      subtext: 'Across matched jobs',
      icon: Award,
      color: 'text-cyan-500',
      bg: 'bg-cyan-500/10',
      delta: trends.matchScoreDelta,
      deltaSuffix: '%',
    },
    {
      label: 'Excellent (85%+)',
      value: metrics.excellentMatches,
      subtext: 'Prime suitability',
      icon: Sparkles,
      color: 'text-emerald-500',
      bg: 'bg-emerald-500/10',
      badge: 'Tier 1',
    },
    {
      label: 'Strong (70-84%)',
      value: metrics.strongMatches,
      subtext: 'High interview yield',
      icon: CheckCircle2,
      color: 'text-blue-500',
      bg: 'bg-blue-500/10',
      badge: 'Tier 2',
    },
    {
      label: 'Moderate (50-69%)',
      value: metrics.moderateMatches,
      subtext: 'Minor skill gaps',
      icon: AlertTriangle,
      color: 'text-amber-500',
      bg: 'bg-amber-500/10',
      badge: 'Tier 3',
    },
    {
      label: 'Weak (<50%)',
      value: metrics.weakMatches,
      subtext: 'Divergent profile',
      icon: HelpCircle,
      color: 'text-rose-500',
      bg: 'bg-rose-500/10',
      badge: 'Tier 4',
    },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3.5">
      {cards.map((c) => {
        const Icon = c.icon;
        const hasDelta = c.delta !== undefined && c.delta !== null && c.delta !== 0;
        const isPositive = hasDelta && c.delta! > 0;

        return (
          <Card
            key={c.label}
            className="border-border/60 hover:border-border transition-all duration-200 hover:shadow-sm"
          >
            <CardContent className="p-3.5 flex flex-col justify-between h-full space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-medium text-muted-foreground truncate">
                  {c.label}
                </span>
                <div className={cn('p-1.5 rounded-md shrink-0', c.bg, c.color)}>
                  <Icon className="h-3.5 w-3.5" />
                </div>
              </div>

              <div>
                <div className="text-xl font-bold tracking-tight text-foreground font-mono">
                  {c.value}
                </div>
                <div className="flex items-center justify-between text-[10px] text-muted-foreground mt-0.5">
                  <span className="truncate">{c.subtext}</span>
                  {hasDelta ? (
                    <span
                      className={cn(
                        'flex items-center font-mono font-medium ml-1 shrink-0',
                        isPositive ? 'text-emerald-500' : 'text-rose-500'
                      )}
                    >
                      {isPositive ? (
                        <TrendingUp className="h-2.5 w-2.5 mr-0.5 inline" />
                      ) : (
                        <TrendingDown className="h-2.5 w-2.5 mr-0.5 inline" />
                      )}
                      {isPositive ? `+${c.delta}` : c.delta}
                      {c.deltaSuffix}
                    </span>
                  ) : c.badge ? (
                    <span className="text-[9px] px-1 py-0.2 rounded bg-muted font-mono shrink-0">
                      {c.badge}
                    </span>
                  ) : null}
                </div>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
