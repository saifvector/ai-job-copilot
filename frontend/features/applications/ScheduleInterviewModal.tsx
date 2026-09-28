'use client';

import React, { useState } from 'react';
import { Calendar, Clock, User, FileText } from 'lucide-react';
import { CreateInterviewPayload, InterviewType } from '@/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Modal } from '@/components/ui/modal';

interface ScheduleInterviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (payload: CreateInterviewPayload) => Promise<boolean>;
  companyName?: string;
  jobTitle?: string;
  defaultRound?: number;
}

const INTERVIEW_TYPES: { value: InterviewType; label: string; desc: string }[] = [
  { value: 'HR', label: 'HR / Recruiter Screen', desc: 'Initial background & salary alignment' },
  { value: 'TECHNICAL', label: 'Technical Assessment', desc: 'Coding, system design, or architecture' },
  { value: 'MANAGERIAL', label: 'Hiring Manager', desc: 'Team fit, leadership, and experience deep-dive' },
  { value: 'FINAL', label: 'Executive / Final', desc: 'Leadership, executive presentation, or offer prep' },
];

export function ScheduleInterviewModal({
  isOpen,
  onClose,
  onSubmit,
  companyName = 'Employer',
  jobTitle = 'Role',
  defaultRound = 1,
}: ScheduleInterviewModalProps) {
  const [interviewType, setInterviewType] = useState<InterviewType>('TECHNICAL');
  const [interviewRound, setInterviewRound] = useState<number>(defaultRound);
  const [interviewDate, setInterviewDate] = useState<string>(() => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(15, 0, 0, 0);
    return tomorrow.toISOString().slice(0, 16);
  });
  const [notes, setNotes] = useState<string>('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!interviewDate) return;

    setSubmitting(true);
    try {
      const isoDate = new Date(interviewDate).toISOString();
      const success = await onSubmit({
        interviewType,
        interviewRound: Number(interviewRound),
        interviewDate: isoDate,
        notes: notes.trim() || undefined,
      });
      if (success) {
        onClose();
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Schedule Interview Round"
      description={`Record an interview round for ${jobTitle} at ${companyName}`}
      size="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4 pt-1">
        {/* Round & Type Selection */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-foreground">Interview Stage</label>
          <div className="grid grid-cols-2 gap-2">
            {INTERVIEW_TYPES.map((type) => (
              <button
                type="button"
                key={type.value}
                onClick={() => setInterviewType(type.value)}
                className={`p-2.5 text-left rounded-lg border text-xs transition-all ${
                  interviewType === type.value
                    ? 'border-primary bg-primary/10 text-primary font-medium ring-1 ring-primary/30'
                    : 'border-border/60 hover:border-border text-foreground hover:bg-muted/30'
                }`}
              >
                <div className="font-semibold">{type.label}</div>
                <div className="text-[10px] text-muted-foreground mt-0.5 leading-tight">
                  {type.desc}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Round Number + Date/Time Row */}
        <div className="grid grid-cols-3 gap-3">
          <div className="space-y-1">
            <label className="text-xs font-semibold text-foreground">Round #</label>
            <Input
              type="number"
              min={1}
              max={10}
              value={interviewRound}
              onChange={(e) => setInterviewRound(parseInt(e.target.value) || 1)}
              className="text-xs"
              required
            />
          </div>

          <div className="col-span-2 space-y-1">
            <label className="text-xs font-semibold text-foreground">Scheduled Date & Time</label>
            <Input
              type="datetime-local"
              value={interviewDate}
              onChange={(e) => setInterviewDate(e.target.value)}
              className="text-xs"
              required
            />
          </div>
        </div>

        {/* Notes / Interviewer Info */}
        <div className="space-y-1">
          <label className="text-xs font-semibold text-foreground flex items-center justify-between">
            <span>Interview Notes & Preparation</span>
            <span className="text-[10px] text-muted-foreground font-normal">Optional</span>
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            placeholder="Interviewer names, focus topics, video link, or questions to ask..."
            className="w-full text-xs rounded-lg border border-border/60 bg-background px-3 py-2 text-foreground focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary placeholder:text-muted-foreground/60 resize-none"
          />
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-2 pt-2 border-t border-border/40">
          <Button type="button" variant="outline" size="sm" onClick={onClose} disabled={submitting}>
            Cancel
          </Button>
          <Button type="submit" size="sm" disabled={submitting || !interviewDate}>
            {submitting ? 'Scheduling...' : 'Confirm Interview'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
