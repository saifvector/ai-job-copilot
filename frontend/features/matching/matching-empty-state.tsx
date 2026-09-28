'use client';

import * as React from 'react';
import { Target, Sparkles, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useMatchingStore } from '@/store/matching-store';

interface MatchingEmptyStateProps {
  isFiltered?: boolean;
}

export function MatchingEmptyState({ isFiltered = false }: MatchingEmptyStateProps) {
  const { runMatching, runningMatch, resetFilters } = useMatchingStore();

  if (isFiltered) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center rounded-xl border border-dashed border-border/80 bg-card/20 space-y-3">
        <div className="p-3 rounded-full bg-muted/40 text-muted-foreground">
          <Target className="h-6 w-6" />
        </div>
        <h3 className="text-base font-semibold text-foreground">No matches meet your criteria</h3>
        <p className="text-xs text-muted-foreground max-w-sm">
          Try lowering the minimum score threshold or clearing location and company filters.
        </p>
        <Button variant="outline" size="sm" onClick={resetFilters} className="text-xs mt-2">
          <RefreshCw className="mr-1.5 h-3.5 w-3.5" />
          Reset All Filters
        </Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center p-14 text-center rounded-xl border border-dashed border-border/80 bg-card/30 space-y-4">
      <div className="p-4 rounded-2xl bg-primary/10 border border-primary/20 text-primary">
        <Sparkles className="h-8 w-8 animate-pulse" />
      </div>
      <div className="space-y-1 max-w-md">
        <h3 className="text-lg font-bold text-foreground">No Job Matches Computed Yet</h3>
        <p className="text-xs text-muted-foreground leading-relaxed">
          Run our 5-dimensional matching algorithm to evaluate your resume, skills, and experience against live job postings.
        </p>
      </div>
      <Button
        variant="default"
        onClick={() => runMatching({ limit: 500 })}
        disabled={runningMatch}
        className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-md text-xs px-5 h-9"
      >
        <Sparkles className={`mr-2 h-4 w-4 ${runningMatch ? 'animate-spin' : ''}`} />
        {runningMatch ? 'Evaluating 500+ Jobs...' : 'Trigger AI Job Matching'}
      </Button>
    </div>
  );
}
