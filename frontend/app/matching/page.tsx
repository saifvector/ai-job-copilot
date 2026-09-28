'use client';

import React, { useEffect } from 'react';
import {
  Sparkles,
  Target,
  RefreshCw,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  TrendingUp,
  Cpu,
} from 'lucide-react';
import { useMatchingStore } from '@/store/matching-store';
import {
  MatchFiltersBar,
  TopMatchesShowcase,
  MatchResultsTable,
  MatchAnalysisModal,
  MatchingSkeleton,
  MatchingEmptyState,
} from '@/features/matching';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export default function MatchingPage() {
  const {
    results,
    topMatches,
    selectedResult,
    loading,
    runningMatch,
    error,
    total,
    page,
    totalPages,
    lastRunResult,
    fetchResults,
    fetchTopMatches,
    runMatching,
    selectResult,
    setPage,
    clearError,
    filters,
  } = useMatchingStore();

  useEffect(() => {
    fetchResults();
    fetchTopMatches(5);
  }, [fetchResults, fetchTopMatches]);

  const hasActiveFilters = Boolean(
    filters.minScore || filters.role || filters.location || filters.company
  );

  return (
    <div className="space-y-6 pb-12">
      {/* Top Header & Analytics Summary */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/60 pb-5">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-xl bg-gradient-to-br from-blue-500/20 to-indigo-500/20 border border-blue-500/30 text-blue-400">
              <Target className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
                AI Job Match Engine
                <Badge variant="outline" className="text-[10px] font-mono border-primary/30 text-primary">
                  Phase 5
                </Badge>
              </h1>
              <p className="text-xs text-muted-foreground">
                5-dimensional algorithmic scoring & Gemini gap analysis comparing your profile against live jobs
              </p>
            </div>
          </div>
        </div>

        {/* Global Action & Last Run Telemetry */}
        <div className="flex flex-wrap items-center gap-2.5">
          {lastRunResult && (
            <div className="hidden lg:flex items-center gap-2 rounded-lg bg-card/60 border border-border/50 px-3 py-1.5 text-xs text-muted-foreground">
              <Cpu className="h-3.5 w-3.5 text-emerald-400" />
              <span>
                Scored <strong className="text-foreground">{lastRunResult.totalEvaluated}</strong> jobs in{' '}
                <strong className="text-foreground">{lastRunResult.durationMs}ms</strong>
              </span>
            </div>
          )}

          <Button
            variant="default"
            size="sm"
            onClick={() => runMatching({ limit: 500 })}
            disabled={runningMatch}
            className="h-9 px-4 text-xs bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-md font-medium"
          >
            <Sparkles className={`mr-1.5 h-3.5 w-3.5 ${runningMatch ? 'animate-spin' : ''}`} />
            {runningMatch ? 'Scoring Jobs...' : 'Run Matching'}
          </Button>
        </div>
      </div>

      {/* Error Alert Display */}
      {error && (
        <div className="rounded-xl border border-destructive/30 bg-destructive/10 p-4 text-xs text-destructive flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
          <Button variant="ghost" size="sm" onClick={clearError} className="h-7 text-xs">
            Dismiss
          </Button>
        </div>
      )}

      {/* Loading Skeleton */}
      {loading && results.length === 0 ? (
        <MatchingSkeleton />
      ) : (
        <div className="space-y-6">
          {/* Top Recommendations Showcase */}
          {topMatches.length > 0 && !hasActiveFilters && (
            <TopMatchesShowcase matches={topMatches} />
          )}

          {/* Faceted Filters Toolbar */}
          <MatchFiltersBar />

          {/* Results Summary & Table */}
          {results.length > 0 ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs text-muted-foreground px-1">
                <span>
                  Showing <strong className="text-foreground">{results.length}</strong> of{' '}
                  <strong className="text-foreground">{total}</strong> evaluated matches
                </span>
                <span className="flex items-center gap-1 font-mono text-[11px]">
                  <TrendingUp className="h-3.5 w-3.5 text-primary" /> Sorted by fit score
                </span>
              </div>

              <MatchResultsTable matches={results} />

              {/* Pagination Bar */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between pt-2 px-1">
                  <span className="text-xs text-muted-foreground font-mono">
                    Page {page} of {totalPages}
                  </span>

                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage(page - 1)}
                      disabled={page <= 1 || loading}
                      className="h-8 px-2.5 text-xs"
                    >
                      <ChevronLeft className="h-3.5 w-3.5 mr-1" /> Previous
                    </Button>

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage(page + 1)}
                      disabled={page >= totalPages || loading}
                      className="h-8 px-2.5 text-xs"
                    >
                      Next <ChevronRight className="h-3.5 w-3.5 ml-1" />
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <MatchingEmptyState isFiltered={hasActiveFilters} />
          )}
        </div>
      )}

      {/* Expandable Analysis Modal */}
      <MatchAnalysisModal
        match={selectedResult}
        isOpen={Boolean(selectedResult)}
        onClose={() => selectResult(null)}
      />
    </div>
  );
}
