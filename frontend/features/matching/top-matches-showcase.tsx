'use client';

import * as React from 'react';
import { Sparkles, ArrowRight, Building, MapPin, DollarSign, CheckCircle2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { CircularScoreIndicator } from './score-indicator';
import { MatchResult } from '@/types';
import { useMatchingStore } from '@/store/matching-store';

interface TopMatchesShowcaseProps {
  matches: MatchResult[];
}

export function TopMatchesShowcase({ matches }: TopMatchesShowcaseProps) {
  const { selectResult } = useMatchingStore();

  if (!matches || matches.length === 0) {
    return null;
  }

  // Display top 3 jobs prominently
  const displayItems = matches.slice(0, 3);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-primary/10 border border-primary/20 text-primary">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-sm font-semibold tracking-tight text-foreground">Top AI Recommendations</h2>
            <p className="text-xs text-muted-foreground">Highest-ranked jobs evaluated against your candidate profile</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {displayItems.map((match, idx) => {
          const job = match.job;
          if (!job) return null;

          const hasSalary = job.salaryMin || job.salaryMax;
          const salaryText = hasSalary
            ? `$${((job.salaryMin || 0) / 1000).toFixed(0)}k - $${((job.salaryMax || 0) / 1000).toFixed(0)}k`
            : null;

          return (
            <Card
              key={match.id}
              className="relative overflow-hidden border-border/80 bg-gradient-to-b from-card/80 to-card/40 hover:border-primary/50 transition-all duration-300 shadow-sm hover:shadow-md cursor-pointer group"
              onClick={() => selectResult(match)}
            >
              {/* Rank ribbon badge */}
              <div className="absolute top-3 right-3 flex items-center gap-2">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-md bg-muted/60 text-muted-foreground border border-border/50">
                  Rank #{idx + 1}
                </span>
              </div>

              <CardHeader className="p-4 pb-2">
                <div className="flex items-start gap-3">
                  <CircularScoreIndicator score={match.overallScore} size={48} strokeWidth={4} />
                  <div className="space-y-1 min-w-0 flex-1 pr-12">
                    <CardTitle className="text-sm font-semibold truncate group-hover:text-primary transition-colors">
                      {job.title}
                    </CardTitle>
                    <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                      <Building className="h-3 w-3 shrink-0" />
                      <span className="truncate font-medium">{job.company}</span>
                    </div>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="p-4 pt-2 space-y-3">
                <div className="flex flex-wrap items-center gap-1.5 text-[11px] text-muted-foreground">
                  <span className="inline-flex items-center gap-1">
                    <MapPin className="h-3 w-3" />
                    {job.location}
                  </span>
                  {salaryText && (
                    <>
                      <span>•</span>
                      <span className="inline-flex items-center gap-0.5 font-medium text-foreground">
                        <DollarSign className="h-3 w-3 text-emerald-500" />
                        {salaryText}
                      </span>
                    </>
                  )}
                  <span>•</span>
                  <Badge variant="outline" className="text-[10px] px-1.5 py-0">
                    {job.source}
                  </Badge>
                </div>

                {/* Key match strength excerpt */}
                {match.strengths && match.strengths.length > 0 && (
                  <div className="rounded-md bg-muted/30 border border-border/40 p-2 text-[11px] text-muted-foreground line-clamp-2">
                    <span className="font-semibold text-emerald-400 mr-1 inline-flex items-center gap-0.5">
                      <CheckCircle2 className="h-3 w-3 inline" /> Strength:
                    </span>
                    {match.strengths[0]}
                  </div>
                )}

                <div className="pt-1 flex items-center justify-between">
                  <span className="text-[11px] text-muted-foreground font-mono">
                    {match.missingSkills.length} missing skill{match.missingSkills.length !== 1 ? 's' : ''}
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-7 px-2 text-xs text-primary group-hover:translate-x-0.5 transition-transform"
                  >
                    View Analysis <ArrowRight className="ml-1 h-3 w-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
