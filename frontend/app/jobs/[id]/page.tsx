'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/navigation';
import { apiClient, ApiClientError } from '@/services/api-client';
import { Job } from '@/types';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/loader';
import {
  ArrowLeft,
  Building2,
  MapPin,
  DollarSign,
  Calendar,
  ExternalLink,
  Briefcase,
  Sparkles,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';

function formatSalary(min?: number | null, max?: number | null, currency: string = 'USD'): string {
  if (!min && !max) return 'Competitive compensation package';
  const symbol = currency === 'USD' ? '$' : currency + ' ';
  if (min && max) {
    return `${symbol}${min.toLocaleString()} – ${symbol}${max.toLocaleString()} / year`;
  }
  if (min) return `${symbol}${min.toLocaleString()}+ / year`;
  if (max) return `Up to ${symbol}${max.toLocaleString()} / year`;
  return 'Competitive compensation';
}

export default function JobDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;

  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadJob() {
      if (!id) return;
      setLoading(true);
      setError(null);
      try {
        const response = await apiClient.getJobById(id);
        setJob(response.data);
      } catch (err: unknown) {
        const msg = err instanceof ApiClientError ? err.message : 'Job posting not found';
        setError(msg);
      } finally {
        setLoading(false);
      }
    }
    loadJob();
  }, [id]);

  if (loading) {
    return (
      <div className="container max-w-4xl mx-auto py-10 px-4 space-y-6">
        <Skeleton className="h-8 w-32" />
        <Skeleton className="h-12 w-3/4" />
        <div className="grid grid-cols-2 gap-4">
          <Skeleton className="h-20 rounded-xl" />
          <Skeleton className="h-20 rounded-xl" />
        </div>
        <Skeleton className="h-64 rounded-xl" />
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="container max-w-md mx-auto py-16 px-4 text-center space-y-4">
        <div className="flex h-14 w-14 mx-auto items-center justify-center rounded-2xl bg-destructive/10 text-destructive">
          <AlertCircle className="h-7 w-7" />
        </div>
        <h2 className="text-xl font-bold text-foreground">Job Posting Not Found</h2>
        <p className="text-sm text-muted-foreground">{error || 'This job may have expired or been removed.'}</p>
        <Button onClick={() => router.push('/jobs')} variant="outline" className="gap-2">
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Jobs</span>
        </Button>
      </div>
    );
  }

  return (
    <div className="container max-w-4xl mx-auto py-10 px-4 sm:px-6 space-y-8 animate-fade-in">
      {/* Back button */}
      <div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push('/jobs')}
          className="gap-2 text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to All Jobs</span>
        </Button>
      </div>

      {/* Main Header Card */}
      <div className="rounded-2xl border border-border/60 bg-card p-6 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-2xl font-bold text-foreground">{job.title}</h1>
              <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20 text-xs">
                {job.source}
              </Badge>
            </div>

            <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
              <span className="flex items-center gap-1.5 font-semibold text-foreground">
                <Building2 className="h-4 w-4 text-primary" /> {job.company}
              </span>
              <span className="flex items-center gap-1.5">
                <MapPin className="h-4 w-4" /> {job.location}
              </span>
              {job.employmentType && (
                <span className="flex items-center gap-1.5">
                  <Briefcase className="h-4 w-4" /> {job.employmentType}
                </span>
              )}
            </div>
          </div>

          <Button
            size="lg"
            onClick={() => window.open(job.applyUrl, '_blank', 'noopener,noreferrer')}
            className="shrink-0 gap-2 bg-gradient-to-r from-primary to-indigo-600 hover:from-primary/90 hover:to-indigo-500 text-white shadow-md"
          >
            <span>Apply Now</span>
            <ExternalLink className="h-4 w-4" />
          </Button>
        </div>

        {/* Highlights Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 rounded-xl border border-border/40 bg-muted/20 p-4">
          <div className="space-y-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1">
              <DollarSign className="h-3.5 w-3.5 text-emerald-500" /> Salary
            </span>
            <p className="text-sm font-semibold text-foreground">
              {formatSalary(job.salaryMin, job.salaryMax, job.currency || 'USD')}
            </p>
          </div>

          <div className="space-y-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1">
              <Calendar className="h-3.5 w-3.5 text-primary" /> Date Posted
            </span>
            <p className="text-sm font-medium text-foreground">
              {job.postedAt
                ? new Date(job.postedAt).toLocaleDateString(undefined, {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })
                : 'Recently posted'}
            </p>
          </div>
        </div>

        {/* Skills Section */}
        {job.skills && job.skills.length > 0 && (
          <div className="space-y-2.5 border-t border-border/40 pt-4">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
              <Sparkles className="h-3.5 w-3.5 text-primary" /> Extracted Skills
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {job.skills.map((skill) => (
                <Badge
                  key={skill}
                  variant="secondary"
                  className="bg-primary/10 text-primary border-primary/20 text-xs px-2.5 py-1"
                >
                  {skill}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Requirements */}
        {job.requirements && (
          <div className="space-y-2 border-t border-border/40 pt-4">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" /> Requirements
            </h3>
            <div className="text-sm text-foreground/90 whitespace-pre-line leading-relaxed rounded-xl border border-border/40 bg-muted/10 p-4">
              {job.requirements}
            </div>
          </div>
        )}

        {/* Full Job Description */}
        <div className="space-y-2 border-t border-border/40 pt-4">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Full Description
          </h3>
          <div className="text-sm text-foreground/90 whitespace-pre-line leading-relaxed rounded-xl border border-border/40 bg-card/60 p-4 space-y-3">
            {job.description}
          </div>
        </div>
      </div>
    </div>
  );
}
