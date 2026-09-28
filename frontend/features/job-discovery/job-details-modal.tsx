'use client';

import React from 'react';
import { Modal } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Job } from '@/types';
import {
  Building2,
  MapPin,
  DollarSign,
  Calendar,
  ExternalLink,
  Briefcase,
  Sparkles,
  CheckCircle2,
  Share2,
} from 'lucide-react';

interface JobDetailsModalProps {
  job: Job | null;
  isOpen: boolean;
  onClose: () => void;
}

function formatSalary(min?: number | null, max?: number | null, currency: string = 'USD'): string {
  if (!min && !max) return 'Competitive compensation package';
  const symbol = currency === 'USD' ? '$' : currency + ' ';
  if (min && max) {
    return `${symbol}${min.toLocaleString()} – ${symbol}${max.toLocaleString()} per year`;
  }
  if (min) return `${symbol}${min.toLocaleString()}+ per year`;
  if (max) return `Up to ${symbol}${max.toLocaleString()} per year`;
  return 'Competitive compensation';
}

export function JobDetailsModal({ job, isOpen, onClose }: JobDetailsModalProps) {
  if (!job) return null;

  const isRemote = job.location.toLowerCase().includes('remote');

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      size="xl"
      title={
        <div className="space-y-1 pr-6">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xl font-bold text-foreground">{job.title}</span>
            <Badge variant="secondary" className="text-xs bg-primary/10 text-primary border-primary/20">
              {job.source}
            </Badge>
          </div>
          <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground font-normal">
            <span className="flex items-center gap-1 font-medium text-foreground">
              <Building2 className="h-3.5 w-3.5 text-primary" /> {job.company}
            </span>
            <span className="flex items-center gap-1">
              <MapPin className="h-3.5 w-3.5" /> {job.location}
            </span>
            {job.employmentType && (
              <span className="flex items-center gap-1">
                <Briefcase className="h-3.5 w-3.5" /> {job.employmentType}
              </span>
            )}
          </div>
        </div>
      }
      footer={
        <div className="flex w-full items-center justify-between gap-3">
          <Button variant="outline" size="sm" onClick={onClose}>
            Close
          </Button>

          <Button
            size="sm"
            onClick={() => window.open(job.applyUrl, '_blank', 'noopener,noreferrer')}
            className="gap-2 bg-gradient-to-r from-primary to-indigo-600 hover:from-primary/90 hover:to-indigo-500 text-white shadow-md"
          >
            <span>Apply on {job.source}</span>
            <ExternalLink className="h-3.5 w-3.5" />
          </Button>
        </div>
      }
    >
      <div className="space-y-6 max-h-[70vh] overflow-y-auto pr-1">
        {/* Quick Highlights Card */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 rounded-xl border border-border/60 bg-muted/20 p-4">
          <div className="space-y-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1">
              <DollarSign className="h-3.5 w-3.5 text-emerald-500" /> Compensation
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

        {/* Extracted Skills Section */}
        {job.skills && job.skills.length > 0 && (
          <div className="space-y-2.5">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
              <Sparkles className="h-3.5 w-3.5 text-primary" /> Key Technologies & Skills
            </h4>
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

        {/* Requirements Section (if extracted or listed) */}
        {job.requirements && (
          <div className="space-y-2">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" /> Requirements
            </h4>
            <div className="text-sm text-foreground/90 whitespace-pre-line leading-relaxed rounded-xl border border-border/40 bg-muted/10 p-4">
              {job.requirements}
            </div>
          </div>
        )}

        {/* Job Description */}
        <div className="space-y-2">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Role Description
          </h4>
          <div className="text-sm text-foreground/90 whitespace-pre-line leading-relaxed rounded-xl border border-border/40 bg-card p-4 space-y-3">
            {job.description}
          </div>
        </div>
      </div>
    </Modal>
  );
}
