'use client';

import * as React from 'react';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Sparkles,
  RefreshCw,
  UploadCloud,
  ArrowLeft,
  AlertTriangle,
  CheckCircle2,
  FileText,
  Cpu,
} from 'lucide-react';
import { AppShell } from '@/components/layout/app-shell';
import { PageHeader } from '@/components/common/page-header';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { useProfileStore } from '@/store/profile-store';
import { useResumeStore } from '@/store/resume-store';
import {
  ProfileCard,
  SummarySection,
  SkillsSection,
  ProjectsSection,
  ExperienceSection,
  EducationSection,
  CertificationsSection,
  AnalysisSkeleton,
} from '@/features/resume-analysis';

export default function ResumeAnalysisPage() {
  const {
    profile,
    skills,
    projects,
    education,
    experience,
    certifications,
    loading: profileLoading,
    error: profileError,
    modelUsed,
    parsedAt,
    fetchProfile,
    parseResume,
    resetError,
  } = useProfileStore();

  const { resume, fetchResume } = useResumeStore();
  const [analyzing, setAnalyzing] = useState(false);
  const [successNotice, setSuccessNotice] = useState<string | null>(null);

  useEffect(() => {
    fetchResume();
    fetchProfile();
  }, [fetchResume, fetchProfile]);

  const handleTriggerAnalysis = async () => {
    resetError();
    setSuccessNotice(null);
    setAnalyzing(true);
    const success = await parseResume();
    setAnalyzing(false);
    if (success) {
      setSuccessNotice('Resume intelligence parsed and normalized successfully!');
      setTimeout(() => setSuccessNotice(null), 5000);
    }
  };

  const hasIntelligenceData =
    Boolean(profile?.contact?.name) ||
    skills.length > 0 ||
    projects.length > 0 ||
    education.length > 0 ||
    experience.length > 0;

  const isLoading = profileLoading || analyzing;

  return (
    <AppShell>
      <div className="container max-w-6xl mx-auto py-8 px-4 sm:px-6 space-y-8">
        {/* Navigation & Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Link
                href="/resume"
                className="inline-flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                <ArrowLeft className="h-3.5 w-3.5" />
                <span>Back to Files</span>
              </Link>
            </div>
            <PageHeader
              title="Resume Intelligence Engine"
              description="High-precision candidate profile extraction powered by Google Gemini 2.5 Pro & Flash"
            />
          </div>

          {/* Action Bar */}
          <div className="flex items-center gap-2.5">
            {resume && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleTriggerAnalysis}
                disabled={isLoading}
                className="gap-2 border-primary/30 hover:border-primary/60 hover:bg-primary/5"
              >
                <RefreshCw className={`h-4 w-4 text-primary ${isLoading ? 'animate-spin' : ''}`} />
                <span>{isLoading ? 'Extracting with AI...' : 'Re-analyze Resume'}</span>
              </Button>
            )}

            <Link href="/resume">
              <Button size="sm" className="gap-2">
                <UploadCloud className="h-4 w-4" />
                <span>Manage Resume</span>
              </Button>
            </Link>
          </div>
        </div>


        {/* Success Alert */}
        {successNotice && (
          <div className="flex items-center gap-3 p-4 rounded-xl border border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-sm">
            <CheckCircle2 className="h-5 w-5 shrink-0" />
            <p className="font-medium">{successNotice}</p>
          </div>
        )}

        {/* Error Alert */}
        {profileError && (
          <div className="flex items-start gap-3 p-4 rounded-xl border border-destructive/30 bg-destructive/10 text-destructive text-sm">
            <AlertTriangle className="h-5 w-5 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <p className="font-medium">Resume Analysis Error</p>
              <p className="text-xs opacity-90">{profileError}</p>
            </div>
          </div>
        )}

        {/* Content View */}
        {isLoading ? (
          <div className="space-y-6">
            <div className="flex items-center justify-center gap-3 p-6 rounded-2xl border border-primary/20 bg-primary/5 text-primary">
              <div className="relative flex h-8 w-8 items-center justify-center">
                <RefreshCw className="h-6 w-6 animate-spin" />
                <Sparkles className="absolute -top-1 -right-1 h-3.5 w-3.5 text-amber-500 animate-pulse" />
              </div>
              <div className="text-sm">
                <p className="font-semibold text-foreground">
                  Gemini Multi-Attempt Extraction in Progress
                </p>
                <p className="text-xs text-muted-foreground">
                  Validating schema, normalizing entities, and synthesizing executive summary...
                </p>
              </div>
            </div>
            <AnalysisSkeleton />
          </div>
        ) : !hasIntelligenceData ? (
          /* Empty State */
          <Card className="border border-dashed border-border/80 bg-card/40 p-12 text-center">
            <CardContent className="space-y-4 max-w-md mx-auto p-0">
              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 text-primary">
                <FileText className="h-8 w-8" />
              </div>
              <div className="space-y-1.5">
                <h3 className="text-lg font-bold text-foreground">
                  No Resume Intelligence Found
                </h3>
                <p className="text-sm text-muted-foreground">
                  {resume
                    ? `Your active file (${resume.originalFilename}) is uploaded and ready to be parsed.`
                    : 'Upload a PDF or DOCX resume to extract verified skills, projects, and credentials.'}
                </p>
              </div>

              <div className="pt-2">
                {resume ? (
                  <Button
                    onClick={handleTriggerAnalysis}
                    className="gap-2 shadow-md hover:shadow-lg transition-all"
                  >
                    <Sparkles className="h-4 w-4" />
                    <span>Run Gemini Intelligence Analysis</span>
                  </Button>
                ) : (
                  <Link href="/resume">
                    <Button className="gap-2">
                      <UploadCloud className="h-4 w-4" />
                      <span>Upload Resume Document</span>
                    </Button>
                  </Link>
                )}

              </div>
            </CardContent>
          </Card>
        ) : (
          /* Main Intelligence Layout */
          <div className="space-y-8">
            {/* 1. Candidate Identity Card */}
            <ProfileCard
              contact={profile?.contact}
              modelUsed={modelUsed}
              parsedAt={parsedAt}
            />

            {/* 2. Professional Executive Summary */}
            <SummarySection summary={profile?.summary} />

            {/* 3. Skills Section with Category Filters */}
            <SkillsSection skills={skills} />

            {/* 4. Projects Portfolio */}
            <ProjectsSection projects={projects} />

            {/* 5. Career Work Experience */}
            <ExperienceSection experience={experience} />

            {/* 6. Education & Certifications Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <EducationSection education={education} />
              <CertificationsSection certifications={certifications} />
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
