'use client';

import React, { useState } from 'react';
import { Modal } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { CreateInteractionPayload, InteractionType, Recruiter } from '@/types';
import {
  MessageSquare,
  Mail,
  PhoneCall,
  Video,
  Award,
  Calendar,
  AlertCircle,
} from 'lucide-react';

interface AddInteractionModalProps {
  recruiter: Recruiter | null;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (recruiterId: string, payload: CreateInteractionPayload) => Promise<unknown>;
  loading?: boolean;
}

const INTERACTION_TYPES: {
  type: InteractionType;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}[] = [
  {
    type: 'Message',
    label: 'LinkedIn / DM',
    icon: MessageSquare,
    color: 'text-blue-500 bg-blue-500/10 border-blue-500/30',
  },
  {
    type: 'Email',
    label: 'Direct Email',
    icon: Mail,
    color: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/30',
  },
  {
    type: 'Call',
    label: 'Phone Call',
    icon: PhoneCall,
    color: 'text-amber-500 bg-amber-500/10 border-amber-500/30',
  },
  {
    type: 'Interview',
    label: 'Interview Round',
    icon: Video,
    color: 'text-indigo-500 bg-indigo-500/10 border-indigo-500/30',
  },
  {
    type: 'Referral',
    label: 'Referral Check-in',
    icon: Award,
    color: 'text-purple-500 bg-purple-500/10 border-purple-500/30',
  },
];

export function AddInteractionModal({
  recruiter,
  isOpen,
  onClose,
  onSubmit,
  loading = false,
}: AddInteractionModalProps) {
  const [type, setType] = useState<InteractionType>('Message');
  const [summary, setSummary] = useState('');
  const [date, setDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [formError, setFormError] = useState<string | null>(null);

  if (!recruiter) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!summary.trim()) {
      setFormError('Interaction summary is required.');
      return;
    }

    setFormError(null);
    const success = await onSubmit(recruiter.id, {
      interactionType: type,
      summary: summary.trim(),
      interactionDate: date ? new Date(date).toISOString() : undefined,
    });

    if (success) {
      setSummary('');
      setType('Message');
      onClose();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      size="md"
      className="max-w-lg bg-card border-border"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between pb-2 border-b border-border/60">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-medium text-muted-foreground">Touchpoint with</span>
              <Badge variant="outline" className="text-xs font-semibold text-primary">
                {recruiter.name}
              </Badge>
              <span className="text-xs text-muted-foreground">at {recruiter.company}</span>
            </div>
            <h2 className="text-base font-bold text-foreground">
              Log Outreach Touchpoint
            </h2>
          </div>
        </div>

        {formError && (
          <div className="p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span>{formError}</span>
          </div>
        )}

        {/* Interaction Type Picker */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-foreground">
            Interaction Channel
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {INTERACTION_TYPES.map((t) => {
              const Icon = t.icon;
              const isSelected = type === t.type;
              return (
                <button
                  type="button"
                  key={t.type}
                  onClick={() => setType(t.type)}
                  className={`p-2.5 rounded-lg border text-left transition-all flex items-center gap-2 text-xs font-medium ${
                    isSelected
                      ? `${t.color} ring-1 ring-primary/40 font-semibold shadow-sm`
                      : 'border-border/60 bg-muted/20 text-muted-foreground hover:bg-muted/40 hover:text-foreground'
                  }`}
                >
                  <Icon className="h-4 w-4 flex-shrink-0" />
                  <span className="truncate">{t.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Date Field */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-foreground flex items-center gap-1.5">
            <Calendar className="h-3.5 w-3.5 text-muted-foreground" />
            <span>Interaction Date</span>
          </label>
          <Input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="text-xs h-9 bg-background/50 border-border/70 max-w-xs"
          />
        </div>

        {/* Summary Field */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-foreground">
            Summary / Discussion Notes <span className="text-rose-500">*</span>
          </label>
          <textarea
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            rows={4}
            required
            placeholder="e.g. Sent customized pitch regarding the Staff Backend Engineer role. Recruiter replied asking for availability next Tuesday..."
            className="w-full text-xs rounded-md border border-border/70 bg-background/50 p-2.5 text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-2 pt-3 border-t border-border/60">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onClose}
            disabled={loading}
            className="text-xs h-8"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            size="sm"
            disabled={loading}
            className="text-xs h-8 bg-primary hover:bg-primary/90 text-primary-foreground font-medium"
          >
            {loading ? 'Logging...' : 'Save Touchpoint'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
