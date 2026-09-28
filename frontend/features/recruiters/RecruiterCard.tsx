'use client';

import React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Recruiter } from '@/types';
import {
  Building2,
  Mail,
  Linkedin,
  Clock,
  MessageSquare,
  Award,
  ChevronRight,
  ExternalLink,
  Plus,
} from 'lucide-react';

interface RecruiterCardProps {
  recruiter: Recruiter;
  onSelect: (recruiter: Recruiter) => void;
  onAddInteraction: (recruiter: Recruiter) => void;
  onAddReferral: (recruiter: Recruiter) => void;
}

function formatDate(dateStr?: string | null): string {
  if (!dateStr) return 'No interactions yet';
  try {
    const d = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 30) return `${diffDays}d ago`;
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  } catch {
    return dateStr;
  }
}

export function RecruiterCard({
  recruiter,
  onSelect,
  onAddInteraction,
  onAddReferral,
}: RecruiterCardProps) {
  return (
    <Card className="p-4 rounded-xl border border-border/60 bg-card hover:border-primary/50 transition-all shadow-sm hover:shadow-md flex flex-col justify-between group">
      <div className="space-y-3">
        {/* Header row */}
        <div className="flex items-start justify-between gap-2">
          <div className="space-y-1 flex-1 pr-2">
            <h3
              onClick={() => onSelect(recruiter)}
              className="text-sm font-bold text-foreground group-hover:text-primary transition-colors cursor-pointer line-clamp-1"
            >
              {recruiter.name}
            </h3>
            <p className="text-xs text-muted-foreground line-clamp-1">
              {recruiter.title || 'Recruiter / Talent Partner'}
            </p>
          </div>
          <Badge
            variant="outline"
            className="text-[11px] font-medium bg-muted/40 border-border/70 text-foreground flex-shrink-0 flex items-center gap-1"
          >
            <Building2 className="h-3 w-3 text-muted-foreground" />
            <span className="truncate max-w-[120px]">{recruiter.company}</span>
          </Badge>
        </div>

        {/* Contact Links */}
        <div className="flex items-center gap-3 text-xs text-muted-foreground pt-1 border-t border-border/40">
          {recruiter.email ? (
            <a
              href={`mailto:${recruiter.email}`}
              className="inline-flex items-center gap-1.5 hover:text-primary transition-colors truncate max-w-[160px]"
              title={recruiter.email}
              onClick={(e) => e.stopPropagation()}
            >
              <Mail className="h-3.5 w-3.5 text-blue-500 flex-shrink-0" />
              <span className="truncate">{recruiter.email}</span>
            </a>
          ) : (
            <span className="text-muted-foreground/60 italic text-[11px]">No email listed</span>
          )}

          {recruiter.linkedinUrl && (
            <a
              href={recruiter.linkedinUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 hover:text-blue-500 transition-colors ml-auto text-blue-400 font-medium text-[11px]"
              onClick={(e) => e.stopPropagation()}
            >
              <Linkedin className="h-3.5 w-3.5" />
              <span>LinkedIn</span>
              <ExternalLink className="h-2.5 w-2.5 opacity-70" />
            </a>
          )}
        </div>

        {/* Notes preview if present */}
        {recruiter.notes && (
          <p className="text-[11px] text-muted-foreground/90 line-clamp-2 bg-muted/20 p-2 rounded-md border border-border/30 italic">
            "{recruiter.notes}"
          </p>
        )}
      </div>

      {/* Metrics & Actions Footer */}
      <div className="mt-4 pt-3 border-t border-border/50 space-y-3">
        <div className="flex items-center justify-between text-[11px] text-muted-foreground">
          <div className="flex items-center gap-3">
            <span
              className="inline-flex items-center gap-1 font-medium text-foreground"
              title="Touchpoints logged"
            >
              <MessageSquare className="h-3 w-3 text-blue-500" />
              {recruiter.interactionCount}
            </span>
            <span
              className="inline-flex items-center gap-1 font-medium text-foreground"
              title="Referrals tracked"
            >
              <Award className="h-3 w-3 text-purple-500" />
              {recruiter.referralCount}
            </span>
          </div>

          <div className="flex items-center gap-1 text-[10px] text-muted-foreground/80">
            <Clock className="h-3 w-3" />
            <span>{formatDate(recruiter.lastInteractionDate)}</span>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-1.5 pt-1">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onAddInteraction(recruiter)}
            className="text-[10px] h-7 px-1.5 border-border/60 hover:border-primary/40 hover:bg-muted/40 gap-1"
          >
            <Plus className="h-3 w-3" />
            <span>Touchpoint</span>
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => onAddReferral(recruiter)}
            className="text-[10px] h-7 px-1.5 border-border/60 hover:border-purple-500/40 hover:bg-purple-500/10 text-purple-400 gap-1"
          >
            <Award className="h-3 w-3" />
            <span>Referral</span>
          </Button>

          <Button
            variant="default"
            size="sm"
            onClick={() => onSelect(recruiter)}
            className="text-[10px] h-7 px-1.5 bg-primary/90 hover:bg-primary text-primary-foreground gap-1"
          >
            <span>History</span>
            <ChevronRight className="h-3 w-3" />
          </Button>
        </div>
      </div>
    </Card>
  );
}
