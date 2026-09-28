'use client';

import * as React from 'react';
import { MatchInsightItem } from '@/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Modal } from '@/components/ui/modal';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Bookmark,
  BookmarkCheck,
  Building2,
  Calendar,
  ExternalLink,
  Eye,
  Globe,
  MapPin,
  Sparkles,
  Target,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface MatchInsightsTableProps {
  matches: MatchInsightItem[];
  savedJobIds: string[];
  onToggleSave: (jobId: string) => void;
  loading?: boolean;
}

export function MatchInsightsTable({
  matches,
  savedJobIds,
  onToggleSave,
  loading,
}: MatchInsightsTableProps) {
  const [selectedJob, setSelectedJob] = React.useState<MatchInsightItem | null>(null);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Target className="h-4 w-4 text-primary" />
            Top 10 Match Insights
          </CardTitle>
          <CardDescription>Highest scoring role recommendations</CardDescription>
        </CardHeader>
        <CardContent className="p-6">
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-10 bg-muted/40 animate-pulse rounded-md" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const getScoreBadge = (score: number) => {
    if (score >= 85) {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold font-mono bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
          <Sparkles className="h-3 w-3 mr-1 inline" />
          {score}%
        </span>
      );
    }
    if (score >= 70) {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold font-mono bg-blue-500/10 text-blue-500 border border-blue-500/20">
          {score}%
        </span>
      );
    }
    if (score >= 50) {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold font-mono bg-amber-500/10 text-amber-500 border border-amber-500/20">
          {score}%
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold font-mono bg-rose-500/10 text-rose-500 border border-rose-500/20">
        {score}%
      </span>
    );
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'Recent';
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return 'Recent';
    return d.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <>
      <Card>
        <CardHeader className="pb-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <Target className="h-4 w-4 text-primary" />
                Match Insights: Top 10 Opportunities
              </CardTitle>
              <CardDescription>
                Ranked by AI matching compatibility across skills, experience, and role alignment
              </CardDescription>
            </div>
            <span className="text-xs text-muted-foreground self-start sm:self-auto">
              Showing top {matches.length} matches
            </span>
          </div>
        </CardHeader>

        <CardContent className="p-0">
          {matches.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground text-sm">
              No matching records found. Visit the AI Matching workspace to trigger an evaluation.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent">
                    <TableHead className="w-[30%]">Job Title</TableHead>
                    <TableHead>Company</TableHead>
                    <TableHead className="text-center">Match %</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>Source</TableHead>
                    <TableHead>Posted Date</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {matches.map((job) => {
                    const isSaved = savedJobIds.includes(job.jobId);

                    return (
                      <TableRow key={job.jobId} className="hover:bg-muted/30 transition-colors">
                        <TableCell className="font-medium text-foreground">
                          <div className="flex flex-col">
                            <span className="truncate font-semibold">{job.jobTitle}</span>
                            {job.salaryMin || job.salaryMax ? (
                              <span className="text-[11px] text-muted-foreground font-mono">
                                {job.currency || '$'}
                                {job.salaryMin?.toLocaleString()} - {job.currency || '$'}
                                {job.salaryMax?.toLocaleString()}
                              </span>
                            ) : null}
                          </div>
                        </TableCell>

                        <TableCell>
                          <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
                            <Building2 className="h-3.5 w-3.5 text-muted-foreground/70 shrink-0" />
                            <span className="truncate font-medium text-foreground">{job.company}</span>
                          </span>
                        </TableCell>

                        <TableCell className="text-center">
                          {getScoreBadge(job.matchScore)}
                        </TableCell>

                        <TableCell>
                          <span className="flex items-center gap-1 text-xs text-muted-foreground">
                            <MapPin className="h-3.5 w-3.5 text-muted-foreground/70 shrink-0" />
                            <span className="truncate">{job.location}</span>
                          </span>
                        </TableCell>

                        <TableCell>
                          <Badge variant="outline" className="text-[11px] font-mono capitalize">
                            {job.source}
                          </Badge>
                        </TableCell>

                        <TableCell className="text-xs text-muted-foreground whitespace-nowrap">
                          {formatDate(job.postedDate)}
                        </TableCell>

                        <TableCell className="text-right">
                          <div className="flex items-center justify-end gap-1.5">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setSelectedJob(job)}
                              className="h-8 px-2 text-xs text-muted-foreground hover:text-foreground"
                              title="View Match Details"
                            >
                              <Eye className="h-3.5 w-3.5 mr-1" />
                              Details
                            </Button>

                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => onToggleSave(job.jobId)}
                              className={cn(
                                'h-8 px-2 text-xs',
                                isSaved
                                  ? 'text-amber-500 hover:text-amber-600'
                                  : 'text-muted-foreground hover:text-foreground'
                              )}
                              title={isSaved ? 'Saved to bookmarks' : 'Save Job'}
                            >
                              {isSaved ? (
                                <BookmarkCheck className="h-4 w-4" />
                              ) : (
                                <Bookmark className="h-4 w-4" />
                              )}
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Detail Inspection Modal */}
      {selectedJob && (
        <Modal
          isOpen={!!selectedJob}
          onClose={() => setSelectedJob(null)}
          title={
            <div className="flex items-center gap-2">
              <span className="truncate font-bold">{selectedJob.jobTitle}</span>
              {getScoreBadge(selectedJob.matchScore)}
            </div>
          }
          description={`${selectedJob.company} • ${selectedJob.location}`}
          size="lg"
          footer={
            <div className="flex items-center justify-between w-full">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onToggleSave(selectedJob.jobId)}
                className="gap-1.5"
              >
                {savedJobIds.includes(selectedJob.jobId) ? (
                  <>
                    <BookmarkCheck className="h-4 w-4 text-amber-500" />
                    Saved
                  </>
                ) : (
                  <>
                    <Bookmark className="h-4 w-4" />
                    Save Opportunity
                  </>
                )}
              </Button>

              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={() => setSelectedJob(null)}>
                  Close
                </Button>
                {selectedJob.applyUrl && (
                  <a
                    href={selectedJob.applyUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center rounded-md text-xs font-semibold h-8 px-3 bg-primary text-primary-foreground hover:bg-primary/90"
                  >
                    Apply on {selectedJob.source}
                    <ExternalLink className="h-3 w-3 ml-1.5" />
                  </a>
                )}
              </div>
            </div>
          }
        >
          <div className="space-y-4 py-2 text-sm">
            {/* Metadata pills */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
              <div className="p-2.5 rounded-lg bg-muted/40">
                <span className="text-muted-foreground block text-[11px]">Location</span>
                <span className="font-semibold text-foreground flex items-center gap-1 mt-0.5">
                  <MapPin className="h-3 w-3 text-primary" />
                  {selectedJob.location}
                </span>
              </div>
              <div className="p-2.5 rounded-lg bg-muted/40">
                <span className="text-muted-foreground block text-[11px]">Job Source</span>
                <span className="font-semibold text-foreground flex items-center gap-1 mt-0.5">
                  <Globe className="h-3 w-3 text-indigo-500" />
                  {selectedJob.source}
                </span>
              </div>
              <div className="p-2.5 rounded-lg bg-muted/40">
                <span className="text-muted-foreground block text-[11px]">Posted</span>
                <span className="font-semibold text-foreground flex items-center gap-1 mt-0.5">
                  <Calendar className="h-3 w-3 text-cyan-500" />
                  {formatDate(selectedJob.postedDate)}
                </span>
              </div>
              <div className="p-2.5 rounded-lg bg-muted/40">
                <span className="text-muted-foreground block text-[11px]">Match Rating</span>
                <span className="font-semibold text-foreground flex items-center gap-1 mt-0.5">
                  <Target className="h-3 w-3 text-emerald-500" />
                  {selectedJob.matchScore}% Compatibility
                </span>
              </div>
            </div>

            {/* Missing Skills Warning */}
            {selectedJob.missingSkills && selectedJob.missingSkills.length > 0 && (
              <div className="p-3 rounded-lg border border-amber-500/20 bg-amber-500/5 space-y-1.5">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-amber-500">
                  <span>Identified Missing Skills for this Role:</span>
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {selectedJob.missingSkills.map((s) => (
                    <span
                      key={s}
                      className="px-2 py-0.5 rounded text-[11px] font-mono bg-amber-500/10 text-amber-500 border border-amber-500/20"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="text-xs text-muted-foreground">
              To view full AI explanations, dimensional score breakdowns (skill, experience, education, location),
              navigate to the <strong className="text-foreground">AI Matches</strong> workspace.
            </div>
          </div>
        </Modal>
      )}
    </>
  );
}
