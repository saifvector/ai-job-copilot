'use client';

import React from 'react';
import {
  FileText,
  Download,
  Calendar,
  Clock,
  HardDrive,
  Trash2,
  CheckCircle2,
  Sparkles,
  BarChart3,
  Layers,
  FileSpreadsheet,
  FileCode,
  Tag,
  Info,
} from 'lucide-react';
import { Report, ExportFormat, ReportType } from '@/types';
import { Modal } from '@/components/ui/modal';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface ReportPreviewModalProps {
  report: Report | null;
  isOpen: boolean;
  onClose: () => void;
  onDownload: (id: string, fileName?: string) => Promise<void>;
  onDelete: (id: string) => Promise<boolean>;
  isDownloading?: boolean;
}

const REPORT_TYPE_CONFIG: Record<
  ReportType,
  {
    label: string;
    description: string;
    badgeColor: string;
    icon: React.ComponentType<{ className?: string }>;
    sections: string[];
  }
> = {
  APPLICATION_REPORT: {
    label: 'Application Performance',
    description: 'Comprehensive pipeline funnel, interview & offer rates, and monthly trends.',
    badgeColor: 'bg-blue-500/10 text-blue-500 border-blue-500/30',
    icon: BarChart3,
    sections: [
      'Total Applications & Active Funnel',
      'Interview, Offer, Response & Rejection Rates',
      'Timeline Velocity & Monthly Trajectory',
      'Detailed Application Log & Current Statuses',
    ],
  },
  MATCH_REPORT: {
    label: 'Match Score Analysis',
    description: 'Algorithmic scoring, top opportunity matches, and skill alignment profiles.',
    badgeColor: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/30',
    icon: Sparkles,
    sections: [
      'Overall Average Match Score & Tier Distribution',
      'Top 10 High-Fit Job Recommendations',
      'Strongest Matched Skill Capabilities',
      'Target Skill Gaps by Employer Demand',
    ],
  },
  SKILL_REPORT: {
    label: 'Skill Gap & Priorities',
    description: 'Market demand mapping, missing keywords, and structured learning roadmap.',
    badgeColor: 'bg-purple-500/10 text-purple-500 border-purple-500/30',
    icon: Layers,
    sections: [
      'Market Frequency of High-Value Skills',
      'Candidate Deficit & Missing Competencies',
      'Prioritized Upskilling Roadmap (P1, P2, P3)',
      'Estimated Velocity to Market Alignment',
    ],
  },
  CAREER_REPORT: {
    label: 'Career Readiness Index',
    description: 'Holistic career benchmarking, resume strength, and market alignment index.',
    badgeColor: 'bg-indigo-500/10 text-indigo-500 border-indigo-500/30',
    icon: CheckCircle2,
    sections: [
      'Weighted Career Readiness Composite Score',
      'Resume Baseline Structural Strength',
      'Technical Skill & Experience Coverage Ratios',
      'Domain & Industry Target Alignment',
    ],
  },
  RESUME_REPORT: {
    label: 'Resume Performance & ATS',
    description: 'ATS compliance checks, tailored versions audit, and keyword coverage.',
    badgeColor: 'bg-amber-500/10 text-amber-500 border-amber-500/30',
    icon: FileText,
    sections: [
      'ATS Benchmark Scoring & Keyword Density',
      'Tailored Resume Versions Breakdown',
      'Employer Match Alignment History',
      'High-Impact Tailoring Action Points',
    ],
  },
};

const FORMAT_CONFIG: Record<
  ExportFormat,
  {
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    color: string;
    badgeStyle: string;
  }
> = {
  PDF: {
    label: 'PDF Document',
    icon: FileText,
    color: 'text-rose-500',
    badgeStyle: 'bg-rose-500/10 text-rose-500 border-rose-500/30',
  },
  CSV: {
    label: 'CSV Data File',
    icon: FileCode,
    color: 'text-emerald-500',
    badgeStyle: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/30',
  },
  XLSX: {
    label: 'Excel Workbook',
    icon: FileSpreadsheet,
    color: 'text-blue-500',
    badgeStyle: 'bg-blue-500/10 text-blue-500 border-blue-500/30',
  },
  JSON: {
    label: 'JSON Object',
    icon: FileCode,
    color: 'text-amber-500',
    badgeStyle: 'bg-amber-500/10 text-amber-500 border-amber-500/30',
  },
};

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

function formatDate(dateStr: string): string {
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

export function ReportPreviewModal({
  report,
  isOpen,
  onClose,
  onDownload,
  onDelete,
  isDownloading = false,
}: ReportPreviewModalProps) {
  const [isDeleting, setIsDeleting] = React.useState(false);

  if (!report) return null;

  const typeConfig = REPORT_TYPE_CONFIG[report.reportType] || {
    label: report.reportType,
    description: 'Custom analytical export report.',
    badgeColor: 'bg-zinc-500/10 text-zinc-400 border-zinc-500/30',
    icon: FileText,
    sections: ['Data Summary', 'Metrics Breakdown', 'Detailed Logs'],
  };

  const formatConfig = FORMAT_CONFIG[report.format] || {
    label: report.format,
    icon: FileText,
    color: 'text-muted-foreground',
    badgeStyle: 'bg-zinc-500/10 text-zinc-400 border-zinc-500/30',
  };

  const FormatIcon = formatConfig.icon;
  const TypeIcon = typeConfig.icon;

  const handleDelete = async () => {
    if (window.confirm(`Are you sure you want to delete "${report.title}"?`)) {
      setIsDeleting(true);
      const success = await onDelete(report.id);
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
      <div className="space-y-6">
        {/* Header Section */}
        <div className="flex items-start justify-between gap-4 border-b border-border/60 pb-5">
          <div className="space-y-1.5 flex-1 pr-4">
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <Badge variant="outline" className={typeConfig.badgeColor}>
                <TypeIcon className="h-3 w-3 mr-1" />
                {typeConfig.label}
              </Badge>
              <Badge variant="outline" className={formatConfig.badgeStyle}>
                <FormatIcon className="h-3 w-3 mr-1" />
                {formatConfig.label}
              </Badge>
            </div>
            <h2 className="text-xl font-bold tracking-tight text-foreground">
              {report.title}
            </h2>
            <p className="text-xs text-muted-foreground">
              {typeConfig.description}
            </p>
          </div>
        </div>

        {/* File & Generation Telemetry Card */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-3 rounded-lg border border-border/60 bg-muted/20 space-y-1">
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <Calendar className="h-3.5 w-3.5 text-blue-500" />
              <span>Generated</span>
            </div>
            <div className="text-xs font-semibold text-foreground truncate">
              {formatDate(report.generatedAt)}
            </div>
          </div>

          <div className="p-3 rounded-lg border border-border/60 bg-muted/20 space-y-1">
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <HardDrive className="h-3.5 w-3.5 text-emerald-500" />
              <span>File Size</span>
            </div>
            <div className="text-xs font-semibold text-foreground">
              {formatBytes(report.fileSize)}
            </div>
          </div>

          <div className="p-3 rounded-lg border border-border/60 bg-muted/20 space-y-1">
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <Download className="h-3.5 w-3.5 text-purple-500" />
              <span>Downloads</span>
            </div>
            <div className="text-xs font-semibold text-foreground">
              {report.downloadCount} {report.downloadCount === 1 ? 'time' : 'times'}
            </div>
          </div>

          <div className="p-3 rounded-lg border border-border/60 bg-muted/20 space-y-1">
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <Clock className="h-3.5 w-3.5 text-amber-500" />
              <span>Generation</span>
            </div>
            <div className="text-xs font-semibold text-foreground">
              {report.generationDurationMs > 0
                ? `${report.generationDurationMs.toFixed(0)} ms`
                : '< 100 ms'}
            </div>
          </div>
        </div>

        {/* Summary or Description */}
        <div className="rounded-lg border border-border/60 bg-muted/10 p-4 space-y-2">
          <div className="flex items-center gap-1.5 text-xs font-medium text-foreground">
            <Info className="h-4 w-4 text-primary" />
            <span>Executive Report Summary</span>
          </div>
          <p className="text-sm text-muted-foreground leading-relaxed">
            {report.summary ||
              `This report was synthesized from your active profile, job discoveries, and telemetry data. It contains up-to-date metrics formatted for professional presentation and archival.`}
          </p>
        </div>

        {/* Sections Included Breakdown */}
        <div className="space-y-2.5">
          <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Included In This Artifact
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {typeConfig.sections.map((section, idx) => (
              <div
                key={idx}
                className="flex items-center gap-2 p-2.5 rounded-md border border-border/40 bg-card/60 text-xs text-foreground/90"
              >
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 flex-shrink-0" />
                <span className="truncate">{section}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex flex-col-reverse sm:flex-row items-center justify-between gap-3 pt-4 border-t border-border/60">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleDelete}
            disabled={isDeleting}
            className="w-full sm:w-auto text-rose-500 hover:text-rose-600 hover:bg-rose-500/10"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            {isDeleting ? 'Deleting...' : 'Delete Artifact'}
          </Button>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Button variant="outline" size="sm" onClick={onClose} className="flex-1 sm:flex-initial">
              Close
            </Button>
            <Button
              variant="default"
              size="sm"
              onClick={() => onDownload(report.id, report.fileName)}
              disabled={isDownloading}
              className="flex-1 sm:flex-initial bg-primary hover:bg-primary/90 text-primary-foreground font-medium shadow-sm"
            >
              <Download className="h-4 w-4 mr-2" />
              {isDownloading ? 'Downloading...' : `Download ${report.format}`}
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  );
}
