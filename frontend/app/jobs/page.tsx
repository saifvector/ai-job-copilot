'use client';

import React, { useEffect } from 'react';
import { useJobStore } from '@/store/job-store';
import {
  JobSearchBar,
  JobFiltersBar,
  JobsTable,
  JobDetailsModal,
  JobsSkeleton,
  JobsEmptyState,
} from '@/features/job-discovery';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Briefcase,
  RefreshCw,
  Sparkles,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Layers,
  CheckCircle2,
} from 'lucide-react';

export default function JobsPage() {
  const {
    jobs,
    total,
    page,
    pageSize,
    totalPages,
    selectedJob,
    filters,
    loading,
    syncing,
    error,
    syncResult,
    fetchJobs,
    searchJobs,
    setFilters,
    resetFilters,
    selectJob,
    syncJobs,
    setPage,
    resetError,
  } = useJobStore();

  useEffect(() => {
    // Initial fetch on mount
    fetchJobs();
  }, [fetchJobs]);

  const handleSearch = (query: string) => {
    searchJobs({ query, page: 1 });
  };

  const handleFilterChange = (newFilters: Parameters<typeof setFilters>[0]) => {
    setFilters(newFilters);
    searchJobs(newFilters);
  };

  const handleSync = async () => {
    await syncJobs();
  };

  const hasActiveFilters = Boolean(
    filters.query ||
    filters.role ||
    filters.location ||
    filters.source ||
    filters.minSalary ||
    (filters.sortBy && filters.sortBy !== 'newest')
  );

  return (
    <div className="container max-w-7xl mx-auto py-8 px-4 sm:px-6 space-y-8 animate-fade-in">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border/40 pb-6">
        <div className="space-y-1">
          <div className="flex items-center gap-2.5">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary shadow-sm">
              <Briefcase className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold tracking-tight text-foreground">
                  Job Discovery Engine
                </h1>
                <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20 text-xs">
                  Phase 4
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">
                Aggregated, normalized, and deduplicated positions from RemoteOK, Greenhouse, Lever, and Wellfound.
              </p>
            </div>
          </div>
        </div>

        {/* Sync Action Controls */}
        <div className="flex items-center gap-3">
          <Button
            onClick={handleSync}
            disabled={syncing || loading}
            variant="default"
            className="gap-2 bg-gradient-to-r from-primary to-indigo-600 hover:from-primary/90 hover:to-indigo-500 shadow-md text-white font-medium"
          >
            <RefreshCw className={`h-4 w-4 ${syncing ? 'animate-spin' : ''}`} />
            <span>{syncing ? 'Syncing Sources...' : 'Sync All Sources'}</span>
          </Button>
        </div>
      </div>

      {/* Sync Success Alert */}
      {syncResult && (
        <div className="flex items-center justify-between gap-3 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-emerald-800 dark:text-emerald-300 text-sm shadow-sm animate-fade-in">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600 dark:text-emerald-400" />
            <span>{syncResult.message}</span>
          </div>
        </div>
      )}

      {/* Error Alert */}
      {error && (
        <div className="flex items-center justify-between gap-3 rounded-xl border border-destructive/30 bg-destructive/10 p-4 text-destructive text-sm shadow-sm animate-fade-in">
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
          <Button variant="ghost" size="sm" onClick={resetError} className="h-7 text-xs">
            Dismiss
          </Button>
        </div>
      )}

      {/* Search Input */}
      <JobSearchBar
        initialQuery={filters.query || ''}
        onSearch={handleSearch}
        loading={loading}
      />

      {/* Filter and Sorting Options Bar */}
      <JobFiltersBar
        filters={filters}
        onChange={handleFilterChange}
        onReset={resetFilters}
        loading={loading}
      />

      {/* Results Header */}
      <div className="flex items-center justify-between text-xs text-muted-foreground px-1">
        <span className="font-medium text-foreground">
          Showing {jobs.length} {jobs.length === 1 ? 'job' : 'jobs'} (out of {total.toLocaleString()} total)
        </span>
        {totalPages > 1 && (
          <span>
            Page {page} of {totalPages}
          </span>
        )}
      </div>

      {/* Main Content Area */}
      {loading ? (
        <JobsSkeleton />
      ) : jobs.length > 0 ? (
        <div className="space-y-6">
          <JobsTable
            jobs={jobs}
            onSelectJob={(job) => selectJob(job)}
          />

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between border-t border-border/40 pt-4">
              <Button
                variant="outline"
                size="sm"
                disabled={page <= 1 || loading}
                onClick={() => setPage(page - 1)}
                className="gap-1.5 text-xs"
              >
                <ChevronLeft className="h-4 w-4" />
                <span>Previous</span>
              </Button>

              <span className="text-xs text-muted-foreground font-medium">
                Page {page} of {totalPages}
              </span>

              <Button
                variant="outline"
                size="sm"
                disabled={page >= totalPages || loading}
                onClick={() => setPage(page + 1)}
                className="gap-1.5 text-xs"
              >
                <span>Next</span>
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>
      ) : (
        <JobsEmptyState
          hasFilters={hasActiveFilters}
          onReset={resetFilters}
          onSync={handleSync}
          syncing={syncing}
        />
      )}

      {/* Job Details Modal */}
      <JobDetailsModal
        job={selectedJob}
        isOpen={Boolean(selectedJob)}
        onClose={() => selectJob(null)}
      />
    </div>
  );
}
