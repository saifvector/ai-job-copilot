'use client';

import * as React from 'react';
import {
  ExternalLink,
  CheckCircle2,
  AlertTriangle,
  Lightbulb,
  Building,
  MapPin,
  DollarSign,
  Sparkles,
  Briefcase,
  GraduationCap,
  Calendar,
} from 'lucide-react';
import { Modal } from '@/components/ui/modal';
import { Badge } from '@/components/ui/badge';
import { Button, buttonVariants } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { CircularScoreIndicator, ScoreProgressBar } from './score-indicator';
import { MatchResult } from '@/types';
import { useMatchingStore } from '@/store/matching-store';

interface MatchAnalysisModalProps {
  match: MatchResult | null;
  isOpen: boolean;
  onClose: () => void;
}

export function MatchAnalysisModal({
  match,
  isOpen,
  onClose,
}: MatchAnalysisModalProps) {
  const { enrichJobMatch, enrichingJobId } = useMatchingStore();

  if (!match || !match.job) return null;
  const job = match.job;

  const isEnriching = enrichingJobId === match.jobId;

  const hasSalary = job.salaryMin || job.salaryMax;
  const salaryText = hasSalary
    ? `$${((job.salaryMin || 0) / 1000).toFixed(0)}k - $${((job.salaryMax || 0) / 1000).toFixed(0)}k`
    : null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title=""
      className="max-w-3xl max-h-[88vh] overflow-y-auto p-0"
    >
      <div className="p-6 space-y-6">
        {/* Header Header Info */}
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 border-b border-border/60 pb-5">
          <div className="space-y-1.5 flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="outline" className="text-xs font-mono font-medium">
                {job.source}
              </Badge>
              {job.employmentType && (
                <span className="text-xs text-muted-foreground bg-muted/60 px-2 py-0.5 rounded border border-border/40">
                  {job.employmentType}
                </span>
              )}
            </div>
            <h2 className="text-xl font-bold tracking-tight text-foreground">{job.title}</h2>
            <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground pt-0.5">
              <span className="inline-flex items-center gap-1 font-medium text-foreground">
                <Building className="h-3.5 w-3.5 text-muted-foreground" />
                {job.company}
              </span>
              <span>•</span>
              <span className="inline-flex items-center gap-1">
                <MapPin className="h-3.5 w-3.5 text-muted-foreground" />
                {job.location}
              </span>
              {salaryText && (
                <>
                  <span>•</span>
                  <span className="inline-flex items-center gap-1 font-semibold text-emerald-400">
                    <DollarSign className="h-3.5 w-3.5" />
                    {salaryText}
                  </span>
                </>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => enrichJobMatch(match.jobId)}
              disabled={isEnriching}
              className="h-9 px-3 text-xs border-primary/30 text-primary hover:bg-primary/10"
            >
              <Sparkles className={`h-3.5 w-3.5 mr-1.5 ${isEnriching ? 'animate-spin' : ''}`} />
              {isEnriching ? 'Analyzing...' : 'Enrich with Gemini'}
            </Button>
            <a
              href={job.applyUrl}
              target="_blank"
              rel="noopener noreferrer"
              className={cn(buttonVariants({ size: 'sm' }), 'h-9 px-4 text-xs font-medium inline-flex items-center gap-1.5')}
            >
              Apply Now <ExternalLink className="h-3.5 w-3.5" />
            </a>
          </div>
        </div>

        {/* Score Breakdown Hero Panel */}
        <div className="rounded-xl border border-border/70 bg-gradient-to-r from-card/90 to-card/40 p-5 shadow-sm">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-4">
            AI Match Score Architecture
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
            {/* Overall Score Gauge */}
            <div className="flex flex-col items-center justify-center p-3 border-b md:border-b-0 md:border-r border-border/60">
              <CircularScoreIndicator score={match.overallScore} size={92} strokeWidth={7} />
              <span className="text-xs font-semibold mt-2.5 text-foreground">
                Overall Composite Fit
              </span>
              <p className="text-[11px] text-muted-foreground text-center mt-0.5">
                Weighted across 5 intelligence dimensions
              </p>
            </div>

            {/* Individual Criteria Progress Bars */}
            <div className="md:col-span-2 space-y-3">
              <ScoreProgressBar
                label="Technical Skills"
                weightLabel="50%"
                score={match.skillScore}
              />
              <ScoreProgressBar
                label="Experience Alignment"
                weightLabel="20%"
                score={match.experienceScore}
              />
              <ScoreProgressBar
                label="Role Title Relevance"
                weightLabel="15%"
                score={match.roleScore}
              />
              <ScoreProgressBar
                label="Location & Workplace"
                weightLabel="10%"
                score={match.locationScore}
              />
              <ScoreProgressBar
                label="Education Credentials"
                weightLabel="5%"
                score={match.educationScore}
              />
            </div>
          </div>
        </div>

        {/* Gap Analysis Tabs / Columns */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {/* Why Recommended: Strengths */}
          <div className="space-y-3 rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4">
            <div className="flex items-center gap-2 text-emerald-400 font-semibold text-xs tracking-wide uppercase">
              <CheckCircle2 className="h-4 w-4 text-emerald-500" />
              Candidate Strengths
            </div>
            <ul className="space-y-2">
              {match.strengths && match.strengths.length > 0 ? (
                match.strengths.map((str, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-xs text-foreground/90 leading-relaxed">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0" />
                    <span>{str}</span>
                  </li>
                ))
              ) : (
                <li className="text-xs text-muted-foreground italic">No specific strengths cataloged yet.</li>
              )}
            </ul>
          </div>

          {/* Missing Skills */}
          <div className="space-y-3 rounded-xl border border-amber-500/20 bg-amber-500/5 p-4">
            <div className="flex items-center gap-2 text-amber-400 font-semibold text-xs tracking-wide uppercase">
              <AlertTriangle className="h-4 w-4 text-amber-500" />
              Missing Job Requirements ({match.missingSkills.length})
            </div>
            {match.missingSkills && match.missingSkills.length > 0 ? (
              <div className="flex flex-wrap gap-1.5 pt-1">
                {match.missingSkills.map((skill, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center text-xs px-2.5 py-1 rounded-md bg-amber-500/10 text-amber-300 border border-amber-500/25 font-medium"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-emerald-400 font-medium">
                All identified technical skills are satisfied by your profile!
              </p>
            )}
          </div>
        </div>

        {/* Improvement Recommendations */}
        <div className="space-y-3 rounded-xl border border-blue-500/20 bg-blue-500/5 p-4">
          <div className="flex items-center gap-2 text-blue-400 font-semibold text-xs tracking-wide uppercase">
            <Lightbulb className="h-4 w-4 text-blue-500" />
            AI Improvement Recommendations
          </div>
          <div className="grid grid-cols-1 gap-2.5">
            {match.recommendations && match.recommendations.length > 0 ? (
              match.recommendations.map((rec, idx) => (
                <div
                  key={idx}
                  className="rounded-lg bg-card/60 border border-border/50 p-3 text-xs text-foreground flex items-start gap-2.5"
                >
                  <span className="flex h-5 w-5 items-center justify-center rounded-full bg-blue-500/15 text-blue-400 font-mono text-[10px] font-bold shrink-0 mt-0.5">
                    {idx + 1}
                  </span>
                  <span className="leading-relaxed">{rec}</span>
                </div>
              ))
            ) : (
              <p className="text-xs text-muted-foreground italic">No recommendations generated.</p>
            )}
          </div>
        </div>

        {/* Job Description Excerpt */}
        {job.description && (
          <div className="space-y-2 border-t border-border/60 pt-4">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Job Description Preview
            </h4>
            <div className="rounded-lg bg-muted/20 border border-border/40 p-4 text-xs text-muted-foreground leading-relaxed max-h-48 overflow-y-auto whitespace-pre-wrap">
              {job.description}
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
}
