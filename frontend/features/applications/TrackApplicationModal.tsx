'use client';

import React, { useState, useEffect } from 'react';
import { Search, Building2, MapPin, Briefcase } from 'lucide-react';
import { ApplicationStatus, CreateApplicationPayload, Job } from '@/types';
import { useJobStore } from '@/store';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Modal } from '@/components/ui/modal';

interface TrackApplicationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (payload: CreateApplicationPayload) => Promise<unknown>;
  defaultStatus?: ApplicationStatus;
}

const STATUS_OPTIONS: { value: ApplicationStatus; label: string }[] = [
  { value: 'SAVED', label: 'Saved Opportunity' },
  { value: 'APPLIED', label: 'Applied' },
  { value: 'ASSESSMENT', label: 'Assessment' },
  { value: 'INTERVIEW', label: 'Interview' },
  { value: 'OFFER', label: 'Offer Received' },
];

export function TrackApplicationModal({
  isOpen,
  onClose,
  onSubmit,
  defaultStatus = 'SAVED',
}: TrackApplicationModalProps) {
  const { jobs, fetchJobs } = useJobStore();
  const [search, setSearch] = useState('');
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [status, setStatus] = useState<ApplicationStatus>(defaultStatus);
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (isOpen && jobs.length === 0) {
      fetchJobs();
    }
  }, [isOpen, jobs.length, fetchJobs]);

  useEffect(() => {
    setStatus(defaultStatus);
  }, [defaultStatus]);

  const filteredJobs = jobs.filter((j) => {
    const q = search.toLowerCase();
    return (
      j.title.toLowerCase().includes(q) ||
      j.company.toLowerCase().includes(q) ||
      j.location.toLowerCase().includes(q)
    );
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedJob) return;

    setSubmitting(true);
    try {
      await onSubmit({
        jobId: selectedJob.id,
        status,
        source: selectedJob.source,
        notes: notes.trim() || undefined,
      });
      onClose();
      setSelectedJob(null);
      setNotes('');
      setSearch('');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Track New Job Application"
      description="Add an opportunity to your tracking pipeline to monitor interviews, milestones, and status."
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-4 pt-1">
        {/* Job Selection Search */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-foreground">Select Target Job Opportunity</label>
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by position title, company, or location..."
              className="pl-8 text-xs"
            />
          </div>

          {/* Job List Selection Box */}
          <div className="border border-border/60 rounded-lg max-h-48 overflow-y-auto divide-y divide-border/40 bg-muted/10 p-1">
            {filteredJobs.length === 0 ? (
              <div className="p-4 text-center text-xs text-muted-foreground">
                No matching jobs found in discovery engine.
              </div>
            ) : (
              filteredJobs.slice(0, 20).map((job) => {
                const isSelected = selectedJob?.id === job.id;
                return (
                  <button
                    type="button"
                    key={job.id}
                    onClick={() => setSelectedJob(job)}
                    className={`w-full text-left p-2.5 rounded-md text-xs transition-colors flex items-center justify-between gap-3 ${
                      isSelected
                        ? 'bg-primary/10 text-primary font-medium border border-primary/30'
                        : 'hover:bg-muted/40 text-foreground'
                    }`}
                  >
                    <div className="min-w-0 flex-1">
                      <div className="font-semibold truncate">{job.title}</div>
                      <div className="flex items-center gap-2 text-[11px] text-muted-foreground mt-0.5">
                        <span className="flex items-center gap-1 truncate">
                          <Building2 className="w-3 h-3 shrink-0" />
                          {job.company}
                        </span>
                        <span>•</span>
                        <span className="flex items-center gap-1 truncate">
                          <MapPin className="w-3 h-3 shrink-0" />
                          {job.location}
                        </span>
                      </div>
                    </div>
                    {isSelected && (
                      <span className="text-[10px] font-semibold uppercase tracking-wider text-primary px-2 py-0.5 bg-primary/20 rounded">
                        Selected
                      </span>
                    )}
                  </button>
                );
              })
            )}
          </div>
        </div>

        {/* Selected Job Confirmation Pill */}
        {selectedJob && (
          <div className="p-2.5 rounded-lg bg-primary/5 border border-primary/20 text-xs flex items-center justify-between">
            <div>
              <span className="font-semibold text-primary">{selectedJob.title}</span>
              <span className="text-muted-foreground"> at {selectedJob.company}</span>
            </div>
            <button
              type="button"
              onClick={() => setSelectedJob(null)}
              className="text-xs text-muted-foreground hover:text-foreground"
            >
              Change
            </button>
          </div>
        )}

        {/* Status Selection */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-foreground">Pipeline Stage</label>
          <div className="grid grid-cols-3 sm:grid-cols-5 gap-2">
            {STATUS_OPTIONS.map((opt) => (
              <button
                type="button"
                key={opt.value}
                onClick={() => setStatus(opt.value)}
                className={`py-2 px-2 text-center rounded-lg border text-xs transition-all ${
                  status === opt.value
                    ? 'border-primary bg-primary/10 text-primary font-semibold ring-1 ring-primary/30'
                    : 'border-border/60 hover:border-border text-foreground hover:bg-muted/30'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Initial Notes */}
        <div className="space-y-1">
          <label className="text-xs font-semibold text-foreground flex items-center justify-between">
            <span>Notes & Context</span>
            <span className="text-[10px] text-muted-foreground font-normal">Optional</span>
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={2}
            placeholder="Recruiter contact, referral details, or target salary..."
            className="w-full text-xs rounded-lg border border-border/60 bg-background px-3 py-2 text-foreground focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary placeholder:text-muted-foreground/60 resize-none"
          />
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-2 pt-2 border-t border-border/40">
          <Button type="button" variant="outline" size="sm" onClick={onClose} disabled={submitting}>
            Cancel
          </Button>
          <Button type="submit" size="sm" disabled={submitting || !selectedJob}>
            {submitting ? 'Tracking...' : 'Track Application'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
