'use client';

import React, { useEffect, useState } from 'react';
import { Job } from '@/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useJobStore } from '@/store';
import { Briefcase, Sparkles, Loader2, Building, MapPin, DollarSign, Search } from 'lucide-react';

interface JobSelectorProps {
  onTailor: (jobId: string, targetVersion: 'ats' | 'recruiter' | 'balanced', customInstructions?: string) => Promise<void>;
  loading: boolean;
  className?: string;
  defaultJobId?: string;
}

export const JobSelector: React.FC<JobSelectorProps> = ({
  onTailor,
  loading,
  className = '',
  defaultJobId,
}) => {
  const { jobs, fetchJobs } = useJobStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [targetVersion, setTargetVersion] = useState<'ats' | 'recruiter' | 'balanced'>('balanced');
  const [customInstructions, setCustomInstructions] = useState('');

  useEffect(() => {
    if (jobs.length === 0) {
      fetchJobs();
    }
  }, [jobs.length, fetchJobs]);

  useEffect(() => {
    if (defaultJobId && jobs.length > 0) {
      const match = jobs.find((j) => j.id === defaultJobId);
      if (match) setSelectedJob(match);
    } else if (!selectedJob && jobs.length > 0) {
      setSelectedJob(jobs[0]);
    }
  }, [defaultJobId, jobs, selectedJob]);

  const filteredJobs = jobs.filter(
    (j) =>
      j.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      j.company.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleTriggerTailor = async () => {
    if (!selectedJob) return;
    await onTailor(selectedJob.id, targetVersion, customInstructions || undefined);
  };

  return (
    <Card className={`border shadow-sm ${className}`}>
      <CardHeader className="pb-3 border-b border-border/40">
        <CardTitle className="text-base font-semibold flex items-center gap-2">
          <Briefcase className="w-4 h-4 text-primary" />
          Target Opportunity Selection
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-4 space-y-4">
        {/* Search Input for Jobs */}
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-3 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search opportunities by title or company..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 h-10 text-xs"
          />
        </div>

        {/* Job Selection Dropdown / List */}
        <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
          {filteredJobs.length > 0 ? (
            filteredJobs.map((job) => {
              const isSelected = selectedJob?.id === job.id;
              return (
                <div
                  key={job.id}
                  onClick={() => setSelectedJob(job)}
                  className={`p-2.5 rounded-lg border text-xs cursor-pointer transition-all ${
                    isSelected
                      ? 'border-primary bg-primary/5 shadow-xs font-medium'
                      : 'border-border/50 hover:border-border hover:bg-muted/30'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-foreground truncate">{job.title}</span>
                    <Badge variant="outline" className="text-[10px] font-normal shrink-0">
                      {job.source}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-3 text-muted-foreground text-[11px] mt-1">
                    <span className="flex items-center gap-1">
                      <Building className="w-3 h-3" />
                      {job.company}
                    </span>
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3 h-3" />
                      {job.location}
                    </span>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="p-4 text-center text-xs text-muted-foreground border border-dashed rounded-lg">
              No matching jobs found. Sync or discover opportunities first.
            </div>
          )}
        </div>

        {/* Selected Job Highlights Card */}
        {selectedJob && (
          <div className="p-3 bg-muted/20 border border-border/60 rounded-xl space-y-2 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-foreground text-sm">{selectedJob.title}</span>
              {selectedJob.salaryMin && (
                <span className="text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-0.5">
                  <DollarSign className="w-3 h-3" />
                  ${selectedJob.salaryMin.toLocaleString()}
                  {selectedJob.salaryMax ? ` – $${selectedJob.salaryMax.toLocaleString()}` : '+'}
                </span>
              )}
            </div>
            <p className="text-muted-foreground line-clamp-2 leading-relaxed">
              {selectedJob.description}
            </p>
          </div>
        )}

        {/* Target Version & Custom Instructions */}
        <div className="space-y-3 pt-2 border-t border-border/40">
          <div>
            <label className="text-xs font-semibold text-foreground mb-1.5 block">
              Default Optimization Focus
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { key: 'balanced', label: 'Balanced (Optimal)' },
                { key: 'ats', label: 'ATS Scanners' },
                { key: 'recruiter', label: 'Human Recruiter' },
              ].map(({ key, label }) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => setTargetVersion(key as any)}
                  className={`p-2 rounded-lg border text-xs text-center transition-all ${
                    targetVersion === key
                      ? 'border-primary bg-primary/10 text-primary font-semibold'
                      : 'border-border/60 hover:bg-muted/30 text-muted-foreground'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold text-foreground mb-1 block">
              Custom Tailoring Directives <span className="font-normal text-muted-foreground">(Optional)</span>
            </label>
            <Input
              type="text"
              placeholder="e.g. Focus on high-throughput distributed systems & PostgreSQL"
              value={customInstructions}
              onChange={(e) => setCustomInstructions(e.target.value)}
              className="h-8 text-xs"
            />
          </div>
        </div>

        {/* CTA Button */}
        <Button
          variant="default"
          size="default"
          disabled={loading || !selectedJob}
          onClick={handleTriggerTailor}
          className="w-full gap-2 font-semibold shadow-sm"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Tailoring with Gemini 2.5 Pro...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              Tailor Resume for Selected Role
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
};
