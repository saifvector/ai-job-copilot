'use client';

import React, { useEffect, useState } from 'react';
import { PageHeader } from '@/components/common/page-header';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import {
  useApplicationStore,
  useJobStore,
} from '@/store';
import {
  ApplicationAnalyticsHeader,
  KanbanBoard,
  ApplicationDetailModal,
  ScheduleInterviewModal,
  TrackApplicationModal,
} from '@/features/applications';
import {
  Briefcase,
  Plus,
  RefreshCw,
  AlertCircle,
} from 'lucide-react';
import { ApplicationStatus, CreateApplicationPayload, CreateInterviewPayload } from '@/types';

export default function ApplicationsPage() {
  const {
    pipeline,
    selectedApplication,
    analytics,
    loading,
    analyticsLoading,
    error,
    fetchPipeline,
    fetchAnalytics,
    selectApplicationById,
    createApplication,
    updateStatus,
    updateNotes,
    addEvent,
    addInterview,
    deleteApplication,
    clearSelected,
    clearError,
  } = useApplicationStore();

  const { fetchJobs } = useJobStore();

  const [isTrackModalOpen, setIsTrackModalOpen] = useState(false);
  const [trackDefaultStatus, setTrackDefaultStatus] = useState<ApplicationStatus>('SAVED');
  const [isInterviewModalOpen, setIsInterviewModalOpen] = useState(false);

  useEffect(() => {
    fetchPipeline();
    fetchAnalytics();
    fetchJobs();
  }, [fetchPipeline, fetchAnalytics, fetchJobs]);

  const handleOpenTrackModal = (defaultStatus: ApplicationStatus = 'SAVED') => {
    setTrackDefaultStatus(defaultStatus);
    setIsTrackModalOpen(true);
  };

  const handleSelectApplication = async (id: string) => {
    await selectApplicationById(id);
  };

  const handleStatusChange = async (id: string, newStatus: ApplicationStatus) => {
    await updateStatus(id, newStatus);
  };

  const handleDetailStatusChange = async (newStatus: ApplicationStatus) => {
    if (selectedApplication) {
      await updateStatus(selectedApplication.id, newStatus);
    }
  };

  const handleUpdateNotes = async (notes: string) => {
    if (selectedApplication) {
      await updateNotes(selectedApplication.id, notes);
    }
  };

  const handleAddEvent = async (payload: { eventType: string; description: string }) => {
    if (selectedApplication) {
      return await addEvent(selectedApplication.id, payload);
    }
    return false;
  };

  const handleScheduleInterview = async (payload: CreateInterviewPayload) => {
    if (selectedApplication) {
      return await addInterview(selectedApplication.id, payload);
    }
    return false;
  };

  const handleDeleteApplication = async () => {
    if (selectedApplication) {
      await deleteApplication(selectedApplication.id);
    }
  };

  const handleRefresh = () => {
    fetchPipeline();
    fetchAnalytics();
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Application Pipeline & Tracking"
        description="Monitor end-to-end job opportunities from discovery and submission to interviews, offers, and conversion performance."
        badge={
          <Badge variant="outline" className="border-primary/40 bg-primary/10 text-primary font-medium">
            <Briefcase className="w-3.5 h-3.5 mr-1 text-primary" />
            Phase 8: Active Pipeline
          </Badge>
        }
        action={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={loading}
              className="text-xs h-8 gap-1.5"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </Button>
            <Button
              size="sm"
              onClick={() => handleOpenTrackModal('SAVED')}
              className="text-xs h-8 gap-1.5 shadow-sm"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Track Application</span>
            </Button>
          </div>
        }
      />

      {/* Error Banner */}
      {error && (
        <div className="p-3 bg-destructive/10 border border-destructive/20 text-destructive rounded-lg flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
          <Button variant="ghost" size="sm" onClick={clearError} className="h-6 px-2 text-xs">
            Dismiss
          </Button>
        </div>
      )}

      {/* Analytics KPI Header */}
      <ApplicationAnalyticsHeader
        analytics={analytics}
        loading={analyticsLoading && !analytics}
      />

      {/* Kanban Board */}
      <Card className="p-5 border-border/60 bg-card/40 backdrop-blur-xs">
        <KanbanBoard
          pipeline={pipeline}
          loading={loading}
          onSelectApplication={handleSelectApplication}
          onStatusChange={handleStatusChange}
          onOpenTrackModal={handleOpenTrackModal}
        />
      </Card>

      {/* Application Details Modal */}
      <ApplicationDetailModal
        application={selectedApplication}
        isOpen={!!selectedApplication}
        onClose={clearSelected}
        onStatusChange={handleDetailStatusChange}
        onUpdateNotes={handleUpdateNotes}
        onAddEvent={handleAddEvent}
        onScheduleInterview={() => setIsInterviewModalOpen(true)}
        onDelete={handleDeleteApplication}
      />

      {/* Schedule Interview Modal */}
      {selectedApplication && (
        <ScheduleInterviewModal
          isOpen={isInterviewModalOpen}
          onClose={() => setIsInterviewModalOpen(false)}
          onSubmit={handleScheduleInterview}
          companyName={selectedApplication.job?.company || 'Target Employer'}
          jobTitle={selectedApplication.job?.title || 'Target Role'}
          defaultRound={(selectedApplication.interviews?.length || 0) + 1}
        />
      )}

      {/* Track Application Modal */}
      <TrackApplicationModal
        isOpen={isTrackModalOpen}
        onClose={() => setIsTrackModalOpen(false)}
        onSubmit={async (payload: CreateApplicationPayload) => {
          return await createApplication(payload);
        }}
        defaultStatus={trackDefaultStatus}
      />
    </div>
  );
}
