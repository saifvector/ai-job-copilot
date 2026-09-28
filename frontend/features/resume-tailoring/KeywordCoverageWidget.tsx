'use client';

import React, { useState } from 'react';
import { KeywordAnalysis } from '@/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Check, AlertTriangle, Search, ShieldCheck } from 'lucide-react';

interface KeywordCoverageWidgetProps {
  analysis?: KeywordAnalysis;
  className?: string;
}

export const KeywordCoverageWidget: React.FC<KeywordCoverageWidgetProps> = ({
  analysis,
  className = '',
}) => {
  const [filterQuery, setFilterQuery] = useState('');

  if (!analysis) {
    return null;
  }

  const coverage = analysis.coveragePercentage || 0;
  const matched = analysis.matchedKeywords || [];
  const missing = analysis.missingKeywords || [];

  const filteredMatched = matched.filter((kw) =>
    kw.toLowerCase().includes(filterQuery.toLowerCase())
  );
  const filteredMissing = missing.filter((kw) =>
    kw.toLowerCase().includes(filterQuery.toLowerCase())
  );

  return (
    <Card className={`border shadow-sm ${className}`}>
      <CardHeader className="pb-3 border-b border-border/40">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-500" />
            Keyword Alignment & Coverage
          </CardTitle>
          <span className="text-xs font-semibold text-muted-foreground">
            {matched.length} of {matched.length + missing.length} Matched
          </span>
        </div>
      </CardHeader>
      <CardContent className="pt-4 space-y-4">
        {/* Coverage Progress Bar */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs font-medium">
            <span className="text-muted-foreground">Overall Keyword Match</span>
            <span className="font-bold text-foreground">{Math.round(coverage)}%</span>
          </div>
          <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                coverage >= 80 ? 'bg-emerald-500' : coverage >= 60 ? 'bg-blue-500' : 'bg-amber-500'
              }`}
              style={{ width: `${Math.min(100, Math.max(0, coverage))}%` }}
            />
          </div>
        </div>

        {/* Filter Input */}
        {(matched.length > 6 || missing.length > 6) && (
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search keywords..."
              value={filterQuery}
              onChange={(e) => setFilterQuery(e.target.value)}
              className="pl-8 h-8 text-xs bg-muted/20"
            />
          </div>
        )}

        {/* Matched Keywords */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5">
              <Check className="w-3.5 h-3.5" />
              Verified Matched Keywords ({matched.length})
            </span>
          </div>
          <div className="flex flex-wrap gap-1.5 max-h-36 overflow-y-auto pr-1">
            {filteredMatched.length > 0 ? (
              filteredMatched.map((kw) => (
                <Badge
                  key={kw}
                  variant="outline"
                  className="bg-emerald-50 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800 text-[11px] font-normal py-0.5"
                >
                  {kw}
                </Badge>
              ))
            ) : (
              <span className="text-xs text-muted-foreground italic">No matched keywords</span>
            )}
          </div>
        </div>

        {/* Missing Keywords (Truthfulness Protected) */}
        <div className="space-y-2 pt-2 border-t border-border/40">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-amber-600 dark:text-amber-400 flex items-center gap-1.5">
              <AlertTriangle className="w-3.5 h-3.5" />
              Missing Job Keywords ({missing.length})
            </span>
          </div>
          <p className="text-[11px] text-muted-foreground leading-tight">
            These keywords from the job description are not in your verified record. They were intentionally
            omitted to maintain 100% truthfulness.
          </p>
          <div className="flex flex-wrap gap-1.5 max-h-36 overflow-y-auto pr-1">
            {filteredMissing.length > 0 ? (
              filteredMissing.map((kw) => (
                <Badge
                  key={kw}
                  variant="outline"
                  className="bg-amber-50 dark:bg-amber-950/30 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800 text-[11px] font-normal py-0.5"
                >
                  {kw}
                </Badge>
              ))
            ) : (
              <span className="text-xs text-muted-foreground italic">No missing keywords</span>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
