'use client';

import React, { useState } from 'react';
import { Modal } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Recruiter, ContactInteraction, Referral, InteractionType, ReferralStatus } from '@/types';
import {
  Building2,
  Mail,
  Linkedin,
  Calendar,
  Clock,
  MessageSquare,
  Award,
  Plus,
  Trash2,
  PhoneCall,
  Video,
  FileText,
  ExternalLink,
  ChevronRight,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';

interface RecruiterDetailModalProps {
  recruiter: Recruiter | null;
  isOpen: boolean;
  onClose: () => void;
  onAddInteraction: (recruiter: Recruiter) => void;
  onAddReferral: (recruiter: Recruiter) => void;
  onDeleteRecruiter: (id: string) => Promise<boolean>;
}

const INTERACTION_CONFIG: Record<
  InteractionType,
  { label: string; icon: React.ComponentType<{ className?: string }>; color: string }
> = {
  Message: { label: 'Message / DM', icon: MessageSquare, color: 'text-blue-500 bg-blue-500/10 border-blue-500/30' },
  Email: { label: 'Email', icon: Mail, color: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/30' },
  Call: { label: 'Phone Call', icon: PhoneCall, color: 'text-amber-500 bg-amber-500/10 border-amber-500/30' },
  Interview: { label: 'Interview', icon: Video, color: 'text-indigo-500 bg-indigo-500/10 border-indigo-500/30' },
  Referral: { label: 'Referral Touchpoint', icon: Award, color: 'text-purple-500 bg-purple-500/10 border-purple-500/30' },
};

const REFERRAL_STATUS_CONFIG: Record<
  ReferralStatus,
  { label: string; color: string }
> = {
  Requested: { label: 'Requested', color: 'bg-blue-500/10 text-blue-400 border-blue-500/30' },
  Pending: { label: 'Pending Review', color: 'bg-amber-500/10 text-amber-400 border-amber-500/30' },
  Received: { label: 'Received / Endorsed', color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' },
  Declined: { label: 'Declined', color: 'bg-rose-500/10 text-rose-400 border-rose-500/30' },
};

function formatFullDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateStr;
  }
}

export function RecruiterDetailModal({
  recruiter,
  isOpen,
  onClose,
  onAddInteraction,
  onAddReferral,
  onDeleteRecruiter,
}: RecruiterDetailModalProps) {
  const [activeTab, setActiveTab] = useState<'timeline' | 'referrals' | 'notes'>('timeline');
  const [isDeleting, setIsDeleting] = useState(false);

  if (!recruiter) return null;

  const interactions = recruiter.interactions || [];
  const referrals = recruiter.referrals || [];

  const handleDelete = async () => {
    if (window.confirm(`Are you sure you want to remove "${recruiter.name}" from your CRM?`)) {
      setIsDeleting(true);
      const success = await onDeleteRecruiter(recruiter.id);
      setIsDeleting(false);
      if (success) {
        onClose();
      }
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      size="lg"
      className="max-w-2xl bg-card border-border"
    >
      <div className="space-y-5">
        {/* Recruiter Profile Header */}
        <div className="flex items-start justify-between gap-4 pb-4 border-b border-border/60">
          <div className="space-y-1.5 flex-1 pr-2">
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <Badge
                variant="outline"
                className="bg-muted/40 border-border/70 text-foreground font-medium text-xs flex items-center gap-1"
              >
                <Building2 className="h-3 w-3 text-muted-foreground" />
                <span>{recruiter.company}</span>
              </Badge>
              {recruiter.title && (
                <span className="text-xs text-muted-foreground">• {recruiter.title}</span>
              )}
            </div>

            <h2 className="text-xl font-bold tracking-tight text-foreground">
              {recruiter.name}
            </h2>

            {/* Contact links */}
            <div className="flex items-center gap-3 text-xs text-muted-foreground pt-1">
              {recruiter.email && (
                <a
                  href={`mailto:${recruiter.email}`}
                  className="inline-flex items-center gap-1.5 hover:text-primary transition-colors"
                >
                  <Mail className="h-3.5 w-3.5 text-blue-500" />
                  <span>{recruiter.email}</span>
                </a>
              )}

              {recruiter.linkedinUrl && (
                <a
                  href={recruiter.linkedinUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-blue-400 hover:text-blue-300 font-medium transition-colors"
                >
                  <Linkedin className="h-3.5 w-3.5" />
                  <span>LinkedIn Profile</span>
                  <ExternalLink className="h-2.5 w-2.5 opacity-70" />
                </a>
              )}
            </div>
          </div>

          <Button
            variant="ghost"
            size="sm"
            onClick={handleDelete}
            disabled={isDeleting}
            className="text-rose-500 hover:text-rose-600 hover:bg-rose-500/10 text-xs h-8 gap-1.5"
          >
            <Trash2 className="h-3.5 w-3.5" />
            <span>{isDeleting ? 'Deleting...' : 'Delete'}</span>
          </Button>
        </div>

        {/* Quick Action Buttons */}
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onAddInteraction(recruiter)}
            className="text-xs h-8 gap-1.5 border-border/70 hover:border-primary/50"
          >
            <Plus className="h-3.5 w-3.5 text-primary" />
            <span>Log Touchpoint</span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onAddReferral(recruiter)}
            className="text-xs h-8 gap-1.5 border-border/70 hover:border-purple-500/50 text-purple-400"
          >
            <Award className="h-3.5 w-3.5" />
            <span>Request Referral</span>
          </Button>
        </div>

        {/* Nav Tabs */}
        <div className="flex items-center gap-1 border-b border-border/60 pb-1">
          <button
            onClick={() => setActiveTab('timeline')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-colors flex items-center gap-1.5 ${
              activeTab === 'timeline'
                ? 'bg-primary/10 text-primary'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted/30'
            }`}
          >
            <Clock className="h-3.5 w-3.5" />
            <span>Touchpoint Timeline ({interactions.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('referrals')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-colors flex items-center gap-1.5 ${
              activeTab === 'referrals'
                ? 'bg-purple-500/10 text-purple-400'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted/30'
            }`}
          >
            <Award className="h-3.5 w-3.5" />
            <span>Referrals ({referrals.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('notes')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-colors flex items-center gap-1.5 ${
              activeTab === 'notes'
                ? 'bg-amber-500/10 text-amber-400'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted/30'
            }`}
          >
            <FileText className="h-3.5 w-3.5" />
            <span>Private Notes</span>
          </button>
        </div>

        {/* Tab 1: Chronological Interaction Timeline */}
        {activeTab === 'timeline' && (
          <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
            {interactions.length === 0 ? (
              <div className="text-center py-8 border border-dashed border-border/60 rounded-xl bg-muted/10 space-y-2">
                <MessageSquare className="h-6 w-6 text-muted-foreground/60 mx-auto" />
                <p className="text-xs text-muted-foreground">
                  No interactions recorded yet. Log your first message, call, or email.
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onAddInteraction(recruiter)}
                  className="text-xs h-7 gap-1"
                >
                  <Plus className="h-3 w-3" />
                  <span>Log Touchpoint</span>
                </Button>
              </div>
            ) : (
              <div className="relative pl-6 space-y-4 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-border/60">
                {interactions.map((interaction) => {
                  const cfg =
                    INTERACTION_CONFIG[interaction.interactionType as InteractionType] || {
                      label: interaction.interactionType,
                      icon: MessageSquare,
                      color: 'text-blue-500 bg-blue-500/10 border-blue-500/30',
                    };
                  const Icon = cfg.icon;

                  return (
                    <div key={interaction.id} className="relative space-y-1 group">
                      <div className="absolute -left-[27px] top-1 h-3.5 w-3.5 rounded-full bg-card border-2 border-primary" />
                      <div className="p-3 rounded-lg border border-border/60 bg-muted/20 space-y-1.5">
                        <div className="flex items-center justify-between">
                          <Badge variant="outline" className={`text-[10px] ${cfg.color}`}>
                            <Icon className="h-2.5 w-2.5 mr-1" />
                            {cfg.label}
                          </Badge>
                          <span className="text-[10px] text-muted-foreground">
                            {formatFullDate(interaction.interactionDate)}
                          </span>
                        </div>
                        <p className="text-xs text-foreground/90 whitespace-pre-wrap leading-relaxed">
                          {interaction.summary}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Referrals Pipeline */}
        {activeTab === 'referrals' && (
          <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
            {referrals.length === 0 ? (
              <div className="text-center py-8 border border-dashed border-border/60 rounded-xl bg-muted/10 space-y-2">
                <Award className="h-6 w-6 text-muted-foreground/60 mx-auto" />
                <p className="text-xs text-muted-foreground">
                  No referrals requested through {recruiter.name} yet.
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onAddReferral(recruiter)}
                  className="text-xs h-7 gap-1"
                >
                  <Plus className="h-3 w-3" />
                  <span>Track Referral</span>
                </Button>
              </div>
            ) : (
              <div className="space-y-2.5">
                {referrals.map((referral) => {
                  const statusCfg =
                    REFERRAL_STATUS_CONFIG[referral.status as ReferralStatus] || {
                      label: referral.status,
                      color: 'bg-zinc-500/10 text-zinc-400 border-zinc-500/30',
                    };

                  return (
                    <div
                      key={referral.id}
                      className="p-3 rounded-lg border border-border/60 bg-muted/20 flex items-start justify-between gap-3"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-foreground">
                            {referral.role}
                          </span>
                          <span className="text-xs text-muted-foreground">at {referral.company}</span>
                        </div>
                        {referral.notes && (
                          <p className="text-[11px] text-muted-foreground italic">
                            "{referral.notes}"
                          </p>
                        )}
                        <span className="text-[10px] text-muted-foreground/70 block">
                          Logged on {formatFullDate(referral.createdAt)}
                        </span>
                      </div>

                      <Badge variant="outline" className={`text-[10px] font-medium ${statusCfg.color}`}>
                        {statusCfg.label}
                      </Badge>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* Tab 3: Notes */}
        {activeTab === 'notes' && (
          <div className="p-4 rounded-lg border border-border/60 bg-muted/20 space-y-2">
            <span className="text-xs font-semibold text-foreground flex items-center gap-1.5">
              <FileText className="h-3.5 w-3.5 text-amber-500" />
              <span>Relationship Background & Context</span>
            </span>
            <p className="text-xs text-foreground/90 whitespace-pre-wrap leading-relaxed">
              {recruiter.notes || 'No private notes logged for this contact yet.'}
            </p>
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-end pt-3 border-t border-border/60">
          <Button variant="outline" size="sm" onClick={onClose} className="text-xs h-8">
            Close
          </Button>
        </div>
      </div>
    </Modal>
  );
}
