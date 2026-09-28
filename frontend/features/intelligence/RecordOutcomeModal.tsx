'use client';

import * as React from 'react';
import { Modal } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { OutcomeType, RecordOutcomePayload } from '@/types';
import { useApplicationStore } from '@/store/application-store';
import { Award, Briefcase, Calendar, CheckCircle2, FileText, Tag } from 'lucide-react';

interface RecordOutcomeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (payload: RecordOutcomePayload) => Promise<unknown>;
  loading?: boolean;
}

const OUTCOME_OPTIONS: { type: OutcomeType; label: string; desc: string; color: string }[] = [
  {
    type: 'InterviewReceived',
    label: 'Interview Received',
    desc: 'Recruiter screen, technical interview, or manager loop scheduled',
    color: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-400',
  },
  {
    type: 'AssessmentReceived',
    label: 'Assessment Received',
    desc: 'Take-home assignment, HackerRank, or automated screening',
    color: 'border-blue-500/40 bg-blue-500/10 text-blue-400',
  },
  {
    type: 'OfferReceived',
    label: 'Offer Received',
    desc: 'Formal job offer extended by employer',
    color: 'border-purple-500/40 bg-purple-500/10 text-purple-400',
  },
  {
    type: 'Rejected',
    label: 'Rejected',
    desc: 'Application or post-interview loop declined',
    color: 'border-rose-500/40 bg-rose-500/10 text-rose-400',
  },
  {
    type: 'Withdrawn',
    label: 'Withdrawn',
    desc: 'Candidate voluntarily withdrew from hiring process',
    color: 'border-slate-500/40 bg-slate-500/10 text-slate-400',
  },
];

export function RecordOutcomeModal({
  isOpen,
  onClose,
  onSubmit,
  loading = false,
}: RecordOutcomeModalProps) {
  const { applications, fetchApplications } = useApplicationStore();
  const [selectedAppId, setSelectedAppId] = React.useState('');
  const [outcomeType, setOutcomeType] = React.useState<OutcomeType>('InterviewReceived');
  const [occurredAt, setOccurredAt] = React.useState(new Date().toISOString().split('T')[0]);
  const [notes, setNotes] = React.useState('');
  const [extraDetail, setExtraDetail] = React.useState('');
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (isOpen) {
      fetchApplications();
    }
  }, [isOpen, fetchApplications]);

  React.useEffect(() => {
    if (applications.length > 0 && !selectedAppId) {
      setSelectedAppId(applications[0].id);
    }
  }, [applications, selectedAppId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAppId.trim()) {
      setError('Please select an application.');
      return;
    }

    setError(null);
    const metadata: Record<string, unknown> = {};
    if (outcomeType === 'InterviewReceived' && extraDetail) {
      metadata.round = extraDetail;
    } else if (outcomeType === 'OfferReceived' && extraDetail) {
      metadata.offerAmount = extraDetail;
    } else if (extraDetail) {
      metadata.detail = extraDetail;
    }

    try {
      await onSubmit({
        application_id: selectedAppId,
        outcome_type: outcomeType,
        occurred_at: new Date(occurredAt).toISOString(),
        notes: notes.trim() || undefined,
        metadata: Object.keys(metadata).length > 0 ? metadata : undefined,
      });
      onClose();
    } catch (err: any) {
      setError(err?.message || 'Failed to record outcome event');
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Record Application Outcome"
      description="Feed actual hiring results back into the career intelligence engine to optimize resume, skill, and strategy recommendations."
      size="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-5">
        {error && (
          <div className="p-3 text-xs bg-rose-500/10 border border-rose-500/30 text-rose-400 rounded-md">
            {error}
          </div>
        )}

        {/* 1. Target Application */}
        <div>
          <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground block mb-1">
            Target Application
          </label>
          {applications.length > 0 ? (
            <select
              value={selectedAppId}
              onChange={(e) => setSelectedAppId(e.target.value)}
              className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
            >
              {applications.map((app) => (
                <option key={app.id} value={app.id}>
                  {app.jobTitle || 'Unknown Title'} @ {app.jobCompany || 'Company'} ({app.status})
                </option>
              ))}
            </select>
          ) : (
            <Input
              placeholder="Paste Application UUID"
              value={selectedAppId}
              onChange={(e) => setSelectedAppId(e.target.value)}
            />
          )}
        </div>

        {/* 2. Outcome Type Select */}
        <div>
          <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground block mb-2">
            Outcome Milestone
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {OUTCOME_OPTIONS.map((opt) => {
              const isSelected = outcomeType === opt.type;
              return (
                <button
                  type="button"
                  key={opt.type}
                  onClick={() => setOutcomeType(opt.type)}
                  className={`text-left p-3 rounded-lg border transition-all ${
                    isSelected
                      ? `${opt.color} ring-1 ring-primary shadow-sm`
                      : 'border-border/60 bg-muted/20 hover:bg-muted/40 text-muted-foreground'
                  }`}
                >
                  <div className="font-semibold text-xs flex items-center justify-between">
                    <span>{opt.label}</span>
                    {isSelected && <CheckCircle2 className="h-3.5 w-3.5" />}
                  </div>
                  <p className="text-[11px] opacity-80 mt-1 line-clamp-2">{opt.desc}</p>
                </button>
              );
            })}
          </div>
        </div>

        {/* 3. Occurred Date & Optional Detail */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground block mb-1">
              Event Date
            </label>
            <Input
              type="date"
              value={occurredAt}
              onChange={(e) => setOccurredAt(e.target.value)}
            />
          </div>
          <div>
            <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground block mb-1">
              {outcomeType === 'OfferReceived'
                ? 'Offer Amount / Comp ($)'
                : outcomeType === 'InterviewReceived'
                ? 'Interview Round (e.g. Round 1 / Final)'
                : 'Extra Detail / Context'}
            </label>
            <Input
              placeholder={
                outcomeType === 'OfferReceived'
                  ? 'e.g. 185000'
                  : outcomeType === 'InterviewReceived'
                  ? 'e.g. Technical System Design'
                  : 'Optional detail'
              }
              value={extraDetail}
              onChange={(e) => setExtraDetail(e.target.value)}
            />
          </div>
        </div>

        {/* 4. Notes */}
        <div>
          <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground block mb-1">
            Recruiter / Interviewer Notes
          </label>
          <textarea
            rows={3}
            placeholder="Feedback received, topics covered, or reasons noted..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="w-full bg-background border border-border rounded-md p-2.5 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-2 pt-2 border-t border-border/60">
          <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button type="submit" disabled={loading} className="gap-2">
            {loading ? 'Recording...' : 'Record Outcome'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
