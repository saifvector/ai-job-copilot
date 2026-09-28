'use client';

import * as React from 'react';
import {
  ExternalLink,
  ChevronRight,
  MapPin,
  Building,
  DollarSign,
  Briefcase,
  Sparkles,
} from 'lucide-react';
import {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button, buttonVariants } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { CircularScoreIndicator, getScoreCategory } from './score-indicator';
import { MatchResult } from '@/types';
import { useMatchingStore } from '@/store/matching-store';

interface MatchResultsTableProps {
  matches: MatchResult[];
}

export function MatchResultsTable({ matches }: MatchResultsTableProps) {
  const { selectResult } = useMatchingStore();

  const getSourceBadge = (source: string) => {
    switch (source.toLowerCase()) {
      case 'remoteok':
        return <Badge className="bg-red-500/15 text-red-400 border-red-500/30 text-[10px]">RemoteOK</Badge>;
      case 'greenhouse':
        return <Badge className="bg-emerald-500/15 text-emerald-400 border-emerald-500/30 text-[10px]">Greenhouse</Badge>;
      case 'lever':
        return <Badge className="bg-blue-500/15 text-blue-400 border-blue-500/30 text-[10px]">Lever</Badge>;
      case 'wellfound':
        return <Badge className="bg-purple-500/15 text-purple-400 border-purple-500/30 text-[10px]">Wellfound</Badge>;
      default:
        return <Badge variant="outline" className="text-[10px]">{source}</Badge>;
    }
  };

  return (
    <div className="overflow-hidden rounded-xl border border-border/70 bg-card/40 shadow-sm backdrop-blur-sm">
      <Table>
        <TableHeader>
          <TableRow className="border-border/60 hover:bg-transparent">
            <TableHead className="w-[110px] text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Match Fit
            </TableHead>
            <TableHead className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Job Title & Details
            </TableHead>
            <TableHead className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Company
            </TableHead>
            <TableHead className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Location
            </TableHead>
            <TableHead className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Source
            </TableHead>
            <TableHead className="w-[140px] text-right text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Actions
            </TableHead>
          </TableRow>
        </TableHeader>

        <TableBody>
          {matches.map((item) => {
            const job = item.job;
            if (!job) return null;

            const hasSalary = job.salaryMin || job.salaryMax;
            const salaryText = hasSalary
              ? `$${((job.salaryMin || 0) / 1000).toFixed(0)}k - $${((job.salaryMax || 0) / 1000).toFixed(0)}k`
              : null;

            const { label, badgeClass } = getScoreCategory(item.overallScore);

            return (
              <TableRow
                key={item.id}
                className="border-border/50 hover:bg-accent/40 transition-colors cursor-pointer group"
                onClick={() => selectResult(item)}
              >
                {/* Match % Column */}
                <TableCell className="py-3">
                  <div className="flex flex-col items-start gap-1">
                    <CircularScoreIndicator score={item.overallScore} size={42} strokeWidth={3.5} />
                    <span className={`text-[10px] px-1.5 py-0.2 rounded-full border font-medium ${badgeClass}`}>
                      {label}
                    </span>
                  </div>
                </TableCell>

                {/* Job Title Column */}
                <TableCell className="py-3">
                  <div className="space-y-1">
                    <div className="font-semibold text-foreground text-sm group-hover:text-primary transition-colors flex items-center gap-1.5">
                      {job.title}
                      {job.employmentType && (
                        <span className="text-[10px] font-normal text-muted-foreground font-mono bg-muted/60 px-1.5 py-0.5 rounded border border-border/40">
                          {job.employmentType}
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      {salaryText && (
                        <span className="inline-flex items-center gap-0.5 font-medium text-emerald-400">
                          <DollarSign className="h-3 w-3" />
                          {salaryText}
                        </span>
                      )}
                      {item.missingSkills && item.missingSkills.length > 0 && (
                        <span className="text-[11px] text-muted-foreground">
                          • {item.missingSkills.length} missing skill{item.missingSkills.length > 1 ? 's' : ''}
                        </span>
                      )}
                    </div>
                  </div>
                </TableCell>

                {/* Company Column */}
                <TableCell className="py-3">
                  <div className="flex items-center gap-1.5 text-xs font-medium text-foreground">
                    <Building className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                    <span>{job.company}</span>
                  </div>
                </TableCell>

                {/* Location Column */}
                <TableCell className="py-3">
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <MapPin className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                    <span className="truncate max-w-[140px]">{job.location}</span>
                  </div>
                </TableCell>

                {/* Source Column */}
                <TableCell className="py-3">
                  {getSourceBadge(job.source)}
                </TableCell>

                {/* Actions Column */}
                <TableCell className="py-3 text-right">
                  <div
                    className="flex items-center justify-end gap-1.5"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => selectResult(item)}
                      className="h-8 px-2.5 text-xs border-border/70 hover:bg-primary/10 hover:text-primary"
                    >
                      <Sparkles className="h-3.5 w-3.5 mr-1" />
                      Analysis
                    </Button>

                    <a
                      href={job.applyUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      title="Open external job application"
                      className={cn(
                        buttonVariants({ variant: 'ghost', size: 'sm' }),
                        'h-8 w-8 p-0 text-muted-foreground hover:text-foreground inline-flex items-center justify-center'
                      )}
                    >
                      <ExternalLink className="h-3.5 w-3.5" />
                    </a>
                  </div>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}
