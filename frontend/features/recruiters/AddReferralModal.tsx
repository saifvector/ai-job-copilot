'use client';

import React, { useState, useEffect } from 'react';
import { Modal } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { CreateReferralPayload, Recruiter, ReferralStatus } from '@/types';
import { Award, Building2, Briefcase, FileText, AlertCircle } from 'lucide-react';

interface AddReferralModalProps {
  recruiter: Recruiter | null;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (recruiterId: string, payload: CreateReferralPayload) => Promise<unknown>;
  loading?: boolean;
}

const REFERRAL_STATUSES: {
  status: ReferralStatus;
  label: string;
  color: string;
}[] = [
  { status: 'Requested', label: 'Requested', color: 'bg-blue-500/10 text-blue-400 border-blue-500/30' },
  { status: 'Pending', label: 'Pending Review', color: 'bg-amber-500/10 text-amber-400 border-amber-500/30' },
  { status: 'Received', label: 'Received / Endorsed', color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' },
  { status: 'Declined', label: 'Declined', color: 'bg-rose-500/10 text-rose-400 border-rose-500/30' },
];

export function AddReferralModal({
  recruiter,
  isOpen,
  onClose,
  onSubmit,
  loading = false,
}: AddReferralModalProps) {
  const [company, setCompany] = useState('');
  const [role, setRole] = useState('');
  const [status, setStatus] = useState<ReferralStatus>('Requested');
  const [notes, setNotes] = useState('');
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (recruiter) {
      setCompany(recruiter.company || '');
    }
  }, [recruiter, isOpen]);

  if (!recruiter) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!company.trim()) {
      setFormError('Company name is required.');
      return;
    }
    if (!role.trim()) {
      setFormError('Target role title is required.');
      return;
    }

    setFormError(null);
    const success = await onSubmit(recruiter.id, {
      company: company.trim(),
      role: role.trim(),
      status,
      notes: notes.trim() || undefined,
    });

    if (success) {
      setRole('');
      setNotes('');
      setStatus('Requested');
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
              <span className="text-xs text-muted-foreground">Referral contact:</span>
              <Badge variant="outline" className="text-xs font-semibold text-purple-400 border-purple-500/30 bg-purple-500/10">
                {recruiter.name}
              </Badge>
            </div>
            <h2 className="text-base font-bold text-foreground">
              Request / Track Job Referral
            </h2>
          </div>
        </div>

        {formError && (
          <div className="p-2.5 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span>{formError}</span>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-foreground">
              Company <span className="text-rose-500">*</span>
            </label>
            <Input
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              placeholder="e.g. Datadog, Stripe"
              required
              className="text-xs h-9 bg-background/50 border-border/70"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-foreground">
              Role / Target Position <span className="text-rose-500">*</span>
            </label>
            <Input
              value={role}
              onChange={(e) => setRole(e.target.value)}
              placeholder="e.g. Senior Platform Engineer"
              required
              className="text-xs h-9 bg-background/50 border-border/70"
            />
          </div>
        </div>

        {/* Status Selector */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-foreground">
            Referral Status
          </label>
          <div className="grid grid-cols-2 gap-2">
            {REFERRAL_STATUSES.map((s) => {
              const isSelected = status === s.status;
              return (
                <button
                  type="button"
                  key={s.status}
                  onClick={() => setStatus(s.status)}
                  className={`p-2 rounded-lg border text-xs font-medium transition-all text-left ${
                    isSelected
                      ? `${s.color} ring-1 ring-purple-500/40 font-semibold shadow-sm`
                      : 'border-border/60 bg-muted/20 text-muted-foreground hover:bg-muted/40 hover:text-foreground'
                  }`}
                >
                  {s.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Notes */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-foreground">
            Requisition Link & Notes
          </label>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            placeholder="Internal requisition ID (e.g. REQ-9901), referral confirmation code, or link to job description..."
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
            className="text-xs h-8 bg-purple-600 hover:bg-purple-700 text-white font-medium"
          >
            {loading ? 'Saving...' : 'Track Referral'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
