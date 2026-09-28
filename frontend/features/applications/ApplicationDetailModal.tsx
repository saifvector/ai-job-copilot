'use client';

import React, { useState, useEffect } from 'react';
import {
  Building2,
  MapPin,
  Calendar,
  Clock,
  Sparkles,
  ExternalLink,
  Trash2,
  Save,
  Plus,
  DollarSign,
  Briefcase,
  FileText,
  History,
  CheckCircle2,
} from 'lucide-react';
import {
  Application,
  ApplicationStatus,
  CreateEventPayload,
} from '@/types';
import { TimelineView } from './TimelineView';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Modal } from '@/components/ui/modal';

interface ApplicationDetailModalProps {
  application: Application | null;
  isOpen: boolean;
  onClose: () => void;
  onStatusChange: (status: ApplicationStatus, notes?: string) => Promise<unknown>;
  onUpdateNotes: (notes: string) => Promise<unknown>;
  onAddEvent: (payload: CreateEventPayload) => Promise<boolean>;
  onScheduleInterview: () => void;
  onDelete: () => Promise<unknown>;
}

const STATUSES: { value: ApplicationStatus; label: string; color: string }[] = [
  { value: 'SAVED', label: 'Saved', color: 'bg-amber-500/10 text-amber-500 border-amber-500/30' },
  { value: 'APPLIED', label: 'Applied', color: 'bg-blue-500/10 text-blue-500 border-blue-500/30' },
  { value: 'ASSESSMENT', label: 'Assessment', color: 'bg-purple-500/10 text-purple-500 border-purple-500/30' },
  { value: 'INTERVIEW', label: 'Interview', color: 'bg-indigo-500/10 text-indigo-500 border-indigo-500/30' },
  { value: 'OFFER', label: 'Offer Received', color: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/30' },
  { value: 'REJECTED', label: 'Rejected', color: 'bg-rose-500/10 text-rose-500 border-rose-500/30' },
  { value: 'WITHDRAWN', label: 'Withdrawn', color: 'bg-zinc-500/10 text-zinc-500 border-zinc-500/30' },
];

export function ApplicationDetailModal({
  application,
  isOpen,
  onClose,
  onStatusChange,
  onUpdateNotes,
  onAddEvent,
  onScheduleInterview,
  onDelete,
}: ApplicationDetailModalProps) {
  const [activeTab, setActiveTab] = useState<'timeline' | 'interviews' | 'notes'>('timeline');
  const [notes, setNotes] = useState('');
  const [savingNotes, setSavingNotes] = useState(false);
  const [notesSaved, setNotesSaved] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);

  useEffect(() => {
    if (application) {
      setNotes(application.notes || '');
      setConfirmDelete(false);
      setNotesSaved(false);
    }
  }, [application]);

  if (!application) return null;

  const handleSaveNotes = async () => {
    setSavingNotes(true);
    try {
      await onUpdateNotes(notes);
      setNotesSaved(true);
      setTimeout(() => setNotesSaved(false), 2500);
    } finally {
      setSavingNotes(false);
    }
  };

  const currentStatusObj = STATUSES.find((s) => s.value === application.status) || STATUSES[0];

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title=""
      size="xl"
    >
      <div className="space-y-5 -mt-3">
        {/* Top Header Card */}
        <div className="p-4 rounded-xl border border-border/60 bg-muted/20 space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="font-semibold text-sm text-foreground flex items-center gap-1.5">
                  <Building2 className="w-4 h-4 text-primary" />
                  {application.job?.company || 'Company'}
                </span>
                {application.source && (
                  <Badge variant="outline" className="text-[10px] font-normal text-muted-foreground">
                    via {application.source}
                  </Badge>
                )}
              </div>
              <h2 className="text-lg font-bold text-foreground">
                {application.job?.title || 'Target Position'}
              </h2>
            </div>

            {/* Status Selector Dropdown */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground font-medium">Status:</span>
              <select
                value={application.status}
                onChange={(e) => onStatusChange(e.target.value as ApplicationStatus)}
                className={`text-xs font-semibold px-2.5 py-1.5 rounded-lg border focus:outline-none focus:ring-1 focus:ring-primary ${currentStatusObj.color}`}
              >
                {STATUSES.map((s) => (
                  <option key={s.value} value={s.value} className="bg-background text-foreground">
                    {s.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Meta Details Row */}
          <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-muted-foreground pt-1 border-t border-border/40">
            <div className="flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5" />
              <span>{application.job?.location || 'Remote'}</span>
            </div>

            {application.job?.employmentType && (
              <div className="flex items-center gap-1">
                <Briefcase className="w-3.5 h-3.5" />
                <span>{application.job.employmentType}</span>
              </div>
            )}

            {(application.job?.salaryMin || application.job?.salaryMax) && (
              <div className="flex items-center gap-1">
                <DollarSign className="w-3.5 h-3.5" />
                <span>
                  {application.job.currency || '$'}
                  {application.job.salaryMin ? application.job.salaryMin.toLocaleString() : ''}
                  {application.job.salaryMin && application.job.salaryMax ? ' - ' : ''}
                  {application.job.salaryMax ? application.job.salaryMax.toLocaleString() : ''}
                </span>
              </div>
            )}

            {application.applicationDate && (
              <div className="flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5" />
                <span>Applied: {new Date(application.applicationDate).toLocaleDateString()}</span>
              </div>
            )}

            {application.job?.applyUrl && (
              <a
                href={application.job.applyUrl}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-1 text-primary hover:underline ml-auto font-medium"
              >
                <span>Job Posting</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            )}
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center border-b border-border/60 gap-4 text-xs">
          <button
            type="button"
            onClick={() => setActiveTab('timeline')}
            className={`pb-2 font-semibold transition-colors flex items-center gap-1.5 border-b-2 -mb-[1px] ${
              activeTab === 'timeline'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <History className="w-3.5 h-3.5" />
            <span>Timeline ({application.events?.length || 0})</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('interviews')}
            className={`pb-2 font-semibold transition-colors flex items-center gap-1.5 border-b-2 -mb-[1px] ${
              activeTab === 'interviews'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <Calendar className="w-3.5 h-3.5" />
            <span>Interviews ({application.interviews?.length || 0})</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('notes')}
            className={`pb-2 font-semibold transition-colors flex items-center gap-1.5 border-b-2 -mb-[1px] ${
              activeTab === 'notes'
                ? 'border-primary text-primary'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Notes & Strategy</span>
          </button>
        </div>

        {/* Tab 1: Timeline */}
        {activeTab === 'timeline' && (
          <div className="max-h-[380px] overflow-y-auto pr-1">
            <TimelineView events={application.events} onAddEvent={onAddEvent} />
          </div>
        )}

        {/* Tab 2: Interviews */}
        {activeTab === 'interviews' && (
          <div className="space-y-4 max-h-[380px] overflow-y-auto pr-1">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-foreground">Interview Rounds History</span>
              <Button size="sm" onClick={onScheduleInterview} className="text-xs h-7 gap-1">
                <Plus className="w-3.5 h-3.5" />
                <span>Schedule Next Round</span>
              </Button>
            </div>

            {(!application.interviews || application.interviews.length === 0) ? (
              <div className="p-8 text-center border-2 border-dashed border-border/40 rounded-xl space-y-2">
                <Calendar className="w-8 h-8 text-muted-foreground/40 mx-auto" />
                <p className="text-xs font-semibold text-foreground">No interview rounds scheduled yet</p>
                <p className="text-[11px] text-muted-foreground max-w-sm mx-auto">
                  Record recruiter screens, technical assessments, system design, or executive final rounds.
                </p>
                <Button size="sm" variant="outline" onClick={onScheduleInterview} className="mt-2 text-xs">
                  Schedule Round 1
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {application.interviews.map((interview) => {
                  const rawDate = interview.interviewDate || (interview as any).interview_date || '';
                  const date = new Date(rawDate);
                  const isValid = !isNaN(date.getTime());
                  const isFuture = isValid && date.getTime() > Date.now();
                  const roundNum = interview.interviewRound ?? (interview as any).interview_round ?? 1;
                  const typeStr = interview.interviewType || (interview as any).interview_type || 'TECHNICAL';

                  return (
                    <div
                      key={interview.id}
                      className="p-3.5 rounded-lg border border-border/60 bg-card hover:border-border transition-colors space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-xs text-foreground">
                            Round {roundNum}
                          </span>
                          <Badge variant="secondary" className="text-[10px] uppercase font-semibold">
                            {typeStr}
                          </Badge>
                          {isFuture ? (
                            <span className="text-[10px] text-blue-500 font-semibold px-2 py-0.5 rounded bg-blue-500/10">
                              Upcoming
                            </span>
                          ) : (
                            <span className="text-[10px] text-muted-foreground px-2 py-0.5 rounded bg-muted">
                              {isValid ? 'Completed' : 'Scheduled'}
                            </span>
                          )}
                        </div>

                        <div className="flex items-center gap-1.5 text-xs text-muted-foreground font-medium">
                          <Clock className="w-3.5 h-3.5" />
                          <span>
                            {isValid ? (
                              <>
                                {date.toLocaleDateString(undefined, {
                                  weekday: 'short',
                                  month: 'short',
                                  day: 'numeric',
                                  year: 'numeric',
                                })}{' '}
                                at{' '}
                                {date.toLocaleTimeString(undefined, {
                                  hour: '2-digit',
                                  minute: '2-digit',
                                })}
                              </>
                            ) : (
                              'Date TBD'
                            )}
                          </span>
                        </div>
                      </div>

                      {interview.notes && (
                        <p className="text-xs text-muted-foreground bg-muted/20 p-2.5 rounded-md border border-border/30 whitespace-pre-wrap">
                          {interview.notes}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* Tab 3: Notes & Strategy */}
        {activeTab === 'notes' && (
          <div className="space-y-3">
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-foreground">
                  Candidate Private Notes & Strategy
                </label>
                {notesSaved && (
                  <span className="text-[11px] text-emerald-500 font-medium flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" />
                    Saved!
                  </span>
                )}
              </div>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={8}
                placeholder="Log internal recruiter notes, interview feedback, compensation discussion, questions to ask, or preparation strategy..."
                className="w-full text-xs font-mono rounded-lg border border-border/60 bg-background p-3 text-foreground focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary placeholder:text-muted-foreground/60 resize-none leading-relaxed"
              />
            </div>

            <div className="flex justify-end">
              <Button
                size="sm"
                onClick={handleSaveNotes}
                disabled={savingNotes}
                className="text-xs gap-1.5"
              >
                <Save className="w-3.5 h-3.5" />
                <span>{savingNotes ? 'Saving...' : 'Save Notes'}</span>
              </Button>
            </div>
          </div>
        )}

        {/* Bottom Footer Actions */}
        <div className="flex items-center justify-between pt-3 border-t border-border/50 text-xs">
          {confirmDelete ? (
            <div className="flex items-center gap-2">
              <span className="text-rose-500 font-semibold">Delete application permanently?</span>
              <Button
                size="sm"
                variant="destructive"
                onClick={async () => {
                  await onDelete();
                  onClose();
                }}
                className="h-7 text-xs px-2.5"
              >
                Yes, Delete
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => setConfirmDelete(false)}
                className="h-7 text-xs px-2.5"
              >
                Cancel
              </Button>
            </div>
          ) : (
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setConfirmDelete(true)}
              className="h-7 text-xs text-muted-foreground hover:text-rose-500 gap-1 px-2"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Delete Application</span>
            </Button>
          )}

          <Button size="sm" variant="outline" onClick={onClose} className="h-7 text-xs px-3">
            Close
          </Button>
        </div>
      </div>
    </Modal>
  );
}
