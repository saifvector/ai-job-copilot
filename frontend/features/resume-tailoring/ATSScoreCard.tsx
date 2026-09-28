'use client';

import React from 'react';
import { ATSScoreBreakdown } from '@/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle2, AlertCircle, Sparkles } from 'lucide-react';

interface ATSScoreCardProps {
  score: number;
  breakdown?: ATSScoreBreakdown;
  className?: string;
}

export const ATSScoreCard: React.FC<ATSScoreCardProps> = ({
  score,
  breakdown,
  className = '',
}) => {
  const getScoreColor = (val: number) => {
    if (val >= 85) return 'text-emerald-500 bg-emerald-50 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-800';
    if (val >= 70) return 'text-blue-500 bg-blue-50 dark:bg-blue-950/30 border-blue-200 dark:border-blue-800';
    if (val >= 55) return 'text-amber-500 bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-800';
    return 'text-rose-500 bg-rose-50 dark:bg-rose-950/30 border-rose-200 dark:border-rose-800';
  };

  const getScoreLabel = (val: number) => {
    if (val >= 85) return 'Excellent ATS Fit';
    if (val >= 70) return 'Strong Alignment';
    if (val >= 55) return 'Moderate Fit';
    return 'Requires Optimization';
  };

  const factors = breakdown
    ? [
        { label: 'Keyword Match', score: breakdown.keywordMatch, weight: '30%' },
        { label: 'Skill Match', score: breakdown.skillMatch, weight: '25%' },
        { label: 'Section Quality', score: breakdown.sectionQuality, weight: '15%' },
        { label: 'Experience Relevance', score: breakdown.experienceRelevance, weight: '15%' },
        { label: 'Formatting Structure', score: breakdown.formattingStructure, weight: '15%' },
      ]
    : [];

  return (
    <Card className={`border shadow-sm ${className}`}>
      <CardHeader className="pb-3 border-b border-border/40">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-primary" />
            ATS Compatibility Score
          </CardTitle>
          <Badge variant="outline" className={`px-2.5 py-0.5 font-medium border ${getScoreColor(score)}`}>
            {getScoreLabel(score)}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="pt-4 space-y-5">
        {/* Main Score Gauge */}
        <div className="flex items-center justify-between bg-muted/30 p-4 rounded-xl border border-border/50">
          <div>
            <div className="text-3xl font-bold tracking-tight text-foreground flex items-baseline gap-1">
              <span>{Math.round(score)}</span>
              <span className="text-sm font-normal text-muted-foreground">/ 100</span>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">
              Evaluated across 5 ATS evaluation dimensions
            </p>
          </div>
          <div className="w-16 h-16 rounded-full flex items-center justify-center border-4 border-primary/20 bg-primary/5 text-primary font-bold text-lg">
            {Math.round(score)}%
          </div>
        </div>

        {/* 5 Scoring Factors */}
        {factors.length > 0 && (
          <div className="space-y-3">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Factor Breakdown
            </h4>
            <div className="space-y-2.5">
              {factors.map((f) => (
                <div key={f.label} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-foreground font-medium">
                      {f.label}{' '}
                      <span className="text-muted-foreground font-normal">({f.weight})</span>
                    </span>
                    <span className="font-semibold text-foreground">{Math.round(f.score)}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        f.score >= 80 ? 'bg-emerald-500' : f.score >= 65 ? 'bg-blue-500' : 'bg-amber-500'
                      }`}
                      style={{ width: `${Math.min(100, Math.max(0, f.score))}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Suggestions Checklist */}
        {breakdown?.suggestions && breakdown.suggestions.length > 0 && (
          <div className="pt-2 border-t border-border/40 space-y-2">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              ATS Optimization Suggestions
            </h4>
            <ul className="space-y-1.5">
              {breakdown.suggestions.map((suggestion, idx) => (
                <li key={idx} className="flex items-start gap-2 text-xs text-muted-foreground leading-relaxed">
                  {score >= 80 ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0 mt-0.5" />
                  ) : (
                    <AlertCircle className="w-3.5 h-3.5 text-amber-500 shrink-0 mt-0.5" />
                  )}
                  <span>{suggestion}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
