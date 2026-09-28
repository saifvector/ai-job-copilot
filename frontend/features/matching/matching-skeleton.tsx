'use client';

import * as React from 'react';

export function MatchingSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      {/* Top showcase cards skeleton */}
      <div className="space-y-3">
        <div className="h-5 w-48 bg-muted/60 rounded" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-44 rounded-xl border border-border/60 bg-card/40 p-4 space-y-3">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-full bg-muted/70" />
                <div className="space-y-2 flex-1">
                  <div className="h-4 w-3/4 bg-muted/70 rounded" />
                  <div className="h-3 w-1/2 bg-muted/50 rounded" />
                </div>
              </div>
              <div className="h-12 w-full bg-muted/30 rounded" />
            </div>
          ))}
        </div>
      </div>

      {/* Filter bar skeleton */}
      <div className="h-14 rounded-xl border border-border/60 bg-card/30" />

      {/* Table skeleton */}
      <div className="rounded-xl border border-border/60 bg-card/30 p-4 space-y-4">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="flex items-center justify-between py-2 border-b border-border/30">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-muted/60" />
              <div className="space-y-2">
                <div className="h-4 w-48 bg-muted/60 rounded" />
                <div className="h-3 w-32 bg-muted/40 rounded" />
              </div>
            </div>
            <div className="h-8 w-24 bg-muted/50 rounded" />
          </div>
        ))}
      </div>
    </div>
  );
}
