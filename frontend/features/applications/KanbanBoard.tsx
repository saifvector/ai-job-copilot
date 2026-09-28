'use client';

import React, { useState } from 'react';
import {
  Bookmark,
  Send,
  ClipboardCheck,
  Calendar,
  Award,
  XCircle,
  Archive,
  Plus,
} from 'lucide-react';
import { ApplicationListItem, ApplicationStatus, PipelineData } from '@/types';
import { ApplicationCard } from './ApplicationCard';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface KanbanColumnConfig {
  status: ApplicationStatus;
  label: string;
  icon: React.ElementType;
  color: string;
  badgeBg: string;
  headerBorder: string;
}

const COLUMNS: KanbanColumnConfig[] = [
  {
    status: 'SAVED',
    label: 'Saved',
    icon: Bookmark,
    color: 'text-amber-500',
    badgeBg: 'bg-amber-500/10 text-amber-500',
    headerBorder: 'border-t-amber-500',
  },
  {
    status: 'APPLIED',
    label: 'Applied',
    icon: Send,
    color: 'text-blue-500',
    badgeBg: 'bg-blue-500/10 text-blue-500',
    headerBorder: 'border-t-blue-500',
  },
  {
    status: 'ASSESSMENT',
    label: 'Assessment',
    icon: ClipboardCheck,
    color: 'text-purple-500',
    badgeBg: 'bg-purple-500/10 text-purple-500',
    headerBorder: 'border-t-purple-500',
  },
  {
    status: 'INTERVIEW',
    label: 'Interview',
    icon: Calendar,
    color: 'text-indigo-500',
    badgeBg: 'bg-indigo-500/10 text-indigo-500',
    headerBorder: 'border-t-indigo-500',
  },
  {
    status: 'OFFER',
    label: 'Offer',
    icon: Award,
    color: 'text-emerald-500',
    badgeBg: 'bg-emerald-500/10 text-emerald-500',
    headerBorder: 'border-t-emerald-500',
  },
  {
    status: 'REJECTED',
    label: 'Rejected',
    icon: XCircle,
    color: 'text-rose-500',
    badgeBg: 'bg-rose-500/10 text-rose-500',
    headerBorder: 'border-t-rose-500',
  },
];

interface KanbanBoardProps {
  pipeline: PipelineData;
  loading?: boolean;
  onSelectApplication: (id: string) => void;
  onStatusChange: (id: string, newStatus: ApplicationStatus) => void;
  onOpenTrackModal?: (defaultStatus?: ApplicationStatus) => void;
}

export function KanbanBoard({
  pipeline,
  loading = false,
  onSelectApplication,
  onStatusChange,
  onOpenTrackModal,
}: KanbanBoardProps) {
  const [dragOverColumn, setDragOverColumn] = useState<ApplicationStatus | null>(null);
  const [showWithdrawn, setShowWithdrawn] = useState(false);

  const getColumnItems = (status: ApplicationStatus): ApplicationListItem[] => {
    switch (status) {
      case 'SAVED':
        return pipeline.saved || [];
      case 'APPLIED':
        return pipeline.applied || [];
      case 'ASSESSMENT':
        return pipeline.assessment || [];
      case 'INTERVIEW':
        return pipeline.interview || [];
      case 'OFFER':
        return pipeline.offer || [];
      case 'REJECTED':
        return pipeline.rejected || [];
      case 'WITHDRAWN':
        return pipeline.withdrawn || [];
      default:
        return [];
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>, status: ApplicationStatus) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    if (dragOverColumn !== status) {
      setDragOverColumn(status);
    }
  };

  const handleDragLeave = () => {
    setDragOverColumn(null);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>, targetStatus: ApplicationStatus) => {
    e.preventDefault();
    setDragOverColumn(null);
    const appId = e.dataTransfer.getData('applicationId');
    const currentStatus = e.dataTransfer.getData('currentStatus');

    if (appId && currentStatus !== targetStatus) {
      onStatusChange(appId, targetStatus);
    }
  };

  const activeColumns = showWithdrawn
    ? [
        ...COLUMNS,
        {
          status: 'WITHDRAWN' as ApplicationStatus,
          label: 'Withdrawn',
          icon: Archive,
          color: 'text-zinc-500',
          badgeBg: 'bg-zinc-500/10 text-zinc-500',
          headerBorder: 'border-t-zinc-500',
        },
      ]
    : COLUMNS;

  return (
    <div className="space-y-4">
      {/* Board Controls Bar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span>Total Tracked:</span>
          <Badge variant="outline" className="font-semibold text-foreground px-2 py-0.5">
            {pipeline.totalApplications}
          </Badge>
          <span className="text-muted-foreground/60">•</span>
          <span>Active Pipeline:</span>
          <Badge variant="secondary" className="font-semibold text-primary px-2 py-0.5">
            {pipeline.totalActive}
          </Badge>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant={showWithdrawn ? 'secondary' : 'outline'}
            onClick={() => setShowWithdrawn(!showWithdrawn)}
            className="text-xs h-7 gap-1 px-2.5"
          >
            <Archive className="w-3.5 h-3.5" />
            <span>{showWithdrawn ? 'Hide Withdrawn' : `Withdrawn (${pipeline.withdrawn?.length || 0})`}</span>
          </Button>

          {onOpenTrackModal && (
            <Button
              size="sm"
              onClick={() => onOpenTrackModal('SAVED')}
              className="text-xs h-7 gap-1 px-2.5 shadow-sm"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Track Application</span>
            </Button>
          )}
        </div>
      </div>

      {/* Responsive Horizontal Kanban Grid */}
      <div className="overflow-x-auto pb-4">
        <div className="flex gap-4 min-w-[1280px]">
          {activeColumns.map((col) => {
            const items = getColumnItems(col.status);
            const isDragOver = dragOverColumn === col.status;
            const Icon = col.icon;

            return (
              <div
                key={col.status}
                onDragOver={(e) => handleDragOver(e, col.status)}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, col.status)}
                className={`flex-1 min-w-[220px] max-w-[260px] flex flex-col rounded-xl border border-t-2 ${col.headerBorder} ${
                  isDragOver
                    ? 'border-primary bg-primary/5 ring-2 ring-primary/20'
                    : 'border-border/60 bg-muted/20'
                } transition-all duration-150`}
              >
                {/* Column Header */}
                <div className="p-3 border-b border-border/40 flex items-center justify-between">
                  <div className="flex items-center gap-2 min-w-0">
                    <Icon className={`w-4 h-4 ${col.color} shrink-0`} />
                    <span className="font-semibold text-xs text-foreground truncate">
                      {col.label}
                    </span>
                  </div>
                  <Badge
                    variant="outline"
                    className={`text-[11px] font-semibold px-1.5 py-0 h-4.5 border-0 ${col.badgeBg}`}
                  >
                    {items.length}
                  </Badge>
                </div>

                {/* Cards Container */}
                <div className="p-2 flex-1 flex flex-col gap-2 min-h-[380px] max-h-[calc(100vh-320px)] overflow-y-auto">
                  {loading && items.length === 0 ? (
                    <div className="space-y-2 p-1">
                      {[1, 2].map((i) => (
                        <div key={i} className="h-24 rounded-lg bg-card/50 animate-pulse" />
                      ))}
                    </div>
                  ) : items.length === 0 ? (
                    <div className="flex-1 flex flex-col items-center justify-center p-4 text-center border-2 border-dashed border-border/30 rounded-lg my-1">
                      <p className="text-xs text-muted-foreground/70">No applications</p>
                      {onOpenTrackModal && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onOpenTrackModal(col.status)}
                          className="mt-2 text-[11px] h-6 px-2 text-muted-foreground hover:text-foreground gap-1"
                        >
                          <Plus className="w-3 h-3" />
                          <span>Add to {col.label}</span>
                        </Button>
                      )}
                    </div>
                  ) : (
                    items.map((app) => (
                      <ApplicationCard
                        key={app.id}
                        application={app}
                        onSelect={onSelectApplication}
                        onAdvanceStatus={onStatusChange}
                      />
                    ))
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
