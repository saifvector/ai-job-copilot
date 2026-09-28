'use client';

import React, { useEffect } from 'react';
import { PageHeader } from '@/components/common/page-header';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import {
  useTailoredResumeStore,
  useProfileStore,
} from '@/store';
import {
  ATSScoreCard,
  KeywordCoverageWidget,
  VersionComparisonView,
  ExportButtons,
  JobSelector,
} from '@/features/resume-tailoring';
import { Sparkles, FileText, History, AlertCircle } from 'lucide-react';

export default function ResumeTailoringPage() {
  const {
    resumes,
    selectedResume,
    selectedVersion,
    loading,
    error,
    fetchResumes,
    selectResumeById,
    selectVersion,
    tailorResume,
    clearError,
  } = useTailoredResumeStore();

  const { fetchProfile } = useProfileStore();

  useEffect(() => {
    fetchResumes();
    fetchProfile();
  }, [fetchResumes, fetchProfile]);

  const handleTailor = async (
    jobId: string,
    targetVersion: 'ats' | 'recruiter' | 'balanced',
    customInstructions?: string
  ) => {
    await tailorResume({
      jobId,
      targetVersion,
      customInstructions,
    });
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl space-y-8">
      {/* Page Header */}
      <PageHeader
        title="AI Resume Tailoring Engine"
        description="Synthesize ATS-optimized and recruiter-aligned resume versions with mathematical keyword alignment and zero hallucination guarantee."
        badge={
          <Badge variant="outline" className="border-primary/40 bg-primary/10 text-primary font-medium">
            <Sparkles className="w-3 h-3 mr-1 inline" />
            Phase 7 Engine
          </Badge>
        }
        action={
          selectedResume ? (
            <ExportButtons version={selectedVersion} />
          ) : undefined
        }
      />

      {/* Global Error Banner */}
      {error && (
        <div className="p-4 rounded-xl bg-destructive/10 border border-destructive/30 text-destructive text-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
          <button
            onClick={clearError}
            className="text-xs font-semibold underline hover:no-underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Top Workspace Grid: Job Selector + ATS Diagnostics */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Job Selector */}
        <div className="lg:col-span-5 space-y-4">
          <JobSelector onTailor={handleTailor} loading={loading} />

          {/* Past Tailored Resumes History */}
          {resumes.length > 0 && (
            <Card className="border border-border/50 shadow-xs">
              <div className="p-3.5 border-b border-border/40 flex items-center justify-between">
                <span className="text-xs font-semibold flex items-center gap-1.5 text-muted-foreground">
                  <History className="w-3.5 h-3.5" />
                  Previously Tailored Versions ({resumes.length})
                </span>
              </div>
              <div className="p-2 space-y-1 max-h-48 overflow-y-auto">
                {resumes.map((item) => {
                  const isSelected = selectedResume?.id === item.id;
                  return (
                    <div
                      key={item.id}
                      onClick={() => selectResumeById(item.id)}
                      className={`p-2.5 rounded-lg border text-xs cursor-pointer transition-all flex items-center justify-between ${
                        isSelected
                          ? 'border-primary bg-primary/10 font-semibold text-primary'
                          : 'border-transparent hover:bg-muted/40 text-foreground'
                      }`}
                    >
                      <div className="truncate pr-2">
                        <div className="truncate font-medium">{item.title}</div>
                        <div className="text-[11px] text-muted-foreground truncate">
                          {item.jobCompany}
                        </div>
                      </div>
                      <Badge variant="outline" className="text-[10px] shrink-0 font-medium">
                        ATS {Math.round(item.atsScore)}%
                      </Badge>
                    </div>
                  );
                })}
              </div>
            </Card>
          )}
        </div>

        {/* Right Column: ATS Score & Keyword Coverage */}
        <div className="lg:col-span-7 space-y-5">
          {selectedResume ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <ATSScoreCard
                score={selectedResume.atsScore}
                breakdown={selectedResume.atsBreakdown}
              />
              <KeywordCoverageWidget analysis={selectedResume.keywordAnalysis} />
            </div>
          ) : (
            <Card className="border border-dashed border-border/80 h-full min-h-[300px] flex items-center justify-center p-8 text-center bg-muted/5">
              <CardContent className="space-y-3 max-w-md">
                <div className="w-12 h-12 rounded-full bg-primary/10 text-primary flex items-center justify-center mx-auto">
                  <FileText className="w-6 h-6" />
                </div>
                <h3 className="text-base font-semibold text-foreground">
                  Ready to Tailor Your Resume
                </h3>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  Select a target job opportunity on the left to analyze requirements, calculate ATS compatibility, and synthesize Version A (ATS), Version B (Recruiter), and Version C (Balanced).
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Bottom Section: Multi-Version Comparison View */}
      {selectedResume && (
        <div className="pt-4 space-y-4">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div>
              <h2 className="text-lg font-bold text-foreground">
                Document Comparison & Version Analysis
              </h2>
              <p className="text-xs text-muted-foreground">
                Review section improvements, reordered bullet points, and highlighted matched keywords.
              </p>
            </div>
            <ExportButtons version={selectedVersion} />
          </div>

          <VersionComparisonView
            tailoredResume={selectedResume}
            activeVersionKey={selectedVersion}
            onSelectVersion={selectVersion}
          />
        </div>
      )}
    </div>
  );
}
