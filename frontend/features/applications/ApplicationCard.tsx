'use client';

import React from 'react';
import {
  Building2,
  MapPin,
  Calendar,
  Clock,
  Sparkles,
  ArrowRight,
  GripVertical,
} from 'lucide-react';
import { ApplicationListItem, ApplicationStatus } from '@/types';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface ApplicationCardProps {
  application: ApplicationListItem;
  onSelect: (id: string) => void;
  onAdvanceStatus?: (id: string, nextStatus: ApplicationStatus) => void;
}

const NEXT_STAGE_MAP: Record<ApplicationStatus, ApplicationStatus | null> = {
  SAVED: 'APPLIED',
  APPLIED: 'ASSESSMENT',
  ASSESSMENT: 'INTERVIEW',
  INTERVIEW: 'OFFER',
  OFFER: null,
  REJECTED: null,
  WITHDRAWN: null,
};

export function ApplicationCard({
  application,
  onSelect,
  onAdvanceStatus,
}: ApplicationCardProps) {
  const nextStage = NEXT_STAGE_MAP[application.status];

  const handleDragStart = (e: React.DragEvent<HTMLDivElement>) => {
    e.dataTransfer.setData('applicationId', application.id);
    e.dataTransfer.setData('currentStatus', application.status);
    e.dataTransfer.effectAllowed = 'move';
  };

  const formatRelativeTime = (isoString: string) => {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 30) return `${diffDays}d ago`;
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  };

  const company = application.jobCompany || (application as any).job_company || 'Company';
  const title = application.jobTitle || (application as any).job_title || 'Position';
  const location = application.jobLocation || (application as any).job_location || 'Remote';
  const lastUpdated = application.lastUpdated || (application as any).last_updated || (application as any).created_at || new Date().toISOString();
  const nextInterview = application.nextInterviewDate || (application as any).next_interview_date;

  return (
    <div
      draggable
      onDragStart={handleDragStart}
      onClick={() => onSelect(application.id)}
      className="group relative bg-card/90 hover:bg-card border border-border/60 hover:border-primary/40 rounded-lg p-3.5 shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer select-none"
    >
      {/* Top Header: Company + Source */}
      <div className="flex items-center justify-between gap-2 mb-1.5">
        <div className="flex items-center gap-1.5 min-w-0">
          <Building2 className="w-3.5 h-3.5 text-muted-foreground shrink-0" />
          <span className="font-semibold text-xs text-foreground truncate">
            {company}
          </span>
        </div>
        <div className="flex items-center gap-1 shrink-0">
          {application.source && (
            <Badge
              variant="outline"
              className="text-[10px] px-1.5 py-0 h-4 font-normal text-muted-foreground bg-muted/30 border-border/40"
            >
              {application.source}
            </Badge>
          )}
          <GripVertical className="w-3 h-3 text-muted-foreground/40 group-hover:text-muted-foreground/80 transition-colors" />
        </div>
      </div>

      {/* Job Title */}
      <h4 className="font-medium text-sm text-foreground group-hover:text-primary transition-colors line-clamp-1 mb-2">
        {title}
      </h4>

      {/* Meta Row: Location + Tailored resume pill */}
      <div className="flex items-center flex-wrap gap-2 text-[11px] text-muted-foreground mb-3">
        <div className="flex items-center gap-1">
          <MapPin className="w-3 h-3 shrink-0" />
          <span className="truncate max-w-[120px]">{location}</span>
        </div>

        {application.tailoredResumeId && (
          <div className="flex items-center gap-1 text-primary bg-primary/10 px-1.5 py-0.5 rounded text-[10px] font-medium">
            <Sparkles className="w-2.5 h-2.5" />
            <span>Tailored</span>
          </div>
        )}
      </div>

      {/* Interview Badge if scheduled */}
      {nextInterview && (
        <div className="flex items-center gap-1.5 bg-blue-500/10 border border-blue-500/20 text-blue-500 text-[11px] px-2 py-1 rounded mb-2 font-medium">
          <Calendar className="w-3 h-3 shrink-0" />
          <span>Next: {new Date(nextInterview).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
        </div>
      )}

      {/* Bottom Footer: Time ago + Quick advance button */}
      <div className="flex items-center justify-between pt-2 border-t border-border/40 text-[11px] text-muted-foreground">
        <div className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          <span>{formatRelativeTime(lastUpdated)}</span>
        </div>

        {nextStage && onAdvanceStatus && (
          <Button
            size="sm"
            variant="ghost"
            onClick={(e) => {
              e.stopPropagation();
              onAdvanceStatus(application.id, nextStage);
            }}
            className="h-6 px-1.5 text-[10px] text-primary hover:text-primary hover:bg-primary/10 gap-0.5"
            title={`Advance to ${nextStage}`}
          >
            <span>Advance</span>
            <ArrowRight className="w-2.5 h-2.5" />
          </Button>
        )}
      </div>
    </div>
  );
}
