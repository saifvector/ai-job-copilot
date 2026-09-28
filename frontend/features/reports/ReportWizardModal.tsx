'use client';

import React, { useState } from 'react';
import {
  FileText,
  BarChart3,
  Lightbulb,
  Award,
  Sparkles,
  FileSpreadsheet,
  FileCode,
  Calendar,
  CheckCircle2,
  Loader2,
} from 'lucide-react';
import { ExportFormat, ReportGeneratePayload, ReportType } from '@/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Modal } from '@/components/ui/modal';

interface ReportWizardModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: (payload: ReportGeneratePayload) => Promise<unknown>;
  generating: boolean;
  initialType?: ReportType;
}

const REPORT_TYPES: {
  id: ReportType;
  title: string;
  subtitle: string;
  description: string;
  icon: React.ElementType;
  badge: string;
  color: string;
}[] = [
  {
    id: 'APPLICATION_REPORT',
    title: 'Application Performance',
    subtitle: 'Funnel & Conversion Pipeline',
    description: 'Tracks sent applications, response rate, interview conversion rate, offer milestones, and monthly timeline.',
    icon: BarChart3,
    badge: 'Applications',
    color: 'text-blue-500 bg-blue-500/10 border-blue-500/20',
  },
  {
    id: 'MATCH_REPORT',
    title: 'Job Match Compatibility',
    subtitle: 'Fit Scores & Ranking Scorecard',
    description: 'Evaluates compatibility across all discovered jobs, average match scores, score distribution, and top positions.',
    icon: Award,
    badge: 'Matches',
    color: 'text-indigo-500 bg-indigo-500/10 border-indigo-500/20',
  },
  {
    id: 'SKILL_REPORT',
    title: 'Skill Gap & Priorities',
    subtitle: 'Market Demand & Learning Roadmap',
    description: 'Identifies missing market skills, demand frequencies, learning priorities (Docker, AWS, K8s), and sprint roadmap.',
    icon: Lightbulb,
    badge: 'Skill Gaps',
    color: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
  },
  {
    id: 'CAREER_REPORT',
    title: 'Career Readiness Audit',
    subtitle: 'Executive Benchmarks & Alignment',
    description: 'Calculates overall readiness score, resume strength, experience coverage, and high-impact career recommendations.',
    icon: Sparkles,
    badge: 'Readiness',
    color: 'text-purple-500 bg-purple-500/10 border-purple-500/20',
  },
  {
    id: 'RESUME_REPORT',
    title: 'Resume & ATS Performance',
    subtitle: 'Keyword Density & Tailoring History',
    description: 'Audits ATS optimization scores across tailored resumes, tailoring history, and keyword alignment benchmarks.',
    icon: FileText,
    badge: 'Resume',
    color: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20',
  },
];

const FORMAT_OPTIONS: {
  id: ExportFormat;
  label: string;
  description: string;
  icon: React.ElementType;
  color: string;
}[] = [
  {
    id: 'PDF',
    label: 'Publication PDF',
    description: 'Executive document with charts, branding, and tables',
    icon: FileText,
    color: 'text-rose-500 bg-rose-500/10 border-rose-500/20',
  },
  {
    id: 'XLSX',
    label: 'Excel Spreadsheet',
    description: 'Multi-tab workbook: Applications, Matches, Analytics',
    icon: FileSpreadsheet,
    color: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20',
  },
  {
    id: 'CSV',
    label: 'Raw CSV Data',
    description: 'Standard RFC 4180 format for spreadsheets & databases',
    icon: FileSpreadsheet,
    color: 'text-blue-500 bg-blue-500/10 border-blue-500/20',
  },
  {
    id: 'JSON',
    label: 'Structured JSON',
    description: 'Complete data tree for developers & programmatic tools',
    icon: FileCode,
    color: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
  },
];

const DATE_SCOPES: { label: string; days: number | undefined }[] = [
  { label: 'Past 30 Days', days: 30 },
  { label: 'Past 90 Days', days: 90 },
  { label: 'Past 1 Year', days: 365 },
  { label: 'All Time', days: undefined },
];

export function ReportWizardModal({
  isOpen,
  onClose,
  onGenerate,
  generating,
  initialType,
}: ReportWizardModalProps) {
  const [selectedType, setSelectedType] = useState<ReportType>('APPLICATION_REPORT');
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>('PDF');
  const [dateRangeDays, setDateRangeDays] = useState<number | undefined>(30);
  const [customTitle, setCustomTitle] = useState('');

  React.useEffect(() => {
    if (initialType) {
      setSelectedType(initialType);
    }
  }, [initialType, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onGenerate({
      reportType: selectedType,
      format: selectedFormat,
      title: customTitle.trim() || undefined,
      dateRangeDays,
      includeDetails: true,
    });
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Generate Career Report & Export"
      description="Create a publication-grade PDF or structured dataset from your career telemetry."
      size="xl"
    >
      <form onSubmit={handleSubmit} className="space-y-6 pt-2">
        {/* Step 1: Select Report Type */}
        <div className="space-y-2.5">
          <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center justify-between">
            <span>1. Select Report Category</span>
            <span className="text-[11px] font-normal normal-case text-primary">Required</span>
          </label>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
            {REPORT_TYPES.map((type) => {
              const Icon = type.icon;
              const isSelected = selectedType === type.id;

              return (
                <div
                  key={type.id}
                  onClick={() => setSelectedType(type.id)}
                  className={`relative p-3.5 rounded-xl border cursor-pointer transition-all duration-150 select-none ${
                    isSelected
                      ? 'border-primary bg-primary/5 ring-1 ring-primary/40 shadow-xs'
                      : 'border-border/60 hover:border-border hover:bg-muted/30 bg-card'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className={`p-2 rounded-lg border ${type.color}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    {isSelected && (
                      <CheckCircle2 className="w-4 h-4 text-primary shrink-0" />
                    )}
                  </div>
                  <h4 className="text-xs font-bold text-foreground mb-0.5">{type.title}</h4>
                  <p className="text-[11px] font-medium text-muted-foreground line-clamp-1 mb-1">
                    {type.subtitle}
                  </p>
                  <p className="text-[10px] text-muted-foreground/80 line-clamp-2 leading-relaxed">
                    {type.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Step 2: Select Format */}
        <div className="space-y-2.5">
          <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            2. Choose Export Format
          </label>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
            {FORMAT_OPTIONS.map((fmt) => {
              const Icon = fmt.icon;
              const isSelected = selectedFormat === fmt.id;

              return (
                <div
                  key={fmt.id}
                  onClick={() => setSelectedFormat(fmt.id)}
                  className={`p-3 rounded-xl border cursor-pointer transition-all duration-150 select-none text-center space-y-1.5 ${
                    isSelected
                      ? 'border-primary bg-primary/5 ring-1 ring-primary/40 shadow-xs'
                      : 'border-border/60 hover:border-border hover:bg-muted/30 bg-card'
                  }`}
                >
                  <div className={`w-8 h-8 rounded-lg border mx-auto flex items-center justify-center ${fmt.color}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div className="text-xs font-bold text-foreground">{fmt.label}</div>
                  <div className="text-[10px] text-muted-foreground line-clamp-1">
                    {fmt.description}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Step 3: Scope and Custom Title */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1 border-t border-border/40">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-foreground flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-primary" />
              <span>Timeframe Scope</span>
            </label>
            <div className="grid grid-cols-2 gap-1.5">
              {DATE_SCOPES.map((scope) => (
                <button
                  key={scope.label}
                  type="button"
                  onClick={() => setDateRangeDays(scope.days)}
                  className={`text-xs px-2.5 py-1.5 rounded-lg border transition-colors ${
                    dateRangeDays === scope.days
                      ? 'bg-primary text-primary-foreground border-primary font-semibold'
                      : 'bg-muted/40 hover:bg-muted border-border/60 text-muted-foreground'
                  }`}
                >
                  {scope.label}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-foreground">
              Custom Title (Optional)
            </label>
            <Input
              value={customTitle}
              onChange={(e) => setCustomTitle(e.target.value)}
              placeholder="e.g. Q4 Executive Application Audit"
              className="text-xs h-9"
            />
            <p className="text-[10px] text-muted-foreground">
              Leave blank to automatically title with report name and date.
            </p>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-border/60">
          <Button type="button" variant="outline" size="sm" onClick={onClose} disabled={generating}>
            Cancel
          </Button>
          <Button type="submit" size="sm" disabled={generating} className="gap-1.5 min-w-[140px]">
            {generating ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Generating...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-3.5 h-3.5" />
                <span>Generate & Export</span>
              </>
            )}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
