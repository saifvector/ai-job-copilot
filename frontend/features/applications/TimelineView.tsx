'use client';

import React, { useState } from 'react';
import {
  Activity,
  ArrowRightCircle,
  Award,
  Calendar,
  CheckCircle2,
  Clock,
  FileText,
  Plus,
  Send,
  Sparkles,
  XCircle,
} from 'lucide-react';
import { ApplicationEvent, CreateEventPayload } from '@/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface TimelineViewProps {
  events: ApplicationEvent[];
  onAddEvent?: (payload: CreateEventPayload) => Promise<boolean>;
  compact?: boolean;
}

export function TimelineView({
  events,
  onAddEvent,
  compact = false,
}: TimelineViewProps) {
  const [newEventText, setNewEventText] = useState('');
  const [eventType, setEventType] = useState('NOTE_ADDED');
  const [submitting, setSubmitting] = useState(false);

  const getEventIcon = (type?: string) => {
    const t = (type || 'NOTE_ADDED').toUpperCase();
    switch (t) {
      case 'CREATED':
        return <Sparkles className="w-3.5 h-3.5 text-primary" />;
      case 'STATUS_CHANGE':
        return <ArrowRightCircle className="w-3.5 h-3.5 text-blue-500" />;
      case 'INTERVIEW_SCHEDULED':
        return <Calendar className="w-3.5 h-3.5 text-indigo-500" />;
      case 'NOTE_ADDED':
        return <FileText className="w-3.5 h-3.5 text-amber-500" />;
      case 'OFFER_RECEIVED':
        return <Award className="w-3.5 h-3.5 text-emerald-500" />;
      case 'REJECTED':
        return <XCircle className="w-3.5 h-3.5 text-rose-500" />;
      default:
        return <Activity className="w-3.5 h-3.5 text-muted-foreground" />;
    }
  };

  const getEventBadgeColor = (type?: string) => {
    const t = (type || 'NOTE_ADDED').toUpperCase();
    switch (t) {
      case 'CREATED':
        return 'bg-primary/10 border-primary/20 text-primary';
      case 'STATUS_CHANGE':
        return 'bg-blue-500/10 border-blue-500/20 text-blue-500';
      case 'INTERVIEW_SCHEDULED':
        return 'bg-indigo-500/10 border-indigo-500/20 text-indigo-500';
      case 'NOTE_ADDED':
        return 'bg-amber-500/10 border-amber-500/20 text-amber-500';
      case 'OFFER_RECEIVED':
        return 'bg-emerald-500/10 border-emerald-500/20 text-emerald-500';
      case 'REJECTED':
        return 'bg-rose-500/10 border-rose-500/20 text-rose-500';
      default:
        return 'bg-muted border-border/40 text-muted-foreground';
    }
  };

  const handleAddEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newEventText.trim() || !onAddEvent) return;

    setSubmitting(true);
    try {
      const ok = await onAddEvent({
        eventType,
        description: newEventText.trim(),
      });
      if (ok) {
        setNewEventText('');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const sortedEvents = [...(events || [])].sort((a, b) => {
    const timeA = new Date(a.createdAt || (a as any).created_at || 0).getTime();
    const timeB = new Date(b.createdAt || (b as any).created_at || 0).getTime();
    return timeB - timeA;
  });

  return (
    <div className="space-y-4">
      {/* Quick Add Milestone Form */}
      {onAddEvent && !compact && (
        <form onSubmit={handleAddEvent} className="p-3 rounded-lg border border-border/60 bg-muted/20 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-foreground">Log Timeline Activity</span>
            <select
              value={eventType}
              onChange={(e) => setEventType(e.target.value)}
              className="text-[11px] bg-background border border-border/60 rounded px-2 py-0.5 text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
            >
              <option value="NOTE_ADDED">Note / Log</option>
              <option value="RECRUITER_CONTACT">Recruiter Contact</option>
              <option value="ASSESSMENT_RECEIVED">Assessment Received</option>
              <option value="FOLLOW_UP">Follow Up Sent</option>
            </select>
          </div>
          <div className="flex gap-2">
            <Input
              value={newEventText}
              onChange={(e) => setNewEventText(e.target.value)}
              placeholder="e.g. Recruiter sent follow-up email regarding salary band..."
              className="text-xs flex-1 h-8"
              required
            />
            <Button type="submit" size="sm" className="h-8 text-xs gap-1" disabled={submitting || !newEventText.trim()}>
              <Plus className="w-3.5 h-3.5" />
              <span>Log</span>
            </Button>
          </div>
        </form>
      )}

      {/* Events Timeline */}
      {sortedEvents.length === 0 ? (
        <div className="text-center py-6 text-xs text-muted-foreground">
          No timeline events recorded yet.
        </div>
      ) : (
        <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-[1px] before:bg-border/60">
          {sortedEvents.map((event) => {
            const rawType = event.eventType || (event as any).event_type || 'NOTE_ADDED';
            const rawDate = event.createdAt || (event as any).created_at || new Date().toISOString();
            const date = new Date(rawDate);
            const isValid = !isNaN(date.getTime());
            const dateFormatted = isValid
              ? date.toLocaleDateString(undefined, {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                })
              : 'Recent';
            const timeFormatted = isValid
              ? date.toLocaleTimeString(undefined, {
                  hour: '2-digit',
                  minute: '2-digit',
                })
              : '';

            return (
              <div key={event.id} className="relative group">
                {/* Node icon on line */}
                <div className="absolute -left-6 top-0.5 p-1 rounded-full bg-background border border-border/80 shadow-xs flex items-center justify-center">
                  {getEventIcon(rawType)}
                </div>

                <div className="bg-card/70 border border-border/50 rounded-lg p-3 hover:border-border transition-colors">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span
                      className={`text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.2 rounded border ${getEventBadgeColor(
                        rawType
                      )}`}
                    >
                      {String(rawType).replace(/_/g, ' ')}
                    </span>
                    <div className="flex items-center gap-1 text-[11px] text-muted-foreground">
                      <Clock className="w-3 h-3" />
                      <span>{dateFormatted} {timeFormatted ? `at ${timeFormatted}` : ''}</span>
                    </div>
                  </div>

                  <p className="text-xs text-foreground/90 whitespace-pre-wrap leading-relaxed mt-1">
                    {event.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
