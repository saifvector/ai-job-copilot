'use client';

import * as React from 'react';
import { SkillGapAnalysisData } from '@/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Check, Flame, Layers, Lightbulb, Sparkles, X } from 'lucide-react';

interface SkillGapWidgetProps {
  data: SkillGapAnalysisData | null;
  loading?: boolean;
}

export function SkillGapWidget({ data, loading }: SkillGapWidgetProps) {
  if (loading || !data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Layers className="h-4 w-4 text-primary" />
            Market Skill Gap Analysis
          </CardTitle>
          <CardDescription>Identifying high-value skills across matched jobs</CardDescription>
        </CardHeader>
        <CardContent className="h-[200px] flex items-center justify-center">
          <div className="h-full w-full bg-muted/20 animate-pulse rounded-lg" />
        </CardContent>
      </Card>
    );
  }

  const { mostRequestedSkills, missingSkills, emergingSkills, recommendations } = data;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Layers className="h-4 w-4 text-primary" />
            Skill Gap & Market Intelligence
          </CardTitle>
          <span className="text-xs text-muted-foreground font-mono">
            {data.totalAnalyzedJobs} roles analyzed
          </span>
        </div>
        <CardDescription>
          Comparison between your profile competencies and employer requirements
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* 1. Most Requested */}
          <div className="p-3.5 rounded-xl border border-border/70 bg-card/50 space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-foreground flex items-center gap-1.5">
                <Sparkles className="h-3.5 w-3.5 text-primary" />
                Most Requested
              </span>
              <span className="text-[10px] text-muted-foreground">Across target roles</span>
            </div>

            <div className="space-y-1.5">
              {mostRequestedSkills.slice(0, 5).map((skill) => (
                <div
                  key={skill.name}
                  className="flex items-center justify-between p-1.5 rounded-md bg-muted/30 text-xs"
                >
                  <span className="flex items-center gap-1.5 font-medium truncate">
                    {skill.inCandidateProfile ? (
                      <Check className="h-3 w-3 text-emerald-500 shrink-0" />
                    ) : (
                      <X className="h-3 w-3 text-rose-500 shrink-0" />
                    )}
                    <span className="truncate">{skill.name}</span>
                  </span>
                  <span className="text-[11px] font-mono text-muted-foreground shrink-0 ml-2">
                    {skill.percentage}%
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* 2. Missing Skills */}
          <div className="p-3.5 rounded-xl border border-border/70 bg-card/50 space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-rose-500 flex items-center gap-1.5">
                <X className="h-3.5 w-3.5" />
                Missing Qualifications
              </span>
              <span className="text-[10px] text-muted-foreground">Action needed</span>
            </div>

            <div className="space-y-1.5">
              {missingSkills.slice(0, 5).map((skill) => (
                <div
                  key={skill.name}
                  className="flex items-center justify-between p-1.5 rounded-md bg-rose-500/5 border border-rose-500/10 text-xs"
                >
                  <span className="font-medium text-foreground truncate">{skill.name}</span>
                  <div className="flex items-center gap-1.5 shrink-0 ml-2">
                    <Badge variant="outline" className="text-[10px] px-1.5 py-0 font-mono text-rose-500">
                      {skill.priority}
                    </Badge>
                    <span className="text-[11px] font-mono text-muted-foreground">{skill.percentage}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 3. Emerging Skills */}
          <div className="p-3.5 rounded-xl border border-border/70 bg-card/50 space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-cyan-500 flex items-center gap-1.5">
                <Flame className="h-3.5 w-3.5" />
                Emerging & Modern
              </span>
              <span className="text-[10px] text-muted-foreground">High growth</span>
            </div>

            <div className="space-y-1.5">
              {emergingSkills.slice(0, 5).map((skill) => (
                <div
                  key={skill.name}
                  className="flex items-center justify-between p-1.5 rounded-md bg-cyan-500/5 border border-cyan-500/10 text-xs"
                >
                  <span className="font-medium text-foreground truncate">{skill.name}</span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-500 font-mono shrink-0 ml-2">
                    {skill.category || 'High-Growth'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Actionable Recommendations */}
        {recommendations && recommendations.length > 0 && (
          <div className="p-3 rounded-lg border border-primary/20 bg-primary/5 space-y-1.5 text-xs">
            <div className="flex items-center gap-1.5 font-semibold text-foreground">
              <Lightbulb className="h-3.5 w-3.5 text-amber-500" />
              Strategic AI Recommendations:
            </div>
            <ul className="list-disc list-inside space-y-1 text-muted-foreground">
              {recommendations.map((rec, i) => (
                <li key={i}>{rec}</li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
