'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ApplicationDraftJob } from '@/types';
import { Building2, MapPin, DollarSign, ExternalLink, ChevronDown, ChevronUp, Briefcase } from 'lucide-react';

interface JobSummaryCardProps {
  job?: ApplicationDraftJob | null;
  status?: string;
}

export const JobSummaryCard: React.FC<JobSummaryCardProps> = ({ job, status = 'Draft' }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!job) {
    return (
      <Card className="border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm">
        <CardContent className="p-6 text-center text-slate-500 dark:text-slate-400">
          <Briefcase className="w-8 h-8 mx-auto mb-2 text-slate-400 opacity-60" />
          <p className="text-sm font-medium">Select a target job posting to start preparing your application.</p>
        </CardContent>
      </Card>
    );
  }

  const getStatusBadge = (st: string) => {
    switch (st) {
      case 'SubmittedByUser':
        return <Badge variant="success">Submitted by Candidate</Badge>;
      case 'ReadyForReview':
        return <Badge variant="warning">Ready for Review</Badge>;
      case 'Cancelled':
        return <Badge variant="destructive">Cancelled</Badge>;
      default:
        return <Badge variant="secondary">Draft Mode</Badge>;
    }
  };

  return (
    <Card className="border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm overflow-hidden mb-6">
      <CardHeader className="p-5 pb-3 border-b border-slate-100 dark:border-slate-800/80">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2 mb-1.5 flex-wrap">
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-50 dark:bg-blue-950/70 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-800">
                Target Role
              </span>
              {getStatusBadge(status)}
            </div>
            <CardTitle className="text-xl font-bold text-slate-900 dark:text-white">
              {job.title}
            </CardTitle>
            <CardDescription className="flex items-center gap-4 text-xs text-slate-500 dark:text-slate-400 mt-1.5 flex-wrap">
              <span className="flex items-center gap-1 font-medium text-slate-700 dark:text-slate-300">
                <Building2 className="w-3.5 h-3.5 text-slate-400" />
                {job.company}
              </span>
              <span className="flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-slate-400" />
                {job.location}
              </span>
              {job.salary && (
                <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-medium">
                  <DollarSign className="w-3.5 h-3.5" />
                  {job.salary}
                </span>
              )}
            </CardDescription>
          </div>

          {job.applyUrl && (
            <a
              href={job.applyUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors shrink-0"
            >
              <span>View Original Job Posting</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
        </div>
      </CardHeader>

      <CardContent className="p-5 pt-4">
        {job.requirements && job.requirements.length > 0 && (
          <div className="mb-4">
            <h4 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">
              Key Requirements & Focus Skills
            </h4>
            <div className="flex flex-wrap gap-1.5">
              {job.requirements.map((req, idx) => (
                <span
                  key={idx}
                  className="text-xs px-2.5 py-1 rounded-md bg-slate-100 dark:bg-slate-800/80 text-slate-700 dark:text-slate-300 border border-slate-200/60 dark:border-slate-700/60"
                >
                  {req}
                </span>
              ))}
            </div>
          </div>
        )}

        {job.description && (
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <h4 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                Job Overview
              </h4>
              <button
                type="button"
                onClick={() => setIsExpanded(!isExpanded)}
                className="text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
              >
                {isExpanded ? (
                  <>
                    <span>Show Less</span>
                    <ChevronUp className="w-3.5 h-3.5" />
                  </>
                ) : (
                  <>
                    <span>Expand Description</span>
                    <ChevronDown className="w-3.5 h-3.5" />
                  </>
                )}
              </button>
            </div>
            <p className={`text-xs text-slate-600 dark:text-slate-400 leading-relaxed ${
              isExpanded ? '' : 'line-clamp-2'
            }`}>
              {job.description}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
