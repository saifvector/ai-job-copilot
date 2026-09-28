'use client';

import * as React from 'react';
import { ProfileHealthData } from '@/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { HeartPulse, CheckCircle2, ChevronRight, FileText, Code2, Briefcase, GraduationCap } from 'lucide-react';
import Link from 'next/link';

interface ProfileHealthCardProps {
  data: ProfileHealthData | null;
  loading?: boolean;
}

export function ProfileHealthCard({ data, loading }: ProfileHealthCardProps) {
  if (loading || !data) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <HeartPulse className="h-4 w-4 text-rose-500" />
            Profile Health Score
          </CardTitle>
          <CardDescription>Completeness & AI matching optimization index</CardDescription>
        </CardHeader>
        <CardContent className="h-[260px] flex items-center justify-center">
          <div className="h-full w-full bg-muted/20 animate-pulse rounded-lg" />
        </CardContent>
      </Card>
    );
  }

  const { overallScore, breakdown } = data;

  const pillars = [
    {
      name: 'Resume Completeness',
      score: breakdown.resumeCompleteness,
      icon: FileText,
      color: 'bg-emerald-500',
    },
    {
      name: 'Skill Coverage',
      score: breakdown.skillCoverage,
      icon: Code2,
      color: 'bg-blue-500',
    },
    {
      name: 'Experience Depth',
      score: breakdown.experienceCoverage,
      icon: Briefcase,
      color: 'bg-indigo-500',
    },
    {
      name: 'Education & Credentials',
      score: breakdown.educationCoverage,
      icon: GraduationCap,
      color: 'bg-amber-500',
    },
  ];

  return (
    <Card className="h-full flex flex-col justify-between">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <HeartPulse className="h-4 w-4 text-rose-500" />
            Profile Health Score
          </CardTitle>
          <Link
            href="/profile-health"
            className="text-xs text-primary hover:underline flex items-center font-medium"
          >
            Audit Details
            <ChevronRight className="h-3 w-3 ml-0.5" />
          </Link>
        </div>
        <CardDescription>Overall AI readiness rating across 4 foundational pillars</CardDescription>
      </CardHeader>

      <CardContent className="space-y-4 pt-1 flex-1 flex flex-col justify-between">
        {/* Score Ring / Bar */}
        <div className="flex items-center justify-between p-3 rounded-xl bg-card/60 border border-border/70">
          <div>
            <div className="text-3xl font-extrabold font-mono tracking-tight text-foreground flex items-baseline gap-1">
              <span>{overallScore}%</span>
              <span className="text-xs font-normal text-muted-foreground">Optimal</span>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">
              {overallScore >= 80
                ? 'High matching efficiency. Profiles above 80% receive 3.4x more accurate recommendations.'
                : 'Complete the recommendations below to unlock higher fit score calibration.'}
            </p>
          </div>

          <div className="h-14 w-14 rounded-full border-4 border-primary/20 border-t-primary flex items-center justify-center font-mono font-bold text-sm text-primary">
            {overallScore}%
          </div>
        </div>

        {/* 4 Pillars Progress */}
        <div className="space-y-2.5">
          {pillars.map((p) => {
            const Icon = p.icon;
            return (
              <div key={p.name} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="flex items-center gap-1.5 text-muted-foreground">
                    <Icon className="h-3.5 w-3.5 text-foreground/70" />
                    {p.name}
                  </span>
                  <span className="font-mono font-semibold text-foreground">{p.score}%</span>
                </div>
                <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${p.color} transition-all duration-500`}
                    style={{ width: `${p.score}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>

        {/* Top Recommendation */}
        {data.actionableRecommendations && data.actionableRecommendations.length > 0 && (
          <div className="pt-2 border-t border-border/50 text-xs">
            <div className="flex items-start gap-1.5 text-muted-foreground">
              <CheckCircle2 className="h-3.5 w-3.5 text-primary shrink-0 mt-0.5" />
              <span>
                <strong className="text-foreground">Next Action:</strong> {data.actionableRecommendations[0]}
              </span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
