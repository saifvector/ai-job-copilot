'use client';

import * as React from 'react';
import { CareerReadinessData } from '@/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Compass, Lightbulb, ShieldCheck, Zap } from 'lucide-react';

interface CareerReadinessCardProps {
  data: CareerReadinessData | null;
  loading?: boolean;
}

export function CareerReadinessCard({ data, loading }: CareerReadinessCardProps) {
  if (loading || !data) {
    return (
      <Card className="h-full">
        <CardHeader>
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Compass className="h-4 w-4 text-cyan-500" />
            Career Readiness Index
          </CardTitle>
          <CardDescription>Competitive standing against active market demand</CardDescription>
        </CardHeader>
        <CardContent className="h-[260px] flex items-center justify-center">
          <div className="h-full w-full bg-muted/20 animate-pulse rounded-lg" />
        </CardContent>
      </Card>
    );
  }

  const { careerReadinessScore, tier, factors, explanation, keyCompetencies } = data;

  const getTierVariant = (tierName: string) => {
    if (tierName === 'Market Leader') return 'default';
    if (tierName === 'Market Ready') return 'secondary';
    return 'outline';
  };

  return (
    <Card className="h-full flex flex-col justify-between">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Compass className="h-4 w-4 text-cyan-500" />
            Career Readiness Score
          </CardTitle>
          <Badge variant={getTierVariant(tier)} className="font-mono text-xs">
            {tier}
          </Badge>
        </div>
        <CardDescription>Evaluated across skills depth, experience, and market fit rates</CardDescription>
      </CardHeader>

      <CardContent className="space-y-4 pt-1 flex-1 flex flex-col justify-between">
        {/* Metric summary */}
        <div className="p-3 rounded-xl bg-card/60 border border-border/70 flex items-center justify-between">
          <div>
            <div className="text-3xl font-extrabold font-mono tracking-tight text-foreground flex items-baseline gap-1">
              <span>{careerReadinessScore}%</span>
              <span className="text-xs font-normal text-cyan-500 font-sans">Readiness Rating</span>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
              {explanation}
            </p>
          </div>

          <div className="h-12 w-12 rounded-xl bg-cyan-500/10 text-cyan-500 flex items-center justify-center shrink-0">
            <ShieldCheck className="h-6 w-6" />
          </div>
        </div>

        {/* 4 Pillars Breakdown */}
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="p-2 rounded-lg bg-muted/30">
            <span className="text-[11px] text-muted-foreground block">Resume Quality</span>
            <span className="font-mono font-bold text-foreground">{factors.resumeQuality}%</span>
          </div>
          <div className="p-2 rounded-lg bg-muted/30">
            <span className="text-[11px] text-muted-foreground block">Skills Alignment</span>
            <span className="font-mono font-bold text-foreground">{factors.skillsAlignment}%</span>
          </div>
          <div className="p-2 rounded-lg bg-muted/30">
            <span className="text-[11px] text-muted-foreground block">Experience Depth</span>
            <span className="font-mono font-bold text-foreground">{factors.experienceDepth}%</span>
          </div>
          <div className="p-2 rounded-lg bg-muted/30">
            <span className="text-[11px] text-muted-foreground block">High Fit Rate</span>
            <span className="font-mono font-bold text-foreground">{factors.marketMatchRate}%</span>
          </div>
        </div>

        {/* Top Key Competencies */}
        {keyCompetencies && keyCompetencies.length > 0 && (
          <div className="pt-2 border-t border-border/50 text-xs">
            <div className="flex items-center gap-1 text-[11px] text-muted-foreground mb-1.5 font-medium">
              <Zap className="h-3 w-3 text-amber-500" />
              Verified Signature Strengths:
            </div>
            <div className="flex flex-wrap gap-1">
              {keyCompetencies.map((skill) => (
                <span
                  key={skill}
                  className="px-2 py-0.5 rounded text-[10px] font-mono bg-primary/10 text-primary border border-primary/20"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
