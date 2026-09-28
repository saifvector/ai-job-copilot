'use client';

import React, { useEffect, useState } from 'react';
import { useApplicationAssistantStore } from '@/store/application-assistant-store';
import {
  AssistantAnalyticsHeader,
  JobSummaryCard,
  ResumeSelector,
  QuestionAnswerList,
  ChecklistProgress,
  ReviewScreen,
} from '@/features/application-assistant';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { apiClient } from '@/services/api-client';
import { Job } from '@/types';
import {
  Bot,
  Sparkles,
  FileText,
  CheckCircle2,
  ShieldCheck,
  ArrowRight,
  ArrowLeft,
  Briefcase,
  Save,
  Check,
} from 'lucide-react';

export default function ApplicationAssistantPage() {
  const {
    draft,
    drafts,
    answers,
    checklist,
    analytics,
    loading,
    isGenerating,
    isSaving,
    isSubmitting,
    activeStep,
    accuracyConfirmed,
    fetchDrafts,
    fetchDraft,
    createDraft,
    generateAnswers,
    updateAnswer,
    selectResume,
    saveReviewDraft,
    validateChecklist,
    submitDraft,
    fetchAnalytics,
    setActiveStep,
    setAccuracyConfirmed,
  } = useApplicationAssistantStore();

  const [availableJobs, setAvailableJobs] = useState<Job[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<string>('');
  const [lastSavedTime, setLastSavedTime] = useState<string | null>(null);

  // Initialize data
  useEffect(() => {
    fetchDrafts();
    fetchAnalytics();

    const loadJobs = async () => {
      try {
        const res = await apiClient.getJobs({ pageSize: 20 });
        const list = res.data?.items || [];
        setAvailableJobs(list);
        if (list.length > 0 && !selectedJobId) {
          setSelectedJobId(list[0].id);
        }
      } catch (err) {
        console.warn('Could not load jobs:', err);
      }
    };
    loadJobs();
  }, []);

  // Sync draft or select default
  useEffect(() => {
    if (drafts.length > 0 && !draft) {
      fetchDraft(drafts[0].id);
    }
  }, [drafts]);

  // Handle job selection and draft creation
  const handleSelectJob = async (jobId: string) => {
    setSelectedJobId(jobId);
    // Find if draft exists
    const existing = drafts.find((d) => d.jobId === jobId);
    if (existing) {
      await fetchDraft(existing.id);
    } else {
      await createDraft({ jobId });
    }
  };

  // Autosave answers when user edits
  const handleAnswerUpdate = (questionId: string, answer: string, isReviewed = true) => {
    updateAnswer(questionId, answer, isReviewed);
    setLastSavedTime('Saving...');

    // Simple debounce autosave
    const timer = setTimeout(async () => {
      await saveReviewDraft();
      setLastSavedTime(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    }, 1200);

    return () => clearTimeout(timer);
  };

  const currentScore = draft?.readinessScore ?? checklist?.readinessScore ?? 0;

  const steps = [
    { num: 1, label: 'Job & Resume', icon: Briefcase },
    { num: 2, label: 'AI Questions & Answers', icon: Sparkles },
    { num: 3, label: 'Readiness Checklist', icon: ShieldCheck },
    { num: 4, label: 'Candidate Review & Confirm', icon: CheckCircle2 },
  ];

  return (
    <div className="min-h-screen bg-slate-50/50 dark:bg-slate-950 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header Section */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="p-1.5 rounded-lg bg-blue-600/10 text-blue-600 dark:text-blue-400">
                <Bot className="w-5 h-5" />
              </span>
              <Badge variant="outline" className="text-xs">
                Phase 12
              </Badge>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-purple-50 dark:bg-purple-950/70 text-purple-600 dark:text-purple-400 border border-purple-200 dark:border-purple-800 flex items-center gap-1">
                <Sparkles className="w-3 h-3" />
                Gemini 2.5 Pro Powered
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white tracking-tight">
              Application Assistant
            </h1>
            <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
              Prepare truthful responses, attach tailored resumes, and audit readiness. Candidate reviews and confirms accuracy before submission.
            </p>
          </div>

          {/* Quick Draft Switcher */}
          {drafts.length > 0 && (
            <div className="flex items-center gap-2">
              <select
                value={draft?.id || ''}
                onChange={(e) => fetchDraft(e.target.value)}
                className="text-xs font-semibold px-3 py-2 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 shadow-sm focus:ring-1 focus:ring-blue-500"
              >
                {drafts.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.job?.title ? `${d.job.title} (${d.job.company})` : `Draft: ${d.id.slice(0, 8)}`} [{d.status}]
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Analytics Header */}
        <AssistantAnalyticsHeader analytics={analytics} currentScore={currentScore} />

        {/* Multi-Step Wizard Navigator */}
        <Card className="border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 shadow-sm">
          <CardContent className="p-3 sm:p-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {steps.map((s) => {
                const Icon = s.icon;
                const isActive = activeStep === s.num;
                const isPassed = activeStep > s.num;

                return (
                  <button
                    key={s.num}
                    type="button"
                    onClick={() => setActiveStep(s.num)}
                    className={`flex items-center gap-2.5 p-2.5 rounded-xl border text-left transition-all ${
                      isActive
                        ? 'border-blue-600 dark:border-blue-500 bg-blue-50/60 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 ring-1 ring-blue-600 dark:ring-blue-500'
                        : isPassed
                        ? 'border-emerald-200 dark:border-emerald-950 bg-emerald-50/30 dark:bg-emerald-950/20 text-emerald-700 dark:text-emerald-400'
                        : 'border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/40 text-slate-600 dark:text-slate-400 hover:border-slate-300'
                    }`}
                  >
                    <div className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 text-xs font-bold ${
                      isActive
                        ? 'bg-blue-600 text-white'
                        : isPassed
                        ? 'bg-emerald-600 text-white'
                        : 'bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300'
                    }`}>
                      {isPassed ? <Check className="w-4 h-4" /> : s.num}
                    </div>

                    <div className="truncate">
                      <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
                        Step {s.num}
                      </p>
                      <p className="text-xs font-bold truncate">
                        {s.label}
                      </p>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Autosave Status Bar */}
            <div className="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 px-1">
              <span className="flex items-center gap-1.5">
                <Save className="w-3.5 h-3.5 text-slate-400" />
                <span>
                  {isSaving ? 'Saving changes...' : lastSavedTime ? `Autosaved at ${lastSavedTime}` : 'Autosave active'}
                </span>
              </span>

              <span className="text-[11px] text-slate-400">
                Ready for Review: <strong>{currentScore}%</strong>
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Step 1: Job Summary & Resume Selection */}
        {activeStep === 1 && (
          <div className="space-y-6">
            {/* If no draft created, show job picker */}
            {!draft && availableJobs.length > 0 && (
              <Card className="border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 p-5">
                <h3 className="text-sm font-bold text-slate-900 dark:text-white mb-2">
                  Select Target Position to Prepare
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {availableJobs.map((j) => (
                    <div
                      key={j.id}
                      onClick={() => handleSelectJob(j.id)}
                      className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                        selectedJobId === j.id
                          ? 'border-blue-600 bg-blue-50/50 dark:bg-blue-950/20'
                          : 'border-slate-200 dark:border-slate-800 hover:border-slate-300'
                      }`}
                    >
                      <p className="text-sm font-bold text-slate-900 dark:text-white">{j.title}</p>
                      <p className="text-xs text-slate-500 mt-0.5">{j.company} • {j.location}</p>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            <JobSummaryCard job={draft?.job} status={draft?.status} />

            <ResumeSelector
              selectedResumeId={draft?.selectedResumeId}
              onSelectResume={selectResume}
              jobId={draft?.jobId}
            />

            <div className="flex justify-end gap-3">
              <Button
                variant="default"
                onClick={() => setActiveStep(2)}
                className="text-xs flex items-center gap-1.5"
              >
                <span>Proceed to Application Questions</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Button>
            </div>
          </div>
        )}

        {/* Step 2: AI Questions & Answers */}
        {activeStep === 2 && (
          <div className="space-y-6">
            <JobSummaryCard job={draft?.job} status={draft?.status} />

            <QuestionAnswerList
              questions={draft?.questions || []}
              answers={answers}
              onUpdateAnswer={handleAnswerUpdate}
              onRegenerateAnswers={() => generateAnswers({ regenerateAll: true })}
              isGenerating={isGenerating}
            />

            <div className="flex items-center justify-between gap-3">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setActiveStep(1)}
                className="text-xs flex items-center gap-1"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Back to Document Selection</span>
              </Button>

              <Button
                variant="default"
                size="sm"
                onClick={() => {
                  validateChecklist();
                  setActiveStep(3);
                }}
                className="text-xs flex items-center gap-1"
              >
                <span>Audit Readiness Checklist</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Button>
            </div>
          </div>
        )}

        {/* Step 3: Application Readiness Checklist */}
        {activeStep === 3 && (
          <div className="space-y-6">
            <JobSummaryCard job={draft?.job} status={draft?.status} />

            <ChecklistProgress
              checklist={checklist || (draft?.checklist as any) || null}
              onNavigateToStep={setActiveStep}
            />

            <div className="flex items-center justify-between gap-3">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setActiveStep(2)}
                className="text-xs flex items-center gap-1"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Back to Questions</span>
              </Button>

              <Button
                variant="default"
                size="sm"
                onClick={() => setActiveStep(4)}
                className="text-xs flex items-center gap-1"
              >
                <span>Proceed to Review Screen</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Button>
            </div>
          </div>
        )}

        {/* Step 4: Candidate Review & Confirm Screen */}
        {activeStep === 4 && (
          <div className="space-y-6">
            <ReviewScreen
              draft={draft}
              accuracyConfirmed={accuracyConfirmed}
              onConfirmAccuracyChange={setAccuracyConfirmed}
              onSubmitDraft={async () => {
                await submitDraft();
              }}
              onBackToQuestions={() => setActiveStep(2)}
              isSubmitting={isSubmitting}
            />
          </div>
        )}
      </div>
    </div>
  );
}
