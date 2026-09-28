'use client';

import React from 'react';
import {
  CheckCircle2,
  Award,
  Sparkles,
  Layers,
  TrendingUp,
  AlertTriangle,
  Flame,
} from 'lucide-react';
import { InterviewAnalytics, CareerCoaching } from '@/types';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';

interface InterviewAnalyticsHeaderProps {
  analytics: InterviewAnalytics | null;
  coaching?: CareerCoaching | null;
  loading?: boolean;
}

export function InterviewAnalyticsHeader({
  analytics,
  coaching,
  loading = false,
}: InterviewAnalyticsHeaderProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i} className="p-4 border-border/40 bg-card/60 animate-pulse">
            <div className="h-3 w-20 bg-muted rounded mb-2" />
            <div className="h-7 w-16 bg-muted rounded" />
          </Card>
        ))}
      </div>
    );
  }

  const completed = analytics?.questionsCompleted ?? 0;
  const total = Math.max(completed, 10);
  const avgScore = Math.round(analytics?.averageScore ?? 0);
  const readiness = Math.round(coaching?.interviewReadinessScore ?? analytics?.readinessScore ?? (avgScore > 0 ? avgScore : 70));
  const mockCount = analytics?.totalSessions ?? 0;
  const strongAreas = coaching?.strongAreas?.length
    ? coaching.strongAreas
    : analytics?.strongAreas ?? [];
  const weakAreas = coaching?.weakAreas?.length
    ? coaching.weakAreas
    : analytics?.weakAreas ?? [];

  const completionPct = total > 0 ? Math.min(100, Math.round((completed / total) * 100)) : 0;

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-500';
    if (score >= 65) return 'text-blue-500';
    if (score >= 50) return 'text-amber-500';
    return 'text-rose-500';
  };

  const getReadinessBadge = (score: number) => {
    if (score >= 85) return { label: 'High Readiness', variant: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/30' };
    if (score >= 70) return { label: 'Interview Ready', variant: 'bg-blue-500/10 text-blue-500 border-blue-500/30' };
    if (score >= 50) return { label: 'Emerging', variant: 'bg-amber-500/10 text-amber-500 border-amber-500/30' };
    return { label: 'Needs Practice', variant: 'bg-rose-500/10 text-rose-500 border-rose-500/30' };
  };

  const readinessBadge = getReadinessBadge(readiness);

  return (
    <div className="space-y-4 mb-6">
      {/* 4 Primary KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Questions Completed */}
        <Card className="p-4 border-border/50 bg-card/70 backdrop-blur-sm hover:border-border transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-muted-foreground">Questions Completed</span>
            <div className="p-1.5 rounded-md bg-primary/10 text-primary">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight text-foreground">{completed}</span>
            <span className="text-xs text-muted-foreground">/ {total} questions</span>
          </div>
          <div className="mt-2.5 space-y-1">
            <Progress value={completionPct} className="h-1.5" />
            <div className="flex justify-between text-[10px] text-muted-foreground">
              <span>Progress</span>
              <span>{completionPct}%</span>
            </div>
          </div>
        </Card>

        {/* Average Score */}
        <Card className="p-4 border-border/50 bg-card/70 backdrop-blur-sm hover:border-border transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-muted-foreground">Average Score</span>
            <div className="p-1.5 rounded-md bg-blue-500/10 text-blue-500">
              <Award className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className={`text-2xl font-bold tracking-tight ${getScoreColor(avgScore)}`}>
              {avgScore > 0 ? `${avgScore}%` : 'N/A'}
            </span>
            <span className="text-xs text-muted-foreground">evaluated answers</span>
          </div>
          <p className="text-[11px] text-muted-foreground mt-2">
            Calibrated on STAR & Technical accuracy
          </p>
        </Card>

        {/* Interview Readiness */}
        <Card className="p-4 border-border/50 bg-card/70 backdrop-blur-sm hover:border-border transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-muted-foreground">Readiness Score</span>
            <div className="p-1.5 rounded-md bg-purple-500/10 text-purple-500">
              <Sparkles className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-2xl font-bold tracking-tight text-foreground">
              {readiness > 0 ? `${readiness}%` : '70%'}
            </span>
            <span className={`text-[11px] font-medium px-2 py-0.5 rounded-full border ${readinessBadge.variant}`}>
              {readinessBadge.label}
            </span>
          </div>
          <p className="text-[11px] text-muted-foreground mt-2">
            AI benchmarked against role requirements
          </p>
        </Card>

        {/* Mock Interviews */}
        <Card className="p-4 border-border/50 bg-card/70 backdrop-blur-sm hover:border-border transition-all">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-muted-foreground">Mock Interviews</span>
            <div className="p-1.5 rounded-md bg-amber-500/10 text-amber-500">
              <Flame className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold tracking-tight text-foreground">{mockCount}</span>
            <span className="text-xs text-muted-foreground">sessions recorded</span>
          </div>
          <p className="text-[11px] text-muted-foreground mt-2">
            Full-loop timed simulation runs
          </p>
        </Card>
      </div>

      {/* Strong & Weak Areas Bar */}
      {(strongAreas.length > 0 || weakAreas.length > 0) && (
        <Card className="p-3 border-border/50 bg-card/50 backdrop-blur-sm flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-semibold text-emerald-500 flex items-center gap-1">
              <TrendingUp className="w-3.5 h-3.5" /> Strong Areas:
            </span>
            {strongAreas.length > 0 ? (
              strongAreas.map((skill, idx) => (
                <Badge
                  key={idx}
                  variant="outline"
                  className="bg-emerald-500/10 text-emerald-400 border-emerald-500/30 text-[11px] py-0"
                >
                  {skill}
                </Badge>
              ))
            ) : (
              <span className="text-muted-foreground">Keep answering to surface strengths</span>
            )}
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-semibold text-amber-500 flex items-center gap-1">
              <AlertTriangle className="w-3.5 h-3.5" /> Growth Areas:
            </span>
            {weakAreas.length > 0 ? (
              weakAreas.map((skill, idx) => (
                <Badge
                  key={idx}
                  variant="outline"
                  className="bg-amber-500/10 text-amber-400 border-amber-500/30 text-[11px] py-0"
                >
                  {skill}
                </Badge>
              ))
            ) : (
              <span className="text-muted-foreground">No weak areas detected yet</span>
            )}
          </div>
        </Card>
      )}
    </div>
  );
}
