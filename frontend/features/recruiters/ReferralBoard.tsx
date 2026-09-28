'use client';

import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Referral, ReferralStatus } from '@/types';
import {
  Award,
  Building2,
  User,
  Clock,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Trash2,
  Calendar,
  Layers,
  ArrowRight,
} from 'lucide-react';

interface ReferralBoardProps {
  referrals: Referral[];
  loading?: boolean;
  onUpdateStatus: (id: string, newStatus: ReferralStatus) => Promise<unknown>;
  onDeleteReferral: (id: string) => Promise<boolean>;
}

const COLUMNS: {
  status: ReferralStatus;
  title: string;
  badgeColor: string;
  dotColor: string;
  emptyText: string;
}[] = [
  {
    status: 'Requested',
    title: 'Requested',
    badgeColor: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
    dotColor: 'bg-blue-500',
    emptyText: 'No referrals currently requested',
  },
  {
    status: 'Pending',
    title: 'Pending Review',
    badgeColor: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    dotColor: 'bg-amber-500',
    emptyText: 'No referrals awaiting recruiter action',
  },
  {
    status: 'Received',
    title: 'Received / Endorsed',
    badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    dotColor: 'bg-emerald-500',
    emptyText: 'No referrals endorsed yet',
  },
  {
    status: 'Declined',
    title: 'Declined',
    badgeColor: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
    dotColor: 'bg-rose-500',
    emptyText: 'No declined referrals',
  },
];

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

export function ReferralBoard({
  referrals,
  loading = false,
  onUpdateStatus,
  onDeleteReferral,
}: ReferralBoardProps) {
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const handleStatusChange = async (id: string, newStatus: ReferralStatus) => {
    setUpdatingId(id);
    await onUpdateStatus(id, newStatus);
    setUpdatingId(null);
  };

  const handleDelete = async (id: string, role: string, company: string) => {
    if (window.confirm(`Delete referral for "${role} at ${company}"?`)) {
      await onDeleteReferral(id);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {COLUMNS.map((col) => {
        const columnReferrals = referrals.filter(
          (r) => r.status.toLowerCase() === col.status.toLowerCase()
        );

        return (
          <div
            key={col.status}
            className="flex flex-col rounded-xl border border-border/60 bg-card/60 backdrop-blur-sm p-3.5 space-y-3 min-h-[420px]"
          >
            {/* Column Header */}
            <div className="flex items-center justify-between pb-2 border-b border-border/50">
              <div className="flex items-center gap-2">
                <span className={`h-2.5 w-2.5 rounded-full ${col.dotColor}`} />
                <h3 className="text-xs font-bold text-foreground uppercase tracking-wider">
                  {col.title}
                </h3>
              </div>
              <Badge variant="outline" className={`text-[10px] font-mono ${col.badgeColor}`}>
                {columnReferrals.length}
              </Badge>
            </div>

            {/* Referrals Cards Column */}
            <div className="flex-1 space-y-2.5 overflow-y-auto max-h-[600px] pr-0.5">
              {columnReferrals.length === 0 ? (
                <div className="text-center py-12 px-3 border border-dashed border-border/40 rounded-lg text-muted-foreground/60 text-xs">
                  {col.emptyText}
                </div>
              ) : (
                columnReferrals.map((referral) => {
                  const isUpdating = updatingId === referral.id;

                  return (
                    <Card
                      key={referral.id}
                      className="p-3.5 rounded-lg border border-border/60 bg-muted/20 hover:border-primary/40 transition-all shadow-sm space-y-2.5 group"
                    >
                      <div className="flex items-start justify-between gap-1.5">
                        <div className="space-y-0.5">
                          <h4 className="text-xs font-bold text-foreground line-clamp-1">
                            {referral.role}
                          </h4>
                          <div className="flex items-center gap-1 text-[11px] text-muted-foreground">
                            <Building2 className="h-3 w-3 text-muted-foreground/70" />
                            <span className="font-medium text-foreground/80">{referral.company}</span>
                          </div>
                        </div>

                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(referral.id, referral.role, referral.company)}
                          className="h-6 w-6 p-0 text-muted-foreground hover:text-rose-500 opacity-60 group-hover:opacity-100"
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>

                      {/* Recruiter attribution */}
                      {referral.recruiterName && (
                        <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground bg-card/60 p-1.5 rounded border border-border/40">
                          <User className="h-3 w-3 text-purple-400" />
                          <span className="truncate">Contact: <strong className="text-foreground">{referral.recruiterName}</strong></span>
                        </div>
                      )}

                      {/* Notes snippet */}
                      {referral.notes && (
                        <p className="text-[11px] text-muted-foreground/90 line-clamp-2 italic bg-muted/30 p-2 rounded border border-border/30">
                          "{referral.notes}"
                        </p>
                      )}

                      {/* Footer & Transition Actions */}
                      <div className="pt-2 border-t border-border/40 flex items-center justify-between text-[10px] text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {formatDate(referral.createdAt)}
                        </span>

                        {/* Status switcher */}
                        <div className="flex items-center gap-1">
                          {referral.status !== 'Received' && (
                            <button
                              onClick={() => handleStatusChange(referral.id, 'Received')}
                              disabled={isUpdating}
                              className="px-1.5 py-0.5 rounded bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[10px] font-medium transition-colors"
                              title="Mark as Received"
                            >
                              ✓ Received
                            </button>
                          )}

                          {referral.status === 'Requested' && (
                            <button
                              onClick={() => handleStatusChange(referral.id, 'Pending')}
                              disabled={isUpdating}
                              className="px-1.5 py-0.5 rounded bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 text-[10px] font-medium transition-colors"
                              title="Mark as Pending"
                            >
                              ⏳ Pending
                            </button>
                          )}

                          {referral.status !== 'Declined' && (
                            <button
                              onClick={() => handleStatusChange(referral.id, 'Declined')}
                              disabled={isUpdating}
                              className="px-1.5 py-0.5 rounded bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 text-[10px] font-medium transition-colors"
                              title="Mark as Declined"
                            >
                              ✕
                            </button>
                          )}
                        </div>
                      </div>
                    </Card>
                  );
                })
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
