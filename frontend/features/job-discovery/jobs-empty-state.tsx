'use client';

import React from 'react';
import { Briefcase, RotateCcw, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface JobsEmptyStateProps {
  hasFilters: boolean;
  onReset: () => void;
  onSync: () => void;
  syncing?: boolean;
}

export function JobsEmptyState({ hasFilters, onReset, onSync, syncing = false }: JobsEmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border/80 bg-card/40 p-12 text-center space-y-4 shadow-sm">
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary">
        <Briefcase className="h-7 w-7" />
      </div>

      <div className="space-y-1.5 max-w-md">
        <h3 className="text-lg font-semibold text-foreground">
          {hasFilters ? 'No jobs match your filter criteria' : 'No jobs found in discovery engine'}
        </h3>
        <p className="text-sm text-muted-foreground">
          {hasFilters
            ? 'Try widening your search terms, removing location constraints, or lowering your minimum salary threshold.'
            : 'Synchronize listings from RemoteOK, Greenhouse, Lever, and Wellfound to populate your feed.'}
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-3 pt-2">
        {hasFilters && (
          <Button variant="outline" size="sm" onClick={onReset} className="gap-2">
            <RotateCcw className="h-4 w-4" />
            <span>Reset All Filters</span>
          </Button>
        )}

        <Button
          size="sm"
          onClick={onSync}
          disabled={syncing}
          className="gap-2 bg-gradient-to-r from-primary to-indigo-600 hover:from-primary/90 hover:to-indigo-500 text-white shadow-sm"
        >
          <RefreshCw className={`h-4 w-4 ${syncing ? 'animate-spin' : ''}`} />
          <span>{syncing ? 'Synchronizing...' : 'Sync Jobs Now'}</span>
        </Button>
      </div>
    </div>
  );
}
