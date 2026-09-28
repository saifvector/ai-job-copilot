'use client';

import React from 'react';
import {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Job } from '@/types';
import {
  Building2,
  MapPin,
  DollarSign,
  Calendar,
  ExternalLink,
  ChevronRight,
  Globe,
} from 'lucide-react';

interface JobsTableProps {
  jobs: Job[];
  onSelectJob: (job: Job) => void;
}

function formatSalary(min?: number | null, max?: number | null, currency: string = 'USD'): string {
  if (!min && !max) return 'Competitive';
  const symbol = currency === 'USD' ? '$' : currency + ' ';
  if (min && max) {
    return `${symbol}${(min / 1000).toFixed(0)}k – ${symbol}${(max / 1000).toFixed(0)}k`;
  }
  if (min) return `${symbol}${(min / 1000).toFixed(0)}k+`;
  if (max) return `Up to ${symbol}${(max / 1000).toFixed(0)}k`;
  return 'Competitive';
}

function formatDate(dateStr?: string | null): string {
  if (!dateStr) return 'Recent';
  try {
    const d = new Date(dateStr);
    const now = new Date();
    const diffDays = Math.floor((now.getTime() - d.getTime()) / (1000 * 3600 * 24));
    if (diffDays <= 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  } catch {
    return 'Recent';
  }
}

function getSourceBadgeClass(source: string): string {
  switch (source.toLowerCase()) {
    case 'remoteok':
      return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20';
    case 'greenhouse':
      return 'bg-teal-500/10 text-teal-600 dark:text-teal-400 border-teal-500/20';
    case 'lever':
      return 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20';
    case 'wellfound':
      return 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20';
    default:
      return 'bg-primary/10 text-primary border-primary/20';
  }
}

export function JobsTable({ jobs, onSelectJob }: JobsTableProps) {
  return (
    <div className="w-full space-y-4">
      {/* Desktop Table View */}
      <div className="hidden md:block overflow-hidden rounded-2xl border border-border/60 bg-card/40 backdrop-blur-sm shadow-sm">
        <Table>
          <TableHeader>
            <TableRow className="border-b border-border/60 bg-muted/30">
              <TableHead className="font-semibold text-foreground py-3.5">Job Title</TableHead>
              <TableHead className="font-semibold text-foreground">Company</TableHead>
              <TableHead className="font-semibold text-foreground">Location</TableHead>
              <TableHead className="font-semibold text-foreground">Salary</TableHead>
              <TableHead className="font-semibold text-foreground">Source</TableHead>
              <TableHead className="font-semibold text-foreground">Posted Date</TableHead>
              <TableHead className="text-right font-semibold text-foreground pr-4">Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {jobs.map((job) => {
              const isRemote = job.location.toLowerCase().includes('remote');
              return (
                <TableRow
                  key={job.id}
                  onClick={() => onSelectJob(job)}
                  className="cursor-pointer transition-colors hover:bg-muted/40 border-b border-border/40 group"
                >
                  {/* Job Title & Tech Badges */}
                  <TableCell className="py-4">
                    <div className="space-y-1">
                      <div className="font-semibold text-foreground group-hover:text-primary transition-colors flex items-center gap-2">
                        <span>{job.title}</span>
                        {job.employmentType && (
                          <Badge variant="outline" className="text-[10px] py-0 px-1.5 font-normal text-muted-foreground border-border/60">
                            {job.employmentType}
                          </Badge>
                        )}
                      </div>
                      {job.skills && job.skills.length > 0 && (
                        <div className="flex flex-wrap gap-1 max-w-md">
                          {job.skills.slice(0, 3).map((sk) => (
                            <span
                              key={sk}
                              className="inline-block text-[10px] font-medium bg-secondary/60 text-secondary-foreground px-1.5 py-0.5 rounded-md"
                            >
                              {sk}
                            </span>
                          ))}
                          {job.skills.length > 3 && (
                            <span className="text-[10px] text-muted-foreground self-center">
                              +{job.skills.length - 3}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </TableCell>

                  {/* Company */}
                  <TableCell>
                    <div className="flex items-center gap-1.5 font-medium text-foreground">
                      <Building2 className="h-3.5 w-3.5 text-muted-foreground" />
                      <span>{job.company}</span>
                    </div>
                  </TableCell>

                  {/* Location */}
                  <TableCell>
                    <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                      <MapPin className="h-3.5 w-3.5 text-muted-foreground" />
                      <span className="max-w-[140px] truncate">{job.location}</span>
                      {isRemote && (
                        <Badge variant="secondary" className="text-[9px] bg-primary/10 text-primary py-0 px-1">
                          Remote
                        </Badge>
                      )}
                    </div>
                  </TableCell>

                  {/* Salary */}
                  <TableCell>
                    <div className="flex items-center gap-1 text-xs font-semibold text-foreground">
                      <DollarSign className="h-3.5 w-3.5 text-emerald-500" />
                      <span>{formatSalary(job.salaryMin, job.salaryMax, job.currency || 'USD')}</span>
                    </div>
                  </TableCell>

                  {/* Source */}
                  <TableCell>
                    <Badge variant="outline" className={`text-[11px] font-medium ${getSourceBadgeClass(job.source)}`}>
                      {job.source}
                    </Badge>
                  </TableCell>

                  {/* Posted Date */}
                  <TableCell>
                    <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                      <Calendar className="h-3.5 w-3.5" />
                      <span>{formatDate(job.postedAt || job.createdAt)}</span>
                    </div>
                  </TableCell>

                  {/* Action */}
                  <TableCell className="text-right pr-4">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectJob(job);
                      }}
                      className="h-8 px-2.5 text-xs text-muted-foreground hover:text-foreground gap-1"
                    >
                      <span>View</span>
                      <ChevronRight className="h-3.5 w-3.5" />
                    </Button>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>

      {/* Mobile Card Fallback View */}
      <div className="grid grid-cols-1 gap-3 md:hidden">
        {jobs.map((job) => (
          <div
            key={job.id}
            onClick={() => onSelectJob(job)}
            className="rounded-2xl border border-border/60 bg-card p-4 shadow-sm hover:border-primary/40 transition-all cursor-pointer space-y-3"
          >
            <div className="flex items-start justify-between gap-2">
              <div className="space-y-0.5">
                <h4 className="text-sm font-semibold text-foreground line-clamp-1">{job.title}</h4>
                <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <Building2 className="h-3 w-3" />
                  <span>{job.company}</span>
                </div>
              </div>
              <Badge variant="outline" className={`text-[10px] shrink-0 ${getSourceBadgeClass(job.source)}`}>
                {job.source}
              </Badge>
            </div>

            <div className="flex flex-wrap items-center gap-y-1 gap-x-3 text-xs text-muted-foreground pt-1">
              <span className="flex items-center gap-1">
                <MapPin className="h-3.5 w-3.5" />
                {job.location}
              </span>
              <span className="flex items-center gap-1 font-semibold text-emerald-500">
                <DollarSign className="h-3.5 w-3.5" />
                {formatSalary(job.salaryMin, job.salaryMax, job.currency || 'USD')}
              </span>
              <span className="flex items-center gap-1">
                <Calendar className="h-3.5 w-3.5" />
                {formatDate(job.postedAt || job.createdAt)}
              </span>
            </div>

            {job.skills && job.skills.length > 0 && (
              <div className="flex flex-wrap gap-1 pt-1">
                {job.skills.slice(0, 4).map((sk) => (
                  <span
                    key={sk}
                    className="text-[10px] bg-secondary/60 text-secondary-foreground px-1.5 py-0.5 rounded-md"
                  >
                    {sk}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
