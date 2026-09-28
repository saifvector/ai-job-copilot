'use client';

import React from 'react';
import { Skeleton } from '@/components/ui/loader';

export function JobsSkeleton() {
  return (
    <div className="w-full space-y-3">
      {/* Table Skeleton Header */}
      <div className="hidden md:grid grid-cols-6 gap-4 p-4 rounded-xl border border-border/40 bg-muted/20">
        <Skeleton className="h-4 w-28" />
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-4 w-20" />
        <Skeleton className="h-4 w-20" />
        <Skeleton className="h-4 w-16" />
        <Skeleton className="h-4 w-16 ml-auto" />
      </div>

      {/* Row Skeletons */}
      {Array.from({ length: 6 }).map((_, idx) => (
        <div
          key={idx}
          className="rounded-xl border border-border/40 bg-card/60 p-4 space-y-2.5 animate-pulse"
        >
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="space-y-1.5 flex-1">
              <Skeleton className="h-5 w-64" />
              <div className="flex items-center gap-2">
                <Skeleton className="h-3.5 w-28" />
                <Skeleton className="h-3.5 w-20" />
              </div>
            </div>
            <Skeleton className="h-6 w-20 rounded-full" />
          </div>
          <div className="flex items-center gap-2 pt-1">
            <Skeleton className="h-4 w-16 rounded-md" />
            <Skeleton className="h-4 w-16 rounded-md" />
            <Skeleton className="h-4 w-16 rounded-md" />
          </div>
        </div>
      ))}
    </div>
  );
}
